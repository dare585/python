import boto3
from botocore.exceptions import ClientError
from collections import defaultdict


class S3BucketManager:

    def __init__(self, aws_access_key_id:str, aws_secret_access_key: str, aws_session_token: str, region: str):
        """
        Get temporary AWS Credentials and aws region - 
        aws_access_key_id, aws_secret_access_key, aws_session_token and region
        """
        self._s3 = boto3.resource('s3', \
                                  aws_access_key_id=aws_access_key_id, \
                                  aws_secret_access_key=aws_secret_access_key, \
                                  aws_session_token=aws_session_token, \
                                  region_name=region)

    def list_s3_buckets(self) -> dict:
        """
        list All S3 buckets
        """
        buckets_info = []
        for bucket in self._s3.buckets.all():
            bucket_info = {
                'name': bucket.name,
                'creation_date': bucket.creation_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'region': self.get_bucket_region(bucket),
                'object_count': self.get_object_count(bucket),
                'total_size_bytes': self.get_total_size_bytes(bucket),
                'versioning_enabled': self.is_versioning_enabled(bucket),
                'public_access_blocked': self.is_public_access_blocked(bucket)
            }
            buckets_info.append(bucket_info)

        return {"buckets": buckets_info}


    def get_bucket_details(self, bucket_name: str) -> dict:
        """
        Get a bucket name and return this bucket details
        """
        bucket = self._s3.Bucket(bucket_name)
        storage_class_summary = self.get_storage_class_summary(bucket)
        lifecycle_rules = self.get_lifecycle_rules(bucket)
        encryption = self.get_encryption(bucket)

        bucket_details = {
            'name': bucket.name,
            'creation_date': bucket.creation_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'region': self.get_bucket_region(bucket),
            'storage_class_summary': storage_class_summary,
            'lifecycle_rules': lifecycle_rules,
            'encryption': encryption
        }

        return bucket_details


    def get_buckets_summary(self) -> dict:
        """
        Return a buckets summary
        """
        summary = {
            "total_buckets": self.get_buckets_count(),
            "total_storage_gb": self.get_total_size_gb(),
            "buckets_without_encryption": self.get_total_buckets_without_encryption(),
            "publicly_accessible_buckets": self.get_total_publicly_accessible_buckets()
            }

        return summary


    def get_bucket_region(self, bucket) -> str:
        """
        Get s3.Bucket object and return the bucket region
        LocationConstraint - Specifies the Region where the bucket resides
        - Buckets in Region us-east-1 have a LocationConstraint of null.
        - Buckets with a LocationConstraint of EU reside in eu-west-1
        - see docs: https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLocation.html
        """
        bucket_region_mapping = {
            None: "us-east-1",
            "EU": "eu-west-1"
        }

        region = bucket.meta.client.get_bucket_location(Bucket=bucket.name)["LocationConstraint"]
        return bucket_region_mapping.get(region, region)


    @staticmethod
    def get_object_count(bucket) -> int:
        """
        Get s3.Bucket 
        Return total object count in this bucket
        """
        return sum(1 for _ in bucket.objects.all())



    def get_buckets_count(self) -> int:
        """
        Return total S3 buckets count in the AWS account
        """
        return sum(1 for _ in self._s3.buckets.all())


    @staticmethod
    def get_total_size_bytes(bucket) -> int:
        """
        Get s3.Bucket 
        Return total bucket size in bytes
        """
        return sum(obj.size for obj in bucket.objects.all())


    def get_total_size_gb(self) -> float:
        """
        Return total of all the buckets size in GB
        """
        total_storage_size_bytes = sum(self.get_total_size_bytes(bucket) for bucket in self._s3.buckets.all())
        return total_storage_size_bytes / (1024 * 1024 * 1024)


    @staticmethod
    def is_versioning_enabled(bucket) -> bool:
        """
        Get s3.Bucket object
        Check if versioning is enabled on this bucket
        """
        return bucket.Versioning().status == 'Enabled'


    @staticmethod
    def is_public_access_blocked(bucket) -> bool:
        """ 
        Get s3.Bucket object
        Check if "Block all public access" settings is checked on the S3 bucket,
        which means all the below settings are checked:
        - Block public access to buckets and objects granted through new access control lists (ACLs)
        - Block public access to buckets and objects granted through any access control lists (ACLs)
        - Block public access to buckets and objects granted through new public bucket or access point policies
        - Block public and cross-account access to buckets and objects through any public bucket or access point policies

        we check all the public access block configurations are set to True
        public_access_block = bucket.meta.client.get_public_access_block(Bucket=bucket.name)
        public_access_block["PublicAccessBlockConfiguration"]["BlockPublicAcls"]
        public_access_block["PublicAccessBlockConfiguration"]["BlockPublicPolicy"]
        public_access_block["PublicAccessBlockConfiguration"]["IgnorePublicAcls"]
        public_access_block["PublicAccessBlockConfiguration"]["RestrictPublicBuckets"]
        """
        public_access_block = bucket.meta.client.get_public_access_block(Bucket=bucket.name)
        return all(public_access_block["PublicAccessBlockConfiguration"].values())


    @staticmethod 
    def get_storage_class_summary(bucket) -> dict:
        """
        Get s3.Bucket object and return the bucket storage class summary
        """
        storage_class_summary = defaultdict(int)
        for obj in bucket.objects.all():
            storage_class_summary[obj.storage_class] += 1
        return dict(storage_class_summary)

    
    @staticmethod
    def get_lifecycle_rules(bucket) -> list:
        """
        Get s3.Bucket object and return the bucket lifecycle rules
        In case no life cycle rules exist, return an empty list
        """
        life_cycle_config = bucket.LifecycleConfiguration()
        try:
            life_cycle_rules = life_cycle_config.rules
        except ClientError as e:
            life_cycle_rules = []

        converted_life_cycle_rules = [
            {
                'id': rule['ID'],
                'status': rule['Status'],
                'transitions': [
                    {
                        'days': transition['Days'],
                        'storage_class': transition['StorageClass']
                    }
                    for transition in rule['Transitions']
                ]
            }
            for rule in life_cycle_rules
        ]

        return converted_life_cycle_rules

  
    @staticmethod
    def get_encryption(bucket) -> dict:
        """
        Get s3.Bucket object and return the bucket server side encryption configuration
        """
        bucket_encryption = bucket.meta.client.get_bucket_encryption(Bucket=bucket.name)

        # if empty dict than encryption is disabled
        is_encryption_enabled = True if bucket_encryption["ServerSideEncryptionConfiguration"] else False  

        # if encryption is disabled than set type to empty string
        encryption_type = \
            bucket_encryption["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"] \
                if is_encryption_enabled else ""

        encryption_config = {"enabled": is_encryption_enabled,
                             "type": encryption_type}

        return encryption_config
    

    def get_total_buckets_without_encryption(self) -> int:
        """
        Return total buckets without encryption
        """
        return sum(1 for bucket in self._s3.buckets.all() \
                   if not (self.get_bucket_details(bucket.name)["encryption"]["enabled"]))
        


    def get_total_publicly_accessible_buckets(self) -> int:
        """
        Return total buckets that are publicly accessible
        """
        return sum(1 for bucket in self.list_s3_buckets()["buckets"] \
                   if not bucket["public_access_blocked"])
