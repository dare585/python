import boto3
import random
import string
import secrets
from flask import g
from datetime import datetime
from botocore.exceptions import ClientError

from app.db.db import get_db
from app.services.s3 import S3BucketManager


def generate_secret_key(length=24):
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(length)


def generate_random_string(length: int = 8) -> str:
    """
        Generate rundom string from lower case chars and digits, of length "length"
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def convert_date(date_str: str) -> str:
    """
    Get date string of this form Tue, 18 Mar 2025 18:54:24 GMT'
    and convert it to date string of this form '2025-03-18T18:54:24Z'
    """
    # Parse the date string into a datetime object
    dt_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')

    # Convert the datetime object to the desired string format
    formatted_date = dt_obj.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Return the formatted date
    return formatted_date


def has_expired(session_expiration: datetime) -> bool:
    """
        Check if the current time has passed the expiration datetime.

        Args:
        session_expiration (datetime.datetime): The expiration date (UTC) to compare with the current time.

        Returns:
        bool: True if the current time is greater than the expiration datetime, False otherwise.
    """
    # Get the current time (in UTC)
    current_time = datetime.utcnow()

    # Compare the current time with the expiration time
    return current_time > session_expiration


def get_session_expiration_as_str(session_expiration: datetime) -> str:
    """
        get session_expiration as datetime.datetime object, utc time
        return UTC timestamp of the form "2025-03-06T14:30:00Z"
    """
    # Format the expiration date as per the required format
    session_expiration_as_str = session_expiration.strftime('%Y-%m-%dT%H:%M:%SZ')

    return session_expiration_as_str


def delete_session_from_db() -> None:
    """
        delete the session row from the database if exist
    """
    if g.user:
        session_id = g.user['session_id']
        db = get_db()
        db.execute(
        'DELETE FROM aws_config WHERE session_id = ?', (session_id,))
        db.commit()


def get_s3_manager():
    """
        Get S3BucketManager of with temporary credentials of current user session
    """
    s3_manager = S3BucketManager(g.user['aws_access_key_id'], \
                                 g.user['aws_secret_access_key'], \
                                 g.user['aws_session_token'], \
                                 g.user['aws_region'])
    return s3_manager


def get_temporary_aws_credentials(aws_access_key_id, aws_secret_access_key, \
                                  aws_region, session_duration=3600):
    """
        Get temporary AWS credentials
        Default session duration is 3600 seconds (1 hour)
        raises ClientError in case of an AWS exception
    """
    try:
        # Create an STS client with provided credentials
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )

        # Request temporary session credentials with custom duration
        response = sts_client.get_session_token(DurationSeconds=session_duration)

        # The response contains the temporary credentials
        temp_credentials = response['Credentials']
        expiration = response['Credentials']['Expiration']
        expiration_as_str = get_session_expiration_as_str(expiration)
        
        return temp_credentials, expiration_as_str  # Returns temporary credentials and expiration time

    except ClientError as e:
        raise
