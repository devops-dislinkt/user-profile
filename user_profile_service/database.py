from typing import Optional
from .models import Profile, db
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError


def get_all(model):
    data = model.query.all()
    return data


def add_or_update(instance: db.Model):
    db.session.merge(instance)
    commit_changes()

def delete_instance(model, id):
    model.query.filter_by(id=id).delete()
    commit_changes()


def edit_instance(model, id, fields:dict):
    instance = model.query.filter_by(id=id).all()[0]
    for attr, new_value in fields.items():
        setattr(instance, attr, new_value)
    commit_changes()

def find_by_username(model, username:str) -> Optional[Profile]:
    '''Finds profile by username. If Profile object is not found, None is returned.'''
    return model.query.filter_by(username=username).first()

def find_by_id(model, id):
    return model.query.get(id)


def commit_changes():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)