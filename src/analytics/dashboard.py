"""
🏆 Competition-Grade Analytics Dashboard
Advanced real-time monitoring and predictive insights engine
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
import uuid
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetric:
    """Real-time performance tracking"""
    metric_id: str
    timestamp: datetime
    agent_id: str
    task_type: str
    execution_time: float
    success_rate: float
    resource_usage: Dict[str, Any]
    quality_score: float
    user_satisfaction: float

@dataclass
class PredictiveInsight:
    """AI-powered predictive analytics"""
    insight_id: str
    timestamp: datetime
    category: str
    prediction: str
    confidence: float
    impact_score: float
    recommended_actions: List[str]
    data_points: Dict[str, Any]

class AdvancedAnalyticsDashboard:
    """
    🎯 Competition-Grade Analytics Engine
    Real-time monitoring + predictive intelligence + optimization recommendations
    """
    
    def __init__(self):
        self.performance_history: deque = deque(maxlen=10000)
        self.real_time_metrics: Dict[str, Any] = {}
        self.predictive_models: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, float] = {
            'response_time': 30.0,  # seconds
            'success_rate': 0.95,   # 95%
            'resource_usage': 0.85, # 85%
            'quality_score': 0.90   # 90%
        }
        self.dashboard_started = datetime.now(timezone.utc)
        self.active_sessions: Dict[str, Dict] = {}
        
    async def track_performance_metric(self, 
                                     agent_id: str,
                                     task_type: str,
                                     execution_time: float,
                                     success: bool,
                                     resource_usage: Dict[str, Any],
                                     quality_score: float = 0.9,
                                     user_satisfaction: float = 0.85) -> str:
        """Track real-time performance with advanced analytics"""
        
        metric_id = str(uuid.uuid4())
        metric = PerformanceMetric(
            metric_id=metric_id,
            timestamp=datetime.now(timezone.utc),
            agent_id=agent_id,
            task_type=task_type,
            execution_time=execution_time,
            success_rate=1.0 if success else 0.0,
            resource_usage=resource_usage,
            quality_score=quality_score,
            user_satisfaction=user_satisfaction
        )
        
        # Store in history
        self.performance_history.append(metric)
        
        # Update real-time metrics
        await self._update_real_time_metrics(metric)
        
        # Generate alerts if needed
        await self._check_alert_conditions(metric)
        
        # Update predictive models
        await self._update_predictive_models(metric)
        
        return metric_id
    
    async def _update_real_time_metrics(self, metric: PerformanceMetric):
        """Update real-time dashboard metrics"""
        
        current_time = datetime.now(timezone.utc)
        
        # Agent-specific metrics
        agent_key = f"agent_{metric.agent_id}"
        if agent_key not in self.real_time_metrics:
            self.real_time_metrics[agent_key] = {
                'total_tasks': 0,
                'success_count': 0,
                'total_execution_time': 0.0,
                'avg_quality_score': 0.0,
                'avg_satisfaction': 0.0,
                'last_activity': current_time,
                'resource_trend': []
            }
        
        agent_metrics = self.real_time_metrics[agent_key]
        agent_metrics['total_tasks'] += 1
        agent_metrics['success_count'] += int(metric.success_rate)
        agent_metrics['total_execution_time'] += metric.execution_time
        agent_metrics['last_activity'] = current_time
        
        # Calculate rolling averages
        agent_metrics['success_rate'] = agent_metrics['success_count'] / agent_metrics['total_tasks']
        agent_metrics['avg_execution_time'] = agent_metrics['total_execution_time'] / agent_metrics['total_tasks']
        agent_metrics['avg_quality_score'] = (agent_metrics.get('avg_quality_score', 0.0) * 0.8 + metric.quality_score * 0.2)
        agent_metrics['avg_satisfaction'] = (agent_metrics.get('avg_satisfaction', 0.0) * 0.8 + metric.user_satisfaction * 0.2)
        
        # Resource usage trending
        agent_metrics['resource_trend'].append({
            'timestamp': current_time,
            'cpu_usage': metric.resource_usage.get('cpu_usage', 0.0),
            'memory_usage': metric.resource_usage.get('memory_usage', 0.0),
            'network_io': metric.resource_usage.get('network_io', 0.0)
        })
        
        # Keep only last 100 data points for trending
        if len(agent_metrics['resource_trend']) > 100:
            agent_metrics['resource_trend'] = agent_metrics['resource_trend'][-100:]
        
        # System-wide metrics
        if 'system_overview' not in self.real_time_metrics:
            self.real_time_metrics['system_overview'] = {
                'total_tasks_processed': 0,
                'overall_success_rate': 0.0,
                'average_response_time': 0.0,
                'active_agents': set(),
                'peak_performance_time': current_time,
                'system_health_score': 0.0
            }
        
        system_metrics = self.real_time_metrics['system_overview']
        system_metrics['total_tasks_processed'] += 1
        system_metrics['active_agents'].add(metric.agent_id)
        
        # Calculate system health score (0-100)
        health_factors = {
            'success_rate': agent_metrics['success_rate'] * 30,
            'response_time': max(0, (60 - metric.execution_time) / 60) * 25,
            'quality_score': metric.quality_score * 25,
            'satisfaction': metric.user_satisfaction * 20
        }
        system_metrics['system_health_score'] = sum(health_factors.values())
    
    async def _check_alert_conditions(self, metric: PerformanceMetric):
        """Check for alert conditions and generate warnings"""
        
        alerts = []
        
        # Response time alert
        if metric.execution_time > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'performance_warning',
                'message': f"Slow response time: {metric.execution_time:.1f}s for {metric.agent_id}",
                'severity': 'medium' if metric.execution_time < 60 else 'high'
            })
        
        # Success rate alert (based on recent history)
        recent_metrics = [m for m in list(self.performance_history)[-20:] if m.agent_id == metric.agent_id]
        if len(recent_metrics) >= 5:
            recent_success_rate = sum(m.success_rate for m in recent_metrics) / len(recent_metrics)
            if recent_success_rate < self.alert_thresholds['success_rate']:
                alerts.append({
                    'type': 'reliability_warning',
                    'message': f"Low success rate: {recent_success_rate:.1%} for {metric.agent_id}",
                    'severity': 'high'
                })
        
        # Quality score alert
        if metric.quality_score < self.alert_thresholds['quality_score']:
            alerts.append({
                'type': 'quality_warning',
                'message': f"Quality below threshold: {metric.quality_score:.1%} for {metric.agent_id}",
                'severity': 'medium'
            })
        
        # Resource usage alert
        cpu_usage = metric.resource_usage.get('cpu_usage', 0.0)
        memory_usage = metric.resource_usage.get('memory_usage', 0.0)
        
        if cpu_usage > self.alert_thresholds['resource_usage']:
            alerts.append({
                'type': 'resource_warning',
                'message': f"High CPU usage: {cpu_usage:.1%} for {metric.agent_id}",
                'severity': 'medium'
            })
        
        if memory_usage > self.alert_thresholds['resource_usage']:
            alerts.append({
                'type': 'resource_warning',
                'message': f"High memory usage: {memory_usage:.1%} for {metric.agent_id}",
                'severity': 'medium'
            })
        
        # Store alerts in real-time metrics
        if alerts:
            if 'active_alerts' not in self.real_time_metrics:
                self.real_time_metrics['active_alerts'] = []
            
            for alert in alerts:
                alert['timestamp'] = datetime.now(timezone.utc)
                alert['metric_id'] = metric.metric_id
                self.real_time_metrics['active_alerts'].append(alert)
            
            # Keep only last 50 alerts
            self.real_time_metrics['active_alerts'] = self.real_time_metrics['active_alerts'][-50:]
    
    async def _update_predictive_models(self, metric: PerformanceMetric):
        """Update predictive models with new data"""
        
        # Ensure we have enough data for predictions
        if len(self.performance_history) < 10:
            return
        
        # Prepare data for analysis
        recent_data = list(self.performance_history)[-100:]  # Last 100 metrics
        
        # Performance trend analysis
        execution_times = [m.execution_time for m in recent_data]
        success_rates = [m.success_rate for m in recent_data]
        quality_scores = [m.quality_score for m in recent_data]
        
        # Simple trend analysis (could be enhanced with ML models)
        if len(execution_times) >= 20:
            recent_avg = statistics.mean(execution_times[-10:])
            older_avg = statistics.mean(execution_times[-20:-10])
            
            if recent_avg > older_avg * 1.2:  # 20% increase
                await self._generate_predictive_insight(
                    'performance_degradation',
                    'Response times are trending upward',
                    0.75,
                    8.5,
                    [
                        'Consider scaling up resources',
                        'Review recent code changes',
                        'Analyze system bottlenecks'
                    ],
                    {
                        'trend_increase': (recent_avg - older_avg) / older_avg,
                        'recent_avg': recent_avg,
                        'older_avg': older_avg
                    }
                )
        
        # Agent workload prediction
        agent_workloads = defaultdict(list)
        for m in recent_data:
            agent_workloads[m.agent_id].append(m.execution_time)
        
        for agent_id, times in agent_workloads.items():
            if len(times) >= 10:
                avg_time = statistics.mean(times)
                time_variance = statistics.variance(times) if len(times) > 1 else 0
                
                if time_variance > avg_time * 0.5:  # High variance
                    await self._generate_predictive_insight(
                        'workload_instability',
                        f'Agent {agent_id} showing inconsistent performance',
                        0.65,
                        6.0,
                        [
                            f'Investigate {agent_id} task allocation',
                            'Consider workload rebalancing',
                            'Monitor resource constraints'
                        ],
                        {
                            'agent_id': agent_id,
                            'avg_time': avg_time,
                            'variance': time_variance,
                            'coefficient_variation': time_variance / avg_time if avg_time > 0 else 0
                        }
                    )
        
        # System capacity prediction
        total_tasks_last_hour = len([m for m in recent_data 
                                   if (datetime.now(timezone.utc) - m.timestamp).seconds < 3600])
        
        if total_tasks_last_hour > 100:  # High load scenario
            avg_success_rate = statistics.mean(success_rates)
            if avg_success_rate < 0.95:
                await self._generate_predictive_insight(
                    'capacity_warning',
                    'System approaching capacity limits',
                    0.85,
                    9.0,
                    [
                        'Scale out additional agents',
                        'Implement load balancing',
                        'Optimize critical paths'
                    ],
                    {
                        'tasks_per_hour': total_tasks_last_hour,
                        'success_rate': avg_success_rate,
                        'load_factor': total_tasks_last_hour / 100
                    }
                )
    
    async def _generate_predictive_insight(self,
                                         category: str,
                                         prediction: str,
                                         confidence: float,
                                         impact_score: float,
                                         recommended_actions: List[str],
                                         data_points: Dict[str, Any]):
        """Generate and store predictive insights"""
        
        insight = PredictiveInsight(
            insight_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            category=category,
            prediction=prediction,
            confidence=confidence,
            impact_score=impact_score,
            recommended_actions=recommended_actions,
            data_points=data_points
        )
        
        # Store in predictive models
        if 'insights' not in self.predictive_models:
            self.predictive_models['insights'] = []
        
        self.predictive_models['insights'].append(insight)
        
        # Keep only last 100 insights
        self.predictive_models['insights'] = self.predictive_models['insights'][-100:]
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data for visualization"""
        
        current_time = datetime.now(timezone.utc)
        uptime = (current_time - self.dashboard_started).total_seconds()
        
        # Calculate system statistics
        recent_metrics = list(self.performance_history)[-100:] if self.performance_history else []
        
        system_stats = {
            'uptime_seconds': uptime,
            'uptime_formatted': f"{uptime/3600:.1f} hours",
            'total_metrics_collected': len(self.performance_history),
            'metrics_last_hour': len([m for m in recent_metrics 
                                    if (current_time - m.timestamp).seconds < 3600]),
            'overall_success_rate': statistics.mean([m.success_rate for m in recent_metrics]) if recent_metrics else 0.0,
            'average_response_time': statistics.mean([m.execution_time for m in recent_metrics]) if recent_metrics else 0.0,
            'active_agents_count': len(self.real_time_metrics.get('system_overview', {}).get('active_agents', set())),
            'system_health_score': self.real_time_metrics.get('system_overview', {}).get('system_health_score', 0.0)
        }
        
        # Get recent insights
        recent_insights = []
        if 'insights' in self.predictive_models:
            recent_insights = [
                asdict(insight) for insight in self.predictive_models['insights'][-10:]
            ]
        
        # Performance trends
        performance_trends = {}
        if recent_metrics:
            # Group by agent
            agent_trends = defaultdict(list)
            for metric in recent_metrics:
                agent_trends[metric.agent_id].append({
                    'timestamp': metric.timestamp.isoformat(),
                    'execution_time': metric.execution_time,
                    'success_rate': metric.success_rate,
                    'quality_score': metric.quality_score
                })
            performance_trends = dict(agent_trends)
        
        return {
            'timestamp': current_time.isoformat(),
            'system_stats': system_stats,
            'real_time_metrics': {
                k: v for k, v in self.real_time_metrics.items() 
                if k != 'system_overview' or isinstance(v.get('active_agents'), (list, set))
            },
            'performance_trends': performance_trends,
            'predictive_insights': recent_insights,
            'active_alerts': self.real_time_metrics.get('active_alerts', [])[-10:],  # Last 10 alerts
            'dashboard_status': 'healthy'
        }
    
    async def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization recommendations"""
        
        if len(self.performance_history) < 20:
            return {
                'status': 'insufficient_data',
                'message': 'Need more performance data for optimization analysis',
                'recommendations': []
            }
        
        recent_data = list(self.performance_history)[-200:]  # Last 200 metrics
        
        # Analyze bottlenecks
        bottlenecks = []
        
        # Response time analysis
        slow_agents = defaultdict(list)
        for metric in recent_data:
            if metric.execution_time > 30:  # Slow threshold
                slow_agents[metric.agent_id].append(metric.execution_time)
        
        for agent_id, times in slow_agents.items():
            if len(times) >= 5:  # Consistent slowness
                avg_time = statistics.mean(times)
                bottlenecks.append({
                    'type': 'response_time',
                    'agent_id': agent_id,
                    'severity': 'high' if avg_time > 60 else 'medium',
                    'avg_time': avg_time,
                    'occurrence_count': len(times),
                    'recommendation': f'Optimize {agent_id} processing pipeline'
                })
        
        # Resource utilization analysis
        resource_issues = []
        for metric in recent_data:
            cpu = metric.resource_usage.get('cpu_usage', 0.0)
            memory = metric.resource_usage.get('memory_usage', 0.0)
            
            if cpu > 0.8 or memory > 0.8:
                resource_issues.append({
                    'agent_id': metric.agent_id,
                    'cpu_usage': cpu,
                    'memory_usage': memory,
                    'timestamp': metric.timestamp.isoformat()
                })
        
        # Success rate analysis
        failure_patterns = defaultdict(int)
        for metric in recent_data:
            if metric.success_rate < 1.0:
                failure_patterns[metric.agent_id] += 1
        
        # Generate recommendations
        recommendations = []
        
        # Performance recommendations
        if bottlenecks:
            recommendations.append({
                'category': 'performance',
                'priority': 'high',
                'title': 'Address Response Time Bottlenecks',
                'description': f'Found {len(bottlenecks)} agents with consistent slow responses',
                'actions': [
                    'Profile slow agents for optimization opportunities',
                    'Consider parallel processing for heavy tasks',
                    'Implement caching for repeated operations'
                ],
                'expected_impact': 'Reduce average response time by 30-50%'
            })
        
        # Resource recommendations
        if resource_issues:
            recommendations.append({
                'category': 'resources',
                'priority': 'medium',
                'title': 'Optimize Resource Utilization',
                'description': f'Detected {len(resource_issues)} high resource usage instances',
                'actions': [
                    'Scale up infrastructure for high-load agents',
                    'Implement resource pooling',
                    'Add auto-scaling policies'
                ],
                'expected_impact': 'Improve system stability and reduce resource contention'
            })
        
        # Reliability recommendations
        if failure_patterns:
            total_failures = sum(failure_patterns.values())
            recommendations.append({
                'category': 'reliability',
                'priority': 'high',
                'title': 'Improve System Reliability',
                'description': f'Detected {total_failures} failures across {len(failure_patterns)} agents',
                'actions': [
                    'Implement retry mechanisms with exponential backoff',
                    'Add circuit breaker patterns',
                    'Enhance error handling and recovery'
                ],
                'expected_impact': 'Increase overall success rate to 99%+'
            })
        
        # Calculate optimization score
        performance_score = max(0, 100 - len(bottlenecks) * 10)
        resource_score = max(0, 100 - len(resource_issues) * 2)
        reliability_score = max(0, 100 - sum(failure_patterns.values()) * 5)
        
        optimization_score = (performance_score + resource_score + reliability_score) / 3
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'optimization_score': optimization_score,
            'analysis_period': f'{len(recent_data)} recent metrics',
            'bottlenecks_detected': len(bottlenecks),
            'resource_issues': len(resource_issues),
            'failure_count': sum(failure_patterns.values()),
            'recommendations': recommendations,
            'detailed_analysis': {
                'bottlenecks': bottlenecks,
                'resource_issues': resource_issues[-10:],  # Last 10 issues
                'failure_patterns': dict(failure_patterns)
            },
            'next_analysis': (datetime.now(timezone.utc).timestamp() + 3600)  # 1 hour from now
        }

# Global dashboard instance
analytics_dashboard = AdvancedAnalyticsDashboard()