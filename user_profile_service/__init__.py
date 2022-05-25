from flask import Flask

from .models import db
from . import config

def create_app():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.app_context().push()
    db.init_app(flask_app)
    db.create_all()

    from user_profile_service.views import profile_bp

    flask_app.register_blueprint(profile_bp, url_prefix='/api')

    return flask_app

