import pytest

# from flask.testing import FlaskClient
from flask import Flask
from user_profile_service import create_app, db
from user_profile_service.models import Profile
from user_profile_service import database
from user_profile_service.services import profile_service


def seed_db():
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
    kiki = Profile(
        {
            "username": "kiki_test",
            "email": "kiki@gmail.com",
            "first_name": "Kiki",
            "last_name": "Mikic",
            "phone_number": "123456",
            "birthday": "1920-04-30",
            "biography": "Kikina biografija",
            "private": True,
        }
    )

    profiles = [pera, mika, zika, kiki]
    db.session.bulk_save_objects(profiles)
    db.session.commit()


@pytest.fixture(scope="function")
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
@pytest.fixture(scope="function")
def pera() -> Profile:
    return database.find_by_username("pera_test")


@pytest.fixture(scope="function")
def mika() -> Profile:
    return database.find_by_username("mika_test")


@pytest.fixture(scope="function")
def zika() -> Profile:
    return database.find_by_username("zika_test")


@pytest.fixture(scope="function")
def kiki() -> Profile:
    return database.find_by_username("kiki_test")


class TestBlockProfile:
    """Test case for unit tests, blocking profiles should restrict interaction between profiles."""

    def test_block_one_profile_success(self, app: Flask, mika: Profile, kiki: Profile):
        """
        mika ->X kiki
        """
        block = profile_service.block_profile(
            username_to_block=kiki.username, profile=mika
        )

        assert block.blocker_id == mika.id
        assert block.blocked_id == kiki.id
        assert mika.is_profile_blocked_by_me(kiki.id)

    def test_block_multiple_profiles_success(
        self, app: Flask, pera: Profile, mika: Profile, zika: Profile, kiki: Profile
    ):
        """
        Pera blocks [zika, kiki]. Mika blocks [kiki, pera]. Zika tries to block pera (fails), zika tries to blocks mika (success).
        pera ->X zika
             ->X kiki
        zika ->X kiki
             ->X mika
        """
        pera_blocks_zika = profile_service.block_profile(
            username_to_block=zika.username, profile=pera
        )
        pera_blocks_kiki = profile_service.block_profile(
            username_to_block=kiki.username, profile=pera
        )
        zika_blocks_kiki = profile_service.block_profile(
            username_to_block=kiki.username, profile=zika
        )
        zika_blocks_mika = profile_service.block_profile(
            username_to_block=mika.username, profile=zika
        )

        assert pera_blocks_zika.blocker_id == pera.id
        assert pera_blocks_zika.blocked_id == zika.id
        assert pera.is_profile_blocked_by_me(zika.id)

        assert pera_blocks_kiki.blocker_id == pera.id
        assert pera_blocks_kiki.blocked_id == kiki.id
        assert pera.is_profile_blocked_by_me(kiki.id)

        assert zika_blocks_kiki.blocker_id == zika.id
        assert zika_blocks_kiki.blocked_id == kiki.id
        assert zika.is_profile_blocked_by_me(kiki.id)

        assert zika_blocks_mika.blocker_id == zika.id
        assert zika_blocks_mika.blocked_id == mika.id
        assert zika.is_profile_blocked_by_me(mika.id)

        assert len(pera.profiles_blocked_by_me) == 2
        assert len(zika.profiles_blocked_by_me) == 2
