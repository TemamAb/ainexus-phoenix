"""
BEHAVIORAL MODELS AI
REF: Morgan Stanley Algo Trading + Behavioral Finance Research
Institutional-grade market participant behavior modeling
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import tensorflow as tf

class ParticipantType(Enum):
    RETAIL = "retail"
    INSTITUTIONAL = "institutional"
    MARKET_MAKER = "market_maker"
    ARBITRAGEUR = "arbitrageur"
    HFT = "high_frequency_trader"
    WHALE = "whale"

class BehavioralPattern(Enum):
    MOMENTUM_CHASING = "momentum_chasing"
    FEAR_OF_MISSING_OUT = "fomo"
    PANIC_SELLING = "panic_selling"
    GREED_ACCUMULATION = "greed_accumulation"
    VALUE_INVESTING = "value_investing"
    ARBITRAGE_EXECUTION = "arbitrage_execution"
    MARKET_MAKING = "market_making"

@dataclass
class ParticipantBehavior:
    """Morgan Stanley-inspired participant behavior analysis"""
    address: str
    participant_type: ParticipantType
    behavioral_patterns: List[BehavioralPattern]
    confidence: float
    recent_activities: List[Dict]
    risk_profile: str
    influence_score: float
    timestamp: datetime

@dataclass
class MarketSentiment:
    """Behavioral finance-inspired market sentiment analysis"""
    overall_sentiment: str
    sentiment_score: float
    fear_greed_index: float
    participant_sentiments: Dict[ParticipantType, float]
    dominant_behavior: BehavioralPattern
    sentiment_momentum: float
    timestamp: datetime

class BehavioralModelsAI:
    """
    Morgan Stanley Algo Trading + Behavioral Finance AI
    Institutional-grade market participant behavior modeling
    """
    
    def __init__(self):
        self.participant_profiles = {}
        self.behavioral_clusters = {}
        self.sentiment_models = {}
        self.anomaly_detectors = {}
        
        # Behavioral finance configuration
        self.config = {
            'clustering': {
                'min_cluster_size': 5,
                'eps': 0.5,
                'features': ['trade_size', 'frequency', 'holding_period', 'profit_taking']
            },
            'sentiment': {
                'lookback_window': 100,
                'update_frequency': 300,  # 5 minutes
                'confidence_threshold': 0.7
            },
            'anomaly_detection': {
                'contamination': 0.1,
                'random_state': 42
            }
        }
        
        # Initialize models
        self._initialize_models()

    async def analyze_participant_behavior(self, 
                                         address: str,
                                         transaction_history: List[Dict]) -> ParticipantBehavior:
        """
        Morgan Stanley-inspired participant behavior analysis
        """
        # Feature extraction
        features = await self._extract_behavioral_features(address, transaction_history)
        
        # Participant type classification
        participant_type = await self._classify_participant_type(features)
        
        # Behavioral pattern recognition
        behavioral_patterns = await self._identify_behavioral_patterns(features, transaction_history)
        
        # Risk profile assessment
        risk_profile = await self._assess_risk_profile(features, behavioral_patterns)
        
        # Influence scoring
        influence_score = await self._calculate_influence_score(features, transaction_history)
        
        # Confidence calculation
        confidence = await self._calculate_behavior_confidence(features, behavioral_patterns)
        
        return ParticipantBehavior(
            address=address,
            participant_type=participant_type,
            behavioral_patterns=behavioral_patterns,
            confidence=confidence,
            recent_activities=transaction_history[-10:],  # Last 10 activities
            risk_profile=risk_profile,
            influence_score=influence_score,
            timestamp=datetime.now()
        )

    async def analyze_market_sentiment(self, 
                                     market_data: Dict,
                                     participant_activities: List[Dict]) -> MarketSentiment:
        """
        Behavioral finance-inspired market sentiment analysis
        """
        # Participant sentiment aggregation
        participant_sentiments = await self._aggregate_participant_sentiments(participant_activities)
        
        # Price-based sentiment indicators
        price_sentiment = await self._analyze_price_sentiment(market_data)
        
        # Volume-based sentiment indicators
        volume_sentiment = await self._analyze_volume_sentiment(market_data)
        
        # Social sentiment indicators (would integrate with external data)
        social_sentiment = await self._analyze_social_sentiment()
        
        # Fear & Greed Index calculation
        fear_greed_index = await self._calculate_fear_greed_index(
            price_sentiment, volume_sentiment, social_sentiment
        )
        
        # Overall sentiment determination
        overall_sentiment = await self._determine_overall_sentiment(
            participant_sentiments, fear_greed_index
        )
        
        # Sentiment momentum
        sentiment_momentum = await self._calculate_sentiment_momentum()
        
        return MarketSentiment(
            overall_sentiment=overall_sentiment,
            sentiment_score=self._calculate_sentiment_score(participant_sentiments),
            fear_greed_index=fear_greed_index,
            participant_sentiments=participant_sentiments,
            dominant_behavior=await self._identify_dominant_behavior(participant_activities),
            sentiment_momentum=sentiment_momentum,
            timestamp=datetime.now()
        )

    async def detect_behavioral_anomalies(self, 
                                        current_behavior: ParticipantBehavior,
                                        historical_patterns: List[Dict]) -> List[Dict]:
        """
        Detect anomalous behavior patterns
        """
        anomalies = []
        
        # Trading pattern anomalies
        pattern_anomalies = await self._detect_pattern_anomalies(current_behavior, historical_patterns)
        anomalies.extend(pattern_anomalies)
        
        # Volume anomalies
        volume_anomalies = await self._detect_volume_anomalies(current_behavior)
        anomalies.extend(volume_anomalies)
        
        # Timing anomalies
        timing_anomalies = await self._detect_timing_anomalies(current_behavior)
        anomalies.extend(timing_anomalies)
        
        # Social network anomalies
        network_anomalies = await self._detect_network_anomalies(current_behavior)
        anomalies.extend(network_anomalies)
        
        return anomalies

    async def predict_participant_actions(self,
                                        participant_behavior: ParticipantBehavior,
                                        market_conditions: Dict) -> List[Dict]:
        """
        Predict future actions based on behavioral patterns
        """
        predictions = []
        
        # Pattern-based prediction
        pattern_predictions = await self._predict_from_patterns(participant_behavior, market_conditions)
        predictions.extend(pattern_predictions)
        
        # Reinforcement learning based prediction
        rl_predictions = await self._predict_from_rl(participant_behavior, market_conditions)
        predictions.extend(rl_predictions)
        
        # Game theory based prediction
        game_theory_predictions = await self._predict_from_game_theory(participant_behavior, market_conditions)
        predictions.extend(game_theory_predictions)
        
        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)[:5]  # Top 5 predictions

    async def _extract_behavioral_features(self, address: str, transaction_history: List[Dict]) -> Dict:
        """
        Extract comprehensive behavioral features
        """
        features = {}
        
        # Trading frequency features
        features['trading_frequency'] = await self._calculate_trading_frequency(transaction_history)
        features['session_activity'] = await self._analyze_session_activity(transaction_history)
        
        # Position sizing features
        features['avg_position_size'] = await self._calculate_avg_position_size(transaction_history)
        features['position_size_volatility'] = await self._calculate_position_volatility(transaction_history)
        
        # Holding period features
        features['avg_holding_period'] = await self._calculate_avg_holding_period(transaction_history)
        features['holding_period_consistency'] = await self._calculate_holding_consistency(transaction_history)
        
        # Profit-taking behavior
        features['profit_taking_aggressiveness'] = await self._calculate_profit_taking_behavior(transaction_history)
        features['loss_cutting_behavior'] = await self._calculate_loss_cutting_behavior(transaction_history)
        
        # Risk management features
        features['risk_management_consistency'] = await self._assess_risk_management(transaction_history)
        features['drawdown_tolerance'] = await self._calculate_drawdown_tolerance(transaction_history)
        
        return features

    async def _classify_participant_type(self, features: Dict) -> ParticipantType:
        """
        Classify participant type using machine learning
        """
        # Feature vector for classification
        feature_vector = np.array([
            features['trading_frequency'],
            features['avg_position_size'],
            features['avg_holding_period'],
            features['profit_taking_aggressiveness']
        ]).reshape(1, -1)
        
        # This would use a pre-trained classifier
        # For now, using rule-based classification
        if features['trading_frequency'] > 1000:  # Very high frequency
            return ParticipantType.HFT
        elif features['avg_position_size'] > 1000000:  # Large positions
            return ParticipantType.WHALE
        elif features['avg_holding_period'] < 3600:  # Short holding periods
            return ParticipantType.ARBITRAGEUR
        elif features['trading_frequency'] < 10:  # Low frequency
            return ParticipantType.RETAIL
        else:
            return ParticipantType.INSTITUTIONAL

    async def _identify_behavioral_patterns(self, features: Dict, transactions: List[Dict]) -> List[BehavioralPattern]:
        """
        Identify behavioral patterns from transaction history
        """
        patterns = []
        
        # Momentum chasing detection
        if await self._detect_momentum_chasing(transactions):
            patterns.append(BehavioralPattern.MOMENTUM_CHASING)
        
        # FOMO detection
        if await self._detect_fomo_behavior(transactions):
            patterns.append(BehavioralPattern.FEAR_OF_MISSING_OUT)
        
        # Panic selling detection
        if await self._detect_panic_selling(transactions):
            patterns.append(BehavioralPattern.PANIC_SELLING)
        
        # Greed accumulation detection
        if await self._detect_greed_accumulation(transactions):
            patterns.append(BehavioralPattern.GREED_ACCUMULATION)
        
        # Value investing detection
        if await self._detect_value_investing(transactions):
            patterns.append(BehavioralPattern.VALUE_INVESTING)
        
        # Arbitrage behavior detection
        if await self._detect_arbitrage_behavior(transactions):
            patterns.append(BehavioralPattern.ARBITRAGE_EXECUTION)
        
        return patterns

    async def _calculate_influence_score(self, features: Dict, transactions: List[Dict]) -> float:
        """
        Calculate participant influence score
        """
        score_components = []
        
        # Trading volume influence
        volume_influence = await self._calculate_volume_influence(transactions)
        score_components.append(volume_influence * 0.3)
        
        # Network influence
        network_influence = await self._calculate_network_influence(transactions)
        score_components.append(network_influence * 0.25)
        
        # Price impact influence
        price_impact = await self._calculate_price_impact(transactions)
        score_components.append(price_impact * 0.25)
        
        # Follow-on activity influence
        follow_influence = await self._calculate_follow_influence(transactions)
        score_components.append(follow_influence * 0.2)
        
        return sum(score_components)

    async def _aggregate_participant_sentiments(self, activities: List[Dict]) -> Dict[ParticipantType, float]:
        """
        Aggregate sentiments across participant types
        """
        sentiments = {}
        
        for participant_type in ParticipantType:
            type_activities = [a for a in activities if a.get('participant_type') == participant_type]
            if type_activities:
                sentiment = await self._calculate_participant_sentiment(type_activities)
                sentiments[participant_type] = sentiment
        
        return sentiments

    async def _calculate_fear_greed_index(self, 
                                        price_sentiment: float, 
                                        volume_sentiment: float, 
                                        social_sentiment: float) -> float:
        """
        Calculate Fear & Greed Index (0-100 scale)
        """
        components = {
            'price_momentum': price_sentiment * 25,
            'market_volatility': (1 - abs(price_sentiment)) * 25,
            'volume_strength': volume_sentiment * 15,
            'social_sentiment': social_sentiment * 15,
            'dominant_behavior': await self._calculate_behavior_sentiment() * 20
        }
        
        return sum(components.values())

    def _initialize_models(self):
        """Initialize machine learning models"""
        # Anomaly detection model
        self.anomaly_detectors['behavioral'] = IsolationForest(
            contamination=self.config['anomaly_detection']['contamination'],
            random_state=self.config['anomaly_detection']['random_state']
        )
        
        # Clustering model for participant segmentation
        self.behavioral_clusters['participant'] = DBSCAN(
            eps=self.config['clustering']['eps'],
            min_samples=self.config['clustering']['min_cluster_size']
        )

    # Placeholder implementations for detection methods
    async def _detect_momentum_chasing(self, transactions: List[Dict]) -> bool:
        """Detect momentum chasing behavior"""
        # Implementation would analyze buying patterns during price increases
        return len(transactions) > 5  # Simplified

    async def _detect_fomo_behavior(self, transactions: List[Dict]) -> bool:
        """Detect Fear Of Missing Out behavior"""
        # Implementation would analyze rapid buying after price spikes
        return any(t.get('fomo_indicator', False) for t in transactions)

    async def _calculate_volume_influence(self, transactions: List[Dict]) -> float:
        """Calculate volume-based influence score"""
        total_volume = sum(t.get('volume', 0) for t in transactions)
        return min(total_volume / 1000000, 1.0)  # Normalize to 0-1

# Usage example
async def main():
    """Example usage of Behavioral Models AI"""
    behavioral_ai = BehavioralModelsAI()
    
    # Sample transaction history
    transaction_history = [
        {'timestamp': datetime.now() - timedelta(hours=2), 'volume': 50000, 'price': 3500},
        {'timestamp': datetime.now() - timedelta(hours=1), 'volume': 75000, 'price': 3520},
        {'timestamp': datetime.now(), 'volume': 100000, 'price': 3530}
    ]
    
    # Analyze participant behavior
    behavior = await behavioral_ai.analyze_participant_behavior(
        "0x742d35Cc6634C0532925a3b8D7a1C3f5F5A6E8C8",
        transaction_history
    )
    
    print(f"Participant Type: {behavior.participant_type.value}")
    print(f"Behavioral Patterns: {[p.value for p in behavior.behavioral_patterns]}")
    print(f"Influence Score: {behavior.influence_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
