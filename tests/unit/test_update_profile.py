import pytest
import psycopg2
import os

# from flask.testing import FlaskClient
from flask import Flask
from user_profile_service import create_app, db
from user_profile_service.models import Profile
from user_profile_service import database
from user_profile_service.services import profile_service


def seed_db():
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

    profiles = [PUBLIC_PROFILE, PRIVATE_PROFILE]
    db.session.bulk_save_objects(profiles)
    db.session.commit()


@pytest.fixture(scope="module")
def app() -> Flask:
    """
    Initlializes flask client app which is used for unit testing with app context.
    Returns flask app.
    """

    # setup
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_db()
        yield app

    # teardown
    with app.app_context():
        db.drop_all()


# PARAMS
@pytest.fixture(scope="module")
def public_profile() -> Profile:
    return database.find_by_username("pera_test")


@pytest.fixture(scope="module")
def private_profile() -> Profile:
    return database.find_by_username("mika_test")


@pytest.fixture(scope="function")
def basic_info_data():
    return {
        "email": "petar@gmail.com",
        "first_name": "Petar",
        "last_name": "Peric",
        "phone_number": "654321",
        "birthday": "2001-04-30",
    }


@pytest.fixture(scope="function")
def work_experience_data():
    return {
        "title": "Strucna prak",
        "type": "INTERNSHIP",
        "company": "devops & co",
        "location": "Izmisljenog junaka 8",
        "currently_working": False,
        "start_date": "2015-05-15",
        "end_date": "2018-05-15",
    }


@pytest.fixture(scope="function")
def education_data():
    return {
        "education": "Master's Degree",
        "school": "FTN",
        "degree": "Master",
        "field_of_study": "Software Engineering",
        "start_date": "2014-05-15",
    }


@pytest.fixture(scope="function")
def skills_data():
    return {"skills": "angular, tensorflow, python"}


@pytest.fixture(scope="function")
def interests_data():
    return {"interests": "swimming, hiking,..."}


@pytest.fixture(scope="function")
def trash_data():
    return {"trash": "trash"}


class TestEditProfile:
    """Test case for unit tests, editing basic info, experience, education, skills, interests."""

    def test_edit_basic_info_success(
        self, app: Flask, public_profile: Profile, basic_info_data: dict
    ):
        # with app.app_context(): # no need to use context, context is already set
        updated = profile_service.edit_basic_info(
            data=basic_info_data, profile=public_profile
        )
        assert basic_info_data["email"] == updated.email
        assert basic_info_data["first_name"] == updated.first_name
        assert basic_info_data["last_name"] == updated.last_name
        assert basic_info_data["phone_number"] == updated.phone_number
        assert basic_info_data["birthday"] == updated.birthday.strftime("%Y-%m-%d")

    def test_edit_work_experience_success(
        self, app: Flask, public_profile: Profile, work_experience_data: dict
    ):
        updated_exp = profile_service.create_or_update_work_experience(
            data=work_experience_data, profile=public_profile
        )

        assert public_profile.id == updated_exp.profile_id
        assert work_experience_data["title"] == updated_exp.title
        assert (
            work_experience_data["type"] == updated_exp.type.name
        )  # name is to get enum str representation
        assert work_experience_data["title"] == updated_exp.title
        assert work_experience_data["company"] == updated_exp.company
        assert work_experience_data["location"] == updated_exp.location
        assert (
            work_experience_data["currently_working"] == updated_exp.currently_working
        )
        assert work_experience_data["start_date"] == updated_exp.start_date.strftime(
            "%Y-%m-%d"
        )
        assert work_experience_data["end_date"] == updated_exp.end_date.strftime(
            "%Y-%m-%d"
        )

    def test_edit_education_success(
        self, app: Flask, public_profile: Profile, education_data: dict
    ):
        updated_edu = profile_service.create_or_update_education(
            data=education_data, profile=public_profile
        )

        print(updated_edu.start_date, type(updated_edu.start_date))

        assert public_profile.id == updated_edu.profile_id
        assert education_data["school"] == updated_edu.school
        assert education_data["degree"] == updated_edu.degree
        assert education_data["field_of_study"] == updated_edu.field_of_study
        assert education_data["start_date"] == updated_edu.start_date.strftime(
            "%Y-%m-%d"
        )


class TestEditProfileKeys:
    """
    Test case for unit tests when sending bad keys as json data and when sending extra keys (beside regular keys).
    Sending bad keys shouldn't raise keyerror exception.
    Sending non existing keys shouldn't make a difference. Request should fail
    """

    def test_edit_basic_info_bad_keys(
        self, app: Flask, public_profile: Profile, trash_data: dict
    ):
        response = profile_service.edit_basic_info(
            data=trash_data, profile=public_profile
        )
        assert response.id == public_profile.id

    def test_edit_basic_info_extra_keys(
        self,
        app: Flask,
        public_profile: Profile,
        basic_info_data: dict,
        trash_data: dict,
    ):
        basic_info_data_with_trash_data = {**basic_info_data, **trash_data}
        updated = profile_service.edit_basic_info(
            data=basic_info_data_with_trash_data, profile=public_profile
        )

        assert basic_info_data_with_trash_data["email"] == updated.email
        assert basic_info_data_with_trash_data["first_name"] == updated.first_name
        assert basic_info_data_with_trash_data["last_name"] == updated.last_name
        assert basic_info_data_with_trash_data["phone_number"] == updated.phone_number
        assert basic_info_data_with_trash_data["birthday"] == updated.birthday.strftime(
            "%Y-%m-%d"
        )

    def test_edit_work_experience_bad_keys(
        self, app: Flask, public_profile: Profile, trash_data: dict
    ):

        response = profile_service.create_or_update_work_experience(
            data=trash_data, profile=public_profile
        )
        assert response.profile_id == public_profile.id

    def test_edit_work_experience_extra_keys(
        self,
        app: Flask,
        public_profile: Profile,
        work_experience_data: dict,
        trash_data: dict,
    ):
        work_experience_data_with_trash_data = {**work_experience_data, **trash_data}
        updated_exp = profile_service.create_or_update_work_experience(
            data=work_experience_data_with_trash_data, profile=public_profile
        )

        assert work_experience_data["title"] == updated_exp.title
        assert (
            work_experience_data["type"] == updated_exp.type.name
        )  # name is to get enum str representation
        assert work_experience_data["title"] == updated_exp.title
        assert work_experience_data["company"] == updated_exp.company
        assert work_experience_data["location"] == updated_exp.location
        assert (
            work_experience_data["currently_working"] == updated_exp.currently_working
        )
        assert work_experience_data["start_date"] == updated_exp.start_date.strftime(
            "%Y-%m-%d"
        )
        assert work_experience_data["end_date"] == updated_exp.end_date.strftime(
            "%Y-%m-%d"
        )

    def test_edit_education_extra_keys(
        self,
        app: Flask,
        public_profile: Profile,
        education_data: dict,
        trash_data: dict,
    ):
        education_data_with_trash_data = {**education_data, **trash_data}
        updated_edu = profile_service.create_or_update_education(
            data=education_data_with_trash_data, profile=public_profile
        )

        assert public_profile.id == updated_edu.profile_id
        assert education_data["school"] == updated_edu.school
        assert education_data["degree"] == updated_edu.degree
        assert education_data["field_of_study"] == updated_edu.field_of_study
        assert education_data["start_date"] == updated_edu.start_date.strftime(
            "%Y-%m-%d"
        )
