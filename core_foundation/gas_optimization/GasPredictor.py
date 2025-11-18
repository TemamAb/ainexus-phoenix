"""
Enterprise Gas Price Prediction Engine
AI-powered gas price forecasting with EIP-1559 optimization
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configure enterprise logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GasPriority(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class GasPrediction:
    timestamp: datetime
    base_fee_prediction: float
    priority_fee_predictions: Dict[GasPriority, float]
    confidence: float
    market_conditions: Dict[str, Any]
    recommended_strategy: str

@dataclass
class GasConfig:
    prediction_horizon: int = 6  # blocks to predict ahead
    confidence_threshold: float = 0.85
    max_priority_fee: float = 3.0  # Gwei
    fallback_priority_fee: float = 1.5  # Gwei
    update_frequency: int = 30  # seconds
    historical_window: int = 1000  # blocks

@dataclass
class BlockData:
    block_number: int
    base_fee_per_gas: float
    gas_used: int
    gas_limit: int
    timestamp: datetime
    transactions_count: int
    priority_fees: List[float]

class GasPredictor:
    """
    Enterprise-grade gas price prediction engine with EIP-1559 optimization,
    machine learning forecasting, and real-time market analysis.
    """
    
    def __init__(self, config: GasConfig = None):
        self.config = config or GasConfig()
        self.model = None
        self.scaler = StandardScaler()
        self.historical_data: List[BlockData] = []
        self.prediction_cache: Dict[str, GasPrediction] = {}
        
        # Market analysis components
        self.network_analyzer = NetworkCongestionAnalyzer()
        self.fee_optimizer = FeeOptimizationEngine()
        self.anomaly_detector = GasAnomalyDetector()
        
        # Performance metrics
        self.metrics = {
            'total_predictions': 0,
            'accurate_predictions': 0,
            'average_confidence': 0.0,
            'prediction_latency': 0.0
        }
        
        # Initialize models
        self.initialize_models()
        logger.info("GasPredictor initialized with EIP-1559 optimization")

    def initialize_models(self):
        """Initialize machine learning models for gas prediction"""
        try:
            # Ensemble model for base fee prediction
            self.base_fee_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            # Model for priority fee prediction
            self.priority_fee_model = GradientBoostingRegressor(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
            
            # Initialize with dummy data for cold start
            dummy_X = np.random.rand(10, 5)
            dummy_y = np.random.rand(10)
            self.base_fee_model.fit(dummy_X, dummy_y)
            self.priority_fee_model.fit(dummy_X, dummy_y)
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            self._initialize_fallback_models()

    def _initialize_fallback_models(self):
        """Initialize fallback models if primary initialization fails"""
        self.base_fee_model = None
        self.priority_fee_model = None
        logger.warning("Using fallback statistical models")

    async def predict_gas_prices(self, 
                               current_block_data: Dict[str, Any],
                               priority: GasPriority = GasPriority.MEDIUM) -> GasPrediction:
        """
        Predict gas prices for upcoming blocks with confidence scoring
        """
        start_time = datetime.utcnow()
        self.metrics['total_predictions'] += 1
        
        try:
            logger.info(f"Starting gas prediction for priority: {priority.value}")
            
            # 1. Analyze current network conditions
            network_analysis = await self.analyze_network_conditions(current_block_data)
            
            # 2. Predict base fee for upcoming blocks
            base_fee_predictions = await self.predict_base_fee_series(
                current_block_data, 
                self.config.prediction_horizon
            )
            
            # 3. Predict priority fees based on urgency
            priority_fee_predictions = await self.predict_priority_fees(
                base_fee_predictions, 
                network_analysis,
                priority
            )
            
            # 4. Calculate confidence scores
            confidence = self.calculate_prediction_confidence(
                base_fee_predictions, 
                priority_fee_predictions,
                network_analysis
            )
            
            # 5. Determine optimal strategy
            recommended_strategy = self.determine_optimal_strategy(
                base_fee_predictions,
                priority_fee_predictions,
                priority,
                confidence
            )
            
            # Compile prediction result
            prediction = GasPrediction(
                timestamp=datetime.utcnow(),
                base_fee_prediction=base_fee_predictions[0],  # Next block prediction
                priority_fee_predictions=priority_fee_predictions,
                confidence=confidence,
                market_conditions=network_analysis,
                recommended_strategy=recommended_strategy
            )
            
            # Cache prediction
            cache_key = f"{current_block_data.get('block_number', 0)}_{priority.value}"
            self.prediction_cache[cache_key] = prediction
            
            # Update performance metrics
            self._update_performance_metrics(start_time, confidence)
            
            logger.info(f"Gas prediction completed with confidence: {confidence:.2f}")
            return prediction
            
        except Exception as e:
            logger.error(f"Gas prediction failed: {e}")
            return await self.get_fallback_prediction(priority)

    async def predict_base_fee_series(self, 
                                    current_block_data: Dict[str, Any], 
                                    horizon: int) -> List[float]:
        """Predict base fee for multiple upcoming blocks"""
        try:
            # Prepare features for prediction
            features = self._prepare_base_fee_features(current_block_data)
            
            if self.base_fee_model and len(self.historical_data) > 50:
                # Use ML model for prediction
                predictions = []
                current_features = features.copy()
                
                for i in range(horizon):
                    # Scale features
                    scaled_features = self.scaler.transform([current_features])
                    
                    # Predict next base fee
                    pred = self.base_fee_model.predict(scaled_features)[0]
                    predictions.append(max(0.1, pred))  # Ensure positive base fee
                    
                    # Update features for next prediction
                    current_features = self._update_features_for_next_prediction(
                        current_features, pred, i
                    )
                
                return predictions
            else:
                # Use statistical fallback
                return await self._statistical_base_fee_prediction(
                    current_block_data, horizon
                )
                
        except Exception as e:
            logger.warning(f"ML base fee prediction failed, using fallback: {e}")
            return await self._statistical_base_fee_prediction(current_block_data, horizon)

    async def _statistical_base_fee_prediction(self, 
                                             current_block_data: Dict[str, Any],
                                             horizon: int) -> List[float]:
        """Statistical fallback for base fee prediction"""
        recent_base_fees = [bd.base_fee_per_gas for bd in self.historical_data[-50:]]
        
        if not recent_base_fees:
            return [current_block_data.get('base_fee_per_gas', 30.0)] * horizon
        
        current_base_fee = current_block_data.get('base_fee_per_gas', recent_base_fees[-1])
        gas_used_ratio = current_block_data.get('gas_used', 0) / current_block_data.get('gas_limit', 30_000_000)
        
        predictions = []
        base_fee = current_base_fee
        
        for i in range(horizon):
            # EIP-1559 base fee adjustment calculation
            if gas_used_ratio > 0.5:  # Target is 50% full
                # Increase base fee
                adjustment = (gas_used_ratio - 0.5) * 1.125  # Max 12.5% increase
                base_fee *= (1 + adjustment)
            else:
                # Decrease base fee
                adjustment = (0.5 - gas_used_ratio) * 1.125
                base_fee *= (1 - adjustment)
            
            # Add some randomness based on historical volatility
            if len(recent_base_fees) > 10:
                volatility = np.std(recent_base_fees) / np.mean(recent_base_fees)
                random_factor = 1 + np.random.normal(0, volatility * 0.5)
                base_fee *= random_factor
            
            predictions.append(max(0.1, base_fee))
            
            # Simulate gas usage for next prediction
            gas_used_ratio = min(1.0, gas_used_ratio * (1 + np.random.normal(0, 0.1)))
        
        return predictions

    async def predict_priority_fees(self,
                                  base_fee_predictions: List[float],
                                  network_analysis: Dict[str, Any],
                                  priority: GasPriority) -> Dict[GasPriority, float]:
        """Predict priority fees for different urgency levels"""
        try:
            current_congestion = network_analysis.get('congestion_level', 0.5)
            mempool_pressure = network_analysis.get('mempool_pressure', 0.5)
            
            # Base priority fees based on network conditions
            base_priority = self._calculate_base_priority_fee(
                current_congestion, 
                mempool_pressure
            )
            
            # Adjust for different priority levels
            priority_fees = {}
            for p in GasPriority:
                multiplier = self._get_priority_multiplier(p, current_congestion)
                priority_fees[p] = min(
                    self.config.max_priority_fee,
                    base_priority * multiplier
                )
            
            # Ensure proper ordering
            priority_fees = dict(sorted(
                priority_fees.items(), 
                key=lambda x: self._get_priority_multiplier(x[0], current_congestion)
            ))
            
            return priority_fees
            
        except Exception as e:
            logger.warning(f"Priority fee prediction failed: {e}")
            return self._get_fallback_priority_fees()

    def _calculate_base_priority_fee(self, congestion: float, mempool_pressure: float) -> float:
        """Calculate base priority fee based on network conditions"""
        # Base fee increases with congestion and mempool pressure
        base_fee = 0.1  # Minimum priority fee
        
        # Congestion factor (0.0 to 2.0 Gwei)
        congestion_factor = congestion * 2.0
        
        # Mempool pressure factor (0.0 to 1.0 Gwei)
        pressure_factor = mempool_pressure * 1.0
        
        total_fee = base_fee + congestion_factor + pressure_factor
        
        return min(self.config.max_priority_fee, total_fee)

    def _get_priority_multiplier(self, priority: GasPriority, congestion: float) -> float:
        """Get multiplier for different priority levels"""
        base_multipliers = {
            GasPriority.LOW: 0.5,
            GasPriority.MEDIUM: 1.0,
            GasPriority.HIGH: 2.0,
            GasPriority.URGENT: 4.0
        }
        
        # Adjust multipliers based on congestion
        base_multiplier = base_multipliers[priority]
        
        if congestion > 0.7:  # High congestion
            if priority in [GasPriority.HIGH, GasPriority.URGENT]:
                return base_multiplier * 1.5
            else:
                return base_multiplier * 0.8  # Lower priorities get squeezed
        elif congestion < 0.3:  # Low congestion
            return base_multiplier * 0.7
        
        return base_multiplier

    async def analyze_network_conditions(self, current_block_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive network conditions analysis"""
        try:
            # Calculate congestion level
            gas_used_ratio = current_block_data.get('gas_used', 0) / current_block_data.get('gas_limit', 30_000_000)
            
            # Analyze historical trends
            trend_analysis = self._analyze_historical_trends()
            
            # Mempool analysis
            mempool_analysis = await self._analyze_mempool_conditions()
            
            # Network health assessment
            health_metrics = self._assess_network_health()
            
            # Detect anomalies
            anomalies = self.anomaly_detector.detect_anomalies(
                current_block_data, 
                self.historical_data
            )
            
            return {
                'congestion_level': min(1.0, gas_used_ratio * 1.5),  # Normalize to 0-1
                'gas_used_ratio': gas_used_ratio,
                'trend_direction': trend_analysis.get('direction', 'stable'),
                'trend_strength': trend_analysis.get('strength', 0),
                'mempool_pressure': mempool_analysis.get('pressure', 0.5),
                'pending_transactions': mempool_analysis.get('pending_count', 0),
                'network_health': health_metrics.get('health_score', 1.0),
                'anomalies_detected': len(anomalies) > 0,
                'anomaly_details': anomalies,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Network analysis failed: {e}")
            return {
                'congestion_level': 0.5,
                'gas_used_ratio': 0.5,
                'trend_direction': 'unknown',
                'trend_strength': 0,
                'mempool_pressure': 0.5,
                'network_health': 0.5,
                'anomalies_detected': False,
                'error': str(e)
            }

    def _analyze_historical_trends(self) -> Dict[str, Any]:
        """Analyze historical gas price trends"""
        if len(self.historical_data) < 10:
            return {'direction': 'stable', 'strength': 0}
        
        recent_fees = [bd.base_fee_per_gas for bd in self.historical_data[-20:]]
        
        if len(recent_fees) < 5:
            return {'direction': 'stable', 'strength': 0}
        
        # Calculate trend using linear regression
        x = np.arange(len(recent_fees))
        slope, _, r_value, _, _ = stats.linregress(x, recent_fees)
        
        direction = 'increasing' if slope > 0.01 else 'decreasing' if slope < -0.01 else 'stable'
        strength = min(1.0, abs(slope) * 100)  # Normalize strength
        
        return {
            'direction': direction,
            'strength': strength,
            'correlation': r_value ** 2
        }

    async def _analyze_mempool_conditions(self) -> Dict[str, Any]:
        """Analyze current mempool conditions"""
        try:
            # This would integrate with mempool monitoring services
            async with aiohttp.ClientSession() as session:
                async with session.get('https://etherscan.io/gastracker') as response:
                    # Parse mempool data (simplified)
                    return {
                        'pressure': np.random.uniform(0.1, 0.9),  # Simulated
                        'pending_count': np.random.randint(1000, 50000),
                        'avg_pending_time': np.random.uniform(10, 300)
                    }
        except Exception as e:
            logger.warning(f"Mempool analysis failed: {e}")
            return {
                'pressure': 0.5,
                'pending_count': 15000,
                'avg_pending_time': 60
            }

    def _assess_network_health(self) -> Dict[str, Any]:
        """Assess overall network health and stability"""
        if len(self.historical_data) < 20:
            return {'health_score': 1.0, 'stability': 1.0}
        
        recent_blocks = self.historical_data[-20:]
        
        # Calculate base fee volatility
        base_fees = [bd.base_fee_per_gas for bd in recent_blocks]
        volatility = np.std(base_fees) / np.mean(base_fees) if np.mean(base_fees) > 0 else 0
        
        # Calculate block time consistency
        timestamps = [bd.timestamp for bd in recent_blocks]
        block_times = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                      for i in range(1, len(timestamps))]
        time_std = np.std(block_times) if block_times else 0
        
        # Health score (1.0 is perfect)
        volatility_score = max(0, 1 - volatility * 10)  # Penalize high volatility
        time_score = max(0, 1 - time_std / 5)  # Penalize inconsistent block times
        
        health_score = (volatility_score + time_score) / 2
        
        return {
            'health_score': health_score,
            'volatility': volatility,
            'block_time_consistency': 1 - min(1, time_std / 2),
            'stability': health_score
        }

    def calculate_prediction_confidence(self,
                                      base_fee_predictions: List[float],
                                      priority_fee_predictions: Dict[GasPriority, float],
                                      network_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for predictions"""
        confidence_factors = []
        
        # Historical accuracy factor
        if len(self.historical_data) > 50:
            historical_accuracy = self._calculate_historical_accuracy()
            confidence_factors.append(historical_accuracy)
        
        # Network stability factor
        stability = network_analysis.get('network_health', 0.5)
        confidence_factors.append(stability)
        
        # Trend strength factor
        trend_strength = network_analysis.get('trend_strength', 0)
        trend_confidence = 1 - min(1.0, abs(trend_strength) * 2)  # Strong trends = lower confidence
        confidence_factors.append(trend_confidence)
        
        # Anomaly factor
        if network_analysis.get('anomalies_detected', False):
            confidence_factors.append(0.3)  # Significant penalty for anomalies
        else:
            confidence_factors.append(0.9)
        
        # Data freshness factor
        if self.historical_data:
            latest_block_time = self.historical_data[-1].timestamp
            time_diff = (datetime.utcnow() - latest_block_time).total_seconds()
            freshness = max(0, 1 - time_diff / 300)  # 5 minute half-life
            confidence_factors.append(freshness)
        
        return min(0.99, np.mean(confidence_factors))

    def _calculate_historical_accuracy(self) -> float:
        """Calculate accuracy of previous predictions"""
        if len(self.historical_data) < 10:
            return 0.5
        
        # Compare recent predictions with actuals
        accuracy_scores = []
        
        for i in range(min(20, len(self.historical_data) - 1)):
            if i >= len(self.prediction_cache):
                continue
                
            # This is simplified - would need actual prediction storage
            accuracy_scores.append(0.8)  # Placeholder
        
        return np.mean(accuracy_scores) if accuracy_scores else 0.7

    def determine_optimal_strategy(self,
                                 base_fee_predictions: List[float],
                                 priority_fee_predictions: Dict[GasPriority, float],
                                 priority: GasPriority,
                                 confidence: float) -> str:
        """Determine optimal gas bidding strategy"""
        next_base_fee = base_fee_predictions[0]
        recommended_priority_fee = priority_fee_predictions[priority]
        
        if confidence < 0.6:
            return "conservative_bidding"
        
        # Analyze fee trends
        fee_trend = "stable"
        if len(base_fee_predictions) > 3:
            if base_fee_predictions[3] > next_base_fee * 1.1:
                fee_trend = "increasing"
            elif base_fee_predictions[3] < next_base_fee * 0.9:
                fee_trend = "decreasing"
        
        if fee_trend == "decreasing" and priority != GasPriority.URGENT:
            return "delayed_execution"
        elif fee_trend == "increasing" and priority in [GasPriority.HIGH, GasPriority.URGENT]:
            return "accelerated_execution"
        elif confidence > 0.8:
            return "optimized_bidding"
        else:
            return "standard_bidding"

    async def get_fallback_prediction(self, priority: GasPriority) -> GasPrediction:
        """Get fallback prediction when primary prediction fails"""
        logger.warning("Using fallback gas prediction")
        
        return GasPrediction(
            timestamp=datetime.utcnow(),
            base_fee_prediction=30.0,  # Conservative base fee
            priority_fee_predictions=self._get_fallback_priority_fees(),
            confidence=0.5,
            market_conditions={'fallback': True, 'congestion_level': 0.5},
            recommended_strategy="conservative_bidding"
        )

    def _get_fallback_priority_fees(self) -> Dict[GasPriority, float]:
        """Get fallback priority fees"""
        return {
            GasPriority.LOW: 0.5,
            GasPriority.MEDIUM: 1.0,
            GasPriority.HIGH: 2.0,
            GasPriority.URGENT: 3.0
        }

    def _prepare_base_fee_features(self, current_block_data: Dict[str, Any]) -> List[float]:
        """Prepare features for base fee prediction"""
        features = []
        
        # Current block features
        features.append(current_block_data.get('base_fee_per_gas', 30.0))
        features.append(current_block_data.get('gas_used', 15_000_000))
        features.append(current_block_data.get('gas_limit', 30_000_000))
        features.append(current_block_data.get('transactions_count', 150))
        
        # Historical features
        if self.historical_data:
            recent_fees = [bd.base_fee_per_gas for bd in self.historical_data[-10:]]
            features.append(np.mean(recent_fees))
            features.append(np.std(recent_fees))
            features.append(len(recent_fees))
        else:
            features.extend([30.0, 5.0, 1.0])
        
        # Time-based features
        now = datetime.utcnow()
        features.append(now.hour)  # Hour of day
        features.append(now.weekday())  # Day of week
        
        return features

    def _update_features_for_next_prediction(self, 
                                           current_features: List[float],
                                           predicted_base_fee: float,
                                           step: int) -> List[float]:
        """Update features for multi-step prediction"""
        # This is a simplified implementation
        # In production, this would incorporate more sophisticated state management
        new_features = current_features.copy()
        
        # Update base fee
        new_features[0] = predicted_base_fee
        
        # Simulate gas usage changes
        new_features[1] = new_features[1] * (1 + np.random.normal(0, 0.05))
        new_features[1] = min(new_features[2] * 0.95, new_features[1])  # Don't exceed limit
        
        return new_features

    def _update_performance_metrics(self, start_time: datetime, confidence: float):
        """Update performance tracking metrics"""
        latency = (datetime.utcnow() - start_time).total_seconds()
        
        self.metrics['prediction_latency'] = (
            self.metrics['prediction_latency'] * (self.metrics['total_predictions'] - 1) + latency
        ) / self.metrics['total_predictions']
        
        self.metrics['average_confidence'] = (
            self.metrics['average_confidence'] * (self.metrics['total_predictions'] - 1) + confidence
        ) / self.metrics['total_predictions']

    async def update_historical_data(self, new_block_data: BlockData):
        """Update historical data with new block information"""
        self.historical_data.append(new_block_data)
        
        # Maintain window size
        if len(self.historical_data) > self.config.historical_window:
            self.historical_data = self.historical_data[-self.config.historical_window:]
        
        # Retrain models periodically
        if len(self.historical_data) % 100 == 0:
            await self.retrain_models()

    async def retrain_models(self):
        """Retrain ML models with updated historical data"""
        if len(self.historical_data) < 100:
            logger.info("Insufficient data for model retraining")
            return
        
        try:
            logger.info("Retraining gas prediction models...")
            
            # Prepare training data
            X, y = self._prepare_training_data()
            
            if len(X) > 50:
                # Retrain base fee model
                self.base_fee_model.fit(X, y)
                
                # Update scaler
                self.scaler.fit(X)
                
                logger.info("Models retrained successfully")
            else:
                logger.warning("Insufficient training data for retraining")
                
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")

    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from historical blocks"""
        X = []
        y = []
        
        for i in range(1, len(self.historical_data)):
            current_block = self.historical_data[i-1]
            next_block = self.historical_data[i]
            
            features = self._prepare_base_fee_features({
                'base_fee_per_gas': current_block.base_fee_per_gas,
                'gas_used': current_block.gas_used,
                'gas_limit': current_block.gas_limit,
                'transactions_count': current_block.transactions_count
            })
            
            X.append(features)
            y.append(next_block.base_fee_per_gas)
        
        return np.array(X), np.array(y)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            **self.metrics,
            'historical_data_points': len(self.historical_data),
            'model_status': 'active' if self.base_fee_model else 'fallback',
            'cache_size': len(self.prediction_cache),
            'last_update': datetime.utcnow().isoformat()
        }

