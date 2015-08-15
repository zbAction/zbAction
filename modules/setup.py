import os

from flask import request, session, url_for
from jinja2 import PackageLoader

from main import app, loader, login_manager

from helpers import check_server
from models.user import User
from secure import get_form_key

login_manager.refresh_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.from_id(int(userid))

def cache_bust(ep, **kwargs):
    if ep == 'static' and 'filename' in kwargs:
        file = kwargs['filename']
        path = os.path.join(app.root_path, 'static', file)
        lm = int(os.stat(path).st_mtime)

        kwargs['m'] = lm

    return url_for(ep, **kwargs)

'''
@app.before_first_request
def setup():
    session.pop('form_key', None)
    session['form_key'] = get_form_key()
'''

@app.before_request
def setup2():
    get_form_key()

def include_source(f):
    return loader.get_source(app.jinja_env, f)[0]

@app.context_processor
def injections():
    server_online = check_server()

    return {
        'url_for': cache_bust,
        'get_form_key': get_form_key,
        'include_source': include_source,
        'server_online': server_online
    }
