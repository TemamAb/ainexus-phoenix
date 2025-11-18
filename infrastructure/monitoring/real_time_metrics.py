"""
AI-NEXUS REAL-TIME METRICS ENGINE
Enterprise-grade real-time trading metrics and performance monitoring
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict, deque
import statistics
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

class MetricType(Enum):
    TRADING = "trading"
    RISK = "risk"
    PERFORMANCE = "performance"
    LIQUIDITY = "liquidity"
    NETWORK = "network"
    SYSTEM = "system"

@dataclass
class MetricPoint:
    timestamp: float
    metric_type: MetricType
    name: str
    value: float
    tags: Dict[str, str]
    metadata: Dict[str, Any]

@dataclass
class MetricAlert:
    alert_id: str
    metric_name: str
    threshold: float
    actual_value: float
    severity: str
    message: str
    timestamp: float
    triggered_by: str

class RealTimeMetricsEngine:
    """Enterprise real-time metrics collection and analysis engine"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=10000))  # Last 10k points per metric
        self.metric_aggregates = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        
        # Performance tracking
        self.performance_cache = {}
        self.metric_processors = {}
        
        # Initialize metric processors
        self.initialize_metric_processors()
        
        # Start background tasks
        self.background_tasks = set()
        self.start_background_tasks()
    
    def initialize_metric_processors(self):
        """Initialize metric-specific processors"""
        self.metric_processors = {
            MetricType.TRADING: TradingMetricsProcessor(),
            MetricType.RISK: RiskMetricsProcessor(),
            MetricType.PERFORMANCE: PerformanceMetricsProcessor(),
            MetricType.LIQUIDITY: LiquidityMetricsProcessor(),
            MetricType.NETWORK: NetworkMetricsProcessor(),
            MetricType.SYSTEM: SystemMetricsProcessor()
        }
    
    def start_background_tasks(self):
        """Start background metric processing tasks"""
        # Aggregate calculation task
        task = asyncio.create_task(self.calculate_aggregates_loop())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        
        # Alert evaluation task
        task = asyncio.create_task(self.evaluate_alerts_loop())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        
        # Metric cleanup task
        task = asyncio.create_task(self.cleanup_old_metrics_loop())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    async def record_metric(self, metric_point: MetricPoint):
        """Record a new metric point"""
        try:
            key = f"{metric_point.metric_type.value}_{metric_point.name}"
            
            # Store metric point
            self.metrics_buffer[key].append(metric_point)
            
            # Process metric with type-specific processor
            processor = self.metric_processors.get(metric_point.metric_type)
            if processor:
                await processor.process_metric(metric_point, self.metrics_buffer[key])
            
            # Check for alerts
            await self.check_metric_alerts(metric_point)
            
            # Update performance cache
            await self.update_performance_cache(metric_point)
            
            self.logger.debug(f"Recorded metric: {key} = {metric_point.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
    
    async def check_metric_alerts(self, metric_point: MetricPoint):
        """Check if metric triggers any alerts"""
        alert_rules = self.config.get('alert_rules', {}).get(metric_point.name, [])
        
        for rule in alert_rules:
            if await self.evaluate_alert_rule(metric_point, rule):
                await self.trigger_alert(metric_point, rule)
    
    async def evaluate_alert_rule(self, metric_point: MetricPoint, rule: Dict) -> bool:
        """Evaluate if metric point triggers alert rule"""
        try:
            value = metric_point.value
            threshold = rule['threshold']
            operator = rule.get('operator', 'gt')
            
            if operator == 'gt' and value > threshold:
                return True
            elif operator == 'lt' and value < threshold:
                return True
            elif operator == 'eq' and value == threshold:
                return True
            elif operator == 'gte' and value >= threshold:
                return True
            elif operator == 'lte' and value <= threshold:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Alert rule evaluation failed: {e}")
            return False
    
    async def trigger_alert(self, metric_point: MetricPoint, rule: Dict):
        """Trigger metric alert"""
        alert_id = f"alert_{metric_point.name}_{int(time.time())}"
        
        alert = MetricAlert(
            alert_id=alert_id,
            metric_name=metric_point.name,
            threshold=rule['threshold'],
            actual_value=metric_point.value,
            severity=rule.get('severity', 'medium'),
            message=rule.get('message', f"Alert for {metric_point.name}"),
            timestamp=time.time(),
            triggered_by=metric_point.name
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Notify alert system
        await self.notify_alert(alert)
        
        self.logger.warning(f"Alert triggered: {alert.message}")
    
    async def notify_alert(self, alert: MetricAlert):
        """Notify about alert (would integrate with external systems)"""
        # Implementation would send to Slack, PagerDuty, etc.
        print(f"íº¨ ALERT [{alert.severity.upper()}]: {alert.message}")
    
    async def update_performance_cache(self, metric_point: MetricPoint):
        """Update performance cache with latest metric"""
        key = f"{metric_point.metric_type.value}_{metric_point.name}"
        
        if key not in self.performance_cache:
            self.performance_cache[key] = {
                'last_value': metric_point.value,
                'trend': 'stable',
                'volatility': 0,
                'last_updated': time.time()
            }
        else:
            cache = self.performance_cache[key]
            old_value = cache['last_value']
            
            # Update trend
            if metric_point.value > old_value * 1.1:
                cache['trend'] = 'increasing'
            elif metric_point.value < old_value * 0.9:
                cache['trend'] = 'decreasing'
            else:
                cache['trend'] = 'stable'
            
            cache['last_value'] = metric_point.value
            cache['last_updated'] = time.time()
    
    async def calculate_aggregates_loop(self):
        """Background task to calculate metric aggregates"""
        while True:
            try:
                await self.calculate_all_aggregates()
                await asyncio.sleep(60)  # Calculate every minute
            except Exception as e:
                self.logger.error(f"Aggregate calculation failed: {e}")
                await asyncio.sleep(30)
    
    async def calculate_all_aggregates(self):
        """Calculate aggregates for all metrics"""
        for key, metric_points in self.metrics_buffer.items():
            if len(metric_points) > 0:
                await self.calculate_metric_aggregates(key, list(metric_points))
    
    async def calculate_metric_aggregates(self, metric_key: str, metric_points: List[MetricPoint]):
        """Calculate aggregates for specific metric"""
        values = [mp.value for mp in metric_points]
        timestamps = [mp.timestamp for mp in metric_points]
        
        aggregates = {
            'count': len(values),
            'mean': statistics.mean(values) if values else 0,
            'median': statistics.median(values) if values else 0,
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values) if values else 0,
            'max': max(values) if values else 0,
            'latest': values[-1] if values else 0,
            'trend': await self.calculate_trend(values),
            'volatility': np.std(values) if values else 0,
            'last_calculated': time.time()
        }
        
        self.metric_aggregates[metric_key] = aggregates
    
    async def calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 5:
            return 'insufficient_data'
        
        recent = values[-5:]
        older = values[-10:-5] if len(values) >= 10 else values[:5]
        
        if not older:
            return 'stable'
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        if recent_avg > older_avg * 1.05:
            return 'increasing'
        elif recent_avg < older_avg * 0.95:
            return 'decreasing'
        else:
            return 'stable'
    
    async def evaluate_alerts_loop(self):
        """Background task to evaluate alerts"""
        while True:
            try:
                await self.evaluate_all_alerts()
                await asyncio.sleep(30)  # Evaluate every 30 seconds
            except Exception as e:
                self.logger.error(f"Alert evaluation failed: {e}")
                await asyncio.sleep(30)
    
    async def evaluate_all_alerts(self):
        """Evaluate all active alerts"""
        # Implementation would re-evaluate alert conditions
        # and auto-resolve alerts when conditions normalize
        pass
    
    async def cleanup_old_metrics_loop(self):
        """Background task to cleanup old metrics"""
        while True:
            try:
                await self.cleanup_old_metrics()
                await asyncio.sleep(3600)  # Cleanup every hour
            except Exception as e:
                self.logger.error(f"Metrics cleanup failed: {e}")
                await asyncio.sleep(1800)
    
    async def cleanup_old_metrics(self):
        """Cleanup metrics older than retention period"""
        retention_hours = self.config.get('retention_hours', 24)
        cutoff_time = time.time() - (retention_hours * 3600)
        
        for key in list(self.metrics_buffer.keys()):
            # Remove old metric points
            self.metrics_buffer[key] = deque(
                [mp for mp in self.metrics_buffer[key] if mp.timestamp > cutoff_time],
                maxlen=10000
            )
    
    async def get_metric_stats(self, metric_type: MetricType, metric_name: str, 
                             timeframe: str = '1h') -> Dict:
        """Get statistics for specific metric"""
        key = f"{metric_type.value}_{metric_name}"
        metric_points = list(self.metrics_buffer.get(key, []))
        
        if not metric_points:
            return {'error': 'No data available'}
        
        # Filter by timeframe
        timeframe_seconds = self.get_timeframe_seconds(timeframe)
        cutoff_time = time.time() - timeframe_seconds
        filtered_points = [mp for mp in metric_points if mp.timestamp > cutoff_time]
        
        if not filtered_points:
            return {'error': 'No data for specified timeframe'}
        
        values = [mp.value for mp in filtered_points]
        
        return {
            'metric_type': metric_type.value,
            'metric_name': metric_name,
            'timeframe': timeframe,
            'data_points': len(filtered_points),
            'statistics': {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'latest': values[-1],
                'trend': await self.calculate_trend(values)
            },
            'time_series': [
                {'timestamp': mp.timestamp, 'value': mp.value}
                for mp in filtered_points[-100:]  # Last 100 points
            ]
        }
    
    async def get_performance_dashboard(self) -> Dict:
        """Get comprehensive performance dashboard"""
        dashboard = {
            'timestamp': time.time(),
            'overview': await self.get_system_overview(),
            'trading_metrics': await self.get_trading_metrics_overview(),
            'risk_metrics': await self.get_risk_metrics_overview(),
            'system_health': await self.get_system_health_overview(),
            'active_alerts': len(self.active_alerts),
            'recommendations': await self.generate_dashboard_recommendations()
        }
        
        return dashboard
    
    async def get_system_overview(self) -> Dict:
        """Get system overview metrics"""
        return {
            'uptime': await self.get_system_uptime(),
            'total_metrics': sum(len(buffer) for buffer in self.metrics_buffer.values()),
            'active_alerts': len(self.active_alerts),
            'system_load': await self.get_system_load(),
            'performance_score': await self.calculate_performance_score()
        }
    
    async def get_trading_metrics_overview(self) -> Dict:
        """Get trading metrics overview"""
        trading_metrics = {}
        
        for key in self.metric_aggregates:
            if key.startswith('trading_'):
                trading_metrics[key] = self.metric_aggregates[key]
        
        return trading_metrics
    
    async def get_risk_metrics_overview(self) -> Dict:
        """Get risk metrics overview"""
        risk_metrics = {}
        
        for key in self.metric_aggregates:
            if key.startswith('risk_'):
                risk_metrics[key] = self.metric_aggregates[key]
        
        return risk_metrics
    
    async def get_system_health_overview(self) -> Dict:
        """Get system health overview"""
        return {
            'metric_processing': 'healthy',
            'alert_system': 'healthy',
            'data_storage': 'healthy',
            'api_endpoints': 'healthy'
        }
    
    async def generate_dashboard_recommendations(self) -> List[Dict]:
        """Generate dashboard recommendations"""
        recommendations = []
        
        # Check for high volatility
        volatility_alerts = [alert for alert in self.active_alerts.values() 
                           if 'volatility' in alert.metric_name.lower()]
        if volatility_alerts:
            recommendations.append({
                'type': 'HIGH_VOLATILITY',
                'priority': 'HIGH',
                'message': 'High volatility detected in trading metrics',
                'suggestion': 'Review risk parameters and consider reducing position sizes'
            })
        
        # Check system performance
        performance_score = await self.calculate_performance_score()
        if performance_score < 0.7:
            recommendations.append({
                'type': 'PERFORMANCE_DEGRADATION',
                'priority': 'MEDIUM',
                'message': f'System performance score low: {performance_score:.2f}',
                'suggestion': 'Investigate system bottlenecks and optimize resource usage'
            })
        
        return recommendations
    
    async def get_system_uptime(self) -> float:
        """Get system uptime percentage"""
        # Implementation would calculate actual uptime
        return 99.95  # Placeholder
    
    async def get_system_load(self) -> float:
        """Get current system load"""
        # Implementation would measure actual system load
        return 0.65  # Placeholder
    
    async def calculate_performance_score(self) -> float:
        """Calculate overall performance score"""
        # Implementation would calculate based on various metrics
        return 0.88  # Placeholder
    
    def get_timeframe_seconds(self, timeframe: str) -> int:
        """Convert timeframe to seconds"""
        timeframes = {
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '6h': 21600,
            '24h': 86400,
            '7d': 604800
        }
        return timeframes.get(timeframe, 3600)
    
    async def export_metrics(self, metric_type: Optional[MetricType] = None, 
                           format: str = 'json') -> str:
        """Export metrics data"""
        export_data = {}
        
        for key, metric_points in self.metrics_buffer.items():
            if metric_type and not key.startswith(metric_type.value):
                continue
            
            export_data[key] = [
                {
                    'timestamp': mp.timestamp,
                    'value': mp.value,
                    'tags': mp.tags,
                    'metadata': mp.metadata
                }
                for mp in metric_points
            ]
        
        if format == 'json':
            return json.dumps(export_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Metric Processor Classes
class TradingMetricsProcessor:
    async def process_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process trading-specific metrics"""
        if 'pnl' in metric_point.name.lower():
            await self.process_pnl_metric(metric_point, metric_history)
        elif 'volume' in metric_point.name.lower():
            await self.process_volume_metric(metric_point, metric_history)
        elif 'slippage' in metric_point.name.lower():
            await self.process_slippage_metric(metric_point, metric_history)

    async def process_pnl_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process PnL metrics"""
        # Implementation would calculate PnL-specific analytics
        pass

    async def process_volume_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process volume metrics"""
        # Implementation would calculate volume-specific analytics
        pass

    async def process_slippage_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process slippage metrics"""
        # Implementation would calculate slippage-specific analytics
        pass

class RiskMetricsProcessor:
    async def process_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process risk-specific metrics"""
        if 'exposure' in metric_point.name.lower():
            await self.process_exposure_metric(metric_point, metric_history)
        elif 'var' in metric_point.name.lower():
            await self.process_var_metric(metric_point, metric_history)
        elif 'drawdown' in metric_point.name.lower():
            await self.process_drawdown_metric(metric_point, metric_history)

    async def process_exposure_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process exposure metrics"""
        pass

    async def process_var_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process VaR metrics"""
        pass

    async def process_drawdown_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process drawdown metrics"""
        pass

class PerformanceMetricsProcessor:
    async def process_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process performance-specific metrics"""
        pass

class LiquidityMetricsProcessor:
    async def process_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process liquidity-specific metrics"""
        pass

class NetworkMetricsProcessor:
    async def process_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process network-specific metrics"""
        pass

class SystemMetricsProcessor:
    async def process_metric(self, metric_point: MetricPoint, metric_history: deque):
        """Process system-specific metrics"""
        pass

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'alert_rules': {
            'trading_pnl': [
                {
                    'threshold': -10000,
                    'operator': 'lt',
                    'severity': 'high',
                    'message': 'Significant PnL loss detected'
                }
            ],
            'risk_exposure': [
                {
                    'threshold': 0.8,
                    'operator': 'gt',
                    'severity': 'medium',
                    'message': 'High risk exposure detected'
                }
            ]
        },
        'retention_hours': 24
    }
    
    # Create metrics engine
    engine = RealTimeMetricsEngine(config)
    
    # Example metric recording
    async def example():
        # Record some metrics
        pnl_metric = MetricPoint(
            timestamp=time.time(),
            metric_type=MetricType.TRADING,
            name='pnl',
            value=1500.50,
            tags={'strategy': 'arbitrage', 'asset': 'ETH-USDC'},
            metadata={'trade_count': 15}
        )
        
        await engine.record_metric(pnl_metric)
        
        # Get metric stats
        stats = await engine.get_metric_stats(MetricType.TRADING, 'pnl', '1h')
        print(f"PnL Stats: {stats}")
        
        # Get dashboard
        dashboard = await engine.get_performance_dashboard()
        print(f"Dashboard: {dashboard}")
    
    asyncio.run(example())
