from datetime import datetime, timedelta
from functools import wraps
import hashlib
import time

from flask import abort, request, session

def get_ip():
    if 'X-Forwarded-For' in request.headers:
        return '|'.join(request.headers.getlist('X-Forwarded-For'))

    return request.remote_addr

def get_form_key():
    now = datetime.utcnow()

    if 'form_key' in session and 'expires_at' in session and session['expires_at'] > now:
        return session['form_key']

    string = request.url + str(time.time()) + get_ip()
    hashed = hashlib.sha512(string).hexdigest()

    # retire form keys after 30 minutes
    session['expires_at'] = now + timedelta(minutes=30)
    session['form_key'] = hashed

    return hashed

def form_key_required(ep):
    @wraps(ep)
    def func(**kwargs):
        if 'form_key' not in session:
            abort(404)

        if '__form_key' not in request.form:
            if '__form_key' not in request.args:
                abort(404)
            else:
                form_key = request.args['__form_key']
        else:
            form_key = request.args['__form_key']

        if form_key != session['form_key']:
            abort(404)

        return ep(**kwargs)

    return func
