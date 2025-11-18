"""
AI-NEXUS v5.0 - CAPITAL VELOCITY MODULE
Advanced Capital Movement and Utilization Tracking
Real-time capital efficiency monitoring and optimization
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

class VelocityMetric(Enum):
    TURNOVER_RATE = "turnover_rate"
    UTILIZATION_RATE = "utilization_rate"
    IDLE_TIME_RATIO = "idle_time_ratio"
    RETURN_VELOCITY = "return_velocity"
    CROSS_PROTOCOL_FLOW = "cross_protocol_flow"
    CAPITAL_EFFICIENCY = "capital_efficiency"

class MovementType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    ARBITRAGE = "arbitrage"
    LIQUIDITY_PROVISION = "liquidity_provision"
    LOAN = "loan"

@dataclass
class CapitalMovement:
    movement_id: str
    timestamp: datetime
    amount: float
    source: str
    destination: str
    movement_type: MovementType
    asset: str
    protocol: str
    fees: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class VelocitySnapshot:
    snapshot_id: str
    timestamp: datetime
    total_capital: float
    deployed_capital: float
    available_capital: float
    velocity_metrics: Dict[VelocityMetric, float]
    utilization_by_protocol: Dict[str, float]
    movement_statistics: Dict[str, float]
    efficiency_score: float

@dataclass
class EfficiencyRecommendation:
    recommendation_id: str
    priority: str  # "HIGH", "MEDIUM", "LOW"
    category: str
    description: str
    expected_impact: float
    implementation_complexity: int
    metadata: Dict[str, Any]

class CapitalVelocityTracker:
    """
    Advanced capital velocity and efficiency tracking system
    Monitors capital movement patterns and optimization opportunities
    """
    
    def __init__(self, lookback_period: timedelta = timedelta(days=30)):
        self.lookback_period = lookback_period
        self.capital_movements = deque(maxlen=10000)  # Store recent movements
        self.velocity_snapshots = deque(maxlen=1000)   # Store historical snapshots
        self.capital_allocations = {}  # Current capital allocations by protocol
        
        # Performance tracking
        self.performance_metrics = {
            'total_movements': 0,
            'total_capital_flow': 0.0,
            'avg_velocity': 0.0,
            'peak_utilization': 0.0,
            'efficiency_trend': deque(maxlen=100)
        }
        
        # Velocity calculation parameters
        self.velocity_params = {
            'turnover_window': timedelta(hours=24),
            'utilization_window': timedelta(hours=1),
            'efficiency_threshold': 0.7,
            'idle_time_threshold': 0.3
        }
        
        # Protocol efficiency benchmarks
        self.protocol_benchmarks = {
            'uniswap_v3': {'target_utilization': 0.8, 'min_turnover': 2.0},
            'aave': {'target_utilization': 0.9, 'min_turnover': 1.5},
            'compound': {'target_utilization': 0.85, 'min_turnover': 1.2},
            'curve': {'target_utilization': 0.75, 'min_turnover': 3.0}
        }
    
    def record_capital_movement(self, movement: CapitalMovement):
        """Record a capital movement event"""
        
        self.capital_movements.append(movement)
        self.performance_metrics['total_movements'] += 1
        self.performance_metrics['total_capital_flow'] += movement.amount
        
        # Update capital allocations
        self._update_capital_allocations(movement)
        
        print(f"Recorded movement: {movement.movement_type.value} of {movement.amount} {movement.asset} "
              f"from {movement.source} to {movement.destination}")
    
    def _update_capital_allocations(self, movement: CapitalMovement):
        """Update current capital allocations based on movement"""
        
        asset = movement.asset
        protocol = movement.protocol
        
        if asset not in self.capital_allocations:
            self.capital_allocations[asset] = {}
        
        if protocol not in self.capital_allocations[asset]:
            self.capital_allocations[asset][protocol] = 0.0
        
        # Update allocation based on movement type
        if movement.movement_type in [MovementType.DEPOSIT, MovementType.ARBITRAGE, MovementType.LIQUIDITY_PROVISION]:
            self.capital_allocations[asset][protocol] += movement.amount
        elif movement.movement_type in [MovementType.WITHDRAWAL, MovementType.TRANSFER]:
            self.capital_allocations[asset][protocol] -= movement.amount
        
        # Ensure non-negative allocations
        self.capital_allocations[asset][protocol] = max(0.0, self.capital_allocations[asset][protocol])
    
    def calculate_velocity_metrics(self) -> VelocitySnapshot:
        """Calculate comprehensive velocity metrics"""
        
        current_time = datetime.now()
        snapshot_id = f"VEL_{current_time.strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate total capital
        total_capital = self._calculate_total_capital()
        deployed_capital = self._calculate_deployed_capital()
        available_capital = total_capital - deployed_capital
        
        # Calculate velocity metrics
        velocity_metrics = {
            VelocityMetric.TURNOVER_RATE: self._calculate_turnover_rate(current_time),
            VelocityMetric.UTILIZATION_RATE: self._calculate_utilization_rate(total_capital, deployed_capital),
            VelocityMetric.IDLE_TIME_RATIO: self._calculate_idle_time_ratio(current_time),
            VelocityMetric.RETURN_VELOCITY: self._calculate_return_velocity(current_time),
            VelocityMetric.CROSS_PROTOCOL_FLOW: self._calculate_cross_protocol_flow(current_time),
            VelocityMetric.CAPITAL_EFFICIENCY: self._calculate_capital_efficiency(total_capital, deployed_capital)
        }
        
        # Calculate utilization by protocol
        utilization_by_protocol = self._calculate_utilization_by_protocol(total_capital)
        
        # Calculate movement statistics
        movement_statistics = self._calculate_movement_statistics(current_time)
        
        # Calculate overall efficiency score
        efficiency_score = self._calculate_efficiency_score(velocity_metrics, utilization_by_protocol)
        
        # Create snapshot
        snapshot = VelocitySnapshot(
            snapshot_id=snapshot_id,
            timestamp=current_time,
            total_capital=total_capital,
            deployed_capital=deployed_capital,
            available_capital=available_capital,
            velocity_metrics=velocity_metrics,
            utilization_by_protocol=utilization_by_protocol,
            movement_statistics=movement_statistics,
            efficiency_score=efficiency_score
        )
        
        self.velocity_snapshots.append(snapshot)
        self.performance_metrics['efficiency_trend'].append(efficiency_score)
        self.performance_metrics['avg_velocity'] = np.mean(list(self.performance_metrics['efficiency_trend']))
        self.performance_metrics['peak_utilization'] = max(
            self.performance_metrics['peak_utilization'],
            velocity_metrics[VelocityMetric.UTILIZATION_RATE]
        )
        
        return snapshot
    
    def _calculate_total_capital(self) -> float:
        """Calculate total available capital across all assets and protocols"""
        
        total = 0.0
        for asset, protocol_allocations in self.capital_allocations.items():
            for protocol, amount in protocol_allocations.items():
                total += amount
        
        # Add recent inflows that might not be allocated yet
        recent_movements = self._get_recent_movements(timedelta(hours=1))
        recent_inflows = sum(
            m.amount for m in recent_movements 
            if m.movement_type in [MovementType.DEPOSIT, MovementType.ARBITRAGE]
        )
        
        return total + recent_inflows
    
    def _calculate_deployed_capital(self) -> float:
        """Calculate currently deployed capital"""
        
        deployed = 0.0
        for asset, protocol_allocations in self.capital_allocations.items():
            for protocol, amount in protocol_allocations.items():
                deployed += amount
        
        return deployed
    
    def _calculate_turnover_rate(self, current_time: datetime) -> float:
        """Calculate capital turnover rate (how frequently capital is reused)"""
        
        window = self.velocity_params['turnover_window']
        recent_movements = self._get_recent_movements(window)
        
        if not recent_movements:
            return 0.0
        
        total_turnover = sum(m.amount for m in recent_movements)
        avg_deployed_capital = self._calculate_average_deployed_capital(window)
        
        if avg_deployed_capital > 0:
            turnover_rate = total_turnover / avg_deployed_capital
        else:
            turnover_rate = 0.0
        
        return turnover_rate
    
    def _calculate_utilization_rate(self, total_capital: float, deployed_capital: float) -> float:
        """Calculate capital utilization rate"""
        
        if total_capital > 0:
            utilization_rate = deployed_capital / total_capital
        else:
            utilization_rate = 0.0
        
        return utilization_rate
    
    def _calculate_idle_time_ratio(self, current_time: datetime) -> float:
        """Calculate ratio of time capital is idle"""
        
        window = timedelta(hours=24)  # Look at last 24 hours
        movement_timestamps = [m.timestamp for m in self.capital_movements 
                              if current_time - m.timestamp <= window]
        
        if not movement_timestamps:
            return 1.0  # All time idle if no movements
        
        # Sort timestamps and calculate gaps
        sorted_timestamps = sorted(movement_timestamps)
        total_idle_time = 0.0
        
        # Calculate gaps between movements
        for i in range(1, len(sorted_timestamps)):
            gap = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds()
            total_idle_time += gap
        
        # Add time from first movement to window start and last movement to current time
        window_start = current_time - window
        if sorted_timestamps:
            total_idle_time += (sorted_timestamps[0] - window_start).total_seconds()
            total_idle_time += (current_time - sorted_timestamps[-1]).total_seconds()
        else:
            total_idle_time = window.total_seconds()
        
        total_window_seconds = window.total_seconds()
        idle_time_ratio = total_idle_time / total_window_seconds
        
        return idle_time_ratio
    
    def _calculate_return_velocity(self, current_time: datetime) -> float:
        """Calculate velocity of returns generation"""
        
        window = timedelta(hours=24)
        recent_movements = self._get_recent_movements(window)
        
        profitable_movements = [
            m for m in recent_movements 
            if m.movement_type == MovementType.ARBITRAGE and 
            m.metadata and m.metadata.get('realized_profit', 0) > 0
        ]
        
        if not profitable_movements:
            return 0.0
        
        total_profit = sum(m.metadata.get('realized_profit', 0) for m in profitable_movements)
        avg_deployed_capital = self._calculate_average_deployed_capital(window)
        
        if avg_deployed_capital > 0:
            return_velocity = total_profit / avg_deployed_capital
        else:
            return_velocity = 0.0
        
        return return_velocity
    
    def _calculate_cross_protocol_flow(self, current_time: datetime) -> float:
        """Calculate cross-protocol capital movement"""
        
        window = timedelta(hours=6)  # Shorter window for protocol flow
        recent_movements = self._get_recent_movements(window)
        
        cross_protocol_movements = [
            m for m in recent_movements 
            if m.movement_type == MovementType.TRANSFER and m.source != m.destination
        ]
        
        if not recent_movements:
            return 0.0
        
        cross_protocol_flow = sum(m.amount for m in cross_protocol_movements)
        total_flow = sum(m.amount for m in recent_movements)
        
        if total_flow > 0:
            cross_protocol_ratio = cross_protocol_flow / total_flow
        else:
            cross_protocol_ratio = 0.0
        
        return cross_protocol_ratio
    
    def _calculate_capital_efficiency(self, total_capital: float, deployed_capital: float) -> float:
        """Calculate overall capital efficiency score"""
        
        # Get recent velocity metrics
        turnover_rate = self._calculate_turnover_rate(datetime.now())
        utilization_rate = self._calculate_utilization_rate(total_capital, deployed_capital)
        return_velocity = self._calculate_return_velocity(datetime.now())
        
        # Calculate efficiency components
        turnover_efficiency = min(1.0, turnover_rate / 5.0)  # Target 5x turnover
        utilization_efficiency = utilization_rate
        return_efficiency = min(1.0, return_velocity / 0.1)  # Target 10% return velocity
        
        # Weighted combination
        efficiency_score = (
            turnover_efficiency * 0.3 +
            utilization_efficiency * 0.4 +
            return_efficiency * 0.3
        )
        
        return efficiency_score
    
    def _calculate_utilization_by_protocol(self, total_capital: float) -> Dict[str, float]:
        """Calculate utilization rate for each protocol"""
        
        utilization_by_protocol = {}
        
        for asset, protocol_allocations in self.capital_allocations.items():
            for protocol, amount in protocol_allocations.items():
                if total_capital > 0:
                    utilization = amount / total_capital
                else:
                    utilization = 0.0
                
                utilization_by_protocol[protocol] = utilization_by_protocol.get(protocol, 0.0) + utilization
        
        return utilization_by_protocol
    
    def _calculate_movement_statistics(self, current_time: datetime) -> Dict[str, float]:
        """Calculate movement statistics"""
        
        window = timedelta(hours=24)
        recent_movements = self._get_recent_movements(window)
        
        if not recent_movements:
            return {}
        
        movement_amounts = [m.amount for m in recent_movements]
        movement_types = [m.movement_type for m in recent_movements]
        
        type_counts = defaultdict(int)
        for movement_type in movement_types:
            type_counts[movement_type] += 1
        
        return {
            'total_movements': len(recent_movements),
            'total_volume': sum(movement_amounts),
            'avg_movement_size': np.mean(movement_amounts),
            'movement_frequency': len(recent_movements) / (window.total_seconds() / 3600),  # movements per hour
            'arbitrage_ratio': type_counts[MovementType.ARBITRAGE] / len(recent_movements) 
                              if recent_movements else 0.0
        }
    
    def _calculate_efficiency_score(self, 
                                 velocity_metrics: Dict[VelocityMetric, float],
                                 utilization_by_protocol: Dict[str, float]) -> float:
        """Calculate overall efficiency score"""
        
        # Base efficiency from velocity metrics
        base_efficiency = (
            velocity_metrics[VelocityMetric.TURNOVER_RATE] * 0.25 +
            velocity_metrics[VelocityMetric.UTILIZATION_RATE] * 0.30 +
            velocity_metrics[VelocityMetric.RETURN_VELOCITY] * 0.25 +
            velocity_metrics[VelocityMetric.CROSS_PROTOCOL_FLOW] * 0.20
        )
        
        # Protocol efficiency adjustment
        protocol_efficiency = self._calculate_protocol_efficiency(utilization_by_protocol)
        
        # Combined efficiency score
        efficiency_score = base_efficiency * 0.7 + protocol_efficiency * 0.3
        
        return efficiency_score
    
    def _calculate_protocol_efficiency(self, utilization_by_protocol: Dict[str, float]) -> float:
        """Calculate protocol-specific efficiency"""
        
        if not utilization_by_protocol:
            return 0.5  # Neutral efficiency
        
        total_utilization = sum(utilization_by_protocol.values())
        if total_utilization == 0:
            return 0.5
        
        protocol_scores = []
        
        for protocol, utilization in utilization_by_protocol.items():
            if protocol in self.protocol_benchmarks:
                benchmark = self.protocol_benchmarks[protocol]
                target_utilization = benchmark['target_utilization']
                min_turnover = benchmark['min_turnover']
                
                # Score based on utilization vs target
                utilization_score = 1.0 - abs(utilization - target_utilization) / target_utilization
                
                # Simple protocol score (would be more sophisticated in practice)
                protocol_score = utilization_score
                protocol_scores.append(protocol_score)
            else:
                # Default score for unknown protocols
                protocol_scores.append(0.7)
        
        # Weighted average by utilization
        weighted_score = 0.0
        for protocol, utilization in utilization_by_protocol.items():
            if protocol in self.protocol_benchmarks:
                benchmark = self.protocol_benchmarks[protocol]
                utilization_weight = utilization / total_utilization
                protocol_index = list(utilization_by_protocol.keys()).index(protocol)
                weighted_score += protocol_scores[protocol_index] * utilization_weight
        
        return weighted_score
    
    def _get_recent_movements(self, time_window: timedelta) -> List[CapitalMovement]:
        """Get movements within specified time window"""
        
        cutoff_time = datetime.now() - time_window
        return [m for m in self.capital_movements if m.timestamp >= cutoff_time]
    
    def _calculate_average_deployed_capital(self, window: timedelta) -> float:
        """Calculate average deployed capital over time window"""
        
        # Simplified implementation - would use historical snapshots in production
        recent_snapshots = [
            s for s in self.velocity_snapshots 
            if datetime.now() - s.timestamp <= window
        ]
        
        if recent_snapshots:
            avg_deployed = np.mean([s.deployed_capital for s in recent_snapshots])
        else:
            # Fallback to current deployed capital
            avg_deployed = self._calculate_deployed_capital()
        
        return avg_deployed
    
    def generate_efficiency_recommendations(self) -> List[EfficiencyRecommendation]:
        """Generate capital efficiency optimization recommendations"""
        
        recommendations = []
        
        # Get current velocity metrics
        current_snapshot = self.calculate_velocity_metrics()
        velocity_metrics = current_snapshot.velocity_metrics
        
        # Check for low utilization
        utilization = velocity_metrics[VelocityMetric.UTILIZATION_RATE]
        if utilization < self.velocity_params['efficiency_threshold']:
            recommendations.append(
                EfficiencyRecommendation(
                    recommendation_id=f"REC_UTIL_{datetime.now().strftime('%H%M%S')}",
                    priority="HIGH" if utilization < 0.5 else "MEDIUM",
                    category="capital_allocation",
                    description=f"Low capital utilization ({utilization:.1%}). Consider deploying idle capital to productive protocols.",
                    expected_impact=0.1,  # 10% potential improvement
                    implementation_complexity=2,
                    metadata={'current_utilization': utilization, 'target_utilization': self.velocity_params['efficiency_threshold']}
                )
            )
        
        # Check for high idle time
        idle_ratio = velocity_metrics[VelocityMetric.IDLE_TIME_RATIO]
        if idle_ratio > self.velocity_params['idle_time_threshold']:
            recommendations.append(
                EfficiencyRecommendation(
                    recommendation_id=f"REC_IDLE_{datetime.now().strftime('%H%M%S')}",
                    priority="MEDIUM",
                    category="movement_frequency",
                    description=f"High capital idle time ({idle_ratio:.1%}). Increase trading frequency or explore additional strategies.",
                    expected_impact=0.08,
                    implementation_complexity=3,
                    metadata={'idle_ratio': idle_ratio, 'threshold': self.velocity_params['idle_time_threshold']}
                )
            )
        
        # Check for low cross-protocol flow
        cross_protocol_flow = velocity_metrics[VelocityMetric.CROSS_PROTOCOL_FLOW]
        if cross_protocol_flow < 0.2:  # Less than 20% cross-protocol movement
            recommendations.append(
                EfficiencyRecommendation(
                    recommendation_id=f"REC_FLOW_{datetime.now().strftime('%H%M%S')}",
                    priority="LOW",
                    category="protocol_diversification",
                    description=f"Low cross-protocol capital flow ({cross_protocol_flow:.1%}). Consider diversifying across more protocols.",
                    expected_impact=0.05,
                    implementation_complexity=2,
                    metadata={'cross_protocol_flow': cross_protocol_flow}
                )
            )
        
        # Check protocol-specific optimizations
        for protocol, utilization in current_snapshot.utilization_by_protocol.items():
            if protocol in self.protocol_benchmarks:
                benchmark = self.protocol_benchmarks[protocol]
                target_utilization = benchmark['target_utilization']
                
                if abs(utilization - target_utilization) > 0.1:  # More than 10% deviation
                    action = "increase" if utilization < target_utilization else "decrease"
                    recommendations.append(
                        EfficiencyRecommendation(
                            recommendation_id=f"REC_{protocol}_{datetime.now().strftime('%H%M%S')}",
                            priority="MEDIUM",
                            category="protocol_optimization",
                            description=f"Optimize {protocol} allocation: {action} from {utilization:.1%} to target {target_utilization:.1%}.",
                            expected_impact=0.03,
                            implementation_complexity=1,
                            metadata={
                                'protocol': protocol,
                                'current_utilization': utilization,
                                'target_utilization': target_utilization,
                                'action': action
                            }
                        )
                    )
        
        return recommendations
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        current_snapshot = self.calculate_velocity_metrics()
        
        return {
            'total_capital': current_snapshot.total_capital,
            'deployed_capital': current_snapshot.deployed_capital,
            'available_capital': current_snapshot.available_capital,
            'efficiency_score': current_snapshot.efficiency_score,
            'velocity_metrics': {k.value: v for k, v in current_snapshot.velocity_metrics.items()},
            'utilization_by_protocol': current_snapshot.utilization_by_protocol,
            'movement_statistics': current_snapshot.movement_statistics,
            'performance_trend': {
                'avg_efficiency': self.performance_metrics['avg_velocity'],
                'peak_utilization': self.performance_metrics['peak_utilization'],
                'total_movements': self.performance_metrics['total_movements'],
                'total_capital_flow': self.performance_metrics['total_capital_flow']
            }
        }

# Example usage
def main():
    velocity_tracker = CapitalVelocityTracker()
    
    # Record sample capital movements
    sample_movements = [
        CapitalMovement(
            movement_id="MOV_001",
            timestamp=datetime.now() - timedelta(hours=2),
            amount=50000,
            source="wallet",
            destination="uniswap_v3",
            movement_type=MovementType.DEPOSIT,
            asset="USDC",
            protocol="uniswap_v3"
        ),
        CapitalMovement(
            movement_id="MOV_002", 
            timestamp=datetime.now() - timedelta(hours=1),
            amount=10000,
            source="uniswap_v3",
            destination="sushiswap",
            movement_type=MovementType.ARBITRAGE,
            asset="USDC",
            protocol="cross_dex",
            metadata={'realized_profit': 150}
        ),
        CapitalMovement(
            movement_id="MOV_003",
            timestamp=datetime.now() - timedelta(minutes=30),
            amount=20000,
            source="wallet", 
            destination="aave",
            movement_type=MovementType.LIQUIDITY_PROVISION,
            asset="USDC",
            protocol="aave"
        )
    ]
    
    for movement in sample_movements:
        velocity_tracker.record_capital_movement(movement)
    
    # Calculate velocity metrics
    snapshot = velocity_tracker.calculate_velocity_metrics()
    
    print("Capital Velocity Snapshot:")
    print(f"Total Capital: ${snapshot.total_capital:,.2f}")
    print(f"Deployed Capital: ${snapshot.deployed_capital:,.2f}")
    print(f"Efficiency Score: {snapshot.efficiency_score:.3f}")
    
    print("\nVelocity Metrics:")
    for metric, value in snapshot.velocity_metrics.items():
        print(f"- {metric.value}: {value:.3f}")
    
    # Generate recommendations
    recommendations = velocity_tracker.generate_efficiency_recommendations()
    
    print(f"\nEfficiency Recommendations ({len(recommendations)}):")
    for rec in recommendations:
        print(f"- [{rec.priority}] {rec.description}")
    
    # Get performance summary
    summary = velocity_tracker.get_performance_summary()
    print(f"\nPerformance Summary: {summary}")

if __name__ == "__main__":
    main()
