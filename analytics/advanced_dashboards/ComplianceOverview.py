"""
Advanced Compliance Dashboard for Institutional-Grade Monitoring
Real-time compliance tracking across multiple jurisdictions and protocols
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@dataclass
class ComplianceAlert:
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    category: str  # REGULATORY, RISK, SANCTIONS, TAX
    message: str
    timestamp: datetime
    wallet_address: Optional[str] = None
    protocol: Optional[str] = None

class ComplianceOverview:
    def __init__(self):
        self.compliance_rules = self._load_compliance_rules()
        self.alert_history = []
        
    def _load_compliance_rules(self) -> Dict:
        """Load compliance rules from configuration"""
        return {
            "sanctioned_countries": ["IR", "KP", "SY", "CU", "RU"],
            "transaction_limits": {
                "daily_limit": 1000000,  # $1M
                "single_tx_limit": 500000  # $500K
            },
            "kyc_requirements": {
                "min_kyc_level": 2,
                "required_documents": ["ID", "PROOF_OF_ADDRESS"]
            }
        }
    
    async def monitor_real_time_compliance(self, transaction_data: Dict) -> List[ComplianceAlert]:
        """Monitor transactions for compliance violations"""
        alerts = []
        
        # Check for sanctioned jurisdictions
        if self._is_sanctioned_jurisdiction(transaction_data):
            alerts.append(ComplianceAlert(
                severity="HIGH",
                category="SANCTIONS",
                message=f"Transaction involving sanctioned jurisdiction: {transaction_data.get('country')}",
                timestamp=datetime.now(),
                wallet_address=transaction_data.get('from_address')
            ))
        
        # Check transaction limits
        limit_alerts = self._check_transaction_limits(transaction_data)
        alerts.extend(limit_alerts)
        
        # Check KYC requirements
        kyc_alerts = self._check_kyc_compliance(transaction_data)
        alerts.extend(kyc_alerts)
        
        self.alert_history.extend(alerts)
        return alerts
    
    def _is_sanctioned_jurisdiction(self, data: Dict) -> bool:
        """Check if transaction involves sanctioned jurisdiction"""
        country = data.get('country', '').upper()
        return country in self.compliance_rules["sanctioned_countries"]
    
    def _check_transaction_limits(self, data: Dict) -> List[ComplianceAlert]:
        """Check if transaction exceeds limits"""
        alerts = []
        amount = data.get('amount_usd', 0)
        
        if amount > self.compliance_rules["transaction_limits"]["single_tx_limit"]:
            alerts.append(ComplianceAlert(
                severity="MEDIUM",
                category="RISK",
                message=f"Single transaction limit exceeded: ${amount:,.2f}",
                timestamp=datetime.now(),
                wallet_address=data.get('from_address')
            ))
        
        return alerts
    
    def _check_kyc_compliance(self, data: Dict) -> List[ComplianceAlert]:
        """Verify KYC compliance"""
        alerts = []
        kyc_level = data.get('kyc_level', 0)
        
        if kyc_level < self.compliance_rules["kyc_requirements"]["min_kyc_level"]:
            alerts.append(ComplianceAlert(
                severity="HIGH",
                category="REGULATORY",
                message=f"Insufficient KYC level: {kyc_level}",
                timestamp=datetime.now(),
                wallet_address=data.get('from_address')
            ))
        
        return alerts
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        total_alerts = len(self.alert_history)
        critical_alerts = len([a for a in self.alert_history if a.severity == "CRITICAL"])
        
        return {
            "report_timestamp": datetime.now(),
            "total_alerts": total_alerts,
            "alert_severity_breakdown": self._get_alert_breakdown(),
            "compliance_score": self._calculate_compliance_score(),
            "recent_violations": self._get_recent_violations(),
            "recommendations": self._generate_recommendations()
        }
    
    def _get_alert_breakdown(self) -> Dict:
        """Break down alerts by severity and category"""
        breakdown = {}
        for alert in self.alert_history:
            if alert.severity not in breakdown:
                breakdown[alert.severity] = {}
            if alert.category not in breakdown[alert.severity]:
                breakdown[alert.severity][alert.category] = 0
            breakdown[alert.severity][alert.category] += 1
        return breakdown
    
    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score (0-100)"""
        if not self.alert_history:
            return 100.0
        
        critical_alerts = len([a for a in self.alert_history if a.severity == "CRITICAL"])
        total_weight = len(self.alert_history) * 10
        penalty = critical_alerts * 10
        
        return max(0, 100 - (penalty / total_weight * 100))
    
    def _get_recent_violations(self) -> List[Dict]:
        """Get recent compliance violations"""
        recent_alerts = [a for a in self.alert_history 
                        if datetime.now() - a.timestamp < timedelta(hours=24)]
        return [
            {
                "severity": alert.severity,
                "category": alert.category,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat()
            }
            for alert in recent_alerts[-10:]  # Last 10 alerts
        ]
    
    def _generate_recommendations(self) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        high_risk_count = len([a for a in self.alert_history if a.severity in ["HIGH", "CRITICAL"]])
        if high_risk_count > 5:
            recommendations.append("Implement enhanced due diligence procedures")
        
        sanctions_alerts = len([a for a in self.alert_history if a.category == "SANCTIONS"])
        if sanctions_alerts > 0:
            recommendations.append("Strengthen sanctions screening protocols")
        
        return recommendations
    
    def create_compliance_dashboard(self) -> go.Figure:
        """Create interactive compliance dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Compliance Score Trend', 'Alert Severity Distribution', 
                          'Violations by Category', 'Real-time Monitoring'),
            specs=[[{"type": "indicator"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Compliance score gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=self._calculate_compliance_score(),
            title={'text': "Compliance Score"},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=1)
        
        # Alert distribution pie chart
        severity_counts = self._get_severity_counts()
        fig.add_trace(go.Pie(
            labels=list(severity_counts.keys()),
            values=list(severity_counts.values()),
            hole=0.3
        ), row=1, col=2)
        
        # Violations by category bar chart
        category_counts = self._get_category_counts()
        fig.add_trace(go.Bar(
            x=list(category_counts.keys()),
            y=list(category_counts.values())
        ), row=2, col=1)
        
        fig.update_layout(height=600, title_text="Advanced Compliance Overview")
        return fig
    
    def _get_severity_counts(self) -> Dict:
        """Count alerts by severity"""
        counts = {}
        for alert in self.alert_history:
            counts[alert.severity] = counts.get(alert.severity, 0) + 1
        return counts
    
    def _get_category_counts(self) -> Dict:
        """Count alerts by category"""
        counts = {}
        for alert in self.alert_history:
            counts[alert.category] = counts.get(alert.category, 0) + 1
        return counts

# Example usage
async def main():
    dashboard = ComplianceOverview()
    
    # Simulate monitoring
    sample_tx = {
        'from_address': '0x742d35Cc6634C0532925a3b8D...',
        'amount_usd': 600000,
        'country': 'US',
        'kyc_level': 1
    }
    
    alerts = await dashboard.monitor_real_time_compliance(sample_tx)
    report = dashboard.generate_compliance_report()
    
    print("Compliance Report:", report)
    return dashboard

if __name__ == "__main__":
    asyncio.run(main())