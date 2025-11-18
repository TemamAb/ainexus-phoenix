"""
AI-NEXUS v5.0 - DETECTION AGENT MODULE
Advanced Anomaly and Pattern Detection Agent
Real-time market anomaly detection and pattern recognition
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import asyncio
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class DetectionType(Enum):
    ANOMALY = "anomaly"
    PATTERN = "pattern"
    REGIME_CHANGE = "regime_change"
    STRUCTURAL_BREAK = "structural_break"
    OUTLIER = "outlier"

class PatternCategory(Enum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    BEHAVIORAL = "behavioral"
    STATISTICAL = "statistical"
    TEMPORAL = "temporal"

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class DetectionInput:
    input_id: str
    timestamp: datetime
    data_type: str
    data: pd.DataFrame
    metadata: Dict[str, Any]

@dataclass
class DetectionResult:
    detection_id: str
    timestamp: datetime
    detection_type: DetectionType
    pattern_category: PatternCategory
    confidence: float
    severity: float
    description: str
    location: Tuple[float, float]  # (time_index, value_index)
    features: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class PatternSignature:
    pattern_id: str
    category: PatternCategory
    signature_vector: np.ndarray
    frequency: float
    persistence: float
    metadata: Dict[str, Any]

class DetectionAgent:
    """
    Advanced detection agent for market anomalies and patterns
    Multi-modal detection using statistical, ML, and temporal methods
    """
    
    def __init__(self, agent_id: str, detection_capabilities: List[DetectionType]):
        self.agent_id = agent_id
        self.detection_capabilities = detection_capabilities
        
        # Detection history and patterns
        self.detection_history = deque(maxlen=10000)
        self.pattern_library = {}
        self.anomaly_thresholds = {}
        
        # Statistical parameters
        self.statistical_params = {
            'z_score_threshold': 3.0,
            'rolling_window': 100,
            'volatility_lookback': 20,
            'correlation_threshold': 0.8
        }
        
        # ML detection parameters
        self.ml_params = {
            'isolation_forest_contamination': 0.1,
            'autoencoder_threshold': 0.95,
            'cluster_outlier_fraction': 0.05
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_detections': 0,
            'true_positives': 0,
            'false_positives': 0,
            'detection_accuracy': 0.0,
            'avg_confidence': 0.0
        }
        
        # Initialize detection engines
        self._initialize_detection_engines()
        self._initialize_pattern_library()
    
    def _initialize_detection_engines(self):
        """Initialize various detection engines"""
        
        self.detection_engines = {
            DetectionType.ANOMALY: {
                'methods': ['statistical', 'ml', 'temporal'],
                'engines': [
                    StatisticalAnomalyDetector(self.statistical_params),
                    MLAnomalyDetector(self.ml_params),
                    TemporalAnomalyDetector()
                ]
            },
            DetectionType.PATTERN: {
                'methods': ['technical', 'statistical', 'behavioral'],
                'engines': [
                    TechnicalPatternDetector(),
                    StatisticalPatternDetector(),
                    BehavioralPatternDetector()
                ]
            },
            DetectionType.REGIME_CHANGE: {
                'methods': ['markov', 'volatility', 'correlation'],
                'engines': [
                    RegimeChangeDetector(),
                    VolatilityRegimeDetector(),
                    CorrelationRegimeDetector()
                ]
            },
            DetectionType.STRUCTURAL_BREAK: {
                'methods': ['chow_test', 'cusum', 'bai_perron'],
                'engines': [
                    StructuralBreakDetector(),
                    CUSUMDetector(),
                    BaiPerronDetector()
                ]
            }
        }
    
    def _initialize_pattern_library(self):
        """Initialize pattern library with common market patterns"""
        
        # Technical patterns
        self.pattern_library['head_shoulders'] = PatternSignature(
            pattern_id='head_shoulders',
            category=PatternCategory.TECHNICAL,
            signature_vector=np.array([1, 2, 1, -1, -2, -1]),  # Simplified pattern
            frequency=0.05,
            persistence=0.7,
            metadata={'complexity': 'high', 'reliability': 0.6}
        )
        
        self.pattern_library['double_top'] = PatternSignature(
            pattern_id='double_top',
            category=PatternCategory.TECHNICAL,
            signature_vector=np.array([1, 0, 1, -1, 0, -1]),
            frequency=0.08,
            persistence=0.6,
            metadata={'complexity': 'medium', 'reliability': 0.5}
        )
        
        # Statistical patterns
        self.pattern_library['mean_reversion'] = PatternSignature(
            pattern_id='mean_reversion',
            category=PatternCategory.STATISTICAL,
            signature_vector=np.array([0.1, -0.1, 0.05, -0.05]),
            frequency=0.15,
            persistence=0.8,
            metadata={'complexity': 'low', 'reliability': 0.7}
        )
    
    async def analyze_market_data(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Analyze market data for various detections"""
        
        results = []
        
        # Run detection for each capability
        for detection_type in self.detection_capabilities:
            if detection_type in self.detection_engines:
                detection_results = await self._run_detection_engine(
                    detection_type, input_data
                )
                results.extend(detection_results)
        
        # Update performance metrics
        self.performance_metrics['total_detections'] += len(results)
        if results:
            self.performance_metrics['avg_confidence'] = np.mean([r.confidence for r in results])
        
        # Store results in history
        for result in results:
            self.detection_history.append(result)
        
        print(f"Detection completed: {len(results)} findings")
        
        return results
    
    async def _run_detection_engine(self, detection_type: DetectionType, 
                                  input_data: DetectionInput) -> List[DetectionResult]:
        """Run specific detection engine"""
        
        engine_config = self.detection_engines[detection_type]
        all_results = []
        
        for engine in engine_config['engines']:
            try:
                results = await engine.detect(input_data)
                all_results.extend(results)
            except Exception as e:
                print(f"Detection engine {engine.__class__.__name__} failed: {e}")
        
        return all_results
    
    async def detect_anomalies(self, price_data: pd.DataFrame, 
                             volume_data: pd.DataFrame = None) -> List[DetectionResult]:
        """Specialized anomaly detection"""
        
        input_data = DetectionInput(
            input_id=f"anomaly_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            data_type='price_volume',
            data=price_data,
            metadata={'volume_data': volume_data} if volume_data is not None else {}
        )
        
        return await self.analyze_market_data(input_data)
    
    async def detect_patterns(self, price_data: pd.DataFrame, 
                            pattern_categories: List[PatternCategory] = None) -> List[DetectionResult]:
        """Specialized pattern detection"""
        
        if pattern_categories is None:
            pattern_categories = [PatternCategory.TECHNICAL, PatternCategory.STATISTICAL]
        
        input_data = DetectionInput(
            input_id=f"pattern_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            data_type='price_patterns',
            data=price_data,
            metadata={'pattern_categories': pattern_categories}
        )
        
        return await self.analyze_market_data(input_data)
    
    async def detect_regime_changes(self, market_data: pd.DataFrame) -> List[DetectionResult]:
        """Specialized regime change detection"""
        
        input_data = DetectionInput(
            input_id=f"regime_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            data_type='market_regime',
            data=market_data,
            metadata={'features': ['volatility', 'correlation', 'momentum']}
        )
        
        return await self.analyze_market_data(input_data)
    
    def update_detection_thresholds(self, new_thresholds: Dict[str, float]):
        """Update detection thresholds based on performance"""
        
        self.anomaly_thresholds.update(new_thresholds)
        print("Updated detection thresholds")
    
    async def learn_new_pattern(self, pattern_data: pd.DataFrame, 
                              category: PatternCategory, 
                              metadata: Dict[str, Any] = None) -> PatternSignature:
        """Learn new pattern from data"""
        
        # Extract pattern signature
        signature = await self._extract_pattern_signature(pattern_data)
        
        # Create pattern signature
        pattern_id = f"pattern_{category.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        pattern_sig = PatternSignature(
            pattern_id=pattern_id,
            category=category,
            signature_vector=signature,
            frequency=0.1,  # Initial frequency
            persistence=0.5,  # Initial persistence
            metadata=metadata or {}
        )
        
        # Add to pattern library
        self.pattern_library[pattern_id] = pattern_sig
        
        print(f"Learned new pattern: {pattern_id}")
        
        return pattern_sig
    
    async def _extract_pattern_signature(self, pattern_data: pd.DataFrame) -> np.ndarray:
        """Extract pattern signature from data"""
        
        # Simple signature extraction using PCA and feature engineering
        # In production, this would use more sophisticated methods
        
        # Normalize data
        normalized_data = (pattern_data - pattern_data.mean()) / pattern_data.std()
        
        # Extract key features
        features = []
        
        # Trend features
        features.append(normalized_data.iloc[-1] - normalized_data.iloc[0])  # Overall trend
        features.append(normalized_data.max() - normalized_data.min())  # Range
        features.append(normalized_data.std())  # Volatility
        
        # Pattern shape features
        features.append(self._calculate_curvature(normalized_data))
        features.append(self._calculate_autocorrelation(normalized_data))
        
        return np.array(features)
    
    def _calculate_curvature(self, data: pd.DataFrame) -> float:
        """Calculate curvature of pattern"""
        
        if len(data) < 3:
            return 0.0
        
        # Simple curvature calculation
        x = np.arange(len(data))
        y = data.values.flatten()
        
        # Second derivative approximation
        if len(y) >= 3:
            curvature = np.abs(y[2:] - 2*y[1:-1] + y[:-2]).mean()
            return curvature
        else:
            return 0.0
    
    def _calculate_autocorrelation(self, data: pd.DataFrame, lag: int = 1) -> float:
        """Calculate autocorrelation at given lag"""
        
        if len(data) <= lag:
            return 0.0
        
        series = data.values.flatten()
        return np.corrcoef(series[:-lag], series[lag:])[0, 1]
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection statistics and performance"""
        
        recent_detections = list(self.detection_history)[-100:]  # Last 100 detections
        
        type_counts = defaultdict(int)
        confidence_levels = []
        severity_levels = []
        
        for detection in recent_detections:
            type_counts[detection.detection_type.value] += 1
            confidence_levels.append(detection.confidence)
            severity_levels.append(detection.severity)
        
        return {
            'agent_id': self.agent_id,
            'total_patterns_learned': len(self.pattern_library),
            'recent_detection_types': dict(type_counts),
            'avg_confidence': np.mean(confidence_levels) if confidence_levels else 0.0,
            'avg_severity': np.mean(severity_levels) if severity_levels else 0.0,
            'performance_metrics': self.performance_metrics
        }
    
    def validate_detection(self, detection_id: str, is_valid: bool):
        """Validate detection result for learning"""
        
        # Find detection in history
        detection = None
        for d in self.detection_history:
            if d.detection_id == detection_id:
                detection = d
                break
        
        if detection:
            if is_valid:
                self.performance_metrics['true_positives'] += 1
            else:
                self.performance_metrics['false_positives'] += 1
            
            # Update accuracy
            total_validated = self.performance_metrics['true_positives'] + self.performance_metrics['false_positives']
            if total_validated > 0:
                self.performance_metrics['detection_accuracy'] = (
                    self.performance_metrics['true_positives'] / total_validated
                )
            
            print(f"Detection {detection_id} validated as {'true' if is_valid else 'false'} positive")

# Detection Engine Implementations
class StatisticalAnomalyDetector:
    """Statistical methods for anomaly detection"""
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
    
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Detect anomalies using statistical methods"""
        
        data = input_data.data
        results = []
        
        # Z-score based anomaly detection
        z_scores = np.abs(stats.zscore(data))
        anomaly_indices = np.where(z_scores > self.params['z_score_threshold'])[0]
        
        for idx in anomaly_indices:
            result = DetectionResult(
                detection_id=f"stat_anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}",
                timestamp=datetime.now(),
                detection_type=DetectionType.ANOMALY,
                pattern_category=PatternCategory.STATISTICAL,
                confidence=min(1.0, z_scores[idx] / 5.0),  # Normalize to 0-1
                severity=min(1.0, z_scores[idx] / 10.0),
                description=f"Statistical anomaly detected at index {idx}",
                location=(idx, data.iloc[idx].values[0]),
                features={'z_score': z_scores[idx], 'method': 'z_score'},
                metadata={'detector': 'statistical_zscore'}
            )
            results.append(result)
        
        return results

