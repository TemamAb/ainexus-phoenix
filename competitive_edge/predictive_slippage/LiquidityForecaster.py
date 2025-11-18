"""
Advanced Liquidity Forecasting Engine
Predicts liquidity across DEXs and CEXs to optimize trade execution
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MarketRegime(Enum):
    NORMAL = "normal"
    VOLATILE = "volatile"
    CRISIS = "crisis"
    CALM = "calm"

@dataclass
class LiquidityForecast:
    timestamp: datetime
    asset_pair: str
    predicted_depth: float
    confidence_interval: Tuple[float, float]
    regime: MarketRegime
    features: Dict[str, float]
    model_version: str

class LiquidityForecaster:
    """
    Advanced liquidity forecasting using machine learning and market microstructure
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.models = {}
        self.scalers = {}
        self.feature_history = {}
        self.forecast_cache = {}
        
        # Initialize models for major asset pairs
        self.supported_pairs = ['ETH-USDT', 'BTC-USDT', 'ETH-BTC', 'SOL-USDT']
        self._initialize_models()
    
    def _setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _initialize_models(self):
        """Initialize ML models for each asset pair"""
        for pair in self.supported_pairs:
            self.models[pair] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.scalers[pair] = StandardScaler()
            
            # Initialize with dummy data for cold start
            self._initialize_with_historical_data(pair)
    
    def _initialize_with_historical_data(self, pair: str):
        """Initialize model with historical liquidity patterns"""
        # In production, this would load real historical data
        # For now, we create synthetic training data
        n_samples = 1000
        X_train = np.random.randn(n_samples, 8)  # 8 features
        y_train = np.random.exponential(2, n_samples)  # Liquidity depth
        
        self.scalers[pair].fit(X_train)
        X_scaled = self.scalers[pair].transform(X_train)
        self.models[pair].fit(X_scaled, y_train)
        
        self.logger.info(f"Initialized model for {pair}")
    
    async def forecast_liquidity(self, asset_pair: str, 
                               features: Optional[Dict] = None,
                               horizon_minutes: int = 30) -> LiquidityForecast:
        """
        Forecast liquidity for a given asset pair
        
        Args:
            asset_pair: Trading pair (e.g., 'ETH-USDT')
            features: Optional feature overrides
            horizon_minutes: Forecast horizon in minutes
            
        Returns:
            LiquidityForecast object
        """
        if asset_pair not in self.supported_pairs:
            raise ValueError(f"Unsupported asset pair: {asset_pair}")
        
        # Generate or use provided features
        if features is None:
            features = await self._collect_market_features(asset_pair)
        
        # Add temporal features
        features.update(self._get_temporal_features())
        
        # Prepare feature vector
        feature_vector = self._create_feature_vector(features, asset_pair)
        
        # Make prediction
        prediction, confidence = self._predict_with_confidence(
            asset_pair, feature_vector
        )
        
        # Determine market regime
        regime = self._determine_market_regime(features, prediction)
        
        forecast = LiquidityForecast(
            timestamp=datetime.now(),
            asset_pair=asset_pair,
            predicted_depth=prediction,
            confidence_interval=confidence,
            regime=regime,
            features=features,
            model_version="1.0"
        )
        
        # Cache forecast
        cache_key = f"{asset_pair}_{horizon_minutes}"
        self.forecast_cache[cache_key] = forecast
        
        self.logger.info(f"Forecast for {asset_pair}: {prediction:.2f} ({regime.value})")
        
        return forecast
    
    async def _collect_market_features(self, asset_pair: str) -> Dict[str, float]:
        """Collect real-time market features for forecasting"""
        # In production, this would fetch real market data
        # For now, we simulate feature collection
        
        features = {
            'volatility_5m': np.random.uniform(0.01, 0.05),
            'volatility_1h': np.random.uniform(0.02, 0.08),
            'volume_24h': np.random.uniform(1000000, 50000000),
            'bid_ask_spread': np.random.uniform(0.0001, 0.002),
            'order_book_imbalance': np.random.uniform(-0.5, 0.5),
            'market_depth_5': np.random.uniform(50000, 500000),
            'price_momentum': np.random.uniform(-0.1, 0.1),
            'funding_rate': np.random.uniform(-0.001, 0.001)
        }
        
        # Add some correlation structure
        features['volatility_1h'] = max(features['volatility_5m'] * 1.5, 
                                      features['volatility_1h'])
        
        return features
    
    def _get_temporal_features(self) -> Dict[str, float]:
        """Get time-based features"""
        now = datetime.now()
        
        return {
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'is_weekend': 1 if now.weekday() >= 5 else 0,
            'is_london_open': 1 if 8 <= now.hour <= 16 else 0,
            'is_ny_open': 1 if 13 <= now.hour <= 21 else 0,
            'is_asia_open': 1 if 0 <= now.hour <= 8 else 0
        }
    
    def _create_feature_vector(self, features: Dict, asset_pair: str) -> np.ndarray:
        """Create normalized feature vector for model prediction"""
        feature_names = [
            'volatility_5m', 'volatility_1h', 'volume_24h', 'bid_ask_spread',
            'order_book_imbalance', 'market_depth_5', 'price_momentum', 'funding_rate',
            'hour_of_day', 'day_of_week', 'is_weekend', 'is_london_open',
            'is_ny_open', 'is_asia_open'
        ]
        
        vector = np.array([features.get(name, 0) for name in feature_names])
        vector = vector.reshape(1, -1)
        
        # Scale features
        return self.scalers[asset_pair].transform(vector)
    
    def _predict_with_confidence(self, asset_pair: str, 
                               feature_vector: np.ndarray) -> Tuple[float, Tuple[float, float]]:
        """Make prediction with confidence intervals"""
        model = self.models[asset_pair]
        
        # Get predictions from all trees
        predictions = []
        for tree in model.estimators_:
            pred = tree.predict(feature_vector)[0]
            predictions.append(pred)
        
        mean_prediction = np.mean(predictions)
        std_prediction = np.std(predictions)
        
        # 95% confidence interval
        confidence_interval = (
            max(0, mean_prediction - 1.96 * std_prediction),
            mean_prediction + 1.96 * std_prediction
        )
        
        return mean_prediction, confidence_interval
    
    def _determine_market_regime(self, features: Dict, 
                               prediction: float) -> MarketRegime:
        """Determine current market regime based on features and prediction"""
        volatility = features['volatility_1h']
        volume = features['volume_24h']
        spread = features['bid_ask_spread']
        
        if volatility > 0.06:
            return MarketRegime.CRISIS
        elif volatility > 0.03:
            return MarketRegime.VOLATILE
        elif volatility < 0.01 and spread < 0.0005:
            return MarketRegime.CALM
        else:
            return MarketRegime.NORMAL
    
    async def batch_forecast(self, asset_pairs: List[str],
                           horizon_minutes: int = 30) -> Dict[str, LiquidityForecast]:
        """Forecast liquidity for multiple asset pairs"""
        forecasts = {}
        
        tasks = []
        for pair in asset_pairs:
            if pair in self.supported_pairs:
                task = self.forecast_liquidity(pair, horizon_minutes=horizon_minutes)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for pair, forecast in zip(asset_pairs, results):
            if not isinstance(forecast, Exception):
                forecasts[pair] = forecast
        
        return forecasts
    
    def get_optimal_trade_size(self, asset_pair: str, 
                             max_slippage: float = 0.001) -> float:
        """
        Calculate optimal trade size given max acceptable slippage
        
        Args:
            asset_pair: Trading pair
            max_slippage: Maximum acceptable slippage (0.1% default)
            
        Returns:
            Optimal trade size in base asset
        """
        # Get latest forecast
        cache_key = f"{asset_pair}_30"
        if cache_key not in self.forecast_cache:
            raise ValueError(f"No forecast available for {asset_pair}")
        
        forecast = self.forecast_cache[cache_key]
        
        # Simplified optimal size calculation
        # In production, this would use more sophisticated market impact models
        optimal_size = forecast.predicted_depth * max_slippage * 0.1
        
        self.logger.info(f"Optimal trade size for {asset_pair}: {optimal_size:.4f}")
        
        return optimal_size
    
    def calculate_slippage_estimate(self, asset_pair: str, 
                                  trade_size: float) -> float:
        """
        Estimate slippage for a given trade size
        
        Args:
            asset_pair: Trading pair
            trade_size: Proposed trade size
            
        Returns:
            Estimated slippage as percentage
        """
        cache_key = f"{asset_pair}_30"
        if cache_key not in self.forecast_cache:
            raise ValueError(f"No forecast available for {asset_pair}")
        
        forecast = self.forecast_cache[cache_key]
        
        # Simple power-law market impact model
        # impact = k * (size/depth)^alpha
        k = 0.1  # Impact coefficient
        alpha = 0.5  # Square root model
        
        normalized_size = trade_size / forecast.predicted_depth
        slippage = k * (normalized_size ** alpha)
        
        self.logger.info(f"Estimated slippage for {trade_size:.4f} {asset_pair}: {slippage:.4%}")
        
        return slippage
    
    async def monitor_liquidity_regime_changes(self) -> Dict[str, MarketRegime]:
        """Monitor for liquidity regime changes across all pairs"""
        regime_changes = {}
        
        forecasts = await self.batch_forecast(self.supported_pairs)
        
        for pair, forecast in forecasts.items():
            cache_key = f"{pair}_30"
            previous_forecast = self.forecast_cache.get(cache_key)
            
            if previous_forecast and previous_forecast.regime != forecast.regime:
                regime_changes[pair] = {
                    'from': previous_forecast.regime,
                    'to': forecast.regime,
                    'timestamp': forecast.timestamp
                }
                self.logger.warning(
                    f"Regime change for {pair}: {previous_forecast.regime.value} -> {forecast.regime.value}"
                )
        
        return regime_changes
    
    def get_forecast_accuracy(self, asset_pair: str, 
                            lookback_days: int = 7) -> Dict[str, float]:
        """
        Calculate forecast accuracy metrics
        
        Args:
            asset_pair: Trading pair to analyze
            lookback_days: Number of days to look back
            
        Returns:
            Dictionary of accuracy metrics
        """
        # In production, this would compare forecasts with actual liquidity
        # For now, return placeholder metrics
        return {
            'mae': 0.15,  # Mean Absolute Error
            'rmse': 0.22,  # Root Mean Square Error
            'r_squared': 0.78,
            'direction_accuracy': 0.82  # % of correct regime predictions
        }

