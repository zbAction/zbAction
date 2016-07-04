import os

from flask import abort, redirect, render_template, send_file, url_for
from flask.ext.login import current_user
from jinja2.exceptions import TemplateNotFound
import markdown
from xml.etree import ElementTree

from main import app, cache

from db import flarum_session_factory
from object import Object

# Routes

blueprints = ['api', 'meta', 'jobs', 'manager']

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
    return redirect('https://forum.zbaction.reticent.io')

@app.route('/announcements')
@app.route('/announcements/<int:id>')
def announcements(id=None):
    with flarum_session_factory() as sess:
        if id is None:
            with flarum_session_factory() as sess:
                res = sess.execute(
                    '''
                    SELECT
                        x.id,
                        x.title,
                        u.username AS 'author',
                        x.start_time AS 'timestamp',
                        z.content
                    FROM flarum_discussions x
                    JOIN 
                        flarum_discussions_tags y
                        ON x.id=y.discussion_id
                    JOIN
                        flarum_posts z
                        ON x.start_post_id=z.id
                    JOIN
                        flarum_users u
                        ON x.start_user_id=u.id
                    WHERE
                        y.tag_id=10
                    ORDER BY x.start_time DESC
                    '''
                )

                posts = [
                    Object({
                        'id': r.id,
                        'title': r.title,
                        'author': r.author,
                        'timestamp': r.timestamp,
                        'content': markdown.markdown(
                            ''.join(ElementTree.fromstring(r.content).itertext()),
                            extensions=['pymdownx.github']
                        )
                    }) for r in res
                ]

                return render_template('announcements.html', posts=posts)
        else:
            try:
                res = sess.execute(
                    '''
                    SELECT
                        x.id,
                        x.title,
                        u.username AS 'author',
                        x.start_time AS 'timestamp',
                        z.content
                    FROM flarum_discussions x
                    JOIN 
                        flarum_discussions_tags y
                        ON x.id=y.discussion_id
                    JOIN
                        flarum_posts z
                        ON x.start_post_id=z.id
                    JOIN
                        flarum_users u
                        ON x.start_user_id=u.id
                    WHERE
                        y.tag_id=10
                        AND
                        x.id={}
                    ORDER BY x.start_time DESC
                    '''.format(id)
                )

                post = [Object({
                    'id': r.id,
                    'title': r.title,
                    'author': r.author,
                    'timestamp': r.timestamp,
                    'content': markdown.markdown(
                        ''.join(ElementTree.fromstring(r.content).itertext()),
                        extensions=['pymdownx.github']
                    )
                }) for r in res][0]

                return render_template('post.html', post=post)
            except:
                return redirect(url_for('oops', err=404))

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return announcements()
    else:
        return render_template('home.html')

@app.route('/<int:uid>')
def test(uid):
    return render_template('test.html', uid=uid)
