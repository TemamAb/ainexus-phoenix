"""
Strategy Researcher - Real-Time Trading Strategy Development

Advanced real-time strategy research system that continuously develops,
tests, and optimizes trading strategies based on live market data.

Key Features:
- Real-time strategy generation
- Automated backtesting and validation
- Machine learning-driven optimization
- Market regime adaptation
- Risk-aware strategy selection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import asyncio
import json
import pickle
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """Types of trading strategies"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    ARBITRAGE = "arbitrage"
    MARKET_NEUTRAL = "market_neutral"
    TREND_FOLLOWING = "trend_following"
    VOLATILITY = "volatility"
    STATISTICAL_ARB = "statistical_arb"

class MarketRegime(Enum):
    """Market regime classifications"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOL = "high_volatility"
    LOW_VOL = "low_volatility"
    CRISIS = "crisis"

class ResearchStatus(Enum):
    """Strategy research status"""
    DEVELOPING = "developing"
    BACKTESTING = "backtesting"
    VALIDATING = "validating"
    READY = "ready"
    DEPRECATED = "deprecated"
    FAILED = "failed"

@dataclass
class StrategyParameter:
    """Strategy parameter definition"""
    name: str
    value: float
    min_value: float
    max_value: float
    step: float
    optimized: bool = False

@dataclass
class TradingStrategy:
    """Complete trading strategy definition"""
    strategy_id: str
    strategy_type: StrategyType
    parameters: Dict[str, StrategyParameter]
    performance_metrics: Dict[str, float]
    market_regimes: List[MarketRegime]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: ResearchStatus = ResearchStatus.DEVELOPING
    confidence: float = 0.0

@dataclass
class ResearchResult:
    """Result of strategy research"""
    strategy_id: str
    performance_score: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    parameters: Dict[str, float]
    market_regime: MarketRegime
    backtest_period: timedelta
    validation_score: float

class StrategyResearcher:
    """
    Advanced real-time strategy research engine
    
    This system continuously develops and optimizes trading strategies
    using machine learning, statistical analysis, and real-time market data.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.strategies: Dict[str, TradingStrategy] = {}
        self.research_results: Dict[str, ResearchResult] = {}
        self.market_data_buffer = []
        self.current_regime = MarketRegime.SIDEWAYS
        
        # ML models for strategy optimization
        self.performance_predictor = None
        self.regime_classifier = None
        
        # Research configuration
        self.research_config = {
            'backtest_periods': [30, 90, 180],  # days
            'validation_period': 30,  # days
            'min_performance_threshold': 0.1,  # Minimum Sharpe ratio
            'max_drawdown_threshold': 0.15,    # Maximum allowed drawdown
            'optimization_iterations': 100,
            'feature_lookback': 20,  # periods for feature calculation
            'retrain_frequency': 7,  # days
        }
        
        # Performance tracking
        self.research_metrics = {
            'strategies_developed': 0,
            'strategies_validated': 0,
            'best_performance_score': 0.0,
            'average_development_time': timedelta(0),
            'regime_adaptation_success': 0.0
        }
        
        self._initialize_ml_models()
        self._load_template_strategies()
    
    def _initialize_ml_models(self):
        """Initialize machine learning models for strategy research"""
        # Performance prediction model
        self.performance_predictor = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        # Market regime classification model (simplified)
        self.regime_classifier = RandomForestRegressor(
            n_estimators=50,
            random_state=42
        )
        
        logger.info("ML models initialized for strategy research")
    
    def _load_template_strategies(self):
        """Load template strategies for research"""
        template_strategies = {
            "momentum_basic": {
                "type": StrategyType.MOMENTUM,
                "parameters": {
                    "lookback_period": StrategyParameter("lookback_period", 20, 5, 50, 1),
                    "holding_period": StrategyParameter("holding_period", 5, 1, 20, 1),
                    "entry_threshold": StrategyParameter("entry_threshold", 0.02, 0.005, 0.05, 0.005)
                },
                "regimes": [MarketRegime.BULL, MarketRegime.TREND_FOLLOWING]
            },
            "mean_reversion_basic": {
                "type": StrategyType.MEAN_REVERSION,
                "parameters": {
                    "lookback_period": StrategyParameter("lookback_period", 30, 10, 100, 5),
                    "std_dev_threshold": StrategyParameter("std_dev_threshold", 2.0, 1.0, 3.0, 0.1),
                    "reversion_period": StrategyParameter("reversion_period", 10, 5, 30, 1)
                },
                "regimes": [MarketRegime.SIDEWAYS, MarketRegime.MEAN_REVERSION]
            },
            "breakout_basic": {
                "type": StrategyType.BREAKOUT,
                "parameters": {
                    "resistance_lookback": StrategyParameter("resistance_lookback", 50, 20, 100, 5),
                    "support_lookback": StrategyParameter("support_lookback", 50, 20, 100, 5),
                    "breakout_threshold": StrategyParameter("breakout_threshold", 0.01, 0.005, 0.03, 0.002)
                },
                "regimes": [MarketRegime.BULL, MarketRegime.VOLATILITY]
            }
        }
        
        for strategy_id, template in template_strategies.items():
            strategy = TradingStrategy(
                strategy_id=strategy_id,
                strategy_type=template["type"],
                parameters=template["parameters"],
                performance_metrics={},
                market_regimes=template["regimes"]
            )
            self.strategies[strategy_id] = strategy
        
        logger.info(f"Loaded {len(template_strategies)} template strategies")
    
    def ingest_market_data(self, symbol: str, price_data: pd.DataFrame):
        """
        Ingest real-time market data for strategy research
        
        Args:
            symbol: Trading symbol
            price_data: DataFrame with OHLCV data
        """
        self.market_data_buffer.append({
            'symbol': symbol,
            'data': price_data,
            'timestamp': datetime.now()
        })
        
        # Keep only recent data to manage memory
        if len(self.market_data_buffer) > 1000:
            self.market_data_buffer = self.market_data_buffer[-1000:]
        
        # Update market regime
        self._update_market_regime(price_data)
        
        logger.debug(f"Ingested market data for {symbol}, buffer size: {len(self.market_data_buffer)}")
    
    def _update_market_regime(self, price_data: pd.DataFrame):
        """Update current market regime based on price data"""
        if len(price_data) < 50:
            return
        
        returns = price_data['close'].pct_change().dropna()
        
        # Calculate regime indicators
        volatility = returns.std()
        trend_strength = self._calculate_trend_strength(price_data['close'])
        mean_reversion = self._calculate_mean_reversion(price_data['close'])
        
        # Simple regime classification
        if volatility > returns.std() * 1.5:
            self.current_regime = MarketRegime.HIGH_VOL
        elif trend_strength > 0.7:
            self.current_regime = MarketRegime.BULL
        elif trend_strength < -0.7:
            self.current_regime = MarketRegime.BEAR
        elif mean_reversion > 0.8:
            self.current_regime = MarketRegime.SIDEWAYS
        else:
            self.current_regime = MarketRegime.LOW_VOL
        
        logger.info(f"Market regime updated to: {self.current_regime.value}")
    
    def _calculate_trend_strength(self, prices: pd.Series) -> float:
        """Calculate trend strength using linear regression"""
        if len(prices) < 20:
            return 0.0
        
        x = np.arange(len(prices))
        y = prices.values
        
        slope, _, r_value, _, _ = stats.linregress(x, y)
        
        # Normalize slope and combine with R²
        normalized_slope = slope / prices.mean()
        trend_strength = normalized_slope * r_value ** 2
        
        return float(trend_strength)
    
    def _calculate_mean_reversion(self, prices: pd.Series) -> float:
        """Calculate mean reversion tendency using Hurst exponent"""
        if len(prices) < 50:
            return 0.0
        
        # Simplified mean reversion calculation
        returns = prices.pct_change().dropna()
        acf_1 = returns.autocorr(lag=1)
        
        # Convert to 0-1 scale where 1 indicates strong mean reversion
        mean_reversion = (1 - abs(acf_1)) if acf_1 is not None else 0.5
        
        return float(mean_reversion)
    
    def generate_strategy_ideas(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate new strategy ideas based on current market conditions
        
        Args:
            count: Number of strategy ideas to generate
            
        Returns:
            List of strategy ideas with metadata
        """
        ideas = []
        
        for i in range(count):
            # Base strategy type selection based on market regime
            base_strategy = self._select_base_strategy_type()
            
            # Generate unique parameters
            parameters = self._generate_strategy_parameters(base_strategy)
            
            # Create strategy idea
            idea = {
                'strategy_id': f"idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                'strategy_type': base_strategy,
                'parameters': parameters,
                'expected_regimes': [self.current_regime],
                'confidence_estimate': np.random.uniform(0.3, 0.8),
                'complexity_score': np.random.uniform(0.2, 0.9)
            }
            
            ideas.append(idea)
        
        logger.info(f"Generated {len(ideas)} new strategy ideas")
        return ideas
    
    def _select_base_strategy_type(self) -> StrategyType:
        """Select base strategy type based on current market regime"""
        regime_strategy_map = {
            MarketRegime.BULL: [StrategyType.MOMENTUM, StrategyType.TREND_FOLLOWING],
            MarketRegime.BEAR: [StrategyType.MOMENTUM, StrategyType.BREAKOUT],
            MarketRegime.SIDEWAYS: [StrategyType.MEAN_REVERSION, StrategyType.MARKET_NEUTRAL],
            MarketRegime.HIGH_VOL: [StrategyType.VOLATILITY, StrategyType.BREAKOUT],
            MarketRegime.LOW_VOL: [StrategyType.MEAN_REVERSION, StrategyType.MARKET_NEUTRAL],
            MarketRegime.CRISIS: [StrategyType.VOLATILITY, StrategyType.BREAKOUT]
        }
        
        available_strategies = regime_strategy_map.get(self.current_regime, 
                                                     [StrategyType.MOMENTUM, StrategyType.MEAN_REVERSION])
        
        return np.random.choice(available_strategies)
    
    def _generate_strategy_parameters(self, strategy_type: StrategyType) -> Dict[str, StrategyParameter]:
        """Generate strategy parameters based on strategy type"""
        if strategy_type == StrategyType.MOMENTUM:
            return {
                "lookback_period": StrategyParameter("lookback_period", 
                                                   np.random.randint(10, 30),
                                                   5, 50, 1),
                "momentum_threshold": StrategyParameter("momentum_threshold",
                                                      np.random.uniform(0.01, 0.05),
                                                      0.005, 0.1, 0.002),
                "exit_threshold": StrategyParameter("exit_threshold",
                                                  np.random.uniform(-0.02, -0.005),
                                                  -0.05, -0.001, 0.002)
            }
        elif strategy_type == StrategyType.MEAN_REVERSION:
            return {
                "mean_period": StrategyParameter("mean_period",
                                               np.random.randint(20, 60),
                                               10, 100, 5),
                "std_dev_threshold": StrategyParameter("std_dev_threshold",
                                                     np.random.uniform(1.5, 2.5),
                                                     1.0, 3.0, 0.1),
                "reversion_period": StrategyParameter("reversion_period",
                                                    np.random.randint(5, 15),
                                                    3, 30, 1)
            }
        else:
            # Default parameters for other strategy types
            return {
                "lookback_period": StrategyParameter("lookback_period", 20, 5, 50, 1),
                "threshold": StrategyParameter("threshold", 0.02, 0.005, 0.05, 0.005)
            }
    
    def develop_strategy(self, strategy_idea: Dict[str, Any]) -> TradingStrategy:
        """
        Develop a complete trading strategy from an idea
        
        Args:
            strategy_idea: Strategy idea generated by generate_strategy_ideas
            
        Returns:
            Developed trading strategy
        """
        start_time = datetime.now()
        
        strategy = TradingStrategy(
            strategy_id=strategy_idea['strategy_id'],
            strategy_type=strategy_idea['strategy_type'],
            parameters=strategy_idea['parameters'],
            performance_metrics={},
            market_regimes=strategy_idea['expected_regimes'],
            status=ResearchStatus.DEVELOPING
        )
        
        # Optimize parameters
        optimized_strategy = self._optimize_strategy_parameters(strategy)
        
        # Backtest strategy
        backtest_results = self._backtest_strategy(optimized_strategy)
        
        # Update strategy with results
        optimized_strategy.performance_metrics = backtest_results
        optimized_strategy.confidence = self._calculate_strategy_confidence(backtest_results)
        optimized_strategy.status = ResearchStatus.BACKTESTING
        optimized_strategy.updated_at = datetime.now()
        
        # Store strategy
        self.strategies[strategy_idea['strategy_id']] = optimized_strategy
        self.research_metrics['strategies_developed'] += 1
        
        development_time = datetime.now() - start_time
        self.research_metrics['average_development_time'] = (
            (self.research_metrics['average_development_time'] * 
             (self.research_metrics['strategies_developed'] - 1) + development_time) /
            self.research_metrics['strategies_developed']
        )
        
        logger.info(f"Developed strategy {strategy_idea['strategy_id']} "
                   f"with confidence {optimized_strategy.confidence:.3f}")
        
        return optimized_strategy
    
    def _optimize_strategy_parameters(self, strategy: TradingStrategy) -> TradingStrategy:
        """
        Optimize strategy parameters using machine learning
        
        Args:
            strategy: Strategy to optimize
            
        Returns:
            Optimized strategy
        """
        best_strategy = strategy
        best_performance = -np.inf
        
        # Simple parameter optimization (in production, use Bayesian optimization)
        for iteration in range(self.research_config['optimization_iterations']):
            # Create parameter variations
            test_strategy = self._create_parameter_variation(strategy)
            
            # Quick backtest to evaluate performance
            try:
                performance = self._quick_evaluate_strategy(test_strategy)
                
                if performance > best_performance:
                    best_performance = performance
                    best_strategy = test_strategy
            except Exception as e:
                logger.warning(f"Strategy evaluation failed: {e}")
                continue
        
        # Mark optimized parameters
        for param_name in best_strategy.parameters:
            best_strategy.parameters[param_name].optimized = True
        
        return best_strategy
    
    def _create_parameter_variation(self, strategy: TradingStrategy) -> TradingStrategy:
        """Create a parameter variation for optimization"""
        variation = TradingStrategy(
            strategy_id=f"{strategy.strategy_id}_var",
            strategy_type=strategy.strategy_type,
            parameters={},
            performance_metrics={},
            market_regimes=strategy.market_regimes,
            status=ResearchStatus.DEVELOPING
        )
        
        # Create parameter variations
        for param_name, param in strategy.parameters.items():
            # Add random variation within bounds
            variation_range = (param.max_value - param.min_value) * 0.1
            new_value = param.value + np.random.uniform(-variation_range, variation_range)
            
            # Clamp to bounds
            new_value = max(param.min_value, min(param.max_value, new_value))
            
            variation.parameters[param_name] = StrategyParameter(
                name=param.name,
                value=new_value,
                min_value=param.min_value,
                max_value=param.max_value,
                step=param.step
            )
        
        return variation
    
    def _quick_evaluate_strategy(self, strategy: TradingStrategy) -> float:
        """Quick evaluation of strategy performance"""
        if not self.market_data_buffer:
            return 0.0
        
        # Use most recent market data for quick evaluation
        recent_data = self.market_data_buffer[-1]['data']
        
        try:
            # Simulate strategy execution
            returns = self._simulate_strategy_execution(strategy, recent_data)
            
            if len(returns) < 5:
                return 0.0
            
            # Calculate simple performance metric
            sharpe = returns.mean() / returns.std() if returns.std() > 0 else 0
            win_rate = (returns > 0).mean()
            
            return sharpe * win_rate
            
        except Exception as e:
            logger.warning(f"Quick strategy evaluation failed: {e}")
            return 0.0
    
    def _backtest_strategy(self, strategy: TradingStrategy) -> Dict[str, float]:
        """
        Comprehensive backtesting of strategy
        
        Args:
            strategy: Strategy to backtest
            
        Returns:
            Performance metrics dictionary
        """
        if not self.market_data_buffer:
            return {}
        
        all_returns = []
        
        for market_data in self.market_data_buffer:
            try:
                returns = self._simulate_strategy_execution(strategy, market_data['data'])
                all_returns.extend(returns)
            except Exception as e:
                logger.warning(f"Backtest failed for {market_data['symbol']}: {e}")
                continue
        
        if not all_returns:
            return {}
        
        returns_series = pd.Series(all_returns)
        
        # Calculate comprehensive metrics
        metrics = {
            'sharpe_ratio': returns_series.mean() / returns_series.std() if returns_series.std() > 0 else 0,
            'total_return': returns_series.sum(),
            'win_rate': (returns_series > 0).mean(),
            'max_drawdown': self._calculate_max_drawdown(returns_series),
            'profit_factor': returns_series[returns_series > 0].sum() / 
                           abs(returns_series[returns_series < 0].sum()) if returns_series[returns_series < 0].sum() < 0 else float('inf'),
            'avg_win': returns_series[returns_series > 0].mean(),
            'avg_loss': returns_series[returns_series < 0].mean(),
            'volatility': returns_series.std()
        }
        
        return metrics
    
    def _simulate_strategy_execution(self, strategy: TradingStrategy, 
                                   price_data: pd.DataFrame) -> List[float]:
        """
        Simulate strategy execution on price data
        
        Args:
            strategy: Strategy to simulate
            price_data: OHLCV price data
            
        Returns:
            List of returns
        """
        returns = []
        
        if strategy.strategy_type == StrategyType.MOMENTUM:
            returns = self._simulate_momentum_strategy(strategy, price_data)
        elif strategy.strategy_type == StrategyType.MEAN_REVERSION:
            returns = self._simulate_mean_reversion_strategy(strategy, price_data)
        else:
            # Default simulation for other strategy types
            returns = self._simulate_generic_strategy(strategy, price_data)
        
        return returns
    
    def _simulate_momentum_strategy(self, strategy: TradingStrategy,
                                  price_data: pd.DataFrame) -> List[float]:
        """Simulate momentum strategy execution"""
        lookback = int(strategy.parameters['lookback_period'].value)
        threshold = strategy.parameters['momentum_threshold'].value
        
        if len(price_data) < lookback + 1:
            return []
        
        returns = []
        position = 0
        entry_price = 0
        
        for i in range(lookback, len(price_data)):
            # Calculate momentum
            past_prices = price_data['close'].iloc[i-lookback:i]
            current_price = price_data['close'].iloc[i]
            
            momentum = (current_price - past_prices.iloc[0]) / past_prices.iloc[0]
            
            # Trading logic
            if position == 0 and momentum > threshold:
                # Enter long position
                position = 1
                entry_price = current_price
            elif position == 1 and momentum < -threshold:
                # Exit position
                returns.append((current_price - entry_price) / entry_price)
                position = 0
        
        return returns
    
    def _simulate_mean_reversion_strategy(self, strategy: TradingStrategy,
                                        price_data: pd.DataFrame) -> List[float]:
        """Simulate mean reversion strategy execution"""
        lookback = int(strategy.parameters['mean_period'].value)
        threshold = strategy.parameters['std_dev_threshold'].value
        
        if len(price_data) < lookback + 1:
            return []
        
        returns = []
        position = 0
        entry_price = 0
        
        for i in range(lookback, len(price_data)):
            # Calculate mean and standard deviation
            past_prices = price_data['close'].iloc[i-lookback:i]
            current_price = price_data['close'].iloc[i]
            
            mean_price = past_prices.mean()
            std_price = past_prices.std()
            
            z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
            
            # Trading logic
            if position == 0 and z_score < -threshold:
                # Buy when price is below mean
                position = 1
                entry_price = current_price
            elif position == 0 and z_score > threshold:
                # Sell when price is above mean
                position = -1
                entry_price = current_price
            elif position != 0 and abs(z_score) < 0.5:
                # Exit when price reverts to mean
                if position == 1:
                    returns.append((current_price - entry_price) / entry_price)
                else:
                    returns.append((entry_price - current_price) / entry_price)
                position = 0
        
        return returns
    
    def _simulate_generic_strategy(self, strategy: TradingStrategy,
                                 price_data: pd.DataFrame) -> List[float]:
        """Generic strategy simulation"""
        # Simple random walk simulation for demonstration
        returns = np.random.normal(0, 0.01, min(100, len(price_data) - 10))
        return returns.tolist()
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown from returns series"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _calculate_strategy_confidence(self, metrics: Dict[str, float]) -> float:
        """Calculate confidence score for strategy"""
        if not metrics:
            return 0.0
        
        sharpe = metrics.get('sharpe_ratio', 0)
        win_rate = metrics.get('win_rate', 0)
        max_dd = abs(metrics.get('max_drawdown', 0))
        
        # Base confidence calculation
        confidence = sharpe * win_rate
        
        # Penalize high drawdowns
        if max_dd > self.research_config['max_drawdown_threshold']:
            confidence *= 0.5
        
        return max(0.0, min(1.0, confidence))
    
    def validate_strategy(self, strategy_id: str, validation_period: int = None) -> ResearchResult:
        """
        Validate strategy on out-of-sample data
        
        Args:
            strategy_id: Strategy to validate
            validation_period: Validation period in days
            
        Returns:
            Validation results
        """
        if strategy_id not in self.strategies:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        strategy = self.strategies[strategy_id]
        validation_period = validation_period or self.research_config['validation_period']
        
        # Use older data for validation (simulated)
        validation_data = self.market_data_buffer[:max(1, len(self.market_data_buffer) // 2)]
        
        validation_returns = []
        for market_data in validation_data:
            try:
                returns = self._simulate_strategy_execution(strategy, market_data['data'])
                validation_returns.extend(returns)
            except Exception as e:
                logger.warning(f"Validation failed for {market_data['symbol']}: {e}")
                continue
        
        if not validation_returns:
            raise ValueError("No validation data available")
        
        returns_series = pd.Series(validation_returns)
        
        # Calculate validation metrics
        sharpe = returns_series.mean() / returns_series.std() if returns_series.std() > 0 else 0
        max_dd = self._calculate_max_drawdown(returns_series)
        win_rate = (returns_series > 0).mean()
        
        # Overall performance score
        performance_score = sharpe * win_rate * (1 - max_dd)
        
        result = ResearchResult(
            strategy_id=strategy_id,
            performance_score=performance_score,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
            parameters={name: param.value for name, param in strategy.parameters.items()},
            market_regime=self.current_regime,
            backtest_period=timedelta(days=validation_period),
            validation_score=performance_score
        )
        
        self.research_results[strategy_id] = result
        
        # Update strategy status
        if performance_score > self.research_config['min_performance_threshold']:
            strategy.status = ResearchStatus.READY
            strategy.confidence = performance_score
            self.research_metrics['strategies_validated'] += 1
        else:
            strategy.status = ResearchStatus.FAILED
        
        strategy.updated_at = datetime.now()
        
        logger.info(f"Validated strategy {strategy_id}: score={performance_score:.3f}, "
                   f"status={strategy.status.value}")
        
        return result
    
    def get_top_strategies(self, count: int = 10) -> List[Tuple[str, float]]:
        """Get top performing strategies by confidence score"""
        valid_strategies = [
            (strategy_id, strategy.confidence)
            for strategy_id, strategy in self.strategies.items()
            if strategy.status == ResearchStatus.READY
        ]
        
        return sorted(valid_strategies, key=lambda x: x[1], reverse=True)[:count]
    
    def get_research_metrics(self) -> Dict[str, Any]:
        """Get comprehensive research metrics"""
        return {
            **self.research_metrics,
            'total_strategies': len(self.strategies),
            'ready_strategies': len([s for s in self.strategies.values() 
                                   if s.status == ResearchStatus.READY]),
            'current_regime': self.current_regime.value,
            'market_data_points': len(self.market_data_buffer),
            'top_strategy_score': max([s.confidence for s in self.strategies.values()]) 
                                if self.strategies else 0.0
        }

# Example usage and testing
async def main():
    """Example usage of the Strategy Researcher"""
    researcher = StrategyResearcher()
    
    # Generate sample market data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.cumsum(np.random.normal(0, 1, len(dates))),
        'high': 100 + np.cumsum(np.random.normal(0, 1.2, len(dates))),
        'low': 100 + np.cumsum(np.random.normal(0, 0.8, len(dates))),
        'close': 100 + np.cumsum(np.random.normal(0, 1, len(dates))),
        'volume': np.random.randint(1000000, 5000000, len(dates))
    }).set_index('date')
    
    # Ingest market data
    researcher.ingest_market_data("TEST", sample_data)
    
    # Generate strategy ideas
    ideas = researcher.generate_strategy_ideas(3)
    print(f"Generated {len(ideas)} strategy ideas")
    
    # Develop strategies
    developed_strategies = []
    for idea in ideas:
        try:
            strategy = researcher.develop_strategy(idea)
            developed_strategies.append(strategy)
            print(f"Developed: {strategy.strategy_id} "
                  f"(Type: {strategy.strategy_type.value}, "
                  f"Confidence: {strategy.confidence:.3f})")
        except Exception as e:
            print(f"Failed to develop {idea['strategy_id']}: {e}")
    
    # Validate strategies
    for strategy in developed_strategies:
        try:
            result = researcher.validate_strategy(strategy.strategy_id)
            print(f"Validated: {result.strategy_id} "
                  f"(Score: {result.validation_score:.3f}, "
                  f"Sharpe: {result.sharpe_ratio:.3f})")
        except Exception as e:
            print(f"Failed to validate {strategy.strategy_id}: {e}")
    
    # Display research metrics
    metrics = researcher.get_research_metrics()
    print(f"\nResearch Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Display top strategies
    top_strategies = researcher.get_top_strategies(5)
    print(f"\nTop Strategies:")
    for i, (strategy_id, confidence) in enumerate(top_strategies, 1):
        print(f"  {i}. {strategy_id}: {confidence:.3f}")

if __name__ == "__main__":
    asyncio.run(main())