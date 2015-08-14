from sqlalchemy import Column, Boolean, Integer, String, DateTime
from sqlalchemy.orm.exc import NoResultFound

from db import Model, Session, session_factory

class Forum(Model):
    __tablename__ = 'forums'

    id = Column(Integer, primary_key=True)
    board_key = Column(String)
    bpath = Column(String)
    password = Column(String)
    enabled = Column(Boolean, default=True)
    bare_location = Column(String)
    mod_keys = Column(String, default='')

    def save(self):
        with session_factory() as sess:
            sess.merge(self)

    def delete(self):
        with session_factory() as sess:
            sess.delete(self)

    @staticmethod
    def from_id(id):
        with session_factory() as session:
            try:
                forum = session.query(Forum).filter(
                    Forum.id==id
                ).one()

                session.expunge(forum)

                return forum
            except NoResultFound:
                return None

    @staticmethod
    def from_key(key, bpath):
        with session_factory() as session:
            try:
                forum = session.query(Forum).filter(
                    Forum.board_key==key,
                    Forum.bpath==bpath
                ).one()

                session.expunge(forum)

                return forum
            except NoResultFound:
                return None

    @staticmethod
    def key_exists(key):
        with session_factory() as session:
            try:
                session.query(Forum.board_key).filter(
                    Forum.board_key==key
                ).one()

                return False
            except NoResultFound:
                return True

    @staticmethod
    def bpath_exists(bpath):
        with session_factory() as session:
            try:
                session.query(Forum.bpath).filter(
                    Forum.bpath==bpath
                ).one()

                return True
            except NoResultFound:
                return False