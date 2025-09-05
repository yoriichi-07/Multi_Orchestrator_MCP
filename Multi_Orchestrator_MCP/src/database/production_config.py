"""
Production database configuration with external PostgreSQL support
Enhanced for serverless deployment with external providers (Supabase, PlanetScale, Neon)
"""
import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
import structlog

logger = structlog.get_logger()


class ProductionDatabaseConfig:
    """Production database configuration for external PostgreSQL providers"""
    
    def __init__(self):
        # External provider automatically provides DATABASE_URL
        # Supports Supabase, PlanetScale, Neon, etc.
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            # Fallback for development or manual configuration
            self.database_url = self._build_database_url()
        
        # Parse connection parameters with optimized defaults
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "5"))  # Optimized for serverless
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # Create engine with connection pooling optimized for serverless
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            pool_pre_ping=True,  # Essential for serverless network reliability
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            # External provider specific optimizations
            connect_args={
                "sslmode": "require",  # Most external providers require SSL
                "application_name": "autonomous-software-foundry"
            }
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(
            "fly_database_configured",
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            ssl_enabled=True
        )
    
    def _build_database_url(self) -> str:
        """Build database URL from individual components for development"""
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "asf_dev")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "password")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    async def health_check(self) -> bool:
        """Check database connectivity and health"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error("fly_database_health_check_failed", error=str(e))
            return False
    
    async def get_connection_info(self) -> dict:
        """Get database connection information for monitoring"""
        try:
            with self.engine.connect() as connection:
                version_result = connection.execute(text("SELECT version()"))
                connections_result = connection.execute(text("""
                    SELECT count(*) as active_connections 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """))
                
                return {
                    "status": "connected",
                    "version": version_result.scalar(),
                    "active_connections": connections_result.scalar(),
                    "pool_size": self.pool_size,
                    "checked_out": self.engine.pool.checkedout(),
                    "checked_in": self.engine.pool.checkedin(),
                    "overflow": self.engine.pool.overflow(),
                    "invalid": self.engine.pool.invalid()
                }
        except Exception as e:
            logger.error("database_connection_info_failed", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()


async def initialize_production_database():
    """Initialize database with required tables and indexes for production deployment"""
    try:
        # Import models after engine creation to avoid circular imports
        from src.database.models import Base
        
        db_config = ProductionDatabaseConfig()
        
        # Create all tables
        Base.metadata.create_all(bind=db_config.engine)
        
        # Create indexes for performance with IF NOT EXISTS for idempotency
        with db_config.engine.connect() as connection:
            # Project files index
            connection.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_project_files_project_id 
                ON project_files(project_id);
            """))
            
            # Health reports index for monitoring
            connection.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_health_reports_timestamp 
                ON health_reports(timestamp DESC);
            """))
            
            # Agent sessions index for active session tracking
            connection.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_sessions_last_activity 
                ON agent_sessions(last_activity DESC);
            """))
            
            # Healing attempts index for analytics
            connection.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_healing_attempts_timestamp
                ON healing_attempts(timestamp DESC);
            """))
            
            connection.commit()
        
        logger.info("fly_database_initialized", tables_created=True, indexes_created=True)
        
    except Exception as e:
        logger.error("fly_database_initialization_failed", error=str(e))
        raise


# Global database configuration instance
prod_db_config = None

def get_production_database_config() -> ProductionDatabaseConfig:
    """Get or create the global database configuration"""
    global prod_db_config
    if prod_db_config is None:
        prod_db_config = ProductionDatabaseConfig()
    return prod_db_config