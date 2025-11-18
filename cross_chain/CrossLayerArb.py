"""
AI-NEXUS CROSS-LAYER ARBITRAGE
Advanced arbitrage between Layer 1 and Layer 2 networks
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from web3 import Web3
import aiohttp

@dataclass
class CrossLayerArbitrage:
    opportunity_id: str
    source_layer: str
    target_layer: str
    asset: str
    price_discrepancy: float
    expected_profit: float
    bridge_costs: float
    execution_path: List[Dict]
    risk_score: float
    time_sensitivity: float

@dataclass
class LayerPriceData:
    layer: str
    asset: str
    price: float
    liquidity: float
    timestamp: float
    confidence: float

class CrossLayerArb:
    def __init__(self, config):
        self.config = config
        self.layer_connections = {}
        self.price_feeds = {}
        self.arbitrage_opportunities = []
        self.execution_history = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize layer connections
        self.supported_layers = config.get('supported_layers', [
            'ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync'
        ])
        self._initialize_layer_connections()
    
    def _initialize_layer_connections(self):
        """Initialize connections to all supported layers"""
        for layer in self.supported_layers:
            try:
                if layer == 'ethereum':
                    rpc_url = self.config['l1_config']['rpc_url']
                else:
                    rpc_url = self.config['l2_configs'][layer]['rpc_url']
                
                self.layer_connections[layer] = Web3(Web3.HTTPProvider(rpc_url))
                self.logger.info(f"Connected to layer: {layer}")
            except Exception as e:
                self.logger.error(f"Failed to connect to {layer}: {e}")
    
    async def monitor_cross_layer_arbitrage(self) -> List[CrossLayerArbitrage]:
        """Monitor for cross-layer arbitrage opportunities"""
        opportunities = []
        
        # Get price data from all layers
        layer_prices = await self.get_all_layer_prices()
        
        # Check for arbitrage between each layer pair
        for i, source_layer in enumerate(self.supported_layers):
            for j, target_layer in enumerate(self.supported_layers):
                if i == j:
                    continue  # Skip same layer
                
                layer_ops = await self.check_layer_pair_arbitrage(
                    source_layer, target_layer, layer_prices
                )
                opportunities.extend(layer_ops)
        
        # Filter and rank opportunities
        filtered_ops = await self.filter_cross_layer_opportunities(opportunities)
        self.arbitrage_opportunities.extend(filtered_ops)
        
        return filtered_ops
    
    async def get_all_layer_prices(self) -> Dict[str, Dict[str, LayerPriceData]]:
        """Get price data from all supported layers"""
        all_prices = {}
        
        for layer in self.supported_layers:
            layer_prices = await self.get_layer_prices(layer)
            all_prices[layer] = layer_prices
        
        return all_prices
    
    async def get_layer_prices(self, layer: str) -> Dict[str, LayerPriceData]:
        """Get price data for specific layer"""
        assets = ['ETH', 'USDC', 'USDT', 'DAI', 'WBTC']
        prices = {}
        
        for asset in assets:
            price_data = await self.fetch_asset_price(layer, asset)
            prices[asset] = price_data
        
        return prices
    
    async def fetch_asset_price(self, layer: str, asset: str) -> LayerPriceData:
        """Fetch asset price from layer-specific sources"""
        # Implementation would use actual price feeds
        # Placeholder with simulated data
        
        base_price = {
            'ETH': 1000,
            'USDC': 1.0,
            'USDT': 1.0,
            'DAI': 1.0,
            'WBTC': 30000
        }[asset]
        
        # Simulate layer-specific price variations
        layer_variations = {
            'ethereum': 0.0,      # Base price
            'arbitrum': 0.002,    # 0.2% typically cheaper
            'optimism': 0.0015,   # 0.15% typically cheaper
            'polygon': 0.003,     # 0.3% typically cheaper
            'base': 0.002,        # 0.2% typically cheaper
            'zksync': 0.0025      # 0.25% typically cheaper
        }
        
        variation = layer_variations.get(layer, 0.0)
        price = base_price * (1 - variation)  # L2s often have slightly lower prices
        
        return LayerPriceData(
            layer=layer,
            asset=asset,
            price=price,
            liquidity=await self.estimate_layer_liquidity(layer, asset),
            timestamp=asyncio.get_event_loop().time(),
            confidence=await self.calculate_price_confidence(layer, asset)
        )
    
    async def estimate_layer_liquidity(self, layer: str, asset: str) -> float:
        """Estimate liquidity for asset on layer"""
        # Base liquidity estimates in USD
        base_liquidity = {
            'ethereum': 10000000,   # $10M
            'arbitrum': 5000000,    # $5M
            'optimism': 3000000,    # $3M
            'polygon': 2000000,     # $2M
            'base': 1500000,        # $1.5M
            'zksync': 1000000       # $1M
        }
        
        asset_multipliers = {
            'ETH': 1.0,
            'USDC': 0.8,
            'USDT': 0.8,
            'DAI': 0.6,
            'WBTC': 0.4
        }
        
        base = base_liquidity.get(layer, 1000000)
        multiplier = asset_multipliers.get(asset, 0.5)
        
        return base * multiplier
    
    async def calculate_price_confidence(self, layer: str, asset: str) -> float:
        """Calculate confidence in price data"""
        # Factors: data recency, source reliability, market depth
        base_confidence = 0.9
        
        # Adjust for layer reliability
        layer_reliability = {
            'ethereum': 0.99,
            'arbitrum': 0.95,
            'optimism': 0.96,
            'polygon': 0.92,
            'base': 0.94,
            'zksync': 0.91
        }
        
        reliability = layer_reliability.get(layer, 0.9)
        return base_confidence * reliability
    
    async def check_layer_pair_arbitrage(self, source_layer: str, target_layer: str,
                                       layer_prices: Dict) -> List[CrossLayerArbitrage]:
        """Check arbitrage opportunities between layer pair"""
        opportunities = []
        
        source_prices = layer_prices.get(source_layer, {})
        target_prices = layer_prices.get(target_layer, {})
        
        for asset in source_prices.keys():
            if asset in target_prices:
                source_data = source_prices[asset]
                target_data = target_prices[asset]
                
                # Calculate price discrepancy
                if source_data.price > 0 and target_data.price > 0:
                    discrepancy = (source_data.price - target_data.price) / source_data.price
                    
                    # Only consider significant discrepancies
                    if abs(discrepancy) > self.config.get('min_cross_layer_discrepancy', 0.008):
                        # Calculate costs and expected profit
                        bridge_cost = await self.estimate_cross_layer_cost(source_layer, target_layer, asset)
                        execution_cost = await self.estimate_execution_costs(source_layer, target_layer)
                        
                        expected_profit = abs(discrepancy) - bridge_cost - execution_cost
                        
                        if expected_profit > self.config.get('min_cross_layer_profit', 0.005):
                            opportunity = CrossLayerArbitrage(
                                opportunity_id=f"cross_{source_layer}_{target_layer}_{asset}_{int(asyncio.get_event_loop().time())}",
                                source_layer=source_layer,
                                target_layer=target_layer,
                                asset=asset,
                                price_discrepancy=discrepancy,
                                expected_profit=expected_profit,
                                bridge_costs=bridge_cost,
                                execution_path=await self.generate_cross_layer_path(
                                    source_layer, target_layer, asset, discrepancy > 0
                                ),
                                risk_score=await self.calculate_cross_layer_risk(
                                    source_layer, target_layer, source_data, target_data
                                ),
                                time_sensitivity=await self.calculate_time_sensitivity(
                                    source_layer, target_layer, asset
                                )
                            )
                            opportunities.append(opportunity)
        
        return opportunities
    
    async def estimate_cross_layer_cost(self, source_layer: str, target_layer: str, 
                                      asset: str) -> float:
        """Estimate cost to move asset between layers"""
        # Bridge costs vary by layer pair and asset
        base_bridge_costs = {
            ('ethereum', 'arbitrum'): 0.0005,
            ('ethereum', 'optimism'): 0.0004,
            ('ethereum', 'polygon'): 0.001,
            ('ethereum', 'base'): 0.00045,
            ('ethereum', 'zksync'): 0.0006,
            # Reverse directions (withdrawal costs)
            ('arbitrum', 'ethereum'): 0.001,
            ('optimism', 'ethereum'): 0.0008,
            ('polygon', 'ethereum'): 0.002,
            ('base', 'ethereum'): 0.0009,
            ('zksync', 'ethereum'): 0.0012
        }
        
        # Additional costs for L2->L2 via L1
        if source_layer != 'ethereum' and target_layer != 'ethereum':
            # Route through Ethereum
            cost1 = base_bridge_costs.get((source_layer, 'ethereum'), 0.001)
            cost2 = base_bridge_costs.get(('ethereum', target_layer), 0.001)
            return cost1 + cost2
        else:
            return base_bridge_costs.get((source_layer, target_layer), 0.001)
    
    async def estimate_execution_costs(self, source_layer: str, target_layer: str) -> float:
        """Estimate execution costs on both layers"""
        # Gas costs for swaps and other operations
        source_cost = await self.estimate_layer_execution_cost(source_layer)
        target_cost = await self.estimate_layer_execution_cost(target_layer)
        
        return source_cost + target_cost
    
    async def estimate_layer_execution_cost(self, layer: str) -> float:
        """Estimate execution cost for a layer"""
        layer_costs = {
            'ethereum': 0.005,    # Higher L1 costs
            'arbitrum': 0.0001,
            'optimism': 0.00008,
            'polygon': 0.0002,
            'base': 0.00009,
            'zksync': 0.00015
        }
        return layer_costs.get(layer, 0.001)
    
    async def generate_cross_layer_path(self, source_layer: str, target_layer: str,
                                      asset: str, buy_on_target: bool) -> List[Dict]:
        """Generate execution path for cross-layer arbitrage"""
        if buy_on_target:
            return [
                {'action': 'bridge', 'from': source_layer, 'to': target_layer, 'asset': 'ETH'},
                {'action': 'swap', 'chain': target_layer, 'from': 'ETH', 'to': asset},
                {'action': 'bridge', 'from': target_layer, 'to': source_layer, 'asset': asset},
                {'action': 'swap', 'chain': source_layer, 'from': asset, 'to': 'ETH'}
            ]
        else:
            return [
                {'action': 'bridge', 'from': source_layer, 'to': target_layer, 'asset': asset},
                {'action': 'swap', 'chain': target_layer, 'from': asset, 'to': 'ETH'},
                {'action': 'bridge', 'from': target_layer, 'to': source_layer, 'asset': 'ETH'}
            ]
    
    async def calculate_cross_layer_risk(self, source_layer: str, target_layer: str,
                                       source_data: LayerPriceData, 
                                       target_data: LayerPriceData) -> float:
        """Calculate risk score for cross-layer arbitrage"""
        risk_factors = []
        
        # Bridge risk
        bridge_risk = await self.estimate_bridge_risk(source_layer, target_layer)
        risk_factors.append(bridge_risk)
        
        # Liquidity risk
        min_liquidity = min(source_data.liquidity, target_data.liquidity)
        liquidity_risk = 1 - (min_liquidity / 1000000)  # Normalize to $1M
        risk_factors.append(max(0, min(1, liquidity_risk)))
        
        # Price confidence risk
        confidence_risk = 1 - ((source_data.confidence + target_data.confidence) / 2)
        risk_factors.append(confidence_risk)
        
        # Layer stability risk
        stability_risk = await self.estimate_layer_stability_risk(source_layer, target_layer)
        risk_factors.append(stability_risk)
        
        return sum(risk_factors) / len(risk_factors)
    
    async def estimate_bridge_risk(self, source_layer: str, target_layer: str) -> float:
        """Estimate risk associated with bridge transfer"""
        bridge_risks = {
            ('ethereum', 'arbitrum'): 0.1,
            ('ethereum', 'optimism'): 0.08,
            ('ethereum', 'polygon'): 0.15,
            ('ethereum', 'base'): 0.09,
            ('ethereum', 'zksync'): 0.12,
            # Withdrawals typically higher risk
            ('arbitrum', 'ethereum'): 0.2,
            ('optimism', 'ethereum'): 0.18,
            ('polygon', 'ethereum'): 0.25,
            ('base', 'ethereum'): 0.19,
            ('zksync', 'ethereum'): 0.22
        }
        
        return bridge_risks.get((source_layer, target_layer), 0.3)
    
    async def estimate_layer_stability_risk(self, layer1: str, layer2: str) -> float:
        """Estimate stability risk for layer pair"""
        layer_stability = {
            'ethereum': 0.99,
            'arbitrum': 0.95,
            'optimism': 0.96,
            'polygon': 0.92,
            'base': 0.94,
            'zksync': 0.91
        }
        
        stability1 = layer_stability.get(layer1, 0.9)
        stability2 = layer_stability.get(layer2, 0.9)
        
        return 1 - (stability1 * stability2)
    
    async def calculate_time_sensitivity(self, source_layer: str, target_layer: str,
                                      asset: str) -> float:
        """Calculate time sensitivity of arbitrage opportunity"""
        # Factors: price volatility, bridge time, competition
        
        # Price volatility factor
        volatility = await self.estimate_asset_volatility(asset)
        
        # Bridge time factor
        bridge_time = await self.estimate_bridge_time(source_layer, target_layer)
        time_factor = min(1.0, bridge_time / 300)  # Normalize to 5 minutes
        
        # Competition factor (simplified)
        competition = 0.3  # Base competition level
        
        return (volatility * 0.5 + time_factor * 0.3 + competition * 0.2)
    
    async def estimate_asset_volatility(self, asset: str) -> float:
        """Estimate price volatility for asset"""
        volatilities = {
            'ETH': 0.02,   # 2% typical volatility
            'USDC': 0.001, # 0.1% typical volatility
            'USDT': 0.001, # 0.1% typical volatility
            'DAI': 0.002,  # 0.2% typical volatility
            'WBTC': 0.015  # 1.5% typical volatility
        }
        return volatilities.get(asset, 0.01)
    
    async def estimate_bridge_time(self, source_layer: str, target_layer: str) -> float:
        """Estimate bridge transfer time in seconds"""
        bridge_times = {
            ('ethereum', 'arbitrum'): 600,    # 10 minutes
            ('ethereum', 'optimism'): 300,    # 5 minutes
            ('ethereum', 'polygon'): 180,     # 3 minutes
            ('ethereum', 'base'): 300,        # 5 minutes
            ('ethereum', 'zksync'): 240,      # 4 minutes
            # Withdrawals typically longer
            ('arbitrum', 'ethereum'): 3600,   # 1 hour (challenge period)
            ('optimism', 'ethereum'): 3600,   # 1 hour (challenge period)
            ('polygon', 'ethereum'): 1800,    # 30 minutes
            ('base', 'ethereum'): 3600,       # 1 hour
            ('zksync', 'ethereum'): 1800      # 30 minutes
        }
        
        return bridge_times.get((source_layer, target_layer), 600)
    
    async def filter_cross_layer_opportunities(self, opportunities: List[CrossLayerArbitrage]) -> List[CrossLayerArbitrage]:
        """Filter and rank cross-layer arbitrage opportunities"""
        if not opportunities:
            return []
        
        # Filter by minimum profit
        min_profit = self.config.get('min_cross_layer_profit_absolute', 0.002)
        profitable_ops = [op for op in opportunities if op.expected_profit >= min_profit]
        
        # Filter by maximum risk
        max_risk = self.config.get('max_cross_layer_risk', 0.7)
        low_risk_ops = [op for op in profitable_ops if op.risk_score <= max_risk]
        
        # Rank by profit-to-risk ratio adjusted for time sensitivity
        ranked_ops = sorted(
            low_risk_ops,
            key=lambda x: (x.expected_profit / (x.risk_score + 0.01)) * (1 - x.time_sensitivity),
            reverse=True
        )
        
        return ranked_ops[:15]  # Return top 15 opportunities
    
    async def execute_cross_layer_arbitrage(self, opportunity: CrossLayerArbitrage) -> Dict:
        """Execute cross-layer arbitrage opportunity"""
        execution_id = f"cross_exec_{opportunity.opportunity_id}"
        
        try:
            execution_steps = []
            total_cost = 0
            step_results = []
            
            for step in opportunity.execution_path:
                step_result = await self.execute_cross_layer_step(step, opportunity)
                step_results.append(step_result)
                
                if step_result['success']:
                    execution_steps.append(step_result)
                    total_cost += step_result.get('cost', 0)
                else:
                    # Handle step failure
                    await self.handle_execution_failure(opportunity, step_results)
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
                'source_layer': opportunity.source_layer,
                'target_layer': opportunity.target_layer,
                'asset': opportunity.asset,
                'expected_profit': opportunity.expected_profit,
                'actual_profit': actual_profit,
                'total_cost': total_cost,
                'execution_steps': execution_steps,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            self.execution_history.append(execution_result)
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Cross-layer arbitrage execution failed: {e}")
            return {
                'execution_id': execution_id,
                'success': False,
                'error': str(e),
                'profit_realized': 0
            }
    
    async def execute_cross_layer_step(self, step: Dict, opportunity: CrossLayerArbitrage) -> Dict:
        """Execute individual cross-layer arbitrage step"""
        action = step['action']
        
        try:
            if action == 'bridge':
                return await self.execute_cross_layer_bridge(step, opportunity)
            elif action == 'swap':
                return await self.execute_cross_layer_swap(step, opportunity)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def execute_cross_layer_bridge(self, step: Dict, opportunity: CrossLayerArbitrage) -> Dict:
        """Execute cross-layer bridge transfer"""
        from_layer = step['from']
        to_layer = step['to']
        asset = step['asset']
        
        # Implementation would use actual bridge contracts
        # Placeholder implementation
        
        bridge_time = await self.estimate_bridge_time(from_layer, to_layer)
        await asyncio.sleep(min(bridge_time / 10, 5))  # Simulate bridge time
        
        return {
            'success': True,
            'action': 'bridge',
            'from_layer': from_layer,
            'to_layer': to_layer,
            'asset': asset,
            'cost': await self.estimate_cross_layer_cost(from_layer, to_layer, asset),
            'duration': bridge_time / 10  # Simulated duration
        }
    
    async def execute_cross_layer_swap(self, step: Dict, opportunity: CrossLayerArbitrage) -> Dict:
        """Execute swap on specific layer"""
        layer = step['chain']
        from_asset = step['from']
        to_asset = step['to']
        
        provider = self.layer_connections.get(layer)
        if not provider:
            return {'success': False, 'error': f'No provider for layer: {layer}'}
        
        # Implementation would use layer-specific DEX contracts
        # Placeholder implementation
        
        await asyncio.sleep(1)  # Simulate swap time
        
        return {
            'success': True,
            'action': 'swap',
            'layer': layer,
            'from_asset': from_asset,
            'to_asset': to_asset,
            'cost': await self.estimate_layer_execution_cost(layer),
            'duration': 1.0
        }
    
    async def handle_execution_failure(self, opportunity: CrossLayerArbitrage, 
                                    step_results: List[Dict]):
        """Handle execution failure and attempt recovery"""
        self.logger.warning(f"Execution failed for {opportunity.opportunity_id}")
        
        # Attempt to recover funds from completed steps
        recovery_attempts = []
        for result in step_results:
            if result['success'] and result['action'] == 'bridge':
                # Attempt to reverse bridge transfer
                recovery_result = await self.attempt_bridge_reversal(result, opportunity)
                recovery_attempts.append(recovery_result)
        
        self.logger.info(f"Recovery attempts: {len([r for r in recovery_attempts if r['success']])} successful")
    
    async def attempt_bridge_reversal(self, bridge_result: Dict, 
                                    opportunity: CrossLayerArbitrage) -> Dict:
        """Attempt to reverse a bridge transfer"""
        # Implementation would attempt to reverse or recover funds
        # Placeholder implementation
        
        return {
            'success': False,  # Bridge reversals are typically not possible
            'action': 'bridge_reversal',
            'message': 'Bridge transfers are typically irreversible'
        }
    
    async def get_cross_layer_performance_metrics(self) -> Dict:
        """Get performance metrics for cross-layer arbitrage"""
        successful_executions = [
            exec for exec in self.execution_history 
            if exec['success']
        ]
        
        total_profit = sum(exec['actual_profit'] for exec in successful_executions)
        
        # Calculate metrics by layer pair
        layer_pair_stats = {}
        for execution in self.execution_history:
            pair_key = f"{execution['source_layer']}_{execution['target_layer']}"
            if pair_key not in layer_pair_stats:
                layer_pair_stats[pair_key] = {'success': 0, 'total': 0, 'profit': 0}
            
            layer_pair_stats[pair_key]['total'] += 1
            if execution['success']:
                layer_pair_stats[pair_key]['success'] += 1
                layer_pair_stats[pair_key]['profit'] += execution.get('actual_profit', 0)
        
        return {
            'total_cross_layer_executions': len(self.execution_history),
            'successful_executions': len(successful_executions),
            'success_rate': len(successful_executions) / len(self.execution_history) if self.execution_history else 0,
            'total_profit': total_profit,
            'avg_profit_per_success': total_profit / len(successful_executions) if successful_executions else 0,
            'layer_pair_performance': layer_pair_stats,
            'active_opportunities': len(self.arbitrage_opportunities)
        }
    
    async def generate_cross_layer_report(self) -> Dict:
        """Generate comprehensive cross-layer arbitrage report"""
        performance_metrics = await self.get_cross_layer_performance_metrics()
        
        # Top opportunities
        top_opportunities = sorted(
            self.arbitrage_opportunities,
            key=lambda x: x.expected_profit,
            reverse=True
        )[:5]
        
        # Layer pair analysis
        layer_pairs = set()
        for op in self.arbitrage_opportunities:
            layer_pairs.add(f"{op.source_layer}_{op.target_layer}")
        
        return {
            'report_timestamp': asyncio.get_event_loop().time(),
            'performance_metrics': performance_metrics,
            'top_opportunities': [
                {
                    'opportunity_id': op.opportunity_id,
                    'source_layer': op.source_layer,
                    'target_layer': op.target_layer,
                    'asset': op.asset,
                    'expected_profit': op.expected_profit,
                    'risk_score': op.risk_score,
                    'time_sensitivity': op.time_sensitivity
                }
                for op in top_opportunities
            ],
            'active_layer_pairs': list(layer_pairs),
            'recommendations': await self.generate_cross_layer_recommendations(performance_metrics)
        }
    
    async def generate_cross_layer_recommendations(self, performance_metrics: Dict) -> List[str]:
        """Generate strategic recommendations for cross-layer arbitrage"""
        recommendations = []
        
        success_rate = performance_metrics.get('success_rate', 0)
        if success_rate < 0.8:
            recommendations.append("Improve execution success rate through better risk assessment")
        
        # Layer pair recommendations
        layer_pair_performance = performance_metrics.get('layer_pair_performance', {})
        for pair, stats in layer_pair_performance.items():
            pair_success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
            if pair_success_rate < 0.7:
                recommendations.append(f"Review strategy for {pair} - low success rate ({pair_success_rate:.1%})")
        
        # Opportunity volume recommendations
        active_opportunities = performance_metrics.get('active_opportunities', 0)
        if active_opportunities < 10:
            recommendations.append("Increase monitoring coverage for more cross-layer opportunities")
        
        return recommendations
