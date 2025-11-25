"""
QUANTUMNEX v1.0 - DETECTION AGENT
Advanced Anomaly and Pattern Detection Agent
Real-time market anomaly detection and pattern recognition
"""

import numpy as np
import pandas as pd
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class DetectionType(Enum):
    ANOMALY = "anomaly"
    PATTERN = "pattern"
    REGIME_CHANGE = "regime_change"
    ARBITRAGE_OPPORTUNITY = "arbitrage_opportunity"

class PatternCategory(Enum):
    TECHNICAL = "technical"
    STATISTICAL = "statistical"
    BEHAVIORAL = "behavioral"

@dataclass
class DetectionInput:
    input_id: str
    timestamp: datetime
    data_type: str
    data: Dict[str, Any]
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
    location: Tuple[str, str]  # (symbol, exchange)
    features: Dict[str, float]
    metadata: Dict[str, Any]

class DetectionAgent:
    """
    Advanced detection agent for market anomalies and patterns
    Multi-modal detection using statistical and ML methods
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.detection_history = deque(maxlen=10000)
        self.performance_metrics = {
            'detections_made': 0,
            'true_positives': 0,
            'false_positives': 0,
            'detection_accuracy': 0.0
        }
        
        # Detection parameters
        self.detection_params = {
            'z_score_threshold': 3.0,
            'volatility_threshold': 0.15,
            'price_deviation_threshold': 0.02,
            'min_confidence': 0.6
        }
        
        # Pattern library
        self.pattern_library = self._initialize_pattern_library()
        
        print(f"âœ… Detection Agent {agent_id} initialized")

    def _initialize_pattern_library(self) -> Dict[str, Any]:
        """Initialize pattern library with common market patterns"""
        return {
            'flash_crash': {
                'description': 'Rapid price decline and recovery',
                'thresholds': {'price_drop': 0.05, 'recovery_time': 300},
                'confidence_weight': 0.8
            },
            'liquidity_spike': {
                'description': 'Sudden increase in trading volume',
                'thresholds': {'volume_increase': 3.0, 'duration': 60},
                'confidence_weight': 0.7
            },
            'arbitrage_opportunity': {
                'description': 'Price discrepancy between exchanges',
                'thresholds': {'price_diff': 0.005, 'liquidity_min': 10000},
                'confidence_weight': 0.9
            },
            'regime_change': {
                'description': 'Market regime transition',
                'thresholds': {'volatility_change': 0.1, 'correlation_break': 0.3},
                'confidence_weight': 0.6
            }
        }

    async def analyze_market_data(self, input_data: DetectionInput) -> List[DetectionResult]:
        """
        Analyze market data for various detections
        """
        print(f"í´ Detection Agent analyzing: {input_data.input_id}")
        
        results = []
        
        # Run multiple detection methods
        detection_methods = [
            self._detect_price_anomalies,
            self._detect_arbitrage_opportunities,
            self._detect_regime_changes,
            self._detect_liquidity_patterns
        ]
        
        for method in detection_methods:
            try:
                method_results = await method(input_data)
                results.extend(method_results)
            except Exception as e:
                print(f"Detection method {method.__name__} failed: {e}")
        
        # Update performance metrics
        self.performance_metrics['detections_made'] += len(results)
        
        # Store results in history
        for result in results:
            self.detection_history.append(result)
        
        print(f"âœ… Detection completed: {len(results)} findings")
        
        return results

    async def _detect_price_anomalies(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Detect price anomalies using statistical methods"""
        results = []
        price_data = input_data.data.get('prices', {})
        
        for symbol, exchanges in price_data.items():
            for exchange, price_info in exchanges.items():
                price = price_info.get('price')
                timestamp = price_info.get('timestamp')
                
                if not price or not timestamp:
                    continue
                
                # Calculate price deviation from recent average
                deviation = await self._calculate_price_deviation(symbol, exchange, price)
                
                if abs(deviation) > self.detection_params['price_deviation_threshold']:
                    result = DetectionResult(
                        detection_id=f"anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        timestamp=datetime.now(),
                        detection_type=DetectionType.ANOMALY,
                        pattern_category=PatternCategory.STATISTICAL,
                        confidence=min(0.95, abs(deviation) * 10),
                        severity=min(1.0, abs(deviation) * 5),
                        description=f"Price anomaly detected for {symbol} on {exchange}",
                        location=(symbol, exchange),
                        features={
                            'price_deviation': deviation,
                            'current_price': price,
                            'z_score': await self._calculate_z_score(symbol, exchange, price)
                        },
                        metadata={'detection_method': 'price_anomaly'}
                    )
                    results.append(result)
        
        return results

    async def _detect_arbitrage_opportunities(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Detect arbitrage opportunities across exchanges"""
        results = []
        price_data = input_data.data.get('prices', {})
        
        for symbol, exchanges in price_data.items():
            exchange_prices = {}
            
            # Collect prices from all exchanges
            for exchange, price_info in exchanges.items():
                price = price_info.get('price')
                liquidity = price_info.get('liquidity', 0)
                
                if price and liquidity > 5000:  # Minimum liquidity threshold
                    exchange_prices[exchange] = price
            
            # Find price discrepancies
            if len(exchange_prices) >= 2:
                opportunities = await self._find_arbitrage_opportunities(symbol, exchange_prices)
                results.extend(opportunities)
        
        return results

    async def _detect_regime_changes(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Detect market regime changes"""
        results = []
        volatility_data = input_data.data.get('volatility', {})
        
        for symbol, volatility_info in volatility_data.items():
            current_volatility = volatility_info.get('current', 0)
            historical_volatility = volatility_info.get('historical', 0)
            
            if current_volatility and historical_volatility:
                volatility_change = abs(current_volatility - historical_volatility) / historical_volatility
                
                if volatility_change > self.detection_params['volatility_threshold']:
                    result = DetectionResult(
                        detection_id=f"regime_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        timestamp=datetime.now(),
                        detection_type=DetectionType.REGIME_CHANGE,
                        pattern_category=PatternCategory.STATISTICAL,
                        confidence=min(0.9, volatility_change * 3),
                        severity=min(1.0, volatility_change * 2),
                        description=f"Market regime change detected for {symbol}",
                        location=(symbol, 'global'),
                        features={
                            'volatility_change': volatility_change,
                            'current_volatility': current_volatility,
                            'historical_volatility': historical_volatility
                        },
                        metadata={'detection_method': 'regime_change'}
                    )
                    results.append(result)
        
        return results

    async def _detect_liquidity_patterns(self, input_data: DetectionInput) -> List[DetectionResult]:
        """Detect unusual liquidity patterns"""
        results = []
        liquidity_data = input_data.data.get('liquidity', {})
        
        for symbol, exchanges in liquidity_data.items():
            for exchange, liquidity_info in exchanges.items():
                current_liquidity = liquidity_info.get('current', 0)
                avg_liquidity = liquidity_info.get('average', 0)
                
                if current_liquidity and avg_liquidity:
                    liquidity_ratio = current_liquidity / avg_liquidity if avg_liquidity > 0 else 1.0
                    
                    # Detect liquidity spikes
                    if liquidity_ratio > 3.0:
                        result = DetectionResult(
                            detection_id=f"liquidity_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            timestamp=datetime.now(),
                            detection_type=DetectionType.PATTERN,
                            pattern_category=PatternCategory.BEHAVIORAL,
                            confidence=min(0.85, (liquidity_ratio - 1) * 0.5),
                            severity=min(1.0, (liquidity_ratio - 1) * 0.3),
                            description=f"Liquidity spike detected for {symbol} on {exchange}",
                            location=(symbol, exchange),
                            features={
                                'liquidity_ratio': liquidity_ratio,
                                'current_liquidity': current_liquidity,
                                'average_liquidity': avg_liquidity
                            },
                            metadata={'detection_method': 'liquidity_pattern'}
                        )
                        results.append(result)
        
        return results

    async def _find_arbitrage_opportunities(self, symbol: str, exchange_prices: Dict[str, float]) -> List[DetectionResult]:
        """Find arbitrage opportunities between exchanges"""
        results = []
        exchanges = list(exchange_prices.keys())
        
        # Compare all exchange combinations
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                dex1, dex2 = exchanges[i], exchanges[j]
                price1, price2 = exchange_prices[dex1], exchange_prices[dex2]
                
                price_diff = abs(price1 - price2)
                price_diff_percent = price_diff / min(price1, price2)
                
                # Check if difference exceeds threshold
                if price_diff_percent > 0.005:  # 0.5% threshold
                    result = DetectionResult(
                        detection_id=f"arbitrage_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        timestamp=datetime.now(),
                        detection_type=DetectionType.ARBITRAGE_OPPORTUNITY,
                        pattern_category=PatternCategory.STATISTICAL,
                        confidence=min(0.95, price_diff_percent * 50),
                        severity=min(1.0, price_diff_percent * 25),
                        description=f"Arbitrage opportunity: {symbol} between {dex1} and {dex2}",
                        location=(symbol, f"{dex1}-{dex2}"),
                        features={
                            'price_difference': price_diff,
                            'price_difference_percent': price_diff_percent,
                            'exchange_a_price': price1,
                            'exchange_b_price': price2,
                            'potential_profit': price_diff_percent * 0.8  # After fees
                        },
                        metadata={
                            'detection_method': 'arbitrage',
                            'exchange_pair': f"{dex1}-{dex2}"
                        }
                    )
                    results.append(result)
        
        return results

    async def _calculate_price_deviation(self, symbol: str, exchange: str, current_price: float) -> float:
        """Calculate price deviation from recent average"""
        # Simulate historical price data retrieval
        await asyncio.sleep(0.001)
        
        # In production, this would use real historical data
        historical_avg = current_price * (0.95 + np.random.random() * 0.1)
        
        deviation = (current_price - historical_avg) / historical_avg
        return deviation

    async def _calculate_z_score(self, symbol: str, exchange: str, current_price: float) -> float:
        """Calculate Z-score for price anomaly detection"""
        # Simulate statistical calculation
        await asyncio.sleep(0.001)
        
        # In production, this would use real statistical models
        mean_price = current_price * (0.98 + np.random.random() * 0.04)
        std_dev = current_price * 0.05  # 5% standard deviation
        
        z_score = (current_price - mean_price) / std_dev if std_dev > 0 else 0
        return z_score

    def validate_detection(self, detection_id: str, is_valid: bool):
        """Validate detection result for learning"""
        detection = next((d for d in self.detection_history if d.detection_id == detection_id), None)
        
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

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and performance"""
        return {
            'agent_id': self.agent_id,
            'performance_metrics': self.performance_metrics,
            'recent_detections': len(self.detection_history),
            'pattern_library_size': len(self.pattern_library),
            'detection_accuracy': self.performance_metrics['detection_accuracy']
        }

# Example usage
async def main():
    """Example usage of Detection Agent"""
    agent = DetectionAgent("quantum_detection_1")
    
    # Create sample input data
    input_data = DetectionInput(
        input_id="market_scan_001",
        timestamp=datetime.now(),
        data_type="price_liquidity",
        data={
            'prices': {
                'ETH/USDC': {
                    'uniswap': {'price': 1800.50, 'liquidity': 15000000, 'timestamp': datetime.now()},
                    'sushiswap': {'price': 1799.80, 'liquidity': 8000000, 'timestamp': datetime.now()}
                }
            },
            'volatility': {
                'ETH/USDC': {'current': 0.22, 'historical': 0.18}
            },
            'liquidity': {
                'ETH/USDC': {
                    'uniswap': {'current': 15000000, 'average': 12000000},
                    'sushiswap': {'current': 8000000, 'average': 7000000}
                }
            }
        },
        metadata={'scan_type': 'comprehensive'}
    )
    
    # Analyze data
    results = await agent.analyze_market_data(input_data)
    
    print(f"Detection Results: {len(results)} findings")
    for result in results[:3]:  # Show first 3 results
        print(f"- {result.description} (Confidence: {result.confidence:.3f})")
    
    # Show agent status
    status = agent.get_agent_status()
    print(f"Agent Status: {status}")

if __name__ == "__main__":
    asyncio.run(main())
