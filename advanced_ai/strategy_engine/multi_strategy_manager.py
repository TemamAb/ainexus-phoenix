# File: advanced_ai/strategy_engine/multi_strategy_manager.py
# 7P-PILLAR: BOT3-7P
# PURPOSE: Multi-strategy orchestration and dynamic management

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
import statistics

class StrategyStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    DISABLED = "disabled"

class StrategyPerformance(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class StrategyConfig:
    name: str
    strategy_id: str
    enabled: bool = True
    max_position_size: float = 10000
    max_daily_loss: float = 1000
    target_apr: float = 0.50  # 50% APR
    risk_level: str = "medium"
    allocation_weight: float = 1.0

@dataclass
class StrategyMetrics:
    strategy_id: str
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    total_trades: int = 0
    successful_trades: int = 0
    total_volume: float = 0.0
    last_trade_time: Optional[float] = None

@dataclass
class StrategyDecision:
    strategy_id: str
    action: str  # "enter", "exit", "hold", "adjust"
    confidence: float
    position_size: float
    reasoning: str
    timestamp: float

class MultiStrategyManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.strategies: Dict[str, StrategyConfig] = {}
        self.strategy_metrics: Dict[str, StrategyMetrics] = {}
        self.strategy_status: Dict[str, StrategyStatus] = {}
        self.active_positions: Dict[str, List[Dict]] = {}
        self.decision_history: List[StrategyDecision] = []
        
        self.performance_thresholds = {
            'min_win_rate': 0.55,
            'max_drawdown': 0.10,
            'min_sharpe': 1.0,
            'max_position_concentration': 0.25
        }
        
        self.setup_strategies()
        self.start_performance_monitoring()

    def setup_strategies(self):
        """Initialize all trading strategies"""
        strategy_configs = [
            StrategyConfig(
                name="Statistical Arbitrage",
                strategy_id="stat_arb_001",
                max_position_size=50000,
                target_apr=0.40,
                risk_level="low"
            ),
            StrategyConfig(
                name="Mean Reversion", 
                strategy_id="mean_rev_001",
                max_position_size=30000,
                target_apr=0.60,
                risk_level="medium"
            ),
            StrategyConfig(
                name="Momentum Trading",
                strategy_id="momentum_001",
                max_position_size=20000,
                target_apr=0.80,
                risk_level="high"
            ),
            StrategyConfig(
                name="Liquidity Provision",
                strategy_id="lp_001",
                max_position_size=75000,
                target_apr=0.25,
                risk_level="low"
            ),
            StrategyConfig(
                name="Cross-Exchange Arbitrage", 
                strategy_id="cross_ex_arb_001",
                max_position_size=25000,
                target_apr=1.20,
                risk_level="medium"
            )
        ]

        for config in strategy_configs:
            self.strategies[config.strategy_id] = config
            self.strategy_metrics[config.strategy_id] = StrategyMetrics(
                strategy_id=config.strategy_id
            )
            self.strategy_status[config.strategy_id] = StrategyStatus.ACTIVE
            self.active_positions[config.strategy_id] = []

        self.logger.info(f"Initialized {len(self.strategies)} trading strategies")

    def start_performance_monitoring(self):
        """Start continuous performance monitoring"""
        self.monitoring_task = asyncio.create_task(self.monitor_strategy_performance())

    async def monitor_strategy_performance(self):
        """Continuously monitor strategy performance"""
        while True:
            try:
                await self.evaluate_all_strategies()
                await self.rebalance_strategy_allocation()
                await self.retire_underperforming_strategies()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Strategy monitoring error: {e}")
                await asyncio.sleep(10)

    async def evaluate_all_strategies(self):
        """Evaluate performance of all strategies"""
        for strategy_id, metrics in self.strategy_metrics.items():
            try:
                performance = await self.evaluate_strategy_performance(strategy_id)
                
                if performance == StrategyPerformance.POOR:
                    await self.handle_poor_performance(strategy_id)
                elif performance == StrategyPerformance.EXCELLENT:
                    await self.handle_excellent_performance(strategy_id)
                    
            except Exception as e:
                self.logger.error(f"Error evaluating strategy {strategy_id}: {e}")

    async def evaluate_strategy_performance(self, strategy_id: str) -> StrategyPerformance:
        """Evaluate individual strategy performance"""
        metrics = self.strategy_metrics[strategy_id]
        config = self.strategies[strategy_id]
        
        if metrics.total_trades < 10:
            return StrategyPerformance.FAIR  # Insufficient data
        
        performance_score = 0
        
        # Win rate evaluation (30% weight)
        win_rate_score = min(1.0, metrics.win_rate / 0.7)  # Normalize to 70% target
        performance_score += win_rate_score * 0.3
        
        # Sharpe ratio evaluation (25% weight) 
        sharpe_score = min(1.0, metrics.sharpe_ratio / 2.0)  # Normalize to 2.0 target
        performance_score += sharpe_score * 0.25
        
        # Drawdown evaluation (20% weight)
        drawdown_score = max(0, 1 - (metrics.max_drawdown / 0.15))  # Normalize to 15% max
        performance_score += drawdown_score * 0.2
        
        # Consistency evaluation (15% weight)
        consistency_score = self.calculate_consistency_score(strategy_id)
        performance_score += consistency_score * 0.15
        
        # Volume efficiency (10% weight)
        volume_score = self.calculate_volume_efficiency(metrics)
        performance_score += volume_score * 0.1
        
        if performance_score >= 0.8:
            return StrategyPerformance.EXCELLENT
        elif performance_score >= 0.6:
            return StrategyPerformance.GOOD  
        elif performance_score >= 0.4:
            return StrategyPerformance.FAIR
        else:
            return StrategyPerformance.POOR

    def calculate_consistency_score(self, strategy_id: str) -> float:
        """Calculate strategy consistency score"""
        # This would analyze PnL consistency over time
        # Simplified implementation
        metrics = self.strategy_metrics[strategy_id]
        if metrics.total_trades < 20:
            return 0.5
            
        # Simulate consistency calculation
        return 0.7 + (hash(strategy_id) % 30) / 100  # 0.7-1.0 range

    def calculate_volume_efficiency(self, metrics: StrategyMetrics) -> float:
        """Calculate volume efficiency score"""
        if metrics.total_volume == 0:
            return 0.0
            
        # PnL per unit of volume
        efficiency = metrics.total_pnl / metrics.total_volume
        return min(1.0, efficiency / 0.1)  # Normalize to 10% efficiency target

    async def handle_poor_performance(self, strategy_id: str):
        """Handle strategies with poor performance"""
        self.logger.warning(f"Strategy {strategy_id} showing poor performance")
        
        # Reduce allocation weight
        config = self.strategies[strategy_id]
        new_weight = max(0.1, config.allocation_weight * 0.7)  # Reduce by 30%
        config.allocation_weight = new_weight
        
        # Consider pausing strategy
        if self.should_pause_strategy(strategy_id):
            await self.pause_strategy(strategy_id, "Poor performance")
            
        self.emit_strategy_alert(strategy_id, "performance_warning", {
            "current_weight": new_weight,
            "reason": "Poor performance detected"
        })

    async def handle_excellent_performance(self, strategy_id: str):
        """Handle strategies with excellent performance"""
        self.logger.info(f"Strategy {strategy_id} showing excellent performance")
        
        # Increase allocation weight (with cap)
        config = self.strategies[strategy_id]
        new_weight = min(2.0, config.allocation_weight * 1.2)  # Increase by 20%
        config.allocation_weight = new_weight
        
        self.emit_strategy_alert(strategy_id, "performance_excellent", {
            "current_weight": new_weight,
            "reason": "Excellent performance rewarded"
        })

    def should_pause_strategy(self, strategy_id: str) -> bool:
        """Determine if strategy should be paused"""
        metrics = self.strategy_metrics[strategy_id]
        
        conditions = [
            metrics.win_rate < self.performance_thresholds['min_win_rate'] * 0.8,
            metrics.max_drawdown > self.performance_thresholds['max_drawdown'] * 1.5, 
            metrics.sharpe_ratio < self.performance_thresholds['min_sharpe'] * 0.5,
            metrics.total_trades > 50 and metrics.total_pnl < 0  # Consistently losing
        ]
        
        return sum(conditions) >= 2  # Pause if 2+ conditions met

    async def pause_strategy(self, strategy_id: str, reason: str):
        """Pause a strategy"""
        self.strategy_status[strategy_id] = StrategyStatus.PAUSED
        self.logger.info(f"Paused strategy {strategy_id}: {reason}")
        
        # Close active positions
        await self.close_strategy_positions(strategy_id)
        
        self.emit_strategy_alert(strategy_id, "strategy_paused", {"reason": reason})

    async def close_strategy_positions(self, strategy_id: str):
        """Close all active positions for a strategy"""
        positions = self.active_positions.get(strategy_id, [])
        
        for position in positions:
            try:
                # In production, this would execute actual close orders
                await self.execute_close_order(position)
                self.logger.info(f"Closed position for strategy {strategy_id}")
            except Exception as e:
                self.logger.error(f"Error closing position for {strategy_id}: {e}")

    async def execute_close_order(self, position: Dict):
        """Execute position close order"""
        # Simulate order execution
        await asyncio.sleep(0.1)
        # In production, this would interact with exchange APIs

    async def rebalance_strategy_allocation(self):
        """Rebalance capital allocation across strategies"""
        total_weight = sum(config.allocation_weight for config in self.strategies.values())
        
        if total_weight == 0:
            return
            
        # Calculate target allocations
        target_allocations = {}
        for strategy_id, config in self.strategies.items():
            if self.strategy_status[strategy_id] == StrategyStatus.ACTIVE:
                target_allocations[strategy_id] = config.allocation_weight / total_weight
        
        # Implement rebalancing logic
        await self.execute_rebalancing(target_allocations)

    async def execute_rebalancing(self, target_allocations: Dict[str, float]):
        """Execute strategy rebalancing"""
        current_allocations = self.calculate_current_allocations()
        
        rebalancing_actions = []
        
        for strategy_id, target_allocation in target_allocations.items():
            current_allocation = current_allocations.get(strategy_id, 0)
            allocation_diff = target_allocation - current_allocation
            
            if abs(allocation_diff) > 0.05:  # 5% threshold
                action = {
                    'strategy_id': strategy_id,
                    'current_allocation': current_allocation,
                    'target_allocation': target_allocation,
                    'adjustment': allocation_diff,
                    'action': 'increase' if allocation_diff > 0 else 'decrease'
                }
                rebalancing_actions.append(action)
        
        if rebalancing_actions:
            self.logger.info(f"Executing {len(rebalancing_actions)} rebalancing actions")
            await self.execute_allocation_adjustments(rebalancing_actions)

    def calculate_current_allocations(self) -> Dict[str, float]:
        """Calculate current capital allocations"""
        # This would use real position data in production
        # Simplified implementation
        total_exposure = sum(
            sum(pos['size'] for pos in positions) 
            for positions in self.active_positions.values()
        )
        
        if total_exposure == 0:
            return {strategy_id: 0 for strategy_id in self.strategies}
            
        allocations = {}
        for strategy_id, positions in self.active_positions.items():
            strategy_exposure = sum(pos['size'] for pos in positions)
            allocations[strategy_id] = strategy_exposure / total_exposure
            
        return allocations

    async def execute_allocation_adjustments(self, adjustments: List[Dict]):
        """Execute capital allocation adjustments"""
        for adjustment in adjustments:
            try:
                strategy_id = adjustment['strategy_id']
                
                if adjustment['action'] == 'increase':
                    await self.increase_strategy_allocation(strategy_id, adjustment['adjustment'])
                else:
                    await self.decrease_strategy_allocation(strategy_id, adjustment['adjustment'])
                    
            except Exception as e:
                self.logger.error(f"Error executing allocation adjustment: {e}")

    async def increase_strategy_allocation(self, strategy_id: str, amount: float):
        """Increase allocation to strategy"""
        self.logger.info(f"Increasing allocation to {strategy_id} by {amount:.2%}")
        # In production, this would allocate more capital to the strategy

    async def decrease_strategy_allocation(self, strategy_id: str, amount: float):
        """Decrease allocation to strategy"""
        self.logger.info(f"Decreasing allocation to {strategy_id} by {amount:.2%}")
        # In production, this would reduce capital allocation

    async def retire_underperforming_strategies(self):
        """Retire consistently underperforming strategies"""
        for strategy_id, metrics in self.strategy_metrics.items():
            if metrics.total_trades < 100:
                continue  # Not enough data
                
            if self.should_retire_strategy(strategy_id):
                await self.retire_strategy(strategy_id)

    def should_retire_strategy(self, strategy_id: str) -> bool:
        """Determine if strategy should be retired"""
        metrics = self.strategy_metrics[strategy_id]
        config = self.strategies[strategy_id]
        
        retirement_conditions = [
            metrics.total_pnl < -config.max_daily_loss * 10,  # 10x daily loss limit
            metrics.win_rate < 0.4,  # Less than 40% win rate
            metrics.sharpe_ratio < 0.5,  # Very poor risk-adjusted returns
            time.time() - (metrics.last_trade_time or 0) > 7 * 24 * 3600  # No trades in 7 days
        ]
        
        return sum(retirement_conditions) >= 2

    async def retire_strategy(self, strategy_id: str):
        """Permanently retire a strategy"""
        self.strategy_status[strategy_id] = StrategyStatus.STOPPED
        self.strategies[strategy_id].enabled = False
        
        # Close all positions
        await self.close_strategy_positions(strategy_id)
        
        self.logger.info(f"Retired strategy {strategy_id} due to consistent underperformance")
        self.emit_strategy_alert(strategy_id, "strategy_retired", {
            "reason": "Consistent underperformance"
        })

    async def make_strategy_decision(self, strategy_id: str, market_data: Dict) -> StrategyDecision:
        """Make trading decision for a strategy"""
        if self.strategy_status[strategy_id] != StrategyStatus.ACTIVE:
            return StrategyDecision(
                strategy_id=strategy_id,
                action="hold",
                confidence=0.0,
                position_size=0.0,
                reasoning="Strategy is not active",
                timestamp=time.time()
            )
        
        try:
            # Get strategy-specific decision
            decision = await self.generate_strategy_decision(strategy_id, market_data)
            
            # Validate decision against risk limits
            validated_decision = await self.validate_decision(decision, strategy_id)
            
            # Record decision
            self.decision_history.append(validated_decision)
            
            return validated_decision
            
        except Exception as e:
            self.logger.error(f"Error making decision for {strategy_id}: {e}")
            return StrategyDecision(
                strategy_id=strategy_id,
                action="hold", 
                confidence=0.0,
                position_size=0.0,
                reasoning=f"Error: {str(e)}",
                timestamp=time.time()
            )

    async def generate_strategy_decision(self, strategy_id: str, market_data: Dict) -> StrategyDecision:
        """Generate strategy-specific trading decision"""
        # This would use actual strategy logic in production
        # Simplified implementation
        
        config = self.strategies[strategy_id]
        metrics = self.strategy_metrics[strategy_id]
        
        # Simulate decision making based on strategy type
        if "arb" in strategy_id:
            return await self.generate_arbitrage_decision(strategy_id, market_data)
        elif "mean_rev" in strategy_id:
            return await self.generate_mean_reversion_decision(strategy_id, market_data)
        elif "momentum" in strategy_id:
            return await self.generate_momentum_decision(strategy_id, market_data)
        else:
            return StrategyDecision(
                strategy_id=strategy_id,
                action="hold",
                confidence=0.5,
                position_size=0.0,
                reasoning="No specific signal detected",
                timestamp=time.time()
            )

    async def generate_arbitrage_decision(self, strategy_id: str, market_data: Dict) -> StrategyDecision:
        """Generate arbitrage strategy decision"""
        # Simplified arbitrage logic
        opportunity_size = 0.02  # 2% arbitrage opportunity
        confidence = 0.8
        
        return StrategyDecision(
            strategy_id=strategy_id,
            action="enter",
            confidence=confidence,
            position_size=self.strategies[strategy_id].max_position_size * 0.5,
            reasoning=f"Arbitrage opportunity detected: {opportunity_size:.2%}",
            timestamp=time.time()
        )

    async def generate_mean_reversion_decision(self, strategy_id: str, market_data: Dict) -> StrategyDecision:
        """Generate mean reversion strategy decision"""
        # Simplified mean reversion logic
        deviation_from_mean = 0.05  # 5% deviation
        confidence = 0.7
        
        return StrategyDecision(
            strategy_id=strategy_id,
            action="enter",
            confidence=confidence, 
            position_size=self.strategies[strategy_id].max_position_size * 0.3,
            reasoning=f"Mean reversion opportunity: {deviation_from_mean:.2%} deviation",
            timestamp=time.time()
        )

    async def generate_momentum_decision(self, strategy_id: str, market_data: Dict) -> StrategyDecision:
        """Generate momentum strategy decision"""
        # Simplified momentum logic
        momentum_strength = 0.08  # 8% momentum
        confidence = 0.6
        
        return StrategyDecision(
            strategy_id=strategy_id,
            action="enter",
            confidence=confidence,
            position_size=self.strategies[strategy_id].max_position_size * 0.4,
            reasoning=f"Momentum signal detected: {momentum_strength:.2%} strength",
            timestamp=time.time()
        )

    async def validate_decision(self, decision: StrategyDecision, strategy_id: str) -> StrategyDecision:
        """Validate trading decision against risk limits"""
        config = self.strategies[strategy_id]
        
        # Check position size limits
        if decision.position_size > config.max_position_size:
            decision.position_size = config.max_position_size
            decision.reasoning += " (position size capped at max limit)"
        
        # Check confidence threshold
        if decision.confidence < 0.6 and decision.action != "hold":
            decision.action = "hold"
            decision.reasoning += " (low confidence)"
            
        # Check daily loss limits
        if await self.would_exceed_daily_loss(strategy_id, decision):
            decision.action = "hold"
            decision.reasoning += " (would exceed daily loss limit)"
            
        return decision

    async def would_exceed_daily_loss(self, strategy_id: str, decision: StrategyDecision) -> bool:
        """Check if decision would exceed daily loss limit"""
        config = self.strategies[strategy_id]
        metrics = self.strategy_metrics[strategy_id]
        
        # Simplified check - in production would use more sophisticated risk modeling
        potential_loss = decision.position_size * 0.1  # Assume 10% potential loss
        return metrics.daily_pnl - potential_loss < -config.max_daily_loss

    def emit_strategy_alert(self, strategy_id: str, alert_type: str, data: Dict):
        """Emit strategy alert"""
        alert = {
            'strategy_id': strategy_id,
            'alert_type': alert_type,
            'timestamp': time.time(),
            'data': data
        }
        
        # In production, this would send to alerting system
        self.logger.info(f"Strategy alert: {alert}")

    def get_strategy_performance_report(self) -> Dict:
        """Generate comprehensive strategy performance report"""
        report = {
            'timestamp': time.time(),
            'total_strategies': len(self.strategies),
            'active_strategies': sum(1 for s in self.strategy_status.values() 
                                   if s == StrategyStatus.ACTIVE),
            'strategy_performance': {},
            'overall_metrics': {
                'total_pnl': 0.0,
                'total_volume': 0.0,
                'average_win_rate': 0.0,
                'weighted_sharpe': 0.0
            }
        }
        
        total_weight = 0
        for strategy_id, metrics in self.strategy_metrics.items():
            config = self.strategies[strategy_id]
            
            report['strategy_performance'][strategy_id] = {
                'name': config.name,
                'status': self.strategy_status[strategy_id].value,
                'allocation_weight': config.allocation_weight,
                'metrics': {
                    'total_pnl': metrics.total_pnl,
                    'daily_pnl': metrics.daily_pnl,
                    'win_rate': metrics.win_rate,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'max_drawdown': metrics.max_drawdown,
                    'total_trades': metrics.total_trades,
                    'total_volume': metrics.total_volume
                },
                'performance_rating': await self.evaluate_strategy_performance(strategy_id).value
            }
            
            # Update overall metrics
            report['overall_metrics']['total_pnl'] += metrics.total_pnl
            report['overall_metrics']['total_volume'] += metrics.total_volume
            report['overall_metrics']['average_win_rate'] += metrics.win_rate
            report['overall_metrics']['weighted_sharpe'] += metrics.sharpe_ratio * config.allocation_weight
            total_weight += config.allocation_weight
        
        # Calculate averages
        active_count = report['active_strategies']
        if active_count > 0:
            report['overall_metrics']['average_win_rate'] /= active_count
        if total_weight > 0:
            report['overall_metrics']['weighted_sharpe'] /= total_weight
            
        return report

    async def update_strategy_metrics(self, strategy_id: str, trade_result: Dict):
        """Update strategy metrics with trade result"""
        metrics = self.strategy_metrics[strategy_id]
        
        metrics.total_trades += 1
        metrics.total_volume += trade_result.get('volume', 0)
        metrics.total_pnl += trade_result.get('pnl', 0)
        metrics.daily_pnl += trade_result.get('pnl', 0)
        metrics.last_trade_time = time.time()
        
        if trade_result.get('success', False):
            metrics.successful_trades += 1
            
        # Update derived metrics
        metrics.win_rate = metrics.successful_trades / metrics.total_trades if metrics.total_trades > 0 else 0
        # Note: Sharpe ratio and max drawdown would require more sophisticated calculation

    async def shutdown(self):
        """Graceful shutdown"""
        if hasattr(self, 'monitoring_task'):
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
                
        # Close all active positions
        for strategy_id in self.strategies:
            await self.close_strategy_positions(strategy_id)

# Example usage
async def main():
    manager = MultiStrategyManager({})
    
    # Simulate some activity
    await asyncio.sleep(2)
    
    # Get performance report
    report = manager.get_strategy_performance_report()
    print("Strategy Performance Report:")
    print(report)
    
    await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
