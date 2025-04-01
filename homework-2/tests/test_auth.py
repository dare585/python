import pytest
from flask import session
from datetime import datetime
from time import sleep

from app.db.db import get_db
from tests.expected_results import expected_auth_invalid_body


def test_auth_valid_login(client, app, aws_credentials):
    """
        Test valid login api request
        - POST /api/v1/auth/login
        - valid request body
        Verify: 
        - Respone status code 200, and response body
        - User row created in DB, with expected values
        - Session Cookie set, with session_id
    """
    aws_access_key_id = aws_credentials["aws_access_key_id"]
    aws_secret_access_key = aws_credentials["aws_secret_access_key"]
    aws_region = aws_credentials["aws_region"]

    # Use with client - to allow access to Flask session object
    with client:
        response = client.post('/api/v1/auth/login',
                               json={'aws_access_key_id': aws_access_key_id,
                                     'aws_secret_access_key': aws_secret_access_key,
                                     'aws_region': aws_region})
        # status code
        assert response.status_code == 200

        # Session Cookie set, with expected values
        assert response.headers.get('Set-Cookie') is not None
        assert session.get('session_id') is not None
        session_id = session['session_id']

        # DB row created, with expected values
        with app.app_context():
            user_row = get_db().execute(
                "SELECT * FROM aws_config WHERE session_id = ?",(session_id,)
            ).fetchone()

            assert user_row is not None

            user_row_columns = user_row.keys()
            user_row_columns.sort()

            assert user_row_columns == ['aws_access_key_id', 'aws_region', 'aws_secret_access_key', 'aws_session_token', 'id', 'session_expiration', 'session_id']
            # Verify temporary credentials set
            assert user_row["aws_access_key_id"] is not None
            assert user_row["aws_secret_access_key"] is not None
            assert user_row["aws_session_token"] is not None
            assert user_row["aws_access_key_id"] != aws_access_key_id
            assert user_row["aws_secret_access_key"] != aws_secret_access_key

            # verify aws region set
            assert user_row["aws_region"] == aws_region
            # verify session_expiration set
            assert user_row["session_expiration"] is not None
            assert isinstance(user_row["session_expiration"], datetime)
            session_expiration = user_row["session_expiration"].strftime('%Y-%m-%dT%H:%M:%SZ')

            # Check response
            assert response.json == {'expires_at': session_expiration}


@pytest.mark.parametrize(
    "aws_access_key_id, aws_secret_access_key, aws_region, message",
    [
        ('', '   ', '', expected_auth_invalid_body['keys_all_empty_strings']), # also test for whitespace value
        (None, None, None, expected_auth_invalid_body['keys_all_None']),
        ('test', 'test', 'does-not-exist', expected_auth_invalid_body['invalid_region']),
        (1, 2, 3, expected_auth_invalid_body['invalid_keys_type']),
        ('empty', 'empty', 'empty', expected_auth_invalid_body['empty_request_body'])
    ],
    ids=["keys_all_empty_strings", "keys_all_None", "invalid_region", "invalid_keys_type", 'empty_request_body']
)
def test_auth_invalidate_request(client, app, request, aws_access_key_id, aws_secret_access_key, aws_region, message):
    """
        Test Invalid login api
        - POST /api/v1/auth/login
        - Invalid request body:
          - keys all set as empty strings / whitespaces
          - wrong keys type (all None / all int)
          - invalid region
          - Empty request body
        Verify: 
        - Respone status code 400 (Bad Request), 
          Response body as json, with expected error message
        - No User row created in DB
        - No Session Cookie set
    """
    # Use with client - to allow access session object
    with client:
        # Get the full test ID (including parametrization)
        test_full_name = request.node.nodeid
        # Extract only the custom part of the ID if needed
        test_id = test_full_name.split('[')[-1].split(']')[0]
        
        if test_id == 'empty_request_body':
            request_body= {}
        else:
            request_body={'aws_access_key_id': aws_access_key_id, 
                          'aws_secret_access_key': aws_secret_access_key,
                          'aws_region': aws_region}

        response = client.post(
        '/api/v1/auth/login', json=request_body)

        # Bad request
        assert response.status_code == 400
        assert response.is_json
        response_json = response.get_json()
        assert response_json == message

        # No DB row created
        with app.app_context():
            rows = get_db().execute("SELECT * FROM aws_config").fetchall()

            assert len(rows) == 0 # empty list []

            # No Session Cookie set
            assert response.headers.get('Set-Cookie') is None
            # Empty session object, No session keys set
            assert not session.keys()


