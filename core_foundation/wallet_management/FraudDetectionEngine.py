"""
Advanced Fraud Detection Engine for Wallet Management
Real-time monitoring and detection of suspicious wallet activities
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats
import hashlib

class FraudAlertLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class FraudPattern(Enum):
    MONEY_LAUNDERING = "money_laundering"
    TUMBLER_ACTIVITY = "tumbler_activity"
    PHISHING = "phishing"
    SCAM = "scam"
    MIXER_USAGE = "mixer_usage"
    SANCTIONS_VIOLATION = "sanctions_violation"

@dataclass
class FraudAlert:
    alert_id: str
    wallet_address: str
    alert_level: FraudAlertLevel
    pattern: FraudPattern
    description: str
    timestamp: datetime
    confidence: float
    evidence: Dict
    transaction_hashes: List[str]

@dataclass
class WalletBehaviorProfile:
    wallet_address: str
    risk_score: float
    transaction_patterns: Dict
    associated_entities: Set[str]
    first_seen: datetime
    last_activity: datetime
    total_volume: float
    alert_history: List[FraudAlert]

class FraudDetectionEngine:
    """
    Advanced fraud detection using behavioral analysis, network analysis,
    and machine learning patterns
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.wallet_profiles: Dict[str, WalletBehaviorProfile] = {}
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.known_fraudulent_wallets = self._load_known_fraud_wallets()
        self.alert_history: List[FraudAlert] = []
        
        # Risk thresholds
        self.risk_thresholds = {
            FraudAlertLevel.LOW: 0.3,
            FraudAlertLevel.MEDIUM: 0.5,
            FraudAlertLevel.HIGH: 0.7,
            FraudAlertLevel.CRITICAL: 0.9
        }
    
    def _setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _load_suspicious_patterns(self) -> Dict:
        """Load known fraudulent patterns and heuristics"""
        return {
            "rapid_movement": {
                "description": "Rapid movement of funds between addresses",
                "threshold": 10,  # transactions per minute
                "weight": 0.8
            },
            "tumbler_pattern": {
                "description": "Funds moving through known mixing services",
                "known_mixers": set(),  # Would be populated with actual mixer addresses
                "weight": 0.9
            },
            "amount_rounding": {
                "description": "Suspicious round number transactions",
                "threshold": 0.95,  # similarity to round numbers
                "weight": 0.6
            },
            "time_anomaly": {
                "description": "Unusual transaction timing patterns",
                "weight": 0.7
            },
            "network_centrality": {
                "description": "High centrality in known fraudulent networks",
                "threshold": 0.8,
                "weight": 0.85
            }
        }
    
    def _load_known_fraud_wallets(self) -> Set[str]:
        """Load known fraudulent wallet addresses"""
        # In production, this would load from a database or API
        return set([
            "0x8576acc5c05d6cb89f...",  # Example known fraudulent address
            "0xfec8a60023265354d2..."
        ])
    
    async def analyze_transaction(self, transaction_data: Dict) -> List[FraudAlert]:
        """
        Analyze a single transaction for fraudulent patterns
        
        Args:
            transaction_data: Transaction data including from, to, amount, timestamp
            
        Returns:
            List of fraud alerts if any suspicious patterns detected
        """
        alerts = []
        
        # Update wallet profiles
        self._update_wallet_profiles(transaction_data)
        
        # Check for known fraudulent addresses
        known_fraud_alerts = self._check_known_fraudulent_addresses(transaction_data)
        alerts.extend(known_fraud_alerts)
        
        # Analyze transaction patterns
        pattern_alerts = await self._analyze_transaction_patterns(transaction_data)
        alerts.extend(pattern_alerts)
        
        # Behavioral analysis
        behavioral_alerts = self._analyze_behavioral_patterns(transaction_data)
        alerts.extend(behavioral_alerts)
        
        # Network analysis
        network_alerts = await self._analyze_network_patterns(transaction_data)
        alerts.extend(network_alerts)
        
        # Store alerts
        self.alert_history.extend(alerts)
        
        return alerts
    
    def _update_wallet_profiles(self, transaction_data: Dict):
        """Update wallet behavior profiles with new transaction"""
        from_address = transaction_data.get('from')
        to_address = transaction_data.get('to')
        amount = float(transaction_data.get('value', 0))
        timestamp = datetime.fromisoformat(transaction_data.get('timestamp'))
        
        # Update sender profile
        if from_address:
            if from_address not in self.wallet_profiles:
                self.wallet_profiles[from_address] = WalletBehaviorProfile(
                    wallet_address=from_address,
                    risk_score=0.5,
                    transaction_patterns={},
                    associated_entities=set(),
                    first_seen=timestamp,
                    last_activity=timestamp,
                    total_volume=0,
                    alert_history=[]
                )
            
            profile = self.wallet_profiles[from_address]
            profile.last_activity = timestamp
            profile.total_volume += amount
            profile.associated_entities.add(to_address)
        
        # Update receiver profile
        if to_address:
            if to_address not in self.wallet_profiles:
                self.wallet_profiles[to_address] = WalletBehaviorProfile(
                    wallet_address=to_address,
                    risk_score=0.5,
                    transaction_patterns={},
                    associated_entities=set(),
                    first_seen=timestamp,
                    last_activity=timestamp,
                    total_volume=0,
                    alert_history=[]
                )
            
            profile = self.wallet_profiles[to_address]
            profile.last_activity = timestamp
            profile.total_volume += amount
            profile.associated_entities.add(from_address)
    
    def _check_known_fraudulent_addresses(self, transaction_data: Dict) -> List[FraudAlert]:
        """Check if transaction involves known fraudulent addresses"""
        alerts = []
        from_address = transaction_data.get('from')
        to_address = transaction_data.get('to')
        
        if from_address in self.known_fraudulent_wallets:
            alerts.append(self._create_alert(
                wallet_address=from_address,
                alert_level=FraudAlertLevel.CRITICAL,
                pattern=FraudPattern.SANCTIONS_VIOLATION,
                description=f"Transaction from known fraudulent address: {from_address}",
                confidence=0.95,
                evidence={"known_fraudulent": True},
                transaction_hashes=[transaction_data.get('hash', '')]
            ))
        
        if to_address in self.known_fraudulent_wallets:
            alerts.append(self._create_alert(
                wallet_address=to_address,
                alert_level=FraudAlertLevel.CRITICAL,
                pattern=FraudPattern.SANCTIONS_VIOLATION,
                description=f"Transaction to known fraudulent address: {to_address}",
                confidence=0.95,
                evidence={"known_fraudulent": True},
                transaction_hashes=[transaction_data.get('hash', '')]
            ))
        
        return alerts
    
    async def _analyze_transaction_patterns(self, transaction_data: Dict) -> List[FraudAlert]:
        """Analyze transaction for suspicious patterns"""
        alerts = []
        
        # Check for rapid movement
        rapid_movement_alert = self._check_rapid_movement(transaction_data)
        if rapid_movement_alert:
            alerts.append(rapid_movement_alert)
        
        # Check for tumbler patterns
        tumbler_alert = await self._check_tumbler_patterns(transaction_data)
        if tumbler_alert:
            alerts.append(tumbler_alert)
        
        # Check amount rounding
        rounding_alert = self._check_amount_rounding(transaction_data)
        if rounding_alert:
            alerts.append(rounding_alert)
        
        return alerts
    
    def _check_rapid_movement(self, transaction_data: Dict) -> Optional[FraudAlert]:
        """Check for rapid fund movement patterns"""
        from_address = transaction_data.get('from')
        if not from_address or from_address not in self.wallet_profiles:
            return None
        
        profile = self.wallet_profiles[from_address]
        
        # Calculate transaction frequency (simplified)
        # In production, this would analyze actual transaction history
        recent_activity = self._get_recent_transaction_count(from_address, minutes=5)
        
        if recent_activity > self.suspicious_patterns["rapid_movement"]["threshold"]:
            return self._create_alert(
                wallet_address=from_address,
                alert_level=FraudAlertLevel.HIGH,
                pattern=FraudPattern.MONEY_LAUNDERING,
                description=f"Rapid fund movement detected: {recent_activity} transactions in 5 minutes",
                confidence=0.75,
                evidence={
                    "transaction_count": recent_activity,
                    "threshold": self.suspicious_patterns["rapid_movement"]["threshold"]
                },
                transaction_hashes=[transaction_data.get('hash', '')]
            )
        
        return None
    
    async def _check_tumbler_patterns(self, transaction_data: Dict) -> Optional[FraudAlert]:
        """Check for cryptocurrency tumbler/mixer patterns"""
        to_address = transaction_data.get('to')
        from_address = transaction_data.get('from')
        
        # Simplified check - in production, this would use known mixer addresses
        # and analyze transaction graph patterns
        is_suspicious_tumbler = await self._is_known_mixer(to_address)
        
        if is_suspicious_tumbler:
            return self._create_alert(
                wallet_address=from_address,
                alert_level=FraudAlertLevel.HIGH,
                pattern=FraudPattern.MIXER_USAGE,
                description=f"Transaction to suspected mixer service: {to_address}",
                confidence=0.8,
                evidence={"suspected_mixer": to_address},
                transaction_hashes=[transaction_data.get('hash', '')]
            )
        
        return None
    
    def _check_amount_rounding(self, transaction_data: Dict) -> Optional[FraudAlert]:
        """Check for suspicious amount rounding patterns"""
        amount = float(transaction_data.get('value', 0))
        
        # Check if amount is suspiciously round
        rounded_amount = round(amount, -int(np.floor(np.log10(amount))) if amount > 0 else 0
        rounding_similarity = 1 - abs(amount - rounded_amount) / amount if amount > 0 else 0
        
        if rounding_similarity > self.suspicious_patterns["amount_rounding"]["threshold"]:
            return self._create_alert(
                wallet_address=transaction_data.get('from'),
                alert_level=FraudAlertLevel.MEDIUM,
                pattern=FraudPattern.MONEY_LAUNDERING,
                description=f"Suspicious round number transaction: {amount}",
                confidence=0.6,
                evidence={
                    "amount": amount,
                    "rounding_similarity": rounding_similarity
                },
                transaction_hashes=[transaction_data.get('hash', '')]
            )
        
        return None
    
    def _analyze_behavioral_patterns(self, transaction_data: Dict) -> List[FraudAlert]:
        """Analyze behavioral patterns for anomalies"""
        alerts = []
        from_address = transaction_data.get('from')
        
        if not from_address or from_address not in self.wallet_profiles:
            return alerts
        
        profile = self.wallet_profiles[from_address]
        
        # Check for behavioral anomalies
        time_anomaly_alert = self._check_time_anomaly(transaction_data, profile)
        if time_anomaly_alert:
            alerts.append(time_anomaly_alert)
        
        # Check for sudden activity changes
        activity_alert = self._check_activity_change(transaction_data, profile)
        if activity_alert:
            alerts.append(activity_alert)
        
        return alerts
    
    def _check_time_anomaly(self, transaction_data: Dict, 
                          profile: WalletBehaviorProfile) -> Optional[FraudAlert]:
        """Check for unusual transaction timing"""
        timestamp = datetime.fromisoformat(transaction_data.get('timestamp'))
        hour = timestamp.hour
        
        # Simple check for unusual hours (2 AM - 5 AM)
        if 2 <= hour <= 5:
            return self._create_alert(
                wallet_address=profile.wallet_address,
                alert_level=FraudAlertLevel.LOW,
                pattern=FraudPattern.MONEY_LAUNDERING,
                description=f"Unusual transaction time: {hour}:00",
                confidence=0.4,
                evidence={"transaction_hour": hour},
                transaction_hashes=[transaction_data.get('hash', '')]
            )
        
        return None
    
    def _check_activity_change(self, transaction_data: Dict,
                             profile: WalletBehaviorProfile) -> Optional[FraudAlert]:
        """Check for sudden changes in wallet activity"""
        # Calculate activity change (simplified)
        recent_activity = self._get_recent_transaction_count(profile.wallet_address, hours=24)
        historical_activity = self._get_average_daily_activity(profile.wallet_address)
        
        if historical_activity > 0:
            activity_ratio = recent_activity / historical_activity
            
            if activity_ratio > 5:  # 5x increase in activity
                return self._create_alert(
                    wallet_address=profile.wallet_address,
                    alert_level=FraudAlertLevel.MEDIUM,
                    pattern=FraudPattern.MONEY_LAUNDERING,
                    description=f"Sudden activity increase: {activity_ratio:.1f}x normal",
                    confidence=0.65,
                    evidence={
                        "recent_activity": recent_activity,
                        "historical_activity": historical_activity,
                        "activity_ratio": activity_ratio
                    },
                    transaction_hashes=[transaction_data.get('hash', '')]
                )
        
        return None
    
    async def _analyze_network_patterns(self, transaction_data: Dict) -> List[FraudAlert]:
        """Analyze network patterns for fraud detection"""
        alerts = []
        from_address = transaction_data.get('from')
        
        if not from_address:
            return alerts
        
        # Check network centrality
        centrality_alert = await self._check_network_centrality(from_address)
        if centrality_alert:
            alerts.append(centrality_alert)
        
        # Check for phishing patterns
        phishing_alert = await self._check_phishing_patterns(transaction_data)
        if phishing_alert:
            alerts.append(phishing_alert)
        
        return alerts
    
    async def _check_network_centrality(self, wallet_address: str) -> Optional[FraudAlert]:
        """Check wallet's centrality in known fraudulent networks"""
        # Simplified centrality calculation
        # In production, this would use graph analysis
        profile = self.wallet_profiles.get(wallet_address)
        if not profile:
            return None
        
        # Calculate simplified risk based on connections
        connection_risk = min(1.0, len(profile.associated_entities) / 1000)
        
        if connection_risk > self.suspicious_patterns["network_centrality"]["threshold"]:
            return self._create_alert(
                wallet_address=wallet_address,
                alert_level=FraudAlertLevel.HIGH,
                pattern=FraudPattern.MONEY_LAUNDERING,
                description=f"High network centrality detected: {len(profile.associated_entities)} connections",
                confidence=connection_risk,
                evidence={
                    "connection_count": len(profile.associated_entities),
                    "centrality_score": connection_risk
                },
                transaction_hashes=[]
            )
        
        return None
    
    async def _check_phishing_patterns(self, transaction_data: Dict) -> Optional[FraudAlert]:
        """Check for phishing-related patterns"""
        # Check for small amount transactions (common in phishing)
        amount = float(transaction_data.get('value', 0))
        
        if amount < 0.001:  # Very small amount
            return self._create_alert(
                wallet_address=transaction_data.get('from'),
                alert_level=FraudAlertLevel.MEDIUM,
                pattern=FraudPattern.PHISHING,
                description="Suspicious small amount transaction, possible phishing",
                confidence=0.55,
                evidence={"amount": amount},
                transaction_hashes=[transaction_data.get('hash', '')]
            )
        
        return None
    
    def _create_alert(self, wallet_address: str, alert_level: FraudAlertLevel,
                     pattern: FraudPattern, description: str, confidence: float,
                     evidence: Dict, transaction_hashes: List[str]) -> FraudAlert:
        """Create a fraud alert object"""
        alert_id = hashlib.md5(
            f"{wallet_address}_{pattern.value}_{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        return FraudAlert(
            alert_id=alert_id,
            wallet_address=wallet_address,
            alert_level=alert_level,
            pattern=pattern,
            description=description,
            timestamp=datetime.now(),
            confidence=confidence,
            evidence=evidence,
            transaction_hashes=transaction_hashes
        )
    
    # Utility methods
    def _get_recent_transaction_count(self, wallet_address: str, 
                                    minutes: int = 5) -> int:
        """Get recent transaction count for a wallet (simplified)"""
        # In production, this would query actual transaction history
        return np.random.poisson(lam=2)  # Simplified
    
    def _get_average_daily_activity(self, wallet_address: str) -> float:
        """Get average daily transaction count (simplified)"""
        # In production, this would calculate from historical data
        return 5.0  # Simplified
    
    async def _is_known_mixer(self, address: str) -> bool:
        """Check if address is a known mixer (simplified)"""
        # In production, this would check against known mixer addresses
        return len(address) % 10 == 0  # Simplified heuristic
    
    def get_wallet_risk_score(self, wallet_address: str) -> float:
        """Get comprehensive risk score for a wallet"""
        if wallet_address not in self.wallet_profiles:
            return 0.5  # Default medium risk for unknown wallets
        
        profile = self.wallet_profiles[wallet_address]
        
        # Calculate risk score based on various factors
        risk_factors = []
        
        # Transaction volume factor
        volume_risk = min(1.0, profile.total_volume / 1e6)  # Normalize by 1M
        risk_factors.append(volume_risk * 0.3)
        
        # Connection risk
        connection_risk = min(1.0, len(profile.associated_entities) / 500)
        risk_factors.append(connection_risk * 0.4)
        
        # Alert history risk
        alert_risk = min(1.0, len(profile.alert_history) / 10)
        risk_factors.append(alert_risk * 0.3)
        
        return sum(risk_factors) / len(risk_factors)
    
    def generate_fraud_report(self, wallet_address: str) -> Dict:
        """Generate comprehensive fraud report for a wallet"""
        if wallet_address not in self.wallet_profiles:
            return {"error": "Wallet not found"}
        
        profile = self.wallet_profiles[wallet_address]
        risk_score = self.get_wallet_risk_score(wallet_address)
        
        return {
            "wallet_address": wallet_address,
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "first_seen": profile.first_seen.isoformat(),
            "last_activity": profile.last_activity.isoformat(),
            "total_volume": profile.total_volume,
            "connection_count": len(profile.associated_entities),
            "alert_count": len(profile.alert_history),
            "recent_alerts": [
                {
                    "pattern": alert.pattern.value,
                    "level": alert.alert_level.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "confidence": alert.confidence
                }
                for alert in profile.alert_history[-10:]  # Last 10 alerts
            ],
            "recommendations": self._generate_risk_recommendations(risk_score, profile)
        }
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        elif risk_score >= 0.2:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _generate_risk_recommendations(self, risk_score: float, 
                                     profile: WalletBehaviorProfile) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if risk_score > 0.7:
            recommendations.append("Consider enhanced due diligence for transactions")
            recommendations.append("Monitor wallet activity closely")
        
        if len(profile.alert_history) > 5:
            recommendations.append("Review historical alert patterns")
        
        if len(profile.associated_entities) > 100:
            recommendations.append("Analyze network connections for suspicious patterns")
        
        if not recommendations:
            recommendations.append("Continue normal monitoring")
        
        return recommendations

# Example usage
async def main():
    """Demo the fraud detection engine"""
    engine = FraudDetectionEngine()
    
    print("🕵️ Fraud Detection Engine Started")
    print("=" * 50)
    
    # Sample transaction data
    sample_transaction = {
        "hash": "0xabc123def456...",
        "from": "0x1234567890abcdef...",
        "to": "0xfedcba0987654321...",
        "value": "1000000000000000000",  # 1 ETH
        "timestamp": datetime.now().isoformat()
    }
    
    # Analyze transaction
    alerts = await engine.analyze_transaction(sample_transaction)
    
    print(f"Detected {len(alerts)} alerts")
    for alert in alerts:
        print(f"🚨 {alert.alert_level.value} Alert: {alert.description}")
        print(f"   Pattern: {alert.pattern.value}")
        print(f"   Confidence: {alert.confidence:.2f}")
    
    print("\n" + "=" * 50)
    
    # Generate wallet report
    if alerts:
        wallet_report = engine.generate_fraud_report(sample_transaction["from"])
        print(f"Wallet Risk Score: {wallet_report['risk_score']:.2f}")
        print(f"Risk Level: {wallet_report['risk_level']}")
        print(f"Recommendations: {wallet_report['recommendations']}")

if __name__ == "__main__":
    asyncio.run(main())