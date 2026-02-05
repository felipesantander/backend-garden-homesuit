import redis
from django.conf import settings

import os

class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance.connection = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'localhost'),
                port=6379,
                db=0,
                decode_responses=True
            )
        return cls._instance

    def get_connection(self):
        return self.connection

redis_client = RedisClient()
