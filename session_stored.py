import redis
import os
from redis_connetion_pool import redis_connetion_pool


def password_session_store(key, value, expire=7200):
    r = redis.Redis(connection_pool=redis_connetion_pool)
    r.set(key, value, ex=expire)

def password_session_get(key):
    r = redis.Redis(connection_pool=redis_connetion_pool)
    return r.get(key)

