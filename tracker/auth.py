from os import path
from functools import wraps

from flask import (g, session, request, redirect, abort, render_template, 
                  url_for, flash, get_flashed_messages)
from flask.ext.openid import OpenID, COMMON_PROVIDERS

from . import app
from . import models
from . import forms

oid = OpenID(app, path.join(app.instance_path,'openid_store'))

@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid'in session:
        g.user = models.User.query.filter_by(openid=session['openid']).first()

@app.route('/login', methods=['GET'])
@app.route('/login/<method>', methods=['GET'])
@oid.loginhandler
def login(method=None):
    if g.user is not None:
        return redirect(oid.get_next_url())
    if method is not None: 
        return oid.try_login(COMMON_PROVIDERS[method],
                ask_for=['email','fullname'])
    return render_template('login.html', next=oid.get_next_url(),
            error=oid.fetch_error())

@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    user = models.User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash('Login Successful')
        g.user = user
        if user.admin:
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('index'))
    return redirect(url_for('create_profile', name=resp.fullname,
        email=resp.email))

@app.route('/create-profile', methods=['GET','POST'])
def create_profile():
    email = request.values.get('email',None)
    name = request.values.get('name',None)
    form = forms.Profile(email=email,name=name)
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = models.User()
        form.populate_obj(user)
        user.openid=session['openid']
        models.db.session.add(user)
        models.db.session.commit()
        g.user = user
        tasks.send_registration(user.id)
        return redirect(url_for('index'))
    return render_template('profile.html', form=form)

@app.route('/logout')
def logout():
    session.pop('openid',None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/denied')
def permission_denied():
    msg = session.get('denied',None)
    return render_template('message.html',layout='layout.html', 
            heading='Permission Denied', message=msg)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        if g.user.suspended:
            session['denied'] = "Account has been suspended"
            return redirect(url_for('permission_denied'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        if g.user.suspended or not g.user.approved:
            session['denied'] = "Account has been suspended"
            return redirect(url_for('permission_denied'))
        if not g.user.admin:
            session['denied'] = "Admin level required"
            return redirect(url_for('permission_denied')) 
        return f(*args, **kwargs)
    return decorated_function

def elevation_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user.can_elevate:
            session['denied'] = "Elevation permission required"
            return redirect(url_for('permission_denied')) 
        return f(*args, **kwargs)
    return decorated_function

