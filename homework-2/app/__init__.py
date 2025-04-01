import os
from flask import Flask

from app.utils.utils import generate_secret_key
from app.api.v1.s3 import s3
from app.api.v1.auth import auth
from app.api.v1.dashboard import dashboard


# application factory function
def create_app(test_config=None):
    """
    Flask application factory function,
    create and configure the app
    """
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        # Get the path to the config.py file inside the 'config' folder
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.py')
        app.config.from_pyfile(config_path)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # SQLite database will reside in memory
    app.config['DATABASE'] = ':memory:'

    # Generate a dynamic secret key
    app.config['SECRET_KEY'] = generate_secret_key()

    from app.db import db

    with app.app_context():
        db.init_db()

    # Register auth Blueprint with the app
    app.register_blueprint(auth.bp)

    # Register S3 Blueprint with the app
    app.register_blueprint(s3.bp)
    
    # Register dashboard Blueprint with the app
    app.register_blueprint(dashboard.bp)

    return app
