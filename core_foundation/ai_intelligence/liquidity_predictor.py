"""
AI-NEXUS LIQUIDITY PREDICTOR
Advanced liquidity forecasting and prediction engine
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn

class LiquidityTrend(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"

@dataclass
class LiquidityPrediction:
    timestamp: int
    pool_address: str
    token_pair: Tuple[str, str]
    predicted_liquidity: float
    confidence: float
    trend: LiquidityTrend
    factors: Dict
    time_horizon: int  # in minutes

@dataclass
class LiquidityAlert:
    alert_id: str
    pool_address: str
    alert_type: str
    severity: str
    message: str
    timestamp: int
    metrics: Dict
    recommendation: str

class LSTMLiquidityModel(nn.Module):
    """LSTM Neural Network for liquidity prediction"""
    
    def __init__(self, input_size=10, hidden_size=64, num_layers=2, output_size=3):
        super(LSTMLiquidityModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, output_size)
        self.dropout = nn.Dropout(0.3)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.relu(self.fc1(out[:, -1, :]))
        out = self.dropout(out)
        out = self.fc2(out)
        return out

class LiquidityPredictor:
    """Advanced liquidity prediction engine with ML capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.prediction_history = {}
        self.feature_importance = {}
        
        # Initialize ML models
        self.initialize_models()
        
    def initialize_models(self):
        """Initialize prediction models for different time horizons"""
        time_horizons = [5, 15, 30, 60]  # minutes
        
        for horizon in time_horizons:
            # Random Forest for feature importance
            self.models[f'rf_{horizon}'] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # LSTM for sequence prediction
            self.models[f'lstm_{horizon}'] = LSTMLiquidityModel()
            
            # Scaler for feature normalization
            self.scalers[f'scaler_{horizon}'] = StandardScaler()
    
    async def predict_liquidity(self, pool_data: Dict, time_horizon: int = 15) -> LiquidityPrediction:
        """Predict liquidity for a specific pool and time horizon"""
        try:
            # Extract features
            features = await self.extract_features(pool_data)
            
            # Generate predictions from multiple models
            rf_prediction = await self.random_forest_prediction(features, time_horizon)
            lstm_prediction = await self.lstm_prediction(features, time_horizon)
            
            # Ensemble predictions
            final_prediction = self.ensemble_predictions([rf_prediction, lstm_prediction])
            
            # Analyze trend
            trend = await self.analyze_liquidity_trend(pool_data, final_prediction)
            
            # Calculate confidence
            confidence = await self.calculate_prediction_confidence(features, final_prediction)
            
            prediction = LiquidityPrediction(
                timestamp=int(pd.Timestamp.now().timestamp()),
                pool_address=pool_data['address'],
                token_pair=pool_data['token_pair'],
                predicted_liquidity=final_prediction,
                confidence=confidence,
                trend=trend,
                factors=features,
                time_horizon=time_horizon
            )
            
            # Store prediction history
            await self.store_prediction_history(prediction)
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Liquidity prediction failed: {e}")
            raise
    
    async def extract_features(self, pool_data: Dict) -> Dict:
        """Extract features for liquidity prediction"""
        features = {}
        
        # Historical liquidity data
        features['liquidity_5m_change'] = await self.calculate_liquidity_change(pool_data, 5)
        features['liquidity_15m_change'] = await self.calculate_liquidity_change(pool_data, 15)
        features['liquidity_1h_change'] = await self.calculate_liquidity_change(pool_data, 60)
        
        # Volume metrics
        features['volume_24h'] = pool_data.get('volume_24h', 0)
        features['volume_5m_avg'] = await self.calculate_volume_average(pool_data, 5)
        
        # Price impact features
        features['price_impact_10k'] = await self.calculate_price_impact(pool_data, 10000)
        features['price_impact_100k'] = await self.calculate_price_impact(pool_data, 100000)
        
        # Market depth features
        features['bid_ask_spread'] = await self.calculate_bid_ask_spread(pool_data)
        features['depth_imbalance'] = await self.calculate_depth_imbalance(pool_data)
        
        # Temporal features
        features['hour_of_day'] = pd.Timestamp.now().hour
        features['day_of_week'] = pd.Timestamp.now().dayofweek
        features['is_weekend'] = 1 if pd.Timestamp.now().dayofweek >= 5 else 0
        
        # Volatility features
        features['price_volatility_1h'] = await self.calculate_volatility(pool_data, 60)
        features['liquidity_volatility_1h'] = await self.calculate_liquidity_volatility(pool_data, 60)
        
        # Cross-pool features
        features['competitive_ratio'] = await self.calculate_competitive_ratio(pool_data)
        features['market_share'] = await self.calculate_market_share(pool_data)
        
        return features
    
    async def calculate_liquidity_change(self, pool_data: Dict, minutes: int) -> float:
        """Calculate liquidity change over specified minutes"""
        # Implementation would use historical data
        # Placeholder implementation
        return np.random.uniform(-0.1, 0.1)
    
    async def calculate_volume_average(self, pool_data: Dict, minutes: int) -> float:
        """Calculate volume average over specified minutes"""
        # Implementation would use historical data
        return pool_data.get('volume_24h', 0) / 288  # Approximate 5-minute average
    
    async def calculate_price_impact(self, pool_data: Dict, amount: float) -> float:
        """Calculate price impact for specified trade amount"""
        liquidity = pool_data.get('liquidity', 1)
        return amount / liquidity * 0.01  # Simplified calculation
    
    async def calculate_bid_ask_spread(self, pool_data: Dict) -> float:
        """Calculate bid-ask spread"""
        return pool_data.get('spread', 0.002)
    
    async def calculate_depth_imbalance(self, pool_data: Dict) -> float:
        """Calculate depth imbalance between bids and asks"""
        return np.random.uniform(0.8, 1.2)
    
    async def calculate_volatility(self, pool_data: Dict, minutes: int) -> float:
        """Calculate price volatility over specified minutes"""
        return np.random.uniform(0.001, 0.05)
    
    async def calculate_liquidity_volatility(self, pool_data: Dict, minutes: int) -> float:
        """Calculate liquidity volatility over specified minutes"""
        return np.random.uniform(0.01, 0.1)
    
    async def calculate_competitive_ratio(self, pool_data: Dict) -> float:
        """Calculate competitive ratio with other pools"""
        return np.random.uniform(0.1, 1.0)
    
    async def calculate_market_share(self, pool_data: Dict) -> float:
        """Calculate market share for this pool"""
        return np.random.uniform(0.01, 0.3)
    
    async def random_forest_prediction(self, features: Dict, time_horizon: int) -> float:
        """Generate prediction using Random Forest"""
        model_key = f'rf_{time_horizon}'
        scaler_key = f'scaler_{time_horizon}'
        
        # Convert features to array
        feature_array = np.array(list(features.values())).reshape(1, -1)
        
        # Scale features
        if hasattr(self.scalers[scaler_key], 'n_features_in_'):
            scaled_features = self.scalers[scaler_key].transform(feature_array)
        else:
            scaled_features = feature_array
        
        # Generate prediction
        prediction = self.models[model_key].predict(scaled_features)[0]
        
        return float(prediction)
    
    async def lstm_prediction(self, features: Dict, time_horizon: int) -> float:
        """Generate prediction using LSTM"""
        model_key = f'lstm_{time_horizon}'
        
        # Convert features to sequence format
        feature_sequence = await self.create_feature_sequence(features)
        
        # Generate prediction
        with torch.no_grad():
            prediction = self.models[model_key](feature_sequence)
            prediction = prediction.numpy()[0][0]
        
        return float(prediction)
    
    async def create_feature_sequence(self, features: Dict) -> torch.Tensor:
        """Create sequence data for LSTM"""
        # Create synthetic sequence from current features
        sequence_length = 10
        feature_count = len(features)
        
        # Create sequence with some noise
        base_sequence = np.array(list(features.values()))
        sequence = np.tile(base_sequence, (sequence_length, 1))
        
        # Add temporal variation
        for i in range(sequence_length):
            noise = np.random.normal(0, 0.01, feature_count)
            sequence[i] += noise
        
        return torch.FloatTensor(sequence).unsqueeze(0)
    
    def ensemble_predictions(self, predictions: List[float]) -> float:
        """Combine predictions from multiple models"""
        # Weighted average based on model performance
        weights = [0.6, 0.4]  # RF, LSTM weights
        return sum(p * w for p, w in zip(predictions, weights))
    
    async def analyze_liquidity_trend(self, pool_data: Dict, prediction: float) -> LiquidityTrend:
        """Analyze liquidity trend direction"""
        current_liquidity = pool_data.get('liquidity', 1)
        change_ratio = (prediction - current_liquidity) / current_liquidity
        
        if change_ratio > 0.05:
            return LiquidityTrend.BULLISH
        elif change_ratio < -0.05:
            return LiquidityTrend.BEARISH
        elif abs(change_ratio) < 0.01:
            return LiquidityTrend.SIDEWAYS
        else:
            return LiquidityTrend.VOLATILE
    
    async def calculate_prediction_confidence(self, features: Dict, prediction: float) -> float:
        """Calculate prediction confidence score"""
        confidence_factors = []
        
        # Feature quality confidence
        feature_completeness = len([v for v in features.values() if v != 0]) / len(features)
        confidence_factors.append(feature_completeness)
        
        # Prediction stability confidence
        stability_score = await self.assess_prediction_stability(prediction)
        confidence_factors.append(stability_score)
        
        # Market condition confidence
        market_confidence = await self.assess_market_conditions()
        confidence_factors.append(market_confidence)
        
        return float(np.mean(confidence_factors))
    
    async def assess_prediction_stability(self, prediction: float) -> float:
        """Assess prediction stability based on history"""
        if not self.prediction_history:
            return 0.8  # Default confidence
        
        recent_predictions = list(self.prediction_history.values())[-10:]
        if len(recent_predictions) < 3:
            return 0.8
        
        variances = [abs(p.predicted_liquidity - prediction) for p in recent_predictions]
        avg_variance = np.mean(variances)
        
        return max(0.1, 1 - avg_variance / prediction)
    
    async def assess_market_conditions(self) -> float:
        """Assess overall market conditions for confidence"""
        # Implementation would analyze market volatility, news, etc.
        return 0.7  # Placeholder
    
    async def store_prediction_history(self, prediction: LiquidityPrediction):
        """Store prediction in history"""
        key = f"{prediction.pool_address}_{prediction.timestamp}"
        self.prediction_history[key] = prediction
        
        # Keep only last 1000 predictions
        if len(self.prediction_history) > 1000:
            oldest_key = next(iter(self.prediction_history))
            del self.prediction_history[oldest_key]
    
    async def generate_liquidity_alerts(self, prediction: LiquidityPrediction) -> List[LiquidityAlert]:
        """Generate alerts based on liquidity predictions"""
        alerts = []
        
        # Low liquidity alert
        if prediction.predicted_liquidity < 100000:  # $100k threshold
            alerts.append(LiquidityAlert(
                alert_id=f"low_liquidity_{prediction.timestamp}",
                pool_address=prediction.pool_address,
                alert_type="LOW_LIQUIDITY",
                severity="HIGH",
                message=f"Low liquidity predicted: ${prediction.predicted_liquidity:,.0f}",
                timestamp=prediction.timestamp,
                metrics={"predicted_liquidity": prediction.predicted_liquidity},
                recommendation="Consider alternative pools or reduce trade size"
            ))
        
        # High volatility alert
        if prediction.trend == LiquidityTrend.VOLATILE:
            alerts.append(LiquidityAlert(
                alert_id=f"high_volatility_{prediction.timestamp}",
                pool_address=prediction.pool_address,
                alert_type="HIGH_VOLATILITY",
                severity="MEDIUM",
                message="High liquidity volatility predicted",
                timestamp=prediction.timestamp,
                metrics={"trend": prediction.trend.value},
                recommendation="Monitor closely and adjust strategy parameters"
            ))
        
        # Confidence alert
        if prediction.confidence < 0.5:
            alerts.append(LiquidityAlert(
                alert_id=f"low_confidence_{prediction.timestamp}",
                pool_address=prediction.pool_address,
                alert_type="LOW_CONFIDENCE",
                severity="LOW",
                message=f"Low prediction confidence: {prediction.confidence:.2f}",
                timestamp=prediction.timestamp,
                metrics={"confidence": prediction.confidence},
                recommendation="Verify with additional data sources"
            ))
        
        return alerts
    
    async def get_prediction_analytics(self, pool_address: str, hours: int = 24) -> Dict:
        """Get analytics for prediction performance"""
        relevant_predictions = [
            p for p in self.prediction_history.values() 
            if p.pool_address == pool_address and 
            p.timestamp > (pd.Timestamp.now().timestamp() - hours * 3600)
        ]
        
        if not relevant_predictions:
            return {"error": "No prediction data available"}
        
        actual_liquidity = await self.get_actual_liquidity(pool_address, hours)
        
        analytics = {
            "total_predictions": len(relevant_predictions),
            "average_confidence": np.mean([p.confidence for p in relevant_predictions]),
            "trend_distribution": self.analyze_trend_distribution(relevant_predictions),
            "performance_metrics": await self.calculate_performance_metrics(relevant_predictions, actual_liquidity),
            "feature_analysis": await self.analyze_feature_importance(relevant_predictions)
        }
        
        return analytics
    
    async def get_actual_liquidity(self, pool_address: str, hours: int) -> List[float]:
        """Get actual liquidity data for performance calculation"""
        # Implementation would fetch from database or API
        return [p.predicted_liquidity * np.random.uniform(0.9, 1.1) for p in range(24)]
    
    def analyze_trend_distribution(self, predictions: List[LiquidityPrediction]) -> Dict:
        """Analyze distribution of predicted trends"""
        trend_counts = {}
        for trend in LiquidityTrend:
            trend_counts[trend.value] = len([p for p in predictions if p.trend == trend])
        
        return trend_counts
    
    async def calculate_performance_metrics(self, predictions: List[LiquidityPrediction], actual: List[float]) -> Dict:
        """Calculate prediction performance metrics"""
        if len(predictions) != len(actual):
            return {"error": "Data length mismatch"}
        
        predicted_values = [p.predicted_liquidity for p in predictions]
        
        mae = np.mean(np.abs(np.array(predicted_values) - np.array(actual)))
        mse = np.mean((np.array(predicted_values) - np.array(actual)) ** 2)
        rmse = np.sqrt(mse)
        
        return {
            "mean_absolute_error": mae,
            "mean_squared_error": mse,
            "root_mean_squared_error": rmse,
            "mean_absolute_percentage_error": np.mean(np.abs((np.array(predicted_values) - np.array(actual)) / np.array(actual))) * 100
        }
    
    async def analyze_feature_importance(self, predictions: List[LiquidityPrediction]) -> Dict:
        """Analyze feature importance across predictions"""
        if not predictions:
            return {}
        
        # Extract features from first prediction
        feature_names = list(predictions[0].factors.keys())
        
        # Calculate correlation with prediction confidence
        correlations = {}
        for feature in feature_names:
            feature_values = [p.factors[feature] for p in predictions]
            confidence_values = [p.confidence for p in predictions]
            
            if len(set(feature_values)) > 1:  # Avoid constant features
                correlation = np.corrcoef(feature_values, confidence_values)[0, 1]
                correlations[feature] = correlation if not np.isnan(correlation) else 0
        
        return dict(sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True))
    
    async def optimize_prediction_models(self):
        """Optimize prediction models based on recent performance"""
        self.logger.info("Starting model optimization...")
        
        for model_key, model in self.models.items():
            if hasattr(model, 'partial_fit'):
                # Online learning for compatible models
                try:
                    training_data = await self.prepare_training_data(model_key)
                    if training_data:
                        model.partial_fit(training_data['X'], training_data['y'])
                        self.logger.info(f"Updated model: {model_key}")
                except Exception as e:
                    self.logger.error(f"Model update failed for {model_key}: {e}")
    
    async def prepare_training_data(self, model_key: str) -> Optional[Dict]:
        """Prepare training data for model optimization"""
        # Implementation would use recent prediction history and actual outcomes
        # Placeholder implementation
        return None

# Example usage
if __name__ == "__main__":
    predictor = LiquidityPredictor({})
    
    # Example pool data
    pool_data = {
        'address': '0x123...',
        'token_pair': ('WETH', 'USDC'),
        'liquidity': 1500000,
        'volume_24h': 5000000,
        'spread': 0.0015
    }
    
    # Run prediction
    async def example():
        prediction = await predictor.predict_liquidity(pool_data, 15)
        print(f"Predicted liquidity: ${prediction.predicted_liquidity:,.0f}")
        print(f"Confidence: {prediction.confidence:.2f}")
        print(f"Trend: {prediction.trend.value}")
        
        alerts = await predictor.generate_liquidity_alerts(prediction)
        for alert in alerts:
            print(f"Alert: {alert.message}")
    
    asyncio.run(example())
