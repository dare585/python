from flask import Blueprint, jsonify

from app.api.v1.auth.auth import login_required
from app.utils.utils import get_s3_manager


bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')


@bp.get('/summary')
@login_required
def summary():
    """
        GET /api/v1/dashboard/summary
        Return summary of all supported AWS services the app monitors
    """
    s3_manager = get_s3_manager()
    s3_summary = s3_manager.get_buckets_summary()

    summary = {
                "summary": {
                    "ecs": {},
                    "s3": s3_summary,
                    "ebs": {},
                    "network": {}
                }
              }
    return jsonify(summary)
