from typing import Optional
from flask import Blueprint, jsonify, current_app, request, Request
from user_profile_service import  database
from user_profile_service.models import Profile
from .services import profile_service
from .routes_utils import check_token
import jwt

api = Blueprint('api', __name__)


def get_profile()-> Optional[Profile]:
    token = request.headers['authorization'].split(' ')[1]
    profile: dict | None = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    p =  database.find_by_username(Profile, username=profile['username'])
    return p


@api.get('/profiles')
def get_all_profiles():
    profiles = database.get_all(Profile)
    return  jsonify([profile.to_dict() for profile in profiles])


@api.put('/profiles/basic-info')
@check_token
def edit_profile():
    profile = get_profile()
    if not profile: return 'profile not found', 400
    
    data = request.json
    profile = profile_service.edit_basic_info(data, profile)
    return jsonify(profile.to_dict())


@api.put('/profiles/work-experience')
@check_token
def edit_profile_work_experience():
    profile = get_profile()
    if not profile: return 'profile not found', 400
    
    experience = profile_service.create_or_update_work_experience(data=request.json, profile=profile)
    return jsonify(experience.to_dict())


@api.put('/profiles/education')
@check_token
def edit_profile_education():
    profile = get_profile()
    if not profile: return 'profile not found', 400

    education = profile_service.create_or_update_education(data=request.json, profile=profile)
    return jsonify(education.to_dict())


@api.put('/profiles/skills')
@check_token
def edit_profile_skills():
    profile = get_profile()
    if not profile: return 'profile not found', 400
    if not request.json.get('skills'): return 'did not receive skills', 400
    profile = profile_service.create_or_update_skills(skills=request.json.get('skills'), profile=profile)
    return jsonify(profile.to_dict())


@api.put('/profiles/interests')
@check_token
def edit_profile_interests():
    profile = get_profile()
    if not profile: return 'profile not found', 400
    if not request.json.get('interests'): return 'did not receive interests', 400
    profile = profile_service.create_or_update_interests(interests=request.json.get('interests'), profile=profile)
    return jsonify(profile.to_dict())
