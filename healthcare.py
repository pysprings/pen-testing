# -*- coding: utf-8 -*-
"""
    Healthcare.py
    ~~~~~~~~~~~~~
    A pen-testing example based on Flaskr by Armin Ronacher

    :license: BSD
"""

import os

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, make_response

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='secret.db',
    DEBUG=True,
    SECRET_KEY=os.urandom(8),
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/u/<username>')
def show_user(username):
    # Oops, we are forgetting to authenticate and compare to the
    # appropriate user!
    db = get_db()
    cur = db.execute('select name, email from users where name = ?',
                     [username])
    try:
        user = cur.fetchall()[0]
    except IndexError:
        abort(404)
    return render_template("user.html", user=user)


@app.route('/reset/<username>')
def reset_password(username):
    db = get_db()
    cur = db.execute('select name, reset_code from users where name = ?',
                     [username])
    try:
        user = cur.fetchall()[0]
    except IndexError:
        abort(404)
    flash('Your password was reset. Check your email')
    corr_id = user[1]
    response = make_response(redirect(url_for('show_user', username=username)))
    response.headers.add('Correlation-Id', corr_id)
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run()
