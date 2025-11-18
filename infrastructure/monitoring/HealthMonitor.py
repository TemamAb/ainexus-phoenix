"""
í´– AI-NEXUS HEALTH MONITOR MODULE
Real-time system health monitoring and alerting
"""

import asyncio
import psutil
import time
from datetime import datetime
import logging

class HealthMonitor:
    def __init__(self):
        self.health_metrics = {}
        self.alert_thresholds = {
            'cpu_usage': 85,
            'memory_usage': 80,
            'disk_usage': 90,
            'response_time': 2.0  # seconds
        }
        
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        while True:
            await self.collect_metrics()
            await self.check_thresholds()
            await asyncio.sleep(5)  # Check every 5 seconds
            
    async def collect_metrics(self):
        """Collect system health metrics"""
        self.health_metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'active_processes': len(psutil.pids()),
            'network_io': psutil.net_io_counters()
        }
        
    async def check_thresholds(self):
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        if self.health_metrics['cpu_percent'] > self.alert_thresholds['cpu_usage']:
            alerts.append(f"íº¨ High CPU usage: {self.health_metrics['cpu_percent']}%")
            
        if self.health_metrics['memory_percent'] > self.alert_thresholds['memory_usage']:
            alerts.append(f"íº¨ High Memory usage: {self.health_metrics['memory_percent']}%")
            
        if self.health_metrics['disk_percent'] > self.alert_thresholds['disk_usage']:
            alerts.append(f"íº¨ High Disk usage: {self.health_metrics['disk_percent']}%")
            
        # Trigger alerts
        for alert in alerts:
            await self.trigger_alert(alert)
            
    async def trigger_alert(self, message):
        """Trigger health alert"""
        print(f"HEALTH ALERT: {message}")
        # Integrate with your alerting system
        # await self.send_slack_alert(message)
        # await self.send_email_alert(message)
        
    def get_health_report(self):
        """Generate health report"""
        return {
            'status': 'healthy' if not self.has_alerts() else 'degraded',
            'metrics': self.health_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
    def has_alerts(self):
        """Check if any alerts are active"""
        return any([
            self.health_metrics['cpu_percent'] > self.alert_thresholds['cpu_usage'],
            self.health_metrics['memory_percent'] > self.alert_thresholds['memory_usage'],
            self.health_metrics['disk_percent'] > self.alert_thresholds['disk_usage']
        ])

# Singleton instance
health_monitor = HealthMonitor()

async def main():
    """Main monitoring loop"""
    monitor = HealthMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
