#!/usr/bin/env python3
"""
AI-NEXUS Predictive Arbitrage Oracle
Advanced market movement forecasting with regime detection
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from hmmlearn import hmm
import warnings
warnings.filterwarnings('ignore')

class PredictiveArbOracle:
    def __init__(self, lookback_window: int = 1000):
        self.lookback_window = lookback_window
        self.regime_detector = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
        self.price_predictor = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
        self.volatility_predictor = GradientBoostingRegressor(n_estimators=50, learning_rate=0.1)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.current_regime = 0
        
    def prepare_features(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare technical features for prediction"""
        df = price_data.copy()
        
        # Price features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Volatility features
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['volatility_ratio'] = df['volatility'] / df['volatility'].shift(20)
        
        # Momentum features
        df['momentum'] = df['close'] / df['close'].shift(5) - 1
        df['rsi'] = self.calculate_rsi(df['close'])
        df['macd'] = self.calculate_macd(df['close'])
        
        # Volume features
        if 'volume' in df.columns:
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Market regime features
        df['regime_stability'] = self.calculate_regime_stability(df)
        
        return df.dropna()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate MACD indicator"""
        exp1 = prices.ewm(span=12).mean()
        exp2 = prices.ewm(span=26).mean()
        macd = exp1 - exp2
        return macd
    
    def calculate_regime_stability(self, df: pd.DataFrame) -> pd.Series:
        """Calculate market regime stability metric"""
        # Use volatility and correlation structure
        volatility_regime = df['volatility'].rolling(50).apply(
            lambda x: 0 if x.mean() < 0.01 else 1 if x.mean() < 0.05 else 2
        )
        return volatility_regime
    
    def detect_regime_change(self, features: np.ndarray) -> int:
        """Detect current market regime using HMM"""
        if not hasattr(self.regime_detector, 'means_'):
            # Initialize with simple clustering if not trained
            return np.random.randint(0, 3)
        
        try:
            regime = self.regime_detector.predict(features.reshape(1, -1))[0]
            self.current_regime = regime
            return regime
        except:
            return self.current_regime
    
    def train_models(self, historical_data: pd.DataFrame):
        """Train predictive models on historical data"""
        features_df = self.prepare_features(historical_data)
        features = features_df.drop(['returns', 'log_returns'], axis=1, errors='ignore')
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Train regime detector
        self.regime_detector.fit(scaled_features)
        
        # Prepare targets
        future_returns = features_df['returns'].shift(-5).dropna()
        future_volatility = features_df['volatility'].shift(-5).dropna()
        
        # Align features with targets
        aligned_features = scaled_features[:-5]
        
        # Train predictors
        self.price_predictor.fit(aligned_features, future_returns)
        self.volatility_predictor.fit(aligned_features, future_volatility)
        
        self.is_trained = True
        print("Predictive models trained successfully")
    
    def predict_arbitrage_opportunity(self, current_market_data: dict) -> dict:
        """Predict arbitrage opportunities with confidence scores"""
        if not self.is_trained:
            return {"error": "Models not trained"}
        
        # Convert to DataFrame for feature engineering
        df = pd.DataFrame([current_market_data])
        features_df = self.prepare_features(df)
        
        if features_df.empty:
            return {"error": "Insufficient data for prediction"}
        
        features = features_df.drop(['returns', 'log_returns'], axis=1, errors='ignore')
        scaled_features = self.scaler.transform(features)
        
        # Make predictions
        regime = self.detect_regime_change(scaled_features[0])
        expected_return = self.price_predictor.predict(scaled_features)[0]
        expected_volatility = self.volatility_predictor.predict(scaled_features)[0]
        
        # Calculate opportunity score
        sharpe_ratio = expected_return / (expected_volatility + 1e-8)
        confidence = min(1.0, abs(sharpe_ratio) * 10)
        
        return {
            "regime": regime,
            "expected_return": expected_return,
            "expected_volatility": expected_volatility,
            "sharpe_ratio": sharpe_ratio,
            "confidence": confidence,
            "opportunity_type": self.classify_opportunity(regime, sharpe_ratio),
            "timestamp": pd.Timestamp.now()
        }
    
    def classify_opportunity(self, regime: int, sharpe_ratio: float) -> str:
        """Classify type of arbitrage opportunity"""
        if abs(sharpe_ratio) < 0.5:
            return "NO_OPPORTUNITY"
        
        if regime == 0:  # Low volatility regime
            if sharpe_ratio > 0:
                return "STATISTICAL_ARB"
            else:
                return "MEAN_REVERSION"
        elif regime == 1:  # Medium volatility regime
            if sharpe_ratio > 0:
                return "TRIANGULAR_ARB"
            else:
                return "VOLATILITY_ARB"
        else:  # High volatility regime
            if sharpe_ratio > 0:
                return "FLASH_LOAN_ARB"
            else:
                return "CRISIS_ARB"
