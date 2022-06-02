from user_profile_service.models import Profile
from user_profile_service import  database
from user_profile_service.models import Profile, Experience
from datetime import datetime


def create_profile(username: str):
    database.add_or_update(Profile(username=username))

def create_or_update_work_experience(data:dict, profile: Profile) -> Experience:
    work_experience = Experience(profile_id=profile.id,
                        title=data['title'],
                        type=data['type'],
                        company=data['company'],
                        location=data['location'],
                        currently_working=data['currently_working'],
                        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
                        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d')
                        )

        
    
    # if work experience exists -> update work experience, otherwise create work experience
    found_experience: Experience | None = Experience.query.filter_by(profile_id=profile.id).first()
    if  found_experience: work_experience.id = found_experience.id
    database.add_or_update(work_experience)
    return work_experience