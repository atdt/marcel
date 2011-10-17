from marcel import redis

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
        except redis.error:
            for tag in tags:
                redis.sadd("marcel:%s:%s:tags" % (self.type, uid), tag)
        redis.hmset("marcel:%s:%s" % (self.type, uid), mapping)
        return uid

    def upvote(self, uid):
        return redis.zincrby("marcel:%s" % self.type, uid, 1)

requests = EntryManager("request")
offers = EntryManager("offer")


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
