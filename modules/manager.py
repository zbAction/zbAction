from flask import Blueprint, render_template
from flask.ext.login import current_user, login_required
from sqlalchemy.sql.functions import concat, count
y
from db import session_factory
from models.action import Action
from models.mod import Mod

manager = Blueprint('manager')

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
            Action.event.like(concat(Mod.api_key, '.', '%'))
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
