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
    source = Column(String)
    receiver = Column(String)
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
            'source': User.from_access_key(self.source).to_json(),
            'receiver': User.from_acccess_key(self.receiver).to_json(),
            'seen': self.seen
        })

    @staticmethod
    def create_from(model):
        if isinstance(model, Action):
            return model

        source = User.create_from(model['source'])
        receiver = User.create_from(model['receiver'])

        try:
            model['timestamp'] = datetime.fromtimestamp(model['timestamp'] / 1000.0)
        except:
            model['timestamp'] = datetime.utcnow()

        return Action(
            timestamp=model['timestamp'],
            event=model['event'][0:255],
            details=model['details'][0:10000],
            source=source.access_key,
            receiver=receiver.access_key,
        )
