from flask import jsonify, render_template
from sqlalchemy.orm.exc import NoResultFound

from models import session_factory
from zb_sync import app

from forum import Forum
from mod import Mod

@app.route('/mods/list/<board_key>')
def list_mods(board_key):
	try:
		with session_factory() as session:
			forum = session.query(Forum.mod_keys).filter(
				Forum.board_key==board_key
			).one()

			return jsonify({
				'mods': forum.mod_keys.split(' ')
			})
	except NoResultFound:
		return jsonify({})

@app.route('/')
def index():
	return render_template('test.html')