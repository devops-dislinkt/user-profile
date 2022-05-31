from .models import Profile, db
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError


def get_all(model):
    data = model.query.all()
    return data


def add_instance(model, **kwargs):
    instance = model(**kwargs)
    db.session.add(instance)
    commit_changes()


def delete_instance(model, id):
    model.query.filter_by(id=id).delete()
    commit_changes()


def edit_instance(model, id, fields:dict):
    instance = model.query.filter_by(id=id).all()[0]
    for attr, new_value in fields.items():
        setattr(instance, attr, new_value)
    commit_changes()

def find_by_username(model, username:str) -> Profile:
    '''Finds profile by username. If Profile object is not found, None is returned.'''
    return model.query.filter_by(username=username).first()


def commit_changes():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)