def test_auth_re_login_while_user_session_active(client, app, aws_credentials):
    """
        Test valid login api request, 
        send same login request, one after the other,
        such that second request is sent While the user already logged in
        i.e, while session of first request is still Active
        - POST /api/v1/auth/login
        - valid request body
        Expected:
            In case user send "/login" api with a session cookie already set, 
            then if session_id exist in the DB, then we delete this user row from DB 
            and obtain new temporary AWS credentials, create new row in DB,
            and send a new session_id in the response session cookie
        Verify: 
        - Respone status code 200, for first requests
        - Respone status code 200, and response body, for second requests
        - DB - exactly one row exist, with new values created for second request, 
          i.e, new temporary aws credentials, session_id and session_expiration, 
          same region
        - Session Cookie set in the second response, with new session_id
        - session object is set with new session_id of the second request
          
    """
    aws_access_key_id = aws_credentials["aws_access_key_id"]
    aws_secret_access_key = aws_credentials["aws_secret_access_key"]
    aws_region = aws_credentials["aws_region"]

    # Use with client - to allow access to Flask session object
    with client:
        res1 = client.post(
            '/api/v1/auth/login', json={'aws_access_key_id': aws_access_key_id, 
                                        'aws_secret_access_key': aws_secret_access_key,
                                        'aws_region': aws_region})
        # status code
        assert res1.status_code == 200

        # get first response session_id
        assert session.get('session_id') is not None
        first_session_id = session['session_id']

        # get DB row created for the first "login" request, 
        # to compare later with second "login" request DB row
        with app.app_context():
            user_row = get_db().execute(
                "SELECT * FROM aws_config WHERE session_id = ?",(first_session_id,)
            ).fetchone()

            first_id = user_row["id"]
            first_aws_access_key_id = user_row["aws_access_key_id"]
            first_aws_secret_access_key = user_row["aws_secret_access_key"]
            first_aws_session_token = user_row["aws_session_token"]
            first_session_expiration = user_row["session_expiration"].strftime('%Y-%m-%dT%H:%M:%SZ')

        # sleep 2 seconds, before sending second request
        # to make sure session_expiration wil be different between first and second requests
        sleep(2)
        res2 = client.post(
            '/api/v1/auth/login', json={'aws_access_key_id': aws_access_key_id, 
                                        'aws_secret_access_key': aws_secret_access_key,
                                        'aws_region': aws_region})
        # status code
        assert res2.status_code == 200

        # Session Cookie set, with expected values
        assert res2.headers.get('Set-Cookie') is not None
        assert session.get('session_id') is not None
        second_session_id = session['session_id']

        # verify new session_id created
        assert second_session_id != first_session_id

        # DB - exactly one row exist, new row created, with expected values
        with app.app_context():
            user_row = get_db().execute(
                "SELECT * FROM aws_config WHERE session_id = ?",(second_session_id,)
            ).fetchall()

            # Exactly one row exist
            assert len(user_row) == 1

            user_row = user_row[0]

            user_row_columns = user_row.keys()
            user_row_columns.sort()

            assert user_row_columns == ['aws_access_key_id', 'aws_region', 'aws_secret_access_key', 'aws_session_token', 'id', 'session_expiration', 'session_id']
            
            # verify new row created
            assert user_row["id"] != first_id
            # Verify new temporary credentials set
            assert user_row["aws_access_key_id"] is not None
            assert user_row["aws_secret_access_key"] is not None
            assert user_row["aws_session_token"] is not None
            assert user_row["aws_access_key_id"] != first_aws_access_key_id
            assert user_row["aws_secret_access_key"] != first_aws_secret_access_key
            assert user_row["aws_session_token"] != first_aws_session_token

            # verify same aws region set
            assert user_row["aws_region"] == aws_region
            # verify new session_expiration set
            assert user_row["session_expiration"] is not None
            assert isinstance(user_row["session_expiration"], datetime)
            second_session_expiration = user_row["session_expiration"].strftime('%Y-%m-%dT%H:%M:%SZ')

            # verify new session_expiration set
            assert second_session_expiration != first_session_expiration

            # Check response
            assert res2.json == {'expires_at': second_session_expiration}


# ToDo - Add more Auth test coverage 