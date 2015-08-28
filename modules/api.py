import json

from flask import Blueprint, jsonify
from flask.ext.cors import CORS
from sqlalchemy.orm.exc import NoResultFound

from main import cache

from db import session_factory
from models.action import Action
from models.forum import Forum
from models.mod import Mod
from models.user import User

api = Blueprint('api', __name__)
CORS(API)

@api.route('/mods/list/<board_key>', methods=['GET'])
def list_mods(board_key):
    forum = Forum.from_key(board_key)

    if not forum.enabled:
        return jsonify({
            'mods': []
        })

    mods = forum.mod_keys.split('\r\n')

    with session_factory() as sess:
        mods = sess.query(Mod.api_key).filter(
            Mod.api_key.in_(mods),
            Mod.enabled==True,
            Mod.root_enabled==True
        ).all()

    return jsonify({
        'mods': [mod.api_key for mod in mods]
    })

@api.route('/users/list/<board_key>', methods=['GET'])
def list_users(board_key):
    forum = Forum.from_key(board_key)

    if not forum.enabled:
        return josnify({
            'users': []
        })

    with session_factory() as sess:
        users = sess.query(
            User.uid,
            User.name
        ).filter(
            User.board_key==board_key
        ).all()

        return jsonify({
            'users': {
                user.uid: user.name for user in users
            }
        })

@cache.memoize(timeout=60 * 60)
@api.route('/actions/get/<action_id>', methods=['GET'])
def get_action_by_id(action_id):
    with session_factory() as sess:
        action = sess.query(Action).filter(
            Action.id==action_id
        ).first()

        if not action:
            return jsonify({})

        sess.expunge(action)

    return jsonify(json.loads(action.to_json()))
