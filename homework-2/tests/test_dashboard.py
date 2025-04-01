from pprint import pprint


def test_get_dashboard_summary(create_first_bucket, create_second_bucket, authenticated_client):
    """
        Test valid get dashboard summary api request
        - GET /api/v1/dashboard/summary
        Verify: 
        - Respone status code 200, 
        - Response body
    """
    print(f"\n<<<<<<<<<< Get Dashboard Summary >>>>>>>>>>>>>>")

    response = authenticated_client.get(f'/api/v1/dashboard/summary')
    
    # status code
    assert response.status_code == 200
    assert response.is_json
    actual_result = response.json

    print(f"Actual get_buckets_summary resualt is: ")
    pprint(actual_result)

    expected_result = {'summary': {'ebs': {},
                                   'ecs': {},
                                   'network': {},
                                    's3': {
                                        'buckets_without_encryption': 0,
                                        'publicly_accessible_buckets': 1,
                                        'total_buckets': 2,
                                        'total_storage_gb': 2.9802322387695312e-08}
                                    }}
    
    print(f'Expected get_buckets_summary resualt is: ')
    pprint(expected_result)
    assert actual_result == expected_result

# ToDo - Add more Dashboard summary test coverage - for user not authenticated use case