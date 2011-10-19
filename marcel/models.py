from datetime import datetime
from uuid import uuid5, NAMESPACE_URL

import dateutil.parser
from flask import session

from marcel import redis


# models
class User(object):
    def __init__(self, uuid=None, openid=None):
        if uuid:
            self.uuid = uuid
        elif openid:
            self.uuid = uuid5(NAMESPACE_URL, openid)
        else:
            raise TypeError("Either a uuid or an openid is required")
        self.key = "marcel:user:%s" % self.uuid

    def from_session(self):
        return User(openid=session['openid'])

    def exists(self):
        return redis.exists(self.key)

    def get(self):
        return redis.hgetall(self.key)

    def set(self, **kwargs):
        redis.hmset(self.key, kwargs)


class EntryManager(object):
    def __init__(self, type):
        self.type = type

    def get(self, uid):
        item = redis.hgetall("marcel:%s:%s" % (self.type, uid))
        item['type'] = self.type
        item['pubdate'] = dateutil.parser.parse(item['pubdate'])
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

    def add(self, user, summary, details, contact_info):
        pubdate = datetime.now().isoformat()
        uid = redis.incr("marcel:%s:next_uid" % self.type)
        redis.zadd("marcel:%s" % self.type, uid, 0)
        redis.hmset("marcel:%s:%s" % (self.type, uid), {
            'user': user.uuid,
            'summary': summary,
            'details': details,
            'contact_info': contact_info,
            'pubdate': pubdate
        })
        return uid

    #tags = mapping.pop('tags', None)
    #if tags:
    #    try:
    #        redis.sadd("marcel:%s:%s:tags" % (self.type, uid), *tags)
    #    except redis.error:
    #        for tag in tags:
    #            redis.sadd("marcel:%s:%s:tags" % (self.type, uid), tag)

    def upvote(self, uid):
        return redis.zincrby("marcel:%s" % self.type, uid, 1)

requests = EntryManager("request")
offers = EntryManager("offer")
