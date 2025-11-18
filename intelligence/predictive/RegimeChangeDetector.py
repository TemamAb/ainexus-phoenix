#!/usr/bin/env python3
"""
AI-NEXUS Regime Change Detector
Market regime detection and transition forecasting
"""

import numpy as np
from sklearn.ensemble import IsolationForest

class RegimeChangeDetector:
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.regime_history = []
        self.anomaly_detector = IsolationForest(contamination=0.1)
        
    def detect_regime_change(self, market_features: np.ndarray) -> bool:
        """Detect if market regime has changed"""
        if len(self.regime_history) < self.window_size:
            self.regime_history.append(market_features)
            return False
        
        # Check for anomalies indicating regime change
        is_anomaly = self.anomaly_detector.fit_predict([market_features])[0] == -1
        
        if not is_anomaly:
            self.regime_history.append(market_features)
            # Keep only recent history
            if len(self.regime_history) > self.window_size * 2:
                self.regime_history = self.regime_history[-self.window_size:]
        
        return is_anomaly
    
    def get_current_regime_stability(self) -> float:
        """Calculate stability of current regime"""
        if len(self.regime_history) < 10:
            return 1.0
        
        recent_data = np.array(self.regime_history[-10:])
        volatility = np.std(recent_data, axis=0).mean()
        
        # Convert to stability score (higher = more stable)
        stability = 1.0 / (1.0 + volatility)
        return min(stability, 1.0)
