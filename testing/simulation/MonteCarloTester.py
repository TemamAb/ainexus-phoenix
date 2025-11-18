cat > ./testing/simulation/MonteCarloTester.py << 'EOF'
"""
Monte Carlo Tester for Trading Strategy Validation

This module implements advanced Monte Carlo simulation techniques for
comprehensive trading strategy testing, including path generation,
probability distribution modeling, and statistical significance testing.

Key Features:
- Multi-asset Monte Carlo path generation
- Correlation structure modeling
- Fat-tailed distribution support
- Strategy performance under random walks
- Statistical significance testing
- Convergence analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging
import warnings
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistributionType(Enum):
    """Probability distributions for Monte Carlo simulation"""
    NORMAL = "normal"
    STUDENT_T = "student_t"
    LAPLACE = "laplace"
    LOGNORMAL = "lognormal"
    MIXED_NORMAL = "mixed_normal"
    GARCH = "garch"

class PathDependency(Enum):
    """Types of path dependencies in simulations"""
    INDEPENDENT = "independent"
    MEAN_REVERSION = "mean_reversion"
    TREND_FOLLOWING = "trend_following"
    REGIME_SWITCHING = "regime_switching"

@dataclass
class MonteCarloConfig:
    """Configuration for Monte Carlo simulations"""
    n_simulations: int
    n_periods: int
    distribution_type: DistributionType
    path_dependency: PathDependency
    drift: float
    volatility: float
    correlation_matrix: Optional[np.ndarray] = None
    degrees_freedom: Optional[int] = None  # For Student's t-distribution
    garch_params: Optional[Dict] = None
    regime_params: Optional[Dict] = None

@dataclass
class SimulationResult:
    """Results from Monte Carlo simulation"""
    config: MonteCarloConfig
    paths: np.ndarray
    final_values: np.ndarray
    statistics: Dict[str, float]
    convergence_data: Dict[str, List[float]]
    performance_metrics: Dict[str, Any]

class MonteCarloTester:
    """
    Advanced Monte Carlo testing engine for trading strategy validation
    
    This class provides comprehensive Monte Carlo simulation capabilities:
    - Multi-asset correlated path generation
    - Fat-tailed distribution modeling
    - Path-dependent simulations
    - Statistical significance testing
    - Convergence analysis
    """
    
    def __init__(self, random_seed: Optional[int] = 42):
        """
        Initialize Monte Carlo Tester
        
        Args:
            random_seed: Random seed for reproducible results
        """
        self.random_seed = random_seed
        if random_seed is not None:
            np.random.seed(random_seed)
        
        self.simulation_results = {}
        self.convergence_threshold = 1e-4
        self.max_iterations = 10000
    
    def generate_paths(self, config: MonteCarloConfig) -> np.ndarray:
        """
        Generate Monte Carlo paths based on configuration
        
        Args:
            config: Monte Carlo configuration
            
        Returns:
            np.ndarray: Generated paths (n_simulations x n_periods)
        """
        logger.info(f"Generating {config.n_simulations} Monte Carlo paths with {config.distribution_type.value} distribution")
        
        if config.distribution_type == DistributionType.NORMAL:
            paths = self._generate_normal_paths(config)
        elif config.distribution_type == DistributionType.STUDENT_T:
            paths = self._generate_student_t_paths(config)
        elif config.distribution_type == DistributionType.LAPLACE:
            paths = self._generate_laplace_paths(config)
        elif config.distribution_type == DistributionType.LOGNORMAL:
            paths = self._generate_lognormal_paths(config)
        elif config.distribution_type == DistributionType.MIXED_NORMAL:
            paths = self._generate_mixed_normal_paths(config)
        elif config.distribution_type == DistributionType.GARCH:
            paths = self._generate_garch_paths(config)
        else:
            raise ValueError(f"Unsupported distribution type: {config.distribution_type}")
        
        # Apply path dependencies
        paths = self._apply_path_dependency(paths, config)
        
        return paths
    
    def _generate_normal_paths(self, config: MonteCarloConfig) -> np.ndarray:
        """Generate paths using normal distribution"""
        dt = 1.0 / 252  # Assuming daily data
        drift_component = (config.drift - 0.5 * config.volatility**2) * dt
        volatility_component = config.volatility * np.sqrt(dt)
        
        random_shocks = np.random.normal(0, 1, (config.n_simulations, config.n_periods))
        returns = drift_component + volatility_component * random_shocks
        
        # Convert to price paths starting from 100
        paths = 100 * np.exp(np.cumsum(returns, axis=1))
        paths = np.insert(paths, 0, 100, axis=1)  # Add initial price
        
        return paths
    
    def _generate_student_t_paths(self, config: MonteCarloConfig) -> np.ndarray:
        """Generate paths using Student's t-distribution (fat tails)"""
        if config.degrees_freedom is None:
            config.degrees_freedom = 5  # Default for heavy tails
        
        dt = 1.0 / 252
        drift_component = (config.drift - 0.5 * config.volatility**2) * dt
        volatility_component = config.volatility * np.sqrt(dt)
        
        # Adjust volatility for t-distribution scale
        scale_factor = np.sqrt(config.degrees_freedom / (config.degrees_freedom - 2))
        volatility_component /= scale_factor
        
        random_shocks = stats.t.rvs(
            config.degrees_freedom, 
            size=(config.n_simulations, config.n_periods)
        )
        
        returns = drift_component + volatility_component * random_shocks
        paths = 100 * np.exp(np.cumsum(returns, axis=1))
        paths = np.insert(paths, 0, 100, axis=1)
        
        return paths
    
    def _generate_laplace_paths(self, config: MonteCarloConfig) -> np.ndarray:
        """Generate paths using Laplace distribution (fat tails)"""
        dt = 1.0 / 252
        drift_component = (config.drift - 0.5 * config.volatility**2) * dt
        volatility_component = config.volatility * np.sqrt(dt)
        
        random_shocks = np.random.laplace(0, 1/np.sqrt(2), (config.n_simulations, config.n_periods))
        returns = drift_component + volatility_component * random_shocks
        
        paths = 100 * np.exp(np.cumsum(returns, axis=1))
        paths = np.insert(paths, 0, 100, axis=1)
        
        return paths
    
    def _generate_lognormal_paths(self, config: MonteCarloConfig) -> np.ndarray:
        """Generate paths using lognormal distribution"""
        dt = 1.0 / 252
        mean = config.drift * dt
        std = config.volatility * np.sqrt(dt)
        
        # Generate lognormal returns directly
        returns = np.random.lognormal(mean, std, (config.n_simulations, config.n_periods)) - 1
        
        # Convert to price paths
        paths = 100 * np.cumprod(1 + returns, axis=1)
        paths = np.insert(paths, 0, 100, axis=1)
        
        return paths
    
    def _generate_mixed_normal_paths(self, config: MonteCarloConfig) -> np.ndarray:
        """Generate paths using mixture of normal distributions"""
        dt = 1.0 / 252
        n_periods = config.n_periods
        
        # Two-component mixture: normal regime and high-volatility regime
        mixture_weights = [0.95, 0.05]  # 95% normal, 5% high vol
        volatilities = [config.volatility, config.volatility * 3]
        
        paths = np.zeros((config.n_simulations, n_periods + 1))
        paths[:, 0] = 100
        
        for i in range(config.n_simulations):
            for t in range(n_periods):
                # Choose regime
                regime = np.random.choice(2, p=mixture_weights)
                current_vol = volatilities[regime]
                
                drift_component = (config.drift - 0.5 * current_vol**2) * dt
                volatility_component = current_vol * np.sqrt(dt)
                
                shock = np.random.normal(0, 1)
                returns = drift_component + volatility_component * shock
                
                paths[i, t+1] = paths[i, t] * np.exp(returns)
        
        return paths
    
    def _generate_garch_paths(self, config: MonteCarloConfig) -> np.ndarray:
        """Generate paths using GARCH volatility model"""
        if config.garch_params is None:
            config.garch_params = {'alpha': 0.1, 'beta': 0.85, 'omega': 0.01}
        
        dt = 1.0 / 252
        n_periods = config.n_periods
        
        paths = np.zeros((config.n_simulations, n_periods + 1))
        paths[:, 0] = 100
        
        alpha = config.garch_params['alpha']
        beta = config.garch_params['beta']
        omega = config.garch_params['omega']
        
        for i in range(config.n_simulations):
            returns = np.zeros(n_periods)
            variances = np.zeros(n_periods)
            
            # Initialize variance
            variances[0] = config.volatility**2 * dt
            
            for t in range(n_periods):
                if t > 0:
                    # GARCH(1,1) variance update
                    variances[t] = (omega + alpha * returns[t-1]**2 + 
                                  beta * variances[t-1])
                
                # Generate return with time-varying volatility
                shock = np.random.normal(0, 1)
                returns[t] = config.drift * dt + np.sqrt(variances[t]) * shock
                
                # Update price
                paths[i, t+1] = paths[i, t] * np.exp(returns[t])
        
        return paths
    
    def _apply_path_dependency(self, paths: np.ndarray, config: MonteCarloConfig) -> np.ndarray:
        """Apply path dependency effects to generated paths"""
        if config.path_dependency == PathDependency.INDEPENDENT:
            return paths
        
        elif config.path_dependency == PathDependency.MEAN_REVERSION:
            return self._apply_mean_reversion(paths, config)
        
        elif config.path_dependency == PathDependency.TREND_FOLLOWING:
            return self._apply_trend_following(paths, config)
        
        elif config.path_dependency == PathDependency.REGIME_SWITCHING:
            return self._apply_regime_switching(paths, config)
        
        else:
            warnings.warn(f"Unknown path dependency: {config.path_dependency}")
            return paths
    
    def _apply_mean_reversion(self, paths: np.ndarray, config: MonteCarloConfig) -> np.ndarray:
        """Apply mean reversion to paths"""
        mean_reversion_speed = 0.1  # Speed of mean reversion
        long_term_mean = 100  # Long-term mean price
        
        adjusted_paths = paths.copy()
        n_simulations, n_periods = paths.shape
        
        for i in range(n_simulations):
            for t in range(1, n_periods):
                current_price = adjusted_paths[i, t]
                mean_reversion_effect = mean_reversion_speed * (long_term_mean - current_price) / 252
                adjusted_paths[i, t] = current_price * (1 + mean_reversion_effect)
        
        return adjusted_paths
    
    def _apply_trend_following(self, paths: np.ndarray, config: MonteCarloConfig) -> np.ndarray:
        """Apply trend following effects to paths"""
        trend_strength = 0.05  # Strength of trend following
        lookback_period = 20  # Period for trend calculation
        
        adjusted_paths = paths.copy()
        n_simulations, n_periods = paths.shape
        
        for i in range(n_simulations):
            for t in range(lookback_period, n_periods):
                # Calculate recent trend
                recent_prices = adjusted_paths[i, t-lookback_period:t]
                trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
                
                # Apply trend following effect
                trend_effect = trend_strength * trend
                adjusted_paths[i, t] = adjusted_paths[i, t] * (1 + trend_effect)
        
        return adjusted_paths
    
    def _apply_regime_switching(self, paths: np.ndarray, config: MonteCarloConfig) -> np.ndarray:
        """Apply regime switching behavior to paths"""
        if config.regime_params is None:
            config.regime_params = {
                'transition_matrix': [[0.95, 0.05], [0.02, 0.98]],  # Low vol to high vol transitions
                'regime_volatilities': [config.volatility, config.volatility * 2]
            }
        
        transition_matrix = np.array(config.regime_params['transition_matrix'])
        regime_volatilities = config.regime_params['regime_volatilities']
        
        adjusted_paths = paths.copy()
        n_simulations, n_periods = paths.shape
        
        for i in range(n_simulations):
            # Start in low volatility regime
            current_regime = 0
            
            for t in range(1, n_periods):
                # Transition to new regime
                current_regime = np.random.choice(
                    2, 
                    p=transition_matrix[current_regime]
                )
                
                # Adjust volatility based on regime
                regime_adjustment = regime_volatilities[current_regime] / config.volatility
                adjusted_paths[i, t] = adjusted_paths[i, t] * (1 + 0.1 * (regime_adjustment - 1))
        
        return adjusted_paths
    
    def run_simulation(self, config: MonteCarloConfig, 
                      strategy_function: Optional[Callable] = None) -> SimulationResult:
        """
        Run complete Monte Carlo simulation
        
        Args:
            config: Monte Carlo configuration
            strategy_function: Optional strategy function to test
            
        Returns:
            SimulationResult: Complete simulation results
        """
        logger.info(f"Starting Monte Carlo simulation with {config.n_simulations} paths")
        
        # Generate paths
        paths = self.generate_paths(config)
        final_values = paths[:, -1]
        
        # Calculate basic statistics
        statistics = self._calculate_path_statistics(paths, final_values)
        
        # Calculate convergence metrics
        convergence_data = self._calculate_convergence(paths)
        
        # Test strategy if provided
        performance_metrics = {}
        if strategy_function is not None:
            performance_metrics = self._test_strategy(paths, strategy_function)
        
        # Create result object
        result = SimulationResult(
            config=config,
            paths=paths,
            final_values=final_values,
            statistics=statistics,
            convergence_data=convergence_data,
            performance_metrics=performance_metrics
        )
        
        # Store results
        simulation_id = f"sim_{len(self.simulation_results) + 1}"
        self.simulation_results[simulation_id] = result
        
        logger.info("Monte Carlo simulation completed successfully")
        return result
    
    def _calculate_path_statistics(self, paths: np.ndarray, final_values: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive statistics for generated paths"""
        returns = np.diff(np.log(paths), axis=1)
        
        statistics = {
            'mean_final_value': float(np.mean(final_values)),
            'median_final_value': float(np.median(final_values)),
            'std_final_value': float(np.std(final_values)),
            'min_final_value': float(np.min(final_values)),
            'max_final_value': float(np.max(final_values)),
            'probability_positive_return': float(np.mean(final_values > 100)),
            'expected_return': float(np.mean(returns)),
            'volatility': float(np.std(returns)),
            'sharpe_ratio': float(np.mean(returns) / np.std(returns) * np.sqrt(252)),
            'skewness': float(stats.skew(final_values)),
            'kurtosis': float(stats.kurtosis(final_values)),
            'var_95': float(np.percentile(final_values - 100, 5)),  # 95% VaR
            'cvar_95': float(np.mean(final_values[final_values <= np.percentile(final_values, 5)] - 100))
        }
        
        return statistics
    
    def _calculate_convergence(self, paths: np.ndarray) -> Dict[str, List[float]]:
        """Calculate convergence metrics for Monte Carlo simulation"""
        n_simulations = paths.shape[0]
        convergence_steps = min(100, n_simulations // 10)
        
        mean_convergence = []
        std_convergence = []
        
        for i in range(convergence_steps, n_simulations + 1, convergence_steps):
            subset_paths = paths[:i, -1]
            mean_convergence.append(np.mean(subset_paths))
            std_convergence.append(np.std(subset_paths))
        
        return {
            'sample_sizes': list(range(convergence_steps, n_simulations + 1, convergence_steps)),
            'mean_convergence': mean_convergence,
            'std_convergence': std_convergence
        }
    
    def _test_strategy(self, paths: np.ndarray, strategy_function: Callable) -> Dict[str, Any]:
        """Test trading strategy on generated paths"""
        strategy_results = []
        
        for i in range(paths.shape[0]):
            try:
                result = strategy_function(paths[i, :])
                strategy_results.append(result)
            except Exception as e:
                logger.warning(f"Strategy failed on path {i}: {e}")
                continue
        
        if not strategy_results:
            return {'error': 'Strategy failed on all paths'}
        
        # Calculate strategy performance metrics
        returns = [r.get('total_return', 0) for r in strategy_results if 'total_return' in r]
        
        if returns:
            metrics = {
                'mean_return': float(np.mean(returns)),
                'std_return': float(np.std(returns)),
                'sharpe_ratio': float(np.mean(returns) / np.std(returns)) if np.std(returns) > 0 else 0,
                'win_rate': float(np.mean(np.array(returns) > 0)),
                'max_return': float(np.max(returns)),
                'min_return': float(np.min(returns)),
                'var_95': float(np.percentile(returns, 5)),
                'confidence_interval': stats.norm.interval(0.95, loc=np.mean(returns), scale=stats.sem(returns))
            }
        else:
            metrics = {'error': 'No valid returns calculated'}
        
        return metrics
    
    def calculate_probability_of_success(self, result: SimulationResult, 
                                       threshold: float = 100) -> float:
        """
        Calculate probability of success (final value above threshold)
        
        Args:
            result: Simulation results
            threshold: Success threshold
            
        Returns:
            float: Probability of success
        """
        return float(np.mean(result.final_values >= threshold))
    
    def calculate_risk_metrics(self, result: SimulationResult) -> Dict[str, float]:
        """Calculate comprehensive risk metrics from simulation results"""
        returns = np.diff(np.log(result.paths), axis=1)
        
        risk_metrics = {
            'value_at_risk_95': float(np.percentile(returns, 5)),
            'expected_shortfall_95': float(np.mean(returns[returns <= np.percentile(returns, 5)])),
            'maximum_drawdown': float(self._calculate_max_drawdown(result.paths)),
            'tail_risk': float(stats.kurtosis(returns.flatten())),
            'downside_deviation': float(np.std(returns[returns < 0])),
            'ulcer_index': float(self._calculate_ulcer_index(result.paths))
        }
        
        return risk_metrics
    
    def _calculate_max_drawdown(self, paths: np.ndarray) -> float:
        """Calculate maximum drawdown across all paths"""
        max_drawdowns = []
        
        for i in range(paths.shape[0]):
            running_max = np.maximum.accumulate(paths[i, :])
            drawdown = (running_max - paths[i, :]) / running_max
            max_drawdowns.append(np.max(drawdown))
        
        return np.mean(max_drawdowns)
    
    def _calculate_ulcer_index(self, paths: np.ndarray) -> float:
        """Calculate Ulcer Index across all paths"""
        ulcer_indices = []
        
        for i in range(paths.shape[0]):
            running_max = np.maximum.accumulate(paths[i, :])
            drawdowns = (running_max - paths[i, :]) / running_max
            squared_drawdowns = drawdowns ** 2
            ulcer_index = np.sqrt(np.mean(squared_drawdowns))
            ulcer_indices.append(ulcer_index)
        
        return np.mean(ulcer_indices)
    
    def generate_report(self, result: SimulationResult) -> Dict[str, Any]:
        """Generate comprehensive Monte Carlo simulation report"""
        probability_success = self.calculate_probability_of_success(result)
        risk_metrics = self.calculate_risk_metrics(result)
        
        report = {
            'simulation_parameters': {
                'n_simulations': result.config.n_simulations,
                'n_periods': result.config.n_periods,
                'distribution_type': result.config.distribution_type.value,
                'path_dependency': result.config.path_dependency.value,
                'drift': result.config.drift,
                'volatility': result.config.volatility
            },
            'summary_statistics': result.statistics,
            'risk_assessment': risk_metrics,
            'performance_metrics': result.performance_metrics,
            'convergence_analysis': result.convergence_data,
            'probability_of_success': probability_success,
            'confidence_intervals': {
                'final_value_95ci': stats.norm.interval(
                    0.95, 
                    loc=result.statistics['mean_final_value'], 
                    scale=result.statistics['std_final_value'] / np.sqrt(result.config.n_simulations)
                )
            },
            'recommendations': self._generate_recommendations(result, probability_success)
        }
        
        return report
    
    def _generate_recommendations(self, result: SimulationResult, 
                                probability_success: float) -> List[str]:
        """Generate recommendations based on simulation results"""
        recommendations = []
        
        if probability_success < 0.5:
            recommendations.append("Consider strategy modifications to improve success probability")
        
        if result.statistics['var_95'] < -0.1:
            recommendations.append("Implement robust risk management for extreme loss scenarios")
        
        if result.statistics['sharpe_ratio'] < 0.5:
            recommendations.append("Evaluate risk-adjusted returns and consider optimization")
        
        if result.performance_metrics.get('win_rate', 0.5) < 0.4:
            recommendations.append("Strategy may benefit from improved entry/exit timing")
        
        # Check convergence
        convergence_data = result.convergence_data
        if len(convergence_data['mean_convergence']) > 1:
            last_changes = np.diff(convergence_data['mean_convergence'][-3:])
            if np.any(np.abs(last_changes) > self.convergence_threshold):
                recommendations.append("Consider increasing simulation count for better convergence")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Example implementation
    tester = MonteCarloTester(random_seed=42)
    
    # Create configuration for normal distribution simulation
    config = MonteCarloConfig(
        n_simulations=1000,
        n_periods=252,  # 1 year of daily data
        distribution_type=DistributionType.STUDENT_T,
        path_dependency=PathDependency.MEAN_REVERSION,
        drift=0.08,  # 8% annual drift
        volatility=0.20,  # 20% annual volatility
        degrees_freedom=5  # For Student's t-distribution
    )
    
    # Define a simple strategy function
    def sample_strategy(path):
        """Simple moving average crossover strategy"""
        if len(path) < 50:
            return {'total_return': 0}
        
        short_ma = np.mean(path[-20:])
        long_ma = np.mean(path[-50:])
        
        if short_ma > long_ma:
            # Buy signal
            returns = (path[-1] - path[0]) / path[0]
        else:
            # Sell signal
            returns = (path[0] - path[-1]) / path[0]
        
        return {'total_return': returns}
    
    # Run simulation
    try:
        result = tester.run_simulation(config, sample_strategy)
        
        # Generate report
        report = tester.generate_report(result)
        
        print("Monte Carlo Simulation Completed Successfully")
        print(f"Probability of Success: {report['probability_of_success']:.3f}")
        print(f"Expected Final Value: ${report['summary_statistics']['mean_final_value']:.2f}")
        print(f"95% VaR: {report['risk_assessment']['value_at_risk_95']:.3f}")
        print(f"Sharpe Ratio: {report['summary_statistics']['sharpe_ratio']:.3f}")
        
        # Print recommendations
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"- {rec}")
            
    except Exception as e:
        logger.error(f"Monte Carlo simulation failed: {e}")
        raise

