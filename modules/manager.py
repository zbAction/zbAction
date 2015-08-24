from flask import Blueprint, render_template, request
from flask.ext.login import current_user, login_required
from sqlalchemy.sql.functions import concat, count

from db import session_factory
from models.action import Action
from models.mod import Mod

from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logging.basicConfig()
logger = logging.getLogger("myapp.sqltime")
logger.setLevel(logging.DEBUG)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug("Start Query: %s", statement)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug("Query Complete!")
    logger.debug("Total Time: %f", total)

manager = Blueprint('manager', __name__)

@manager.route('/', methods=['GET'])
@login_required
def manage():
    with session_factory() as sess:
        mods = current_user.mod_keys.split('\r\n')

        mods = sess.query(
            Mod.api_key,
            Mod.enabled,
            Mod.root_enabled,
            Mod.name,
            count(Action.id).label('count')
        ).filter(
            # if for some reason somebody has the master key added.
            Mod.api_key!='0',
            Mod.api_key.in_(mods)
        ).outerjoin(
            Action,
            Action.event.like(Mod.api_key + '.%')
        ).group_by(
            Mod.api_key
        ).order_by(
            # Apparently False < True in SQL.
            #
            # Order by:
            # Enabled
            # Has Name
            # Name
            (Mod.enabled and Mod.root_enabled)==False,
            Mod.name==None,
            Mod.name
        )

        sess.expunge_all()

    return render_template('manager.html', forum=current_user, mods=mods)

@manager.route('/add-mod', methods=['GET'])
@login_required
def add_mod():
    return render_template('add_mod.html', mods=current_user.mod_keys.split('\r\n'))
