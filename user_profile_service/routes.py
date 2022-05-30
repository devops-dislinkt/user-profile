from flask import Blueprint, jsonify, current_app
from user_profile_service import  database
from user_profile_service.models import Profile

api = Blueprint('api', __name__)

@api.get('/profiles')
def get_all_profiles():
    profiles = database.get_all(Profile)
    return  jsonify([profile.to_dict() for profile in profiles])