from flask import Blueprint, jsonify
from user_profile_service import  database
from user_profile_service.models import Profile

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
def get_all_profiles():
    profiles = database.get_all(Profile)

    return  jsonify([profile.to_dict() for profile in profiles]), 200