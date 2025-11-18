"""
AI-NEXUS LATENCY MONITOR
Real-time latency analytics and performance optimization
"""

import time
import asyncio
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from collections import deque

@dataclass
class LatencyMeasurement:
    timestamp: datetime
    endpoint: str
    operation: str
    latency_ms: float
    success: bool
    error_message: Optional[str] = None

class LatencyMonitor:
    def __init__(self, config):
        self.config = config
        self.measurements = deque(maxlen=10000)  # Keep last 10k measurements
        self.endpoint_stats = {}
        self.operation_stats = {}
        self.alert_threshold = config.get('alert_threshold_ms', 1000)
        self.logger = logging.getLogger(__name__)
        
        # Performance thresholds
        self.performance_thresholds = {
            'optimal': 100,    # ms
            'good': 500,       # ms  
            'degraded': 1000,  # ms
            'critical': 5000   # ms
        }
    
    async def measure_latency(self, endpoint: str, operation: str, 
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
        latency_ms = (end_time - start_time) * 1000
        
        measurement = LatencyMeasurement(
            timestamp=datetime.now(),
            endpoint=endpoint,
            operation=operation,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message
        )
        
        self.record_measurement(measurement)
        return measurement
    
    def record_measurement(self, measurement: LatencyMeasurement):
        """Record latency measurement and update statistics"""
        self.measurements.append(measurement)
        
        # Update endpoint statistics
        endpoint = measurement.endpoint
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                'measurements': [],
                'success_count': 0,
                'error_count': 0,
                'total_latency': 0
            }
        
        stats = self.endpoint_stats[endpoint]
        stats['measurements'].append(measurement)
        
        if measurement.success:
            stats['success_count'] += 1
            stats['total_latency'] += measurement.latency_ms
        else:
            stats['error_count'] += 1
        
        # Keep only recent measurements (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        stats['measurements'] = [
            m for m in stats['measurements'] 
            if m.timestamp > one_hour_ago
        ]
        
        # Update operation statistics
        operation = measurement.operation
        if operation not in self.operation_stats:
            self.operation_stats[operation] = {
                'measurements': [],
                'avg_latency': 0,
                'p95_latency': 0,
                'success_rate': 0
            }
        
        self.update_operation_stats(operation)
        
        # Check for alerts
        self.check_alerts(measurement)
    
    def update_operation_stats(self, operation: str):
        """Update statistics for specific operation"""
        op_measurements = [
            m for m in self.measurements 
            if m.operation == operation and m.success
        ]
        
        if not op_measurements:
            return
        
        latencies = [m.latency_ms for m in op_measurements]
        
        self.operation_stats[operation].update({
            'avg_latency': statistics.mean(latencies),
            'p95_latency': statistics.quantiles(latencies, n=20)[18],  # 95th percentile
            'success_rate': len(op_measurements) / len([
                m for m in self.measurements 
                if m.operation == operation
            ])
        })
    
    def check_alerts(self, measurement: LatencyMeasurement):
        """Check if measurement triggers any alerts"""
        # High latency alert
        if measurement.latency_ms > self.alert_threshold:
            self.trigger_alert(
                'HIGH_LATENCY',
                f"High latency detected: {measurement.latency_ms:.2f}ms "
                f"for {measurement.operation} on {measurement.endpoint}",
                measurement
            )
        
        # Success rate alert (if we have enough data)
        endpoint_stats = self.endpoint_stats.get(measurement.endpoint)
        if endpoint_stats:
            total_requests = endpoint_stats['success_count'] + endpoint_stats['error_count']
            if total_requests > 10:
                success_rate = endpoint_stats['success_count'] / total_requests
                if success_rate < 0.9:  # 90% success rate threshold
                    self.trigger_alert(
                        'LOW_SUCCESS_RATE',
                        f"Low success rate: {success_rate:.1%} "
                        f"for {measurement.endpoint}",
                        measurement
                    )
    
    def trigger_alert(self, alert_type: str, message: str, measurement: LatencyMeasurement):
        """Trigger latency alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now(),
            'measurement': measurement,
            'severity': self.determine_alert_severity(alert_type, measurement)
        }
        
        self.logger.warning(f"íº¨ LATENCY ALERT: {message}")
        
        # Here you would typically send to alerting system
        # await self.alerting_system.send_alert(alert)
    
    def determine_alert_severity(self, alert_type: str, measurement: LatencyMeasurement) -> str:
        """Determine alert severity based on impact"""
        if alert_type == 'HIGH_LATENCY':
            if measurement.latency_ms > 5000:
                return 'CRITICAL'
            elif measurement.latency_ms > 2000:
                return 'HIGH'
            else:
                return 'MEDIUM'
        
        elif alert_type == 'LOW_SUCCESS_RATE':
            return 'HIGH'
        
        return 'LOW'
    
    def get_performance_report(self, time_window_minutes: int = 60) -> Dict:
        """Generate performance report for specified time window"""
        window_start = datetime.now() - timedelta(minutes=time_window_minutes)
        
        recent_measurements = [
            m for m in self.measurements 
            if m.timestamp > window_start
        ]
        
        if not recent_measurements:
            return {'error': 'No data in specified time window'}
        
        successful_measurements = [m for m in recent_measurements if m.success]
        
        latencies = [m.latency_ms for m in successful_measurements]
        
        report = {
            'time_window_minutes': time_window_minutes,
            'total_requests': len(recent_measurements),
            'successful_requests': len(successful_measurements),
            'success_rate': len(successful_measurements) / len(recent_measurements),
            'avg_latency_ms': statistics.mean(latencies) if latencies else 0,
            'p95_latency_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0,
            'p99_latency_ms': statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else 0,
            'min_latency_ms': min(latencies) if latencies else 0,
            'max_latency_ms': max(latencies) if latencies else 0,
            'endpoint_performance': self.get_endpoint_performance(window_start),
            'operation_performance': self.get_operation_performance(window_start),
            'performance_grade': self.calculate_performance_grade(latencies)
        }
        
        return report
    
    def get_endpoint_performance(self, since: datetime) -> Dict:
        """Get performance statistics by endpoint"""
        endpoint_performance = {}
        
        for endpoint, stats in self.endpoint_stats.items():
            recent_measurements = [
                m for m in stats['measurements'] 
                if m.timestamp > since
            ]
            
            if recent_measurements:
                successful = [m for m in recent_measurements if m.success]
                latencies = [m.latency_ms for m in successful]
                
                endpoint_performance[endpoint] = {
                    'total_requests': len(recent_measurements),
                    'success_rate': len(successful) / len(recent_measurements),
                    'avg_latency_ms': statistics.mean(latencies) if latencies else 0,
                    'performance_grade': self.calculate_performance_grade(latencies)
                }
        
        return endpoint_performance
    
    def get_operation_performance(self, since: datetime) -> Dict:
        """Get performance statistics by operation"""
        operation_performance = {}
        
        for operation in set(m.operation for m in self.measurements if m.timestamp > since):
            op_measurements = [
                m for m in self.measurements 
                if m.operation == operation and m.timestamp > since
            ]
            
            if op_measurements:
                successful = [m for m in op_measurements if m.success]
                latencies = [m.latency_ms for m in successful]
                
                operation_performance[operation] = {
                    'total_requests': len(op_measurements),
                    'success_rate': len(successful) / len(op_measurements),
                    'avg_latency_ms': statistics.mean(latencies) if latencies else 0,
                    'performance_grade': self.calculate_performance_grade(latencies)
                }
        
        return operation_performance
    
    def calculate_performance_grade(self, latencies: List[float]) -> str:
        """Calculate performance grade based on latency distribution"""
        if not latencies:
            return 'UNKNOWN'
        
        avg_latency = statistics.mean(latencies)
        
        if avg_latency <= self.performance_thresholds['optimal']:
            return 'A+'
        elif avg_latency <= self.performance_thresholds['good']:
            return 'A'
        elif avg_latency <= self.performance_thresholds['degraded']:
            return 'B'
        elif avg_latency <= self.performance_thresholds['critical']:
            return 'C'
        else:
            return 'F'
    
    def get_slowest_operations(self, limit: int = 10) -> List[Dict]:
        """Get slowest operations by average latency"""
        operation_stats = []
        
        for operation, stats in self.operation_stats.items():
            if stats['avg_latency'] > 0:
                operation_stats.append({
                    'operation': operation,
                    'avg_latency_ms': stats['avg_latency'],
                    'p95_latency_ms': stats['p95_latency'],
                    'success_rate': stats['success_rate']
                })
        
        return sorted(operation_stats, key=lambda x: x['avg_latency_ms'], reverse=True)[:limit]
