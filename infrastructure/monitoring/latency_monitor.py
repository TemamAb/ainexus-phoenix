"""
AI-NEXUS LATENCY MONITOR
Real-time latency monitoring and performance analytics
"""

import asyncio
import time
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque, defaultdict
import logging
from datetime import datetime, timedelta

@dataclass
class LatencyMeasurement:
    endpoint: str
    operation: str
    latency_ms: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

@dataclass
class LatencyAlert:
    alert_type: str
    message: str
    severity: str
    timestamp: datetime
    measurements: List[LatencyMeasurement]

class LatencyMonitor:
    def __init__(self, config):
        self.config = config
        self.measurements = deque(maxlen=10000)  # Keep last 10k measurements
        self.endpoint_stats = defaultdict(lambda: {
            'measurements': deque(maxlen=1000),
            'success_count': 0,
            'error_count': 0,
            'total_latency': 0.0
        })
        self.operation_stats = defaultdict(lambda: {
            'measurements': deque(maxlen=1000),
            'avg_latency': 0.0,
            'p95_latency': 0.0,
            'success_rate': 0.0
        })
        self.alerts = deque(maxlen=1000)
        self.alert_thresholds = config.get('alert_thresholds', {
            'high_latency_ms': 1000,
            'error_rate_percent': 10,
            'latency_spike_multiplier': 3.0
        })
        self.logger = logging.getLogger(__name__)
    
    async def measure_operation(self, endpoint: str, operation: str, 
                              coroutine_func, *args, **kwargs) -> LatencyMeasurement:
        """Measure latency of an async operation"""
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            result = await coroutine_func(*args, **kwargs)
            success = True
        except Exception as e:
            error_message = str(e)
            result = None
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        
        measurement = LatencyMeasurement(
            endpoint=endpoint,
            operation=operation,
            latency_ms=latency_ms,
            timestamp=datetime.now(),
            success=success,
            error_message=error_message
        )
        
        await self.record_measurement(measurement)
        return measurement
    
    async def record_measurement(self, measurement: LatencyMeasurement):
        """Record latency measurement and update statistics"""
        self.measurements.append(measurement)
        
        # Update endpoint statistics
        endpoint_data = self.endpoint_stats[measurement.endpoint]
        endpoint_data['measurements'].append(measurement)
        
        if measurement.success:
            endpoint_data['success_count'] += 1
            endpoint_data['total_latency'] += measurement.latency_ms
        else:
            endpoint_data['error_count'] += 1
        
        # Update operation statistics
        operation_data = self.operation_stats[measurement.operation]
        operation_data['measurements'].append(measurement)
        
        # Recalculate operation stats
        await self.update_operation_stats(measurement.operation)
        
        # Check for alerts
        await self.check_alerts(measurement)
    
    async def update_operation_stats(self, operation: str):
        """Update statistics for specific operation"""
        operation_data = self.operation_stats[operation]
        measurements = list(operation_data['measurements'])
        
        if not measurements:
            return
        
        successful_measurements = [m for m in measurements if m.success]
        
        if successful_measurements:
            latencies = [m.latency_ms for m in successful_measurements]
            operation_data['avg_latency'] = statistics.mean(latencies)
            
            if len(latencies) >= 5:
                operation_data['p95_latency'] = self.calculate_percentile(latencies, 95)
        
        total_measurements = len(measurements)
        successful_count = len(successful_measurements)
        operation_data['success_rate'] = successful_count / total_measurements if total_measurements > 0 else 0
    
    def calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value from data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    async def check_alerts(self, measurement: LatencyMeasurement):
        """Check if measurement triggers any alerts"""
        # High latency alert
        if measurement.latency_ms > self.alert_thresholds['high_latency_ms']:
            await self.trigger_alert(
                'HIGH_LATENCY',
                f"High latency detected: {measurement.latency_ms:.2f}ms "
                f"for {measurement.operation} on {measurement.endpoint}",
                'HIGH',
                [measurement]
            )
        
        # Endpoint error rate alert
        endpoint_data = self.endpoint_stats[measurement.endpoint]
        total_requests = endpoint_data['success_count'] + endpoint_data['error_count']
        
        if total_requests >= 10:  # Minimum sample size
            error_rate = (endpoint_data['error_count'] / total_requests) * 100
            if error_rate > self.alert_thresholds['error_rate_percent']:
                await self.trigger_alert(
                    'HIGH_ERROR_RATE',
                    f"High error rate: {error_rate:.1f}% for {measurement.endpoint}",
                    'MEDIUM',
                    list(endpoint_data['measurements'])[-10:]  # Last 10 measurements
                )
        
        # Latency spike alert
        await self.check_latency_spike(measurement)
    
    async def check_latency_spike(self, measurement: LatencyMeasurement):
        """Check for sudden latency spikes"""
        if not measurement.success:
            return
        
        operation_data = self.operation_stats[measurement.operation]
        recent_measurements = list(operation_data['measurements'])
        
        if len(recent_measurements) < 5:
            return
        
        # Get last 5 measurements (excluding current)
        last_5 = [m.latency_ms for m in recent_measurements[-6:-1] if m.success]
        
        if len(last_5) < 3:
            return
        
        avg_recent_latency = statistics.mean(last_5)
        spike_threshold = avg_recent_latency * self.alert_thresholds['latency_spike_multiplier']
        
        if measurement.latency_ms > spike_threshold:
            await self.trigger_alert(
                'LATENCY_SPIKE',
                f"Latency spike detected: {measurement.latency_ms:.2f}ms "
                f"(vs average {avg_recent_latency:.2f}ms) for {measurement.operation}",
                'MEDIUM',
                [measurement]
            )
    
    async def trigger_alert(self, alert_type: str, message: str, severity: str, 
                          measurements: List[LatencyMeasurement]):
        """Trigger latency alert"""
        alert = LatencyAlert(
            alert_type=alert_type,
            message=message,
            severity=severity,
            timestamp=datetime.now(),
            measurements=measurements
        )
        
        self.alerts.append(alert)
        self.logger.warning(f"íº¨ LATENCY ALERT ({severity}): {message}")
        
        # Here you would typically send to external alerting system
        # await self.send_alert_notification(alert)
    
    async def get_performance_report(self, time_window_minutes: int = 60) -> Dict:
        """Generate performance report for specified time window"""
        window_start = datetime.now() - timedelta(minutes=time_window_minutes)
        
        recent_measurements = [
            m for m in self.measurements 
            if m.timestamp > window_start
        ]
        
        if not recent_measurements:
            return {'error': 'No data in specified time window'}
        
        successful_measurements = [m for m in recent_measurements if m.success]
        
        report = {
            'time_window_minutes': time_window_minutes,
            'total_operations': len(recent_measurements),
            'successful_operations': len(successful_measurements),
            'success_rate': len(successful_measurements) / len(recent_measurements),
            'endpoint_performance': await self.get_endpoint_performance(window_start),
            'operation_performance': await self.get_operation_performance(window_start),
            'alerts_summary': self.get_alerts_summary(window_start),
            'performance_grade': self.calculate_performance_grade(successful_measurements)
        }
        
        if successful_measurements:
            latencies = [m.latency_ms for m in successful_measurements]
            report.update({
                'avg_latency_ms': statistics.mean(latencies),
                'p95_latency_ms': self.calculate_percentile(latencies, 95),
                'p99_latency_ms': self.calculate_percentile(latencies, 99),
                'min_latency_ms': min(latencies),
                'max_latency_ms': max(latencies)
            })
        
        return report
    
    async def get_endpoint_performance(self, since: datetime) -> Dict:
        """Get performance statistics by endpoint"""
        endpoint_performance = {}
        
        for endpoint, data in self.endpoint_stats.items():
            recent_measurements = [
                m for m in data['measurements'] 
                if m.timestamp > since
            ]
            
            if recent_measurements:
                successful = [m for m in recent_measurements if m.success]
                latencies = [m.latency_ms for m in successful]
                
                endpoint_performance[endpoint] = {
                    'total_requests': len(recent_measurements),
                    'success_rate': len(successful) / len(recent_measurements),
                    'avg_latency_ms': statistics.mean(latencies) if latencies else 0,
                    'performance_grade': self.calculate_endpoint_grade(successful)
                }
        
        return endpoint_performance
    
    async def get_operation_performance(self, since: datetime) -> Dict:
        """Get performance statistics by operation"""
        operation_performance = {}
        
        for operation in self.operation_stats.keys():
            recent_measurements = [
                m for m in self.measurements 
                if m.operation == operation and m.timestamp > since
            ]
            
            if recent_measurements:
                successful = [m for m in recent_measurements if m.success]
                latencies = [m.latency_ms for m in successful]
                
                operation_performance[operation] = {
                    'total_operations': len(recent_measurements),
                    'success_rate': len(successful) / len(recent_measurements),
                    'avg_latency_ms': statistics.mean(latencies) if latencies else 0,
                    'performance_grade': self.calculate_operation_grade(operation, successful)
                }
        
        return operation_performance
    
    def calculate_performance_grade(self, measurements: List[LatencyMeasurement]) -> str:
        """Calculate overall performance grade"""
        if not measurements:
            return 'F'
        
        success_rate = len(measurements) / (len(measurements) + 
                                          sum(1 for m in self.measurements 
                                              if not m.success and 
                                              m.timestamp > datetime.now() - timedelta(hours=1)))
        
        avg_latency = statistics.mean([m.latency_ms for m in measurements])
        
        if success_rate >= 0.99 and avg_latency <= 100:
            return 'A+'
        elif success_rate >= 0.95 and avg_latency <= 500:
            return 'A'
        elif success_rate >= 0.90 and avg_latency <= 1000:
            return 'B'
        elif success_rate >= 0.80:
            return 'C'
        else:
            return 'F'
    
    def calculate_endpoint_grade(self, measurements: List[LatencyMeasurement]) -> str:
        """Calculate endpoint performance grade"""
        return self.calculate_performance_grade(measurements)
    
    def calculate_operation_grade(self, operation: str, measurements: List[LatencyMeasurement]) -> str:
        """Calculate operation performance grade"""
        return self.calculate_performance_grade(measurements)
    
    def get_alerts_summary(self, since: datetime) -> Dict:
        """Get summary of recent alerts"""
        recent_alerts = [a for a in self.alerts if a.timestamp > since]
        
        alert_counts = {}
        for alert in recent_alerts:
            alert_counts[alert.alert_type] = alert_counts.get(alert.alert_type, 0) + 1
        
        return {
            'total_alerts': len(recent_alerts),
            'alert_breakdown': alert_counts,
            'latest_alert': recent_alerts[-1].message if recent_alerts else None
        }
    
    async def get_slowest_operations(self, limit: int = 10) -> List[Dict]:
        """Get slowest operations by average latency"""
        operation_stats = []
        
        for operation, data in self.operation_stats.items():
            if data['avg_latency'] > 0:
                operation_stats.append({
                    'operation': operation,
                    'avg_latency_ms': data['avg_latency'],
                    'p95_latency_ms': data['p95_latency'],
                    'success_rate': data['success_rate']
                })
        
        return sorted(operation_stats, key=lambda x: x['avg_latency_ms'], reverse=True)[:limit]
    
    async def get_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        # Analyze endpoint performance
        endpoint_performance = await self.get_endpoint_performance(
            datetime.now() - timedelta(hours=1)
        )
        
        for endpoint, stats in endpoint_performance.items():
            if stats['success_rate'] < 0.9:
                recommendations.append(
                    f"Consider replacing endpoint {endpoint} (success rate: {stats['success_rate']:.1%})"
                )
            
            if stats['avg_latency_ms'] > 1000:
                recommendations.append(
                    f"Optimize latency for endpoint {endpoint} (avg: {stats['avg_latency_ms']:.0f}ms)"
                )
        
        # Analyze operation performance
        operation_performance = await self.get_operation_performance(
            datetime.now() - timedelta(hours=1)
        )
        
        for operation, stats in operation_performance.items():
            if stats['avg_latency_ms'] > 2000:
                recommendations.append(
                    f"Investigate slow operation: {operation} (avg: {stats['avg_latency_ms']:.0f}ms)"
                )
        
        return recommendations
    
    async def continuous_monitoring(self):
        """Continuous monitoring loop"""
        while True:
            try:
                # Generate periodic report
                report = await self.get_performance_report(time_window_minutes=5)
                
                # Check for critical issues
                if report.get('success_rate', 1) < 0.8:
                    await self.trigger_alert(
                        'CRITICAL_PERFORMANCE',
                        f"Critical performance degradation detected. Success rate: {report['success_rate']:.1%}",
                        'CRITICAL',
                        []
                    )
                
                # Log performance summary
                self.logger.info(
                    f"Performance Summary - "
                    f"Success Rate: {report.get('success_rate', 0):.1%}, "
                    f"Avg Latency: {report.get('avg_latency_ms', 0):.0f}ms"
                )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Continuous monitoring error: {e}")
                await asyncio.sleep(10)
