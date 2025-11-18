#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENHANCED: Strategy Auction System for Multi-Agent Capital Allocation
Competitive bidding for capital allocation among AI trading strategies
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class AuctionBid:
    """Represents a strategy bid in the capital auction"""
    strategy_id: str
    agent_id: str
    expected_roi: float
    risk_score: float
    capital_requested: float
    confidence: float
    
class StrategyAuction:
    """Enhanced capital allocation through competitive bidding"""
    
    def __init__(self):
        self.active_bids: Dict[str, AuctionBid] = {}
        self.auction_history: List[Dict] = []
        self.capital_pool = 0.0
        
    def submit_bid(self, strategy_id: str, agent_id: str, expected_roi: float, 
                   risk_score: float, capital_requested: float, confidence: float) -> bool:
        """Submit a bid for capital allocation"""
        bid = AuctionBid(
            strategy_id=strategy_id,
            agent_id=agent_id,
            expected_roi=expected_roi,
            risk_score=risk_score,
            capital_requested=capital_requested,
            confidence=confidence
        )
        
        self.active_bids[strategy_id] = bid
        return True
    
    def run_auction(self, available_capital: float) -> Dict[str, float]:
        """Run capital allocation auction"""
        if not self.active_bids:
            return {}
            
        # Calculate bid scores (ROI * Confidence / Risk)
        bid_scores = {}
        for strategy_id, bid in self.active_bids.items():
            score = (bid.expected_roi * bid.confidence) / max(bid.risk_score, 0.1)
            bid_scores[strategy_id] = score
        
        # Allocate capital proportionally to scores
        total_score = sum(bid_scores.values())
        allocations = {}
        
        for strategy_id, score in bid_scores.items():
            allocation = (score / total_score) * available_capital
            allocations[strategy_id] = allocation
            
        # Record auction results
        auction_result = {
            'timestamp': np.datetime64('now'),
            'available_capital': available_capital,
            'allocations': allocations.copy(),
            'bid_count': len(self.active_bids)
        }
        self.auction_history.append(auction_result)
        
        # Clear active bids for next round
        self.active_bids.clear()
        
        return allocations
    
    def get_auction_metrics(self) -> Dict[str, Any]:
        """Get auction performance metrics"""
        if not self.auction_history:
            return {}
            
        recent_auctions = self.auction_history[-10:]  # Last 10 auctions
        total_allocated = sum(auction['available_capital'] for auction in recent_auctions)
        avg_bids = np.mean([auction['bid_count'] for auction in recent_auctions])
        
        return {
            'recent_auctions': len(recent_auctions),
            'total_capital_allocated': total_allocated,
            'average_bids_per_auction': avg_bids,
            'auction_efficiency': self.calculate_efficiency()
        }
    
    def calculate_efficiency(self) -> float:
        """Calculate capital allocation efficiency"""
        if len(self.auction_history) < 2:
            return 0.0
            
        # Simple efficiency metric based on capital utilization
        recent_utilization = [
            sum(auction['allocations'].values()) / auction['available_capital']
            for auction in self.auction_history[-5:]
        ]
        return np.mean(recent_utilization)

# Enhanced integration with DecisionAgent
class CooperativeLearning:
    """Multi-agent cooperative learning enhancements"""
    
    def __init__(self):
        self.agent_network = {}
        self.knowledge_base = {}
        
    def share_insights(self, agent_id: str, insights: Dict) -> bool:
        """Share trading insights across agent network"""
        self.knowledge_base[agent_id] = insights
        return True
    
    def get_collective_intelligence(self) -> Dict:
        """Get aggregated intelligence from all agents"""
        collective_insights = {}
        for agent_id, insights in self.knowledge_base.items():
            for key, value in insights.items():
                if key not in collective_insights:
                    collective_insights[key] = []
                collective_insights[key].append(value)
        
        # Aggregate insights
        aggregated = {}
        for key, values in collective_insights.items():
            if all(isinstance(v, (int, float)) for v in values):
                aggregated[key] = np.mean(values)
            else:
                aggregated[key] = values[-1]  # Most recent non-numeric
        
        return aggregated

if __name__ == "__main__":
    # Test the auction system
    auction = StrategyAuction()
    print("✅ Strategy Auction System Initialized")
    
    # Test cooperative learning
    coop = CooperativeLearning()
    print("✅ Cooperative Learning System Initialized")
