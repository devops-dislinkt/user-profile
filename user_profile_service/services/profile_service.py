from user_profile_service.models import Profile
from user_profile_service import  database
from user_profile_service.models import Profile, Experience, Education
from datetime import datetime


def create_profile(username: str):
    database.add_or_update(Profile(username=username))

def create_or_update_work_experience(data:dict, profile: Profile) -> Experience:
    data['profile_id'] = profile.id
    data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d')
    data['end_date'] = datetime.strptime(data['end_date'], '%Y-%m-%d')
    work_experience = Experience(fields=data)

    # if work experience exists -> update work experience, otherwise create work experience
    found_experience: Experience | None = Experience.query.filter_by(profile_id=profile.id).first()
    if  found_experience: work_experience.id = found_experience.id
    return database.add_or_update(work_experience)

def edit_basic_info(data:dict, profile: Profile):
    data['profile_id'] = profile.id
    data['birthday'] = datetime.strptime(data['birthday'], '%Y-%m-%d')
    database.edit_instance(Profile, profile.id, fields=data)
    return profile

def create_or_update_education(data:dict, profile: Profile) -> Education:
    data['profile_id'] = profile.id
    education = Education(fields=data)

    # if education exists -> update education, otherwise create education
    found_education: Education | None = Education.query.filter_by(profile_id=profile.id).first()
    if found_education: education.id = found_education.id
    return database.add_or_update(education)
    