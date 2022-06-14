import pytest
import psycopg2
import os
from flask.testing import FlaskClient
from user_profile_service import create_app, db
from user_profile_service.models import Profile

# constants
pera = Profile(
    {
        "username": "pera_test",
        "email": "pera@gmail.com",
        "first_name": "Pera",
        "last_name": "Peric",
        "phone_number": "+938480",
        "birthday": "2000-04-30",
        "biography": "Lorem ipsum bio graf i ja.",
        "private": False,
    }
)
pera.id = 1
mika = Profile(
    {
        "username": "mika_test",
        "email": "mika@gmail.com",
        "first_name": "Mika",
        "last_name": "Mikic",
        "phone_number": "123456",
        "birthday": "1920-04-30",
        "biography": "Mikina biografija",
        "private": True,
    }
)
mika.id = 2
zika = Profile(
    {
        "username": "zika_test",
        "email": "zika@gmail.com",
        "first_name": "Zika",
        "last_name": "Mikic",
        "phone_number": "123456",
        "birthday": "1920-04-30",
        "biography": "Zikina biografija",
        "private": True,
    }
)
zika.id = 3


def seed_db():
    profiles = [pera, mika, zika]
    db.session.bulk_save_objects(profiles)
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


@pytest.fixture(scope="function")
def incoming_data_valid():
    return {"profile_to_block": pera.username}


@pytest.fixture(scope="function")
def incoming_data_invalid():
    return {"profile_to_block": "not_found"}


@pytest.fixture(scope="function")
def trash_data():
    return {"trash": "trash"}


class TestBlockProfile:
    """Test case for blocking profile."""

    def get_headers_valid(self, profile: Profile) -> dict:
        """Create headers for authentication and returns headers dictionary."""
        headers = {"user": f"{profile.username}"}
        return headers

    def get_headers_invalid(self) -> dict:
        """Create invalid headers with non existing user and returns headers dictionary."""
        headers = {"user": f"trash"}
        return headers

    def test_block_profile_success(
        self, client: FlaskClient, incoming_data_valid: dict
    ):
        response = client.put(
            "/api/profile/block",
            json=incoming_data_valid,
            headers=self.get_headers_valid(mika),
        )
        print(response.data)
        assert response.status_code == 200
        assert response.json["blocker_id"] == mika.id

    def test_block_profile_fail(self, client: FlaskClient, incoming_data_invalid: dict):
        response = client.put(
            "/api/profile/block",
            json=incoming_data_invalid,
            headers=self.get_headers_valid(mika),
        )
        assert response.status_code == 404
        assert response.data.decode() == "user not found"

    def test_block_profile_trash_data(self, client: FlaskClient, trash_data: dict):
        response = client.put(
            "/api/profile/block", json=trash_data, headers=self.get_headers_valid(mika)
        )
        assert response.status_code == 400

    def test_block_profile_without_token(
        self, client: FlaskClient, incoming_data_valid: dict
    ):
        """Request must be send with valid token. When send without token, request should fail."""
        response = client.put("/api/profile/basic-info", json=incoming_data_valid)
        print(response)
        assert response.status_code == 404

    def test_block_profile_invalid_token(
        self, client: FlaskClient, incoming_data_valid: dict
    ):
        """Request must be send with valid token. When send invalid token, request should fail."""
        response = client.put(
            "/api/profile/basic-info",
            json=incoming_data_valid,
            headers=self.get_headers_invalid(),
        )
        assert response.status_code == 404


    def test_is_profile_blocked_by_me(self, client: FlaskClient, incoming_data_valid:dict):
        '''Should return true if I exist, if user exists and I blocked requested user'''
        # mika blocks pera in previous test

        # mika sees that he blocked pera
        response = client.get(f'/api/profile/is-blocked-by-me/{pera.username}', headers=self.get_headers_valid(mika))
        assert response.status_code == 200
        assert response.json == True

    
    def test_is_profile_blocked_by_me_fail(self, client: FlaskClient):
        '''Should return true if I exist, if user exists and I blocked requested user'''
        # mika blocks pera in previous test

        # mika sees that he blocked pera
        response = client.get(f'/api/profile/is-blocked-by-me/TRASH', headers=self.get_headers_valid(mika))
        assert response.status_code == 404

    def test_is_profile_blocked_by_me_without_login(self, client: FlaskClient):
        '''Should return true if I exist, if user exists and I blocked requested user'''
        # mika blocks pera in previous test

        # mika sees that he blocked pera
        response = client.get(f'/api/profile/is-blocked-by-me/{pera.username}', headers={})
        assert response.status_code == 404