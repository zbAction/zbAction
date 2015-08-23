from flask import abort, jsonify, render_template
from flask.ext.login import current_user, login_required
from jinja2.exceptions import TemplateNotFound
from sqlalchemy.sql.functions import concat, count
from sqlalchemy.orm.exc import NoResultFound
import traceback

from main import app
from meta import meta
from jobs import jobs

from db import session_factory
from models.action import Action
from models.forum import Forum
from models.mod import Mod

# Routes

app.register_blueprint(meta)
app.register_blueprint(jobs)

@app.errorhandler(404)
@app.errorhandler(500)
@app.route('/error')
@app.route('/error/<err>')
def oops(err):
    try:
        return render_template('errors/{}.html'.format(err)), err
    except TemplateNotFound:
        return render_template('errors/404.html'), 404

@app.route('/mods/list/<board_key>', methods=['GET'])
def list_mods(board_key):
    try:
        with session_factory() as sess:
            forum = sess.query(Forum.mod_keys).filter(
                Forum.board_key==board_key,
                Forum.enabled==True
            ).one()

            mods = forum.mod_keys.split(' ')

            mods = sess.query(Mod.api_key).filter(
                Mod.api_key.in_(mods),
                Mod.enabled==True,
                Mod.root_enabled==True
            ).all()

            return jsonify({
                'mods': [mod.api_key for mod in mods]
            })
    except NoResultFound:
        return jsonify({})

@app.route('/manager', methods=['GET'])
@login_required
def manage():
    with session_factory() as sess:
        forum = sess.query(Forum).filter(
            Forum.board_key==current_user.board_key
        ).one()

        mods = forum.mod_keys.split(' ')

        mods = sess.query(
            Mod.api_key,
            Mod.enabled,
            Mod.root_enabled,
            count(Action.id).label('count')
        ).filter(
            # if for some reason somebody has the master key added.
            Mod.api_key!='0',
            Mod.api_key.in_(mods)
        ).outerjoin(
            Action,
            Action.event.like(concat(Mod.api_key, '.', '%'))
        ).group_by(
            Mod.api_key
        )

        sess.expunge_all()

    return render_template('manager.html', forum=forum, mods=mods)

@app.route('/docs/<category>', methods=['GET'], defaults={'page': 'index'})
@app.route('/docs/<category>/<page>', methods=['GET'])
def docs(category, page):
    try:
        return render_template('docs/{}/{}.html'.format(category, page))
    except TemplateNotFound:
        abort(404)

@app.route('/support')
def support():
    abort(404)

@app.route('/index')
def index():
    abort(404)

@app.route('/<int:uid>')
def test(uid):
    return render_template('test.html', uid=uid)
