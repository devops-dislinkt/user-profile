from user_profile_service.models import Profile, Following
from user_profile_service import  database
from sqlalchemy.exc import NoResultFound

def create_profile(username: str):
    database.add_instance(Profile(username=username))

def follow_profile(user : str, user_to_follow: str):
    profile = get_profile(user)
    profile_to_follow = get_profile(user_to_follow)

    request = Following(follower_id=profile.id, following_id=profile_to_follow.id)
    request.approved = False if profile_to_follow.private else True
    profile_to_follow.followers.append(request)
    database.add_instance(request)

def resolve_follow_req(username: str, follower_id: str, reject: bool):
    profile =  get_profile(username)
    request = Following.query.filter_by(follower_id=follower_id, following_id=profile.id)

    if (not request):
        raise NoResultFound("No request for user with given id")

    if (reject):
        request.delete()
    else:
        request.update({ 'approved': True })

    database.commit_changes()


def get_profile(username: str):
    profile = Profile.query.filter_by(username=username).first()
    if (not profile):
        raise NoResultFound("No user with given username")

    return profile