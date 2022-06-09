from user_profile_service.models import Profile, Following, Blocking
from user_profile_service import database
from user_profile_service.models import Profile, Experience, Education
from datetime import datetime
from sqlalchemy.exc import NoResultFound


def create_profile(username: str):
    database.add_or_update(Profile({"username": username}))


def create_or_update_work_experience(data: dict, profile: Profile) -> Experience:
    data["profile_id"] = profile.id
    data["start_date"] = datetime.strptime(data["start_date"], "%Y-%m-%d")
    data["end_date"] = datetime.strptime(data["end_date"], "%Y-%m-%d")
    work_experience = Experience(fields=data)

    # if work experience exists -> update work experience, otherwise create work experience
    found_experience: Experience | None = Experience.query.filter_by(
        profile_id=profile.id
    ).first()
    if found_experience:
        work_experience.id = found_experience.id
    return database.add_or_update(work_experience)


def edit_basic_info(data: dict, profile: Profile):
    data["profile_id"] = profile.id
    data["birthday"] = datetime.strptime(data["birthday"], "%Y-%m-%d")
    database.edit_instance(Profile, profile.id, fields=data)
    return profile


def create_or_update_education(data: dict, profile: Profile) -> Education:
    data["profile_id"] = profile.id
    education = Education(fields=data)

    # if education exists -> update education, otherwise create education
    found_education: Education | None = Education.query.filter_by(
        profile_id=profile.id
    ).first()
    if found_education:
        education.id = found_education.id
    return database.add_or_update(education)


def update_username(old_username: str, new_username: str):
    profile = get_profile(username=old_username)  # find user profile with old username
    profile.username = new_username  # update profile's username
    return database.add_or_update(profile)  # save updated


def create_or_update_skills(skills: str, profile: Profile):
    profile.skills = skills
    return database.add_or_update(profile)


def create_or_update_interests(interests: str, profile: Profile):
    profile.interests = interests
    return database.add_or_update(profile)


def follow_profile(user: str, user_to_follow: str):
    profile = get_profile(user)
    profile_to_follow = get_profile(user_to_follow)

    request = Following(follower_id=profile.id, following_id=profile_to_follow.id)
    request.approved = False if profile_to_follow.private else True
    profile_to_follow.followers.append(request)
    database.add_or_update(request)


def resolve_follow_req(username: str, follower_id: str, reject: bool):
    profile = get_profile(username)
    request = Following.query.filter_by(
        follower_id=follower_id, following_id=profile.id
    )

    if not request:
        raise NoResultFound("No request for user with given id")

    if reject:
        request.delete()
    else:
        request.update({"approved": True})

    database.commit_changes()


def get_profile(username: str):
    profile = Profile.query.filter_by(username=username).first()
    if not profile:
        raise NoResultFound(f"No user with given username: {username}")

    return profile


def search_profile(searched_username: str):
    profiles = Profile.query.filter(
        Profile.username.like("%" + searched_username + "%")
    )
    return profiles


def get_profile_by_id(id: int, logged_in_username=None):
    logged_in_user = get_profile(logged_in_username) if logged_in_username else None
    profile = Profile.query.get(id)
    if not profile:
        raise NoResultFound(f"No user with given id: {id}")
    if not profile.private:
        return profile

    if not logged_in_user and profile.private:
        return None
    followers = profile.followers
    for req in followers:
        if req.approved and req.follower_id == logged_in_user.id:
            return profile
    return None


def block_profile(username_to_block: str, profile: Profile) -> Blocking:
    """Blocks profile with provided username. Second arg is currently logged in profile."""
    profile_to_block: Profile = database.find_by_username(username_to_block)
    if not profile_to_block:
        raise NoResultFound(f"No user with given username: {username_to_block}")
    block = Blocking(blocker_id=profile.id, blocked_id=profile_to_block.id)
    profile.profiles_blocked_by_me.append(block)
    return database.add_or_update(block)
