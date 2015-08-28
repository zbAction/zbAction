import os

from flask import abort, redirect, render_template, send_file
from jinja2.exceptions import TemplateNotFound

from main import app, cache

from db import session_factory

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
    return redirect('http://s15.zetaboards.com/zba/index/')

@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')

@app.route('/<int:uid>')
def test(uid):
    return render_template('test.html', uid=uid)
