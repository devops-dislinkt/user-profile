from flask import Blueprint, jsonify, request
from user_profile_service import database
from user_profile_service.models import Profile
from user_profile_service.services import profile_service
from sqlalchemy.exc import NoResultFound

api = Blueprint("api", __name__)


@api.get("/profiles")
def get_all_profiles():
    profiles = database.get_all(Profile)
    return jsonify([profile.to_dict() for profile in profiles])


@api.post("/profile/follow")
def follow_profile():
    data = request.json
    user: str = data.get("logged_in_user")
    user_to_follow: str = data.get("user_to_follow")
    try:
        profile_service.follow_profile(user, user_to_follow)
    except Exception as e:
        return "Not valid params: {}".format(e), 404

    return "Follow request successfully sent", 200


@api.get("/profile/followers")
def get_all_followers():
    data = request.json
    approved = request.args.get(
        "approved", default=False, type=lambda v: v.lower() == "true"
    )
    user: str = data.get("logged_in_user")
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
    data = request.json
    approved = request.args.get(
        "approved", default=False, type=lambda v: v.lower() == "true"
    )
    user: str = data.get("logged_in_user")
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
    user: str = data.get("logged_in_user")
    follower_id: str = data.get("follower_id")
    try:
        profile_service.resolve_follow_req(user, follower_id, reject)
    except Exception as e:
        return "Not valid params: {}".format(e), 404

    return "Request resolved", 200


@api.get("/profile/search")
def search_profile():
    search_input = request.args.get("username")
    profiles = profile_service.search_profile(search_input)

    return (
        jsonify([profile.to_dict(only=("username", "id")) for profile in profiles]),
        200,
    )


@api.get("/profile/<int:id>")
def get_profile_by_id(
    id: int,
):
    logged_in_username = request.args.get("username")
    try:
        profile = profile_service.get_profile_by_id(id, logged_in_username)
    except NoResultFound as e:
        return "Not valid params: {}".format(e), 404
    if not profile:
        return "Profile is set to private", 403
    return profile.to_dict()
