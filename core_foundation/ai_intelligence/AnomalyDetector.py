"""
AI-NEXUS v5.0 - ANOMALY DETECTOR MODULE
Advanced Multi-Modal Anomaly Detection for DeFi Markets
Real-time detection of market anomalies, manipulation attempts, and system irregularities
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import warnings
warnings.filterwarnings('ignore')

class AnomalyType(Enum):
    PRICE_MANIPULATION = "price_manipulation"
    LIQUIDITY_ANOMALY = "liquidity_anomaly"
    VOLUME_SPIKE = "volume_spike"
    GAS_ANOMALY = "gas_anomaly"
    SMART_CONTRACT_ANOMALY = "smart_contract_anomaly"
    FRONT_RUNNING = "front_running"
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    ORACLE_MANIPULATION = "oracle_manipulation"

class AnomalySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AnomalyDetection:
    detection_id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence: float
    affected_assets: List[str]
    description: str
    triggers: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class DetectionRule:
    rule_id: str
    rule_type: AnomalyType
    parameters: Dict[str, float]
    conditions: List[str]
    severity_mapping: Dict[str, AnomalySeverity]
    enabled: bool

class AnomalyDetector:
    """
    Advanced multi-modal anomaly detection system
    Combines statistical, machine learning, and rule-based detection methods
    """
    
    def __init__(self):
        self.detection_history = deque(maxlen=10000)
        self.active_rules = {}
        self.model_registry = {}
        
        # Detection parameters
        self.detection_params = {
            'price_deviation_threshold': 3.0,  # Standard deviations
            'volume_spike_threshold': 5.0,
            'liquidity_change_threshold': 0.3,  # 30% change
            'gas_price_spike_threshold': 4.0,
            'min_confidence': 0.7,
            'lookback_window': timedelta(hours=24)
        }
        
        # Statistical models
        self.statistical_models = {}
        self.ml_models = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_detections': 0,
            'true_positives': 0,
            'false_positives': 0,
            'precision': 1.0,
            'recall': 1.0
        }
        
        # Initialize detection rules
        self._initialize_detection_rules()
        self._initialize_models()
    
    def _initialize_detection_rules(self):
        """Initialize anomaly detection rules"""
        
        self.active_rules = {
            AnomalyType.PRICE_MANIPULATION: DetectionRule(
                rule_id="price_manip_v1",
                rule_type=AnomalyType.PRICE_MANIPULATION,
                parameters={
                    'z_score_threshold': 3.5,
                    'volume_confirmation': 0.8,
                    'reversion_probability': 0.6
                },
                conditions=[
                    "price_deviation > 3.5σ",
                    "low volume confirmation",
                    "rapid price reversion"
                ],
                severity_mapping={
                    '3.5-4.0σ': AnomalySeverity.MEDIUM,
                    '4.0-5.0σ': AnomalySeverity.HIGH,
                    '>5.0σ': AnomalySeverity.CRITICAL
                },
                enabled=True
            ),
            
            AnomalyType.LIQUIDITY_ANOMALY: DetectionRule(
                rule_id="liquidity_anom_v1",
                rule_type=AnomalyType.LIQUIDITY_ANOMALY,
                parameters={
                    'liquidity_change_threshold': 0.4,
                    'recovery_time_threshold': 300,  # seconds
                    'impact_score_threshold': 0.7
                },
                conditions=[
                    "liquidity change > 40%",
                    "slow recovery time",
                    "high market impact"
                ],
                severity_mapping={
                    '20-40%': AnomalySeverity.LOW,
                    '40-60%': AnomalySeverity.MEDIUM,
                    '60-80%': AnomalySeverity.HIGH,
                    '>80%': AnomalySeverity.CRITICAL
                },
                enabled=True
            ),
            
            AnomalyType.VOLUME_SPIKE: DetectionRule(
                rule_id="volume_spike_v1",
                rule_type=AnomalyType.VOLUME_SPIKE,
                parameters={
                    'volume_z_threshold': 4.0,
                    'price_correlation_threshold': -0.5,
                    'duration_threshold': 60  # seconds
                },
                conditions=[
                    "volume spike > 4.0σ",
                    "negative price correlation",
                    "short duration"
                ],
                severity_mapping={
                    '4.0-5.0σ': AnomalySeverity.MEDIUM,
                    '5.0-6.0σ': AnomalySeverity.HIGH,
                    '>6.0σ': AnomalySeverity.CRITICAL
                },
                enabled=True
            ),
            
            AnomalyType.FRONT_RUNNING: DetectionRule(
                rule_id="front_run_v1",
                rule_type=AnomalyType.FRONT_RUNNING,
                parameters={
                    'time_gap_threshold': 3,  # seconds
                    'price_impact_threshold': 0.02,
                    'similarity_threshold': 0.9
                },
                conditions=[
                    "transaction time gap < 3s",
                    "significant price impact",
                    "high transaction similarity"
                ],
                severity_mapping={
                    '1-2s': AnomalySeverity.HIGH,
                    '<1s': AnomalySeverity.CRITICAL
                },
                enabled=True
            )
        }
    
    def _initialize_models(self):
        """Initialize statistical and ML models"""
        
        # Statistical models for different asset classes
        self.statistical_models = {
            'price_volatility': self._initialize_volatility_model(),
            'volume_patterns': self._initialize_volume_model(),
            'liquidity_flow': self._initialize_liquidity_model(),
            'gas_patterns': self._initialize_gas_model()
        }
        
        # Placeholder for ML models (would be trained on historical data)
        self.ml_models = {
            'ensemble_anomaly': None,  # Would be a trained ensemble model
            'temporal_anomaly': None,  # LSTM/Transformer for time series
            'graph_anomaly': None      # Graph neural networks for transaction patterns
        }
    
    def _initialize_volatility_model(self) -> Dict[str, Any]:
        """Initialize volatility statistical model"""
        return {
            'model_type': 'garch',
            'parameters': {'p': 1, 'q': 1},
            'training_data': deque(maxlen=10000),
            'last_update': datetime.now()
        }
    
    def _initialize_volume_model(self) -> Dict[str, Any]:
        """Initialize volume pattern model"""
        return {
            'model_type': 'seasonal_decomposition',
            'parameters': {'seasonal_period': 24},
            'training_data': deque(maxlen=10000),
            'last_update': datetime.now()
        }
    
    def _initialize_liquidity_model(self) -> Dict[str, Any]:
        """Initialize liquidity flow model"""
        return {
            'model_type': 'regime_switching',
            'parameters': {'n_regimes': 3},
            'training_data': deque(maxlen=5000),
            'last_update': datetime.now()
        }
    
    def _initialize_gas_model(self) -> Dict[str, Any]:
        """Initialize gas price pattern model"""
        return {
            'model_type': 'outlier_detection',
            'parameters': {'contamination': 0.1},
            'training_data': deque(maxlen=10000),
            'last_update': datetime.now()
        }
    
    async def detect_anomalies(self, market_data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Main anomaly detection method"""
        
        detections = []
        
        # Price manipulation detection
        price_anomalies = await self._detect_price_anomalies(market_data)
        detections.extend(price_anomalies)
        
        # Liquidity anomaly detection
        liquidity_anomalies = await self._detect_liquidity_anomalies(market_data)
        detections.extend(liquidity_anomalies)
        
        # Volume spike detection
        volume_anomalies = await self._detect_volume_anomalies(market_data)
        detections.extend(volume_anomalies)
        
        # Gas anomaly detection
        gas_anomalies = await self._detect_gas_anomalies(market_data)
        detections.extend(gas_anomalies)
        
        # Front-running detection
        frontrunning_anomalies = await self._detect_frontrunning(market_data)
        detections.extend(frontrunning_anomalies)
        
        # Update detection history
        for detection in detections:
            self.detection_history.append(detection)
            self.performance_metrics['total_detections'] += 1
        
        return detections
    
    async def _detect_price_anomalies(self, market_data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect price manipulation and anomalies"""
        
        detections = []
        rule = self.active_rules[AnomalyType.PRICE_MANIPULATION]
        
        if not rule.enabled:
            return detections
        
        for asset, data in market_data.get('price_data', {}).items():
            try:
                # Calculate price statistics
                current_price = data['current_price']
                price_history = data.get('price_history', [])
                
                if len(price_history) < 10:
                    continue
                
                # Calculate z-score for current price
                prices = np.array(price_history)
                mean_price = np.mean(prices)
                std_price = np.std(prices)
                
                if std_price == 0:
                    continue
                
                z_score = abs(current_price - mean_price) / std_price
                
                # Check volume confirmation
                volume_data = market_data.get('volume_data', {}).get(asset, {})
                volume_z = self._calculate_volume_z_score(volume_data)
                
                # Calculate reversion probability
                reversion_prob = self._calculate_reversion_probability(
                    current_price, mean_price, std_price
                )
                
                # Apply detection rule
                if (z_score > rule.parameters['z_score_threshold'] and
                    volume_z < rule.parameters['volume_confirmation'] and
                    reversion_prob > rule.parameters['reversion_probability']):
                    
                    # Determine severity
                    severity = self._map_price_severity(z_score, rule)
                    confidence = min(0.95, z_score / 8.0)  # Scale confidence
                    
                    detection = AnomalyDetection(
                        detection_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        timestamp=datetime.now(),
                        anomaly_type=AnomalyType.PRICE_MANIPULATION,
                        severity=severity,
                        confidence=confidence,
                        affected_assets=[asset],
                        description=f"Price manipulation detected for {asset} (z-score: {z_score:.2f})",
                        triggers={
                            'z_score': z_score,
                            'volume_z_score': volume_z,
                            'reversion_probability': reversion_prob,
                            'price_deviation': (current_price - mean_price) / mean_price
                        },
                        metadata={
                            'current_price': current_price,
                            'mean_price': mean_price,
                            'std_price': std_price,
                            'rule_applied': rule.rule_id
                        }
                    )
                    
                    detections.append(detection)
                    print(f"Price anomaly detected for {asset}: z-score {z_score:.2f}")
            
            except Exception as e:
                print(f"Error in price anomaly detection for {asset}: {e}")
                continue
        
        return detections
    
    async def _detect_liquidity_anomalies(self, market_data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect liquidity anomalies and sudden changes"""
        
        detections = []
        rule = self.active_rules[AnomalyType.LIQUIDITY_ANOMALY]
        
        if not rule.enabled:
            return detections
        
        liquidity_data = market_data.get('liquidity_data', {})
        
        for pool_id, pool_data in liquidity_data.items():
            try:
                current_liquidity = pool_data['current_liquidity']
                liquidity_history = pool_data.get('liquidity_history', [])
                
                if len(liquidity_history) < 5:
                    continue
                
                # Calculate liquidity change
                avg_liquidity = np.mean(liquidity_history)
                liquidity_change = abs(current_liquidity - avg_liquidity) / avg_liquidity
                
                # Check recovery time (simplified)
                recovery_time = pool_data.get('recovery_time', 600)  # seconds
                
                # Calculate market impact
                impact_score = self._calculate_liquidity_impact(pool_data)
                
                # Apply detection rule
                if (liquidity_change > rule.parameters['liquidity_change_threshold'] and
                    recovery_time > rule.parameters['recovery_time_threshold'] and
                    impact_score > rule.parameters['impact_score_threshold']):
                    
                    # Determine severity
                    severity = self._map_liquidity_severity(liquidity_change, rule)
                    confidence = min(0.95, liquidity_change / 2.0)  # Scale confidence
                    
                    detection = AnomalyDetection(
                        detection_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        timestamp=datetime.now(),
                        anomaly_type=AnomalyType.LIQUIDITY_ANOMALY,
                        severity=severity,
                        confidence=confidence,
                        affected_assets=pool_data.get('assets', ['unknown']),
                        description=f"Liquidity anomaly detected for pool {pool_id} (change: {liquidity_change:.1%})",
                        triggers={
                            'liquidity_change': liquidity_change,
                            'recovery_time': recovery_time,
                            'impact_score': impact_score
                        },
                        metadata={
                            'pool_id': pool_id,
                            'current_liquidity': current_liquidity,
                            'average_liquidity': avg_liquidity,
                            'rule_applied': rule.rule_id
                        }
                    )
                    
                    detections.append(detection)
                    print(f"Liquidity anomaly detected for pool {pool_id}: change {liquidity_change:.1%}")
            
            except Exception as e:
                print(f"Error in liquidity anomaly detection for pool {pool_id}: {e}")
                continue
        
        return detections
    
    async def _detect_volume_anomalies(self, market_data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect unusual volume spikes and patterns"""
        
        detections = []
        rule = self.active_rules[AnomalyType.VOLUME_SPIKE]
        
        if not rule.enabled:
            return detections
        
        volume_data = market_data.get('volume_data', {})
        
        for asset, data in volume_data.items():
            try:
                current_volume = data['current_volume']
                volume_history = data.get('volume_history', [])
                
                if len(volume_history) < 20:
                    continue
                
                # Calculate volume z-score
                volumes = np.array(volume_history)
                mean_volume = np.mean(volumes)
                std_volume = np.std(volumes)
                
                if std_volume == 0:
                    continue
                
                volume_z = (current_volume - mean_volume) / std_volume
                
                # Calculate price correlation
                price_correlation = data.get('price_correlation', 0)
                
                # Get spike duration
                spike_duration = data.get('spike_duration', 30)  # seconds
                
                # Apply detection rule
                if (volume_z > rule.parameters['volume_z_threshold'] and
                    price_correlation < rule.parameters['price_correlation_threshold'] and
                    spike_duration < rule.parameters['duration_threshold']):
                    
                    # Determine severity
                    severity = self._map_volume_severity(volume_z, rule)
                    confidence = min(0.95, volume_z / 10.0)  # Scale confidence
                    
                    detection = AnomalyDetection(
                        detection_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        timestamp=datetime.now(),
                        anomaly_type=AnomalyType.VOLUME_SPIKE,
                        severity=severity,
                        confidence=confidence,
                        affected_assets=[asset],
                        description=f"Volume spike detected for {asset} (z-score: {volume_z:.2f})",
                        triggers={
                            'volume_z_score': volume_z,
                            'price_correlation': price_correlation,
                            'spike_duration': spike_duration
                        },
                        metadata={
                            'current_volume': current_volume,
                            'mean_volume': mean_volume,
                            'std_volume': std_volume,
                            'rule_applied': rule.rule_id
                        }
                    )
                    
                    detections.append(detection)
                    print(f"Volume anomaly detected for {asset}: z-score {volume_z:.2f}")
            
            except Exception as e:
                print(f"Error in volume anomaly detection for {asset}: {e}")
                continue
        
        return detections
    
    async def _detect_gas_anomalies(self, market_data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect gas price anomalies and network congestion"""
        
        detections = []
        
        gas_data = market_data.get('gas_data', {})
        if not gas_data:
            return detections
        
        try:
            current_gas = gas_data['current_gas_price']
            gas_history = gas_data.get('gas_history', [])
            
            if len(gas_history) < 10:
                return detections
            
            # Calculate gas statistics
            gas_prices = np.array(gas_history)
            mean_gas = np.mean(gas_prices)
            std_gas = np.std(gas_prices)
            
            if std_gas == 0:
                return detections
            
            gas_z = (current_gas - mean_gas) / std_gas
            
            # Check for gas spikes
            if gas_z > self.detection_params['gas_price_spike_threshold']:
                severity = AnomalySeverity.HIGH if gas_z > 6.0 else AnomalySeverity.MEDIUM
                confidence = min(0.95, gas_z / 8.0)
                
                detection = AnomalyDetection(
                    detection_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    timestamp=datetime.now(),
                    anomaly_type=AnomalyType.GAS_ANOMALY,
                    severity=severity,
                    confidence=confidence,
                    affected_assets=['network'],
                    description=f"Gas price anomaly detected (z-score: {gas_z:.2f})",
                    triggers={
                        'gas_z_score': gas_z,
                        'current_gas': current_gas,
                        'mean_gas': mean_gas
                    },
                    metadata={
                        'network_congestion': gas_data.get('congestion', 0),
                        'pending_transactions': gas_data.get('pending_txs', 0)
                    }
                )
                
                detections.append(detection)
                print(f"Gas anomaly detected: z-score {gas_z:.2f}")
        
        except Exception as e:
            print(f"Error in gas anomaly detection: {e}")
        
        return detections
    
    async def _detect_frontrunning(self, market_data: Dict[str, Any]) -> List[AnomalyDetection]:
        """Detect front-running and sandwich attacks"""
        
        detections = []
        rule = self.active_rules[AnomalyType.FRONT_RUNNING]
        
        if not rule.enabled:
            return detections
        
        transaction_data = market_data.get('transaction_data', {})
        
        for tx_batch in transaction_data.get('suspicious_batches', []):
            try:
                time_gap = tx_batch.get('time_gap', 10)
                price_impact = tx_batch.get('price_impact', 0)
                similarity = tx_batch.get('similarity_score', 0)
                
                # Apply detection rule
                if (time_gap < rule.parameters['time_gap_threshold'] and
                    price_impact > rule.parameters['price_impact_threshold'] and
                    similarity > rule.parameters['similarity_threshold']):
                    
                    # Determine severity
                    severity = self._map_frontrunning_severity(time_gap, rule)
                    confidence = min(0.95, (1 - time_gap/10) * similarity)
                    
                    detection = AnomalyDetection(
                        detection_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        timestamp=datetime.now(),
                        anomaly_type=AnomalyType.FRONT_RUNNING,
                        severity=severity,
                        confidence=confidence,
                        affected_assets=tx_batch.get('assets', ['unknown']),
                        description=f"Front-running detected (time gap: {time_gap}s, impact: {price_impact:.2%})",
                        triggers={
                            'time_gap': time_gap,
                            'price_impact': price_impact,
                            'similarity_score': similarity
                        },
                        metadata={
                            'transaction_count': tx_batch.get('tx_count', 0),
                            'total_value': tx_batch.get('total_value', 0),
                            'rule_applied': rule.rule_id
                        }
                    )
                    
                    detections.append(detection)
                    print(f"Front-running detected: time gap {time_gap}s, impact {price_impact:.2%}")
            
            except Exception as e:
                print(f"Error in front-running detection: {e}")
                continue
        
        return detections
    
    def _calculate_volume_z_score(self, volume_data: Dict[str, Any]) -> float:
        """Calculate volume z-score"""
        current_volume = volume_data.get('current_volume', 0)
        volume_history = volume_data.get('volume_history', [])
        
        if len(volume_history) < 5:
            return 0.0
        
        volumes = np.array(volume_history)
        mean_volume = np.mean(volumes)
        std_volume = np.std(volumes)
        
        if std_volume == 0:
            return 0.0
        
        return (current_volume - mean_volume) / std_volume
    
    def _calculate_reversion_probability(self, current_price: float, mean_price: float, 
                                       std_price: float) -> float:
        """Calculate probability of price reversion to mean"""
        if std_price == 0:
            return 0.5
        
        deviation = abs(current_price - mean_price) / std_price
        # Simple heuristic: higher deviation → higher reversion probability
        return min(0.95, deviation / 5.0)
    
    def _calculate_liquidity_impact(self, pool_data: Dict[str, Any]) -> float:
        """Calculate market impact of liquidity change"""
        liquidity_change = pool_data.get('liquidity_change', 0)
        pool_size = pool_data.get('total_liquidity', 1)
        importance = pool_data.get('pool_importance', 0.5)
        
        # Simple impact calculation
        impact = liquidity_change * importance
        return min(1.0, impact)
    
    def _map_price_severity(self, z_score: float, rule: DetectionRule) -> AnomalySeverity:
        """Map price z-score to severity level"""
        if z_score > 5.0:
            return AnomalySeverity.CRITICAL
        elif z_score > 4.0:
            return AnomalySeverity.HIGH
        elif z_score > 3.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def _map_liquidity_severity(self, change: float, rule: DetectionRule) -> AnomalySeverity:
        """Map liquidity change to severity level"""
        if change > 0.8:
            return AnomalySeverity.CRITICAL
        elif change > 0.6:
            return AnomalySeverity.HIGH
        elif change > 0.4:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def _map_volume_severity(self, z_score: float, rule: DetectionRule) -> AnomalySeverity:
        """Map volume z-score to severity level"""
        if z_score > 6.0:
            return AnomalySeverity.CRITICAL
        elif z_score > 5.0:
            return AnomalySeverity.HIGH
        elif z_score > 4.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def _map_frontrunning_severity(self, time_gap: float, rule: DetectionRule) -> AnomalySeverity:
        """Map front-running time gap to severity level"""
        if time_gap < 1.0:
            return AnomalySeverity.CRITICAL
        elif time_gap < 2.0:
            return AnomalySeverity.HIGH
        else:
            return AnomalySeverity.MEDIUM
    
    def update_detection_rule(self, anomaly_type: AnomalyType, new_rule: DetectionRule):
        """Update detection rule parameters"""
        self.active_rules[anomaly_type] = new_rule
        print(f"Updated detection rule for {anomaly_type.value}")
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics"""
        
        recent_detections = list(self.detection_history)[-1000:]  # Last 1000 detections
        
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for detection in recent_detections:
            type_counts[detection.anomaly_type.value] += 1
            severity_counts[detection.severity.value] += 1
        
        return {
            'total_detections': self.performance_metrics['total_detections'],
            'recent_detections': len(recent_detections),
            'type_distribution': dict(type_counts),
            'severity_distribution': dict(severity_counts),
            'precision': self.performance_metrics['precision'],
            'recall': self.performance_metrics['recall'],
            'active_rules': len([r for r in self.active_rules.values() if r.enabled])
        }
    
    def validate_anomaly(self, detection_id: str, is_true_positive: bool):
        """Validate anomaly detection (for learning)"""
        
        detection = next((d for d in self.detection_history if d.detection_id == detection_id), None)
        
        if detection:
            if is_true_positive:
                self.performance_metrics['true_positives'] += 1
            else:
                self.performance_metrics['false_positives'] += 1
            
            # Update precision and recall
            total_positives = self.performance_metrics['true_positives'] + self.performance_metrics['false_positives']
            if total_positives > 0:
                self.performance_metrics['precision'] = (
                    self.performance_metrics['true_positives'] / total_positives
                )
            
            print(f"Anomaly validation: {detection_id} - {'True Positive' if is_true_positive else 'False Positive'}")
    
    async def train_models(self, training_data: Dict[str, Any]):
        """Train anomaly detection models on historical data"""
        
        print("Training anomaly detection models...")
        
        # This would implement actual model training
        # For now, just update statistical models
        for model_name, model in self.statistical_models.items():
            model['last_update'] = datetime.now()
            print(f"Updated {model_name} model")
        
        print("Model training completed")

# Example usage
if __name__ == "__main__":
    # Create anomaly detector
    detector = AnomalyDetector()
    
    # Sample market data
    sample_market_data = {
        'price_data': {
            'ETH': {
                'current_price': 2500.0,
                'price_history': [2450, 2460, 2470, 2480, 2490, 2500, 2510, 2520, 2530, 2540]
            }
        },
        'volume_data': {
            'ETH': {
                'current_volume': 1000000,
                'volume_history': [500000, 550000, 600000, 650000, 700000] * 4,
                'price_correlation': -0.3,
                'spike_duration': 45
            }
        },
        'liquidity_data': {
            'UNI_V3_ETH_USDC': {
                'current_liquidity': 5000000,
                'liquidity_history': [4800000, 4900000, 4950000, 5000000, 5050000],
                'recovery_time': 400,
                'assets': ['ETH', 'USDC'],
                'pool_importance': 0.8
            }
        },
        'gas_data': {
            'current_gas_price': 150.0,
            'gas_history': [30, 35, 40, 45, 50] * 4,
            'congestion': 0.8,
            'pending_txs': 15000
        },
        'transaction_data': {
            'suspicious_batches': [
                {
                    'time_gap': 2.5,
                    'price_impact': 0.03,
                    'similarity_score': 0.95,
                    'assets': ['ETH'],
                    'tx_count': 3,
                    'total_value': 500000
                }
            ]
        }
    }
    
    # Detect anomalies
    async def demo():
        anomalies = await detector.detect_anomalies(sample_market_data)
        
        print(f"Detected {len(anomalies)} anomalies:")
        for anomaly in anomalies:
            print(f" - {anomaly.anomaly_type.value}: {anomaly.severity.value} "
                  f"(confidence: {anomaly.confidence:.2f})")
        
        # Get statistics
        stats = detector.get_detection_statistics()
        print(f"\nDetection Statistics: {stats}")
    
    import asyncio
    asyncio.run(demo())
