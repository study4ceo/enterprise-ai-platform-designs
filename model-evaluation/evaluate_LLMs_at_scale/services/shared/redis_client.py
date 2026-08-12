import redis.asyncio as redis
from typing import Optional, Any
import json
import hashlib


class RedisClient:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        return await self.redis.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in Redis with TTL"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.setex(key, ttl, value)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key) > 0
    
    async def incr(self, key: str) -> int:
        """Increment counter"""
        return await self.redis.incr(key)
    
    async def expire(self, key: str, ttl: int):
        """Set expiry on key"""
        await self.redis.expire(key, ttl)
    
    # Response caching
    def get_cache_key(self, model: str, prompt: str) -> str:
        """Generate cache key for LLM response"""
        content = f"{model}:{prompt}"
        return f"llm_response:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def get_cached_response(self, model: str, prompt: str) -> Optional[dict]:
        """Get cached LLM response"""
        key = self.get_cache_key(model, prompt)
        cached = await self.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_response(self, model: str, prompt: str, response: dict, ttl: int = 86400):
        """Cache LLM response (24h default)"""
        key = self.get_cache_key(model, prompt)
        await self.set(key, response, ttl)
    
    # Rate limiting
    async def check_rate_limit(self, user_id: str, limit: int, window: int) -> bool:
        """
        Check if user has exceeded rate limit
        
        Args:
            user_id: User identifier
            limit: Max requests per window
            window: Time window in seconds
            
        Returns:
            True if request allowed, False if rate limited
        """
        key = f"rate_limit:{user_id}"
        current = await self.redis.get(key)
        
        if current is None:
            await self.redis.setex(key, window, 1)
            return True
        
        current_count = int(current)
        if current_count >= limit:
            return False
        
        await self.redis.incr(key)
        return True
    
    async def get_rate_limit_remaining(self, user_id: str, limit: int) -> int:
        """Get remaining requests for user"""
        key = f"rate_limit:{user_id}"
        current = await self.redis.get(key)
        if current is None:
            return limit
        return max(0, limit - int(current))
    
    # Metrics caching
    async def get_cached_metrics(self, task_id: str) -> Optional[dict]:
        """Get cached metrics for task"""
        key = f"metrics:{task_id}"
        cached = await self.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_metrics(self, task_id: str, metrics: dict, ttl: int = 3600):
        """Cache metrics for task (1h default)"""
        key = f"metrics:{task_id}"
        await self.set(key, metrics, ttl)
    
    # Job status caching
    async def update_job_progress(self, job_id: str, completed: int, total: int):
        """Update job progress in real-time"""
        key = f"job_progress:{job_id}"
        progress = {"completed": completed, "total": total, "percentage": (completed / total * 100) if total > 0 else 0}
        await self.set(key, progress, ttl=3600)
    
    async def get_job_progress(self, job_id: str) -> Optional[dict]:
        """Get real-time job progress"""
        key = f"job_progress:{job_id}"
        cached = await self.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def close(self):
        """Close Redis connection"""
        await self.redis.close()
