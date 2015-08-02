from flask import jsonify, render_template
from sqlalchemy.orm.exc import NoResultFound

from db import session_factory
from zb_sync import app

from models.forum import Forum
from models.mod import Mod

@app.route('/mods/list/<board_key>')
def list_mods(board_key):
    try:
        with session_factory() as session:
            forum = session.query(Forum.mod_keys).filter(
                Forum.board_key==board_key,
            ).one()

            mods = forum.mod_keys.split(' ')

            mods = session.query(Mod.api_key).filter(
                Mod.api_key.in_(mods),
                Mod.enabled==True
            ).all()

            return jsonify({
                'mods': [mod.api_key for mod in mods]
            })
    except NoResultFound:
        return jsonify({})

@app.route('/<uid>')
def index(uid):
    return render_template('test.html', uid=uid)

@app.route('/register')
def register():
    return render_template('register.html')