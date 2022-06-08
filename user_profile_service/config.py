import os

user = os.environ['DATABASE_USERNAME']
password = os.environ['DATABASE_PASSWORD']
host = os.environ['DATABASE_DOMAIN']
database = os.environ['DATABASE_SCHEMA']
port = os.environ['DATABASE_PORT']
secret_key = os.environ['FLASK_SECRET_KEY']

DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

KAFKA_1 = os.environ['KAFKA1']
KAFKA_TOPIC=os.environ['KAFKA_TOPIC']