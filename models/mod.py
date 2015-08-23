import json
from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy.orm.exc import NoResultFound
import uuid

from db import Model, session_factory
import traceback

class Mod(Model):
    __tablename__ = 'mods'

    id = Column(Integer, primary_key=True)
    api_key = Column(String)
    enabled = Column(Boolean, default=True)
    root_enabled = Column(Boolean, default=True)

    def save(self):
        with session_factory() as sess:
            sess.merge(self)

    def delete(self):
        with session_factory() as sess:
            sess.delete(self)

    @staticmethod
    def from_key(key):
        with session_factory() as session:
            try:
                return session.query(
                    Mod.api_key
                ).filter(
                    Mod.api_key==key
                ).one()
            except:
                return None

    @staticmethod
    def key_exists(key):
        if key == 0: return True

        return Mod.from_key(key) is not None
