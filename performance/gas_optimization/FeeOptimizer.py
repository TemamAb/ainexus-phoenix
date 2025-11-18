"""
AI-NEXUS FEE OPTIMIZER
Comprehensive fee optimization for maximum profit efficiency
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from decimal import Decimal, ROUND_UP

@dataclass
class FeeOptimization:
    transaction_hash: str
    original_max_fee: float
    optimized_max_fee: float
    original_priority_fee: float
    optimized_priority_fee: float
    estimated_savings: float
    confidence: float
    optimization_strategy: str

@dataclass
class ProfitabilityAnalysis:
    expected_profit: float
    estimated_gas_cost: float
    net_profit: float
    profit_margin: float
    risk_adjusted_profit: float
    recommendation: str

class FeeOptimizer:
    def __init__(self, config):
        self.config = config
        self.optimization_history = []
        self.gas_price_predictor = None  # Would be initialized with actual predictor
        self.profitability_threshold = config.get('min_profit_margin', 0.01)  # 1%
        self.logger = logging.getLogger(__name__)
    
    async def optimize_transaction_fees(self, transaction_data: Dict, 
                                      arbitrage_opportunity: Dict) -> FeeOptimization:
        """Optimize transaction fees for maximum profitability"""
        # Get current network conditions
        network_conditions = await self._get_network_conditions()
        
        # Calculate base fee estimates
        base_fee_estimate = await self._estimate_base_fee(network_conditions)
        
        # Get optimal priority fee
        priority_fee_analysis = await self._analyze_priority_fee_requirements(
            transaction_data, network_conditions
        )
        
        # Calculate optimal max fee
        max_fee_optimized = self._calculate_optimal_max_fee(
            base_fee_estimate, priority_fee_analysis.optimal_priority_fee
        )
        
        # Analyze profitability
        profitability = await self._analyze_profitability(
            arbitrage_opportunity, max_fee_optimized, priority_fee_analysis.optimal_priority_fee
        )
        
        # Apply optimization strategy
        optimization_strategy = self._select_optimization_strategy(
            profitability, priority_fee_analysis
        )
        
        # Final fee calculation with strategy applied
        final_fees = self._apply_optimization_strategy(
            base_fee_estimate, priority_fee_analysis, optimization_strategy, profitability
        )
        
        optimization = FeeOptimization(
            transaction_hash=transaction_data.get('hash', ''),
            original_max_fee=transaction_data.get('maxFeePerGas', 0),
            optimized_max_fee=final_fees['max_fee'],
            original_priority_fee=transaction_data.get('maxPriorityFeePerGas', 0),
            optimized_priority_fee=final_fees['priority_fee'],
            estimated_savings=self._calculate_savings(transaction_data, final_fees),
            confidence=priority_fee_analysis.confidence,
            optimization_strategy=optimization_strategy
        )
        
        self.optimization_history.append(optimization)
        return optimization
    
    async def _get_network_conditions(self) -> Dict:
        """Get current network conditions"""
        # Implementation would fetch real-time network data
        return {
            'base_fee': 30.0,  # Gwei
            'pending_txs': 15000,
            'block_utilization': 0.75,
            'gas_price_volatility': 0.1
        }
    
    async def _estimate_base_fee(self, network_conditions: Dict) -> float:
        """Estimate base fee for next block"""
        current_base_fee = network_conditions['base_fee']
        utilization = network_conditions['block_utilization']
        
        # Simple base fee prediction based on utilization
        if utilization > 0.9:
            return current_base_fee * 1.125  # 12.5% increase
        elif utilization > 0.7:
            return current_base_fee * 1.05   # 5% increase
        elif utilization < 0.3:
            return current_base_fee * 0.95   # 5% decrease
        else:
            return current_base_fee
    
    async def _analyze_priority_fee_requirements(self, transaction_data: Dict, 
                                               network_conditions: Dict) -> Dict:
        """Analyze priority fee requirements for timely inclusion"""
        urgency = transaction_data.get('urgency', 'medium')
        transaction_value = transaction_data.get('value', 0) / 1e18  # Convert to ETH
        
        # Base priority fee based on network conditions
        base_priority_fee = self._calculate_base_priority_fee(network_conditions)
        
        # Urgency multiplier
        urgency_multipliers = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.5,
            'critical': 2.5
        }
        
        # Value-based adjustment (higher value = more conservative)
        value_multiplier = 1.0 + min(transaction_value * 0.1, 1.0)  # Up to 2x for high-value tx
        
        optimal_priority_fee = base_priority_fee * urgency_multipliers.get(urgency, 1.0) * value_multiplier
        
        # Confidence calculation
        confidence = self._calculate_priority_fee_confidence(network_conditions)
        
        return {
            'optimal_priority_fee': optimal_priority_fee,
            'base_priority_fee': base_priority_fee,
            'urgency_multiplier': urgency_multipliers.get(urgency, 1.0),
            'value_multiplier': value_multiplier,
            'confidence': confidence,
            'inclusion_probability': self._estimate_inclusion_probability(optimal_priority_fee, network_conditions)
        }
    
    def _calculate_base_priority_fee(self, network_conditions: Dict) -> float:
        """Calculate base priority fee from network conditions"""
        base_fee = network_conditions['base_fee']
        pending_txs = network_conditions['pending_txs']
        
        # Simple heuristic based on network congestion
        if pending_txs > 50000:
            return 3.0  # High congestion
        elif pending_txs > 20000:
            return 2.0  # Medium congestion
        else:
            return 1.0  # Low congestion
    
    def _calculate_priority_fee_confidence(self, network_conditions: Dict) -> float:
        """Calculate confidence in priority fee recommendation"""
        volatility = network_conditions.get('gas_price_volatility', 0.1)
        pending_txs = network_conditions['pending_txs']
        
        # Higher volatility and congestion reduce confidence
        volatility_penalty = min(volatility * 2, 0.3)  # Up to 30% penalty
        congestion_penalty = min(pending_txs / 100000, 0.2)  # Up to 20% penalty
        
        base_confidence = 0.8
        confidence = base_confidence * (1 - volatility_penalty) * (1 - congestion_penalty)
        
        return max(0.3, min(0.95, confidence))
    
    def _estimate_inclusion_probability(self, priority_fee: float, network_conditions: Dict) -> float:
        """Estimate probability of transaction inclusion"""
        base_probability = 0.5
        
        # Adjust based on priority fee relative to network conditions
        base_fee = network_conditions['base_fee']
        fee_ratio = priority_fee / base_fee
        
        if fee_ratio > 0.2:
            base_probability += 0.4
        elif fee_ratio > 0.1:
            base_probability += 0.2
        elif fee_ratio > 0.05:
            base_probability += 0.1
        
        # Adjust based on network congestion
        pending_txs = network_conditions['pending_txs']
        if pending_txs > 50000:
            base_probability *= 0.7
        elif pending_txs > 20000:
            base_probability *= 0.9
        
        return min(0.95, max(0.1, base_probability))
    
    def _calculate_optimal_max_fee(self, base_fee_estimate: float, priority_fee: float) -> float:
        """Calculate optimal max fee with safety margin"""
        safety_margin = 1.2  # 20% safety margin on base fee
        return (base_fee_estimate * safety_margin) + priority_fee
    
    async def _analyze_profitability(self, arbitrage_opportunity: Dict, 
                                   max_fee: float, priority_fee: float) -> ProfitabilityAnalysis:
        """Analyze profitability of arbitrage opportunity with given fees"""
        expected_profit = arbitrage_opportunity.get('expected_profit', 0)  # ETH
        gas_limit = arbitrage_opportunity.get('estimated_gas', 300000)
        
        # Calculate gas cost in ETH
        gas_cost_eth = (max_fee * gas_limit) / 1e9  # Convert to ETH
        
        net_profit = expected_profit - gas_cost_eth
        profit_margin = net_profit / expected_profit if expected_profit > 0 else 0
        
        # Risk adjustment (simplified)
        risk_adjusted_profit = net_profit * 0.9  # 10% risk discount
        
        # Generate recommendation
        if profit_margin < self.profitability_threshold:
            recommendation = "NOT_PROFITABLE"
        elif profit_margin < self.profitability_threshold * 2:
            recommendation = "MARGINALLY_PROFITABLE"
        else:
            recommendation = "HIGHLY_PROFITABLE"
        
        return ProfitabilityAnalysis(
            expected_profit=expected_profit,
            estimated_gas_cost=gas_cost_eth,
            net_profit=net_profit,
            profit_margin=profit_margin,
            risk_adjusted_profit=risk_adjusted_profit,
            recommendation=recommendation
        )
    
    def _select_optimization_strategy(self, profitability: ProfitabilityAnalysis,
                                    priority_fee_analysis: Dict) -> str:
        """Select optimal fee optimization strategy"""
        if profitability.recommendation == "NOT_PROFITABLE":
            return "cost_minimization"
        elif profitability.recommendation == "MARGINALLY_PROFITABLE":
            return "balanced"
        else:
            # For highly profitable opportunities, we can be more aggressive
            if priority_fee_analysis['inclusion_probability'] < 0.8:
                return "inclusion_optimization"
            else:
                return "profit_maximization"
    
    def _apply_optimization_strategy(self, base_fee_estimate: float,
                                   priority_fee_analysis: Dict,
                                   strategy: str,
                                   profitability: ProfitabilityAnalysis) -> Dict:
        """Apply optimization strategy to calculate final fees"""
        base_priority_fee = priority_fee_analysis['optimal_priority_fee']
        
        if strategy == "cost_minimization":
            # Minimize costs, accept lower inclusion probability
            priority_fee = base_priority_fee * 0.7
            max_fee_multiplier = 1.1  # Minimal safety margin
        
        elif strategy == "balanced":
            # Balance cost and inclusion probability
            priority_fee = base_priority_fee
            max_fee_multiplier = 1.2
        
        elif strategy == "inclusion_optimization":
            # Optimize for inclusion, accept higher costs
            priority_fee = base_priority_fee * 1.3
            max_fee_multiplier = 1.3
        
        else:  # profit_maximization
            # Balance profit and reliability
            margin = profitability.profit_margin
            if margin > 0.1:  # High margin
                priority_fee = base_priority_fee * 1.2
                max_fee_multiplier = 1.25
            else:
                priority_fee = base_priority_fee
                max_fee_multiplier = 1.2
        
        max_fee = (base_fee_estimate * max_fee_multiplier) + priority_fee
        
        return {
            'priority_fee': priority_fee,
            'max_fee': max_fee,
            'strategy': strategy
        }
    
    def _calculate_savings(self, transaction_data: Dict, optimized_fees: Dict) -> float:
        """Calculate estimated savings from optimization"""
        original_max_fee = transaction_data.get('maxFeePerGas', 0)
        optimized_max_fee = optimized_fees['max_fee']
        
        if original_max_fee == 0:
            return 0
        
        gas_limit = transaction_data.get('gas', 21000)
        
        original_cost = (original_max_fee * gas_limit) / 1e9  # ETH
        optimized_cost = (optimized_max_fee * gas_limit) / 1e9  # ETH
        
        return original_cost - optimized_cost  # Positive = savings
    
    def get_optimization_performance(self) -> Dict:
        """Get fee optimization performance metrics"""
        if not self.optimization_history:
            return {}
        
        total_savings = sum(opt.estimated_savings for opt in self.optimization_history)
        avg_confidence = sum(opt.confidence for opt in self.optimization_history) / len(self.optimization_history)
        
        strategy_counts = {}
        for opt in self.optimization_history:
            strategy_counts[opt.optimization_strategy] = strategy_counts.get(opt.optimization_strategy, 0) + 1
        
        return {
            'total_optimizations': len(self.optimization_history),
            'total_savings_eth': total_savings,
            'average_savings_per_tx': total_savings / len(self.optimization_history),
            'average_confidence': avg_confidence,
            'strategy_distribution': strategy_counts,
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate optimization success rate"""
        # This would require tracking actual transaction outcomes
        # For now, return a placeholder
        return 0.85  # 85% success rate estimate
    
    async def get_fee_recommendation(self, transaction_data: Dict, 
                                   arbitrage_opportunity: Dict) -> Dict:
        """Get comprehensive fee recommendation"""
        optimization = await self.optimize_transaction_fees(transaction_data, arbitrage_opportunity)
        
        return {
            'max_fee_per_gas_gwei': optimization.optimized_max_fee,
            'max_priority_fee_per_gas_gwei': optimization.optimized_priority_fee,
            'estimated_gas_cost_eth': self._estimate_total_cost(optimization, transaction_data),
            'estimated_savings_eth': optimization.estimated_savings,
            'inclusion_probability': await self._estimate_inclusion_probability(
                optimization.optimized_priority_fee
            ),
            'optimization_strategy': optimization.optimization_strategy,
            'confidence': optimization.confidence,
            'recommendation': self._generate_recommendation(optimization)
        }
    
    def _estimate_total_cost(self, optimization: FeeOptimization, transaction_data: Dict) -> float:
        """Estimate total transaction cost"""
        gas_limit = transaction_data.get('gas', 21000)
        total_cost = (optimization.optimized_max_fee * gas_limit) / 1e9  # ETH
        return total_cost
    
    async def _estimate_inclusion_probability(self, priority_fee: float) -> float:
        """Estimate inclusion probability for given priority fee"""
        # Simplified estimation - would use more sophisticated models in production
        if priority_fee > 5:
            return 0.95
        elif priority_fee > 2:
            return 0.8
        elif priority_fee > 1:
            return 0.6
        else:
            return 0.3
    
    def _generate_recommendation(self, optimization: FeeOptimization) -> str:
        """Generate human-readable recommendation"""
        if optimization.optimization_strategy == "cost_minimization":
            return "Cost-optimized: Lower fees but may experience delays"
        elif optimization.optimization_strategy == "balanced":
            return "Balanced: Good trade-off between cost and speed"
        elif optimization.optimization_strategy == "inclusion_optimization":
            return "Inclusion-optimized: Higher fees for faster confirmation"
        else:
            return "Profit-maximized: Optimized for overall profitability"
