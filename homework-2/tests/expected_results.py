expected_auth_invalid_body = {"keys_all_empty_strings": {'validation_error':
                                                        {'body_params': [
                                                        {  'field': 'aws_access_key_id',
                                                            'message': 'Value error, AWS Access Key '
                                                                        'ID cannot be empty',
                                                            'type': 'value_error'},
                                                            {'field': 'aws_secret_access_key',
                                                            'message': 'Value error, AWS Secret '
                                                                        'Access Key cannot be empty',
                                                            'type': 'value_error'},
                                                            {'field': 'aws_region',
                                                            'message': 'Input should be '
                                                                        "'us-east-1', 'us-east-2', "
                                                                        "'us-west-1', 'us-west-2', "
                                                                        "'eu-west-1', 'eu-west-2', "
                                                                        "'eu-west-3', 'eu-north-1', "
                                                                        "'eu-central-1', "
                                                                        "'ca-central-1', "
                                                                        "'ap-south-1', "
                                                                        "'ap-northeast-1', "
                                                                        "'ap-northeast-2', "
                                                                        "'ap-northeast-3', "
                                                                        "'ap-southeast-1', "
                                                                        "'ap-southeast-2' or "
                                                                        "'sa-east-1'",
                                                            'type': 'enum'}]}},
                                "keys_all_None": {'validation_error': 
                                                        {'body_params': [
                                                            {'field': 'aws_access_key_id',
                                                                'message': 'Input should be a valid '
                                                                            'string',
                                                                'type': 'string_type'},
                                                                {'field': 'aws_secret_access_key',
                                                                'message': 'Input should be a valid '
                                                                            'string',
                                                                'type': 'string_type'},
                                                                {'field': 'aws_region',
                                                                'message': 'Input should be '
                                                                            "'us-east-1', 'us-east-2', "
                                                                            "'us-west-1', 'us-west-2', "
                                                                            "'eu-west-1', 'eu-west-2', "
                                                                            "'eu-west-3', 'eu-north-1', "
                                                                            "'eu-central-1', "
                                                                            "'ca-central-1', "
                                                                            "'ap-south-1', "
                                                                            "'ap-northeast-1', "
                                                                            "'ap-northeast-2', "
                                                                            "'ap-northeast-3', "
                                                                            "'ap-southeast-1', "
                                                                            "'ap-southeast-2' or "
                                                                            "'sa-east-1'",
                                                                'type': 'enum'}]}},
                                "invalid_region": {'validation_error': 
                                                   {'body_params': 
                                                    [{'field': 'aws_region',
                                                        'message': 'Input should be '
                                                                    "'us-east-1', 'us-east-2', "
                                                                    "'us-west-1', 'us-west-2', "
                                                                    "'eu-west-1', 'eu-west-2', "
                                                                    "'eu-west-3', 'eu-north-1', "
                                                                    "'eu-central-1', "
                                                                    "'ca-central-1', "
                                                                    "'ap-south-1', "
                                                                    "'ap-northeast-1', "
                                                                    "'ap-northeast-2', "
                                                                    "'ap-northeast-3', "
                                                                    "'ap-southeast-1', "
                                                                    "'ap-southeast-2' or "
                                                                    "'sa-east-1'",
                                                        'type': 'enum'}]}},
                                "invalid_keys_type": {'validation_error': 
                                                      {'body_params': 
                                                       [{'field': 'aws_access_key_id',
                                                        'message': 'Input should be a valid '
                                                                    'string',
                                                        'type': 'string_type'},
                                                        {'field': 'aws_secret_access_key',
                                                        'message': 'Input should be a valid '
                                                                    'string',
                                                        'type': 'string_type'},
                                                        {'field': 'aws_region',
                                                        'message': 'Input should be '
                                                                    "'us-east-1', 'us-east-2', "
                                                                    "'us-west-1', 'us-west-2', "
                                                                    "'eu-west-1', 'eu-west-2', "
                                                                    "'eu-west-3', 'eu-north-1', "
                                                                    "'eu-central-1', "
                                                                    "'ca-central-1', "
                                                                    "'ap-south-1', "
                                                                    "'ap-northeast-1', "
                                                                    "'ap-northeast-2', "
                                                                    "'ap-northeast-3', "
                                                                    "'ap-southeast-1', "
                                                                    "'ap-southeast-2' or "
                                                                    "'sa-east-1'",
                                                        'type': 'enum'}]}},
                                "empty_request_body": {'validation_error': 
                                                        {'body_params': 
                                                        [{'field': 'aws_access_key_id',
                                                            'message': 'Field required',
                                                            'type': 'missing'},
                                                            {'field': 'aws_secret_access_key',
                                                            'message': 'Field required',
                                                            'type': 'missing'},
                                                            {'field': 'aws_region',
                                                            'message': 'Field required',
                                                            'type': 'missing'}]}}
                                                            }
