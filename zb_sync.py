import json
import time

from flask import Flask

from tornado import web, ioloop
from tornado.wsgi import WSGIContainer

from secrets import secrets

from dispatcher import Dispatcher
from handler import SocketHandler
from store import Store

app = Flask(__name__)

from routes import *

store = Store()
dispatcher = Dispatcher()

store.daemon = True
dispatcher.daemon = True

if __name__ == '__main__':
	wsgi = WSGIContainer(app)

	tornado = web.Application([
		(r'/sync', SocketHandler),
		(r'.*', web.FallbackHandler, dict(fallback=wsgi))
	], debug=secrets.DEBUG, autoreload=secrets.DEBUG)

	tornado.listen(4242)

	store.start()
	dispatcher.start()

	ioloop.IOLoop.instance().start()