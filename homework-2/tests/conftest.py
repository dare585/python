import os
import boto3
import pytest
from botocore.exceptions import ClientError

from app import create_app
from app.utils.utils import generate_random_string


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        # This duration can range from 900 seconds (15 minutes)
        # up to a maximum of 129,600 seconds (36 hours)
        'SESSION_TIMEOUT_SECONDS': 900 
    })

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def aws_credentials():
    """
    Fixture that retrieves the AWS environment variables set in the environment.
    It assumes the environment variables are already exported before running the tests.
    """
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")

    # Return the credentials as a dictionary
    return {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
        "aws_region": aws_region
    }


@pytest.fixture
def authenticated_client(client, aws_credentials):
    """
        login to the app, and return the client
        which has the session Cookie header set
    """
    aws_access_key_id = aws_credentials["aws_access_key_id"]
    aws_secret_access_key = aws_credentials["aws_secret_access_key"]
    aws_region = aws_credentials["aws_region"]
    
    client.post('/api/v1/auth/login',
                json={'aws_access_key_id': aws_access_key_id, 
                      'aws_secret_access_key': aws_secret_access_key,
                      'aws_region': aws_region})
    # client now has the session cookie set
    # (done automaticlly after it sent the post request)
    return client

def delete_all_objects_in_bucket(s3_client, bucket_name):
    """
    Deletes all versions of objects in the bucket before deleting the bucket itself.
    """
    # List all the versions of objects in the bucket
    response = s3_client.list_object_versions(Bucket=bucket_name)
    
    # Delete each version of each object
    while 'Versions' in response:
        for version in response['Versions']:
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=version['Key'],
                VersionId=version['VersionId']
            )
        
        # Continue to get the next batch of versions (if any)
        if 'DeleteMarkers' in response:
            for marker in response['DeleteMarkers']:
                s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=marker['Key'],
                    VersionId=marker['VersionId']
                )
        
        # Fetch the next batch of versions, if any
        if 'NextVersionIdMarker' in response:
            response = s3_client.list_object_versions(
                Bucket=bucket_name,
                VersionIdMarker=response['NextVersionIdMarker']
            )
        else:
            break


@pytest.fixture(scope='session')
def s3_client():
    """
    Create boto3 S3 client.
    """
    client = boto3.client('s3', region_name='us-east-1')
    yield client


@pytest.fixture(scope='session')
def create_first_bucket(s3_client):
    """
    Create First Bucket:
    - region: us-east-2
    - with 2 objects
    - versioning enabled
    - public access is alllowed (i.e 'Block all public access' setting is Unchecked, set to "off")
    - with lifecycle policy
    """
    bucket_name = f'pytest-1-{generate_random_string(8)}'
    region = 'us-east-2'

    try:
        # Step 1: Create the S3 bucket
        print(f"\nBucket '{bucket_name}' : Create bucket in region {region}.")
        response = s3_client.create_bucket(
               Bucket=bucket_name,
               CreateBucketConfiguration={'LocationConstraint': region}
           )

        bucket_creation_date = response["ResponseMetadata"]["HTTPHeaders"]["date"]
        print(f"Bucket '{bucket_name}' : bucket created in {region} successfully.")

        # Step 2: Add two objects to the bucket
        print(f"Bucket '{bucket_name}' : Adding two objects.")
        s3_client.put_object(Bucket=bucket_name, Key='pytest-object1.txt', Body='This is object 1')
        s3_client.put_object(Bucket=bucket_name, Key='pytest-object2.txt', Body='This is object 2')
        print(f"Bucket '{bucket_name}' : Two objects added successfully.")

        # Step 3: Set 'Block all public access' to Unchecked (public access is allowed)
        print(f"Bucket '{bucket_name}' : Uncheck 'Block all public access' (public access is allowed).")
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        print(f"Bucket '{bucket_name}' : 'Block all public access' was Unchecked successfully.")

        # Step 4: Enable versioning
        print(f"Bucket '{bucket_name}' : Enable versioning.")
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"Bucket '{bucket_name}' : Versioning enabled successfully.")

        # Step 5: Set lifecycle configuration
        print(f"Bucket '{bucket_name}' : Set lifecycle configuration.")
        lifecycle_configuration = {
            'Rules': [
                {
                    'ID': 'Pytest lifecycle Configuration',
                    'Filter': {},
                    'Status': 'Enabled',
                    'Transitions': [
                        {
                            'Days': 30,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'Days': 90,
                            'StorageClass': 'GLACIER'
                        }
                    ]
                }
            ]
        }
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_configuration
        )
        print(f"Bucket '{bucket_name}' : Lifecycle configuration was set successfully.")

        # Yield the bucket name for testing
        yield bucket_name, bucket_creation_date

    except ClientError as e:
        print(f"Error occurred during bucket '{bucket_name}' creation: {e}")
        raise  # Re-raise the exception so pytest handles it properly

    finally:
        # Cleanup: delete the bucket after the test is done
        print(f"Bucket '{bucket_name}' : Deleting the bucket after test.")
        try:
            # First delete the objects in the bucket (Delete all versions)
            print(f"Bucket '{bucket_name}' : First Deleting objects and versions")
            delete_all_objects_in_bucket(s3_client, bucket_name)
            print(f"Bucket '{bucket_name}' : Objects and versions deleted successfully.")

            # Now delete the bucket
            print(f"Bucket '{bucket_name}' : Now Deleting the bucket")
            s3_client.delete_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' : Bucket deleted successfully.")
        
        except ClientError as e:
            print(f"Error occurred while cleaning up bucket '{bucket_name}': {e}")
            raise  # Re-raise the exception so pytest handles it properly


@pytest.fixture(scope='session')
def create_second_bucket(s3_client):
    """
    Create Second Bucket:
    - region: us-east-1
    - No objects
    - versioning disabled
    - public access is Blocked (i.e 'Block all public access' setting is Checked, set to "on")
    - No lifecycle policy
    """
    bucket_name = f'pytest-2-{generate_random_string(8)}'
    region = 'us-east-1'

    try:
        # Step 1: Create the S3 bucket
        print(f"Bucket '{bucket_name}' : Create bucket in region {region}.")
        response = s3_client.create_bucket(Bucket=bucket_name)
        
        # Wait for the bucket to be created by checking if it's accessible
        waiter = s3_client.get_waiter('bucket_exists')
        print(f"Waiting for the bucket '{bucket_name}' to be created...")
        
        # Wait until the bucket is created (exists)
        waiter.wait(Bucket=bucket_name)

        bucket_creation_date = response["ResponseMetadata"]["HTTPHeaders"]["date"]
        print(f"Bucket '{bucket_name}' : bucket created in {region} successfully.")

        # Yield the bucket name for testing
        yield bucket_name, bucket_creation_date

    except ClientError as e:
        print(f"Error occurred during bucket '{bucket_name}' creation: {e}")
        raise  # Re-raise the exception so pytest handles it properly

    finally:
        # Cleanup: delete the bucket after the test is done
        print(f"\nBucket '{bucket_name}' : Deleting the bucket after test.")
        try:
            # Delete the bucket
            s3_client.delete_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' : deleted successfully.")

        except ClientError as e:
            print(f"Error occurred while cleaning up bucket '{bucket_name}': {e}")
            raise  # Re-raise the exception so pytest handles it properly
