import json
import os
from dotenv import load_dotenv

load_dotenv()

class InMemoryCache:
    """Fallback in-memory cache when Redis is not available"""
    def __init__(self):
        self.cache = {}
    
    def test_connection(self):
        return True
    
    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        return None
    
    def set(self, key, value, expiry=3600):
        self.cache[key] = value
        return True
    
    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
        return True
    
    def clear_pattern(self, pattern):
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.cache[key]
        return True

class RedisCache:
    def __init__(self):
        self.redis = None
        self.fallback_cache = InMemoryCache()
        self._try_connect_redis()
    
    def _try_connect_redis(self):
        """Try to connect to Redis, fallback to in-memory if not available"""
        try:
            import redis
            self.redis = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            self.redis.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"⚠️  Redis not available, using in-memory cache: {e}")
            self.redis = None
    
    def test_connection(self):
        """Test Redis connection"""
        if self.redis:
            try:
                self.redis.ping()
                return True
            except Exception as e:
                print(f"Redis connection test failed: {e}")
                return False
        return True  # In-memory cache always works
    
    def get(self, key):
        """Get value from cache"""
        if self.redis:
            try:
                value = self.redis.get(key)
                return json.loads(value) if value else None
            except Exception as e:
                print(f"Cache get error: {e}")
                return self.fallback_cache.get(key)
        return self.fallback_cache.get(key)
    
    def set(self, key, value, expiry=3600):
        """Set value in cache with expiry"""
        if self.redis:
            try:
                self.redis.setex(key, expiry, json.dumps(value))
                return True
            except Exception as e:
                print(f"Cache set error: {e}")
                return self.fallback_cache.set(key, value, expiry)
        return self.fallback_cache.set(key, value, expiry)
    
    def delete(self, key):
        """Delete key from cache"""
        if self.redis:
            try:
                self.redis.delete(key)
                return True
            except Exception as e:
                print(f"Cache delete error: {e}")
                return self.fallback_cache.delete(key)
        return self.fallback_cache.delete(key)
    
    def clear_pattern(self, pattern):
        """Clear all keys matching pattern"""
        if self.redis:
            try:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                return True
            except Exception as e:
                print(f"Cache clear pattern error: {e}")
                return self.fallback_cache.clear_pattern(pattern)
        return self.fallback_cache.clear_pattern(pattern)

# Global cache instance
cache = RedisCache() 