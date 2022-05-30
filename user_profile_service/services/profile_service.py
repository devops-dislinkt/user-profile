from user_profile_service.models import Profile
from user_profile_service import  database

def create_profile(username: str):
    database.add_instance(Profile, username=username)