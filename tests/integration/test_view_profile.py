import os
from urllib import response
from wsgiref import headers
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
                "biography": "Lorem",
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
                "biography": "Lorem",
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
        """search without login should return all profiles."""
        response = client.get(f"/profile/search?username={SEARCH_INPUT}")

        assert response.status_code == 200
        assert len(response.json) == 2
        for profile in response.json:
            assert profile.get("username") in SEARCH_RESULT

    def test_search_profile_non_existing_profile(self, client: FlaskClient):
        """search without login should return all profiles."""
        response = client.get(f"/profile/search?username=TRASH")

        assert response.status_code == 200
        assert len(response.json) == 0


class TestViewProfile:
    """Test case for viewing user's profile."""

    def test_view_non_existing_profile(self, client: FlaskClient):
        '''Viewing nonexisting profile should raise an error'''
        username_to_find = 'trash'
        response = client.get(f'/profile/details/{username_to_find}')
        assert response.status_code == 404


    def test_view_public_profile_without_login(self, client: FlaskClient):
        '''everyone can view public profiles'''
        username_to_find = PUBLIC_PROFILE_USER_1
        response = client.get(f'/profile/details/{username_to_find}')
        assert response.status_code == 200
        assert response.json['username'] == username_to_find


    def test_view_public_profile_with_login(self, client: FlaskClient):
        '''everyone can view public profiles'''
        username_to_find = PUBLIC_PROFILE_USER_1
        response = client.get(f'/profile/details/{username_to_find}', headers={'user': PUBLIC_PROFILE_USER_2})
        assert response.status_code == 200
        assert response.json['username'] == username_to_find


    def test_view_private_profile_without_login(self, client: FlaskClient):
        '''everyone has partial access to private profile (username, first name, last name).'''
        username_to_find = PRIVATE_PROFILE_USER_1
        response = client.get(f'/profile/details/{username_to_find}')
        assert response.status_code == 200
        assert response.json['username'] == username_to_find
        assert response.json.get('birthday') == None


    def test_view_private_profile_with_login(self, client: FlaskClient):
        '''only logged and not blocked user has partial access to private profile'''
        username_to_find = PRIVATE_PROFILE_USER_1
        response = client.get(f'/profile/details/{username_to_find}', headers={'user': PUBLIC_PROFILE_USER_2})
        assert response.status_code == 200
        assert response.json['username'] == username_to_find
        assert response.json.get('birthday') == None

    def test_view_private_profile_with_approved_follow_request(self, client: FlaskClient):
        '''only logged in profile which has approved follow request, has full access to requested profile'''
        
        # user 1 sends follow request to user 2         
        response = client.post('/api/profile/follow', 
                        json={'user_to_follow': PRIVATE_PROFILE_USER_2},
                        headers={'user': PRIVATE_PROFILE_USER_1}) 
        assert response.status_code == 200

        # user 2 approves
        response = client.post('/api/profile/followers', 
                                json={'follower_id': PRIVATE_VALID_ID, 'reject': 'false'},
                                headers={'user': PRIVATE_PROFILE_USER_2}) 
        assert response.status_code == 200
        
        # user 1 sees user 2
        response = client.get(f'/profile/details/{PRIVATE_PROFILE_USER_2}', headers={'user': PRIVATE_PROFILE_USER_1})
        assert response.status_code == 200
        assert response.json['username'] == PRIVATE_PROFILE_USER_2
        assert response.json.get('birthday') == '1995-04-25'
        assert response.json.get('biography') == 'Lorem'


    def test_view_private_profile_with_login_with_block(self, client: FlaskClient):
        '''only logged and not blocked user has partial access to private profile'''
        # user 1 blocks user 2
        # user 2 cannot find user 1

        # perform block
        response = client.put('/api/profile/block', 
                              json={'profile_to_block': PRIVATE_PROFILE_USER_2},
                              headers={'user': PRIVATE_PROFILE_USER_1}) 
        
        assert response.status_code == 200
        assert response.json['blocker_id'] == PRIVATE_VALID_ID
        
        # try to find
        username_to_find = PRIVATE_PROFILE_USER_1
        response = client.get(f'profile/details/{username_to_find}', headers={'user': PRIVATE_PROFILE_USER_2})
        assert response.status_code == 404
    

