import os
import psycopg2

import pytest
from user_profile_service import create_app, db
from user_profile_service.models import Profile, Following
from flask.testing import FlaskClient


PRIVATE_PROFILE_USER_1 = "john_private"
PRIVATE_PROFILE_USER_2 = "lo_private"
PUBLIC_PROFILE_USER_1 = "john_public"
PUBLIC_PROFILE_USER_2 = "lo_public"
INVALID_USER = "invalid_user"
SEARCH_INPUT = "john"
INVALID_ID = 100
PUBLIC_VALID_ID = 1
PRIVATE_VALID_ID = 2
SEARCH_RESULT = [PRIVATE_PROFILE_USER_1, PUBLIC_PROFILE_USER_1]


def seed_db():
    profiles = [
        Profile(
            {
                "username": PUBLIC_PROFILE_USER_1,
                "email": "john@gmail.com",
                "first_name": "John",
                "last_name": "Smith",
                "phone_number": "+938480",
                "birthday": "1995-04-25",
                "biography": "Lorem",
                "private": False,
            }
        ),
        Profile(
            {
                "username": PRIVATE_PROFILE_USER_1,
                "email": "john@gmail.com",
                "first_name": "John",
                "last_name": "Smith",
                "phone_number": "+938480",
                "birthday": "1995-04-25",
                " biography": "Lorem",
                "private": True,
            }
        ),
        Profile(
            {
                "username": PRIVATE_PROFILE_USER_2,
                "email": "john@gmail.com",
                "first_name": "John",
                "last_name": "Smith",
                "phone_number": "+938480",
                "birthday": "1995-04-25",
                " biography": "Lorem",
                "private": True,
            }
        ),
        Profile(
            {
                "username": PUBLIC_PROFILE_USER_2,
                "email": "john@gmail.com",
                "first_name": "John",
                "last_name": "Smith",
                "phone_number": "+938480",
                "birthday": "1995-04-25",
                " biography": "Lorem",
                "private": False,
            }
        ),
    ]
    db.session.bulk_save_objects(profiles)
    db.session.commit()
    profiles = Profile.query.all()
    following_req = [
        Following(
            follower_id=profiles[0].id, following_id=profiles[1].id, approved=True
        ),
        Following(
            follower_id=profiles[2].id, following_id=profiles[1].id, approved=False
        ),
    ]
    db.session.bulk_save_objects(following_req)
    db.session.commit()


@pytest.fixture(scope="module")
def client() -> FlaskClient:
    """
    Initlializes flask client app which is used to mock requests.
    Returns flask client app.
    """
    # setup
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_db()

    with app.test_client() as client:
        yield client

    # teardown
    with app.app_context():
        db.drop_all()


class TestSearchProfile:
    """Test case for search another profile."""

    def test_search_profile(self, client: FlaskClient):
        response = client.get(f"/profile/search?username={SEARCH_INPUT}")

        assert response.status_code == 200
        assert len(response.json) == 2
        for profile in response.json:
            assert profile.get("username") in SEARCH_RESULT


class TestViewProfile:
    """Test case for viewing user's profile."""

    def test_view_public_profile_visitor(self, client: FlaskClient):
        response = client.get(f"/profile/{PUBLIC_VALID_ID}")

        assert response.status_code == 200
        assert response.json.get("id") == PUBLIC_VALID_ID
        assert response.json.get("username") == PUBLIC_PROFILE_USER_1
        assert "education" in response.json
        assert "work_experience" in response.json

    def test_view_public_profile_loggedin(self, client: FlaskClient):
        response = client.get(
            f"/profile/{PUBLIC_VALID_ID}", headers={"user": PRIVATE_PROFILE_USER_2}
        )

        assert response.status_code == 200
        assert response.json.get("id") == PUBLIC_VALID_ID
        assert response.json.get("username") == PUBLIC_PROFILE_USER_1
        assert "education" in response.json
        assert "work_experience" in response.json

    def test_view_public_profile_invalid_id(self, client: FlaskClient):
        response = client.get(f"/profile/{INVALID_ID}")

        assert response.status_code == 404

    def test_view_private_profile_visitor(self, client: FlaskClient):
        response = client.get(f"/profile/{PRIVATE_VALID_ID}")

        assert response.status_code == 403

    def test_view_private_profile_loggedin(self, client: FlaskClient):
        response = client.get(
            f"/profile/{PRIVATE_VALID_ID}", headers={"user": PUBLIC_PROFILE_USER_2}
        )

        assert response.status_code == 403

    def test_view_private_profile_follower(self, client: FlaskClient):
        response = client.get(
            f"/profile/{PRIVATE_VALID_ID}", headers={"user": PRIVATE_PROFILE_USER_1}
        )

        assert response.status_code == 403

    def test_view_private_profile_follower_approved(self, client: FlaskClient):
        response = client.get(
            f"/profile/{PRIVATE_VALID_ID}", headers={"user": PUBLIC_PROFILE_USER_1}
        )
        profiles = Profile.query.all()
        print(profiles[1].id)
        assert response.status_code == 200
        assert response.json.get("id") == PRIVATE_VALID_ID
        assert response.json.get("username") == PRIVATE_PROFILE_USER_1
        assert "education" in response.json
        assert "work_experience" in response.json
