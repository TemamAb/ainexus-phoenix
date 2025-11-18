# File: advanced_ai/strategic_ai/PortfolioAI.py
# 7P-PILLAR: AIEVO-7P, CAPITAL-7P
# PURPOSE: AI-powered portfolio optimization and capital allocation

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class PortfolioStrategy(Enum):
    MARKOWITZ = "markowitz"
    BLACK_LITTERMAN = "black_litterman"
    RISK_PARITY = "risk_parity"
    MINIMUM_VARIANCE = "minimum_variance"
    MAXIMUM_SHARPE = "maximum_sharpe"

@dataclass
class PortfolioAllocation:
    strategy: PortfolioStrategy
    weights: Dict[str, float]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    diversification_ratio: float

class PortfolioAI:
    """
    AI-powered portfolio optimization with advanced risk management
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.portfolio_history = []
        self.risk_models = {}
        self.logger = logging.getLogger('PortfolioAI')
    
    def optimize_portfolio(self,
                         assets: List[str],
                         expected_returns: pd.Series,
                         covariance_matrix: pd.DataFrame,
                         strategy: PortfolioStrategy = PortfolioStrategy.MARKOWITZ,
                         constraints: Optional[Dict] = None) -> PortfolioAllocation:
        """Optimize portfolio using specified strategy"""
        
        if strategy == PortfolioStrategy.MARKOWITZ:
            return self._markowitz_optimization(assets, expected_returns, covariance_matrix, constraints)
        elif strategy == PortfolioStrategy.BLACK_LITTERMAN:
            return self._black_litterman_optimization(assets, expected_returns, covariance_matrix, constraints)
        elif strategy == PortfolioStrategy.RISK_PARITY:
            return self._risk_parity_optimization(assets, covariance_matrix, constraints)
        elif strategy == PortfolioStrategy.MINIMUM_VARIANCE:
            return self._minimum_variance_optimization(assets, covariance_matrix, constraints)
        elif strategy == PortfolioStrategy.MAXIMUM_SHARPE:
            return self._maximum_sharpe_optimization(assets, expected_returns, covariance_matrix, constraints)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
    
    def _markowitz_optimization(self,
                              assets: List[str],
                              expected_returns: pd.Series,
                              covariance_matrix: pd.DataFrame,
                              constraints: Optional[Dict]) -> PortfolioAllocation:
        """Modern Portfolio Theory optimization"""
        from scipy.optimize import minimize
        
        n_assets = len(assets)
        
        def portfolio_variance(weights):
            return weights.T @ covariance_matrix.values @ weights
        
        def portfolio_return(weights):
            return weights.T @ expected_returns.values
        
        # Default constraints
        if constraints is None:
            constraints = {'sum_to_one': True, 'no_short': True}
        
        # Build optimization constraints
        opt_constraints = []
        if constraints.get('sum_to_one', True):
            opt_constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Build bounds
        if constraints.get('no_short', True):
            bounds = [(0, 1) for _ in range(n_assets)]
        else:
            bounds = [(-1, 1) for _ in range(n_assets)]
        
        # Efficient frontier optimization
        target_returns = np.linspace(expected_returns.min(), expected_returns.max(), 50)
        efficient_portfolios = []
        
        for target_return in target_returns:
            if constraints.get('sum_to_one', True):
                opt_constraints.append({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target_return})
            
            result = minimize(portfolio_variance, 
                            np.array([1/n_assets] * n_assets),
                            method='SLSQP', bounds=bounds, constraints=opt_constraints)
            
            if result.success:
                efficient_portfolios.append({
                    'weights': result.x,
                    'return': portfolio_return(result.x),
                    'risk': np.sqrt(result.fun)
                })
        
        # Find optimal portfolio (maximum Sharpe ratio)
        optimal_portfolio = max(efficient_portfolios, 
                              key=lambda p: p['return'] / p['risk'] if p['risk'] > 0 else 0)
        
        weights_dict = dict(zip(assets, optimal_portfolio['weights']))
        
        return PortfolioAllocation(
            strategy=PortfolioStrategy.MARKOWITZ,
            weights=weights_dict,
            expected_return=optimal_portfolio['return'],
            expected_risk=optimal_portfolio['risk'],
            sharpe_ratio=optimal_portfolio['return'] / optimal_portfolio['risk'],
            diversification_ratio=self._calculate_diversification_ratio(optimal_portfolio['weights'], covariance_matrix)
        )
    
    def _black_litterman_optimization(self,
                                   assets: List[str],
                                   expected_returns: pd.Series,
                                   covariance_matrix: pd.DataFrame,
                                   constraints: Optional[Dict]) -> PortfolioAllocation:
        """Black-Litterman model with investor views"""
        # Simplified implementation
        # In production, would incorporate sophisticated views and confidence levels
        
        # Market equilibrium returns (CAPM)
        market_cap_weights = self._calculate_market_cap_weights(assets)
        risk_aversion = 2.5  # Typical risk aversion coefficient
        equilibrium_returns = risk_aversion * covariance_matrix @ market_cap_weights
        
        # Combine equilibrium with views (simplified)
        # Here we just use a weighted average
        investor_confidence = 0.7
        combined_returns = (investor_confidence * expected_returns + 
                          (1 - investor_confidence) * equilibrium_returns)
        
        # Optimize with combined returns
        return self._markowitz_optimization(assets, combined_returns, covariance_matrix, constraints)
    
    def _risk_parity_optimization(self,
                                assets: List[str],
                                covariance_matrix: pd.DataFrame,
                                constraints: Optional[Dict]) -> PortfolioAllocation:
        """Risk Parity portfolio optimization"""
        from scipy.optimize import minimize
        
        n_assets = len(assets)
        
        def risk_contribution(weights):
            portfolio_risk = np.sqrt(weights.T @ covariance_matrix.values @ weights)
            marginal_risk = covariance_matrix.values @ weights / portfolio_risk
            risk_contributions = weights * marginal_risk
            return risk_contributions
        
        def risk_parity_objective(weights):
            # Objective: equal risk contributions
            rc = risk_contribution(weights)
            target_rc = np.ones(n_assets) / n_assets * np.sum(rc)
            return np.sum((rc - target_rc) ** 2)
        
        # Constraints
        opt_constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Optimization
        result = minimize(risk_parity_objective,
                        np.array([1/n_assets] * n_assets),
                        method='SLSQP', bounds=bounds, constraints=opt_constraints)
        
        if result.success:
            weights = result.x
            portfolio_risk = np.sqrt(weights.T @ covariance_matrix.values @ weights)
            portfolio_return = self._estimate_risk_parity_return(weights, covariance_matrix)
            
            weights_dict = dict(zip(assets, weights))
            
            return PortfolioAllocation(
                strategy=PortfolioStrategy.RISK_PARITY,
                weights=weights_dict,
                expected_return=portfolio_return,
                expected_risk=portfolio_risk,
                sharpe_ratio=portfolio_return / portfolio_risk if portfolio_risk > 0 else 0,
                diversification_ratio=self._calculate_diversification_ratio(weights, covariance_matrix)
            )
        else:
            raise ValueError("Risk parity optimization failed")
    
    def _minimum_variance_optimization(self,
                                     assets: List[str],
                                     covariance_matrix: pd.DataFrame,
                                     constraints: Optional[Dict]) -> PortfolioAllocation:
        """Minimum variance portfolio optimization"""
        from scipy.optimize import minimize
        
        n_assets = len(assets)
        
        def portfolio_variance(weights):
            return weights.T @ covariance_matrix.values @ weights
        
        # Constraints
        opt_constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Optimization
        result = minimize(portfolio_variance,
                        np.array([1/n_assets] * n_assets),
                        method='SLSQP', bounds=bounds, constraints=opt_constraints)
        
        if result.success:
            weights = result.x
            portfolio_risk = np.sqrt(result.fun)
            portfolio_return = self._estimate_minimum_variance_return(weights, covariance_matrix)
            
            weights_dict = dict(zip(assets, weights))
            
            return PortfolioAllocation(
                strategy=PortfolioStrategy.MINIMUM_VARIANCE,
                weights=weights_dict,
                expected_return=portfolio_return,
                expected_risk=portfolio_risk,
                sharpe_ratio=portfolio_return / portfolio_risk if portfolio_risk > 0 else 0,
                diversification_ratio=self._calculate_diversification_ratio(weights, covariance_matrix)
            )
        else:
            raise ValueError("Minimum variance optimization failed")
    
    def _maximum_sharpe_optimization(self,
                                   assets: List[str],
                                   expected_returns: pd.Series,
                                   covariance_matrix: pd.DataFrame,
                                   constraints: Optional[Dict]) -> PortfolioAllocation:
        """Maximum Sharpe ratio portfolio optimization"""
        # This is equivalent to finding the tangency portfolio
        
        # Use Markowitz optimization and select maximum Sharpe portfolio
        markowitz_result = self._markowitz_optimization(assets, expected_returns, covariance_matrix, constraints)
        
        return PortfolioAllocation(
            strategy=PortfolioStrategy.MAXIMUM_SHARPE,
            weights=markowitz_result.weights,
            expected_return=markowitz_result.expected_return,
            expected_risk=markowitz_result.expected_risk,
            sharpe_ratio=markowitz_result.sharpe_ratio,
            diversification_ratio=markowitz_result.diversification_ratio
        )
    
    def _calculate_market_cap_weights(self, assets: List[str]) -> np.ndarray:
        """Calculate market capitalization weights (simplified)"""
        # In production, would fetch real market cap data
        # Using equal weights as placeholder
        n_assets = len(assets)
        return np.array([1/n_assets] * n_assets)
    
    def _estimate_risk_parity_return(self, weights: np.ndarray, covariance_matrix: pd.DataFrame) -> float:
        """Estimate expected return for risk parity portfolio"""
        # Simplified estimation - in production would use more sophisticated models
        risk_contributions = weights * (covariance_matrix.values @ weights)
        total_risk_contribution = np.sum(risk_contributions)
        
        # Assume return proportional to risk contribution
        base_return = 0.08  # 8% base return
        return base_return * (total_risk_contribution / len(weights))
    
    def _estimate_minimum_variance_return(self, weights: np.ndarray, covariance_matrix: pd.DataFrame) -> float:
        """Estimate expected return for minimum variance portfolio"""
        # Conservative return estimate for minimum variance portfolio
        return 0.04  # 4% conservative return
    
    def _calculate_diversification_ratio(self, weights: np.ndarray, covariance_matrix: pd.DataFrame) -> float:
        """Calculate portfolio diversification ratio"""
        weighted_vol = np.sum(weights * np.sqrt(np.diag(covariance_matrix)))
        portfolio_vol = np.sqrt(weights.T @ covariance_matrix.values @ weights)
        
        if portfolio_vol > 0:
            return weighted_vol / portfolio_vol
        return 1.0
    
    def dynamic_portfolio_rebalancing(self,
                                    current_portfolio: Dict[str, float],
                                    market_conditions: Dict,
                                    transaction_costs: float = 0.001) -> Dict[str, float]:
        """Dynamic portfolio rebalancing with transaction cost awareness"""
        
        # Calculate optimal target portfolio
        target_weights = self.optimize_portfolio(
            list(current_portfolio.keys()),
            market_conditions['expected_returns'],
            market_conditions['covariance_matrix']
        ).weights
        
        # Apply transaction cost-aware rebalancing
        rebalanced_weights = {}
        total_transaction_cost = 0
        
        for asset, current_weight in current_portfolio.items():
            target_weight = target_weights.get(asset, 0)
            weight_change = abs(target_weight - current_weight)
            
            # Only rebalance if benefit outweighs cost
            if weight_change > transaction_costs * 2:  # 2x cost threshold
                rebalanced_weights[asset] = target_weight
                total_transaction_cost += weight_change * transaction_costs
            else:
                rebalanced_weights[asset] = current_weight
        
        return {
            'rebalanced_weights': rebalanced_weights,
            'transaction_cost': total_transaction_cost,
            'rebalancing_efficiency': 1 - total_transaction_cost
        }
    
    def calculate_portfolio_metrics(self,
                                  weights: Dict[str, float],
                                  expected_returns: pd.Series,
                                  covariance_matrix: pd.DataFrame) -> Dict:
        """Calculate comprehensive portfolio metrics"""
        
        weight_vector = np.array([weights.get(asset, 0) for asset in expected_returns.index])
        
        portfolio_return = weight_vector.T @ expected_returns.values
        portfolio_variance = weight_vector.T @ covariance_matrix.values @ weight_vector
        portfolio_risk = np.sqrt(portfolio_variance)
        
        # Calculate component contributions
        marginal_risk = covariance_matrix.values @ weight_vector / portfolio_risk
        risk_contributions = weight_vector * marginal_risk
        
        metrics = {
            'expected_return': portfolio_return,
            'expected_risk': portfolio_risk,
            'sharpe_ratio': portfolio_return / portfolio_risk if portfolio_risk > 0 else 0,
            'diversification_ratio': self._calculate_diversification_ratio(weight_vector, covariance_matrix),
            'risk_contributions': dict(zip(expected_returns.index, risk_contributions)),
            'value_at_risk_95': portfolio_risk * 1.645,  # 95% VaR
            'expected_shortfall_95': portfolio_risk * 2.063  # 95% ES
        }
        
        return metrics

# Example usage
if __name__ == "__main__":
    portfolio_ai = PortfolioAI({})
    print("PortfolioAI initialized successfully")
