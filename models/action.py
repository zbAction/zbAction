from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, DateTime, Boolean
import traceback

from db import Model, session_factory
from models.user import User

class Action(Model):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow())
    event = Column(String)
    details = Column(String)
    source = Column(Integer)
    receiver = Column(Integer)
    seen = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        self.seen = False
        self.timestamp = datetime.utcnow()

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def save(self):
        with session_factory() as sess:
            sess.merge(self)

    def delete(self):
        with session_factory() as sess:
            sess.delete(self)

    def to_json(self):
        return json.dumps({
            'timestamp': str(self.timestamp),
            'event': self.event,
            'details': self.details,
            'source': User.from_id(self.source).to_json(),
            'receiver': User.from_id(self.receiver).to_json(),
            'seen': self.seen
        })

    @staticmethod
    def create_from(model):
        if isinstance(model, Action):
            return model

        source = User.create_from(model['source'])
        receiver = User.create_from(model['receiver'])

        return Action(
            event=model['event'],
            details=model['details'],
            source=source.id,
            receiver=receiver.id,
        )