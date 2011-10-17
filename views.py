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

from marcel import app, oid
from marcel.models import offers, requests, add_dummy_data

@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        # get from redis g.user = 
        g.user = session['openid']

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
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
    user = resp.email
    session['openid'] = resp.identity_url
    if user is not None:
        flash('Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())

@app.route('/requests')
def show_requests():
    return render_template('requests.html', requests=requests.all())

@app.route('/offers')
def show_offers():
    return render_template('offers.html', offers=offers.all())

@app.route('/')
def show_entries():
    return render_template('show_entries.html', offers=offers.all(),
            requests=requests.all())

@app.route('/add', methods=['POST'])
def add_entry():
    #if not session.get('logged_in'):
    #    abort(401)
    try:
        tags = tags.split()
        return str(request.form)
    except KeyError:
        pass
    #requests.add(**request.form)
    #flash("Request successfully posted")

@app.route('/debug/dummy')
def dummy():
    return str(add_dummy_data())

@app.route('/debug/alerts')
def debug_alerts():
    flash("This seems to have worked!")
    return redirect('/')

@app.route('/debug/redis')
def redis_debug():
    if g.user is None:
        abort(401)
    return render_template('redis_debug.html', info=redis.info())
