"""
AI-NEXUS RELAYER HEALTH MONITOR
Comprehensive health monitoring and analytics for relay networks
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from collections import defaultdict, deque
import statistics

@dataclass
class RelayerHealth:
    relayer_id: str
    chain: str
    is_healthy: bool
    response_time: float
    success_rate: float
    error_count: int
    last_check: float
    health_score: float
    performance_metrics: Dict

@dataclass
class HealthAlert:
    alert_id: str
    relayer_id: str
    chain: str
    alert_type: str
    severity: str
    message: str
    timestamp: float
    metrics: Dict

class RelayerHealthMonitor:
    def __init__(self, config):
        self.config = config
        self.health_data = defaultdict(lambda: deque(maxlen=1000))  # Keep last 1000 checks
        self.active_alerts = {}
        self.health_history = defaultdict(list)
        self.performance_thresholds = config.get('performance_thresholds', {
            'max_response_time': 5000,  # 5 seconds
            'min_success_rate': 0.9,    # 90%
            'max_error_rate': 0.1,      # 10%
            'health_score_threshold': 0.7
        })
        self.logger = logging.getLogger(__name__)
        
    async def monitor_relayer_health(self, relayer_id: str, chain: str, 
                                   check_data: Dict) -> RelayerHealth:
        """Monitor health of specific relayer"""
        health_check = await self.perform_health_check(relayer_id, chain, check_data)
        
        # Store health data
        self.health_data[relayer_id].append(health_check)
        
        # Update health history
        self.health_history[relayer_id].append(health_check)
        
        # Check for alerts
        await self.check_health_alerts(health_check)
        
        return health_check
    
    async def perform_health_check(self, relayer_id: str, chain: str, 
                                 check_data: Dict) -> RelayerHealth:
        """Perform comprehensive health check for relayer"""
        # Response time check
        response_time = await self.measure_response_time(relayer_id, chain)
        
        # Success rate calculation
        success_rate = await self.calculate_success_rate(relayer_id, chain)
        
        # Error analysis
        error_count = await self.analyze_errors(relayer_id, chain)
        
        # Overall health score
        health_score = await self.calculate_health_score(
            relayer_id, chain, response_time, success_rate, error_count
        )
        
        # Determine health status
        is_healthy = health_score >= self.performance_thresholds['health_score_threshold']
        
        health = RelayerHealth(
            relayer_id=relayer_id,
            chain=chain,
            is_healthy=is_healthy,
            response_time=response_time,
            success_rate=success_rate,
            error_count=error_count,
            last_check=time.time(),
            health_score=health_score,
            performance_metrics={
                'response_time': response_time,
                'success_rate': success_rate,
                'error_rate': error_count / (check_data.get('total_requests', 1) or 1),
                'availability': await self.calculate_availability(relayer_id),
                'throughput': await self.calculate_throughput(relayer_id, chain)
            }
        )
        
        return health
    
    async def measure_response_time(self, relayer_id: str, chain: str) -> float:
        """Measure response time for relayer"""
        # Implementation would measure actual response time
        # Placeholder with simulated data
        base_time = 100  # 100ms base
        variation = await self.get_network_variation(chain)
        return base_time * (1 + variation)
    
    async def get_network_variation(self, chain: str) -> float:
        """Get network-specific response time variation"""
        variations = {
            'ethereum': 0.1,
            'arbitrum': 0.05,
            'optimism': 0.04,
            'polygon': 0.15,
            'base': 0.06,
            'zksync': 0.08
        }
        return variations.get(chain, 0.1)
    
    async def calculate_success_rate(self, relayer_id: str, chain: str) -> float:
        """Calculate success rate for relayer"""
        recent_checks = list(self.health_data[relayer_id])[-100:]  # Last 100 checks
        
        if not recent_checks:
            return 1.0  # Default to 100% if no data
        
        successful_checks = [check for check in recent_checks if check.is_healthy]
        return len(successful_checks) / len(recent_checks)
    
    async def analyze_errors(self, relayer_id: str, chain: str) -> int:
        """Analyze error patterns for relayer"""
        recent_checks = list(self.health_data[relayer_id])[-50:]  # Last 50 checks
        
        if not recent_checks:
            return 0
        
        error_checks = [check for check in recent_checks if not check.is_healthy]
        return len(error_checks)
    
    async def calculate_health_score(self, relayer_id: str, chain: str, 
                                   response_time: float, success_rate: float, 
                                   error_count: int) -> float:
        """Calculate comprehensive health score"""
        weights = {
            'response_time': 0.3,
            'success_rate': 0.4,
            'error_rate': 0.2,
            'stability': 0.1
        }
        
        # Response time score (lower is better)
        max_response = self.performance_thresholds['max_response_time']
        response_score = max(0, 1 - (response_time / max_response))
        
        # Success rate score
        success_score = success_rate
        
        # Error rate score (lower is better)
        max_errors = 10  # Maximum acceptable errors in recent checks
        error_score = max(0, 1 - (error_count / max_errors))
        
        # Stability score (based on variance)
        stability_score = await self.calculate_stability_score(relayer_id)
        
        # Calculate weighted score
        health_score = (
            response_score * weights['response_time'] +
            success_score * weights['success_rate'] +
            error_score * weights['error_rate'] +
            stability_score * weights['stability']
        )
        
        return max(0, min(1, health_score))
    
    async def calculate_stability_score(self, relayer_id: str) -> float:
        """Calculate stability score based on health variance"""
        recent_scores = [check.health_score for check in list(self.health_data[relayer_id])[-20:]]
        
        if len(recent_scores) < 5:
            return 0.8  # Default stability score
        
        variance = statistics.variance(recent_scores) if len(recent_scores) > 1 else 0
        stability = max(0, 1 - (variance * 10))  # Normalize variance
        
        return stability
    
    async def calculate_availability(self, relayer_id: str) -> float:
        """Calculate availability percentage for relayer"""
        recent_checks = list(self.health_data[relayer_id])[-100:]  # Last 100 checks
        
        if not recent_checks:
            return 1.0
        
        available_checks = [check for check in recent_checks if check.is_healthy]
        return len(available_checks) / len(recent_checks)
    
    async def calculate_throughput(self, relayer_id: str, chain: str) -> float:
        """Calculate throughput for relayer"""
        # Implementation would measure actual throughput
        # Placeholder with chain-specific estimates
        chain_throughputs = {
            'ethereum': 100,     # transactions per second
            'arbitrum': 5000,
            'optimism': 2000,
            'polygon': 7000,
            'base': 3000,
            'zksync': 2000
        }
        return chain_throughputs.get(chain, 1000)
    
    async def check_health_alerts(self, health: RelayerHealth):
        """Check if health status triggers any alerts"""
        alerts = []
        
        # Response time alert
        if health.response_time > self.performance_thresholds['max_response_time']:
            alerts.append(await self.create_alert(
                health, 'HIGH_RESPONSE_TIME', 'MEDIUM',
                f"High response time: {health.response_time:.0f}ms"
            ))
        
        # Success rate alert
        if health.success_rate < self.performance_thresholds['min_success_rate']:
            alerts.append(await self.create_alert(
                health, 'LOW_SUCCESS_RATE', 'HIGH',
                f"Low success rate: {health.success_rate:.1%}"
            ))
        
        # Health score alert
        if health.health_score < self.performance_thresholds['health_score_threshold']:
            alerts.append(await self.create_alert(
                health, 'LOW_HEALTH_SCORE', 'HIGH',
                f"Low health score: {health.health_score:.2f}"
            ))
        
        # Error rate alert
        error_rate = health.error_count / 50  # Based on last 50 checks
        if error_rate > self.performance_thresholds['max_error_rate']:
            alerts.append(await self.create_alert(
                health, 'HIGH_ERROR_RATE', 'MEDIUM',
                f"High error rate: {error_rate:.1%}"
            ))
        
        # Process alerts
        for alert in alerts:
            await self.process_alert(alert)
    
    async def create_alert(self, health: RelayerHealth, alert_type: str, 
                          severity: str, message: str) -> HealthAlert:
        """Create health alert"""
        alert_id = f"alert_{health.relayer_id}_{alert_type}_{int(time.time())}"
        
        return HealthAlert(
            alert_id=alert_id,
            relayer_id=health.relayer_id,
            chain=health.chain,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=time.time(),
            metrics=health.performance_metrics
        )
    
    async def process_alert(self, alert: HealthAlert):
        """Process health alert"""
        alert_key = f"{alert.relayer_id}_{alert.alert_type}"
        
        # Check if similar alert is already active
        if alert_key in self.active_alerts:
            existing_alert = self.active_alerts[alert_key]
            # Update existing alert if it's the same type
            if existing_alert.alert_type == alert.alert_type:
                self.active_alerts[alert_key] = alert
                self.logger.info(f"Updated alert: {alert.message}")
                return
        
        # Store new alert
        self.active_alerts[alert_key] = alert
        
        # Log alert based on severity
        if alert.severity == 'HIGH':
            self.logger.error(f"íº¨ HIGH ALERT: {alert.message}")
        elif alert.severity == 'MEDIUM':
            self.logger.warning(f"âš ï¸ MEDIUM ALERT: {alert.message}")
        else:
            self.logger.info(f"â„¹ï¸ INFO ALERT: {alert.message}")
        
        # Here you would typically send to external alerting system
        # await self.send_alert_notification(alert)
    
    async def resolve_alert(self, relayer_id: str, alert_type: str):
        """Resolve specific alert for relayer"""
        alert_key = f"{relayer_id}_{alert_type}"
        
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            self.logger.info(f"Resolved alert: {alert.message}")
            del self.active_alerts[alert_key]
            
            # Record resolution
            await self.record_alert_resolution(alert)
    
    async def record_alert_resolution(self, alert: HealthAlert):
        """Record alert resolution for analytics"""
        resolution_record = {
            'alert_id': alert.alert_id,
            'resolved_at': time.time(),
            'duration': time.time() - alert.timestamp,
            'alert_type': alert.alert_type,
            'severity': alert.severity
        }
        
        # Store resolution in history
        self.health_history[alert.relayer_id].append(resolution_record)
    
    async def get_relayer_health_summary(self, relayer_id: str) -> Dict:
        """Get health summary for specific relayer"""
        recent_health = list(self.health_data[relayer_id])[-100:]  # Last 100 checks
        
        if not recent_health:
            return {'error': 'No health data available'}
        
        current_health = recent_health[-1] if recent_health else None
        
        summary = {
            'relayer_id': relayer_id,
            'current_health': current_health.__dict__ if current_health else None,
            'health_trend': await self.calculate_health_trend(recent_health),
            'availability_30d': await self.calculate_period_availability(recent_health, 30),
            'performance_metrics': await self.calculate_performance_metrics(recent_health),
            'active_alerts': [alert.__dict__ for alert in self.active_alerts.values() 
                             if alert.relayer_id == relayer_id]
        }
        
        return summary
    
    async def calculate_health_trend(self, health_checks: List[RelayerHealth]) -> str:
        """Calculate health trend from recent checks"""
        if len(health_checks) < 10:
            return 'insufficient_data'
        
        recent_scores = [check.health_score for check in health_checks[-10:]]
        older_scores = [check.health_score for check in health_checks[-20:-10]]
        
        if not older_scores:
            return 'stable'
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 0.1:
            return 'improving'
        elif recent_avg < older_avg - 0.1:
            return 'declining'
        else:
            return 'stable'
    
    async def calculate_period_availability(self, health_checks: List[RelayerHealth], 
                                          days: int) -> float:
        """Calculate availability for specific period"""
        # Convert days to number of checks (assuming regular checks)
        check_count = min(len(health_checks), days * 24)  # Assuming hourly checks
        
        if check_count == 0:
            return 0.0
        
        period_checks = health_checks[-check_count:]
        available_checks = [check for check in period_checks if check.is_healthy]
        
        return len(available_checks) / len(period_checks)
    
    async def calculate_performance_metrics(self, health_checks: List[RelayerHealth]) -> Dict:
        """Calculate performance metrics from health checks"""
        if not health_checks:
            return {}
        
        response_times = [check.response_time for check in health_checks]
        success_rates = [check.success_rate for check in health_checks]
        health_scores = [check.health_score for check in health_checks]
        
        return {
            'avg_response_time': sum(response_times) / len(response_times),
            'avg_success_rate': sum(success_rates) / len(success_rates),
            'avg_health_score': sum(health_scores) / len(health_scores),
            'response_time_std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0,
            'min_health_score': min(health_scores),
            'max_health_score': max(health_scores)
        }
    
    async def get_system_health_overview(self) -> Dict:
        """Get overview of system health across all relayers"""
        all_relayers = list(self.health_data.keys())
        
        if not all_relayers:
            return {'error': 'No relayer data available'}
        
        overview = {
            'total_relayers': len(all_relayers),
            'healthy_relayers': 0,
            'unhealthy_relayers': 0,
            'system_health_score': 0,
            'alerts_summary': await self.get_alerts_summary(),
            'performance_by_chain': await self.get_performance_by_chain(),
            'recommendations': await self.generate_system_recommendations()
        }
        
        total_health_score = 0
        for relayer_id in all_relayers:
            recent_health = list(self.health_data[relayer_id])
            if recent_health:
                current_health = recent_health[-1]
                if current_health.is_healthy:
                    overview['healthy_relayers'] += 1
                else:
                    overview['unhealthy_relayers'] += 1
                
                total_health_score += current_health.health_score
        
        if all_relayers:
            overview['system_health_score'] = total_health_score / len(all_relayers)
        
        return overview
    
    async def get_alerts_summary(self) -> Dict:
        """Get summary of active alerts"""
        alert_counts = {
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'TOTAL': len(self.active_alerts)
        }
        
        for alert in self.active_alerts.values():
            alert_counts[alert.severity] += 1
        
        return alert_counts
    
    async def get_performance_by_chain(self) -> Dict:
        """Get performance metrics grouped by chain"""
        chain_performance = {}
        
        for relayer_id, health_checks in self.health_data.items():
            if not health_checks:
                continue
            
            current_health = health_checks[-1]
            chain = current_health.chain
            
            if chain not in chain_performance:
                chain_performance[chain] = {
                    'relayer_count': 0,
                    'avg_health_score': 0,
                    'avg_response_time': 0,
                    'avg_success_rate': 0
                }
            
            chain_data = chain_performance[chain]
            chain_data['relayer_count'] += 1
            chain_data['avg_health_score'] += current_health.health_score
            chain_data['avg_response_time'] += current_health.response_time
            chain_data['avg_success_rate'] += current_health.success_rate
        
        # Calculate averages
        for chain, data in chain_performance.items():
            count = data['relayer_count']
            if count > 0:
                data['avg_health_score'] /= count
                data['avg_response_time'] /= count
                data['avg_success_rate'] /= count
        
        return chain_performance
    
    async def generate_system_recommendations(self) -> List[str]:
        """Generate system-wide health recommendations"""
        recommendations = []
        overview = await self.get_system_health_overview()
        
        # Health score recommendations
        system_health = overview.get('system_health_score', 0)
        if system_health < 0.8:
            recommendations.append(
                f"Improve system health score (current: {system_health:.2f})"
            )
        
        # Unhealthy relayer recommendations
        unhealthy_count = overview.get('unhealthy_relayers', 0)
        if unhealthy_count > 0:
            recommendations.append(
                f"Address {unhealthy_count} unhealthy relayers"
            )
        
        # Alert recommendations
        alerts_summary = overview.get('alerts_summary', {})
        high_alerts = alerts_summary.get('HIGH', 0)
        if high_alerts > 0:
            recommendations.append(
                f"Resolve {high_alerts} high-severity alerts"
            )
        
        # Performance recommendations
        chain_performance = overview.get('performance_by_chain', {})
        for chain, performance in chain_performance.items():
            if performance['avg_health_score'] < 0.7:
                recommendations.append(
                    f"Optimize performance for {chain} network"
                )
        
        return recommendations
    
    async def generate_health_report(self, days: int = 7) -> Dict:
        """Generate comprehensive health report"""
        system_overview = await self.get_system_health_overview()
        
        return {
            'report_timestamp': time.time(),
            'report_period_days': days,
            'system_overview': system_overview,
            'detailed_metrics': await self.get_detailed_metrics(days),
            'trend_analysis': await self.get_trend_analysis(days),
            'action_items': await self.generate_action_items()
        }
    
    async def get_detailed_metrics(self, days: int) -> Dict:
        """Get detailed metrics for report period"""
        cutoff_time = time.time() - (days * 86400)
        
        metrics = {
            'total_health_checks': 0,
            'total_alerts_triggered': 0,
            'avg_response_time': 0,
            'avg_success_rate': 0,
            'downtime_minutes': 0
        }
        
        # Implementation would aggregate metrics from storage
        # Placeholder implementation
        return metrics
    
    async def get_trend_analysis(self, days: int) -> Dict:
        """Get trend analysis for report period"""
        # Implementation would analyze trends over time
        # Placeholder implementation
        return {
            'health_trend': 'stable',
            'performance_trend': 'improving',
            'alert_frequency': 'decreasing'
        }
    
    async def generate_action_items(self) -> List[Dict]:
        """Generate actionable items from health data"""
        action_items = []
        
        # Check for relayers needing attention
        for relayer_id, health_checks in self.health_data.items():
            if not health_checks:
                continue
            
            current_health = health_checks[-1]
            
            if not current_health.is_healthy:
                action_items.append({
                    'type': 'RELAYER_RECOVERY',
                    'relayer_id': relayer_id,
                    'chain': current_health.chain,
                    'priority': 'HIGH',
                    'action': f'Recover unhealthy relayer {relayer_id}',
                    'metrics': current_health.performance_metrics
                })
            
            elif current_health.health_score < 0.8:
                action_items.append({
                    'type': 'PERFORMANCE_OPTIMIZATION',
                    'relayer_id': relayer_id,
                    'chain': current_health.chain,
                    'priority': 'MEDIUM',
                    'action': f'Optimize performance for {relayer_id}',
                    'metrics': current_health.performance_metrics
                })
        
        return sorted(action_items, key=lambda x: 0 if x['priority'] == 'HIGH' else 1)
