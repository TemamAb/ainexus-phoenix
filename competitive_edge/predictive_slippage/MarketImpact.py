"""
Advanced Market Impact Model
Quantifies and predicts market impact of trades across venues
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class ImpactModel(Enum):
    SQUARE_ROOT = "square_root"
    LINEAR = "linear"
    POWER_LAW = "power_law"
    ALMGREN_CHRISS = "almgren_chriss"

@dataclass
class TradeImpact:
    timestamp: datetime
    asset_pair: str
    trade_size: float
    immediate_impact: float
    permanent_impact: float
    total_impact: float
    model_used: ImpactModel
    confidence: float
    execution_advice: str

@dataclass
class VenueLiquidity:
    venue: str
    asset_pair: str
    bid_depth: float
    ask_depth: float
    spread: float
    fee_structure: Dict
    impact_coefficient: float

class MarketImpactCalculator:
    """
    Advanced market impact calculation using multiple models
    and venue-specific liquidity characteristics
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.venue_liquidity = {}
        self.impact_models = {}
        self.trade_history = []
        
        self._initialize_models()
        self._load_venue_characteristics()
    
    def _setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _initialize_models(self):
        """Initialize different market impact models"""
        self.impact_models = {
            ImpactModel.SQUARE_ROOT: self._square_root_impact,
            ImpactModel.LINEAR: self._linear_impact,
            ImpactModel.POWER_LAW: self._power_law_impact,
            ImpactModel.ALMGREN_CHRISS: self._almgren_chriss_impact
        }
    
    def _load_venue_characteristics(self):
        """Load venue-specific liquidity characteristics"""
        # In production, this would be loaded from a database or API
        self.venue_liquidity = {
            'binance': VenueLiquidity(
                venue='binance',
                asset_pair='ETH-USDT',
                bid_depth=500000,
                ask_depth=450000,
                spread=0.0002,
                fee_structure={'maker': -0.0001, 'taker': 0.0004},
                impact_coefficient=0.15
            ),
            'uniswap_v3': VenueLiquidity(
                venue='uniswap_v3',
                asset_pair='ETH-USDT',
                bid_depth=200000,
                ask_depth=180000,
                spread=0.0005,
                fee_structure={'fee_tier': 0.003},
                impact_coefficient=0.25
            ),
            'kraken': VenueLiquidity(
                venue='kraken',
                asset_pair='ETH-USDT',
                bid_depth=300000,
                ask_depth=280000,
                spread=0.0003,
                fee_structure={'maker': -0.0002, 'taker': 0.0005},
                impact_coefficient=0.18
            )
        }
    
    def calculate_impact(self, asset_pair: str, trade_size: float,
                        venue: str = 'binance', 
                        model: ImpactModel = ImpactModel.SQUARE_ROOT,
                        urgency: float = 0.5) -> TradeImpact:
        """
        Calculate market impact for a proposed trade
        
        Args:
            asset_pair: Trading pair
            trade_size: Size of trade in base asset
            venue: Trading venue
            model: Impact model to use
            urgency: Trade urgency (0-1, where 1 is most urgent)
            
        Returns:
            TradeImpact object with impact calculations
        """
        if venue not in self.venue_liquidity:
            raise ValueError(f"Unsupported venue: {venue}")
        
        venue_data = self.venue_liquidity[venue]
        
        # Get impact calculation function
        impact_func = self.impact_models.get(model)
        if not impact_func:
            raise ValueError(f"Unsupported impact model: {model}")
        
        # Calculate impacts
        immediate_impact, permanent_impact = impact_func(
            trade_size, venue_data, urgency
        )
        
        total_impact = immediate_impact + permanent_impact
        
        # Determine execution advice
        execution_advice = self._get_execution_advice(
            total_impact, trade_size, venue_data
        )
        
        # Calculate confidence based on model and data quality
        confidence = self._calculate_confidence(model, venue_data)
        
        impact_result = TradeImpact(
            timestamp=datetime.now(),
            asset_pair=asset_pair,
            trade_size=trade_size,
            immediate_impact=immediate_impact,
            permanent_impact=permanent_impact,
            total_impact=total_impact,
            model_used=model,
            confidence=confidence,
            execution_advice=execution_advice
        )
        
        # Store in history
        self.trade_history.append(impact_result)
        
        self.logger.info(
            f"Impact for {trade_size} {asset_pair} on {venue}: "
            f"{total_impact:.4f}% (Confidence: {confidence:.2f})"
        )
        
        return impact_result
    
    def _square_root_impact(self, trade_size: float, 
                          venue_data: VenueLiquidity,
                          urgency: float) -> Tuple[float, float]:
        """Square root market impact model"""
        # k * sqrt(Q/V) * sigma
        k = venue_data.impact_coefficient
        volume = venue_data.ask_depth  # Use ask depth for buy orders
        
        if volume <= 0:
            return 0.0, 0.0
        
        normalized_size = trade_size / volume
        impact = k * np.sqrt(normalized_size) * (1 + urgency * 0.5)
        
        # Split into immediate (60%) and permanent (40%) impact
        immediate = impact * 0.6
        permanent = impact * 0.4
        
        return immediate, permanent
    
    def _linear_impact(self, trade_size: float,
                     venue_data: VenueLiquidity,
                     urgency: float) -> Tuple[float, float]:
        """Linear market impact model"""
        k = venue_data.impact_coefficient * 2  # Different coefficient for linear
        volume = venue_data.ask_depth
        
        if volume <= 0:
            return 0.0, 0.0
        
        normalized_size = trade_size / volume
        impact = k * normalized_size * (1 + urgency)
        
        immediate = impact * 0.7
        permanent = impact * 0.3
        
        return immediate, permanent
    
    def _power_law_impact(self, trade_size: float,
                        venue_data: VenueLiquidity,
                        urgency: float) -> Tuple[float, float]:
        """Power law market impact model"""
        k = venue_data.impact_coefficient
        volume = venue_data.ask_depth
        alpha = 0.6  # Power law exponent
        
        if volume <= 0:
            return 0.0, 0.0
        
        normalized_size = trade_size / volume
        impact = k * (normalized_size ** alpha) * (1 + urgency * 0.3)
        
        immediate = impact * 0.65
        permanent = impact * 0.35
        
        return immediate, permanent
    
    def _almgren_chriss_impact(self, trade_size: float,
                             venue_data: VenueLiquidity,
                             urgency: float) -> Tuple[float, float]:
        """Almgren-Chriss optimal execution model"""
        # Simplified implementation
        # In production, this would solve the full AC model
        volatility = 0.02  # Placeholder for asset volatility
        liquidity = venue_data.ask_depth
        temporary_impact = 0.1  # Temporary impact parameter
        permanent_impact = 0.05  # Permanent impact parameter
        
        if liquidity <= 0:
            return 0.0, 0.0
        
        # Simplified AC impact calculation
        eta = temporary_impact / (liquidity ** 0.5)
        gamma = permanent_impact / liquidity
        
        # Execution time based on urgency
        T = max(1, int(10 * (1 - urgency)))  # Execution horizon in minutes
        
        # AC impact formula (simplified)
        immediate_impact = gamma * trade_size + eta * (trade_size / T)
        permanent_impact = gamma * trade_size
        
        return immediate_impact, permanent_impact
    
    def _get_execution_advice(self, total_impact: float,
                            trade_size: float,
                            venue_data: VenueLiquidity) -> str:
        """Get execution advice based on impact analysis"""
        normalized_impact = total_impact / (venue_data.spread * 1000)
        
        if normalized_impact < 1:
            return "IMMEDIATE_EXECUTION"
        elif normalized_impact < 3:
            return "SLICE_AND_STRATEGY"
        elif normalized_impact < 5:
            return "VWAP_EXECUTION"
        else:
            return "DARK_POOL_OR_DELAY"
    
    def _calculate_confidence(self, model: ImpactModel,
                            venue_data: VenueLiquidity) -> float:
        """Calculate confidence score for impact prediction"""
        # Base confidence on model sophistication and data quality
        model_confidence = {
            ImpactModel.SQUARE_ROOT: 0.7,
            ImpactModel.LINEAR: 0.6,
            ImpactModel.POWER_LAW: 0.75,
            ImpactModel.ALMGREN_CHRISS: 0.85
        }
        
        # Adjust for venue data quality (simplified)
        data_quality = min(1.0, venue_data.ask_depth / 1000000)
        
        return model_confidence.get(model, 0.5) * data_quality
    
    def optimize_trade_schedule(self, asset_pair: str, total_size: float,
                              venue: str = 'binance',
                              time_horizon: int = 60,
                              risk_aversion: float = 0.5) -> Dict:
        """
        Optimize trade execution schedule using Almgren-Chriss model
        
        Args:
            asset_pair: Trading pair
            total_size: Total trade size
            venue: Trading venue
            time_horizon: Execution horizon in minutes
            risk_aversion: Risk aversion parameter (0-1)
            
        Returns:
            Optimized trade schedule
        """
        venue_data = self.venue_liquidity[venue]
        
        # Model parameters
        volatility = 0.02  # Daily volatility
        temporary_impact = 0.001  # Temporary impact parameter
        permanent_impact = 0.0005  # Permanent impact parameter
        
        # Almgren-Chriss optimization
        def cost_function(trade_sizes):
            """Cost function to minimize (implementation cost + risk)"""
            if len(trade_sizes) != time_horizon:
                return float('inf')
            
            # Implementation shortfall
            impact_cost = 0
            position = 0
            
            for size in trade_sizes:
                position += size
                impact_cost += permanent_impact * size * position
                impact_cost += temporary_impact * (size ** 2)
            
            # Risk cost
            risk_cost = risk_aversion * volatility * sum(
                [pos ** 2 for pos in cumulative_positions]
            )
            
            return impact_cost + risk_cost
        
        # Initial guess (linear execution)
        initial_schedule = [total_size / time_horizon] * time_horizon
        
        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda x: sum(x) - total_size}  # Must execute full size
        )
        
        # Bounds (no negative trades)
        bounds = [(0, total_size)] * time_horizon
        
        # Optimization
        result = minimize(
            cost_function,
            initial_schedule,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_schedule = result.x
            expected_cost = result.fun
            
            schedule = {
                'total_size': total_size,
                'time_horizon': time_horizon,
                'schedule': optimal_schedule.tolist(),
                'expected_cost': expected_cost,
                'cost_savings': self._calculate_cost_savings(
                    initial_schedule, optimal_schedule, venue_data
                )
            }
            
            self.logger.info(
                f"Optimized schedule: {expected_cost:.6f} cost "
                f"({schedule['cost_savings']:.2f}% savings)"
            )
            
            return schedule
        else:
            self.logger.warning("Schedule optimization failed, using linear schedule")
            return {
                'total_size': total_size,
                'time_horizon': time_horizon,
                'schedule': initial_schedule,
                'expected_cost': cost_function(initial_schedule),
                'cost_savings': 0.0,
                'optimization_failed': True
            }
    
    def _calculate_cost_savings(self, initial_schedule: List[float],
                              optimal_schedule: List[float],
                              venue_data: VenueLiquidity) -> float:
        """Calculate cost savings from optimized schedule"""
        # Simplified cost calculation
        def schedule_cost(schedule):
            cost = 0
            for size in schedule:
                impact = self._square_root_impact(size, venue_data, 0.5)[0]
                cost += impact
            return cost
        
        initial_cost = schedule_cost(initial_schedule)
        optimal_cost = schedule_cost(optimal_schedule)
        
        if initial_cost > 0:
            return (initial_cost - optimal_cost) / initial_cost * 100
        else:
            return 0.0
    
    def compare_venues(self, asset_pair: str, trade_size: float) -> Dict[str, TradeImpact]:
        """
        Compare market impact across different venues
        
        Args:
            asset_pair: Trading pair
            trade_size: Trade size to compare
            
        Returns:
            Dictionary of venue -> TradeImpact
        """
        venue_impacts = {}
        
        for venue, venue_data in self.venue_liquidity.items():
            if venue_data.asset_pair == asset_pair:
                impact = self.calculate_impact(
                    asset_pair, trade_size, venue, ImpactModel.SQUARE_ROOT
                )
                venue_impacts[venue] = impact
        
        # Sort by total impact (lowest first)
        sorted_impacts = dict(sorted(
            venue_impacts.items(),
            key=lambda x: x[1].total_impact
        ))
        
        return sorted_impacts
    
    def get_impact_statistics(self, lookback_days: int = 30) -> Dict:
        """
        Calculate impact statistics from trade history
        
        Args:
            lookback_days: Number of days to look back
            
        Returns:
            Impact statistics
        """
        cutoff_time = datetime.now() - timedelta(days=lookback_days)
        recent_trades = [
            trade for trade in self.trade_history 
            if trade.timestamp >= cutoff_time
        ]
        
        if not recent_trades:
            return {}
        
        total_impacts = [trade.total_impact for trade in recent_trades]
        sizes = [trade.trade_size for trade in recent_trades]
        
        return {
            'total_trades': len(recent_trades),
            'average_impact': np.mean(total_impacts),
            'median_impact': np.median(total_impacts),
            'max_impact': np.max(total_impacts),
            'min_impact': np.min(total_impacts),
            'impact_std': np.std(total_impacts),
            'average_trade_size': np.mean(sizes),
            'impact_size_correlation': np.corrcoef(sizes, total_impacts)[0, 1]
        }

# Example usage
def main():
    """Demo the market impact calculator"""
    calculator = MarketImpactCalculator()
    
    print("📊 Market Impact Analysis Engine")
    print("=" * 50)
    
    # Calculate impact for a sample trade
    trade_size = 1000  # ETH
    impact = calculator.calculate_impact(
        'ETH-USDT', trade_size, 'binance', ImpactModel.SQUARE_ROOT
    )
    
    print(f"Trade: {trade_size} ETH on Binance")
    print(f"Immediate Impact: {impact.immediate_impact:.4f}%")
    print(f"Permanent Impact: {impact.permanent_impact:.4f}%")
    print(f"Total Impact: {impact.total_impact:.4f}%")
    print(f"Execution Advice: {impact.execution_advice}")
    print(f"Confidence: {impact.confidence:.2f}")
    
    print("\n" + "=" * 50)
    
    # Compare venues
    print("Venue Comparison for 1000 ETH:")
    venue_comparison = calculator.compare_venues('ETH-USDT', 1000)
    
    for venue, venue_impact in venue_comparison.items():
        print(f"{venue:12}: {venue_impact.total_impact:.4f}% impact")
    
    print("\n" + "=" * 50)
    
    # Optimize trade schedule
    print("Optimizing Trade Schedule for 5000 ETH:")
    schedule = calculator.optimize_trade_schedule(
        'ETH-USDT', 5000, 'binance', time_horizon=30
    )
    
    print(f"Expected Cost: {schedule['expected_cost']:.6f}")
    print(f"Cost Savings: {schedule['cost_savings']:.2f}%")
    print(f"Schedule: {[f'{x:.1f}' for x in schedule['schedule'][:5]]}...")
    
    print("\n" + "=" * 50)
    
    # Impact statistics
    stats = calculator.get_impact_statistics()
    print("Impact Statistics:")
    for key, value in stats.items():
        print(f"{key:25}: {value}")

if __name__ == "__main__":
    main()