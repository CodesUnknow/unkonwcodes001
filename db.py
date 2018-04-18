import redis
from setting import *
class RedisClient(object):
    '''#redis数据库的封装'''

    def __init__(self, host=HOST, port=PORT):
        if PASSWORD:
            self.db = redis.Redis(host=host, port=port, password=PASSWORD)
        else:
            self.db = redis.Redis(host=host, port=port)

    def get(self, count=1):
        result = self.db.lrange(REDIS_KEY_NAME, 0, count - 1)
        self.db.ltrim(REDIS_KEY_NAME, count, -1)
        return result

    def put(self, entity):
        self.db.rpush(REDIS_KEY_NAME, entity)

    def pop(self):
        try:
            return self.db.rpop(REDIS_KEY_NAME)
        except Exception as e:
            print('The queue is empty!')

    def queue_len(self):
        return self.db.llen(REDIS_KEY_NAME)
