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
    name = Column(String)

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
                mod = session.query(
                    Mod
                ).filter(
                    Mod.api_key==key
                ).one()

                session.expunge(mod)

                return mod
            except:
                return None

    @staticmethod
    def key_exists(key):
        if key == 0: return True

        return Mod.from_key(key) is not None
