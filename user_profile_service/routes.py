from datetime import datetime
from typing import Optional
from flask import Blueprint, jsonify, current_app, request, Request
from user_profile_service import  database
from user_profile_service.models import Profile, Experience
from .services.profile_service import create_or_update_work_experience

api = Blueprint('api', __name__)

def get_profile(request: Request) -> Optional[Profile]:
    '''returns profile object if exists.'''
    data:dict = request.json
    if not data.get('username'): return 'did not receive username', 400
    username: str = data.get('username')
    found = database.find_by_username(Profile, username)
    return found

@api.get('/profiles')
def get_all_profiles():
    profiles = database.get_all(Profile)
    return  jsonify([profile.to_dict() for profile in profiles])


@api.put('/profiles/basic-info')
def edit_profile():
    user = get_profile(request)
    if not user: return 'user not found', 400
    data = request.json
    #convert date to a
    data['birthday'] = datetime.strptime(data['birthday'], '%Y-%m-%d')
    database.edit_instance(Profile, user.id, fields=data)
    return jsonify(user.username)

@api.put('/profiles/work-experience')
def edit_profile_work_experience():
    # TODO: dodati da se proverava da li je ulogovani korisni isto sto i profile_id poslat u requestu
    profile = get_profile(request)
    if not profile: return 'profile not found', 400
    data = request.json
    
    work_experience = create_or_update_work_experience(data, profile=profile)

    return jsonify(work_experience.get_attributes_as_dict())
