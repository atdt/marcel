# -*- coding: utf-8 -*-
"""
    Marcel views

    :copyright: (c) 2011 By Ori Livneh
    :license: BSD, see LICENSE for more details.
"""
   
from flask import (
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from flask.views import MethodView

from marcel import app, oid
from marcel.forms import EntryForm
from marcel.models import User, offers, requests, EntryManager


#
# Contexts
#

# Make the authentication status available in template contexts
@app.context_processor
def inject_authentication_status():
    return dict(authenticated=hasattr(g.user, 'uuid'))

# Embed the current user (if any) in the request context
@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        g.user = User(openid=session['openid'])


#
# Login Views
#

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    providers = app.config['OPENID_PROVIDERS']
    openid = None
    if request.method == 'GET' and 'provider' in request.args:
        openid = providers.get(request.args.get('provider'))
    elif request.method == 'POST':
        openid = request.form.get('openid')
    if openid:
        return oid.try_login(openid, ask_for=['email'])
    return render_template('login.html',
                            next=oid.get_next_url(),
                            error=oid.fetch_error())


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash('You were signed out')
    return redirect(oid.get_next_url())


@oid.after_login
def after_login(resp):
    session['openid'] = resp.identity_url
    user = User(openid=resp.identity_url)
    if not user.exists():
        user.set(identity_url=resp.identity_url, email=resp.email)
    flash('Successfully signed in')
    g.user = user
    return redirect(oid.get_next_url())


#
# Entry Views
#

class EntryAPI(MethodView):
    def get(self):
        form = EntryForm()
        return render_template('show_entries.html',
                               form=form,
                               offers=offers.all(),
                               requests=requests.all())

    def post(self):
        form = EntryForm()
        if form.validate():
            flash("Success")
            entry_manager = EntryManager(form.entry_type.data)
            entry_manager.add(
                user=g.user,
                summary=form.summary.data,
                details=form.details.data,
                contact_info=form.contact_info.data
            )
        else:
            flash("Error")
        return render_template('show_entries.html',
                               form=form,
                               offers=offers.all(),
                               requests=requests.all())


app.add_url_rule('/', view_func=EntryAPI.as_view('entries'))
