import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

from flask import Flask

app = Flask(__name__)

from routes import *

from secrets import secrets

if __name__ == '__main__':
    app.secret_key = secrets.secret_key
    app.run(host ='0.0.0.0', port=secrets.web_port, threaded=secrets.DEBUG, debug=secrets.DEBUG)