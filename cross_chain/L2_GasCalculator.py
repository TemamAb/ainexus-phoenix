"""
AI-NEXUS L2 GAS CALCULATOR
Precise gas calculation and optimization for Layer 2 networks
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from web3 import Web3

@dataclass
class L2GasEstimate:
    network: str
    operation: str
    base_gas: int
    l1_fee: int
    l2_fee: int
    total_cost_eth: float
    optimization_suggestions: List[str]

@dataclass
class GasOptimization:
    original_estimate: L2GasEstimate
    optimized_estimate: L2GasEstimate
    savings_percentage: float
    optimization_strategy: str

class L2GasCalculator:
    def __init__(self, config):
        self.config = config
        self.gas_price_feeds = {}
        self.optimization_strategies = {}
        self.calculation_history = []
        self.logger = logging.getLogger(__name__)
        
        self._initialize_optimization_strategies()
    
    def _initialize_optimization_strategies(self):
        """Initialize gas optimization strategies for different L2 networks"""
        self.optimization_strategies = {
            'arbitrum': ArbitrumOptimization(),
            'optimism': OptimismOptimization(),
            'polygon': PolygonOptimization(),
            'base': BaseOptimization(),
            'zksync': ZkSyncOptimization()
        }
    
    async def calculate_transaction_gas(self, network: str, transaction_data: Dict, 
                                      optimization_level: str = 'aggressive') -> L2GasEstimate:
        """Calculate gas costs for L2 transaction with optimization"""
        # Get current gas data
        gas_data = await self.get_network_gas_data(network)
        
        # Calculate base gas estimate
        base_estimate = await self._calculate_base_gas(network, transaction_data, gas_data)
        
        # Apply optimizations
        if optimization_level != 'none':
            optimizer = self.optimization_strategies.get(network)
            if optimizer:
                optimized_estimate = await optimizer.optimize_transaction(base_estimate, transaction_data, optimization_level)
                
                # Record calculation
                self.record_calculation(base_estimate, optimized_estimate, optimization_level)
                
                return optimized_estimate
        
        return base_estimate
    
    async def get_network_gas_data(self, network: str) -> Dict:
        """Get current gas data for specific L2 network"""
        gas_data = {
            'l2_gas_price': await self.get_l2_gas_price(network),
            'l1_gas_price': await self.get_l1_gas_price(),
            'l1_data_price': await self.get_l1_data_price(network),
            'base_fee': await self.get_base_fee(network)
        }
        return gas_data
    
    async def get_l2_gas_price(self, network: str) -> int:
        """Get current L2 gas price"""
        # Implementation would fetch actual L2 gas prices
        # Placeholder values based on typical L2 gas prices
        
        l2_gas_prices = {
            'arbitrum': 0.1,      # gwei
            'optimism': 0.01,     # gwei
            'polygon': 30,        # gwei
            'base': 0.01,         # gwei
            'zksync': 0.25        # gwei
        }
        
        base_price = l2_gas_prices.get(network, 1.0)
        # Add some variation
        variation = await self.get_gas_price_variation(network)
        return int(base_price * (1 + variation) * 1e9)  # Convert to wei
    
    async def get_l1_gas_price(self) -> int:
        """Get current L1 (Ethereum) gas price"""
        # This would fetch actual L1 gas price
        return 30 * 1e9  # 30 gwei in wei
    
    async def get_l1_data_price(self, network: str) -> int:
        """Get L1 data price for specific L2"""
        # L1 data prices vary by L2 solution
        data_prices = {
            'arbitrum': 16,    # gas per byte
            'optimism': 16,    # gas per byte
            'base': 16,        # gas per byte
            'polygon': 0,      # No L1 data cost
            'zksync': 0        # No L1 data cost (different model)
        }
        return data_prices.get(network, 16)
    
    async def get_base_fee(self, network: str) -> int:
        """Get base fee for network"""
        base_fees = {
            'arbitrum': 0.1 * 1e9,
            'optimism': 0.01 * 1e9,
            'polygon': 30 * 1e9,
            'base': 0.01 * 1e9,
            'zksync': 0.25 * 1e9
        }
        return base_fees.get(network, 1 * 1e9)
    
    async def get_gas_price_variation(self, network: str) -> float:
        """Get typical gas price variation for network"""
        variations = {
            'arbitrum': 0.1,    # 10% variation
            'optimism': 0.05,   # 5% variation
            'polygon': 0.2,     # 20% variation
            'base': 0.08,       # 8% variation
            'zksync': 0.15      # 15% variation
        }
        return variations.get(network, 0.1)
    
    async def _calculate_base_gas(self, network: str, transaction_data: Dict, 
                                gas_data: Dict) -> L2GasEstimate:
        """Calculate base gas estimate without optimizations"""
        # Estimate L2 execution gas
        l2_gas = await self.estimate_l2_execution_gas(network, transaction_data)
        l2_cost = (l2_gas * gas_data['l2_gas_price']) / 1e18
        
        # Estimate L1 data cost (for optimistic rollups)
        l1_data_gas = await self.estimate_l1_data_gas(network, transaction_data)
        l1_data_cost = (l1_data_gas * gas_data['l1_gas_price'] * gas_data['l1_data_price']) / 1e18
        
        total_cost = l2_cost + l1_data_cost
        
        estimate = L2GasEstimate(
            network=network,
            operation=transaction_data.get('type', 'unknown'),
            base_gas=l2_gas,
            l1_fee=l1_data_gas,
            l2_fee=l2_gas,
            total_cost_eth=total_cost,
            optimization_suggestions=[]
        )
        
        return estimate
    
    async def estimate_l2_execution_gas(self, network: str, transaction_data: Dict) -> int:
        """Estimate L2 execution gas for transaction"""
        operation = transaction_data.get('type', 'transfer')
        
        # Base gas costs by operation type
        base_costs = {
            'transfer': 21000,
            'swap': 100000,
            'add_liquidity': 150000,
            'remove_liquidity': 120000,
            'bridge': 200000,
            'complex_arbitrage': 300000
        }
        
        base_gas = base_costs.get(operation, 50000)
        
        # Adjust for network-specific factors
        network_multipliers = {
            'arbitrum': 1.0,
            'optimism': 1.2,
            'polygon': 0.8,
            'base': 1.1,
            'zksync': 0.9
        }
        
        multiplier = network_multipliers.get(network, 1.0)
        return int(base_gas * multiplier)
    
    async def estimate_l1_data_gas(self, network: str, transaction_data: Dict) -> int:
        """Estimate L1 data gas for transaction (optimistic rollups)"""
        if network in ['polygon', 'zksync']:
            return 0  # No L1 data cost for these networks
        
        operation = transaction_data.get('type', 'transfer')
        
        # L1 data gas estimates by operation
        data_gas_estimates = {
            'transfer': 100,
            'swap': 500,
            'add_liquidity': 800,
            'remove_liquidity': 600,
            'bridge': 1000,
            'complex_arbitrage': 1500
        }
        
        return data_gas_estimates.get(operation, 300)
    
    def record_calculation(self, original: L2GasEstimate, optimized: L2GasEstimate, 
                         optimization_level: str):
        """Record gas calculation for analytics"""
        savings = (original.total_cost_eth - optimized.total_cost_eth) / original.total_cost_eth if original.total_cost_eth > 0 else 0
        
        calculation_record = {
            'timestamp': asyncio.get_event_loop().time(),
            'network': original.network,
            'operation': original.operation,
            'original_cost': original.total_cost_eth,
            'optimized_cost': optimized.total_cost_eth,
            'savings_percentage': savings,
            'optimization_level': optimization_level,
            'suggestions_applied': len(optimized.optimization_suggestions)
        }
        
        self.calculation_history.append(calculation_record)
    
    async def compare_network_costs(self, transaction_data: Dict) -> Dict[str, L2GasEstimate]:
        """Compare gas costs across all supported L2 networks"""
        comparisons = {}
        
        for network in self.optimization_strategies.keys():
            estimate = await self.calculate_transaction_gas(network, transaction_data, 'balanced')
            comparisons[network] = estimate
        
        return comparisons
    
    async def get_optimal_network(self, transaction_data: Dict, 
                                priority: str = 'cost') -> Tuple[str, L2GasEstimate]:
        """Find optimal L2 network for transaction based on priority"""
        comparisons = await self.compare_network_costs(transaction_data)
        
        if priority == 'cost':
            best_network = min(comparisons.items(), 
                             key=lambda x: x[1].total_cost_eth)
        elif priority == 'speed':
            # Would incorporate network speed data
            best_network = min(comparisons.items(),
                             key=lambda x: self.get_network_speed(x[0]))
        else:  # balanced
            best_network = min(comparisons.items(),
                             key=lambda x: x[1].total_cost_eth * self.get_network_speed(x[0]))
        
        return best_network
    
    def get_network_speed(self, network: str) -> float:
        """Get network speed factor (lower is faster)"""
        speed_factors = {
            'arbitrum': 1.0,
            'optimism': 1.2,
            'polygon': 1.5,
            'base': 1.1,
            'zksync': 0.8
        }
        return speed_factors.get(network, 1.0)
    
    async def get_gas_savings_analytics(self, days: int = 7) -> Dict:
        """Get analytics on gas savings over time"""
        cutoff_time = asyncio.get_event_loop().time() - (days * 86400)
        recent_calculations = [
            calc for calc in self.calculation_history 
            if calc['timestamp'] > cutoff_time
        ]
        
        if not recent_calculations:
            return {}
        
        total_savings = sum(calc['savings_percentage'] * calc['original_cost'] 
                          for calc in recent_calculations)
        avg_savings = sum(calc['savings_percentage'] for calc in recent_calculations) / len(recent_calculations)
        
        # Savings by network
        network_savings = {}
        for calc in recent_calculations:
            network = calc['network']
            if network not in network_savings:
                network_savings[network] = {'total': 0, 'count': 0}
            network_savings[network]['total'] += calc['savings_percentage']
            network_savings[network]['count'] += 1
        
        avg_network_savings = {}
        for network, data in network_savings.items():
            avg_network_savings[network] = data['total'] / data['count']
        
        return {
            'total_calculations': len(recent_calculations),
            'average_savings_percentage': avg_savings,
            'estimated_total_savings_eth': total_savings,
            'average_savings_by_network': avg_network_savings,
            'most_optimized_operation': self.get_most_optimized_operation(recent_calculations)
        }
    
    def get_most_optimized_operation(self, calculations: List[Dict]) -> str:
        """Get the operation type with highest average savings"""
        operation_savings = {}
        
        for calc in calculations:
            operation = calc['operation']
            if operation not in operation_savings:
                operation_savings[operation] = {'total': 0, 'count': 0}
            operation_savings[operation]['total'] += calc['savings_percentage']
            operation_savings[operation]['count'] += 1
        
        if not operation_savings:
            return "unknown"
        
        best_operation = max(operation_savings.items(),
                           key=lambda x: x[1]['total'] / x[1]['count'])
        
        return best_operation[0]
    
    async def generate_gas_optimization_report(self) -> Dict:
        """Generate comprehensive gas optimization report"""
        savings_analytics = await self.get_gas_savings_analytics()
        
        return {
            'report_timestamp': asyncio.get_event_loop().time(),
            'savings_analytics': savings_analytics,
            'supported_networks': list(self.optimization_strategies.keys()),
            'optimization_strategies': self.get_optimization_strategy_summary(),
            'recommendations': await self.generate_optimization_recommendations()
        }
    
    def get_optimization_strategy_summary(self) -> Dict:
        """Get summary of optimization strategies"""
        summary = {}
        
        for network, strategy in self.optimization_strategies.items():
            summary[network] = {
                'strategy_name': strategy.__class__.__name__,
                'optimization_methods': strategy.get_optimization_methods(),
                'estimated_effectiveness': strategy.get_estimated_effectiveness()
            }
        
        return summary
    
    async def generate_optimization_recommendations(self) -> List[str]:
        """Generate gas optimization recommendations"""
        recommendations = []
        analytics = await self.get_gas_savings_analytics()
        
        if analytics.get('average_savings_percentage', 0) < 0.1:
            recommendations.append("Increase optimization aggressiveness for better gas savings")
        
        # Network-specific recommendations
        network_savings = analytics.get('average_savings_by_network', {})
        for network, savings in network_savings.items():
            if savings < 0.05:
                recommendations.append(f"Review optimization strategy for {network} - low savings ({savings:.1%})")
        
        return recommendations

# Network-specific optimization strategies

class ArbitrumOptimization:
    """Optimization strategies for Arbitrum"""
    
    async def optimize_transaction(self, estimate: L2GasEstimate, 
                                 transaction_data: Dict, level: str) -> L2GasEstimate:
        optimized = L2GasEstimate(**estimate.__dict__)
        suggestions = []
        
        if level in ['aggressive', 'balanced']:
            # Compress calldata
            if await self.can_compress_calldata(transaction_data):
                optimized.l1_fee = int(optimized.l1_fee * 0.7)  # 30% reduction
                suggestions.append("Use compressed calldata for L1->L2 communication")
            
            # Batch operations
            if await self.can_batch_operations(transaction_data):
                optimized.base_gas = int(optimized.base_gas * 0.8)  # 20% reduction
                suggestions.append("Batch compatible operations")
        
        if level == 'aggressive':
            # Use L2-native optimizations
            if await self.can_use_l2_native(transaction_data):
                optimized.base_gas = int(optimized.base_gas * 0.9)  # 10% reduction
                suggestions.append("Use L2-native contract calls")
        
        optimized.total_cost_eth = await self.recalculate_total_cost(optimized)
        optimized.optimization_suggestions = suggestions
        
        return optimized
    
    async def can_compress_calldata(self, transaction_data: Dict) -> bool:
        return transaction_data.get('type') in ['swap', 'bridge', 'complex_arbitrage']
    
    async def can_batch_operations(self, transaction_data: Dict) -> bool:
        return 'multiple_operations' in transaction_data
    
    async def can_use_l2_native(self, transaction_data: Dict) -> bool:
        return transaction_data.get('use_l2_native', False)
    
    async def recalculate_total_cost(self, estimate: L2GasEstimate) -> float:
        # Simplified recalculation
        return estimate.total_cost_eth * 0.8  # Placeholder
    
    def get_optimization_methods(self) -> List[str]:
        return ['calldata_compression', 'operation_batching', 'l2_native_calls']
    
    def get_estimated_effectiveness(self) -> float:
        return 0.25  # 25% average savings

class OptimismOptimization:
    """Optimization strategies for Optimism"""
    
    async def optimize_transaction(self, estimate: L2GasEstimate,
                                 transaction_data: Dict, level: str) -> L2GasEstimate:
        optimized = L2GasEstimate(**estimate.__dict__)
        suggestions = []
        
        # Optimism-specific optimizations
        if level in ['aggressive', 'balanced']:
            # Use EIP-1559 optimizations
            optimized.base_gas = int(optimized.base_gas * 0.85)
            suggestions.append("Optimize for EIP-1559 fee market")
            
            # Compress L1 data
            optimized.l1_fee = int(optimized.l1_fee * 0.6)  # 40% reduction
            suggestions.append("Use L1 data compression")
        
        optimized.total_cost_eth = await self.recalculate_total_cost(optimized)
        optimized.optimization_suggestions = suggestions
        
        return optimized
    
    async def recalculate_total_cost(self, estimate: L2GasEstimate) -> float:
        return estimate.total_cost_eth * 0.7  # Placeholder
    
    def get_optimization_methods(self) -> List[str]:
        return ['eip1559_optimization', 'l1_data_compression']
    
    def get_estimated_effectiveness(self) -> float:
        return 0.30  # 30% average savings

class PolygonOptimization:
    """Optimization strategies for Polygon"""
    
    async def optimize_transaction(self, estimate: L2GasEstimate,
                                 transaction_data: Dict, level: str) -> L2GasEstimate:
        optimized = L2GasEstimate(**estimate.__dict__)
        suggestions = []
        
        # Polygon-specific optimizations (no L1 data costs)
        if level in ['aggressive', 'balanced']:
            # Use state channels where possible
            optimized.base_gas = int(optimized.base_gas * 0.75)
            suggestions.append("Utilize Polygon's state channels")
            
            # Batch transactions
            if await self.can_batch_polygon(transaction_data):
                optimized.base_gas = int(optimized.base_gas * 0.8)
                suggestions.append("Batch transactions for bulk processing")
        
        optimized.total_cost_eth = await self.recalculate_total_cost(optimized)
        optimized.optimization_suggestions = suggestions
        
        return optimized
    
    async def can_batch_polygon(self, transaction_data: Dict) -> bool:
        return transaction_data.get('batchable', False)
    
    async def recalculate_total_cost(self, estimate: L2GasEstimate) -> float:
        return estimate.total_cost_eth * 0.65  # Placeholder
    
    def get_optimization_methods(self) -> List[str]:
        return ['state_channels', 'transaction_batching', 'matic_optimization']
    
    def get_estimated_effectiveness(self) -> float:
        return 0.35  # 35% average savings

class BaseOptimization:
    """Optimization strategies for Base"""
    
    async def optimize_transaction(self, estimate: L2GasEstimate,
                                 transaction_data: Dict, level: str) -> L2GasEstimate:
        optimized = L2GasEstimate(**estimate.__dict__)
        suggestions = []
        
        # Base-specific optimizations (Optimism stack)
        if level in ['aggressive', 'balanced']:
            # Use Bedrock optimizations
            optimized.l1_fee = int(optimized.l1_fee * 0.5)  # 50% reduction
            suggestions.append("Leverage Base Bedrock optimizations")
            
            # Optimize for L2 execution
            optimized.base_gas = int(optimized.base_gas * 0.9)
            suggestions.append("Use Base-optimized execution paths")
        
        optimized.total_cost_eth = await self.recalculate_total_cost(optimized)
        optimized.optimization_suggestions = suggestions
        
        return optimized
    
    async def recalculate_total_cost(self, estimate: L2GasEstimate) -> float:
        return estimate.total_cost_eth * 0.6  # Placeholder
    
    def get_optimization_methods(self) -> List[str]:
        return ['bedrock_optimizations', 'l2_execution_optimization']
    
    def get_estimated_effectiveness(self) -> float:
        return 0.40  # 40% average savings

class ZkSyncOptimization:
    """Optimization strategies for zkSync"""
    
    async def optimize_transaction(self, estimate: L2GasEstimate,
                                 transaction_data: Dict, level: str) -> L2GasEstimate:
        optimized = L2GasEstimate(**estimate.__dict__)
        suggestions = []
        
        # zkSync-specific optimizations (ZK-rollup)
        if level in ['aggressive', 'balanced']:
            # Use proof batching
            optimized.base_gas = int(optimized.base_gas * 0.7)
            suggestions.append("Batch operations for proof efficiency")
            
            # Use account abstraction
            if await self.can_use_account_abstraction(transaction_data):
                optimized.base_gas = int(optimized.base_gas * 0.8)
                suggestions.append("Utilize zkSync account abstraction")
        
        optimized.total_cost_eth = await self.recalculate_total_cost(optimized)
        optimized.optimization_suggestions = suggestions
        
        return optimized
    
    async def can_use_account_abstraction(self, transaction_data: Dict) -> bool:
        return transaction_data.get('use_aa', True)
    
    async def recalculate_total_cost(self, estimate: L2GasEstimate) -> float:
        return estimate.total_cost_eth * 0.55  # Placeholder
    
    def get_optimization_methods(self) -> List[str]:
        return ['proof_batching', 'account_abstraction', 'zk_circuit_optimization']
    
    def get_estimated_effectiveness(self) -> float:
        return 0.45  # 45% average savings
