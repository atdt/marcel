from redis import Redis
from flask import Flask, render_template, flash

# config
DEBUG = True
SECRET_KEY = 'development key'
REDIS = {}  # passed as kwargs to redis.Redis()

# init app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MARCEL_SETTINGS', silent=True)

redis = Redis(**app.config['REDIS'])

# utils
def reset():
    keys = redis.keys('marcel:*')
    if keys: redis.delete(*keys)

def add_dummy_data():
    reset()
    uid = requests.add(
        user_id='Buffy',
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
        redis.sadd("marcel:%s:%s:tags" % (self.type, uid), *tags)
        redis.hmset("marcel:%s:%s" % (self.type, uid), mapping)
        return uid

    def upvote(self, uid):
        return redis.zincrby("marcel:%s" % self.type, uid, 1)


requests = EntryManager("request")
offers = EntryManager("offer")
# views
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
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/requests')
def show_requests():
    return render_template('requests.html', requests=requests.all())

@app.route('/offers')
def show_offers():
    return render_template('offers.html', offers=offers.all())

@app.route('/')
def all_entries():
    return render_template('all_entries.html', offers=offers.all(),
            requests=requests.all())

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    requests.add(**request.form)
    flash("Request successfully posted")
    pass

@app.route('/redis_debug')
def redis_debug():
    return render_template('redis_debug.html', info=redis.info())

if __name__ == "__main__":
    app.run()
