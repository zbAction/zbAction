import os
import glob

from flask import abort, jsonify, render_template, send_file
from jinja2.exceptions import TemplateNotFound
from sqlalchemy.orm.exc import NoResultFound

from main import app

from db import session_factory
from models.action import Action
from models.forum import Forum
from models.mod import Mod

# Routes

blueprints = ['meta', 'jobs', 'manager']

for bp in blueprints:
    module = __import__(bp, globals(), locals(), [bp], -1)
    app.register_blueprint(getattr(module, bp), url_prefix='/' + bp)

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

            mods = forum.mod_keys.split('\r\n')

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

@app.route('/docs', methods=['GET'], defaults={'category': 'general', 'page': 'index'})
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

@app.route('/zb.action.min.js')
def serve_zbaction():
    newest = max(glob.iglob('bin/*.js'), key=os.path.getctime)

    return send_file(newest, cache_timeout=0)

@app.route('/<int:uid>')
def test(uid):
    return render_template('test.html', uid=uid)
