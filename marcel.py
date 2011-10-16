from flask import Flask, render_template

from entries import redis, offers, requests

DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/requests')
def show_requests():
    return render_template('requests.html', requests=requests.all())

@app.route('/offers')
def show_offers():
    return render_template('offers.html', offers=offers.all())

@app.route('/requests/add')
def add_request():
    pass

def reset():
    keys = redis.keys('marcel:*')
    if keys: redis.delete(*keys)

def add_dummy_data():
    reset()
    uid = requests.add({
        'user_id': 'Buffy',
        'text': 'Pebble expert needed for deconstructing pebbles',
        'tags': ['pets', 'food'],
        'datetime': '1996-01-01T12:05:25-02:00'
    })
    requests.upvote(uid)
    requests.upvote(uid)

if __name__ == "__main__":
    app.run()
