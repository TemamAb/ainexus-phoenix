"""
Real-Time Alert System for Trading Infrastructure
Monitors and alerts on critical events across the entire trading stack
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import websockets
from concurrent.futures import ThreadPoolExecutor

class AlertSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"

class AlertCategory(Enum):
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    RISK = "RISK"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    BUSINESS = "BUSINESS"

@dataclass
class Alert:
    id: str
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    timestamp: datetime
    source: str
    metadata: Dict
    acknowledged: bool = False
    resolved: bool = False
    
    def to_dict(self):
        return {
            **asdict(self),
            'severity': self.severity.value,
            'category': self.category.value,
            'timestamp': self.timestamp.isoformat()
        }

class AlertRule:
    def __init__(self, name: str, condition: Callable, action: Callable, 
                 cooldown_seconds: int = 300):
        self.name = name
        self.condition = condition
        self.action = action
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered = None
    
    def should_trigger(self, data: Dict) -> bool:
        if self.last_triggered and (
            datetime.now() - self.last_triggered < timedelta(seconds=self.cooldown_seconds)
        ):
            return False
        return self.condition(data)

class RealTimeAlerts:
    def __init__(self):
        self.logger = self._setup_logging()
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_rules: List[AlertRule] = []
        self.alert_handlers = []
        self.websocket_clients = set()
        
        self._setup_default_rules()
        self._setup_alert_handlers()
    
    def _setup_logging(self):
        """Setup structured logging for alerts"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        # Performance rules
        self.alert_rules.append(AlertRule(
            name="high_latency",
            condition=lambda data: data.get('latency', 0) > 1000,
            action=lambda data: self.create_alert(
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.PERFORMANCE,
                title="High Latency Detected",
                message=f"Latency spike: {data.get('latency')}ms",
                source=data.get('source', 'unknown')
            )
        ))
        
        # Risk rules
        self.alert_rules.append(AlertRule(
            name="large_drawdown",
            condition=lambda data: data.get('drawdown', 0) > 0.05,
            action=lambda data: self.create_alert(
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.RISK,
                title="Large Drawdown Detected",
                message=f"Drawdown: {data.get('drawdown')*100:.2f}%",
                source="risk_engine"
            )
        ))
        
        # Security rules
        self.alert_rules.append(AlertRule(
            name="suspicious_activity",
            condition=lambda data: data.get('suspicious_score', 0) > 0.8,
            action=lambda data: self.create_alert(
                severity=AlertSeverity.EMERGENCY,
                category=AlertCategory.SECURITY,
                title="Suspicious Activity Detected",
                message=f"Suspicious activity score: {data.get('suspicious_score')}",
                source="security_monitor"
            )
        ))
    
    def _setup_alert_handlers(self):
        """Setup alert notification handlers"""
        # Console handler
        self.alert_handlers.append(self._handle_console_alert)
        
        # WebSocket handler
        self.alert_handlers.append(self._handle_websocket_alert)
        
        # Email handler (commented out - configure in production)
        # self.alert_handlers.append(self._handle_email_alert)
    
    async def process_data(self, data: Dict):
        """Process incoming data and trigger alerts"""
        self.logger.info(f"Processing data: {data}")
        
        for rule in self.alert_rules:
            try:
                if rule.should_trigger(data):
                    self.logger.info(f"Triggering rule: {rule.name}")
                    rule.action(data)
                    rule.last_triggered = datetime.now()
            except Exception as e:
                self.logger.error(f"Error processing rule {rule.name}: {e}")
    
    def create_alert(self, severity: AlertSeverity, category: AlertCategory, 
                    title: str, message: str, source: str, metadata: Dict = None) -> Alert:
        """Create and store a new alert"""
        alert_id = f"{source}_{datetime.now().timestamp()}"
        
        alert = Alert(
            id=alert_id,
            severity=severity,
            category=category,
            title=title,
            message=message,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {}
        )
        
        self.active_alerts[alert_id] = alert
        self.logger.warning(f"Alert created: {alert.title} - {alert.message}")
        
        # Notify all handlers
        asyncio.create_task(self._notify_handlers(alert))
        
        return alert
    
    async def _notify_handlers(self, alert: Alert):
        """Notify all registered alert handlers"""
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")
    
    async def _handle_console_alert(self, alert: Alert):
        """Console alert handler"""
        print(f"🚨 ALERT [{alert.severity.value}] {alert.title}")
        print(f"   Source: {alert.source}")
        print(f"   Message: {alert.message}")
        print(f"   Time: {alert.timestamp}")
        print("---")
    
    async def _handle_websocket_alert(self, alert: Alert):
        """WebSocket alert handler"""
        if not self.websocket_clients:
            return
        
        message = json.dumps({
            'type': 'ALERT',
            'data': alert.to_dict()
        })
        
        disconnected_clients = set()
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.websocket_clients -= disconnected_clients
    
    async def _handle_email_alert(self, alert: Alert):
        """Email alert handler (for critical alerts only)"""
        if alert.severity not in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            return
        
        # This would be implemented with actual email configuration
        # For now, it's a placeholder
        self.logger.info(f"Would send email for critical alert: {alert.title}")
    
    def acknowledge_alert(self, alert_id: str, user: str = "system"):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            self.active_alerts[alert_id].metadata['acknowledged_by'] = user
            self.active_alerts[alert_id].metadata['acknowledged_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Alert {alert_id} acknowledged by {user}")
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            self.active_alerts[alert_id].metadata['resolved_at'] = datetime.now().isoformat()
            self.active_alerts[alert_id].metadata['resolution_notes'] = resolution_notes
            
            self.logger.info(f"Alert {alert_id} resolved")
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None, 
                         category: Optional[AlertCategory] = None) -> List[Alert]:
        """Get active alerts with optional filtering"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        return [a for a in alerts if not a.resolved]
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        active_alerts = self.get_active_alerts()
        
        return {
            'total_active': len(active_alerts),
            'by_severity': {
                severity.value: len([a for a in active_alerts if a.severity == severity])
                for severity in AlertSeverity
            },
            'by_category': {
                category.value: len([a for a in active_alerts if a.category == category])
                for category in AlertCategory
            },
            'acknowledged_count': len([a for a in active_alerts if a.acknowledged]),
            'critical_unacknowledged': len([
                a for a in active_alerts 
                if a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] 
                and not a.acknowledged
            ])
        }
    
    async def start_websocket_server(self, host: str = 'localhost', port: int = 8765):
        """Start WebSocket server for real-time alert updates"""
        async def alert_handler(websocket, path):
            self.websocket_clients.add(websocket)
            try:
                # Send current active alerts
                current_alerts = [alert.to_dict() for alert in self.get_active_alerts()]
                await websocket.send(json.dumps({
                    'type': 'INITIAL_ALERTS',
                    'data': current_alerts
                }))
                
                # Keep connection alive
                await websocket.wait_closed()
            finally:
                self.websocket_clients.remove(websocket)
        
        server = await websockets.serve(alert_handler, host, port)
        self.logger.info(f"Alert WebSocket server started on {host}:{port}")
        return server

# Example monitoring scenarios
class TradingMonitor:
    def __init__(self, alert_system: RealTimeAlerts):
        self.alert_system = alert_system
        self.metrics_history = []
    
    async def monitor_latency(self, component: str, latency: float):
        """Monitor component latency"""
        if latency > 500:
            await self.alert_system.process_data({
                'latency': latency,
                'source': component,
                'threshold': 500
            })
    
    async def monitor_drawdown(self, drawdown: float):
        """Monitor portfolio drawdown"""
        if drawdown > 0.03:
            await self.alert_system.process_data({
                'drawdown': drawdown,
                'source': 'portfolio_manager',
                'threshold': 0.03
            })
    
    async def monitor_suspicious_activity(self, activity_data: Dict):
        """Monitor for suspicious activity"""
        suspicious_score = self._calculate_suspicious_score(activity_data)
        if suspicious_score > 0.7:
            await self.alert_system.process_data({
                'suspicious_score': suspicious_score,
                'source': 'fraud_detection',
                'activity_data': activity_data
            })
    
    def _calculate_suspicious_score(self, data: Dict) -> float:
        """Calculate suspicious activity score"""
        # Simplified implementation
        score = 0.0
        if data.get('unusual_volume', False):
            score += 0.3
        if data.get('unusual_time', False):
            score += 0.2
        if data.get('sanctioned_counterparty', False):
            score += 0.5
        return min(score, 1.0)

# Example usage
async def main():
    # Initialize alert system
    alert_system = RealTimeAlerts()
    
    # Start WebSocket server
    await alert_system.start_websocket_server()
    
    # Initialize monitor
    monitor = TradingMonitor(alert_system)
    
    # Simulate monitoring
    print("Starting real-time monitoring simulation...")
    
    # Simulate some alert scenarios
    await monitor.monitor_latency('execution_engine', 1200)  # Should trigger alert
    await monitor.monitor_drawdown(0.06)  # Should trigger alert
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Print alert statistics
    stats = alert_system.get_alert_stats()
    print(f"Alert Stats: {stats}")
    
    # List active alerts
    active_alerts = alert_system.get_active_alerts()
    print(f"Active Alerts: {len(active_alerts)}")
    
    for alert in active_alerts:
        print(f" - {alert.title} ({alert.severity.value})")

if __name__ == "__main__":
    asyncio.run(main())