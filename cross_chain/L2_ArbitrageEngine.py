"""
AI-NEXUS L2 ARBITRAGE ENGINE
Optimized arbitrage execution for Layer 2 networks
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from web3 import Web3

@dataclass
class L2Arbitrage:
    opportunity_id: str
    l2_network: str
    base_chain: str
    expected_profit: float
    execution_path: List[Dict]
    gas_savings: float
    speed_advantage: float

class L2ArbitrageEngine:
    def __init__(self, config):
        self.config = config
        self.l2_providers = {}
        self.arbitrage_opportunities = []
        self.execution_history = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize L2 networks
        self.supported_l2s = config.get('supported_l2_networks', [
            'arbitrum', 'optimism', 'polygon', 'base', 'zksync'
        ])
        self._initialize_l2_connections()
    
    def _initialize_l2_connections(self):
        """Initialize connections to L2 networks"""
        for l2_network in self.supported_l2s:
            try:
                rpc_url = self.config['l2_configs'][l2_network]['rpc_url']
                self.l2_providers[l2_network] = Web3(Web3.HTTPProvider(rpc_url))
                self.logger.info(f"Connected to L2: {l2_network}")
            except Exception as e:
                self.logger.error(f"Failed to connect to {l2_network}: {e}")
    
    async def monitor_l2_arbitrage(self, base_chain_data: Dict) -> List[L2Arbitrage]:
        """Monitor for L2 arbitrage opportunities"""
        opportunities = []
        
        for l2_network in self.supported_l2s:
            l2_ops = await self.check_l2_arbitrage(l2_network, base_chain_data)
            opportunities.extend(l2_ops)
        
        # Filter and rank opportunities
        filtered_ops = await self.filter_l2_opportunities(opportunities)
        self.arbitrage_opportunities.extend(filtered_ops)
        
        return filtered_ops
    
    async def check_l2_arbitrage(self, l2_network: str, base_chain_data: Dict) -> List[L2Arbitrage]:
        """Check arbitrage opportunities between L1 and L2"""
        opportunities = []
        
        # Get prices on both chains
        l2_prices = await self.get_l2_prices(l2_network)
        base_prices = base_chain_data.get('prices', {})
        
        for asset, l2_price in l2_prices.items():
            base_price = base_prices.get(asset, 0)
            
            if base_price > 0 and l2_price > 0:
                # Calculate price discrepancy
                discrepancy = (base_price - l2_price) / base_price
                
                if abs(discrepancy) > self.config.get('min_l2_discrepancy', 0.005):
                    # Calculate expected profit after bridge costs
                    bridge_cost = await self.estimate_bridge_cost(l2_network, asset)
                    expected_profit = abs(discrepancy) - bridge_cost
                    
                    if expected_profit > self.config.get('min_l2_profit', 0.003):
                        opportunity = L2Arbitrage(
                            opportunity_id=f"l2_{l2_network}_{asset}_{int(asyncio.get_event_loop().time())}",
                            l2_network=l2_network,
                            base_chain='ethereum',
                            expected_profit=expected_profit,
                            execution_path=await self.generate_l2_execution_path(l2_network, asset, discrepancy > 0),
                            gas_savings=await self.calculate_gas_savings(l2_network),
                            speed_advantage=await self.calculate_speed_advantage(l2_network)
                        )
                        opportunities.append(opportunity)
        
        return opportunities
    
    async def get_l2_prices(self, l2_network: str) -> Dict[str, float]:
        """Get asset prices on L2 network"""
        # Implementation would fetch actual prices from L2 DEXes
        # Placeholder with simulated data
        
        assets = ['ETH', 'USDC', 'USDT', 'DAI']
        prices = {}
        
        for asset in assets:
            base_price = 1000 if asset == 'ETH' else 1.0
            # Simulate small price variations on L2
            variation = await self.get_l2_price_variation(l2_network, asset)
            prices[asset] = base_price * (1 + variation)
        
        return prices
    
    async def get_l2_price_variation(self, l2_network: str, asset: str) -> float:
        """Get typical price variation for asset on L2"""
        # These would be based on historical data
        variations = {
            'arbitrum': 0.002,    # 0.2% typical variation
            'optimism': 0.0015,   # 0.15% typical variation  
            'polygon': 0.003,     # 0.3% typical variation
            'base': 0.0025,       # 0.25% typical variation
            'zksync': 0.002       # 0.2% typical variation
        }
        return variations.get(l2_network, 0.002)
    
    async def estimate_bridge_cost(self, l2_network: str, asset: str) -> float:
        """Estimate cost to bridge asset to/from L2"""
        bridge_costs = {
            'arbitrum': 0.0005,   # 0.05%
            'optimism': 0.0003,   # 0.03%
            'polygon': 0.001,     # 0.1%
            'base': 0.0004,       # 0.04%
            'zksync': 0.0006      # 0.06%
        }
        return bridge_costs.get(l2_network, 0.001)
    
    async def generate_l2_execution_path(self, l2_network: str, asset: str, 
                                       buy_on_l2: bool) -> List[Dict]:
        """Generate execution path for L2 arbitrage"""
        if buy_on_l2:
            return [
                {'action': 'bridge', 'from': 'ethereum', 'to': l2_network, 'asset': 'ETH'},
                {'action': 'swap', 'chain': l2_network, 'from': 'ETH', 'to': asset},
                {'action': 'bridge', 'from': l2_network, 'to': 'ethereum', 'asset': asset},
                {'action': 'swap', 'chain': 'ethereum', 'from': asset, 'to': 'ETH'}
            ]
        else:
            return [
                {'action': 'bridge', 'from': 'ethereum', 'to': l2_network, 'asset': asset},
                {'action': 'swap', 'chain': l2_network, 'from': asset, 'to': 'ETH'},
                {'action': 'bridge', 'from': l2_network, 'to': 'ethereum', 'asset': 'ETH'}
            ]
    
    async def calculate_gas_savings(self, l2_network: str) -> float:
        """Calculate gas savings compared to L1"""
        l1_gas_cost = 0.05  # Average L1 gas cost in ETH
        l2_gas_costs = {
            'arbitrum': 0.001,    # 98% savings
            'optimism': 0.0008,   # 98.4% savings
            'polygon': 0.002,     # 96% savings
            'base': 0.0009,       # 98.2% savings
            'zksync': 0.0012      # 97.6% savings
        }
        l2_cost = l2_gas_costs.get(l2_network, 0.002)
        return (l1_gas_cost - l2_cost) / l1_gas_cost
    
    async def calculate_speed_advantage(self, l2_network: str) -> float:
        """Calculate speed advantage compared to L1"""
        l1_block_time = 12  # seconds
        l2_block_times = {
            'arbitrum': 0.3,      # 40x faster
            'optimism': 2,        # 6x faster
            'polygon': 2,         # 6x faster
            'base': 2,            # 6x faster
            'zksync': 0.5         # 24x faster
        }
        l2_block_time = l2_block_times.get(l2_network, 2)
        return (l1_block_time - l2_block_time) / l1_block_time
    
    async def filter_l2_opportunities(self, opportunities: List[L2Arbitrage]) -> List[L2Arbitrage]:
        """Filter and rank L2 arbitrage opportunities"""
        if not opportunities:
            return []
        
        # Filter by minimum profit
        min_profit = self.config.get('min_l2_profit_absolute', 0.001)
        profitable_ops = [op for op in opportunities if op.expected_profit >= min_profit]
        
        # Rank by profit adjusted for speed and gas savings
        ranked_ops = sorted(
            profitable_ops,
            key=lambda x: x.expected_profit * (1 + x.speed_advantage) * (1 + x.gas_savings),
            reverse=True
        )
        
        return ranked_ops[:10]  # Return top 10 opportunities
    
    async def execute_l2_arbitrage(self, opportunity: L2Arbitrage) -> Dict:
        """Execute L2 arbitrage opportunity"""
        execution_id = f"l2_exec_{opportunity.opportunity_id}"
        
        try:
            execution_steps = []
            total_cost = 0
            total_profit = 0
            
            for step in opportunity.execution_path:
                step_result = await self.execute_l2_step(step, opportunity.l2_network)
                execution_steps.append(step_result)
                
                if step_result['success']:
                    total_cost += step_result.get('cost', 0)
                else:
                    return {
                        'execution_id': execution_id,
                        'success': False,
                        'error': f"Step failed: {step_result['error']}",
                        'steps_completed': len(execution_steps),
                        'total_cost': total_cost,
                        'profit_realized': 0
                    }
            
            # Calculate actual profit
            actual_profit = opportunity.expected_profit - total_cost
            
            execution_result = {
                'execution_id': execution_id,
                'success': True,
                'l2_network': opportunity.l2_network,
                'expected_profit': opportunity.expected_profit,
                'actual_profit': actual_profit,
                'total_cost': total_cost,
                'execution_steps': execution_steps,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            self.execution_history.append(execution_result)
            return execution_result
            
        except Exception as e:
            self.logger.error(f"L2 arbitrage execution failed: {e}")
            return {
                'execution_id': execution_id,
                'success': False,
                'error': str(e),
                'profit_realized': 0
            }
    
    async def execute_l2_step(self, step: Dict, l2_network: str) -> Dict:
        """Execute individual L2 arbitrage step"""
        action = step['action']
        
        try:
            if action == 'bridge':
                return await self.execute_bridge_transfer(step, l2_network)
            elif action == 'swap':
                return await self.execute_l2_swap(step, l2_network)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def execute_bridge_transfer(self, step: Dict, l2_network: str) -> Dict:
        """Execute bridge transfer between chains"""
        # Implementation would use actual bridge contracts
        # Placeholder implementation
        
        await asyncio.sleep(1)  # Simulate bridge time
        
        return {
            'success': True,
            'action': 'bridge',
            'from_chain': step['from'],
            'to_chain': step['to'],
            'asset': step['asset'],
            'cost': 0.0001,  # Estimated bridge cost
            'duration': 1.0
        }
    
    async def execute_l2_swap(self, step: Dict, l2_network: str) -> Dict:
        """Execute swap on L2 network"""
        # Implementation would use L2 DEX contracts
        # Placeholder implementation
        
        provider = self.l2_providers.get(l2_network)
        if not provider:
            return {'success': False, 'error': f'No provider for {l2_network}'}
        
        await asyncio.sleep(0.5)  # Simulate swap time
        
        return {
            'success': True,
            'action': 'swap',
            'chain': l2_network,
            'from_asset': step['from'],
            'to_asset': step['to'],
            'cost': 0.00005,  # Estimated swap cost
            'duration': 0.5
        }
    
    async def get_l2_performance_metrics(self) -> Dict:
        """Get performance metrics for L2 arbitrage"""
        successful_executions = [
            exec for exec in self.execution_history 
            if exec['success']
        ]
        
        total_profit = sum(exec['actual_profit'] for exec in successful_executions)
        
        # Calculate metrics by L2 network
        network_stats = {}
        for execution in self.execution_history:
            network = execution['l2_network']
            if network not in network_stats:
                network_stats[network] = {'success': 0, 'total': 0, 'profit': 0}
            
            network_stats[network]['total'] += 1
            if execution['success']:
                network_stats[network]['success'] += 1
                network_stats[network]['profit'] += execution.get('actual_profit', 0)
        
        return {
            'total_l2_executions': len(self.execution_history),
            'successful_executions': len(successful_executions),
            'success_rate': len(successful_executions) / len(self.execution_history) if self.execution_history else 0,
            'total_profit': total_profit,
            'avg_profit_per_success': total_profit / len(successful_executions) if successful_executions else 0,
            'network_performance': network_stats,
            'active_opportunities': len(self.arbitrage_opportunities)
        }
    
    async def get_l2_network_analysis(self) -> Dict:
        """Get analysis of L2 network performance"""
        analysis = {}
        
        for l2_network in self.supported_l2s:
            network_executions = [
                exec for exec in self.execution_history 
                if exec['l2_network'] == l2_network
            ]
            
            if network_executions:
                successful = [e for e in network_executions if e['success']]
                success_rate = len(successful) / len(network_executions)
                avg_profit = sum(e.get('actual_profit', 0) for e in successful) / len(successful) if successful else 0
                
                analysis[l2_network] = {
                    'total_opportunities': len([op for op in self.arbitrage_opportunities if op.l2_network == l2_network]),
                    'execution_success_rate': success_rate,
                    'average_profit': avg_profit,
                    'gas_savings': await self.calculate_gas_savings(l2_network),
                    'speed_advantage': await self.calculate_speed_advantage(l2_network),
                    'reliability_score': self.calculate_reliability_score(l2_network, network_executions)
                }
        
        return analysis
    
    def calculate_reliability_score(self, l2_network: str, executions: List[Dict]) -> float:
        """Calculate reliability score for L2 network"""
        if not executions:
            return 0.5  # Neutral score
        
        successful = len([e for e in executions if e['success']])
        success_rate = successful / len(executions)
        
        # Adjust for recent performance (last 24 hours)
        recent_cutoff = asyncio.get_event_loop().time() - 86400
        recent_executions = [e for e in executions if e.get('timestamp', 0) > recent_cutoff]
        
        if recent_executions:
            recent_successful = len([e for e in recent_executions if e['success']])
            recent_success_rate = recent_successful / len(recent_executions)
            # Weight recent performance higher
            return (success_rate * 0.3 + recent_success_rate * 0.7)
        else:
            return success_rate
    
    async def generate_l2_strategy_report(self) -> Dict:
        """Generate comprehensive L2 strategy report"""
        performance_metrics = await self.get_l2_performance_metrics()
        network_analysis = await self.get_l2_network_analysis()
        
        # Top opportunities
        top_opportunities = sorted(
            self.arbitrage_opportunities,
            key=lambda x: x.expected_profit,
            reverse=True
        )[:5]
        
        return {
            'report_timestamp': asyncio.get_event_loop().time(),
            'performance_metrics': performance_metrics,
            'network_analysis': network_analysis,
            'top_opportunities': [
                {
                    'opportunity_id': op.opportunity_id,
                    'l2_network': op.l2_network,
                    'expected_profit': op.expected_profit,
                    'gas_savings': op.gas_savings,
                    'speed_advantage': op.speed_advantage
                }
                for op in top_opportunities
            ],
            'strategic_recommendations': await self.generate_l2_recommendations(network_analysis)
        }
    
    async def generate_l2_recommendations(self, network_analysis: Dict) -> List[str]:
        """Generate strategic recommendations for L2 arbitrage"""
        recommendations = []
        
        # Network performance recommendations
        for network, analysis in network_analysis.items():
            if analysis['execution_success_rate'] < 0.8:
                recommendations.append(f"Reduce exposure to {network} - low success rate ({analysis['execution_success_rate']:.1%})")
            
            if analysis['average_profit'] < 0.002:
                recommendations.append(f"Optimize strategy for {network} - low average profit ({analysis['average_profit']:.4f})")
        
        # Overall strategy recommendations
        total_opportunities = sum(analysis['total_opportunities'] for analysis in network_analysis.values())
        if total_opportunities < 10:
            recommendations.append("Increase L2 monitoring coverage for more opportunities")
        
        # Technology recommendations
        best_network = max(network_analysis.items(), 
                          key=lambda x: x[1]['execution_success_rate'] * x[1]['average_profit'],
                          default=(None, {}))
        
        if best_network[0]:
            recommendations.append(f"Focus on {best_network[0]} - best performance network")
        
        return recommendations
