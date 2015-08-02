import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

from tornado import web, ioloop

from secrets import secrets

from dispatcher import Dispatcher
from handler import SocketHandler
from store import Store

store = Store()
dispatcher = Dispatcher()

store.daemon = True
dispatcher.daemon = True

if __name__ == '__main__':
    tornado = web.Application([
        (r'/sync', SocketHandler)
    ], autoreload=secrets.DEBUG)

    tornado.listen(secrets.ws_port)

    store.start()
    dispatcher.start()

    ioloop.IOLoop.instance().start()