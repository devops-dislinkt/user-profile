from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from .enums import Employment_type

db = SQLAlchemy()

class Profile(db.Model, SerializerMixin):
    __tablename__ = 'profile'
    serialize_rules = ('-work_experience.profile','-education.profile')

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120),nullable=True)
    first_name = db.Column(db.String(120),nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(120), nullable=True)
    date_of_birth = db.Column(db.Date,nullable=True)
    biography = db.Column(db.Text, nullable=True)

    work_experience = db.relationship('Experience', backref='profile', lazy=True)
    education = db.relationship('Education', backref='profile', lazy=True)

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