class MLAnomalyDetector:
    """Machine learning based anomaly detection"""
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
    
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Detect anomalies using ML methods"""
        
        # Simplified ML anomaly detection
        # In production, this would use actual ML models
        
        data = input_data.data
        results = []
        
        # Simple rolling window anomaly detection
        window = 20
        if len(data) > window:
            rolling_mean = data.rolling(window=window).mean()
            rolling_std = data.rolling(window=window).std()
            
            # Find points outside 2 standard deviations
            upper_bound = rolling_mean + 2 * rolling_std
            lower_bound = rolling_mean - 2 * rolling_std
            
            anomalies = (data > upper_bound) | (data < lower_bound)
            anomaly_indices = anomalies[anomalies].index
            
            for idx in anomaly_indices:
                deviation = abs(data.loc[idx] - rolling_mean.loc[idx]).values[0]
                severity = min(1.0, deviation / (2 * rolling_std.loc[idx].values[0]))
                
                result = DetectionResult(
                    detection_id=f"ml_anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}",
                    timestamp=datetime.now(),
                    detection_type=DetectionType.ANOMALY,
                    pattern_category=PatternCategory.STATISTICAL,
                    confidence=0.7,
                    severity=severity,
                    description=f"ML-based anomaly detected at index {idx}",
                    location=(idx, data.loc[idx].values[0]),
                    features={'deviation': deviation, 'method': 'rolling_std'},
                    metadata={'detector': 'ml_rolling_std'}
                )
                results.append(result)
        
        return results

class TechnicalPatternDetector:
    """Technical pattern detection"""
    
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Detect technical patterns"""
        
        data = input_data.data
        results = []
        
        # Simplified technical pattern detection
        # In production, this would use sophisticated pattern recognition
        
        # Detect simple patterns like peaks and troughs
        from scipy.signal import find_peaks
        
        values = data.values.flatten()
        
        # Find peaks
        peaks, _ = find_peaks(values, prominence=0.1)
        
        for peak_idx in peaks:
            result = DetectionResult(
                detection_id=f"tech_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{peak_idx}",
                timestamp=datetime.now(),
                detection_type=DetectionType.PATTERN,
                pattern_category=PatternCategory.TECHNICAL,
                confidence=0.6,
                severity=0.3,
                description=f"Technical pattern: Peak detected at index {peak_idx}",
                location=(peak_idx, values[peak_idx]),
                features={'pattern_type': 'peak', 'prominence': 0.1},
                metadata={'detector': 'technical_peak'}
            )
            results.append(result)
        
        # Find troughs
        troughs, _ = find_peaks(-values, prominence=0.1)
        
        for trough_idx in troughs:
            result = DetectionResult(
                detection_id=f"tech_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trough_idx}",
                timestamp=datetime.now(),
                detection_type=DetectionType.PATTERN,
                pattern_category=PatternCategory.TECHNICAL,
                confidence=0.6,
                severity=0.3,
                description=f"Technical pattern: Trough detected at index {trough_idx}",
                location=(trough_idx, values[trough_idx]),
                features={'pattern_type': 'trough', 'prominence': 0.1},
                metadata={'detector': 'technical_trough'}
            )
            results.append(result)
        
        return results

