from flask import Blueprint, g, jsonify

from app.api.v1.auth.auth import login_required
from app.utils.utils import get_s3_manager

bp = Blueprint('s3', __name__, url_prefix='/api/v1/s3')


@bp.get('/buckets')
@login_required
def buckets():
    """
    GET /api/v1/s3/buckets
    List All s3 buckets
    """
    s3_manager = get_s3_manager()
    return jsonify(s3_manager.list_s3_buckets())


@bp.get('/buckets/<bucket_name>/details')
@login_required
def bucket_details(bucket_name):
    """
    GET /api/v1/s3/buckets/{bucket_name}/details
    Get a bucket name and return this bucket details
    """
    s3_manager = get_s3_manager()
    return jsonify(s3_manager.get_bucket_details(bucket_name))