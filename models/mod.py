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
    enabled = Column(Boolean)
    root_enabled = Column(Boolean)

    def save(self):
        with session_factory() as sess:
            sess.merge(self)

    def delete(self):
        with session_factory() as sess:
            sess.delete(self)

    @staticmethod
    def key_exists(key):
        if key == 0: return True

        with session_factory() as session:
            try:
                session.query(
                    Mod.api_key
                ).filter(
                    Mod.api_key==key
                ).one()

                return True
            except NoResultFound:
                return False