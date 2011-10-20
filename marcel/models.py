# -*- coding: utf-8 -*-
"""
    Mapping of Python objects to Redis datatypes for Marcel

    :copyright: (c) 2011 By Ori Livneh
    :license: GPLv3, see LICENSE for more details.
"""
from datetime import datetime
from uuid import uuid5, NAMESPACE_URL

import dateutil.parser
from flask import session

from marcel import redis


class User(object):
    """ Represents a Marcel user / author """
    def __init__(self, uuid=None, openid=None):
        """ Creates a User instance; one of `uuid` or `openid` is required """
        if uuid:
            self.uuid = uuid
        elif openid:
            self.uuid = uuid5(NAMESPACE_URL, openid)
        else:
            raise TypeError("Either a uuid or an openid is required")
        self.key = "marcel:user:%s" % self.uuid

    def from_session(self):
        """ Gets the current user based on the value of `openid` in the session
        context """
        return User(openid=session['openid'])

    def exists(self):
        """ Check whether or not User exists in Redis """
        return redis.exists(self.key)

    def get(self):
        """ Retrieve a User from Redis """
        return redis.hgetall(self.key)

    def set(self, **kwargs):
        """ Store User attributes in Redis """
        redis.hmset(self.key, {key: val for key, val in kwargs.items() if val})


class EntryManager(object):
    """
    The EntryManager class manages both requests and offers.
    """
    def __init__(self, type):
        """ Instantiates a manager for `type` entry type """
        self.type = type

    def get(self, uid):
        """ Retrieves record `uid` from Redis """
        item = redis.hgetall("marcel:%s:%s" % (self.type, uid))
        item['type'] = self.type
        item['pubdate'] = dateutil.parser.parse(item['pubdate'])
        return item

    def all(self):
        """ Gets all records of type self.type """
        # TODO(Ori): This is a sorted set because I initially thought it'd be
        # neat to allow users to vote on requests, but then I had second
        # thoughts. We should decide if we want to keep this a sorted set.
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

    def add(self, user, summary, details, contact_info, pubdate=None):
        """ Adds a new entry """
        if pubdate is None:
            pubdate = datetime.now().isoformat()
        # TODO(Ori): Should we batch these into a single transaction?
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

    def upvote(self, uid):
        # Increments an entry's score by 1. See comment above regarding voting.
        return redis.zincrby("marcel:%s" % self.type, uid, 1)

# Initialize managers for the two types of entries we have:
requests = EntryManager("request")
offers = EntryManager("offer")
