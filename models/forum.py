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
    real_location = Column(String)
    bare_location = Column(String)
    mod_keys = Column(String, default='')
    is_auth = None

    def save(self):
        with session_factory() as sess:
            sess.merge(self)

    def delete(self):
        with session_factory() as sess:
            sess.delete(self)

    def is_authenticated(self):
        if self.is_auth is not None:
            return self.is_auth

        with session_factory() as sess:
            try:
                sess.query(Forum).filter(
                    Forum.board_key==self.board_key,
                    Forum.password==self.password
                ).one()

                self.is_auth = True
                return True
            except:
                self.is_auth = False
                return False

    def is_anonymous(self):
        return False

    def is_active(self):
        return self.enabled

    def get_id(self):
        return unicode(self.id)

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
    def from_key(key):
        with session_factory() as session:
            try:
                forum = session.query(Forum).filter(
                    Forum.board_key==key
                ).one()

                session.expunge(forum)

                return forum
            except NoResultFound:
                return None

    @staticmethod
    def from_key_and_bpath(key, bpath):
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
        return Forum.from_key(key) is not None

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
