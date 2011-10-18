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
from marcel.models import User, offers, requests, add_dummy_data, EntryManager


@app.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        g.user = User(openid=session['openid'])

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        ask_for = ['email', 'fullname', 'nickname']  # from openid provider
        if openid:
            return oid.try_login(openid, ask_for=ask_for)
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
        user.set(**{key:val for key, val in resp.__dict__.items() if val})
    flash('Successfully signed in')
    g.user = user
    return redirect(oid.get_next_url())

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
            entry_manager = EntryManager(form.entrytype.data)
            entry_manager.add(
                summary=form.summary.data,
                details=form.details.data,
                contact=form.contact.data
            )
        else:
            flash("Error")
        return render_template('show_entries.html',
                               form=form,
                               offers=offers.all(),
                               requests=requests.all())



app.add_url_rule('/', view_func=EntryAPI.as_view('entries'))

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
