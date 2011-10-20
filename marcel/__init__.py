# -*- coding: utf-8 -*-
"""
    Marcel
    ------
    A simple web app for facilitating the free exchange of goods and services.

    :copyright: (c) 2011 By Ori Livneh
    :license: GPLv3, see LICENSE for more details.
"""
from flask import Flask
from flaskext.babel import Babel, format_datetime
from flaskext.openid import OpenID
from openidredis import RedisStore
from redis import Redis, RedisError

from marcel.timesince import timesince


# settings
CSRF_ENABLED = True
DEBUG = True
SECRET_KEY = 'development key'
REDIS = {
    'host': 'localhost',
    'port': 6379,
    'password': None,
    'db': 0
}

# Initialize app. Defaults are loaded from the namespace of this module. If the
# MARCEL_SETTINGS environment variable is set, import settings from whatever
# file it points to.
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MARCEL_SETTINGS', silent=True)

# Configure a Redis connection instance
redis = Redis(**app.config['REDIS'])
redis.error = RedisError  # for convenience's sake; use in try/except

# Set up flask-openid to use Redis as its datastore
redis_store_factory = lambda: RedisStore(key_prefix='marcel:oid', conn=redis)
oid = OpenID(app, store_factory=redis_store_factory)

app.config['OPENID_PROVIDERS'] = {
    'google': 'https://www.google.com/accounts/o8/id',
    'yahoo': 'https://yahoo.com/',
}

# Set up flask-babel and register dependent template filters
babel = Babel(app)
app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.filters['timesince'] = timesince


def reset_app():
    """ Reset Marcel by deleting all associated keys """
    keys = redis.keys('marcel:*')
    if keys:
        redis.delete(*keys)

# Views must be loaded after the application object is created:
# See http://flask.pocoo.org/docs/patterns/packages/
import marcel.views
