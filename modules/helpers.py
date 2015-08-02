from datetime import datetime, timedelta

from db import session_factory
from models.action import Action

def serialize(var):
    if isinstance(var, User):
        return var.to_json()

    if isinstance(var, Action):
        return var.to_json()

    if isinstance(var, object):
        return var.__dict__
    else:
        return var

def within_one_week(timestamp):
    now = datetime.utcnow()
    week = timedelta(weeks=1)

    return timestamp + week >= now

def get_unread(user):
    with session_factory() as session:
        actions = session.query(
            Action
        ).filter(
            Action.receiver==user.access_key,
            Action.seen==False
        ).all()

        session.expunge_all()

        return actions