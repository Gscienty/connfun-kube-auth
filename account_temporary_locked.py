import redis
from my_redis_connpool import redis_connetion_pool

def account_temporary_attempt_times(common_account_id):
    r = redis.Redis(connection_pool=redis_connetion_pool)
    times_val = r.get('attempt_times.' + common_account_id)
    if not times_val:
        return 0
    return int(times_val)

def account_temporary_attempt_times_inc(common_account_id, expire):
    r = redis.Redis(connection_pool=redis_connetion_pool)
    times_val = r.get('attempt_times.' + common_account_id)
    if not times_val:
        r.set('attempt_times.' + common_account_id, 1, expire)
    else:
        r.set('attempt_times.' + common_account_id, int(times_val) + 1, expire)
