import json

from sqlalchemy import Column, exists, Integer, String, DateTime
from sqlalchemy.orm.exc import NoResultFound
from models import Model, Session, session_factory
import uuid

import traceback

class Forum(Model):
	__tablename__ = 'forums'

	id = Column(Integer, primary_key = True)
	board_key = Column(String)
	bare_location = Column(String)
	mod_keys = Column(String)

	def save(self):
		with session_factory() as sess:
			sess.merge(self)

	def delete(self):
		with session_factory() as sess:
			sess.delete(self)

	@staticmethod
	def key_exists(key):
		return key == 0 or Session.query(exists().where(Mod.api_key==key))