from redis import Redis

redis = Redis()

class EntryManager(object):
    def __init__(self, type):
        self.type = type

    def get(self, uid):
        item = redis.hgetall("marcel:%s:%s" % (self.type, uid))
        item['tags'] = redis.smembers("marcel:%s:%s:tags" % (self.type, uid))
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

    def add(self, mapping):
        uid = redis.incr("marcel:%s:next_uid" % self.type)
        redis.zadd("marcel:%s" % self.type, uid, 0)
        tags = mapping.pop('tags')
        redis.sadd("marcel:%s:%s:tags" % (self.type, uid), *tags)
        redis.hmset("marcel:%s:%s" % (self.type, uid), mapping)
        return uid

    def upvote(self, uid):
        return redis.zincrby("marcel:%s" % self.type, uid, 1)


requests = EntryManager("requests")
offers = EntryManager("offers")
