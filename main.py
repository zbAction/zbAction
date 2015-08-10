import os, sys

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

import redis

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
from flask.ext.kvsession import KVSessionExtension
from jinja2 import PackageLoader
from simplekv.memory.redisstore import RedisStore

app = Flask(__name__)

store = RedisStore(redis.StrictRedis())
KVSessionExtension(store, app)
login_manager = LoginManager()
bcrypt = Bcrypt(app)

loader = PackageLoader(__name__, 'example')

import setup
from routes import *

from secrets import secrets

if __name__ == '__main__':
    app.secret_key = secrets.secret_key
    app.run(host ='0.0.0.0', port=secrets.web_port, threaded=secrets.DEBUG, debug=secrets.DEBUG)