# Example usage and simulation
async def main():
    """Demo the liquidity forecaster"""
    forecaster = LiquidityForecaster()
    
    print("🧠 Liquidity Forecasting Engine Started")
    print("=" * 50)
    
    # Single forecast
    eth_forecast = await forecaster.forecast_liquidity('ETH-USDT')
    print(f"ETH-USDT Forecast: {eth_forecast.predicted_depth:,.2f}")
    print(f"Confidence: {eth_forecast.confidence_interval}")
    print(f"Regime: {eth_forecast.regime.value}")
    
    print("\n" + "=" * 50)
    
    # Batch forecast
    all_forecasts = await forecaster.batch_forecast(['BTC-USDT', 'ETH-USDT', 'SOL-USDT'])
    
    for pair, forecast in all_forecasts.items():
        print(f"{pair}: {forecast.predicted_depth:,.2f} ({forecast.regime.value})")
    
    print("\n" + "=" * 50)
    
    # Trade size optimization
    optimal_size = forecaster.get_optimal_trade_size('ETH-USDT', max_slippage=0.001)
    print(f"Optimal ETH trade size: {optimal_size:.4f} ETH")
    
    # Slippage estimation
    slippage = forecaster.calculate_slippage_estimate('ETH-USDT', trade_size=100)
    print(f"Slippage for 100 ETH: {slippage:.4%}")
    
    # Monitor regime changes
    regime_changes = await forecaster.monitor_liquidity_regime_changes()
    if regime_changes:
        print(f"Regime changes detected: {len(regime_changes)}")
    else:
        print("No regime changes detected")

if __name__ == "__main__":
    asyncio.run(main())