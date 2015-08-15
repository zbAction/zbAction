from flask import abort, jsonify, render_template
from jinja2.exceptions import TemplateNotFound
from sqlalchemy.orm.exc import NoResultFound
import traceback

from main import app
from meta import meta
from jobs import jobs

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

@app.route('/docs/<category>', methods=['GET'], defaults={'page': 'index'})
@app.route('/docs/<category>/<page>', methods=['GET'])
def docs(category, page):
    try:
        return render_template('docs/{}/{}.html'.format(category, page))
    except TemplateNotFound:
        abort(404)

@app.route('/<int:uid>')
def index(uid):
    return render_template('test.html', uid=uid)
