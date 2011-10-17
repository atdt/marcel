from flaskext.openid import OpenID
from openidredis import RedisStore
from redis import Redis, RedisError
from flask import Flask

# settings
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

redis = Redis(**app.config['REDIS'])
redis.error = RedisError

def redis_oid_store_factory():
    return 

oid = OpenID(app, store_factory=lambda: RedisStore(key_prefix="marcel:oid",
                                                   conn=redis))

import marcel.views
