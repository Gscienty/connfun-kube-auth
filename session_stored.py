import redis
from my_redis_connpool import redis_connetion_pool


def session_store(key, value, expire=7200):
    r = redis.Redis(connection_pool=redis_connetion_pool)
    r.set('session.' + key, value, ex=expire)

def session_get(key):
    r = redis.Redis(connection_pool=redis_connetion_pool)
    return r.get('session.' + key)

def session_delete(key):
    r = redis.Redis(connection_pool=redis_connetion_pool)
    r.remove('session.' + key)

