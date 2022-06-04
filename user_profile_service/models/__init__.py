# from flask_sqlalchemy import SQLAlchemy
from logging import NullHandler
from sqlalchemy_serializer import SerializerMixin
from .enums import Employment_type
from user_profile_service import db

class Following(db.Model, SerializerMixin):
    __tablename__ = 'following'

    follower_id = db.Column(db.Integer, db.ForeignKey('profile.id', ondelete="CASCADE"), primary_key=True)
    following_id = db.Column(db.Integer, db.ForeignKey('profile.id', ondelete="CASCADE"), primary_key=True)
    approved = db.Column(db.Boolean, default=True)


class Profile(db.Model, SerializerMixin):
    __tablename__ = 'profile'
    serialize_rules = ('-work_experience.profile','-education.profile', '-followers', '-following')

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120),nullable=True)
    first_name = db.Column(db.String(120),nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(120), nullable=True)
    birthday = db.Column(db.Date,nullable=True)
    biography = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    interests = db.Column(db.Text, nullable=True)
    private = db.Column(db.Boolean, default=False)

    work_experience = db.relationship('Experience', backref='profile', lazy=True)
    education = db.relationship('Education', backref='profile', lazy=True)
    
    followers = db.relationship('Following', backref=db.backref('following', uselist=True),
                        primaryjoin=id == Following.following_id, uselist=True)
    following = db.relationship('Following', backref=db.backref('follower', uselist=True),
                                primaryjoin=id == Following.follower_id, uselist=True)
    
    
    def __init__(self, fields:dict) -> None:
        # merge dictionaries
        self.__dict__ = {**self.__dict__, **fields}

    def __repr__(self) -> str:
        attributes = dict(self.__dict__)
        attributes.pop('_sa_instance_state')
        attributes.pop('skills')
        attributes.pop('interests')
        
        return f'Profile({attributes})'





class Experience(db.Model, SerializerMixin):
    __tablename__ = 'experience'
    serialize_rules = ('-type', 'employment_type')

    def employment_type(self):
        return self.type.name

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Enum(Employment_type), default=Employment_type.FULL_TIME)
    company = db.Column(db.String(120),nullable=True)
    location = db.Column(db.String(120), nullable=True)
    currently_working = db.Column(db.Boolean, nullable=True)
    start_date = db.Column(db.Date,nullable=True)
    end_date = db.Column(db.Date,nullable=True)

    def __init__(self, fields:dict) -> None:
        # merge dictionaries
        self.__dict__ = {**self.__dict__, **fields}

    def __repr__(self) -> str:
        attributes = dict(self.__dict__)
        attributes.pop('_sa_instance_state')
        return f'Experience({attributes})'


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

    def __init__(self, fields:dict) -> None:
        # merge dictionaries
        self.__dict__ = {**self.__dict__, **fields}

    def __repr__(self) -> str:
        attributes = dict(self.__dict__)
        attributes.pop('_sa_instance_state')
        return f'Education({attributes})'