# Additional detector classes would be implemented similarly
class TemporalAnomalyDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []  # Implementation would go here

class StatisticalPatternDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

class BehavioralPatternDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

class RegimeChangeDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

class VolatilityRegimeDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

class CorrelationRegimeDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

class StructuralBreakDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

class CUSUMDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

class BaiPerronDetector:
    async def detect(self, input_data: DetectionInput) -> List[DetectionResult]:
        return []

# Example usage
if __name__ == "__main__":
    # Create detection agent
    agent = DetectionAgent(
        agent_id="market_detection_agent_1",
        detection_capabilities=[DetectionType.ANOMALY, DetectionType.PATTERN, DetectionType.REGIME_CHANGE]
    )
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='1min')
    np.random.seed(42)
    
    # Create sample price data with some anomalies
    base_trend = np.linspace(100, 110, 1000)
    noise = np.random.normal(0, 0.5, 1000)
    prices = base_trend + noise
    
    # Add some anomalies
    prices[500] += 5  # Large positive anomaly
    prices[750] -= 4  # Large negative anomaly
    
    price_data = pd.DataFrame(prices, index=dates, columns=['price'])
    
    async def demo():
        # Detect anomalies
        anomalies = await agent.detect_anomalies(price_data)
        
        print(f"Detected {len(anomalies)} anomalies")
        for anomaly in anomalies[:3]:  # Show first 3
            print(f"Anomaly: {anomaly.description}, Confidence: {anomaly.confidence:.3f}")
        
        # Detect patterns
        patterns = await agent.detect_patterns(price_data)
        
        print(f"Detected {len(patterns)} patterns")
        
        # Get statistics
        stats = agent.get_detection_statistics()
        print(f"Detection Statistics: {stats}")
    
    import asyncio
    asyncio.run(demo())
