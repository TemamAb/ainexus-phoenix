"""
AI-NEXUS STRATEGY BENCHMARK
Comprehensive strategy performance evaluation and comparison
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

@dataclass
class StrategyMetrics:
    strategy_id: str
    total_profit: float
    total_volume: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    avg_trade_duration: float
    success_rate: float
    risk_adjusted_return: float

@dataclass
class BenchmarkResult:
    timestamp: datetime
    strategy_comparison: Dict[str, StrategyMetrics]
    top_performers: List[str]
    underperformers: List[str]
    market_conditions: Dict
    recommendations: List[str]

class StrategyBenchmark:
    def __init__(self, config):
        self.config = config
        self.strategy_data = {}
        self.benchmark_history = []
        self.market_regimes = {}
        self.logger = logging.getLogger(__name__)
        
    async def run_comprehensive_benchmark(self, strategy_performance_data: Dict, 
                                        market_data: Dict) -> BenchmarkResult:
        """Run comprehensive strategy benchmarking"""
        strategy_metrics = {}
        
        for strategy_id, performance in strategy_performance_data.items():
            metrics = await self.calculate_strategy_metrics(strategy_id, performance, market_data)
            strategy_metrics[strategy_id] = metrics
        
        # Rank strategies by performance
        ranked_strategies = self.rank_strategies(strategy_metrics)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(strategy_metrics, market_data)
        
        benchmark_result = BenchmarkResult(
            timestamp=datetime.now(),
            strategy_comparison=strategy_metrics,
            top_performers=ranked_strategies[:3],
            underperformers=ranked_strategies[-2:],
            market_conditions=market_data,
            recommendations=recommendations
        )
        
        self.benchmark_history.append(benchmark_result)
        self.strategy_data.update(strategy_performance_data)
        
        return benchmark_result
    
    async def calculate_strategy_metrics(self, strategy_id: str, performance: Dict, 
                                       market_data: Dict) -> StrategyMetrics:
        """Calculate comprehensive performance metrics for a strategy"""
        trades = performance.get('trades', [])
        if not trades:
            return self._create_empty_metrics(strategy_id)
        
        # Basic metrics
        total_profit = sum(trade.get('profit', 0) for trade in trades)
        total_volume = sum(abs(trade.get('volume', 0)) for trade in trades)
        
        # Win rate
        winning_trades = [t for t in trades if t.get('profit', 0) > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        # Profit factor
        gross_profit = sum(t.get('profit', 0) for t in winning_trades)
        losing_trades = [t for t in trades if t.get('profit', 0) < 0]
        gross_loss = abs(sum(t.get('profit', 0) for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Risk-adjusted metrics
        returns = [t.get('profit', 0) for t in trades]
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        max_drawdown = self.calculate_max_drawdown(returns)
        
        # Calmar ratio (return to max drawdown)
        avg_return = np.mean(returns) if returns else 0
        calmar_ratio = avg_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Trade duration
        durations = []
        for trade in trades:
            if 'start_time' in trade and 'end_time' in trade:
                start = datetime.fromisoformat(trade['start_time'])
                end = datetime.fromisoformat(trade['end_time'])
                duration = (end - start).total_seconds()
                durations.append(duration)
        avg_duration = np.mean(durations) if durations else 0
        
        # Success rate (profitable after costs)
        success_rate = self.calculate_success_rate(trades)
        
        # Risk-adjusted return
        risk_adjusted_return = self.calculate_risk_adjusted_return(returns, market_data)
        
        return StrategyMetrics(
            strategy_id=strategy_id,
            total_profit=total_profit,
            total_volume=total_volume,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            avg_trade_duration=avg_duration,
            success_rate=success_rate,
            risk_adjusted_return=risk_adjusted_return
        )
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio for strategy returns"""
        if not returns or len(returns) < 2:
            return 0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 365)  # Daily risk-free rate
        return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0
    
    def calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns series"""
        if not returns:
            return 0
        
        cumulative = np.cumsum(returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / (peak + 1e-8)  # Avoid division by zero
        return np.max(drawdown) if len(drawdown) > 0 else 0
    
    def calculate_success_rate(self, trades: List[Dict]) -> float:
        """Calculate success rate considering transaction costs"""
        successful_trades = 0
        
        for trade in trades:
            profit = trade.get('profit', 0)
            costs = trade.get('gas_cost', 0) + trade.get('slippage', 0)
            net_profit = profit - costs
            
            if net_profit > 0:
                successful_trades += 1
        
        return successful_trades / len(trades) if trades else 0
    
    def calculate_risk_adjusted_return(self, returns: List[float], market_data: Dict) -> float:
        """Calculate risk-adjusted return considering market conditions"""
        if not returns:
            return 0
        
        market_volatility = market_data.get('volatility', 0.1)
        strategy_volatility = np.std(returns) if len(returns) > 1 else 0
        
        if strategy_volatility == 0:
            return 0
        
        # Adjust return based on market risk
        market_adjustment = 1 - (strategy_volatility / market_volatility)
        avg_return = np.mean(returns)
        
        return avg_return * max(0.1, market_adjustment)
    
    def rank_strategies(self, strategy_metrics: Dict[str, StrategyMetrics]) -> List[str]:
        """Rank strategies by composite performance score"""
        scores = {}
        
        for strategy_id, metrics in strategy_metrics.items():
            score = self.calculate_composite_score(metrics)
            scores[strategy_id] = score
        
        # Sort by score (descending)
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    
    def calculate_composite_score(self, metrics: StrategyMetrics) -> float:
        """Calculate composite performance score"""
        weights = {
            'profit_factor': 0.25,
            'sharpe_ratio': 0.20,
            'win_rate': 0.15,
            'success_rate': 0.15,
            'calmar_ratio': 0.15,
            'risk_adjusted_return': 0.10
        }
        
        # Normalize metrics to 0-1 scale
        normalized_metrics = {
            'profit_factor': min(metrics.profit_factor / 5, 1.0),  # Cap at 5
            'sharpe_ratio': min(max(metrics.sharpe_ratio, 0) / 3, 1.0),  # Cap at 3
            'win_rate': metrics.win_rate,
            'success_rate': metrics.success_rate,
            'calmar_ratio': min(max(metrics.calmar_ratio, 0) / 2, 1.0),  # Cap at 2
            'risk_adjusted_return': min(max(metrics.risk_adjusted_return, 0) / 0.1, 1.0)  # Cap at 10%
        }
        
        composite_score = 0
        for metric, weight in weights.items():
            composite_score += normalized_metrics[metric] * weight
        
        return composite_score
    
    def generate_recommendations(self, strategy_metrics: Dict[str, StrategyMetrics], 
                               market_data: Dict) -> List[str]:
        """Generate strategy optimization recommendations"""
        recommendations = []
        
        for strategy_id, metrics in strategy_metrics.items():
            # Profitability recommendations
            if metrics.profit_factor < 1.0:
                recommendations.append(
                    f"Strategy {strategy_id}: Improve profit factor (current: {metrics.profit_factor:.2f})"
                )
            
            # Risk management recommendations
            if metrics.max_drawdown > 0.1:  # 10% drawdown
                recommendations.append(
                    f"Strategy {strategy_id}: Reduce max drawdown (current: {metrics.max_drawdown:.1%})"
                )
            
            # Efficiency recommendations
            if metrics.avg_trade_duration > 300:  # 5 minutes
                recommendations.append(
                    f"Strategy {strategy_id}: Optimize trade duration (current: {metrics.avg_trade_duration:.1f}s)"
                )
            
            # Success rate recommendations
            if metrics.success_rate < 0.6:  # 60% success rate
                recommendations.append(
                    f"Strategy {strategy_id}: Improve success rate (current: {metrics.success_rate:.1%})"
                )
        
        # Market condition recommendations
        market_volatility = market_data.get('volatility', 0)
        if market_volatility > 0.15:  # High volatility
            recommendations.append("Market: High volatility detected - consider reducing position sizes")
        
        if market_data.get('trend', 'neutral') == 'bearish':
            recommendations.append("Market: Bearish trend - focus on short-term strategies")
        
        return recommendations
    
    async def run_ab_testing(self, strategy_a: Dict, strategy_b: Dict, 
                           duration_days: int = 7) -> Dict:
        """Run A/B testing between two strategies"""
        start_time = datetime.now()
        end_time = start_time + timedelta(days=duration_days)
        
        a_results = []
        b_results = []
        
        # Simulate A/B testing (in production, this would run actual strategies)
        current_time = start_time
        while current_time < end_time:
            a_performance = await self.simulate_strategy_performance(strategy_a, current_time)
            b_performance = await self.simulate_strategy_performance(strategy_b, current_time)
            
            a_results.append(a_performance)
            b_results.append(b_performance)
            
            current_time += timedelta(hours=1)  # Hourly evaluation
        
        # Statistical significance testing
        significance = self.calculate_statistical_significance(a_results, b_results)
        
        return {
            'strategy_a_metrics': await self.calculate_strategy_metrics('A', {'trades': a_results}, {}),
            'strategy_b_metrics': await self.calculate_strategy_metrics('B', {'trades': b_results}, {}),
            'statistical_significance': significance,
            'winner': 'A' if significance['a_better'] else 'B' if significance['b_better'] else 'Tie',
            'confidence': significance['confidence'],
            'test_duration': duration_days
        }
    
    async def simulate_strategy_performance(self, strategy: Dict, timestamp: datetime) -> Dict:
        """Simulate strategy performance for testing"""
        # Simplified simulation - in production, this would use actual strategy execution
        base_profit = np.random.normal(0.001, 0.005)  # Small random profit/loss
        gas_cost = 0.0001  # Fixed gas cost
        slippage = abs(base_profit) * 0.01  # 1% slippage
        
        net_profit = base_profit - gas_cost - slippage
        
        return {
            'profit': net_profit,
            'volume': abs(base_profit) * 1000,  # Simulated volume
            'gas_cost': gas_cost,
            'slippage': slippage,
            'start_time': timestamp.isoformat(),
            'end_time': (timestamp + timedelta(minutes=5)).isoformat()
        }
    
    def calculate_statistical_significance(self, results_a: List, results_b: List) -> Dict:
        """Calculate statistical significance between two result sets"""
        if len(results_a) < 10 or len(results_b) < 10:
            return {'significant': False, 'confidence': 0, 'a_better': False, 'b_better': False}
        
        profits_a = [r.get('profit', 0) for r in results_a]
        profits_b = [r.get('profit', 0) for r in results_b]
        
        # T-test for means
        t_stat, p_value = stats.ttest_ind(profits_a, profits_b)
        
        # Calculate confidence
        confidence = 1 - p_value
        
        # Determine which is better
        mean_a = np.mean(profits_a)
        mean_b = np.mean(profits_b)
        
        return {
            'significant': p_value < 0.05,  # 95% confidence level
            'confidence': confidence,
            'a_better': mean_a > mean_b and p_value < 0.05,
            'b_better': mean_b > mean_a and p_value < 0.05,
            'p_value': p_value,
            'mean_difference': mean_a - mean_b
        }
    
    def get_benchmark_history(self, lookback_days: int = 30) -> pd.DataFrame:
        """Get benchmark history as DataFrame"""
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        recent_benchmarks = [
            b for b in self.benchmark_history 
            if b.timestamp > cutoff_date
        ]
        
        if not recent_benchmarks:
            return pd.DataFrame()
        
        # Convert to DataFrame for analysis
        data = []
        for benchmark in recent_benchmarks:
            for strategy_id, metrics in benchmark.strategy_comparison.items():
                data.append({
                    'timestamp': benchmark.timestamp,
                    'strategy_id': strategy_id,
                    'total_profit': metrics.total_profit,
                    'win_rate': metrics.win_rate,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'max_drawdown': metrics.max_drawdown,
                    'composite_score': self.calculate_composite_score(metrics)
                })
        
        return pd.DataFrame(data)
    
    def identify_performance_trends(self) -> Dict:
        """Identify performance trends across strategies"""
        df = self.get_benchmark_history()
        if df.empty:
            return {}
        
        trends = {}
        
        for strategy_id in df['strategy_id'].unique():
            strategy_data = df[df['strategy_id'] == strategy_id]
            
            if len(strategy_data) > 1:
                # Calculate trend for composite score
                scores = strategy_data['composite_score'].values
                time_index = np.arange(len(scores))
                
                # Linear regression for trend
                slope, intercept, r_value, p_value, std_err = stats.linregress(time_index, scores)
                
                trends[strategy_id] = {
                    'trend': 'improving' if slope > 0.01 else 'declining' if slope < -0.01 else 'stable',
                    'slope': slope,
                    'r_squared': r_value**2,
                    'current_score': scores[-1] if len(scores) > 0 else 0,
                    'volatility': np.std(scores)
                }
        
        return trends
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        latest_benchmark = self.benchmark_history[-1] if self.benchmark_history else None
        trends = self.identify_performance_trends()
        
        if not latest_benchmark:
            return {'error': 'No benchmark data available'}
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'strategies_analyzed': len(latest_benchmark.strategy_comparison),
            'top_performer': latest_benchmark.top_performers[0] if latest_benchmark.top_performers else None,
            'market_conditions': latest_benchmark.market_conditions,
            'key_metrics_summary': self._summarize_key_metrics(latest_benchmark.strategy_comparison),
            'performance_trends': trends,
            'recommendations': latest_benchmark.recommendations,
            'risk_assessment': self._assess_overall_risk(latest_benchmark.strategy_comparison)
        }
        
        return report
    
    def _summarize_key_metrics(self, strategy_metrics: Dict[str, StrategyMetrics]) -> Dict:
        """Summarize key metrics across all strategies"""
        metrics_list = list(strategy_metrics.values())
        
        return {
            'avg_profit_factor': np.mean([m.profit_factor for m in metrics_list]),
            'avg_sharpe_ratio': np.mean([m.sharpe_ratio for m in metrics_list]),
            'avg_win_rate': np.mean([m.win_rate for m in metrics_list]),
            'worst_drawdown': max([m.max_drawdown for m in metrics_list]),
            'best_strategy_score': max([self.calculate_composite_score(m) for m in metrics_list])
        }
    
    def _assess_overall_risk(self, strategy_metrics: Dict[str, StrategyMetrics]) -> Dict:
        """Assess overall risk across strategy portfolio"""
        drawdowns = [metrics.max_drawdown for metrics in strategy_metrics.values()]
        sharpe_ratios = [metrics.sharpe_ratio for metrics in strategy_metrics.values()]
        
        avg_drawdown = np.mean(drawdowns)
        avg_sharpe = np.mean(sharpe_ratios)
        
        if avg_drawdown > 0.15 or avg_sharpe < 0.5:
            risk_level = 'HIGH'
        elif avg_drawdown > 0.08 or avg_sharpe < 1.0:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'avg_drawdown': avg_drawdown,
            'avg_sharpe_ratio': avg_sharpe,
            'diversification_score': self._calculate_diversification_score(strategy_metrics)
        }
    
    def _calculate_diversification_score(self, strategy_metrics: Dict[str, StrategyMetrics]) -> float:
        """Calculate diversification score across strategies"""
        # Simplified diversification calculation
        # In production, this would analyze correlation between strategies
        return 0.8  # Placeholder
    
    def _create_empty_metrics(self, strategy_id: str) -> StrategyMetrics:
        """Create empty metrics for strategies with no data"""
        return StrategyMetrics(
            strategy_id=strategy_id,
            total_profit=0,
            total_volume=0,
            win_rate=0,
            profit_factor=0,
            sharpe_ratio=0,
            max_drawdown=0,
            calmar_ratio=0,
            avg_trade_duration=0,
            success_rate=0,
            risk_adjusted_return=0
        )
