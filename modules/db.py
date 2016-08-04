from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from secrets import secrets

eng = 'mysql://{username}:{password}@{host}:3307/{name}?charset=utf8'.format(**secrets.db.__dict__)
engine = create_engine(
	eng, pool_recycle=600
)

factory = sessionmaker(bind=engine)
Session = scoped_session(factory)
Model = declarative_base()

@contextmanager
def session_factory():
	s = Session()

	try:
		yield s
		s.commit()
	except:
		s.rollback()
		raise
	finally:
		s.close()

f_eng = 'mysql://{username}:{password}@{host}:3307/{name}?charset=utf8'.format(**secrets.flarum_db.__dict__)
f_engine = create_engine(
	f_eng, pool_recycle=600
)

f_factory = sessionmaker(bind=f_engine)
f_Session = scoped_session(f_factory)

@contextmanager
def flarum_session_factory():
	s = f_Session()

	try:
		yield s
		s.commit()
	except:
		s.rollback()
		raise
	finally:
		s.close()