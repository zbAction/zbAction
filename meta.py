import uuid

from flask import abort, Blueprint, jsonify, render_template, request, session

from main import bcrypt

from db import engine
from helpers import gen_key_script
from logger import log
from models.forum import Forum
from models.user import User
from secure import form_key_required, get_form_key

meta = Blueprint('meta', __name__, url_prefix='/meta')

@meta.route('/register', methods=['GET'])
def register():
    session['board_key'] = str(uuid.uuid4())

    return render_template(
        'register.html',
        board_key=session['board_key'],
        gen_key_script=gen_key_script()
    )

@meta.route('/finalize', methods=['POST'])
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

    return jsonify({
        'status': 0
    })

@meta.route('/registered', methods=['GET'])
def registered():
    return render_template('registered.html', gen_key_script=gen_key_script)

@meta.route('/login', methods=['GET'])
def login():
    return render_template('login.html', form_key=get_form_key())

@meta.route('/try-login', methods=['POST'])
@form_key_required
def try_login():
    pass
