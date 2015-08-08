import os

from flask import request, session, url_for

from main import app
from secure import get_form_key

def cache_bust(ep, **kwargs):
    if ep == 'static' and 'filename' in kwargs:
        file = kwargs['filename']
        path = os.path.join(app.root_path, 'static', file)
        lm = int(os.stat(path).st_mtime)

        kwargs['m'] = lm

    return url_for(ep, **kwargs)

@app.before_first_request
def setup():
    # Refresh form key.
    session.pop('form_key', None)
    session['form_key'] = get_form_key()

@app.context_processor
def injections():
    return {
        'url_for': cache_bust,
        'get_form_key': get_form_key
    }