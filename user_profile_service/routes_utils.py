from flask import  jsonify
from .routes import api
from sqlalchemy.exc import NoResultFound


@api.errorhandler(KeyError)
def handle_key_error(e):
    return jsonify('Bad keys. Check json keys.'), 400

@api.errorhandler(NoResultFound)
def handle_key_error(e):
    return jsonify(str(e)), 404

# allow all origin
@api.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    return response