import traceback
import uuid

from flask import abort, Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from flask.ext.login import login_required, login_user, logout_user

from main import bcrypt

from db import engine
from errors import *
from helpers import gen_key_script
from logger import log
from models.forum import Forum
from models.user import User
from secure import form_key_required, get_form_key, not_logged_in

meta = Blueprint('meta', __name__)

@meta.route('/register', methods=['GET'])
@not_logged_in
def register():
    session['board_key'] = str(uuid.uuid4())

    return render_template(
        'register.html',
        board_key=session['board_key'],
        gen_key_script=gen_key_script()
    )

@meta.route('/finalize', methods=['POST'])
@not_logged_in
@form_key_required
def finalize():
    if 'password' not in request.form or len(request.form['password'].strip()) == 0:
        return jsonify({
            'status': NO_DATA
        })

    password = bcrypt.generate_password_hash(request.form['password'])

    forum = session['forum']
    forum = Forum(password=password, **forum)
    user_data = session['user_data']

    del session['forum']
    del session['user_data']
    del session['board_key']

    try:
        forum.save()

        users = [
            {
                'access_key': str(uuid.uuid4()),
                'board_key': forum.board_key,
                'uid': user[0],
                'name': user[1]
            }

            for user in user_data
        ]

        engine.execute(User.__table__.insert(), users)
    except:
        log('Unknown error occurred:', traceback.format_exc())

        return jsonify({
            'status': UNKNOWN_EXCEPTION
        })

    login_user(forum)

    return jsonify({
        'status': 0
    })

@meta.route('/registered', methods=['GET'])
@not_logged_in
def registered():
    return render_template('registered.html', gen_key_script=gen_key_script)

@meta.route('/login', methods=['GET'])
@not_logged_in
def login():
    return render_template('login.html', form_key=get_form_key())

@meta.route('/try-login', methods=['POST'])
@not_logged_in
@form_key_required
def try_login():
    if any(x not in request.form for x in ['board-key', 'password']):
        flash('You must specify a board key and password.', category='red')
        return redirect(url_for('meta.login'))

    if not request.form['board-key'].strip():
        flash('You must specify a board key.', category='red')
        return redirect(url_for('meta.login'))

    forum = Forum.from_key(request.form['board-key'])

    if forum is None:
        flash('The board key specified does not exist.', category='red')
        return redirect(url_for('meta.login'))

    try_hash = bcrypt.check_password_hash(forum.password, request.form['password'])

    if not try_hash:
        flash('An incorrect board key or password was specified.', category='red')

    login_user(forum)

    return redirect(url_for('manager.manage'))

@meta.route('/logout', methods=['GET'])
@login_required
@form_key_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('index'))
