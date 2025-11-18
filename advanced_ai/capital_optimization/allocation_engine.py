"""
AI-NEXUS v5.0 - CAPITAL ALLOCATION ENGINE MODULE
Advanced Dynamic Capital Allocation and Optimization System
Multi-objective portfolio optimization with risk-aware capital deployment
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

class AllocationStrategy(Enum):
    RISK_PARITY = "risk_parity"
    MEAN_VARIANCE = "mean_variance"
    BLACK_LITTERMAN = "black_litterman"
    KELLY_CRITERION = "kelly_criterion"
    ADAPTIVE_WEIGHTING = "adaptive_weighting"
    CONSTANT_MIX = "constant_mix"
    CPPI = "cppi"

class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"

class CapitalState(Enum):
    DEPLOYED = "deployed"
    IDLE = "idle"
    RESERVED = "reserved"
    IN_TRANSIT = "in_transit"
    AT_RISK = "at_risk"

@dataclass
class CapitalAllocation:
    allocation_id: str
    timestamp: datetime
    strategy_id: str
    asset: str
    allocated_amount: float
    target_allocation: float
    current_allocation: float
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    constraints: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class PortfolioOptimization:
    optimization_id: str
    timestamp: datetime
    strategy: AllocationStrategy
    risk_tolerance: RiskTolerance
    target_allocations: Dict[str, float]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    diversification_score: float
    constraints_applied: List[str]
    metadata: Dict[str, Any]

@dataclass
class CapitalMovement:
    movement_id: str
    timestamp: datetime
    from_strategy: str
    to_strategy: str
    amount: float
    asset: str
    reason: str
    impact_assessment: Dict[str, float]
    metadata: Dict[str, Any]

class CapitalAllocationEngine:
    """
    Advanced capital allocation and optimization system
    Implements multiple allocation strategies with dynamic rebalancing
    """
    
    def __init__(self):
        self.allocation_history = deque(maxlen=10000)
        self.optimization_history = deque(maxlen=5000)
        self.capital_movements = deque(maxlen=10000)
        self.strategy_registry = {}
        
        # Allocation parameters
        self.allocation_params = {
            'total_capital': 1000000.0,  # $1M default
            'max_drawdown_limit': 0.15,  # 15% max drawdown
            'target_sharpe_ratio': 1.5,
            'rebalancing_threshold': 0.05,  # 5% threshold
            'min_allocation_per_strategy': 0.01,  # 1% minimum
            'max_allocation_per_strategy': 0.30,  # 30% maximum
            'correlation_threshold': 0.7,
            'liquidity_buffer': 0.05  # 5% liquidity buffer
        }
        
        # Strategy configurations
        self.strategy_configs = {}
        
        # Risk models
        self.risk_models = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_allocations': 0,
            'rebalancing_events': 0,
            'capital_efficiency': 0.0,
            'risk_adjusted_returns': 0.0,
            'diversification_score': 0.0
        }
        
        # Initialize allocation strategies and models
        self._initialize_strategies()
        self._initialize_risk_models()
        self._initialize_portfolio_tracker()
    
    def _initialize_strategies(self):
        """Initialize allocation strategies"""
        
        self.strategy_configs = {
            AllocationStrategy.RISK_PARITY: {
                'description': 'Equal risk contribution allocation',
                'parameters': {
                    'risk_target': 0.12,  # 12% target volatility
                    'leverage_limit': 3.0,
                    'rebalancing_frequency': timedelta(days=7)
                },
                'enabled': True
            },
            
            AllocationStrategy.MEAN_VARIANCE: {
                'description': 'Markowitz mean-variance optimization',
                'parameters': {
                    'risk_aversion': 1.0,
                    'expected_return_horizon': timedelta(days=30),
                    'covariance_estimation': 'exponential'
                },
                'enabled': True
            },
            
            AllocationStrategy.BLACK_LITTERMAN: {
                'description': 'Black-Litterman model with views',
                'parameters': {
                    'tau': 0.05,
                    'view_confidence': 0.7,
                    'equilibrium_returns': 'market_cap_weighted'
                },
                'enabled': True
            },
            
            AllocationStrategy.KELLY_CRITERION: {
                'description': 'Kelly criterion for optimal betting',
                'parameters': {
                    'fractional_kelly': 0.5,
                    'max_bet_size': 0.25,
                    'edge_estimation_window': timedelta(days=90)
                },
                'enabled': True
            },
            
            AllocationStrategy.ADAPTIVE_WEIGHTING: {
                'description': 'Adaptive weighting based on regime',
                'parameters': {
                    'regime_detection_window': timedelta(days=30),
                    'weight_decay': 0.95,
                    'momentum_factor': 0.3
                },
                'enabled': True
            },
            
            AllocationStrategy.CONSTANT_MIX: {
                'description': 'Constant mix strategy with rebalancing',
                'parameters': {
                    'target_weights': {},
                    'rebalancing_bands': 0.05
                },
                'enabled': True
            },
            
            AllocationStrategy.CPPI: {
                'description': 'Constant Proportion Portfolio Insurance',
                'parameters': {
                    'floor_value': 0.85,  # 85% of initial capital
                    'multiplier': 3.0,
                    'cushion_rebalancing': True
                },
                'enabled': True
            }
        }
    
    def _initialize_risk_models(self):
        """Initialize risk assessment models"""
        
        self.risk_models = {
            'var_model': VaRModel(),
            'cvar_model': CVaRModel(),
            'drawdown_model': DrawdownModel(),
            'correlation_model': CorrelationModel(),
            'liquidity_model': LiquidityModel(),
            'regime_model': RegimeModel()
        }
    
    def _initialize_portfolio_tracker(self):
        """Initialize portfolio tracking system"""
        
        self.portfolio_tracker = {
            'current_allocations': {},
            'historical_allocations': deque(maxlen=1000),
            'capital_states': {
                CapitalState.DEPLOYED: 0.0,
                CapitalState.IDLE: self.allocation_params['total_capital'],
                CapitalState.RESERVED: 0.0,
                CapitalState.IN_TRANSIT: 0.0,
                CapitalState.AT_RISK: 0.0
            },
            'strategy_performance': defaultdict(lambda: {
                'total_allocated': 0.0,
                'current_value': 0.0,
                'realized_pnl': 0.0,
                'unrealized_pnl': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0
            })
        }
    
    async def optimize_portfolio_allocation(self,
                                          strategy_data: Dict[str, Any],
                                          market_data: Dict[str, Any],
                                          risk_tolerance: RiskTolerance = RiskTolerance.MODERATE,
                                          allocation_strategy: AllocationStrategy = AllocationStrategy.RISK_PARITY) -> PortfolioOptimization:
        """Optimize portfolio allocation across strategies"""
        
        optimization_start = datetime.now()
        
        try:
            # Get current portfolio state
            current_state = self._get_current_portfolio_state()
            
            # Calculate strategy expected returns and risks
            strategy_metrics = await self._calculate_strategy_metrics(strategy_data, market_data)
            
            # Apply allocation strategy
            if allocation_strategy == AllocationStrategy.RISK_PARITY:
                optimal_allocations = await self._risk_parity_allocation(strategy_metrics, risk_tolerance)
            
            elif allocation_strategy == AllocationStrategy.MEAN_VARIANCE:
                optimal_allocations = await self._mean_variance_allocation(strategy_metrics, risk_tolerance)
            
            elif allocation_strategy == AllocationStrategy.BLACK_LITTERMAN:
                optimal_allocations = await self._black_litterman_allocation(strategy_metrics, market_data)
            
            elif allocation_strategy == AllocationStrategy.KELLY_CRITERION:
                optimal_allocations = await self._kelly_allocation(strategy_metrics)
            
            elif allocation_strategy == AllocationStrategy.ADAPTIVE_WEIGHTING:
                optimal_allocations = await self._adaptive_weighting_allocation(strategy_metrics, market_data)
            
            elif allocation_strategy == AllocationStrategy.CONSTANT_MIX:
                optimal_allocations = await self._constant_mix_allocation(strategy_metrics)
            
            elif allocation_strategy == AllocationStrategy.CPPI:
                optimal_allocations = await self._cppi_allocation(strategy_metrics, current_state)
            
            else:
                # Default to risk parity
                optimal_allocations = await self._risk_parity_allocation(strategy_metrics, risk_tolerance)
            
            # Apply constraints
            constrained_allocations = await self._apply_allocation_constraints(
                optimal_allocations, strategy_metrics
            )
            
            # Calculate portfolio metrics
            portfolio_metrics = await self._calculate_portfolio_metrics(
                constrained_allocations, strategy_metrics
            )
            
            # Create optimization result
            optimization = PortfolioOptimization(
                optimization_id=f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                timestamp=datetime.now(),
                strategy=allocation_strategy,
                risk_tolerance=risk_tolerance,
                target_allocations=constrained_allocations,
                expected_return=portfolio_metrics['expected_return'],
                expected_risk=portfolio_metrics['expected_risk'],
                sharpe_ratio=portfolio_metrics['sharpe_ratio'],
                diversification_score=portfolio_metrics['diversification_score'],
                constraints_applied=portfolio_metrics['constraints_applied'],
                metadata={
                    'optimization_time': (datetime.now() - optimization_start).total_seconds(),
                    'strategies_considered': len(strategy_metrics),
                    'total_capital': self.allocation_params['total_capital']
                }
            )
            
            self.optimization_history.append(optimization)
            
            print(f"Portfolio optimization completed: {allocation_strategy.value}")
            print(f"Expected return: {portfolio_metrics['expected_return']:.3%}")
            print(f"Expected risk: {portfolio_metrics['expected_risk']:.3%}")
            print(f"Sharpe ratio: {portfolio_metrics['sharpe_ratio']:.3f}")
            
            return optimization
        
        except Exception as e:
            print(f"Portfolio optimization failed: {e}")
            raise
    
    async def _risk_parity_allocation(self,
                                    strategy_metrics: Dict[str, Any],
                                    risk_tolerance: RiskTolerance) -> Dict[str, float]:
        """Risk parity allocation strategy"""
        
        config = self.strategy_configs[AllocationStrategy.RISK_PARITY]
        risk_target = config['parameters']['risk_target']
        
        # Calculate risk contributions
        risk_contributions = {}
        total_risk = 0.0
        
        for strategy_id, metrics in strategy_metrics.items():
            risk = metrics.get('volatility', 0.15)  # Default 15% volatility
            risk_contributions[strategy_id] = risk
            total_risk += risk
        
        if total_risk == 0:
            # Equal allocation if no risk data
            n_strategies = len(strategy_metrics)
            return {s: 1.0 / n_strategies for s in strategy_metrics.keys()}
        
        # Calculate inverse risk weights
        inverse_risk_weights = {}
        total_inverse_risk = 0.0
        
        for strategy_id, risk in risk_contributions.items():
            if risk > 0:
                inverse_risk = 1.0 / risk
                inverse_risk_weights[strategy_id] = inverse_risk
                total_inverse_risk += inverse_risk
        
        # Normalize to get weights
        allocations = {}
        for strategy_id, inverse_risk in inverse_risk_weights.items():
            allocations[strategy_id] = inverse_risk / total_inverse_risk
        
        # Adjust for risk tolerance
        allocations = self._adjust_for_risk_tolerance(allocations, risk_tolerance)
        
        return allocations
    
    async def _mean_variance_allocation(self,
                                      strategy_metrics: Dict[str, Any],
                                      risk_tolerance: RiskTolerance) -> Dict[str, float]:
        """Mean-variance optimization allocation"""
        
        config = self.strategy_configs[AllocationStrategy.MEAN_VARIANCE]
        risk_aversion = config['parameters']['risk_aversion']
        
        # Build expected returns and covariance matrix
        strategy_ids = list(strategy_metrics.keys())
        n_strategies = len(strategy_ids)
        
        if n_strategies == 0:
            return {}
        
        expected_returns = []
        covariance_matrix = np.zeros((n_strategies, n_strategies))
        
        for i, strategy_id in enumerate(strategy_ids):
            metrics = strategy_metrics[strategy_id]
            expected_returns.append(metrics.get('expected_return', 0.1))  # Default 10%
            
            for j, other_id in enumerate(strategy_ids):
                if i == j:
                    # Variance
                    vol = metrics.get('volatility', 0.15)
                    covariance_matrix[i, j] = vol ** 2
                else:
                    # Covariance (simplified)
                    correlation = metrics.get('correlations', {}).get(other_id, 0.2)
                    vol_i = metrics.get('volatility', 0.15)
                    vol_j = strategy_metrics[other_id].get('volatility', 0.15)
                    covariance_matrix[i, j] = correlation * vol_i * vol_j
        
        # Mean-variance optimization
        try:
            # Simple quadratic optimization
            weights = self._solve_mean_variance(
                np.array(expected_returns), 
                covariance_matrix, 
                risk_aversion
            )
            
            allocations = {strategy_ids[i]: weights[i] for i in range(n_strategies)}
            
        except Exception as e:
            print(f"Mean-variance optimization failed: {e}")
            # Fallback to equal weighting
            allocations = {s: 1.0 / n_strategies for s in strategy_ids}
        
        # Adjust for risk tolerance
        allocations = self._adjust_for_risk_tolerance(allocations, risk_tolerance)
        
        return allocations
    
    async def _black_litterman_allocation(self,
                                        strategy_metrics: Dict[str, Any],
                                        market_data: Dict[str, Any]) -> Dict[str, float]:
        """Black-Litterman model allocation"""
        
        config = self.strategy_configs[AllocationStrategy.BLACK_LITTERMAN]
        tau = config['parameters']['tau']
        
        # This would implement the full Black-Litterman model
        # For now, use a simplified version
        
        strategy_ids = list(strategy_metrics.keys())
        n_strategies = len(strategy_ids)
        
        if n_strategies == 0:
            return {}
        
        # Start with market equilibrium weights (equal for simplicity)
        equilibrium_weights = {s: 1.0 / n_strategies for s in strategy_ids}
        
        # Apply views based on strategy metrics
        view_adjusted_weights = {}
        
        for strategy_id in strategy_ids:
            metrics = strategy_metrics[strategy_id]
            
            # Base weight from equilibrium
            base_weight = equilibrium_weights[strategy_id]
            
            # Adjust based on recent performance and confidence
            sharpe_ratio = metrics.get('sharpe_ratio', 1.0)
            confidence = metrics.get('confidence', 0.5)
            
            # View adjustment
            view_adjustment = (sharpe_ratio - 1.0) * confidence * tau
            adjusted_weight = base_weight * (1 + view_adjustment)
            
            view_adjusted_weights[strategy_id] = adjusted_weight
        
        # Normalize weights
        total_weight = sum(view_adjusted_weights.values())
        allocations = {s: w / total_weight for s, w in view_adjusted_weights.items()}
        
        return allocations
    
    async def _kelly_allocation(self, strategy_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Kelly criterion allocation"""
        
        config = self.strategy_configs[AllocationStrategy.KELLY_CRITERION]
        fractional_kelly = config['parameters']['fractional_kelly']
        max_bet_size = config['parameters']['max_bet_size']
        
        allocations = {}
        
        for strategy_id, metrics in strategy_metrics.items():
            win_rate = metrics.get('win_rate', 0.5)
            avg_win = metrics.get('avg_winning_return', 0.02)  # 2% average win
            avg_loss = abs(metrics.get('avg_losing_return', 0.01))  # 1% average loss
            
            if avg_loss == 0:
                # Avoid division by zero
                kelly_fraction = 0.0
            else:
                # Kelly formula: f = (p * b - q) / b
                # where p = win rate, q = loss rate, b = win/loss ratio
                win_loss_ratio = avg_win / avg_loss
                kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            
            # Apply fractional Kelly and cap at maximum bet size
            allocation = max(0.0, kelly_fraction * fractional_kelly)
            allocation = min(allocation, max_bet_size)
            
            allocations[strategy_id] = allocation
        
        # Normalize if total allocation exceeds 1
        total_allocation = sum(allocations.values())
        if total_allocation > 1.0:
            allocations = {s: w / total_allocation for s, w in allocations.items()}
        
        return allocations
    
    async def _adaptive_weighting_allocation(self,
                                           strategy_metrics: Dict[str, Any],
                                           market_data: Dict[str, Any]) -> Dict[str, float]:
        """Adaptive weighting based on market regime"""
        
        config = self.strategy_configs[AllocationStrategy.ADAPTIVE_WEIGHTING]
        weight_decay = config['parameters']['weight_decay']
        momentum_factor = config['parameters']['momentum_factor']
        
        # Detect current market regime
        current_regime = await self.risk_models['regime_model'].detect_regime(market_data)
        
        allocations = {}
        
        for strategy_id, metrics in strategy_metrics.items():
            # Base weight from historical performance
            base_weight = metrics.get('historical_weight', 0.1)
            
            # Regime adjustment
            regime_performance = metrics.get('regime_performance', {}).get(current_regime, 0.5)
            regime_adjustment = (regime_performance - 0.5) * 2  # Scale to -1 to 1
            
            # Momentum adjustment
            recent_performance = metrics.get('recent_performance', 0.0)
            momentum_adjustment = recent_performance * momentum_factor
            
            # Combine adjustments
            total_adjustment = regime_adjustment + momentum_adjustment
            adjusted_weight = base_weight * (1 + total_adjustment) * weight_decay
            
            allocations[strategy_id] = max(0.0, adjusted_weight)
        
        # Normalize
        total_weight = sum(allocations.values())
        if total_weight > 0:
            allocations = {s: w / total_weight for s, w in allocations.items()}
        
        return allocations
    
    async def _constant_mix_allocation(self, strategy_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Constant mix allocation strategy"""
        
        config = self.strategy_configs[AllocationStrategy.CONSTANT_MIX]
        target_weights = config['parameters']['target_weights']
        
        if target_weights:
            # Use predefined target weights
            return target_weights.copy()
        else:
            # Equal weighting
            n_strategies = len(strategy_metrics)
            return {s: 1.0 / n_strategies for s in strategy_metrics.keys()}
    
    async def _cppi_allocation(self,
                             strategy_metrics: Dict[str, Any],
                             current_state: Dict[str, Any]) -> Dict[str, float]:
        """CPPI (Constant Proportion Portfolio Insurance) allocation"""
        
        config = self.strategy_configs[AllocationStrategy.CPPI]
        floor_value = config['parameters']['floor_value']
        multiplier = config['parameters']['multiplier']
        
        total_capital = self.allocation_params['total_capital']
        current_portfolio_value = current_state.get('total_value', total_capital)
        
        # Calculate cushion (portfolio value above floor)
        floor = total_capital * floor_value
        cushion = max(0, current_portfolio_value - floor)
        
        # Calculate risky asset allocation
        risky_allocation = cushion * multiplier
        
        # Cap at total capital
        risky_allocation = min(risky_allocation, total_capital)
        
        # Distribute risky allocation among strategies
        n_strategies = len(strategy_metrics)
        if n_strategies == 0:
            return {}
        
        risky_weight = risky_allocation / total_capital
        safe_weight = 1.0 - risky_weight
        
        # For simplicity, distribute risky allocation equally
        # In practice, this would use strategy-specific risk assessments
        allocations = {}
        for strategy_id in strategy_metrics.keys():
            allocations[strategy_id] = risky_weight / n_strategies
        
        # Add safe asset allocation (would be to a specific safe strategy)
        # For now, this is handled in the constraints
        
        return allocations
    
    def _solve_mean_variance(self, expected_returns: np.ndarray,
                           covariance_matrix: np.ndarray,
                           risk_aversion: float) -> np.ndarray:
        """Solve mean-variance optimization problem"""
        
        n_assets = len(expected_returns)
        
        # Simple analytical solution for unconstrained case
        # In practice, would use quadratic programming with constraints
        
        try:
            # Inverse of covariance matrix
            cov_inv = np.linalg.inv(covariance_matrix)
            
            # Optimal weights: w = (1/λ) * Σ^-1 * μ
            weights = (1 / risk_aversion) * cov_inv @ expected_returns
            
            # Normalize weights to sum to 1
            if weights.sum() != 0:
                weights = weights / weights.sum()
            else:
                weights = np.ones(n_assets) / n_assets
            
            return weights
        
        except np.linalg.LinAlgError:
            # Fallback to equal weighting if matrix is singular
            return np.ones(n_assets) / n_assets
    
    def _adjust_for_risk_tolerance(self, allocations: Dict[str, float],
                                 risk_tolerance: RiskTolerance) -> Dict[str, float]:
        """Adjust allocations based on risk tolerance"""
        
        risk_multipliers = {
            RiskTolerance.CONSERVATIVE: 0.7,
            RiskTolerance.MODERATE: 1.0,
            RiskTolerance.AGGRESSIVE: 1.3,
            RiskTolerance.VERY_AGGRESSIVE: 1.6
        }
        
        multiplier = risk_multipliers.get(risk_tolerance, 1.0)
        
        # Scale allocations (this is a simplified approach)
        # In practice, would adjust the optimization objective
        scaled_allocations = {}
        for strategy_id, weight in allocations.items():
            scaled_allocations[strategy_id] = min(1.0, weight * multiplier)
        
        # Renormalize
        total_weight = sum(scaled_allocations.values())
        if total_weight > 0:
            scaled_allocations = {s: w / total_weight for s, w in scaled_allocations.items()}
        
        return scaled_allocations
    
    async def _apply_allocation_constraints(self,
                                          allocations: Dict[str, float],
                                          strategy_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Apply allocation constraints"""
        
        constrained_allocations = allocations.copy()
        constraints_applied = []
        
        # Minimum allocation constraint
        min_allocation = self.allocation_params['min_allocation_per_strategy']
        for strategy_id in list(constrained_allocations.keys()):
            if constrained_allocations[strategy_id] < min_allocation:
                constrained_allocations[strategy_id] = min_allocation
                constraints_applied.append(f"min_allocation_{strategy_id}")
        
        # Maximum allocation constraint
        max_allocation = self.allocation_params['max_allocation_per_strategy']
        for strategy_id, weight in constrained_allocations.items():
            if weight > max_allocation:
                constrained_allocations[strategy_id] = max_allocation
                constraints_applied.append(f"max_allocation_{strategy_id}")
        
        # Liquidity buffer constraint
        liquidity_buffer = self.allocation_params['liquidity_buffer']
        total_allocated = sum(constrained_allocations.values())
        if total_allocated > (1.0 - liquidity_buffer):
            # Scale down to accommodate liquidity buffer
            scale_factor = (1.0 - liquidity_buffer) / total_allocated
            constrained_allocations = {s: w * scale_factor for s, w in constrained_allocations.items()}
            constraints_applied.append("liquidity_buffer")
        
        # Correlation constraint (simplified)
        # This would typically involve more complex portfolio optimization
        
        # Renormalize if necessary
        total_weight = sum(constrained_allocations.values())
        if abs(total_weight - 1.0) > 0.001:  # Allow for small numerical errors
            constrained_allocations = {s: w / total_weight for s, w in constrained_allocations.items()}
            constraints_applied.append("renormalization")
        
        return constrained_allocations
    
    async def _calculate_strategy_metrics(self,
                                        strategy_data: Dict[str, Any],
                                        market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive strategy metrics"""
        
        strategy_metrics = {}
        
        for strategy_id, data in strategy_data.items():
            metrics = {
                'expected_return': data.get('expected_return', 0.1),
                'volatility': data.get('volatility', 0.15),
                'sharpe_ratio': data.get('sharpe_ratio', 1.0),
                'max_drawdown': data.get('max_drawdown', 0.1),
                'win_rate': data.get('win_rate', 0.5),
                'avg_winning_return': data.get('avg_winning_return', 0.02),
                'avg_losing_return': data.get('avg_losing_return', -0.01),
                'confidence': data.get('confidence', 0.7),
                'correlations': data.get('correlations', {}),
                'regime_performance': data.get('regime_performance', {}),
                'recent_performance': data.get('recent_performance', 0.0),
                'historical_weight': data.get('historical_weight', 0.1)
            }
            
            strategy_metrics[strategy_id] = metrics
        
        return strategy_metrics
    
    async def _calculate_portfolio_metrics(self,
                                         allocations: Dict[str, float],
                                         strategy_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics"""
        
        expected_return = 0.0
        variance = 0.0
        
        strategy_ids = list(allocations.keys())
        n_strategies = len(strategy_ids)
        
        # Calculate expected return
        for strategy_id, weight in allocations.items():
            metrics = strategy_metrics[strategy_id]
            expected_return += weight * metrics['expected_return']
        
        # Calculate portfolio variance
        for i, strategy_id_i in enumerate(strategy_ids):
            weight_i = allocations[strategy_id_i]
            metrics_i = strategy_metrics[strategy_id_i]
            var_i = metrics_i['volatility'] ** 2
            
            variance += (weight_i ** 2) * var_i
            
            for j, strategy_id_j in enumerate(strategy_ids):
                if i != j:
                    weight_j = allocations[strategy_id_j]
                    metrics_j = strategy_metrics[strategy_id_j]
                    
                    # Get correlation
                    correlation = metrics_i['correlations'].get(strategy_id_j, 0.2)
                    cov_ij = correlation * metrics_i['volatility'] * metrics_j['volatility']
                    
                    variance += 2 * weight_i * weight_j * cov_ij
        
        expected_risk = np.sqrt(variance)
        sharpe_ratio = expected_return / expected_risk if expected_risk > 0 else 0.0
        
        # Calculate diversification score (simplified)
        diversification_score = 1.0 - (variance / sum(
            (allocations[s] * strategy_metrics[s]['volatility']) ** 2 
            for s in strategy_ids
        )) if n_strategies > 1 else 0.0
        
        return {
            'expected_return': expected_return,
            'expected_risk': expected_risk,
            'sharpe_ratio': sharpe_ratio,
            'diversification_score': diversification_score,
            'constraints_applied': []  # Would track which constraints were applied
        }
    
    def _get_current_portfolio_state(self) -> Dict[str, Any]:
        """Get current portfolio state"""
        
        return {
            'total_value': self.allocation_params['total_capital'],
            'allocations': self.portfolio_tracker['current_allocations'],
            'capital_states': self.portfolio_tracker['capital_states'],
            'strategy_performance': dict(self.portfolio_tracker['strategy_performance'])
        }
    
    async def execute_capital_allocation(self,
                                       optimization: PortfolioOptimization,
                                       execution_strategy: str = "gradual") -> List[CapitalMovement]:
        """Execute capital allocation based on optimization"""
        
        movements = []
        current_allocations = self.portfolio_tracker['current_allocations'].copy()
        
        for strategy_id, target_allocation in optimization.target_allocations.items():
            current_allocation = current_allocations.get(strategy_id, 0.0)
            target_amount = self.allocation_params['total_capital'] * target_allocation
            current_amount = self.allocation_params['total_capital'] * current_allocation
            
            allocation_diff = target_amount - current_amount
            
            if abs(allocation_diff) > self.allocation_params['total_capital'] * self.allocation_params['rebalancing_threshold']:
                # Create capital movement
                movement = CapitalMovement(
                    movement_id=f"move_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    timestamp=datetime.now(),
                    from_strategy="idle" if allocation_diff > 0 else strategy_id,
                    to_strategy=strategy_id if allocation_diff > 0 else "idle",
                    amount=abs(allocation_diff),
                    asset="USD",
                    reason="portfolio_rebalancing",
                    impact_assessment={
                        'expected_improvement': optimization.expected_return,
                        'risk_reduction': 0.0,  # Would calculate
                        'liquidity_impact': 0.0
                    },
                    metadata={
                        'optimization_id': optimization.optimization_id,
                        'execution_strategy': execution_strategy
                    }
                )
                
                movements.append(movement)
                self.capital_movements.append(movement)
                self.performance_metrics['rebalancing_events'] += 1
                
                # Update portfolio tracker
                if allocation_diff > 0:
                    # Adding capital to strategy
                    self.portfolio_tracker['current_allocations'][strategy_id] = target_allocation
                    self.portfolio_tracker['capital_states'][CapitalState.DEPLOYED] += allocation_diff
                    self.portfolio_tracker['capital_states'][CapitalState.IDLE] -= allocation_diff
                else:
                    # Removing capital from strategy
                    self.portfolio_tracker['current_allocations'][strategy_id] = target_allocation
                    self.portfolio_tracker['capital_states'][CapitalState.DEPLOYED] += allocation_diff  # Negative
                    self.portfolio_tracker['capital_states'][CapitalState.IDLE] -= allocation_diff  # Positive because allocation_diff is negative
        
        self.performance_metrics['total_allocations'] += len(movements)
        
        print(f"Executed {len(movements)} capital movements")
        return movements
    
    def update_strategy_performance(self, strategy_id: str, performance_update: Dict[str, Any]):
        """Update strategy performance metrics"""
        
        if strategy_id not in self.portfolio_tracker['strategy_performance']:
            self.portfolio_tracker['strategy_performance'][strategy_id] = {
                'total_allocated': 0.0,
                'current_value': 0.0,
                'realized_pnl': 0.0,
                'unrealized_pnl': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0
            }
        
        current_perf = self.portfolio_tracker['strategy_performance'][strategy_id]
        current_perf.update(performance_update)
        
        # Update overall performance metrics
        self._update_overall_performance_metrics()
    
    def _update_overall_performance_metrics(self):
        """Update overall performance metrics"""
        
        total_allocated = sum(
            perf['total_allocated'] for perf in self.portfolio_tracker['strategy_performance'].values()
        )
        total_value = sum(
            perf['current_value'] for perf in self.portfolio_tracker['strategy_performance'].values()
        )
        
        if total_allocated > 0:
            self.performance_metrics['capital_efficiency'] = total_value / total_allocated
        
        # Calculate risk-adjusted returns (simplified)
        total_return = (total_value - total_allocated) / total_allocated if total_allocated > 0 else 0.0
        avg_volatility = np.mean([
            perf.get('volatility', 0.15) for perf in self.portfolio_tracker['strategy_performance'].values()
        ])
        
        self.performance_metrics['risk_adjusted_returns'] = total_return / avg_volatility if avg_volatility > 0 else 0.0
        
        # Update diversification score
        n_strategies = len(self.portfolio_tracker['strategy_performance'])
        self.performance_metrics['diversification_score'] = 1.0 - (1.0 / n_strategies) if n_strategies > 1 else 0.0
    
    def get_allocation_status(self) -> Dict[str, Any]:
        """Get current allocation status"""
        
        return {
            'total_capital': self.allocation_params['total_capital'],
            'current_allocations': self.portfolio_tracker['current_allocations'],
            'capital_states': self.portfolio_tracker['capital_states'],
            'performance_metrics': self.performance_metrics,
            'recent_optimizations': len(self.optimization_history),
            'active_strategies': len(self.portfolio_tracker['strategy_performance'])
        }
    
    def update_capital_base(self, new_total_capital: float):
        """Update total capital base"""
        
        old_capital = self.allocation_params['total_capital']
        self.allocation_params['total_capital'] = new_total_capital
        
        # Scale existing allocations
        scale_factor = new_total_capital / old_capital if old_capital > 0 else 1.0
        
        for strategy_id in self.portfolio_tracker['current_allocations']:
            self.portfolio_tracker['current_allocations'][strategy_id] *= scale_factor
        
        # Update capital states
        for state in self.portfolio_tracker['capital_states']:
            self.portfolio_tracker['capital_states'][state] *= scale_factor
        
        print(f"Capital base updated from ${old_capital:,.2f} to ${new_total_capital:,.2f}")

# Supporting Classes
class VaRModel:
    async def calculate_var(self, portfolio: Dict[str, Any], confidence: float = 0.95) -> float:
        return 0.05  # 5% VaR

class CVaRModel:
    async def calculate_cvar(self, portfolio: Dict[str, Any], confidence: float = 0.95) -> float:
        return 0.08  # 8% CVaR

class DrawdownModel:
    async def calculate_max_drawdown(self, portfolio: Dict[str, Any]) -> float:
        return 0.12  # 12% max drawdown

class CorrelationModel:
    async def calculate_correlations(self, strategies: List[str]) -> Dict[str, Dict[str, float]]:
        return {}

class LiquidityModel:
    async def assess_liquidity(self, strategy_id: str, amount: float) -> float:
        return 0.9  # 90% liquidity score

class RegimeModel:
    async def detect_regime(self, market_data: Dict[str, Any]) -> str:
        return "normal"

# Example usage
if __name__ == "__main__":
    # Create capital allocation engine
    allocation_engine = CapitalAllocationEngine()
    
    # Sample strategy data
    sample_strategy_data = {
        "momentum_arbitrage": {
            "expected_return": 0.15,
            "volatility": 0.12,
            "sharpe_ratio": 1.25,
            "max_drawdown": 0.08,
            "win_rate": 0.6,
            "confidence": 0.8
        },
        "statistical_arbitrage": {
            "expected_return": 0.12,
            "volatility": 0.08,
            "sharpe_ratio": 1.5,
            "max_drawdown": 0.05,
            "win_rate": 0.7,
            "confidence": 0.9
        },
        "market_making": {
            "expected_return": 0.08,
            "volatility": 0.05,
            "sharpe_ratio": 1.6,
            "max_drawdown": 0.03,
            "win_rate": 0.8,
            "confidence": 0.7
        }
    }
    
    # Sample market data
    sample_market_data = {
        "volatility": 0.15,
        "correlation_structure": {},
        "regime": "normal"
    }
    
    # Optimize portfolio allocation
    async def demo():
        optimization = await allocation_engine.optimize_portfolio_allocation(
            strategy_data=sample_strategy_data,
            market_data=sample_market_data,
            risk_tolerance=RiskTolerance.MODERATE,
            allocation_strategy=AllocationStrategy.RISK_PARITY
        )
        
        print("Optimal Allocations:")
        for strategy, allocation in optimization.target_allocations.items():
            print(f"  {strategy}: {allocation:.1%}")
        
        # Execute allocation
        movements = await allocation_engine.execute_capital_allocation(optimization)
        print(f"Executed {len(movements)} capital movements")
        
        # Get allocation status
        status = allocation_engine.get_allocation_status()
        print(f"Total Capital: ${status['total_capital']:,.2f}")
        print(f"Capital Efficiency: {status['performance_metrics']['capital_efficiency']:.3f}")
    
    import asyncio
    asyncio.run(demo())
