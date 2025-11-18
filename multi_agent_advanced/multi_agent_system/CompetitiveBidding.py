"""
Competitive Bidding System for Multi-Agent Trading

Advanced auction-based bidding system where multiple trading agents
compete and collaborate to execute optimal trades in dynamic market conditions.

Key Features:
- Real-time auction mechanisms
- Multi-agent bidding strategies
- Market impact modeling
- Collusion detection and prevention
- Dynamic reserve pricing
- Bid optimization algorithms
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import asyncio
import random
from collections import defaultdict, deque
import heapq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuctionType(Enum):
    """Types of auction mechanisms"""
    ENGLISH = "english"           # Ascending price, open outcry
    DUTCH = "dutch"              # Descending price
    SEALED_BID = "sealed_bid"    # Secret bids, highest wins
    VICKREY = "vickrey"          # Second-price sealed bid
    DOUBLE_AUCTION = "double"    # Buyers and sellers bid simultaneously
    COMBINATORIAL = "combinatorial"  # Multiple items bundled

class BidStrategy(Enum):
    """Bidding strategies for agents"""
    TRUTHFUL = "truthful"        # Bid true valuation
    AGGRESSIVE = "aggressive"    # Overbid to secure position
    CONSERVATIVE = "conservative" # Underbid for safety
    SNIPING = "sniping"          # Last-moment bidding
    SHADING = "shading"          # Strategic underbidding
    COLLUSIVE = "collusive"      # Coordinated with other agents

class MarketRegime(Enum):
    """Market regime classifications"""
    NORMAL = "normal"
    VOLATILE = "volatile"
    ILLIQUID = "illiquid"
    CRISIS = "crisis"
    AUCTION = "auction_driven"

@dataclass
class Bid:
    """Individual bid from a trading agent"""
    agent_id: str
    auction_id: str
    price: float
    quantity: int
    timestamp: datetime
    strategy: BidStrategy
    confidence: float = 1.0
    max_price: Optional[float] = None  # Maximum willing to pay
    is_winning: bool = False
    bid_id: str = field(default_factory=lambda: str(random.randint(100000, 999999)))

@dataclass
class AuctionResult:
    """Result of completed auction"""
    auction_id: str
    winning_bids: List[Bid]
    clearing_price: float
    total_quantity: int
    participants: int
    duration: timedelta
    revenue: float
    efficiency: float  # Market efficiency metric

@dataclass
class AgentProfile:
    """Trading agent profile and capabilities"""
    agent_id: str
    strategy_type: BidStrategy
    risk_tolerance: float  # 0-1 scale
    capital_allocation: float
    performance_history: List[float] = field(default_factory=list)
    success_rate: float = 0.0
    average_profit: float = 0.0
    trust_score: float = 1.0  # For collusion detection

class CompetitiveBiddingEngine:
    """
    Advanced competitive bidding engine for multi-agent trading
    
    This system manages complex auction mechanisms where multiple
    trading agents compete for execution priority and optimal pricing
    in dynamic market conditions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.active_auctions: Dict[str, Dict] = {}
        self.bid_history: Dict[str, List[Bid]] = defaultdict(list)
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.auction_results: Dict[str, AuctionResult] = {}
        
        # Market state tracking
        self.market_regime = MarketRegime.NORMAL
        self.volatility_index = 0.0
        self.liquidity_score = 1.0
        
        # Collusion detection
        self.suspicious_patterns = defaultdict(list)
        self.trust_threshold = 0.7
        
        # Performance metrics
        self.metrics = {
            'total_auctions': 0,
            'successful_auctions': 0,
            'total_volume': 0,
            'average_efficiency': 0.0,
            'collusion_detections': 0
        }
        
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default trading agents for testing"""
        default_agents = [
            ("mm_01", BidStrategy.CONSERVATIVE, 0.3, 1000000),
            ("arb_01", BidStrategy.TRUTHFUL, 0.5, 1500000),
            ("mom_01", BidStrategy.AGGRESSIVE, 0.7, 800000),
            ("mr_01", BidStrategy.SHADING, 0.4, 1200000),
            ("hf_01", BidStrategy.SNIPING, 0.8, 2000000)
        ]
        
        for agent_id, strategy, risk, capital in default_agents:
            self.register_agent(agent_id, strategy, risk, capital)
    
    def register_agent(self, agent_id: str, strategy: BidStrategy, 
                      risk_tolerance: float, capital_allocation: float) -> None:
        """Register a new trading agent"""
        profile = AgentProfile(
            agent_id=agent_id,
            strategy_type=strategy,
            risk_tolerance=risk_tolerance,
            capital_allocation=capital_allocation
        )
        self.agent_profiles[agent_id] = profile
        logger.info(f"Agent registered: {agent_id} with strategy {strategy.value}")
    
    def create_auction(self, symbol: str, quantity: int, 
                      auction_type: AuctionType = AuctionType.DOUBLE_AUCTION,
                      duration: int = 30) -> str:
        """Create a new auction for trading"""
        auction_id = f"auction_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        auction_config = {
            'symbol': symbol,
            'quantity': quantity,
            'auction_type': auction_type,
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(seconds=duration),
            'duration': duration,
            'status': 'active',
            'bids': [],
            'reserve_price': self._calculate_reserve_price(symbol, quantity),
            'min_bid_increment': self._calculate_bid_increment(symbol)
        }
        
        self.active_auctions[auction_id] = auction_config
        self.metrics['total_auctions'] += 1
        
        logger.info(f"Created auction {auction_id} for {quantity} {symbol}")
        
        # Start auction countdown
        asyncio.create_task(self._run_auction_timer(auction_id, duration))
        
        return auction_id
    
    def _calculate_reserve_price(self, symbol: str, quantity: int) -> float:
        """Calculate reserve price based on market conditions"""
        # In production, this would use real market data
        base_price = 100.0  # Placeholder
        market_impact = quantity * 0.0001  # Simple linear impact model
        
        # Adjust for market regime
        regime_multiplier = {
            MarketRegime.NORMAL: 1.0,
            MarketRegime.VOLATILE: 1.1,
            MarketRegime.ILLIQUID: 1.2,
            MarketRegime.CRISIS: 1.3,
            MarketRegime.AUCTION: 1.0
        }[self.market_regime]
        
        return base_price * regime_multiplier - market_impact
    
    def _calculate_bid_increment(self, symbol: str) -> float:
        """Calculate minimum bid increment"""
        # Based on symbol price and volatility
        base_increment = 0.01  # $0.01 minimum
        volatility_adjustment = self.volatility_index * 0.1
        
        return max(base_increment, base_increment * (1 + volatility_adjustment))
    
    async def _run_auction_timer(self, auction_id: str, duration: int) -> None:
        """Run auction timer and close auction when time expires"""
        await asyncio.sleep(duration)
        await self.close_auction(auction_id)
    
    def submit_bid(self, auction_id: str, agent_id: str, price: float, 
                  quantity: int, strategy: BidStrategy = None) -> Bid:
        """Submit a bid to an active auction"""
        if auction_id not in self.active_auctions:
            raise ValueError(f"Auction {auction_id} not found or expired")
        
        auction = self.active_auctions[auction_id]
        
        if datetime.now() > auction['end_time']:
            raise ValueError("Auction has already ended")
        
        # Get agent profile for strategy
        agent_profile = self.agent_profiles.get(agent_id)
        if not agent_profile:
            raise ValueError(f"Agent {agent_id} not registered")
        
        # Use agent's default strategy if not specified
        if strategy is None:
            strategy = agent_profile.strategy_type
        
        # Apply strategy-specific bid adjustments
        adjusted_price = self._apply_bid_strategy(price, quantity, strategy, agent_profile)
        
        # Create bid object
        bid = Bid(
            agent_id=agent_id,
            auction_id=auction_id,
            price=adjusted_price,
            quantity=quantity,
            timestamp=datetime.now(),
            strategy=strategy,
            confidence=agent_profile.risk_tolerance,
            max_price=price  # Original intended price
        )
        
        # Add bid to auction
        auction['bids'].append(bid)
        self.bid_history[auction_id].append(bid)
        
        # Update winning bids
        self._update_winning_bids(auction_id)
        
        # Check for suspicious patterns
        self._check_collusion_patterns(auction_id, bid)
        
        logger.info(f"Bid submitted: {agent_id} @ ${adjusted_price:.2f} for {quantity} shares")
        
        return bid
    
    def _apply_bid_strategy(self, intended_price: float, quantity: int,
                          strategy: BidStrategy, profile: AgentProfile) -> float:
        """Apply bidding strategy to adjust intended price"""
        base_price = intended_price
        
        if strategy == BidStrategy.TRUTHFUL:
            return base_price  # No adjustment
        
        elif strategy == BidStrategy.AGGRESSIVE:
            # Overbid by risk tolerance percentage
            aggression_factor = 1.0 + (profile.risk_tolerance * 0.1)
            return base_price * aggression_factor
        
        elif strategy == BidStrategy.CONSERVATIVE:
            # Underbid for safety margin
            conservatism_factor = 1.0 - (profile.risk_tolerance * 0.05)
            return base_price * conservatism_factor
        
        elif strategy == BidStrategy.SNIPING:
            # Bid at last moment (price adjustment handled in timing)
            return base_price
        
        elif strategy == BidStrategy.SHADING:
            # Strategic underbidding in expectation of second-price
            shading_factor = 1.0 - (0.1 * profile.risk_tolerance)
            return base_price * shading_factor
        
        elif strategy == BidStrategy.COLLUSIVE:
            # Coordinated bidding (detected and penalized)
            logger.warning(f"Collusive bidding detected from agent {profile.agent_id}")
            return base_price * 0.95  # Slight undercut for coordination
        
        else:
            return base_price
    
    def _update_winning_bids(self, auction_id: str) -> None:
        """Update which bids are currently winning"""
        auction = self.active_auctions[auction_id]
        bids = auction['bids']
        
        # Sort bids by price (descending for buyers, ascending for sellers)
        # For double auction, we need to match buy and sell bids
        if auction['auction_type'] == AuctionType.DOUBLE_AUCTION:
            self._match_double_auction_bids(auction_id)
        else:
            # For single-sided auctions, simply sort by price
            bids.sort(key=lambda x: x.price, reverse=True)
            
            # Mark top bids as winning based on quantity
            total_filled = 0
            for bid in bids:
                if total_filled < auction['quantity']:
                    bid.is_winning = True
                    total_filled += bid.quantity
                else:
                    bid.is_winning = False
    
    def _match_double_auction_bids(self, auction_id: str) -> None:
        """Match buy and sell bids in double auction"""
        auction = self.active_auctions[auction_id]
        bids = auction['bids']
        
        # Separate buy and sell bids
        buy_bids = [b for b in bids if b.price > 0]  # Positive for buys
        sell_bids = [b for b in bids if b.price < 0]  # Negative for sells (absolute value)
        
        # Sort buys descending, sells ascending (by absolute value)
        buy_bids.sort(key=lambda x: x.price, reverse=True)
        sell_bids.sort(key=lambda x: abs(x.price))
        
        # Match bids to find clearing price
        clearing_price = self._find_clearing_price(buy_bids, sell_bids)
        
        # Mark winning bids
        for bid in bids:
            if (bid.price >= clearing_price and bid.price > 0) or \
               (abs(bid.price) <= clearing_price and bid.price < 0):
                bid.is_winning = True
            else:
                bid.is_winning = False
    
    def _find_clearing_price(self, buy_bids: List[Bid], sell_bids: List[Bid]) -> float:
        """Find market clearing price for double auction"""
        if not buy_bids or not sell_bids:
            return 0.0
        
        # Simple implementation - weighted average of best bid and ask
        best_bid = buy_bids[0].price if buy_bids else 0
        best_ask = abs(sell_bids[0].price) if sell_bids else float('inf')
        
        if best_bid >= best_ask:
            # Market can clear
            return (best_bid + best_ask) / 2
        else:
            # No clearing possible at current bids
            return 0.0
    
    def _check_collusion_patterns(self, auction_id: str, new_bid: Bid) -> None:
        """Check for suspicious bidding patterns indicating collusion"""
        auction_bids = self.bid_history[auction_id]
        
        if len(auction_bids) < 3:
            return  # Need more data for pattern detection
        
        # Check for bid rotation (agents taking turns winning)
        recent_winners = [b.agent_id for b in auction_bids[-10:] if b.is_winning]
        if len(recent_winners) >= 3:
            unique_winners = set(recent_winners)
            if len(unique_winners) == 1:
                # Single agent winning consistently - potential dominance, not necessarily collusion
                pass
            elif len(unique_winners) == 2:
                # Two agents alternating - potential collusion
                self._flag_collusion_suspicion(auction_id, list(unique_winners))
        
        # Check for complementary bidding (one agent always bids just below another)
        agent_bids = defaultdict(list)
        for bid in auction_bids:
            agent_bids[bid.agent_id].append(bid.price)
        
        # Analyze bidding correlations between agents
        self._analyze_bid_correlations(agent_bids, auction_id)
    
    def _flag_collusion_suspicion(self, auction_id: str, agent_ids: List[str]) -> None:
        """Flag potential collusion between agents"""
        for agent_id in agent_ids:
            self.suspicious_patterns[agent_id].append({
                'auction_id': auction_id,
                'timestamp': datetime.now(),
                'pattern': 'bid_rotation',
                'colluders': agent_ids
            })
            
            # Reduce trust score
            if agent_id in self.agent_profiles:
                self.agent_profiles[agent_id].trust_score *= 0.9
                
                if self.agent_profiles[agent_id].trust_score < self.trust_threshold:
                    logger.warning(f"Agent {agent_id} trust score below threshold: "
                                 f"{self.agent_profiles[agent_id].trust_score:.3f}")
                    self.metrics['collusion_detections'] += 1
    
    def _analyze_bid_correlations(self, agent_bids: Dict[str, List[float]], 
                                auction_id: str) -> None:
        """Analyze correlations between agent bidding patterns"""
        agents = list(agent_bids.keys())
        
        if len(agents) < 2:
            return
        
        # Calculate bid price correlations
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                agent1, agent2 = agents[i], agents[j]
                bids1 = agent_bids[agent1]
                bids2 = agent_bids[agent2]
                
                # Ensure we have enough data points
                min_bids = min(len(bids1), len(bids2))
                if min_bids < 3:
                    continue
                
                # Calculate correlation (simplified)
                correlation = self._calculate_bid_correlation(bids1[:min_bids], bids2[:min_bids])
                
                if abs(correlation) > 0.8:  # High correlation threshold
                    self.suspicious_patterns[agent1].append({
                        'auction_id': auction_id,
                        'timestamp': datetime.now(),
                        'pattern': 'high_correlation',
                        'correlated_agent': agent2,
                        'correlation': correlation
                    })
    
    def _calculate_bid_correlation(self, bids1: List[float], bids2: List[float]) -> float:
        """Calculate correlation between two bid sequences"""
        if len(bids1) != len(bids2) or len(bids1) < 2:
            return 0.0
        
        # Simple correlation calculation
        mean1 = sum(bids1) / len(bids1)
        mean2 = sum(bids2) / len(bids2)
        
        numerator = sum((b1 - mean1) * (b2 - mean2) for b1, b2 in zip(bids1, bids2))
        denominator1 = sum((b1 - mean1) ** 2 for b1 in bids1)
        denominator2 = sum((b2 - mean2) ** 2 for b2 in bids2)
        
        if denominator1 == 0 or denominator2 == 0:
            return 0.0
        
        return numerator / (denominator1 * denominator2) ** 0.5
    
    async def close_auction(self, auction_id: str) -> AuctionResult:
        """Close auction and determine results"""
        if auction_id not in self.active_auctions:
            raise ValueError(f"Auction {auction_id} not found")
        
        auction = self.active_auctions[auction_id]
        auction['status'] = 'closed'
        auction['end_time'] = datetime.now()
        
        # Determine winning bids and clearing price
        winning_bids = [b for b in auction['bids'] if b.is_winning]
        clearing_price = self._calculate_clearing_price(winning_bids)
        total_quantity = sum(b.quantity for b in winning_bids)
        
        # Calculate auction metrics
        duration = auction['end_time'] - auction['start_time']
        revenue = clearing_price * total_quantity
        efficiency = self._calculate_auction_efficiency(auction['bids'], winning_bids)
        
        # Create result object
        result = AuctionResult(
            auction_id=auction_id,
            winning_bids=winning_bids,
            clearing_price=clearing_price,
            total_quantity=total_quantity,
            participants=len(set(b.agent_id for b in auction['bids'])),
            duration=duration,
            revenue=revenue,
            efficiency=efficiency
        )
        
        self.auction_results[auction_id] = result
        self.metrics['successful_auctions'] += 1
        self.metrics['total_volume'] += total_quantity
        self.metrics['average_efficiency'] = (
            (self.metrics['average_efficiency'] * (self.metrics['successful_auctions'] - 1) + efficiency) 
            / self.metrics['successful_auctions']
        )
        
        # Update agent performance
        self._update_agent_performance(winning_bids, result)
        
        # Remove from active auctions
        del self.active_auctions[auction_id]
        
        logger.info(f"Auction {auction_id} closed: {len(winning_bids)} winning bids, "
                   f"clearing price ${clearing_price:.2f}, efficiency {efficiency:.3f}")
        
        return result
    
    def _calculate_clearing_price(self, winning_bids: List[Bid]) -> float:
        """Calculate market clearing price from winning bids"""
        if not winning_bids:
            return 0.0
        
        # Weighted average of winning bid prices
        total_value = sum(b.price * b.quantity for b in winning_bids)
        total_quantity = sum(b.quantity for b in winning_bids)
        
        return total_value / total_quantity if total_quantity > 0 else 0.0
    
    def _calculate_auction_efficiency(self, all_bids: List[Bid], winning_bids: List[Bid]) -> float:
        """Calculate auction efficiency metric"""
        if not all_bids:
            return 0.0
        
        # Simple efficiency: ratio of total bid value to winning bid value
        total_bid_value = sum(b.price * b.quantity for b in all_bids)
        winning_bid_value = sum(b.price * b.quantity for b in winning_bids)
        
        if total_bid_value == 0:
            return 0.0
        
        return winning_bid_value / total_bid_value
    
    def _update_agent_performance(self, winning_bids: List[Bid], result: AuctionResult) -> None:
        """Update agent performance metrics based on auction results"""
        for bid in winning_bids:
            if bid.agent_id in self.agent_profiles:
                profile = self.agent_profiles[bid.agent_id]
                
                # Calculate profit (simplified)
                profit = (result.clearing_price - bid.max_price) * bid.quantity if bid.max_price else 0
                profile.average_profit = (
                    (profile.average_profit * len(profile.performance_history) + profit)
                    / (len(profile.performance_history) + 1)
                )
                
                profile.performance_history.append(profit)
                profile.success_rate = len([p for p in profile.performance_history if p > 0]) / len(profile.performance_history)
    
    def get_auction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive auction statistics"""
        return {
            **self.metrics,
            'active_auctions': len(self.active_auctions),
            'total_agents': len(self.agent_profiles),
            'market_regime': self.market_regime.value,
            'average_trust_score': np.mean([p.trust_score for p in self.agent_profiles.values()]),
            'suspicious_agents': len([p for p in self.agent_profiles.values() 
                                    if p.trust_score < self.trust_threshold])
        }
    
    def get_agent_rankings(self) -> List[Dict[str, Any]]:
        """Get agent performance rankings"""
        rankings = []
        for agent_id, profile in self.agent_profiles.items():
            rankings.append({
                'agent_id': agent_id,
                'strategy': profile.strategy_type.value,
                'success_rate': profile.success_rate,
                'average_profit': profile.average_profit,
                'trust_score': profile.trust_score,
                'total_capital': profile.capital_allocation
            })
        
        return sorted(rankings, key=lambda x: x['average_profit'], reverse=True)

