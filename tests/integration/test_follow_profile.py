import os
import psycopg2

import pytest
from user_profile_service import create_app, db
from user_profile_service.models import Profile, Following
from flask.testing import FlaskClient



PRIVATE_PROFILE_USER_1 = 'john_private'
PRIVATE_PROFILE_USER_2 = 'lo_private'
PUBLIC_PROFILE_USER = 'john_public'
INVALID_USER = 'invalid_user'

def create_db():
    conn = psycopg2.connect(
        database="postgres", user=os.environ['DATABASE_USERNAME'], password=os.environ['DATABASE_PASSWORD'], host=os.environ['DATABASE_DOMAIN'], port=os.environ['DATABASE_PORT']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    drop_sql = f'DROP database IF EXISTS {os.environ["DATABASE_SCHEMA"]}';
    sql = f'CREATE database {os.environ["DATABASE_SCHEMA"]}';
    cursor.execute(drop_sql)
    cursor.execute(sql)
    conn.close()

def seed_db():
    profiles = [
        Profile({'username':PUBLIC_PROFILE_USER, 'email':'john@gmail.com', 'first_name':'John', 'last_name':'Smith', 'phone_number':'+938480', 'birthday':'1995-04-25','biography':'Lorem','private':False}),
        Profile({'username':PRIVATE_PROFILE_USER_1, 'email':'john@gmail.com', 'first_name':'John', 'last_name':'Smith', 'phone_number':'+938480', 'birthday':'1995-04-25','biography':'Lorem','private':True}),
        Profile({'username':PRIVATE_PROFILE_USER_2, 'email':'john@gmail.com', 'first_name':'John', 'last_name':'Smith', 'phone_number':'+938480', 'birthday':'1995-04-25','biography':'Lorem','private':True})
    ]

    db.session.bulk_save_objects(profiles)
    db.session.commit()


@pytest.fixture(scope='session')
def client() -> FlaskClient:
    '''
    Initlializes flask client app which is used to mock requests.
    Returns flask client app.
    '''
    # setup
    # create_db()
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


class TestFollowProfile:
    '''Test case for following another profile.'''

    def test_follow_public_profile(self, client: FlaskClient):
        response = client.post('/api/profile/follow', json={'user_to_follow': PUBLIC_PROFILE_USER }, headers={'user': PRIVATE_PROFILE_USER_1 })

        assert response.status_code == 200


    def test_follow_private_profile(self, client: FlaskClient):
        response = client.post('/api/profile/follow',
                               json={'user_to_follow': PRIVATE_PROFILE_USER_1 }, headers={'user': PUBLIC_PROFILE_USER })

        assert response.status_code == 200


    def test_follow_public_profile_invalid_user(self, client: FlaskClient):
        response = client.post('/api/profile/follow',
                               json={'user_to_follow': PUBLIC_PROFILE_USER}, headers={'user': INVALID_USER } )
        assert response.status_code == 404

    def test_follow_private_profile_invalid_user(self, client: FlaskClient):
        response = client.post('/api/profile/follow',
                               json={'user_to_follow': PRIVATE_PROFILE_USER_1}, headers={'user': INVALID_USER } )
        assert response.status_code == 404


class TestListFollowers:
    '''Test case for listing all followers and following profiles.'''

    def test_list_all_followers_public(self, client: FlaskClient):
        pass



    def test_list_all_followers_private(self, client: FlaskClient):
        pass

    def test_list_all_approved_followers_private(self, client: FlaskClient):
        pass

    def test_list_all_followers_invalid_user(self, client: FlaskClient):
        pass

    def test_list_all_following(self, client: FlaskClient):
        pass


class TestResolveFollowRequest:
    '''Test case for when user logs in.'''

    def test_resolve_request(self, client: FlaskClient):
        pass

    def test_resolve_request_invalid_user(self, client: FlaskClient):
        pass

    def test_resolve_request_invalid_follower(self, client: FlaskClient):
        pass


