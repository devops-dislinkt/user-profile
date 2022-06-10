# testovi se pokrecu tako sto otvoris container cli -> pytest

import pytest
import psycopg2
import os
from flask.testing import FlaskClient
from user_profile_service import create_app, db
from user_profile_service.models import Profile

# constants
PUBLIC_PROFILE = Profile(
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
PRIVATE_PROFILE = Profile(
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


def seed_db():
    profiles = [PUBLIC_PROFILE, PRIVATE_PROFILE]
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


class TestEditProfileBasicInfo:
    """Test case for editing profile basic info, work experience, education, skills, interests."""

    def get_headers_valid(self, profile: Profile) -> dict:
        """Create headers for authentication and returns headers dictionary."""
        headers = {"user": f"{profile.username}"}
        return headers

    def get_headers_invalid(self) -> dict:
        """Create invalid headers with non existing user and returns headers dictionary."""
        headers = {"user": f"trash"}
        return headers

    def test_edit_profile_basic_info_without_token(self, client: FlaskClient):
        """Request must be send with valid token. When send without token, request should fail."""

        incoming_data = {
            "email": "petar@gmail.com",
            "first_name": "Petar",
            "last_name": "Peric",
            "phone_number": "654321",
            "birthday": "2001-04-30",
        }
        response = client.put("/api/profiles/basic-info", json=incoming_data)
        assert response.status_code == 404

    def test_edit_profile_basic_info_invalid_token(self, client: FlaskClient):
        """Request must be send with valid token. When send invalid token, request should fail."""

        incoming_data = {
            "email": "petar@gmail.com",
            "first_name": "Petar",
            "last_name": "Peric",
            "phone_number": "654321",
            "birthday": "2001-04-30",
        }
        response = client.put(
            "/api/profiles/basic-info",
            json=incoming_data,
            headers=self.get_headers_invalid(),
        )
        assert response.status_code == 404

    def test_edit_profile_basic_info_success(self, client: FlaskClient):

        incoming_data = {
            "email": "petar@gmail.com",
            "first_name": "Petar",
            "last_name": "Peric",
            "phone_number": "654321",
            "birthday": "2001-04-30",
        }
        response = client.put(
            "/api/profiles/basic-info",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )

        assert response.status_code == 200

        ret_profile = Profile(response.json)
        assert ret_profile.email == incoming_data["email"]
        assert ret_profile.first_name == incoming_data["first_name"]
        assert ret_profile.last_name == incoming_data["last_name"]
        assert ret_profile.phone_number == incoming_data["phone_number"]
        assert ret_profile.birthday == incoming_data["birthday"]

    def test_edit_profile_work_experience_success(self, client: FlaskClient):
        incoming_data = {
            "title": "Strucna prak",
            "type": "INTERNSHIP",
            "company": "devops & co",
            "location": "Izmisljenog junaka 8",
            "currently_working": False,
            "start_date": "2015-05-15",
            "end_date": "2018-05-15",
        }
        response = client.put(
            "/api/profiles/work-experience",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 200

    def test_edit_profile_work_experience_fail(self, client: FlaskClient):
        """Sending bad keys in incoming data should raise KeyError and return 400. Request should fail."""

        incoming_data = {"trash": "trash"}
        response = client.put(
            "/api/profiles/work-experience",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 400

    def test_edit_profile_education_success(self, client: FlaskClient):
        incoming_data = {
            "education": "Master's Degree",
            "school": "FTN",
            "degree": "Master",
            "field_of_study": "Software Engineering",
            "start_date": "2014-05-15",
        }
        response = client.put(
            "/api/profiles/education",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 200

    def test_edit_profile_education_with_nonexisting_keys(self, client: FlaskClient):
        """Sending non existing keys shouldn't make a difference. Request should fail."""

        incoming_data = {
            "trash_field": 1,
            "trash_field2": 2,
            "education": "Master's Degree",
            "school": "FTN",
            "degree": "Master",
            "field_of_study": "Software Engineering",
            "start_date": "2014-05-15",
        }
        response = client.put(
            "/api/profiles/education",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 200

    def test_edit_profile_skills_success(self, client: FlaskClient):
        incoming_data = {"skills": "angular, tensorflow, python"}
        response = client.put(
            "/api/profiles/skills",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 200

    def test_edit_profile_skills_fail(self, client: FlaskClient):
        """Sending bad keys in incoming data should raise KeyError and return 400. Request should fail."""

        incoming_data = {"vestine_wrong_field": "angular, tensorflow, python"}
        response = client.put(
            "/api/profiles/skills",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 400

    def test_edit_profile_interests(self, client: FlaskClient):
        incoming_data = {"interests": "swimming, hiking,..."}
        response = client.put(
            "/api/profiles/interests",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 200

    def test_edit_profile_interests_fail(self, client: FlaskClient):
        """Sending bad keys in incoming data should raise KeyError and return 400. Request should fail."""
        incoming_data = {"trash": "trash"}
        response = client.put(
            "/api/profiles/interests",
            json=incoming_data,
            headers=self.get_headers_valid(PUBLIC_PROFILE),
        )
        assert response.status_code == 400
