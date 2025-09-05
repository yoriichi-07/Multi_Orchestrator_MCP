"""
Production Integration Module
Integrates external service configurations with the existing MCP server
"""
import os
import asyncio
from typing import Optional, Dict, Any
import structlog

# Import external service configurations
from Multi_Orchestrator_MCP.src.database.production_config import get_production_database_config, initialize_production_database
from Multi_Orchestrator_MCP.src.cache.production_redis import get_production_redis_cache, initialize_production_cache
from Multi_Orchestrator_MCP.src.monitoring.production_metrics import production_metrics, start_metrics_collection

logger = structlog.get_logger()


class ProductionIntegration:
    """Integration layer for production deployment"""
    
    def __init__(self):
        self.database_config = None
        self.redis_cache = None
        self.metrics_collector = production_metrics
        self.region = os.getenv('FLY_REGION', 'unknown')
        self.app_name = os.getenv('FLY_APP_NAME', 'autonomous-software-foundry')
        
        logger.info(
            "production_integration_initialized",
            region=self.region,
            app_name=self.app_name
        )
    
    async def initialize(self):
        """Initialize all external services"""
        try:
            logger.info("initializing_fly_services", region=self.region)
            
            # Initialize database
            await self._initialize_database()
            
            # Initialize cache
            await self._initialize_cache()
            
            # Start metrics collection
            await self._start_metrics_collection()
            
            logger.info("fly_services_initialized_successfully")
            
        except Exception as e:
            logger.error("fly_services_initialization_failed", error=str(e))
            raise
    
    async def _initialize_database(self):
        """Initialize external PostgreSQL database"""
        try:
            self.database_config = get_production_database_config()
            await initialize_production_database()
            
            # Test connection
            if await self.database_config.health_check():
                logger.info("fly_database_ready")
            else:
                logger.warning("fly_database_health_check_failed")
                
        except Exception as e:
            logger.error("fly_database_initialization_failed", error=str(e))
            # Don't raise - allow app to start without database in development
    
    async def _initialize_cache(self):
        """Initialize external Redis cache"""
        try:
            self.redis_cache = get_production_redis_cache()
            await initialize_production_cache()
            
            # Test cache
            if await self.redis_cache.health_check():
                logger.info("production_redis_cache_ready")
            else:
                logger.warning("production_redis_cache_health_check_failed")
                
        except Exception as e:
            logger.error("production_redis_initialization_failed", error=str(e))
            # Don't raise - allow app to start without cache in development
    
    async def _start_metrics_collection(self):
        """Start background metrics collection"""
        try:
            # Start metrics collection in background
            asyncio.create_task(start_metrics_collection())
            logger.info("production_metrics_collection_started")
            
        except Exception as e:
            logger.error("production_metrics_collection_failed", error=str(e))
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status for production deployment"""
        health_status = {
            "region": self.region,
            "app_name": self.app_name,
            "timestamp": None,
            "services": {}
        }
        
        # Database health
        if self.database_config:
            try:
                db_health = await self.database_config.health_check()
                db_info = await self.database_config.get_connection_info()
                health_status["services"]["database"] = {
                    "status": "healthy" if db_health else "unhealthy",
                    "details": db_info
                }
            except Exception as e:
                health_status["services"]["database"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Cache health
        if self.redis_cache:
            try:
                cache_health = await self.redis_cache.health_check()
                cache_info = await self.redis_cache.get_info()
                health_status["services"]["cache"] = {
                    "status": "healthy" if cache_health else "unhealthy",
                    "details": cache_info
                }
            except Exception as e:
                health_status["services"]["cache"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Metrics health
        try:
            metrics_summary = await self.metrics_collector.get_health_summary()
            health_status["services"]["metrics"] = {
                "status": "healthy",
                "details": metrics_summary
            }
        except Exception as e:
            health_status["services"]["metrics"] = {
                "status": "error",
                "error": str(e)
            }
        
        return health_status
    
    def get_database_config(self):
        """Get database configuration for use by other modules"""
        return self.database_config
    
    def get_cache(self):
        """Get Redis cache for use by other modules"""
        return self.redis_cache
    
    def get_metrics_collector(self):
        """Get metrics collector for use by other modules"""
        return self.metrics_collector


# Global production integration instance
production_integration = ProductionIntegration()


async def initialize_production_integration():
    """Initialize production integration - call this from main app startup"""
    await production_integration.initialize()


def get_production_integration() -> ProductionIntegration:
    """Get the global production integration instance"""
    return production_integration