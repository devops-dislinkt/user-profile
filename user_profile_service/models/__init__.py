# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from .enums import Employment_type
from user_profile_service import db

class Profile(db.Model, SerializerMixin):
    __tablename__ = 'profile'
    serialize_rules = ('-work_experience.profile','-education.profile')

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120),nullable=True)
    first_name = db.Column(db.String(120),nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(120), nullable=True)
    birthday = db.Column(db.Date,nullable=True)
    biography = db.Column(db.Text, nullable=True)

    work_experience = db.relationship('Experience', backref='profile', lazy=True)
    education = db.relationship('Education', backref='profile', lazy=True)

    def __repr__(self) -> str:
        attributes = dict(self.__dict__)
        attributes.pop('_sa_instance_state')
        return f'Profile({attributes})'

class Experience(db.Model, SerializerMixin):
    __tablename__ = 'experience'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Enum(Employment_type), default=Employment_type.FULL_TIME)
    company = db.Column(db.String(120),nullable=True)
    location = db.Column(db.String(120), nullable=True)
    currently_working = db.Column(db.Boolean, nullable=True)
    start_date = db.Column(db.Date,nullable=True)
    end_date = db.Column(db.Date,nullable=True)

    def __repr__(self) -> str:
        attributes = dict(self.__dict__)
        attributes.pop('_sa_instance_state')
        return f'Experience({attributes})'

    def get_attributes_as_dict(self):
        attributes = dict(self.__dict__)
        attributes.pop('_sa_instance_state')
        return attributes

class Education(db.Model, SerializerMixin):
    __tablename__ = 'education'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    school = db.Column(db.String(80), nullable=False)
    degree = db.Column(db.String(80), nullable=True)
    field_of_study = db.Column(db.String(120),nullable=True)
    start_date = db.Column(db.Date,nullable=True)
    end_date = db.Column(db.Date,nullable=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        attributes = dict(self.__dict__)
        attributes.pop('_sa_instance_state')
        return f'Education({attributes})'