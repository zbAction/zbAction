import json

from sqlalchemy import Column, exists, Integer, String, DateTime
from sqlalchemy.orm.exc import NoResultFound
from models import Model, Session, session_factory
import uuid

import traceback

class User(Model):
	__tablename__ = 'users'

	id = Column(Integer, primary_key = True)
	access_key = Column(String)
	board_key = Column(String)
	uid = Column(Integer)
	name = Column(String)

	def save(self):
		with session_factory() as sess:
			sess.merge(self)

	def delete(self):
		with session_factory() as sess:
			sess.delete(self)

	def get_unread(self):
		with session_factory() as session:
			pass

	def toKey(self):
		return self.board_key + '|' + str(self.uid)

	def validate_key(self, key):
		with session_factory() as session:
			try:
				session.query(User).filter(
					User.board_key==self.board_key,
					User.uid==self.uid,
					User.access_key==key
				).one()

				return True
			except NoResultFound:
				return False

	def to_json(self):
		return {
			'board_key': self.board_key,
			'uid': self.uid,
			'name': self.name
		}

	@staticmethod
	def key_exists(key):
		with session_factory() as session:
			try:
				session.query(
					User.access_key
				).filter(
					User.access_key==key
				).one()

				return True
			except:
				return False

	@staticmethod
	def create_from(model, name=True):
		# Check to see if this user is in the DB.
		# If the user isn't put them into the DB.

		with session_factory() as session:
			try:
				user = session.query(User).filter(
					User.board_key==model['board_key'],
					User.uid==model['uid']
				).one()
		
				session.expunge(user)
				return user
			except NoResultFound:
				access_key = uuid.uuid4()

				# Make sure we generate a truly random access key.

				while User.key_exists(access_key):
					access_key = uuid.uuid4()

				access_key = str(access_key)

				user = User(board_key=model['board_key'], uid=model['uid'], access_key=access_key)
				return user