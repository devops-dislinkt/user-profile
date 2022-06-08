import pytest
import psycopg2
import os
from flask.testing import FlaskClient
from user_profile_service import create_app, db
from user_profile_service.models import Profile
import jwt
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound

# constants
pera = Profile({ 'username':"pera_test", 'email':'pera@gmail.com', 'first_name':'Pera', 'last_name':'Peric', 'phone_number':'+938480', 'birthday':'2000-04-30','biography':'Lorem ipsum bio graf i ja.','private':False})
pera.id = 1
mika = Profile({ 'username':"mika_test", 'email':'mika@gmail.com', 'first_name':'Mika', 'last_name':'Mikic', 'phone_number':'123456', 'birthday':'1920-04-30','biography':'Mikina biografija','private':True})
mika.id = 2
zika = Profile({ 'username':"zika_test", 'email':'zika@gmail.com', 'first_name':'Zika', 'last_name':'Mikic', 'phone_number':'123456', 'birthday':'1920-04-30','biography':'Zikina biografija','private':True})
zika.id = 3


def create_db():
    '''setup database before tests start executing'''
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
    profiles = [pera, mika, zika]
    db.session.bulk_save_objects(profiles)
    db.session.commit()

@pytest.fixture(scope='module')
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
    

@pytest.fixture(scope='function')
def incoming_data_valid():
    return {'profile_to_block': pera.username}

@pytest.fixture(scope='function')
def incoming_data_invalid():
    return {'profile_to_block': 'not_found'}

@pytest.fixture(scope='function')
def trash_data():
    return {"trash": "trash"}


class TestBlockProfile:
    '''Test case for blocking profile.'''

    def get_headers_valid(self, profile: Profile) -> dict:
        '''Create headers for authentication and returns headers dictionary.'''
        headers = {'user': f'{profile.username}'}
        return headers

    
    def get_headers_invalid(self) -> dict:
        '''Create invalid headers with non existing user and returns headers dictionary.'''
        headers = {'user': f'trash'}
        return headers

    
    def test_block_profile_success(self, client: FlaskClient, incoming_data_valid: dict):
        response = client.put('/api/profiles/block', json = incoming_data_valid, headers=self.get_headers_valid(mika))
        print(response.data)
        assert response.status_code == 200
        assert response.json['blocker_id'] == mika.id
        

    def test_block_profile_fail(self, client: FlaskClient, incoming_data_invalid: dict):
        response = client.put('/api/profiles/block', json = incoming_data_invalid, headers=self.get_headers_valid(mika))
        assert response.status_code == 404
        assert response.data.decode() == 'user not found'
        
    def test_block_profile_trash_data(self, client: FlaskClient, trash_data: dict):
        response = client.put('/api/profiles/block', json = trash_data, headers=self.get_headers_valid(mika))
        assert response.status_code == 400

    def test_block_profile_without_token(self, client: FlaskClient, incoming_data_valid: dict):
        '''Request must be send with valid token. When send without token, request should fail.'''
        response = client.put('/api/profiles/basic-info', json= incoming_data_valid)
        print(response)
        assert response.status_code == 404


    def test_block_profile_invalid_token(self, client: FlaskClient,  incoming_data_valid: dict):
        '''Request must be send with valid token. When send invalid token, request should fail.'''
        response = client.put('/api/profiles/basic-info', json= incoming_data_valid, headers=self.get_headers_invalid())
        assert response.status_code == 404