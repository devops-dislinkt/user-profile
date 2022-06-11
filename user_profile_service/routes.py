from flask import Blueprint, jsonify, current_app, request, Request
from user_profile_service import database
from user_profile_service.models import Profile
from .services import profile_service
from flask import Blueprint, jsonify, request
from user_profile_service import database
from user_profile_service.models import Profile
from user_profile_service.services import profile_service
from sqlalchemy.exc import NoResultFound

api = Blueprint("api", __name__)  # private -> requires login

public_api = Blueprint("", __name__)
import user_profile_service.routes_utils

# EDIT PROFILE
# -------------
@api.get('/profile/me') 
def get_profile_details(): 
    user: str = request.headers.get('user') 
    profile = profile_service.get_profile(user) 
    if not profile: return 'profile not found', 400 
    return jsonify(profile.to_dict())

@api.get("/profile")
def get_all_profiles():
    profiles = database.get_all(Profile)
    return jsonify([profile.to_dict() for profile in profiles])


@api.put("/profile/basic-info")
def edit_profile():
    user: str = request.headers.get("user")
    profile = profile_service.get_profile(user)
    if not profile:
        return "profile not found", 400

    data = request.json
    profile = profile_service.edit_basic_info(data, profile)
    return jsonify(profile.to_dict())


@api.put("/profile/work-experience")
def edit_profile_work_experience():
    user: str = request.headers.get("user")
    profile = profile_service.get_profile(user)
    if not profile:
        return "profile not found", 400

    experience = profile_service.create_or_update_work_experience(
        data=request.json, profile=profile
    )
    return jsonify(experience.to_dict())


@api.put("/profile/education")
def edit_profile_education():
    user: str = request.headers.get("user")
    profile = profile_service.get_profile(user)
    if not profile:
        return "profile not found", 400

    education = profile_service.create_or_update_education(
        data=request.json, profile=profile
    )
    return jsonify(education.to_dict())


@api.put("/profile/skills")
def edit_profile_skills():
    user: str = request.headers.get("user")
    profile = profile_service.get_profile(user)
    if not profile:
        return "profile not found", 400
    if not request.json.get("skills"):
        return "did not receive skills", 400

    profile = profile_service.create_or_update_skills(
        skills=request.json.get("skills"), profile=profile
    )
    return jsonify(profile.to_dict())


@api.put("/profile/interests")
def edit_profile_interests():
    user: str = request.headers.get("user")
    profile = profile_service.get_profile(user)
    if not profile:
        return "profile not found", 400
    if not request.json.get("interests"):
        return "did not receive interests", 400

    profile = profile_service.create_or_update_interests(
        interests=request.json.get("interests"), profile=profile
    )
    return jsonify(profile.to_dict())


# BLOCK PROFILE
# --------------


@api.put("/profile/block")
def block_profile():
    user: str = request.headers.get("user")
    profile = profile_service.get_profile(user)
    if not profile:
        return "profile not found", 400
    if not request.json.get("profile_to_block"):
        return "did not receive profile to block", 400
    try:
        block = profile_service.block_profile(
            username_to_block=request.json.get("profile_to_block"), profile=profile
        )
        return jsonify(block.to_dict(only=("blocker_id", "blocked_id")))
    except NoResultFound:
        return "user not found", 404


# FOLLOW PROFILE
# ---------------


@api.post("/profile/follow")
def follow_profile():
    data = request.json
    user: str = request.headers.get("user")
    user_to_follow: str = data.get("user_to_follow")
    try:
        profile_service.follow_profile(user, user_to_follow)
    except Exception as e:
        return "Not valid params: {}".format(e), 404

    return "Follow request successfully sent", 200


@api.get("/profile/followers")
def get_all_followers():
    approved = request.args.get(
        "approved", default=False, type=lambda v: v.lower() == "true"
    )
    user: str = request.headers.get("user")
    try:
        user_profile = profile_service.get_profile(user)
        list = [
            request
            for request in user_profile.followers
            if request.approved == approved
        ]

        return jsonify(
            [
                profile.to_dict(only=("approved", "follower_id", "follower.username"))
                for profile in list
            ]
        )
    except Exception as e:
        return "Not valid params: {}".format(e), 404


@api.get("/profile/following")
def get_all_following():
    approved = request.args.get(
        "approved", default=False, type=lambda v: v.lower() == "true"
    )
    user: str = request.headers.get("user")
    try:
        user_profile = profile_service.get_profile(user)
        list = [
            request
            for request in user_profile.following
            if request.approved == approved
        ]
    except Exception as e:
        return "Not valid params: {}".format(e), 404

    return jsonify(
        [
            profile.to_dict(only=("approved", "following_id", "following.username"))
            for profile in list
        ]
    )


@api.post("/profile/followers")
def resolve_follow_request():
    data = request.json
    reject = data.get("reject").lower() == "true"
    user: str = request.headers.get("user")
    follower_id: str = data.get("follower_id")
    try:
        profile_service.resolve_follow_req(user, follower_id, reject)
    except Exception as e:
        return "Not valid params: {}".format(e), 404

    return "Request resolved", 200


@public_api.get("/profile/search")
def search_profile():
    search_input = request.args.get("username")
    profiles = profile_service.search_profile(search_input)

    return (
        jsonify([profile.to_dict(only=("username", "id")) for profile in profiles]),
        200,
    )


@public_api.get("/profile/<int:id>")
def get_profile_by_id(
    id: int,
):
    user: str = request.headers.get("user")
    try:
        profile = profile_service.get_profile_by_id(id, user)
    except NoResultFound as e:
        return "Not valid params: {}".format(e), 404
    if not profile:
        return "Profile is set to private", 403
    return profile.to_dict()
