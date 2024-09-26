import redis

class Cache:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # Initialize the Redis client
            cls._instance.redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)
        return cls._instance

    async def add_url_cache(self, url: str, tokens: str):
        """
        Update the url's latest tokens in Redis.
        """
        self.redis_client.set(url, tokens)
        self.redis_client.expire(url, 300)


    async def get_url_cache(self, url: str) -> str:
        """
        Retrieve the url's latest tokens from Redis.
        """
        return self.redis_client.get(url)

    async def hasKey(self, url: str) -> int:
        return self.redis_client.exists(url)