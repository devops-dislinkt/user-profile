from flask import request, current_app
from functools import wraps
import jwt

def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('authorization'): 
            return {'message': 'No token provided'}, 400
    
        try:
            # verify token
            token = request.headers['authorization'].split(' ')[1]
            user = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 400
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 400
        except:
            return 'Problem with authentication.', 400

        return f(*args, **kwargs)
    return wrap