"""
Redis cache configuration for serverless deployment
Enhanced for external Redis providers (Upstash, Redis Cloud)
"""
import os
import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
import structlog

logger = structlog.get_logger()


class ProductionRedisCache:
    """Production Redis cache configuration for external Redis providers"""
    
    def __init__(self):
        # External providers automatically provide REDIS_URL
        # Supports Upstash, Redis Cloud, etc.
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Parse Redis URL and extract connection details
        self._parse_redis_url()
        
        # Connection pool configuration optimized for serverless
        self.pool = ConnectionPool.from_url(
            self.redis_url,
            max_connections=10,  # Optimized for serverless resource limits
            retry_on_timeout=True,
            retry_on_error=[redis.ConnectionError, redis.TimeoutError],
            socket_timeout=5,
            socket_connect_timeout=10,  # Increased for external provider latency
            health_check_interval=30,
            # External provider specific configurations
            ssl_cert_reqs=None if self.redis_url.startswith("redis://") else "required"
        )
        
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # Cache configuration
        self.default_ttl = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour
        self.key_prefix = os.getenv("CACHE_KEY_PREFIX", "asf:")
        self.max_key_size = int(os.getenv("CACHE_MAX_KEY_SIZE", "250"))  # Redis key limit
        
        logger.info(
            "production_redis_cache_initialized",
            redis_host=self.host,
            redis_port=self.port,
            default_ttl=self.default_ttl,
            max_connections=10
        )
    
    def _parse_redis_url(self):
        """Parse Redis URL to extract connection details"""
        try:
            if "://" in self.redis_url:
                # Parse URL format: redis://user:pass@host:port/db
                url_parts = self.redis_url.split("://")[1]
                if "@" in url_parts:
                    auth_part, host_part = url_parts.split("@", 1)
                    self.host = host_part.split(":")[0]
                    self.port = int(host_part.split(":")[1].split("/")[0]) if ":" in host_part else 6379
                else:
                    self.host = url_parts.split(":")[0]
                    self.port = int(url_parts.split(":")[1].split("/")[0]) if ":" in url_parts else 6379
            else:
                self.host = "localhost"
                self.port = 6379
        except Exception as e:
            logger.warning("redis_url_parse_failed", error=str(e))
            self.host = "localhost"
            self.port = 6379
    
    def _safe_key(self, key: str) -> str:
        """Ensure key is safe for Redis and within size limits"""
        safe_key = f"{self.key_prefix}{key}"
        if len(safe_key) > self.max_key_size:
            # Truncate and add hash to ensure uniqueness
            import hashlib
            hash_suffix = hashlib.md5(safe_key.encode()).hexdigest()[:8]
            truncated = safe_key[:self.max_key_size - 9]  # 8 chars for hash + 1 for separator
            safe_key = f"{truncated}#{hash_suffix}"
        return safe_key
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            safe_key = self._safe_key(key)
            value = await self.redis_client.get(safe_key)
            
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.warning("fly_cache_get_failed", key=key, error=str(e))
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            safe_key = self._safe_key(key)
            ttl = ttl or self.default_ttl
            
            # Serialize value with error handling
            try:
                serialized_value = json.dumps(value, default=str)
            except (TypeError, ValueError) as e:
                logger.warning("cache_serialization_failed", key=key, error=str(e))
                return False
            
            await self.redis_client.setex(safe_key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.warning("fly_cache_set_failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            safe_key = self._safe_key(key)
            result = await self.redis_client.delete(safe_key)
            return result > 0
            
        except Exception as e:
            logger.warning("fly_cache_delete_failed", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            safe_key = self._safe_key(key)
            result = await self.redis_client.exists(safe_key)
            return result > 0
        except Exception as e:
            logger.warning("fly_cache_exists_failed", key=key, error=str(e))
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value in cache"""
        try:
            safe_key = self._safe_key(key)
            result = await self.redis_client.incrby(safe_key, amount)
            return result
        except Exception as e:
            logger.warning("fly_cache_increment_failed", key=key, error=str(e))
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key"""
        try:
            safe_key = self._safe_key(key)
            result = await self.redis_client.expire(safe_key, ttl)
            return result
        except Exception as e:
            logger.warning("fly_cache_expire_failed", key=key, error=str(e))
            return False
    
    async def health_check(self) -> bool:
        """Check Redis connectivity and health"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error("production_redis_health_check_failed", error=str(e))
            return False
    
    async def get_info(self) -> dict:
        """Get Redis connection and performance information"""
        try:
            info = await self.redis_client.info()
            pool_info = {
                "created_connections": self.pool.connection_pool_created,
                "available_connections": len(self.pool._available_connections),
                "in_use_connections": len(self.pool._in_use_connections)
            }
            
            return {
                "status": "connected",
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "pool_info": pool_info
            }
        except Exception as e:
            logger.error("redis_info_failed", error=str(e))
            return {"status": "error", "error": str(e)}
    
    async def flush_all(self) -> bool:
        """Flush all keys (use with caution in production)"""
        try:
            await self.redis_client.flushall()
            logger.warning("redis_flush_all_executed")
            return True
        except Exception as e:
            logger.error("redis_flush_all_failed", error=str(e))
            return False
    
    async def close(self):
        """Close Redis connection"""
        try:
            await self.redis_client.close()
            logger.info("production_redis_connection_closed")
        except Exception as e:
            logger.error("redis_close_failed", error=str(e))


# Global cache instance
prod_cache = None

def get_production_redis_cache() -> ProductionRedisCache:
    """Get or create the global Redis cache instance"""
    global prod_cache
    if prod_cache is None:
        prod_cache = ProductionRedisCache()
    return prod_cache


async def initialize_production_cache():
    """Initialize and test Redis cache connection"""
    try:
        cache = get_production_redis_cache()
        
        # Test connection
        if await cache.health_check():
            logger.info("production_redis_cache_initialized_successfully")
            
            # Set a test key to verify functionality
            await cache.set("health_check", {"timestamp": "init", "status": "ok"}, ttl=60)
            
        else:
            logger.error("production_redis_cache_initialization_failed")
            
    except Exception as e:
        logger.error("fly_cache_initialization_error", error=str(e))
        raise