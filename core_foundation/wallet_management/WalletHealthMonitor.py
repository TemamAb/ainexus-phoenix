"""
Advanced Wallet Health Monitoring System
Comprehensive monitoring of wallet health, security, and performance
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
from collections import defaultdict

class HealthStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class AlertType(Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    BALANCE = "balance"
    NETWORK = "network"
    COMPLIANCE = "compliance"

@dataclass
class HealthMetric:
    timestamp: datetime
    metric_type: str
    value: float
    threshold: float
    status: HealthStatus

@dataclass
class WalletAlert:
    alert_id: str
    wallet_address: str
    alert_type: AlertType
    severity: str
    message: str
    timestamp: datetime
    resolved: bool
    resolution_notes: Optional[str]

@dataclass
class WalletHealth:
    wallet_address: str
    overall_score: float
    overall_status: HealthStatus
    security_score: float
    performance_score: float
    balance_score: float
    network_score: float
    last_updated: datetime
    metrics: Dict[str, HealthMetric]
    active_alerts: List[WalletAlert]

class WalletHealthMonitor:
    """
    Comprehensive wallet health monitoring with real-time alerts and analytics
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.wallet_health: Dict[str, WalletHealth] = {}
        self.health_history: Dict[str, List[WalletHealth]] = {}
        self.alert_history: Dict[str, List[WalletAlert]] = {}
        self.monitoring_config = self._load_monitoring_config()
        self.alert_rules = self._load_alert_rules()
        
        self._initialize_health_tracking()
    
    def _setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _load_monitoring_config(self) -> Dict:
        """Load monitoring configuration and thresholds"""
        return {
            "security": {
                "private_key_strength": 0.8,
                "multi_sig_enabled": 0.9,
                "recent_activity": 0.7,
                "suspicious_activity": 0.3
            },
            "performance": {
                "transaction_success_rate": 0.95,
                "average_confirmation_time": 30,  # seconds
                "gas_efficiency": 0.8
            },
            "balance": {
                "minimum_balance": 0.1,  # ETH
                "optimal_balance": 1.0,  # ETH
                "balance_volatility": 0.2
            },
            "network": {
                "connectivity": 0.99,
                "latency": 100,  # ms
                "sync_status": 0.95
            }
        }
    
    def _load_alert_rules(self) -> Dict:
        """Load alert rules and thresholds"""
        return {
            "low_balance": {
                "threshold": 0.05,  # ETH
                "severity": "HIGH",
                "message": "Wallet balance below minimum threshold"
            },
            "high_risk_activity": {
                "threshold": 0.8,
                "severity": "CRITICAL",
                "message": "Suspicious high-risk activity detected"
            },
            "performance_degradation": {
                "threshold": 0.7,
                "severity": "MEDIUM",
                "message": "Wallet performance below acceptable levels"
            },
            "network_issues": {
                "threshold": 0.5,
                "severity": "MEDIUM",
                "message": "Network connectivity issues detected"
            },
            "security_breach": {
                "threshold": 0.9,
                "severity": "CRITICAL",
                "message": "Potential security breach detected"
            }
        }
    
    def _initialize_health_tracking(self):
        """Initialize health tracking structures"""
        # This would load existing wallet data in production
        pass
    
    async def register_wallet(self, wallet_address: str, 
                            initial_metrics: Dict = None) -> WalletHealth:
        """Register a wallet for health monitoring"""
        if wallet_address in self.wallet_health:
            raise ValueError(f"Wallet already registered: {wallet_address}")
        
        health = WalletHealth(
            wallet_address=wallet_address,
            overall_score=0.5,  # Default neutral score
            overall_status=HealthStatus.FAIR,
            security_score=0.5,
            performance_score=0.5,
            balance_score=0.5,
            network_score=0.5,
            last_updated=datetime.now(),
            metrics={},
            active_alerts=[]
        )
        
        self.wallet_health[wallet_address] = health
        self.health_history[wallet_address] = [health]
        self.alert_history[wallet_address] = []
        
        # Initialize with provided metrics or defaults
        if initial_metrics:
            await self.update_wallet_metrics(wallet_address, initial_metrics)
        
        self.logger.info(f"Registered wallet for health monitoring: {wallet_address}")
        
        return health
    
    async def update_wallet_metrics(self, wallet_address: str, 
                                  metrics: Dict[str, float]) -> WalletHealth:
        """Update wallet metrics and recalculate health scores"""
        if wallet_address not in self.wallet_health:
            raise ValueError(f"Wallet not registered: {wallet_address}")
        
        health = self.wallet_health[wallet_address]
        
        # Update metrics
        for metric_type, value in metrics.items():
            threshold = self._get_metric_threshold(metric_type)
            status = self._calculate_metric_status(metric_type, value, threshold)
            
            health.metrics[metric_type] = HealthMetric(
                timestamp=datetime.now(),
                metric_type=metric_type,
                value=value,
                threshold=threshold,
                status=status
            )
        
        # Recalculate health scores
        await self._recalculate_health_scores(health)
        
        # Check for alerts
        await self._check_alerts(health)
        
        # Update history
        self.health_history[wallet_address].append(health)
        
        # Keep only recent history
        if len(self.health_history[wallet_address]) > 1000:
            self.health_history[wallet_address] = self.health_history[wallet_address][-500:]
        
        health.last_updated = datetime.now()
        
        self.logger.debug(f"Updated health metrics for {wallet_address}: {health.overall_score:.2f}")
        
        return health
    
    def _get_metric_threshold(self, metric_type: str) -> float:
        """Get threshold for a specific metric type"""
        # Navigate through nested config structure
        parts = metric_type.split('_')
        category = parts[0]
        sub_metric = '_'.join(parts[1:])
        
        category_config = self.monitoring_config.get(category, {})
        return category_config.get(sub_metric, 0.5)  # Default threshold
    
    def _calculate_metric_status(self, metric_type: str, value: float, 
                               threshold: float) -> HealthStatus:
        """Calculate health status for a metric"""
        # Different metrics have different interpretation of "good" values
        if "time" in metric_type or "latency" in metric_type:
            # Lower is better
            if value <= threshold * 0.5:
                return HealthStatus.EXCELLENT
            elif value <= threshold:
                return HealthStatus.GOOD
            elif value <= threshold * 1.5:
                return HealthStatus.FAIR
            elif value <= threshold * 2:
                return HealthStatus.POOR
            else:
                return HealthStatus.CRITICAL
        else:
            # Higher is better (success rates, balances, etc.)
            if value >= threshold * 1.2:
                return HealthStatus.EXCELLENT
            elif value >= threshold:
                return HealthStatus.GOOD
            elif value >= threshold * 0.8:
                return HealthStatus.FAIR
            elif value >= threshold * 0.5:
                return HealthStatus.POOR
            else:
                return HealthStatus.CRITICAL
    
    async def _recalculate_health_scores(self, health: WalletHealth):
        """Recalculate all health scores based on current metrics"""
        # Security score
        security_metrics = {k: v for k, v in health.metrics.items() 
                          if k.startswith('security_')}
        health.security_score = self._calculate_category_score(security_metrics)
        
        # Performance score
        performance_metrics = {k: v for k, v in health.metrics.items() 
                             if k.startswith('performance_')}
        health.performance_score = self._calculate_category_score(performance_metrics)
        
        # Balance score
        balance_metrics = {k: v for k, v in health.metrics.items() 
                         if k.startswith('balance_')}
        health.balance_score = self._calculate_category_score(balance_metrics)
        
        # Network score
        network_metrics = {k: v for k, v in health.metrics.items() 
                         if k.startswith('network_')}
        health.network_score = self._calculate_category_score(network_metrics)
        
        # Overall score (weighted average)
        weights = {
            'security': 0.4,
            'performance': 0.3,
            'balance': 0.2,
            'network': 0.1
        }
        
        health.overall_score = (
            health.security_score * weights['security'] +
            health.performance_score * weights['performance'] +
            health.balance_score * weights['balance'] +
            health.network_score * weights['network']
        )
        
        # Overall status
        health.overall_status = self._calculate_overall_status(health.overall_score)
    
    def _calculate_category_score(self, metrics: Dict[str, HealthMetric]) -> float:
        """Calculate score for a category of metrics"""
        if not metrics:
            return 0.5  # Default neutral score
        
        # Convert status to numerical scores
        status_scores = {
            HealthStatus.EXCELLENT: 1.0,
            HealthStatus.GOOD: 0.8,
            HealthStatus.FAIR: 0.6,
            HealthStatus.POOR: 0.4,
            HealthStatus.CRITICAL: 0.2
        }
        
        scores = [status_scores[metric.status] for metric in metrics.values()]
        return sum(scores) / len(scores)
    
    def _calculate_overall_status(self, overall_score: float) -> HealthStatus:
        """Calculate overall health status from score"""
        if overall_score >= 0.9:
            return HealthStatus.EXCELLENT
        elif overall_score >= 0.8:
            return HealthStatus.GOOD
        elif overall_score >= 0.6:
            return HealthStatus.FAIR
        elif overall_score >= 0.4:
            return HealthStatus.POOR
        else:
            return HealthStatus.CRITICAL
    
    async def _check_alerts(self, health: WalletHealth):
        """Check for and create new alerts"""
        new_alerts = []
        
        # Check balance alerts
        balance_metric = health.metrics.get('balance_current')
        if balance_metric and balance_metric.value < self.alert_rules['low_balance']['threshold']:
            new_alerts.append(await self._create_alert(
                health.wallet_address,
                AlertType.BALANCE,
                self.alert_rules['low_balance']['severity'],
                self.alert_rules['low_balance']['message']
            ))
        
        # Check security alerts
        security_metric = health.metrics.get('security_suspicious_activity')
        if (security_metric and 
            security_metric.value > self.alert_rules['high_risk_activity']['threshold']):
            new_alerts.append(await self._create_alert(
                health.wallet_address,
                AlertType.SECURITY,
                self.alert_rules['high_risk_activity']['severity'],
                self.alert_rules['high_risk_activity']['message']
            ))
        
        # Check performance alerts
        if (health.performance_score < 
            self.alert_rules['performance_degradation']['threshold']):
            new_alerts.append(await self._create_alert(
                health.wallet_address,
                AlertType.PERFORMANCE,
                self.alert_rules['performance_degradation']['severity'],
                self.alert_rules['performance_degradation']['message']
            ))
        
        # Check network alerts
        if (health.network_score < 
            self.alert_rules['network_issues']['threshold']):
            new_alerts.append(await self._create_alert(
                health.wallet_address,
                AlertType.NETWORK,
                self.alert_rules['network_issues']['severity'],
                self.alert_rules['network_issues']['message']
            ))
        
        # Add new alerts to wallet health
        health.active_alerts.extend(new_alerts)
        self.alert_history[health.wallet_address].extend(new_alerts)
        
        # Emit alert events
        for alert in new_alerts:
            await self._emit_alert_event(alert)
    
    async def _create_alert(self, wallet_address: str, alert_type: AlertType,
                          severity: str, message: str) -> WalletAlert:
        """Create a new wallet alert"""
        alert_id = f"alert_{datetime.now().timestamp()}_{hash(wallet_address) % 10000}"
        
        alert = WalletAlert(
            alert_id=alert_id,
            wallet_address=wallet_address,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            resolved=False,
            resolution_notes=None
        )
        
        self.logger.warning(f"Alert created: {alert_type.value} - {message} for {wallet_address}")
        
        return alert
    
    async def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Resolve a wallet alert"""
        for wallet_address, alerts in self.alert_history.items():
            for alert in alerts:
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolution_notes = resolution_notes
                    
                    # Remove from active alerts
                    health = self.wallet_health.get(wallet_address)
                    if health:
                        health.active_alerts = [a for a in health.active_alerts 
                                              if a.alert_id != alert_id]
                    
                    self.logger.info(f"Alert resolved: {alert_id}")
                    await self._emit_alert_resolution(alert)
                    return
        
        raise ValueError(f"Alert not found or already resolved: {alert_id}")
    
    async def get_wallet_health_report(self, wallet_address: str) -> Dict:
        """Generate comprehensive health report for a wallet"""
        if wallet_address not in self.wallet_health:
            return {"error": "Wallet not registered for monitoring"}
        
        health = self.wallet_health[wallet_address]
        history = self.health_history.get(wallet_address, [])
        
        # Calculate trends
        trend_7d = self._calculate_health_trend(history, days=7)
        trend_24h = self._calculate_health_trend(history, hours=24)
        
        # Generate recommendations
        recommendations = await self._generate_health_recommendations(health)
        
        report = {
            "wallet_address": wallet_address,
            "current_health": {
                "overall_score": health.overall_score,
                "overall_status": health.overall_status.value,
                "security_score": health.security_score,
                "performance_score": health.performance_score,
                "balance_score": health.balance_score,
                "network_score": health.network_score,
                "last_updated": health.last_updated.isoformat()
            },
            "trends": {
                "7_day_trend": trend_7d,
                "24_hour_trend": trend_24h
            },
            "active_alerts": len(health.active_alerts),
            "critical_alerts": len([a for a in health.active_alerts 
                                  if a.severity == "CRITICAL"]),
            "metrics_overview": {
                metric_type: {
                    "value": metric.value,
                    "status": metric.status.value,
                    "threshold": metric.threshold
                }
                for metric_type, metric in health.metrics.items()
            },
            "recommendations": recommendations,
            "health_history": len(history)
        }
        
        return report
    
    def _calculate_health_trend(self, history: List[WalletHealth], 
                              **time_kwargs) -> str:
        """Calculate health trend over specified period"""
        if len(history) < 2:
            return "stable"
        
        cutoff = datetime.now() - timedelta(**time_kwargs)
        recent_scores = [h.overall_score for h in history 
                        if h.last_updated >= cutoff]
        
        if len(recent_scores) < 2:
            return "insufficient_data"
        
        old_score = recent_scores[0]
        new_score = recent_scores[-1]
        
        difference = new_score - old_score
        
        if abs(difference) < 0.05:
            return "stable"
        elif difference > 0.1:
            return "improving"
        elif difference > 0.05:
            return "slightly_improving"
        elif difference < -0.1:
            return "deteriorating"
        else:
            return "slightly_deteriorating"
    
    async def _generate_health_recommendations(self, health: WalletHealth) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        # Security recommendations
        if health.security_score < 0.7:
            recommendations.append("Review wallet security settings and consider enabling multi-signature")
        
        # Performance recommendations
        if health.performance_score < 0.7:
            recommendations.append("Optimize transaction settings and gas parameters")
        
        # Balance recommendations
        if health.balance_score < 0.6:
            balance_metric = health.metrics.get('balance_current')
            if balance_metric and balance_metric.value < 0.1:
                recommendations.append("Add funds to wallet to maintain minimum operational balance")
        
        # Network recommendations
        if health.network_score < 0.7:
            recommendations.append("Check network connectivity and node configuration")
        
        # Overall recommendations
        if health.overall_score < 0.6:
            recommendations.append("Comprehensive wallet health review recommended")
        
        if not recommendations:
            recommendations.append("Wallet health is good. Continue regular monitoring.")
        
        return recommendations
    
    async def get_system_health_summary(self) -> Dict:
        """Get overall system health summary"""
        if not self.wallet_health:
            return {"message": "No wallets being monitored"}
        
        total_wallets = len(self.wallet_health)
        health_scores = [health.overall_score for health in self.wallet_health.values()]
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_monitored_wallets": total_wallets,
            "average_health_score": sum(health_scores) / total_wallets,
            "health_distribution": {
                "excellent": len([h for h in self.wallet_health.values() 
                                if h.overall_status == HealthStatus.EXCELLENT]),
                "good": len([h for h in self.wallet_health.values() 
                           if h.overall_status == HealthStatus.GOOD]),
                "fair": len([h for h in self.wallet_health.values() 
                           if h.overall_status == HealthStatus.FAIR]),
                "poor": len([h for h in self.wallet_health.values() 
                           if h.overall_status == HealthStatus.POOR]),
                "critical": len([h for h in self.wallet_health.values() 
                               if h.overall_status == HealthStatus.CRITICAL])
            },
            "total_active_alerts": sum(len(health.active_alerts) 
                                      for health in self.wallet_health.values()),
            "critical_alerts": sum(len([a for a in health.active_alerts 
                                      if a.severity == "CRITICAL"]) 
                                  for health in self.wallet_health.values()),
            "most_common_issues": self._identify_common_issues()
        }
        
        return summary
    
    def _identify_common_issues(self) -> List[Dict]:
        """Identify most common health issues across all wallets"""
        issue_count = defaultdict(int)
        
        for health in self.wallet_health.values():
            for alert in health.active_alerts:
                issue_count[alert.alert_type.value] += 1
        
        return [{"issue": issue, "count": count} 
                for issue, count in sorted(issue_count.items(), 
                                         key=lambda x: x[1], reverse=True)[:5]]
    
    async def run_health_check(self, wallet_address: str) -> WalletHealth:
        """Run a comprehensive health check on a wallet"""
        # Simulate health check data collection
        # In production, this would gather real metrics from various sources
        
        simulated_metrics = {
            'security_private_key_strength': 0.85,
            'security_multi_sig_enabled': 0.0,  # No multi-sig
            'security_recent_activity': 0.8,
            'security_suspicious_activity': 0.1,
            'performance_transaction_success_rate': 0.92,
            'performance_average_confirmation_time': 25.0,
            'performance_gas_efficiency': 0.75,
            'balance_current': 0.3,  # ETH
            'balance_optimal': 1.0,
            'balance_volatility': 0.15,
            'network_connectivity': 0.98,
            'network_latency': 85.0,
            'network_sync_status': 0.99
        }
        
        return await self.update_wallet_metrics(wallet_address, simulated_metrics)
    
    async def _emit_alert_event(self, alert: WalletAlert):
        """Emit alert event (would integrate with event bus in production)"""
        self.logger.info(f"Alert event: {alert.alert_type.value} for {alert.wallet_address}")
    
    async def _emit_alert_resolution(self, alert: WalletAlert):
        """Emit alert resolution event"""
        self.logger.info(f"Alert resolved: {alert.alert_id}")

# Example usage
async def main():
    """Demo the wallet health monitor"""
    monitor = WalletHealthMonitor()
    
    print("❤️ Wallet Health Monitoring System")
    print("=" * 50)
    
    # Register a wallet
    wallet_health = await monitor.register_wallet("0x742d35Cc6634C0532925a3b8Dc9F1a...")
    print(f"Registered wallet: {wallet_health.wallet_address}")
    
    # Run health check
    health_after_check = await monitor.run_health_check("0x742d35Cc6634C0532925a3b8Dc9F1a...")
    print(f"Health score: {health_after_check.overall_score:.2f} ({health_after_check.overall_status.value})")
    
    # Generate health report
    report = await monitor.get_wallet_health_report("0x742d35Cc6634C0532925a3b8Dc9F1a...")
    print(f"Active alerts: {report['active_alerts']}")
    print(f"Recommendations: {report['recommendations']}")
    
    # Get system summary
    summary = await monitor.get_system_health_summary()
    print(f"System summary - Total wallets: {summary['total_monitored_wallets']}")
    print(f"Average health: {summary['average_health_score']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())