import functools
import uuid
from flask import Blueprint, current_app, abort, g, request, session, jsonify
from pydantic import ValidationError
from botocore.exceptions import ClientError

from app.db.db import get_db
from app.models.auth_model import AuthRequestModel
from app.utils.utils import has_expired, delete_session_from_db, \
    get_temporary_aws_credentials

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@bp.post('/login')
def login():
    """
    POST /api/v1/auth/login
    Request
        {
        "aws_access_key_id": "<aws_access_key_id>",
        "aws_secret_access_key": "<aws_secret_access_key>",
        "aws_region": "<aws_region>"
        }

    Response
        {
            "expires_at": "2025-03-06T14:30:00Z"
        }

    get user AWS credentials and obtain AWS temporary credentials using STS

    In case user send /login api with a session cookie already set, 
    then if session_id exist in the DB, then we delete this user row from DB
    and in any case we cleare the session, 
    and obtain new temporary AWS credentials and send a new session
    in the response
    """
    data = AuthRequestModel(**request.json) # pydantic validation
    aws_access_key_id = data.aws_access_key_id
    aws_secret_access_key = data.aws_secret_access_key
    aws_region = data.aws_region
    db = get_db()


    # Get temporary AWS credentials
    session_duration = current_app.config['SESSION_TIMEOUT_SECONDS']
    try:
        temp_credentials, session_expiration = get_temporary_aws_credentials(aws_access_key_id, \
                                                                             aws_secret_access_key, \
                                                                             aws_region, session_duration)
    except ClientError as e:
        # If credentials are invalid, respond with a 401 Unauthorized status
        abort(401, description=str(e))

    temp_aws_access_key_id = temp_credentials['AccessKeyId']
    temp_aws_secret_access_key = temp_credentials['SecretAccessKey']
    temp_aws_session_token = temp_credentials['SessionToken']

    session_id = str(uuid.uuid4())

    # In case user send "/login" api with a session cookie already set 
    # and exist in DB, we delete it from DB (and just create new session for the user)
    delete_session_from_db()

    db.execute(
            "INSERT INTO aws_config (session_id, aws_access_key_id, aws_secret_access_key, aws_session_token, aws_region, session_expiration) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, temp_aws_access_key_id, temp_aws_secret_access_key, temp_aws_session_token, aws_region, session_expiration),
        )
    db.commit()

    session.clear()
    session['session_id'] = session_id

    res = {"expires_at": session_expiration}
    return res


# Custom error handling for pydantic validation errors
@bp.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError):
    # Customize the error response
    return jsonify({
        "validation_error": {
            "body_params": [{"field": error['loc'][0], "message": error['msg'], "type": error['type']} \
                            for error in error.errors()]
        }
    }), 400


# registers a function that runs before the view function
# no matter what URL is requested
@bp.before_app_request
def load_logged_in_user():
    """
    checks if a session_id is stored in the session object,
    and gets that session data from the database, 
    storing it on g.user, which lasts for the length of the request. 
    If there is no session_id, or if the session_id doesn’t exist, g.user will be None.
    """
    session_id = session.get('session_id')

    # Empty session in the request
    if session_id is None:
        g.user = None
    # session in the request coockie
    else:
        g.user = get_db().execute(
            'SELECT * FROM aws_config WHERE session_id = ?', (session_id,)
        ).fetchone()


def login_required(view):
    """
    This decorator returns a new view function 
    that wraps the original view it’s applied to. 
    The new function checks if a user is loaded and that this user 
    credential did not expired, 
    if so the original view is called and continues normally,
    else return 401 Unauthorized response
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # Check if user is Not logged in
        if g.user is None:
            abort(401, description="User not logged in")
        # Check if the credentials expired
        session_expiration = g.user['session_expiration']
        if has_expired(session_expiration):
            # If expired, delete the user's row from the database, and abort
            delete_session_from_db()
            abort(401, description="User credentials expired")
        return view(**kwargs)

    return wrapped_view


# ToDo - 
# Implement Periodic Task for Deleting Expired session Rows from DB
