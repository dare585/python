from pprint import pprint

from app.utils.utils import convert_date


def test_list_s3_buckets(create_first_bucket, create_second_bucket, authenticated_client):
    """
        Test valid list s3 buckets api request
        - GET /api/v1/s3/buckets
        Verify: 
        - Respone status code 200, 
        - Response body
    """
    first_bucket_name, first_bucket_creation_date = create_first_bucket
    second_bucket_name, second_bucket_creation_date = create_second_bucket

    print(f"<<<<<<<<<< List S3 Buckets >>>>>>>>>>>>>>")
    
    response = authenticated_client.get('/api/v1/s3/buckets')
    
    # status code
    assert response.status_code == 200
    assert response.is_json
    actual_result = response.json

    print(f'Actual list_s3_buckets resualt is: ')
    pprint(actual_result)
    
    expected_result = {'buckets': [{'creation_date': convert_date(first_bucket_creation_date),
                        'name': first_bucket_name,
                        'object_count': 2,
                        'public_access_blocked': False,
                        'region': 'us-east-2',
                        'total_size_bytes': 32,
                        'versioning_enabled': True},
                        {'creation_date': convert_date(second_bucket_creation_date),
                        'name': second_bucket_name,
                        'object_count': 0,
                        'public_access_blocked': True,
                        'region': 'us-east-1',
                        'total_size_bytes': 0,
                        'versioning_enabled': False}]}
    
    print(f'Expected list_s3_buckets resualt is: ')
    pprint(expected_result)
    assert actual_result == expected_result


def test_get_bucket_details_first_bucket(create_first_bucket, authenticated_client):
    """
        Test valid get bucket details api request on first bucket
        - GET /api/v1/s3/buckets/{bucket_name}/details
        Verify: 
        - Respone status code 200, 
        - Response body
    """
    bucket_name, bucket_creation_date = create_first_bucket

    print(f"\n<<<<<<<<<< Get bucket Details ----> {bucket_name} >>>>>>>>>>>>>>")

    response = authenticated_client.get(f'/api/v1/s3/buckets/{bucket_name}/details')
    
    # status code
    assert response.status_code == 200
    assert response.is_json
    actual_result = response.json

    print(f"Actual get_bucket_details resualt for bucket '{bucket_name}' is: ")
    pprint(actual_result)

    expected_result = {'creation_date': convert_date(bucket_creation_date),
                        'encryption': {'enabled': True, 'type': 'AES256'},
                        'lifecycle_rules': [{'id': 'Pytest lifecycle Configuration',
                                            'status': 'Enabled',
                                            'transitions': [{'days': 30,
                                                            'storage_class': 'STANDARD_IA'},
                                                            {'days': 90,
                                                            'storage_class': 'GLACIER'}]}],
                        'name': bucket_name,
                        'region': 'us-east-2',
                        'storage_class_summary': {'STANDARD': 2}}
    
    print(f"Expected get_bucket_details resualt for bucket '{bucket_name}' is: ")
    pprint(expected_result)
    assert actual_result == expected_result


def test_get_bucket_details_second_bucket(create_second_bucket, authenticated_client):
    """
        Test valid get bucket details api request on second bucket
        - GET /api/v1/s3/buckets/{bucket_name}/details
        Verify: 
        - Respone status code 200, 
        - Response body
    """
    bucket_name, bucket_creation_date = create_second_bucket

    print(f"\n<<<<<<<<<< Get bucket Details ----> {bucket_name} >>>>>>>>>>>>>>")
    
    response = authenticated_client.get(f'/api/v1/s3/buckets/{bucket_name}/details')
    
    # status code
    assert response.status_code == 200
    assert response.is_json
    actual_result = response.json

    print(f"Actual get_bucket_details resualt for bucket '{bucket_name}' is: ")
    pprint(actual_result)

    expected_result = {'creation_date': convert_date(bucket_creation_date),
                        'encryption': {'enabled': True, 'type': 'AES256'},
                        'lifecycle_rules': [],
                        'name': bucket_name,
                        'region': 'us-east-1',
                        'storage_class_summary': {}}
    
    print(f"Expected get_bucket_details resualt for bucket '{bucket_name}' is: ")
    pprint(expected_result)
    assert actual_result == expected_result

# ToDo - Add more S3 Monitoring test coverage - for user not authenticated use case