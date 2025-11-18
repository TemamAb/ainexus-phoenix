"""
AI-NEXUS HEALTH CHECK ENGINE
Comprehensive system health monitoring and diagnostics
"""

import asyncio
import time
import psutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import socket
import requests
from datetime import datetime, timedelta

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class ComponentType(Enum):
    API = "api"
    DATABASE = "database"
    NETWORK = "network"
    MEMORY = "memory"
    CPU = "cpu"
    STORAGE = "storage"
    EXTERNAL_SERVICE = "external_service"

@dataclass
class HealthCheckResult:
    component: str
    component_type: ComponentType
    status: HealthStatus
    metrics: Dict[str, Any]
    timestamp: datetime
    response_time: float
    error: Optional[str] = None

@dataclass
class SystemHealth:
    overall_status: HealthStatus
    components: List[HealthCheckResult]
    timestamp: datetime
    performance_score: float
    recommendations: List[str]

class HealthCheckEngine:
    """Enterprise-grade health monitoring and diagnostics engine"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.health_history = []
        self.alert_thresholds = config.get('alert_thresholds', {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'response_time': 5.0,
            'error_rate': 5.0
        })
        
        # Initialize health checkers
        self.health_checkers = {
            ComponentType.API: APIHealthChecker(),
            ComponentType.DATABASE: DatabaseHealthChecker(),
            ComponentType.NETWORK: NetworkHealthChecker(),
            ComponentType.MEMORY: MemoryHealthChecker(),
            ComponentType.CPU: CPUHealthChecker(),
            ComponentType.STORAGE: StorageHealthChecker(),
            ComponentType.EXTERNAL_SERVICE: ExternalServiceHealthChecker()
        }
    
    async def perform_health_check(self) -> SystemHealth:
        """Perform comprehensive system health check"""
        start_time = time.time()
        components = []
        
        try:
            # Check all system components
            for component_type, checker in self.health_checkers.items():
                result = await checker.check_health()
                components.append(result)
            
            # Determine overall status
            overall_status = self.determine_overall_status(components)
            
            # Calculate performance score
            performance_score = self.calculate_performance_score(components)
            
            # Generate recommendations
            recommendations = self.generate_health_recommendations(components)
            
            system_health = SystemHealth(
                overall_status=overall_status,
                components=components,
                timestamp=datetime.now(),
                performance_score=performance_score,
                recommendations=recommendations
            )
            
            # Store in history
            self.health_history.append(system_health)
            
            # Keep only last 1000 health checks
            if len(self.health_history) > 1000:
                self.health_history.pop(0)
            
            self.logger.info(f"Health check completed in {time.time() - start_time:.2f}s - Status: {overall_status.value}")
            
            return system_health
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            raise
    
    def determine_overall_status(self, components: List[HealthCheckResult]) -> HealthStatus:
        """Determine overall system health status"""
        status_priority = {
            HealthStatus.CRITICAL: 4,
            HealthStatus.UNHEALTHY: 3,
            HealthStatus.DEGRADED: 2,
            HealthStatus.HEALTHY: 1
        }
        
        # Find the worst status among components
        worst_status = HealthStatus.HEALTHY
        for component in components:
            if status_priority[component.status] > status_priority[worst_status]:
                worst_status = component.status
        
        return worst_status
    
    def calculate_performance_score(self, components: List[HealthCheckResult]) -> float:
        """Calculate overall performance score (0-100)"""
        if not components:
            return 100.0
        
        total_score = 0
        weights = {
            ComponentType.API: 0.25,
            ComponentType.DATABASE: 0.20,
            ComponentType.NETWORK: 0.15,
            ComponentType.CPU: 0.15,
            ComponentType.MEMORY: 0.15,
            ComponentType.STORAGE: 0.10
        }
        
        for component in components:
            component_score = self.calculate_component_score(component)
            weight = weights.get(component.component_type, 0.05)
            total_score += component_score * weight
        
        return min(100.0, total_score)
    
    def calculate_component_score(self, component: HealthCheckResult) -> float:
        """Calculate score for individual component"""
        base_score = 100.0
        
        # Deduct points based on status
        status_deductions = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 20,
            HealthStatus.UNHEALTHY: 50,
            HealthStatus.CRITICAL: 80
        }
        
        base_score -= status_deductions.get(component.status, 0)
        
        # Additional deductions based on metrics
        metrics = component.metrics
        if 'usage_percentage' in metrics:
            usage = metrics['usage_percentage']
            if usage > 90:
                base_score -= 30
            elif usage > 80:
                base_score -= 15
            elif usage > 70:
                base_score -= 5
        
        if 'response_time' in metrics:
            response_time = metrics['response_time']
            if response_time > 10.0:
                base_score -= 25
            elif response_time > 5.0:
                base_score -= 10
            elif response_time > 2.0:
                base_score -= 5
        
        return max(0.0, base_score)
    
    def generate_health_recommendations(self, components: List[HealthCheckResult]) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        for component in components:
            if component.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                rec = self.generate_component_recommendation(component)
                recommendations.extend(rec)
        
        # System-wide recommendations
        if len([c for c in components if c.status == HealthStatus.CRITICAL]) > 0:
            recommendations.append("CRITICAL: Immediate system intervention required")
        
        performance_score = self.calculate_performance_score(components)
        if performance_score < 70:
            recommendations.append(f"Performance optimization needed (score: {performance_score:.1f})")
        
        return recommendations
    
    def generate_component_recommendation(self, component: HealthCheckResult) -> List[str]:
        """Generate recommendations for specific component"""
        recommendations = []
        metrics = component.metrics
        
        if component.component_type == ComponentType.CPU:
            if metrics.get('usage_percentage', 0) > self.alert_thresholds['cpu_usage']:
                recommendations.append(f"High CPU usage: {metrics['usage_percentage']}% - Consider scaling or optimization")
        
        elif component.component_type == ComponentType.MEMORY:
            if metrics.get('usage_percentage', 0) > self.alert_thresholds['memory_usage']:
                recommendations.append(f"High memory usage: {metrics['usage_percentage']}% - Consider memory optimization or scaling")
        
        elif component.component_type == ComponentType.STORAGE:
            if metrics.get('usage_percentage', 0) > self.alert_thresholds['disk_usage']:
                recommendations.append(f"High disk usage: {metrics['usage_percentage']}% - Consider cleanup or storage expansion")
        
        elif component.component_type == ComponentType.API:
            if metrics.get('response_time', 0) > self.alert_thresholds['response_time']:
                recommendations.append(f"Slow API response: {metrics['response_time']:.2f}s - Investigate performance bottlenecks")
        
        return recommendations
    
    async def get_health_history(self, hours: int = 24) -> List[SystemHealth]:
        """Get health check history for specified timeframe"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [h for h in self.health_history if h.timestamp >= cutoff_time]
    
    async def get_health_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trend analysis"""
        history = await self.get_health_history(hours)
        
        if len(history) < 2:
            return {"trend": "insufficient_data", "message": "Not enough data for trend analysis"}
        
        recent_score = history[-1].performance_score
        older_score = history[0].performance_score
        
        trend = "improving" if recent_score > older_score + 5 else \
                "declining" if recent_score < older_score - 5 else "stable"
        
        return {
            "trend": trend,
            "current_score": recent_score,
            "previous_score": older_score,
            "change": recent_score - older_score,
            "timeframe_hours": hours
        }
    
    async def trigger_incident_response(self, component: str, issue: str, severity: str):
        """Trigger incident response for health issues"""
        incident = {
            "component": component,
            "issue": issue,
            "severity": severity,
            "timestamp": datetime.now(),
            "status": "triggered"
        }
        
        self.logger.warning(f"Incident triggered: {component} - {issue} (Severity: {severity})")
        
        # Implementation would integrate with incident management system
        # Placeholder for incident response actions
        await self.notify_incident_team(incident)
        await self.escalate_if_needed(incident)
    
    async def notify_incident_team(self, incident: Dict):
        """Notify incident response team"""
        # Implementation would send notifications via Slack, PagerDuty, etc.
        message = f"íº¨ INCIDENT: {incident['component']} - {incident['issue']} (Severity: {incident['severity']})"
        print(message)  # Placeholder
    
    async def escalate_if_needed(self, incident: Dict):
        """Escalate incident if needed based on severity"""
        if incident['severity'] in ['critical', 'high']:
            # Implementation would trigger escalation procedures
            self.logger.info(f"Incident escalated: {incident['component']}")

# Health Checker Implementations
class APIHealthChecker:
    async def check_health(self) -> HealthCheckResult:
        """Check API health"""
        start_time = time.time()
        
        try:
            # Check API endpoints
            response_time = await self.check_api_endpoints()
            error_rate = await self.calculate_error_rate()
            
            status = HealthStatus.HEALTHY
            if error_rate > 10:
                status = HealthStatus.CRITICAL
            elif error_rate > 5:
                status = HealthStatus.UNHEALTHY
            elif response_time > 5.0:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component="api_gateway",
                component_type=ComponentType.API,
                status=status,
                metrics={
                    "response_time": response_time,
                    "error_rate": error_rate,
                    "active_connections": await self.get_active_connections()
                },
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="api_gateway",
                component_type=ComponentType.API,
                status=HealthStatus.CRITICAL,
                metrics={},
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def check_api_endpoints(self) -> float:
        """Check API endpoint response times"""
        # Implementation would test actual API endpoints
        # Placeholder implementation
        await asyncio.sleep(0.1)
        return 0.15  # 150ms average response time
    
    async def calculate_error_rate(self) -> float:
        """Calculate API error rate"""
        # Implementation would calculate from logs or metrics
        return 1.5  # 1.5% error rate
    
    async def get_active_connections(self) -> int:
        """Get number of active API connections"""
        return 45  # Placeholder

class DatabaseHealthChecker:
    async def check_health(self) -> HealthCheckResult:
        """Check database health"""
        start_time = time.time()
        
        try:
            connection_time = await self.check_connection()
            query_performance = await self.check_query_performance()
            
            status = HealthStatus.HEALTHY
            if connection_time > 2.0:
                status = HealthStatus.CRITICAL
            elif connection_time > 1.0:
                status = HealthStatus.UNHEALTHY
            elif query_performance > 1.0:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component="database",
                component_type=ComponentType.DATABASE,
                status=status,
                metrics={
                    "connection_time": connection_time,
                    "query_performance": query_performance,
                    "active_queries": await self.get_active_queries()
                },
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="database",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.CRITICAL,
                metrics={},
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def check_connection(self) -> float:
        """Check database connection time"""
        await asyncio.sleep(0.05)
        return 0.08  # 80ms connection time
    
    async def check_query_performance(self) -> float:
        """Check database query performance"""
        await asyncio.sleep(0.02)
        return 0.15  # 150ms average query time
    
    async def get_active_queries(self) -> int:
        """Get number of active database queries"""
        return 12  # Placeholder

class NetworkHealthChecker:
    async def check_health(self) -> HealthCheckResult:
        """Check network health"""
        start_time = time.time()
        
        try:
            latency = await self.check_latency()
            packet_loss = await self.check_packet_loss()
            bandwidth = await self.check_bandwidth()
            
            status = HealthStatus.HEALTHY
            if packet_loss > 10:
                status = HealthStatus.CRITICAL
            elif packet_loss > 5:
                status = HealthStatus.UNHEALTHY
            elif latency > 100:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component="network",
                component_type=ComponentType.NETWORK,
                status=status,
                metrics={
                    "latency_ms": latency,
                    "packet_loss_percent": packet_loss,
                    "bandwidth_mbps": bandwidth
                },
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="network",
                component_type=ComponentType.NETWORK,
                status=HealthStatus.CRITICAL,
                metrics={},
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def check_latency(self) -> float:
        """Check network latency"""
        # Implementation would ping key endpoints
        return 25.5  # 25.5ms latency
    
    async def check_packet_loss(self) -> float:
        """Check packet loss percentage"""
        return 0.2  # 0.2% packet loss
    
    async def check_bandwidth(self) -> float:
        """Check available bandwidth"""
        return 950.0  # 950 Mbps

class MemoryHealthChecker:
    async def check_health(self) -> HealthCheckResult:
        """Check memory health"""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            usage_percentage = memory.percent
            status = HealthStatus.HEALTHY
            
            if usage_percentage > 95:
                status = HealthStatus.CRITICAL
            elif usage_percentage > 85:
                status = HealthStatus.UNHEALTHY
            elif usage_percentage > 75:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=status,
                metrics={
                    "usage_percentage": usage_percentage,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                    "swap_usage_percent": swap.percent
                },
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="memory",
                component_type=ComponentType.MEMORY,
                status=HealthStatus.CRITICAL,
                metrics={},
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error=str(e)
            )

class CPUHealthChecker:
    async def check_health(self) -> HealthCheckResult:
        """Check CPU health"""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            load_avg = psutil.getloadavg()
            
            status = HealthStatus.HEALTHY
            if cpu_percent > 95:
                status = HealthStatus.CRITICAL
            elif cpu_percent > 85:
                status = HealthStatus.UNHEALTHY
            elif cpu_percent > 75:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component="cpu",
                component_type=ComponentType.CPU,
                status=status,
                metrics={
                    "usage_percentage": cpu_percent,
                    "load_1min": load_avg[0],
                    "load_5min": load_avg[1],
                    "load_15min": load_avg[2],
                    "core_count": psutil.cpu_count()
                },
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="cpu",
                component_type=ComponentType.CPU,
                status=HealthStatus.CRITICAL,
                metrics={},
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error=str(e)
            )

class StorageHealthChecker:
    async def check_health(self) -> HealthCheckResult:
        """Check storage health"""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            io_counters = psutil.disk_io_counters()
            
            usage_percentage = disk.percent
            status = HealthStatus.HEALTHY
            
            if usage_percentage > 95:
                status = HealthStatus.CRITICAL
            elif usage_percentage > 90:
                status = HealthStatus.UNHEALTHY
            elif usage_percentage > 85:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component="storage",
                component_type=ComponentType.STORAGE,
                status=status,
                metrics={
                    "usage_percentage": usage_percentage,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3),
                    "read_mb_per_sec": io_counters.read_bytes / (1024**2) if io_counters else 0,
                    "write_mb_per_sec": io_counters.write_bytes / (1024**2) if io_counters else 0
                },
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="storage",
                component_type=ComponentType.STORAGE,
                status=HealthStatus.CRITICAL,
                metrics={},
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error=str(e)
            )

class ExternalServiceHealthChecker:
    async def check_health(self) -> HealthCheckResult:
        """Check external service health"""
        start_time = time.time()
        
        try:
            # Check critical external services
            services = {
                "blockchain_rpc": await self.check_blockchain_rpc(),
                "price_oracle": await self.check_price_oracle(),
                "dex_api": await self.check_dex_api()
            }
            
            # Determine overall status
            unhealthy_services = [s for s in services.values() if not s['healthy']]
            
            status = HealthStatus.HEALTHY
            if len(unhealthy_services) >= 2:
                status = HealthStatus.CRITICAL
            elif len(unhealthy_services) == 1:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component="external_services",
                component_type=ComponentType.EXTERNAL_SERVICE,
                status=status,
                metrics={
                    "services_checked": len(services),
                    "unhealthy_services": len(unhealthy_services),
                    "service_details": services
                },
                timestamp=datetime.now(),
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="external_services",
                component_type=ComponentType.EXTERNAL_SERVICE,
                status=HealthStatus.CRITICAL,
                metrics={},
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def check_blockchain_rpc(self) -> Dict:
        """Check blockchain RPC health"""
        try:
            # Implementation would check actual RPC endpoints
            await asyncio.sleep(0.1)
            return {"healthy": True, "response_time": 0.15, "chain_id": 1}
        except:
            return {"healthy": False, "error": "RPC unavailable"}
    
    async def check_price_oracle(self) -> Dict:
        """Check price oracle health"""
        try:
            await asyncio.sleep(0.05)
            return {"healthy": True, "response_time": 0.08, "sources_available": 3}
        except:
            return {"healthy": False, "error": "Oracle unavailable"}
    
    async def check_dex_api(self) -> Dict:
        """Check DEX API health"""
        try:
            await asyncio.sleep(0.07)
            return {"healthy": True, "response_time": 0.12, "dexes_available": 5}
        except:
            return {"healthy": False, "error": "DEX API unavailable"}

# Example usage
if __name__ == "__main__":
    health_engine = HealthCheckEngine({
        'alert_thresholds': {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'response_time': 5.0,
            'error_rate': 5.0
        }
    })
    
    async def example():
        # Perform health check
        health = await health_engine.perform_health_check()
        print(f"Overall Health: {health.overall_status.value}")
        print(f"Performance Score: {health.performance_score:.1f}")
        
        # Show component status
        for component in health.components:
            print(f"  {component.component}: {component.status.value}")
        
        # Show recommendations
        if health.recommendations:
            print("Recommendations:")
            for rec in health.recommendations:
                print(f"  - {rec}")
        
        # Get health trend
        trend = await health_engine.get_health_trend()
        print(f"Health Trend: {trend['trend']}")
    
    asyncio.run(example())
