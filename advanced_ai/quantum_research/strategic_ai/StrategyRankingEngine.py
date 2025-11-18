"""
AI-NEXUS v5.0 - STRATEGY RANKING ENGINE MODULE
Advanced Multi-Objective Strategy Evaluation and Ranking System
Dynamic strategy performance assessment with adaptive weighting
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

class RankingObjective(Enum):
    PROFITABILITY = "profitability"
    RISK_ADJUSTED_RETURN = "risk_adjusted_return"
    CONSISTENCY = "consistency"
    CAPITAL_EFFICIENCY = "capital_efficiency"
    DIVERSIFICATION = "diversification"
    ADAPTABILITY = "adaptability"
    ROBUSTNESS = "robustness"

class MarketRegime(Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    VOLATILE_MARKET = "volatile_market"
    SIDEWAYS_MARKET = "sideways_market"

@dataclass
class StrategyPerformance:
    strategy_id: str
    timestamp: datetime
    returns: Dict[str, float]  # Different timeframe returns
    risk_metrics: Dict[str, float]
    efficiency_metrics: Dict[str, float]
    consistency_metrics: Dict[str, float]
    regime_performance: Dict[MarketRegime, float]
    metadata: Dict[str, Any]

@dataclass
class StrategyRank:
    strategy_id: str
    overall_rank: int
    overall_score: float
    objective_scores: Dict[RankingObjective, float]
    objective_ranks: Dict[RankingObjective, int]
    regime_effectiveness: Dict[MarketRegime, float]
    improvement_areas: List[str]
    confidence: float

@dataclass
class RankingConfiguration:
    objective_weights: Dict[RankingObjective, float]
    regime_aware_weighting: bool
    lookback_period: timedelta
    min_data_points: int
    decay_factor: float
    confidence_threshold: float

class StrategyRankingEngine:
    """
    Advanced strategy ranking system with multi-objective optimization
    Adaptive weighting based on market conditions and strategy characteristics
    """
    
    def __init__(self):
        self.performance_history = defaultdict(lambda: deque(maxlen=1000))
        self.ranking_history = deque(maxlen=500)
        self.ranking_configs = {}
        
        # Ranking parameters
        self.ranking_params = {
            'default_lookback': timedelta(days=90),
            'min_performance_points': 50,
            'performance_decay': 0.95,
            'regime_adaptation_speed': 0.1,
            'confidence_calibration': 0.8
        }
        
        # Objective definitions
        self.objective_definitions = {
            RankingObjective.PROFITABILITY: {
                'description': 'Absolute and relative profitability',
                'metrics': ['total_return', 'sharpe_ratio', 'profit_factor'],
                'normalization': 'log_scale',
                'direction': 'maximize'
            },
            RankingObjective.RISK_ADJUSTED_RETURN: {
                'description': 'Returns adjusted for risk taken',
                'metrics': ['sharpe_ratio', 'sortino_ratio', 'calmar_ratio'],
                'normalization': 'linear',
                'direction': 'maximize'
            },
            RankingObjective.CONSISTENCY: {
                'description': 'Performance consistency and predictability',
                'metrics': ['win_rate', 'consistency_score', 'drawdown_stability'],
                'normalization': 'linear',
                'direction': 'maximize'
            },
            RankingObjective.CAPITAL_EFFICIENCY: {
                'description': 'Efficient use of capital',
                'metrics': ['roi_per_trade', 'capital_turnover', 'utilization_efficiency'],
                'normalization': 'log_scale',
                'direction': 'maximize'
            },
            RankingObjective.DIVERSIFICATION: {
                'description': 'Portfolio diversification benefits',
                'metrics': ['correlation_score', 'cluster_independence', 'strategy_variety'],
                'normalization': 'linear',
                'direction': 'maximize'
            },
            RankingObjective.ADAPTABILITY: {
                'description': 'Adaptation to changing market conditions',
                'metrics': ['regime_adaptation', 'parameter_stability', 'learning_capability'],
                'normalization': 'linear',
                'direction': 'maximize'
            },
            RankingObjective.ROBUSTNESS: {
                'description': 'Robustness to stress and edge cases',
                'metrics': ['stress_test_score', 'outlier_resistance', 'parameter_sensitivity'],
                'normalization': 'linear',
                'direction': 'maximize'
            }
        }
        
        # Market regime detector
        self.regime_detector = MarketRegimeDetector()
        
        # Performance models
        self.performance_models = {}
        
        # Initialize ranking configurations
        self._initialize_ranking_configs()
        self._initialize_performance_models()
    
    def _initialize_ranking_configs(self):
        """Initialize different ranking configurations"""
        
        # Conservative configuration (risk-averse)
        self.ranking_configs['conservative'] = RankingConfiguration(
            objective_weights={
                RankingObjective.RISK_ADJUSTED_RETURN: 0.30,
                RankingObjective.ROBUSTNESS: 0.25,
                RankingObjective.CONSISTENCY: 0.20,
                RankingObjective.PROFITABILITY: 0.15,
                RankingObjective.DIVERSIFICATION: 0.10,
                RankingObjective.ADAPTABILITY: 0.0,
                RankingObjective.CAPITAL_EFFICIENCY: 0.0
            },
            regime_aware_weighting=True,
            lookback_period=timedelta(days=180),
            min_data_points=100,
            decay_factor=0.98,
            confidence_threshold=0.8
        )
        
        # Balanced configuration
        self.ranking_configs['balanced'] = RankingConfiguration(
            objective_weights={
                RankingObjective.PROFITABILITY: 0.25,
                RankingObjective.RISK_ADJUSTED_RETURN: 0.20,
                RankingObjective.CONSISTENCY: 0.15,
                RankingObjective.CAPITAL_EFFICIENCY: 0.15,
                RankingObjective.ADAPTABILITY: 0.10,
                RankingObjective.DIVERSIFICATION: 0.10,
                RankingObjective.ROBUSTNESS: 0.05
            },
            regime_aware_weighting=True,
            lookback_period=timedelta(days=90),
            min_data_points=50,
            decay_factor=0.95,
            confidence_threshold=0.7
        )
        
        # Aggressive configuration (return-focused)
        self.ranking_configs['aggressive'] = RankingConfiguration(
            objective_weights={
                RankingObjective.PROFITABILITY: 0.40,
                RankingObjective.CAPITAL_EFFICIENCY: 0.25,
                RankingObjective.ADAPTABILITY: 0.15,
                RankingObjective.RISK_ADJUSTED_RETURN: 0.10,
                RankingObjective.CONSISTENCY: 0.05,
                RankingObjective.DIVERSIFICATION: 0.05,
                RankingObjective.ROBUSTNESS: 0.0
            },
            regime_aware_weighting=False,
            lookback_period=timedelta(days=30),
            min_data_points=20,
            decay_factor=0.90,
            confidence_threshold=0.6
        )
    
    def _initialize_performance_models(self):
        """Initialize performance prediction models"""
        
        self.performance_models = {
            'regime_performance': RegimePerformanceModel(),
            'risk_adjustment': RiskAdjustmentModel(),
            'consistency_analysis': ConsistencyAnalysisModel(),
            'efficiency_calculator': EfficiencyCalculator()
        }
    
    def record_strategy_performance(self, performance: StrategyPerformance):
        """Record strategy performance data"""
        
        self.performance_history[performance.strategy_id].append(performance)
        
        # Trim history if too long
        max_history = 1000
        if len(self.performance_history[performance.strategy_id]) > max_history:
            self.performance_history[performance.strategy_id] = deque(
                list(self.performance_history[performance.strategy_id])[-max_history:],
                maxlen=max_history
            )
    
    async def rank_strategies(self, 
                            strategy_ids: List[str],
                            ranking_config: str = 'balanced',
                            current_regime: MarketRegime = None) -> Dict[str, StrategyRank]:
        """Rank strategies based on comprehensive multi-objective assessment"""
        
        config = self.ranking_configs.get(ranking_config, self.ranking_configs['balanced'])
        
        if current_regime is None:
            current_regime = await self.regime_detector.detect_current_regime()
        
        # Calculate objective scores for each strategy
        strategy_scores = {}
        objective_scores_all = {}
        
        for strategy_id in strategy_ids:
            objective_scores = await self._calculate_objective_scores(
                strategy_id, config, current_regime
            )
            
            if objective_scores:
                strategy_scores[strategy_id] = objective_scores
                objective_scores_all[strategy_id] = objective_scores
        
        if not strategy_scores:
            return {}
        
        # Calculate overall scores with adaptive weighting
        overall_scores = {}
        for strategy_id, objective_scores in strategy_scores.items():
            overall_score = self._calculate_overall_score(
                objective_scores, config, current_regime
            )
            overall_scores[strategy_id] = overall_score
        
        # Rank strategies by overall score
        ranked_strategies = sorted(
            overall_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Create strategy rank objects
        strategy_ranks = {}
        for rank, (strategy_id, overall_score) in enumerate(ranked_strategies, 1):
            objective_scores = strategy_scores[strategy_id]
            
            # Calculate objective ranks
            objective_ranks = self._calculate_objective_ranks(
                strategy_id, objective_scores_all
            )
            
            # Calculate regime effectiveness
            regime_effectiveness = await self._calculate_regime_effectiveness(
                strategy_id, current_regime
            )
            
            # Identify improvement areas
            improvement_areas = self._identify_improvement_areas(
                objective_scores, config.objective_weights
            )
            
            # Calculate confidence
            confidence = self._calculate_ranking_confidence(
                strategy_id, objective_scores, config
            )
            
            strategy_rank = StrategyRank(
                strategy_id=strategy_id,
                overall_rank=rank,
                overall_score=overall_score,
                objective_scores=objective_scores,
                objective_ranks=objective_ranks,
                regime_effectiveness=regime_effectiveness,
                improvement_areas=improvement_areas,
                confidence=confidence
            )
            
            strategy_ranks[strategy_id] = strategy_rank
        
        # Store ranking history
        ranking_record = {
            'timestamp': datetime.now(),
            'ranking_config': ranking_config,
            'current_regime': current_regime,
            'strategy_ranks': strategy_ranks
        }
        self.ranking_history.append(ranking_record)
        
        return strategy_ranks
    
    async def _calculate_objective_scores(self, 
                                        strategy_id: str,
                                        config: RankingConfiguration,
                                        current_regime: MarketRegime) -> Dict[RankingObjective, float]:
        """Calculate scores for each ranking objective"""
        
        performance_data = list(self.performance_history[strategy_id])
        
        if len(performance_data) < config.min_data_points:
            return {}
        
        objective_scores = {}
        
        for objective in RankingObjective:
            try:
                score = await self._calculate_single_objective_score(
                    objective, strategy_id, performance_data, config, current_regime
                )
                objective_scores[objective] = score
            except Exception as e:
                print(f"Error calculating {objective.value} for {strategy_id}: {e}")
                objective_scores[objective] = 0.0
        
        return objective_scores
    
    async def _calculate_single_objective_score(self,
                                              objective: RankingObjective,
                                              strategy_id: str,
                                              performance_data: List[StrategyPerformance],
                                              config: RankingConfiguration,
                                              current_regime: MarketRegime) -> float:
        """Calculate score for a single objective"""
        
        objective_def = self.objective_definitions[objective]
        metrics = objective_def['metrics']
        
        metric_scores = []
        
        for metric in metrics:
            metric_values = []
            weights = []
            
            # Calculate time-weighted metric values
            for i, performance in enumerate(performance_data):
                value = self._extract_metric_value(performance, metric)
                if value is not None:
                    # Apply time decay
                    time_weight = config.decay_factor ** i
                    metric_values.append(value * time_weight)
                    weights.append(time_weight)
            
            if metric_values:
                # Calculate weighted average
                weighted_avg = np.average(metric_values, weights=weights)
                
                # Normalize based on objective definition
                normalized_score = self._normalize_metric_score(
                    weighted_avg, metric, objective_def['normalization']
                )
                metric_scores.append(normalized_score)
        
        if not metric_scores:
            return 0.0
        
        # Combine metric scores (simple average for now)
        objective_score = np.mean(metric_scores)
        
        # Apply regime-specific adjustments
        if config.regime_aware_weighting:
            regime_adjustment = await self._calculate_regime_adjustment(
                strategy_id, objective, current_regime
            )
            objective_score *= regime_adjustment
        
        return max(0.0, min(1.0, objective_score))
    
    def _extract_metric_value(self, performance: StrategyPerformance, metric: str) -> Optional[float]:
        """Extract metric value from performance data"""
        
        # Check returns
        if metric in performance.returns:
            return performance.returns[metric]
        
        # Check risk metrics
        if metric in performance.risk_metrics:
            return performance.risk_metrics[metric]
        
        # Check efficiency metrics
        if metric in performance.efficiency_metrics:
            return performance.efficiency_metrics[metric]
        
        # Check consistency metrics
        if metric in performance.consistency_metrics:
            return performance.consistency_metrics[metric]
        
        # Special metrics
        if metric == 'profit_factor':
            return self._calculate_profit_factor(performance)
        elif metric == 'consistency_score':
            return self._calculate_consistency_score(performance)
        elif metric == 'drawdown_stability':
            return self._calculate_drawdown_stability(performance)
        
        return None
    
    def _calculate_profit_factor(self, performance: StrategyPerformance) -> float:
        """Calculate profit factor (gross profits / gross losses)"""
        
        gross_profits = performance.returns.get('gross_profits', 0)
        gross_losses = abs(performance.returns.get('gross_losses', 0))
        
        if gross_losses == 0:
            return 10.0  # Arbitrary high value for no losses
        
        return gross_profits / gross_losses
    
    def _calculate_consistency_score(self, performance: StrategyPerformance) -> float:
        """Calculate performance consistency score"""
        
        win_rate = performance.consistency_metrics.get('win_rate', 0.5)
        return_std = performance.risk_metrics.get('return_std', 0.1)
        
        # Higher win rate and lower std = higher consistency
        consistency = win_rate * (1 - min(1.0, return_std))
        return consistency
    
    def _calculate_drawdown_stability(self, performance: StrategyPerformance) -> float:
        """Calculate drawdown stability score"""
        
        max_drawdown = performance.risk_metrics.get('max_drawdown', 0.1)
        recovery_time = performance.risk_metrics.get('avg_recovery_time', 10)
        
        # Lower drawdown and faster recovery = higher stability
        drawdown_score = 1.0 - min(1.0, max_drawdown * 2)
        recovery_score = 1.0 - min(1.0, recovery_time / 100)
        
        return (drawdown_score + recovery_score) / 2
    
    def _normalize_metric_score(self, value: float, metric: str, normalization: str) -> float:
        """Normalize metric score to 0-1 range"""
        
        if normalization == 'linear':
            # Linear normalization based on reasonable ranges
            ranges = {
                'total_return': (-0.5, 2.0),  # -50% to 200%
                'sharpe_ratio': (-1.0, 5.0),
                'sortino_ratio': (-1.0, 7.0),
                'calmar_ratio': (-2.0, 10.0),
                'win_rate': (0.3, 0.9),
                'profit_factor': (0.5, 5.0),
                'max_drawdown': (0.05, 0.5),  # Inverted: lower is better
                'roi_per_trade': (-0.01, 0.05),
                'capital_turnover': (0.1, 10.0)
            }
            
            min_val, max_val = ranges.get(metric, (0.0, 1.0))
            
            # For metrics where lower is better (like drawdown), invert
            if metric in ['max_drawdown', 'return_std', 'var']:
                normalized = 1.0 - ((value - min_val) / (max_val - min_val))
            else:
                normalized = (value - min_val) / (max_val - min_val)
            
            return max(0.0, min(1.0, normalized))
        
        elif normalization == 'log_scale':
            # Logarithmic normalization for metrics with wide ranges
            return min(1.0, max(0.0, np.log1p(abs(value)) / 10))
        
        else:
            # Default linear normalization
            return max(0.0, min(1.0, value))
    
    async def _calculate_regime_adjustment(self, 
                                        strategy_id: str,
                                        objective: RankingObjective,
                                        current_regime: MarketRegime) -> float:
        """Calculate regime-based adjustment for objective score"""
        
        performance_data = list(self.performance_history[strategy_id])
        
        if len(performance_data) < 10:
            return 1.0  # No adjustment for insufficient data
        
        # Calculate performance in current regime vs other regimes
        regime_performance = []
        other_performance = []
        
        for performance in performance_data:
            regime = performance.regime_performance.get(current_regime, 0.5)
            regime_performance.append(regime)
            
            # Average of other regimes
            other_regimes = [p for r, p in performance.regime_performance.items() 
                           if r != current_regime]
            if other_regimes:
                other_performance.append(np.mean(other_regimes))
        
        if not regime_performance or not other_performance:
            return 1.0
        
        avg_regime_perf = np.mean(regime_performance)
        avg_other_perf = np.mean(other_performance)
        
        if avg_other_perf == 0:
            return 1.0
        
        # Adjustment factor: how much better/worse in current regime
        adjustment = avg_regime_perf / avg_other_perf
        
        return min(2.0, max(0.5, adjustment))
    
    def _calculate_overall_score(self,
                               objective_scores: Dict[RankingObjective, float],
                               config: RankingConfiguration,
                               current_regime: MarketRegime) -> float:
        """Calculate overall strategy score with adaptive weighting"""
        
        # Start with base weights
        weights = config.objective_weights.copy()
        
        # Apply regime-aware adjustments if enabled
        if config.regime_aware_weighting:
            weights = self._adjust_weights_for_regime(weights, current_regime)
        
        # Calculate weighted sum
        overall_score = 0.0
        total_weight = 0.0
        
        for objective, weight in weights.items():
            if objective in objective_scores:
                overall_score += objective_scores[objective] * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score /= total_weight
        
        return overall_score
    
    def _adjust_weights_for_regime(self, 
                                 weights: Dict[RankingObjective, float],
                                 regime: MarketRegime) -> Dict[RankingObjective, float]:
        """Adjust objective weights based on market regime"""
        
        regime_adjustments = {
            MarketRegime.BULL_MARKET: {
                RankingObjective.PROFITABILITY: 1.2,
                RankingObjective.CAPITAL_EFFICIENCY: 1.1,
                RankingObjective.RISK_ADJUSTED_RETURN: 0.9,
                RankingObjective.ROBUSTNESS: 0.8
            },
            MarketRegime.BEAR_MARKET: {
                RankingObjective.RISK_ADJUSTED_RETURN: 1.3,
                RankingObjective.ROBUSTNESS: 1.2,
                RankingObjective.CONSISTENCY: 1.1,
                RankingObjective.PROFITABILITY: 0.7
            },
            MarketRegime.VOLATILE_MARKET: {
                RankingObjective.ADAPTABILITY: 1.4,
                RankingObjective.RISK_ADJUSTED_RETURN: 1.2,
                RankingObjective.CONSISTENCY: 0.8,
                RankingObjective.DIVERSIFICATION: 1.1
            },
            MarketRegime.SIDEWAYS_MARKET: {
                RankingObjective.CAPITAL_EFFICIENCY: 1.3,
                RankingObjective.CONSISTENCY: 1.1,
                RankingObjective.ADAPTABILITY: 0.9,
                RankingObjective.PROFITABILITY: 0.8
            }
        }
        
        adjustments = regime_adjustments.get(regime, {})
        adjusted_weights = weights.copy()
        
        for objective, adjustment in adjustments.items():
            if objective in adjusted_weights:
                adjusted_weights[objective] *= adjustment
        
        # Normalize weights
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {k: v/total_weight for k, v in adjusted_weights.items()}
        
        return adjusted_weights
    
    def _calculate_objective_ranks(self,
                                 strategy_id: str,
                                 all_objective_scores: Dict[str, Dict[RankingObjective, float]]) -> Dict[RankingObjective, int]:
        """Calculate rank for each objective across all strategies"""
        
        objective_ranks = {}
        
        for objective in RankingObjective:
            # Get scores for this objective across all strategies
            objective_scores = {}
            for sid, scores in all_objective_scores.items():
                if objective in scores:
                    objective_scores[sid] = scores[objective]
            
            if objective_scores:
                # Rank strategies by this objective
                ranked = sorted(objective_scores.items(), key=lambda x: x[1], reverse=True)
                
                # Find rank of current strategy
                rank = 1
                for sid, score in ranked:
                    if sid == strategy_id:
                        objective_ranks[objective] = rank
                        break
                    rank += 1
            else:
                objective_ranks[objective] = 1  # Default to rank 1 if no data
        
        return objective_ranks
    
    async def _calculate_regime_effectiveness(self,
                                           strategy_id: str,
                                           current_regime: MarketRegime) -> Dict[MarketRegime, float]:
        """Calculate strategy effectiveness across different market regimes"""
        
        performance_data = list(self.performance_history[strategy_id])
        
        if not performance_data:
            return {regime: 0.5 for regime in MarketRegime}
        
        regime_effectiveness = {}
        
        for regime in MarketRegime:
            regime_performances = []
            
            for performance in performance_data:
                if regime in performance.regime_performance:
                    regime_performances.append(performance.regime_performance[regime])
            
            if regime_performances:
                effectiveness = np.mean(regime_performances)
            else:
                effectiveness = 0.5  # Neutral effectiveness
            
            regime_effectiveness[regime] = max(0.0, min(1.0, effectiveness))
        
        return regime_effectiveness
    
    def _identify_improvement_areas(self,
                                  objective_scores: Dict[RankingObjective, float],
                                  weights: Dict[RankingObjective, float]) -> List[str]:
        """Identify areas where strategy needs improvement"""
        
        improvement_areas = []
        threshold = 0.6  # Scores below this need improvement
        
        for objective, score in objective_scores.items():
            if score < threshold:
                # Only include if objective has significant weight
                if weights.get(objective, 0) > 0.05:
                    improvement_areas.append(
                        f"Improve {objective.value} (current: {score:.2f})"
                    )
        
        # If no specific areas, check if overall score is low
        overall_score = self._calculate_overall_score(objective_scores, 
                                                    RankingConfiguration(
                                                        objective_weights=weights,
                                                        regime_aware_weighting=False,
                                                        lookback_period=timedelta(days=90),
                                                        min_data_points=10,
                                                        decay_factor=0.95,
                                                        confidence_threshold=0.7
                                                    ), MarketRegime.BULL_MARKET)
        
        if overall_score < 0.7 and not improvement_areas:
            improvement_areas.append("General performance improvement needed")
        
        return improvement_areas[:3]  # Return top 3 improvement areas
    
    def _calculate_ranking_confidence(self,
                                   strategy_id: str,
                                   objective_scores: Dict[RankingObjective, float],
                                   config: RankingConfiguration) -> float:
        """Calculate confidence in strategy ranking"""
        
        performance_data = list(self.performance_history[strategy_id])
        
        if len(performance_data) < config.min_data_points:
            return 0.3  # Low confidence for insufficient data
        
        # Calculate data quality confidence
        data_quality = min(1.0, len(performance_data) / 200)
        
        # Calculate score stability confidence
        score_variance = np.var(list(objective_scores.values())) if objective_scores else 0.5
        stability_confidence = 1.0 - min(1.0, score_variance * 2)
        
        # Calculate regime coverage confidence
        regime_coverage = self._calculate_regime_coverage(strategy_id)
        
        # Combine confidence factors
        confidence = (
            data_quality * 0.4 +
            stability_confidence * 0.4 +
            regime_coverage * 0.2
        )
        
        return max(0.1, min(1.0, confidence))
    
    def _calculate_regime_coverage(self, strategy_id: str) -> float:
        """Calculate how well strategy performance covers different market regimes"""
        
        performance_data = list(self.performance_history[strategy_id])
        
        if not performance_data:
            return 0.0
        
        regime_coverage = set()
        
        for performance in performance_data:
            for regime in performance.regime_performance.keys():
                regime_coverage.add(regime)
        
        coverage_ratio = len(regime_coverage) / len(MarketRegime)
        return coverage_ratio
    
    def get_ranking_history(self, strategy_id: str, lookback_days: int = 30) -> List[Dict[str, Any]]:
        """Get ranking history for a strategy"""
        
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        history = []
        for ranking_record in self.ranking_history:
            if ranking_record['timestamp'] >= cutoff_date:
                if strategy_id in ranking_record['strategy_ranks']:
                    rank_info = ranking_record['strategy_ranks'][strategy_id]
                    history.append({
                        'timestamp': ranking_record['timestamp'],
                        'overall_rank': rank_info.overall_rank,
                        'overall_score': rank_info.overall_score,
                        'ranking_config': ranking_record['ranking_config'],
                        'regime': ranking_record['current_regime'].value
                    })
        
        return sorted(history, key=lambda x: x['timestamp'])
    
    def get_top_strategies(self, 
                          top_n: int = 10,
                          ranking_config: str = 'balanced',
                          regime: MarketRegime = None) -> List[Tuple[str, float]]:
        """Get top N strategies based on recent rankings"""
        
        if not self.ranking_history:
            return []
        
        # Get most recent ranking
        latest_ranking = self.ranking_history[-1]
        
        if latest_ranking['ranking_config'] != ranking_config:
            return []
        
        # Filter by regime if specified
        if regime and latest_ranking['current_regime'] != regime:
            return []
        
        # Get top strategies
        strategy_ranks = latest_ranking['strategy_ranks']
        ranked_strategies = sorted(
            strategy_ranks.items(),
            key=lambda x: x[1].overall_rank
        )[:top_n]
        
        return [(s[0], s[1].overall_score) for s in ranked_strategies]

# Supporting Classes
class MarketRegimeDetector:
    """Market regime detection system"""
    
    async def detect_current_regime(self) -> MarketRegime:
        """Detect current market regime"""
        # Simplified implementation
        # In production, this would use sophisticated market analysis
        return MarketRegime.BULL_MARKET

class RegimePerformanceModel:
    """Model for regime-specific performance prediction"""
    pass

class RiskAdjustmentModel:
    """Model for risk-adjusted performance calculation"""
    pass

class ConsistencyAnalysisModel:
    """Model for performance consistency analysis"""
    pass

class EfficiencyCalculator:
    """Calculator for capital efficiency metrics"""
    pass

# Example usage
if __name__ == "__main__":
    # Create strategy ranking engine
    ranking_engine = StrategyRankingEngine()
    
    # Sample strategy performance data
    sample_performance = StrategyPerformance(
        strategy_id="momentum_arb_v1",
        timestamp=datetime.now(),
        returns={
            'total_return': 0.15,
            'daily_return': 0.0012,
            'weekly_return': 0.008,
            'monthly_return': 0.035
        },
        risk_metrics={
            'sharpe_ratio': 2.1,
            'max_drawdown': 0.08,
            'volatility': 0.12,
            'var_95': 0.025
        },
        efficiency_metrics={
            'roi_per_trade': 0.002,
            'capital_turnover': 3.5,
            'utilization_efficiency': 0.85
        },
        consistency_metrics={
            'win_rate': 0.65,
            'profit_factor': 1.8,
            'consecutive_wins': 5
        },
        regime_performance={
            MarketRegime.BULL_MARKET: 0.8,
            MarketRegime.BEAR_MARKET: 0.4,
            MarketRegime.VOLATILE_MARKET: 0.7,
            MarketRegime.SIDEWAYS_MARKET: 0.6
        },
        metadata={'trades_count': 150, 'avg_trade_size': 5000}
    )
    
    # Record performance
    ranking_engine.record_strategy_performance(sample_performance)
    
    # Add more sample data for other strategies
    for i in range(5):
        other_performance = StrategyPerformance(
            strategy_id=f"strategy_{i}",
            timestamp=datetime.now() - timedelta(days=i),
            returns={'total_return': 0.05 + i*0.02},
            risk_metrics={'sharpe_ratio': 1.0 + i*0.2},
            efficiency_metrics={'roi_per_trade': 0.001 + i*0.0005},
            consistency_metrics={'win_rate': 0.5 + i*0.05},
            regime_performance={r: 0.4 + i*0.1 for r in MarketRegime},
            metadata={}
        )
        ranking_engine.record_strategy_performance(other_performance)
    
    # Rank strategies
    async def demo():
        strategy_ids = ["momentum_arb_v1", "strategy_0", "strategy_1", "strategy_2", "strategy_3", "strategy_4"]
        
        rankings = await ranking_engine.rank_strategies(
            strategy_ids, ranking_config='balanced'
        )
        
        print("Strategy Rankings:")
        for strategy_id, rank in rankings.items():
            print(f"#{rank.overall_rank}: {strategy_id} (Score: {rank.overall_score:.3f})")
            print(f"  Confidence: {rank.confidence:.2f}")
            print(f"  Improvement Areas: {rank.improvement_areas}")
            print()
    
    import asyncio
    asyncio.run(demo())
