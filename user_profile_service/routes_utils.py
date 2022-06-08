from flask import request, current_app, jsonify
from functools import wraps
import jwt
from user_profile_service import  database
from .routes import api
from sqlalchemy.exc import NoResultFound


def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('authorization'): 
            return {'message': 'No token provided'}, 401
    
        try:
            # verify token
            token = request.headers['authorization'].split(' ')[1]
            user = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            found_user = database.find_by_username(username=user['username'])

            if not found_user: return f'not found user with username: {user["username"]}', 401
        
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 401
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 401
        except:
            return 'Problem with authentication.', 401

        return f(*args, **kwargs)
    return wrap


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