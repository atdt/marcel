import traceback
from flask import (Flask, render_template, flash, g, session, request, redirect,
    url_for, abort)
from flaskext.openid import OpenID
from openidredis import RedisStore
from redis import Redis
from redis.exceptions import ResponseError

# config
DEBUG = True
SECRET_KEY = 'development key'
REDIS = {}  # passed as kwargs to redis.Redis()

# Initialize app. Defaults are loaded from the namespace of this module. If the
# MARCEL_SETTINGS environment variable is set, import settings from whatever
# file it points to.
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MARCEL_SETTINGS', silent=True)

redis = Redis(**app.config['REDIS'])

def redis_oid_store_factory():
    return RedisStore(key_prefix="marcel:oid", conn=redis)

oid = OpenID(app, store_factory=redis_oid_store_factory)

# utils
def reset():
    keys = redis.keys('marcel:*')
    if keys: redis.delete(*keys)

def add_dummy_data():
    reset()
    uid = requests.add(
        user='Buffy',
        text='Pebble expert needed for deconstructing pebbles',
        tags=['pets', 'food'],
        datetime='1996-01-01T12:05:25-02:00'
    )
    requests.upvote(uid)
    requests.upvote(uid)

# models
class EntryManager(object):
    def __init__(self, type):
        self.type = type

    def get(self, uid):
        item = redis.hgetall("marcel:%s:%s" % (self.type, uid))
        item['tags'] = redis.smembers("marcel:%s:%s:tags" % (self.type, uid))
        item['type'] = self.type
        return item

    def all(self):
        keys = redis.zrevrange(
            name="marcel:%s" % self.type,
            start=0,
            num=-1,
            withscores=True,
            score_cast_func=int
        )
        items = []
        for uid, score in keys:
            item = self.get(uid)
            item['score'] = score  # annotate with score
            items.append(item)
        return items

    def add(self, **mapping):
        uid = redis.incr("marcel:%s:next_uid" % self.type)
        redis.zadd("marcel:%s" % self.type, uid, 0)
        tags = mapping.pop('tags')
        try:
            redis.sadd("marcel:%s:%s:tags" % (self.type, uid), *tags)
        except ResponseError:
            for tag in tags:
                redis.sadd("marcel:%s:%s:tags" % (self.type, uid), tag)
        redis.hmset("marcel:%s:%s" % (self.type, uid), mapping)
        return uid

    def upvote(self, uid):
        return redis.zincrby("marcel:%s" % self.type, uid, 1)


requests = EntryManager("request")
offers = EntryManager("offer")

# views
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

@app.route('/debug/alerts')
def debug_alerts():
    flash("This seems to have worked!")
    return redirect('/')

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

@app.route('/dummy')
def dummy():
    return str(add_dummy_data())

@app.route('/redis_debug')
def redis_debug():
    if g.user is None:
        abort(401)
    return render_template('redis_debug.html', info=redis.info())

if __name__ == "__main__":
    app.run()