# Example usage and testing
async def main():
    """Example usage of the Competitive Bidding Engine"""
    engine = CompetitiveBiddingEngine()
    
    # Create an auction
    auction_id = engine.create_auction(
        symbol="AAPL",
        quantity=10000,
        auction_type=AuctionType.DOUBLE_AUCTION,
        duration=10  # 10 second auction
    )
    
    # Simulate agents submitting bids
    agents = list(engine.agent_profiles.keys())
    
    for i in range(20):
        agent_id = random.choice(agents)
        price = 100 + random.uniform(-5, 5)  # Random price around $100
        quantity = random.randint(100, 2000)
        
        try:
            engine.submit_bid(auction_id, agent_id, price, quantity)
            await asyncio.sleep(0.5)  # Simulate time between bids
        except ValueError as e:
            print(f"Bid failed: {e}")
    
    # Wait for auction to complete
    await asyncio.sleep(11)
    
    # Get results
    if auction_id in engine.auction_results:
        result = engine.auction_results[auction_id]
        print(f"\nAuction Results for {auction_id}:")
        print(f"Clearing Price: ${result.clearing_price:.2f}")
        print(f"Total Quantity: {result.total_quantity}")
        print(f"Efficiency: {result.efficiency:.3f}")
        print(f"Participants: {result.participants}")
        print(f"Winning Bids: {len(result.winning_bids)}")
    
    # Print statistics
    stats = engine.get_auction_statistics()
    print(f"\nEngine Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Print agent rankings
    rankings = engine.get_agent_rankings()
    print(f"\nAgent Rankings:")
    for i, rank in enumerate(rankings[:5], 1):
        print(f"  {i}. {rank['agent_id']}: ${rank['average_profit']:.2f} "
              f"(Success: {rank['success_rate']:.1%})")

if __name__ == "__main__":
    asyncio.run(main())