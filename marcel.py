from flask import Flask, render_template, flash
from entries import redis, offers, requests

# config
DEBUG = True
SECRET_KEY = 'development key'

# init app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MARCEL_SETTINGS', silent=True)

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


if __name__ == "__main__":
    app.run()
