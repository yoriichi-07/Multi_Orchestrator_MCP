"""
Production metrics collection and monitoring for serverless deployment
Enhanced with Vercel and external service specific metrics and monitoring capabilities
"""
import time
import asyncio
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
import structlog
import psutil
import os

logger = structlog.get_logger()


class ProductionMetricsCollector:
    """Production metrics collection optimized for serverless deployment"""
    
    def __init__(self):
        # Create custom registry for isolation
        self.registry = CollectorRegistry()
        
        # HTTP request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code', 'region'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # MCP protocol metrics
        self.mcp_tool_calls_total = Counter(
            'mcp_tool_calls_total',
            'Total MCP tool calls',
            ['tool_name', 'status', 'region'],
            registry=self.registry
        )
        
        self.mcp_tool_duration = Histogram(
            'mcp_tool_duration_seconds',
            'MCP tool execution duration',
            ['tool_name'],
            buckets=[1, 5, 15, 30, 60, 300, 600],
            registry=self.registry
        )
        
        # Code generation metrics
        self.code_generation_total = Counter(
            'code_generation_total',
            'Total code generation requests',
            ['agent_type', 'status', 'language'],
            registry=self.registry
        )
        
        self.code_generation_duration = Histogram(
            'code_generation_duration_seconds',
            'Code generation duration',
            ['agent_type'],
            buckets=[5, 15, 30, 60, 120, 300, 600],
            registry=self.registry
        )
        
        # Self-healing metrics
        self.healing_attempts_total = Counter(
            'healing_attempts_total',
            'Total self-healing attempts',
            ['issue_type', 'status', 'severity'],
            registry=self.registry
        )
        
        self.healing_success_rate = Gauge(
            'healing_success_rate',
            'Self-healing success rate',
            registry=self.registry
        )
        
        self.healing_duration = Histogram(
            'healing_duration_seconds',
            'Self-healing process duration',
            ['issue_type'],
            buckets=[1, 5, 10, 30, 60, 300, 600],
            registry=self.registry
        )
        
        # System health metrics
        self.health_score = Gauge(
            'system_health_score',
            'Overall system health score',
            ['project_id', 'region'],
            registry=self.registry
        )
        
        self.active_sessions = Gauge(
            'active_sessions_total',
            'Number of active agent sessions',
            ['session_type'],
            registry=self.registry
        )
        
        # LLM usage metrics
        self.llm_requests_total = Counter(
            'llm_requests_total',
            'Total LLM requests',
            ['model', 'operation', 'status'],
            registry=self.registry
        )
        
        self.llm_tokens_used = Counter(
            'llm_tokens_used_total',
            'Total LLM tokens used',
            ['model', 'operation', 'token_type'],
            registry=self.registry
        )
        
        self.llm_cost_estimate = Counter(
            'llm_cost_estimate_usd',
            'Estimated LLM costs in USD',
            ['model'],
            registry=self.registry
        )
        
        # Serverless deployment specific metrics
        self.vercel_region = Gauge(
            'vercel_region_info',
            'Vercel region information',
            ['region', 'app_name'],
            registry=self.registry
        )
        
        self.vercel_memory_usage = Gauge(
            'vercel_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.vercel_cpu_usage = Gauge(
            'vercel_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.vercel_disk_usage = Gauge(
            'vercel_disk_usage_bytes',
            'Disk usage in bytes',
            ['mount_point'],
            registry=self.registry
        )
        
        # Database metrics
        self.database_connections = Gauge(
            'database_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.database_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query execution time',
            ['query_type'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_operations_total = Counter(
            'cache_operations_total',
            'Total cache operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'cache_hit_rate',
            'Cache hit rate percentage',
            registry=self.registry
        )
        
        # Application info
        self.app_info = Info(
            'app_info',
            'Application information',
            registry=self.registry
        )
        
        # Set static application info
        self._set_app_info()
        
        # Initialize Vercel specific metrics
        self._initialize_vercel_metrics()

        logger.info("production_metrics_collector_initialized")

    def _set_app_info(self):
        """Set static application information"""
        self.app_info.info({
            'version': '1.0.0',
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            'environment': os.getenv('APP_ENV', 'development'),
            'region': os.getenv('VERCEL_REGION', 'unknown'),
            'app_name': os.getenv('VERCEL_URL', 'autonomous-software-foundry')
        })
    
    def _initialize_vercel_metrics(self):
        """Initialize Vercel specific metrics"""
        region = os.getenv('VERCEL_REGION', 'unknown')
        app_name = os.getenv('VERCEL_URL', 'autonomous-software-foundry')

        self.vercel_region.labels(region=region, app_name=app_name).set(1)

    async def collect_system_metrics(self):
        """Collect system metrics (CPU, memory, disk)"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.vercel_memory_usage.set(memory.used)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.fly_cpu_usage.set(cpu_percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.fly_disk_usage.labels(mount_point='/').set(disk.used)
            
        except Exception as e:
            logger.warning("system_metrics_collection_failed", error=str(e))
    
    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        region: Optional[str] = None
    ):
        """Record HTTP request metrics"""
        region = region or os.getenv('FLY_REGION', 'unknown')
        
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            region=region
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_tool_call(
        self,
        tool_name: str,
        status: str,
        duration: float
    ):
        """Record MCP tool call metrics"""
        region = os.getenv('FLY_REGION', 'unknown')
        
        self.mcp_tool_calls_total.labels(
            tool_name=tool_name,
            status=status,
            region=region
        ).inc()
        
        self.mcp_tool_duration.labels(
            tool_name=tool_name
        ).observe(duration)
    
    def record_code_generation(
        self,
        agent_type: str,
        status: str,
        duration: float,
        language: str = "python"
    ):
        """Record code generation metrics"""
        self.code_generation_total.labels(
            agent_type=agent_type,
            status=status,
            language=language
        ).inc()
        
        self.code_generation_duration.labels(
            agent_type=agent_type
        ).observe(duration)
    
    def record_healing_attempt(
        self,
        issue_type: str,
        status: str,
        duration: float,
        severity: str = "medium"
    ):
        """Record self-healing attempt"""
        self.healing_attempts_total.labels(
            issue_type=issue_type,
            status=status,
            severity=severity
        ).inc()
        
        self.healing_duration.labels(
            issue_type=issue_type
        ).observe(duration)
    
    def update_health_score(self, project_id: str, score: float):
        """Update system health score"""
        region = os.getenv('FLY_REGION', 'unknown')
        self.health_score.labels(project_id=project_id, region=region).set(score)
    
    def record_llm_usage(
        self,
        model: str,
        operation: str,
        status: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float
    ):
        """Record LLM usage metrics"""
        self.llm_requests_total.labels(
            model=model,
            operation=operation,
            status=status
        ).inc()
        
        self.llm_tokens_used.labels(
            model=model,
            operation=operation,
            token_type="input"
        ).inc(input_tokens)
        
        self.llm_tokens_used.labels(
            model=model,
            operation=operation,
            token_type="output"
        ).inc(output_tokens)
        
        self.llm_cost_estimate.labels(model=model).inc(estimated_cost)
    
    def record_database_query(self, query_type: str, duration: float):
        """Record database query metrics"""
        self.database_query_duration.labels(
            query_type=query_type
        ).observe(duration)
    
    def update_database_connections(self, active_connections: int):
        """Update active database connections count"""
        self.database_connections.set(active_connections)
    
    def record_cache_operation(self, operation: str, status: str):
        """Record cache operation"""
        self.cache_operations_total.labels(
            operation=operation,
            status=status
        ).inc()
    
    def update_cache_hit_rate(self, hit_rate: float):
        """Update cache hit rate"""
        self.cache_hit_rate.set(hit_rate)
    
    def update_active_sessions(self, session_type: str, count: int):
        """Update active sessions count"""
        self.active_sessions.labels(session_type=session_type).set(count)
    
    def get_metrics(self) -> bytes:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry)
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        try:
            await self.collect_system_metrics()
            
            return {
                "timestamp": time.time(),
                "region": os.getenv('FLY_REGION', 'unknown'),
                "app_name": os.getenv('FLY_APP_NAME', 'autonomous-software-foundry'),
                "system": {
                    "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
                    "memory_percent": psutil.virtual_memory().percent,
                    "cpu_percent": psutil.cpu_percent(),
                    "disk_used_gb": psutil.disk_usage('/').used / 1024 / 1024 / 1024
                },
                "status": "healthy"
            }
        except Exception as e:
            logger.error("health_summary_failed", error=str(e))
            return {
                "timestamp": time.time(),
                "status": "error",
                "error": str(e)
            }


# Global metrics instance
production_metrics = ProductionMetricsCollector()


async def start_metrics_collection():
    """Start background metrics collection"""
    try:
        while True:
            await production_metrics.collect_system_metrics()
            await asyncio.sleep(30)  # Collect every 30 seconds
    except Exception as e:
        logger.error("metrics_collection_stopped", error=str(e))