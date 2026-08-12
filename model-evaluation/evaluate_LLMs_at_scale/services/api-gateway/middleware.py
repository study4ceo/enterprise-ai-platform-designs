from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import sys
sys.path.append('../shared')

from shared.redis_client import RedisClient
from config import settings
import logging

logger = logging.getLogger(__name__)

redis_client = RedisClient(settings.REDIS_URL)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/api/v1/health", "/metrics"]:
            return await call_next(request)
        
        # Extract user ID from token (if authenticated)
        user_id = request.state.user_id if hasattr(request.state, 'user_id') else request.client.host
        
        # Check rate limit
        allowed = await redis_client.check_rate_limit(
            user_id=user_id,
            limit=settings.RATE_LIMIT_PER_USER,
            window=settings.RATE_LIMIT_WINDOW
        )
        
        if not allowed:
            remaining = await redis_client.get_rate_limit_remaining(
                user_id, settings.RATE_LIMIT_PER_USER
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again later. Remaining: {remaining}"
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await redis_client.get_rate_limit_remaining(
            user_id, settings.RATE_LIMIT_PER_USER
        )
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_USER)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(settings.RATE_LIMIT_WINDOW)
        
        return response
