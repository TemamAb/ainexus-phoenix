"""
AI-NEXUS GAS AUCTION MANAGER
Dynamic gas auction management for competitive transaction inclusion
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict
import time

@dataclass
class GasBid:
    transaction_hash: str
    max_fee: float  # in Gwei
    priority_fee: float  # in Gwei
    bid_timestamp: float
    urgency: str
    transaction_value: float

@dataclass
class AuctionRound:
    block_number: int
    winning_bids: List[GasBid]
    cutoff_priority_fee: float
    total_bids: int
    timestamp: float

class GasAuctionManager:
    def __init__(self, config):
        self.config = config
        self.active_bids = {}
        self.auction_history = []
        self.bid_strategies = {}
        self.competitor_analysis = CompetitorAnalysis()
        self.logger = logging.getLogger(__name__)
        
        # Initialize bidding strategies
        self._initialize_bid_strategies()
    
    def _initialize_bid_strategies(self):
        """Initialize different gas bidding strategies"""
        self.bid_strategies = {
            'conservative': {
                'base_multiplier': 1.0,
                'urgency_weights': {'low': 0.8, 'medium': 1.0, 'high': 1.3, 'critical': 2.0},
                'value_weights': {0: 1.0, 1: 1.1, 10: 1.3, 100: 1.5},
                'description': 'Cost-optimized, lower inclusion probability'
            },
            'balanced': {
                'base_multiplier': 1.2,
                'urgency_weights': {'low': 1.0, 'medium': 1.2, 'high': 1.6, 'critical': 2.5},
                'value_weights': {0: 1.0, 1: 1.2, 10: 1.5, 100: 2.0},
                'description': 'Balanced cost and inclusion probability'
            },
            'aggressive': {
                'base_multiplier': 1.5,
                'urgency_weights': {'low': 1.2, 'medium': 1.5, 'high': 2.0, 'critical': 3.0},
                'value_weights': {0: 1.0, 1: 1.3, 10: 1.8, 100: 2.5},
                'description': 'Inclusion-optimized, higher cost'
            },
            'maximum': {
                'base_multiplier': 2.0,
                'urgency_weights': {'low': 1.5, 'medium': 2.0, 'high': 2.5, 'critical': 4.0},
                'value_weights': {0: 1.0, 1: 1.5, 10: 2.0, 100: 3.0},
                'description': 'Maximum inclusion probability'
            }
        }
    
    async def place_gas_bid(self, transaction_hash: str, base_priority_fee: float, 
                          urgency: str, transaction_value: float, strategy: str = 'balanced') -> GasBid:
        """Place a gas bid for transaction inclusion"""
        # Get bidding strategy
        bid_strategy = self.bid_strategies.get(strategy, self.bid_strategies['balanced'])
        
        # Calculate bid amount
        priority_fee = self._calculate_bid_amount(base_priority_fee, urgency, transaction_value, bid_strategy)
        
        # Apply competitor adjustment
        competitor_adjustment = await self.competitor_analysis.get_priority_fee_adjustment()
        adjusted_priority_fee = priority_fee * (1 + competitor_adjustment)
        
        # Calculate max fee (base fee estimation + priority fee with buffer)
        base_fee_estimate = await self._get_base_fee_estimate()
        max_fee = base_fee_estimate * 1.2 + adjusted_priority_fee  # 20% buffer on base fee
        
        bid = GasBid(
            transaction_hash=transaction_hash,
            max_fee=max_fee,
            priority_fee=adjusted_priority_fee,
            bid_timestamp=time.time(),
            urgency=urgency,
            transaction_value=transaction_value
        )
        
        self.active_bids[transaction_hash] = bid
        self.logger.info(f"Gas bid placed: {bid}")
        
        return bid
    
    def _calculate_bid_amount(self, base_priority_fee: float, urgency: str, 
                            transaction_value: float, strategy: Dict) -> float:
        """Calculate bid amount based on strategy and parameters"""
        # Apply base multiplier
        bid_amount = base_priority_fee * strategy['base_multiplier']
        
        # Apply urgency weight
        urgency_weight = strategy['urgency_weights'].get(urgency, 1.0)
        bid_amount *= urgency_weight
        
        # Apply transaction value weight
        value_weight = 1.0
        for value_threshold, weight in sorted(strategy['value_weights'].items()):
            if transaction_value >= value_threshold:
                value_weight = weight
        bid_amount *= value_weight
        
        return max(base_priority_fee, bid_amount)  # Ensure at least base amount
    
    async def _get_base_fee_estimate(self) -> float:
        """Get base fee estimate for next block"""
        # Implementation would fetch current base fee and predict next block
        # For now, return a conservative estimate
        return 30.0  # Gwei
    
    async def simulate_auction_round(self, block_number: int, competing_bids: List[GasBid]) -> AuctionRound:
        """Simulate gas auction round to determine inclusion"""
        all_bids = list(self.active_bids.values()) + competing_bids
        
        if not all_bids:
            return AuctionRound(
                block_number=block_number,
                winning_bids=[],
                cutoff_priority_fee=0,
                total_bids=0,
                timestamp=time.time()
            )
        
        # Sort bids by priority fee (descending)
        sorted_bids = sorted(all_bids, key=lambda x: x.priority_fee, reverse=True)
        
        # Simulate block space (assume 80% of gas limit for priority transactions)
        gas_limit = 15_000_000  # Standard block gas limit
        available_gas = gas_limit * 0.8
        gas_used = 0
        
        winning_bids = []
        cutoff_priority_fee = 0
        
        for bid in sorted_bids:
            # Assume average transaction gas usage
            tx_gas = 100_000  # Conservative estimate
            
            if gas_used + tx_gas <= available_gas:
                winning_bids.append(bid)
                gas_used += tx_gas
                cutoff_priority_fee = bid.priority_fee
            else:
                break
        
        auction_round = AuctionRound(
            block_number=block_number,
            winning_bids=winning_bids,
            cutoff_priority_fee=cutoff_priority_fee,
            total_bids=len(all_bids),
            timestamp=time.time()
        )
        
        self.auction_history.append(auction_round)
        
        # Update competitor analysis
        await self.competitor_analysis.analyze_auction_results(auction_round)
        
        # Clear active bids (in real implementation, would only clear included bids)
        self.active_bids.clear()
        
        return auction_round
    
    def get_optimal_bid_strategy(self, transaction_value: float, time_sensitivity: str) -> str:
        """Get optimal bidding strategy based on transaction parameters"""
        if time_sensitivity == 'critical' or transaction_value > 50:
            return 'maximum'
        elif time_sensitivity == 'high' or transaction_value > 10:
            return 'aggressive'
        elif time_sensitivity == 'medium' or transaction_value > 1:
            return 'balanced'
        else:
            return 'conservative'
    
    def get_auction_statistics(self, lookback_blocks: int = 100) -> Dict:
        """Get gas auction statistics"""
        recent_auctions = [
            auction for auction in self.auction_history 
            if len(self.auction_history) - self.auction_history.index(auction) <= lookback_blocks
        ]
        
        if not recent_auctions:
            return {}
        
        cutoff_fees = [auction.cutoff_priority_fee for auction in recent_auctions]
        bid_counts = [auction.total_bids for auction in recent_auctions]
        
        return {
            'average_cutoff_fee': sum(cutoff_fees) / len(cutoff_fees),
            'median_cutoff_fee': sorted(cutoff_fees)[len(cutoff_fees) // 2],
            'max_cutoff_fee': max(cutoff_fees),
            'min_cutoff_fee': min(cutoff_fees),
            'average_bids_per_block': sum(bid_counts) / len(bid_counts),
            'inclusion_rate': self._calculate_inclusion_rate(recent_auctions),
            'cost_efficiency': self._calculate_cost_efficiency(recent_auctions)
        }
    
    def _calculate_inclusion_rate(self, auctions: List[AuctionRound]) -> float:
        """Calculate our bid inclusion rate"""
        our_bids_included = 0
        our_total_bids = 0
        
        for auction in auctions:
            our_bids_in_block = sum(1 for bid in auction.winning_bids if bid.transaction_hash in self.active_bids)
            our_bids_included += our_bids_in_block
            our_total_bids += sum(1 for bid in auction.winning_bids)  # Approximation
        
        return our_bids_included / our_total_bids if our_total_bids > 0 else 0
    
    def _calculate_cost_efficiency(self, auctions: List[AuctionRound]) -> float:
        """Calculate cost efficiency of our bidding strategy"""
        # Compare our bid prices to cutoff prices
        total_overbid = 0
        total_comparisons = 0
        
        for auction in auctions:
            for bid in auction.winning_bids:
                if bid.transaction_hash in self.active_bids:
                    overbid_amount = bid.priority_fee - auction.cutoff_priority_fee
                    total_overbid += max(0, overbid_amount)
                    total_comparisons += 1
        
        return 1 - (total_overbid / total_comparisons) if total_comparisons > 0 else 1
    
    async def optimize_bid_strategy(self) -> Dict:
        """Continuously optimize bidding strategy based on historical performance"""
        stats = self.get_auction_statistics()
        competitor_behavior = await self.competitor_analysis.get_behavior_patterns()
        
        # Adjust strategies based on performance
        optimized_strategies = {}
        
        for strategy_name, strategy in self.bid_strategies.items():
            optimized_strategy = strategy.copy()
            
            # Adjust based on market conditions
            if stats.get('average_cutoff_fee', 0) > 10:  # High fee environment
                optimized_strategy['base_multiplier'] *= 1.1
            elif stats.get('average_cutoff_fee', 0) < 2:  # Low fee environment
                optimized_strategy['base_multiplier'] *= 0.9
            
            # Adjust based on competitor aggression
            if competitor_behavior.get('aggression_level') == 'high':
                optimized_strategy['base_multiplier'] *= 1.05
            
            optimized_strategies[strategy_name] = optimized_strategy
        
        self.bid_strategies.update(optimized_strategies)
        
        return {
            'optimization_applied': True,
            'old_strategies': self.bid_strategies,
            'new_strategies': optimized_strategies,
            'optimization_factors': {
                'market_conditions': stats.get('average_cutoff_fee', 0),
                'competitor_aggression': competitor_behavior.get('aggression_level', 'medium')
            }
        }

class CompetitorAnalysis:
    """Analyze competitor bidding behavior"""
    
    def __init__(self):
        self.competitor_bids = defaultdict(list)
        self.behavior_patterns = {}
    
    async def analyze_auction_results(self, auction_round: AuctionRound):
        """Analyze competitor behavior from auction results"""
        for bid in auction_round.winning_bids:
            # Group by transaction patterns (simplified)
            competitor_id = self._identify_competitor(bid)
            self.competitor_bids[competitor_id].append(bid)
        
        # Update behavior patterns
        self._update_behavior_patterns()
    
    def _identify_competitor(self, bid: GasBid) -> str:
        """Identify competitor based on bidding patterns"""
        # Simplified implementation - in production would use more sophisticated clustering
        if bid.priority_fee > 10:
            return 'aggressive_bidder'
        elif bid.priority_fee > 5:
            return 'balanced_bidder'
        else:
            return 'conservative_bidder'
    
    def _update_behavior_patterns(self):
        """Update competitor behavior patterns"""
        patterns = {}
        
        for competitor, bids in self.competitor_bids.items():
            if bids:
                priority_fees = [bid.priority_fee for bid in bids]
                avg_fee = sum(priority_fees) / len(priority_fees)
                
                if avg_fee > 8:
                    patterns[competitor] = {'aggression_level': 'high', 'consistency': 'high'}
                elif avg_fee > 4:
                    patterns[competitor] = {'aggression_level': 'medium', 'consistency': 'medium'}
                else:
                    patterns[competitor] = {'aggression_level': 'low', 'consistency': 'high'}
        
        self.behavior_patterns = patterns
    
    async def get_priority_fee_adjustment(self) -> float:
        """Get adjustment factor based on competitor behavior"""
        if not self.behavior_patterns:
            return 0.0
        
        # Calculate average aggression level
        total_aggression = 0
        for pattern in self.behavior_patterns.values():
            aggression_map = {'high': 0.1, 'medium': 0.05, 'low': 0.0}
            total_aggression += aggression_map.get(pattern['aggression_level'], 0.0)
        
        avg_aggression = total_aggression / len(self.behavior_patterns)
        return avg_aggression
    
    def get_behavior_patterns(self) -> Dict:
        """Get current competitor behavior patterns"""
        return self.behavior_patterns