# Supporting classes
class NetworkCongestionAnalyzer:
    def __init__(self):
        self.congestion_models = {}

class FeeOptimizationEngine:
    def __init__(self):
        self.optimization_strategies = {}

class GasAnomalyDetector:
    def detect_anomalies(self, current_block: Dict[str, Any], historical_data: List[BlockData]) -> List[Dict[str, Any]]:
        """Detect anomalies in gas price patterns"""
        # Simplified anomaly detection
        anomalies = []
        
        if historical_data:
            recent_base_fees = [bd.base_fee_per_gas for bd in historical_data[-10:]]
            avg_base_fee = np.mean(recent_base_fees)
            std_base_fee = np.std(recent_base_fees)
            
            current_base_fee = current_block.get('base_fee_per_gas', avg_base_fee)
            
            # Check for significant deviation
            if std_base_fee > 0 and abs(current_base_fee - avg_base_fee) > 3 * std_base_fee:
                anomalies.append({
                    'type': 'BASE_FEE_SPIKE',
                    'severity': 'high',
                    'current_value': current_base_fee,
                    'expected_range': f"{avg_base_fee - 2*std_base_fee:.2f}-{avg_base_fee + 2*std_base_fee:.2f}"
                })
        
        return anomalies

# Factory function
def create_gas_predictor(config: GasConfig = None) -> GasPredictor:
    return GasPredictor(config)

# Example usage
async def example_usage():
    """Example demonstrating gas prediction usage"""
    predictor = GasPredictor()
    
    # Simulate current block data
    current_block = {
        'block_number': 18000000,
        'base_fee_per_gas': 32.5,
        'gas_used': 22_500_000,
        'gas_limit': 30_000_000,
        'transactions_count': 185,
        'timestamp': datetime.utcnow()
    }
    
    # Get gas prediction
    prediction = await predictor.predict_gas_prices(
        current_block, 
        GasPriority.HIGH
    )
    
    print("Gas Prediction Results:")
    print(f"Base Fee: {prediction.base_fee_prediction:.2f} Gwei")
    print(f"Priority Fees: {prediction.priority_fee_predictions}")
    print(f"Confidence: {prediction.confidence:.2f}")
    print(f"Strategy: {prediction.recommended_strategy}")
    print(f"Market Conditions: {prediction.market_conditions}")
    
    # Show performance metrics
    print("\nPerformance Metrics:")
    print(predictor.get_performance_metrics())

if __name__ == "__main__":
    asyncio.run(example_usage())
