"""
AI-NEXUS COMPETITIVE ANALYSIS
Real-time competitor monitoring and strategic positioning
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

@dataclass
class CompetitorActivity:
    competitor_id: str
    activity_type: str
    timestamp: datetime
    details: Dict
    impact_score: float

@dataclass
class MarketPosition:
    our_position: str
    competitive_advantage: List[str]
    threats: List[str]
    opportunities: List[str]
    recommendation: str

class CompetitiveAnalysis:
    def __init__(self, config):
        self.config = config
        self.competitor_activities = []
        self.market_data = {}
        self.performance_benchmarks = {}
        self.strategic_insights = []
        self.logger = logging.getLogger(__name__)
        
    async def monitor_competitor_activity(self, market_data: Dict) -> List[CompetitorActivity]:
        """Monitor and analyze competitor activities in real-time"""
        activities = []
        
        # Monitor arbitrage activity
        arb_activities = await self._detect_arbitrage_activity(market_data)
        activities.extend(arb_activities)
        
        # Monitor MEV activity
        mev_activities = await self._detect_mev_activity(market_data)
        activities.extend(mev_activities)
        
        # Monitor strategic moves
        strategic_activities = await self._detect_strategic_moves(market_data)
        activities.extend(strategic_activities)
        
        # Analyze impact and store
        for activity in activities:
            activity.impact_score = await self._calculate_impact_score(activity)
            self.competitor_activities.append(activity)
        
        return activities
    
    async def _detect_arbitrage_activity(self, market_data: Dict) -> List[CompetitorActivity]:
        """Detect arbitrage activities from competitors"""
        activities = []
        
        # Analyze recent transactions for arbitrage patterns
        recent_txs = market_data.get('recent_transactions', [])
        
        for tx in recent_txs[-100:]:  # Last 100 transactions
            if self._is_arbitrage_transaction(tx):
                competitor_id = self._identify_competitor(tx)
                
                activity = CompetitorActivity(
                    competitor_id=competitor_id,
                    activity_type='ARBITRAGE',
                    timestamp=datetime.fromisoformat(tx.get('timestamp', datetime.now().isoformat())),
                    details={
                        'profit_estimated': self._estimate_arbitrage_profit(tx),
                        'strategy_type': self._classify_arbitrage_strategy(tx),
                        'assets_involved': self._extract_assets(tx),
                        'execution_speed': tx.get('execution_time', 0)
                    },
                    impact_score=0
                )
                activities.append(activity)
        
        return activities
    
    async def _detect_mev_activity(self, market_data: Dict) -> List[CompetitorActivity]:
        """Detect MEV activities from competitors"""
        activities = []
        
        # Analyze for sandwich attacks, front-running, etc.
        pending_txs = market_data.get('pending_transactions', [])
        
        for i, tx in enumerate(pending_txs):
            if self._is_mev_transaction(tx, pending_txs, i):
                competitor_id = self._identify_competitor(tx)
                
                activity = CompetitorActivity(
                    competitor_id=competitor_id,
                    activity_type='MEV',
                    timestamp=datetime.now(),
                    details={
                        'mev_type': self._classify_mev_type(tx, pending_txs, i),
                        'estimated_profit': self._estimate_mev_profit(tx, pending_txs, i),
                        'target_victim': self._identify_mev_victim(tx, pending_txs, i)
                    },
                    impact_score=0
                )
                activities.append(activity)
        
        return activities
    
    async def _detect_strategic_moves(self, market_data: Dict) -> List[CompetitorActivity]:
        """Detect strategic moves by competitors"""
        activities = []
        
        # Monitor for large capital movements
        large_transfers = await self._detect_large_capital_movements(market_data)
        activities.extend(large_transfers)
        
        # Monitor for protocol integrations
        new_integrations = await self._detect_new_integrations(market_data)
        activities.extend(new_integrations)
        
        # Monitor for strategy changes
        strategy_changes = await self._detect_strategy_changes(market_data)
        activities.extend(strategy_changes)
        
        return activities
    
    def _is_arbitrage_transaction(self, tx: Dict) -> bool:
        """Check if transaction is an arbitrage opportunity"""
        # Analyze transaction patterns for arbitrage characteristics
        input_data = tx.get('input', '')
        
        # Look for multi-DEX interactions
        dex_interactions = ['uniswap', 'sushiswap', 'pancakeswap', 'curve']
        dex_count = sum(1 for dex in dex_interactions if dex in input_data.lower())
        
        # Check for profit
        value = tx.get('value', 0)
        gas_used = tx.get('gasUsed', 0)
        gas_price = tx.get('gasPrice', 0)
        gas_cost = (gas_used * gas_price) / 1e18
        
        # Simple heuristic: multiple DEX interactions and positive expected value
        return dex_count >= 2 and value > gas_cost * 10
    
    def _is_mev_transaction(self, tx: Dict, pending_txs: List[Dict], index: int) -> bool:
        """Check if transaction is MEV-related"""
        # Look for front-running patterns
        if index > 0:
            prev_tx = pending_txs[index - 1]
            if (tx.get('gasPrice', 0) > prev_tx.get('gasPrice', 0) * 1.5 and
                tx.get('to') == prev_tx.get('to')):
                return True
        
        # Look for sandwich attack patterns
        if index > 0 and index < len(pending_txs) - 1:
            prev_tx = pending_txs[index - 1]
            next_tx = pending_txs[index + 1]
            
            if (prev_tx.get('from') == next_tx.get('from') and
                tx.get('to') == prev_tx.get('to')):
                return True
        
        return False
    
    def _identify_competitor(self, tx: Dict) -> str:
        """Identify competitor from transaction data"""
        from_address = tx.get('from', 'unknown')
        
        # Known competitor addresses (would be populated from intelligence)
        known_competitors = {
            '0x123...': 'ArbitrageBot_v1',
            '0x456...': 'MEV_Expert',
            '0x789...': 'FlashLoan_Master'
        }
        
        return known_competitors.get(from_address, f"Unknown_{from_address[:8]}")
    
    def _estimate_arbitrage_profit(self, tx: Dict) -> float:
        """Estimate profit from arbitrage transaction"""
        # Simplified estimation - in production would use more sophisticated models
        value = tx.get('value', 0) / 1e18  # Convert to ETH
        gas_used = tx.get('gasUsed', 0)
        gas_price = tx.get('gasPrice', 0) / 1e9  # Convert to Gwei
        gas_cost = (gas_used * gas_price) / 1e9  # Convert to ETH
        
        # Assume 0.5-2% profit on volume
        estimated_profit = value * 0.01 - gas_cost
        return max(0, estimated_profit)
    
    def _classify_arbitrage_strategy(self, tx: Dict) -> str:
        """Classify arbitrage strategy type"""
        input_data = tx.get('input', '').lower()
        
        if 'flash' in input_data:
            return 'FLASH_LOAN_ARBITRAGE'
        elif 'triangular' in input_data or '3' in input_data:
            return 'TRIANGULAR_ARBITRAGE'
        elif 'cross' in input_data:
            return 'CROSS_CHAIN_ARBITRAGE'
        else:
            return 'SIMPLE_ARBITRAGE'
    
    def _extract_assets(self, tx: Dict) -> List[str]:
        """Extract assets involved in transaction"""
        # Simplified implementation
        return ['ETH', 'USDC']  # Placeholder
    
    def _classify_mev_type(self, tx: Dict, pending_txs: List[Dict], index: int) -> str:
        """Classify type of MEV activity"""
        if index > 0 and tx.get('to') == pending_txs[index - 1].get('to'):
            return 'FRONT_RUNNING'
        
        if (index > 0 and index < len(pending_txs) - 1 and
            pending_txs[index - 1].get('from') == pending_txs[index + 1].get('from')):
            return 'SANDWICH_ATTACK'
        
        return 'UNKNOWN_MEV'
    
    def _estimate_mev_profit(self, tx: Dict, pending_txs: List[Dict], index: int) -> float:
        """Estimate profit from MEV activity"""
        # Simplified estimation
        return 0.001  # Placeholder
    
    def _identify_mev_victim(self, tx: Dict, pending_txs: List[Dict], index: int) -> str:
        """Identify victim of MEV activity"""
        if index > 0:
            return pending_txs[index - 1].get('from', 'unknown')
        return 'unknown'
    
    async def _detect_large_capital_movements(self, market_data: Dict) -> List[CompetitorActivity]:
        """Detect large capital movements by competitors"""
        activities = []
        
        # Implementation would monitor large transfers
        # Placeholder implementation
        return activities
    
    async def _detect_new_integrations(self, market_data: Dict) -> List[CompetitorActivity]:
        """Detect new protocol integrations by competitors"""
        activities = []
        
        # Implementation would monitor for new contract interactions
        # Placeholder implementation
        return activities
    
    async def _detect_strategy_changes(self, market_data: Dict) -> List[CompetitorActivity]:
        """Detect strategy changes by competitors"""
        activities = []
        
        # Implementation would analyze pattern changes
        # Placeholder implementation
        return activities
    
    async def _calculate_impact_score(self, activity: CompetitorActivity) -> float:
        """Calculate impact score of competitor activity"""
        base_score = 0.5
        
        # Adjust based on activity type
        type_weights = {
            'ARBITRAGE': 0.3,
            'MEV': 0.7,
            'STRATEGIC_MOVE': 0.8
        }
        
        base_score *= type_weights.get(activity.activity_type, 0.5)
        
        # Adjust based on profit impact
        if 'profit_estimated' in activity.details:
            profit = activity.details['profit_estimated']
            if profit > 0.1:
                base_score *= 1.5
            elif profit > 0.01:
                base_score *= 1.2
        
        # Adjust based on frequency (recent similar activities)
        recent_activities = [
            a for a in self.competitor_activities 
            if a.competitor_id == activity.competitor_id and
            a.activity_type == activity.activity_type and
            (datetime.now() - a.timestamp).total_seconds() < 3600
        ]
        
        if len(recent_activities) > 5:
            base_score *= 1.3  # High frequency increases impact
        
        return min(1.0, base_score)
    
    async def analyze_market_position(self, our_performance: Dict, 
                                    competitor_activities: List[CompetitorActivity]) -> MarketPosition:
        """Analyze our market position relative to competitors"""
        # Calculate competitive metrics
        our_speed = our_performance.get('avg_execution_speed', 0)
        our_success_rate = our_performance.get('success_rate', 0)
        our_profitability = our_performance.get('profitability', 0)
        
        # Compare with competitors
        competitor_metrics = await self._calculate_competitor_metrics(competitor_activities)
        
        advantages = []
        threats = []
        opportunities = []
        
        # Speed advantage
        avg_competitor_speed = np.mean([m.get('speed', 0) for m in competitor_metrics.values()])
        if our_speed < avg_competitor_speed * 0.8:  # 20% faster
            advantages.append(f"Execution speed ({our_speed}ms vs avg {avg_competitor_speed:.0f}ms)")
        
        # Success rate advantage
        avg_competitor_success = np.mean([m.get('success_rate', 0) for m in competitor_metrics.values()])
        if our_success_rate > avg_competitor_success * 1.1:  # 10% higher
            advantages.append(f"Success rate ({our_success_rate:.1%} vs avg {avg_competitor_success:.1%})")
        
        # Identify threats
        for competitor, metrics in competitor_metrics.items():
            if metrics.get('speed', 0) < our_speed * 0.8:  # 20% faster than us
                threats.append(f"{competitor} has faster execution ({metrics['speed']}ms)")
            
            if metrics.get('activity_frequency', 0) > 10:  # High frequency
                threats.append(f"{competitor} has high activity frequency")
        
        # Identify opportunities
        market_gaps = await self._identify_market_gaps(our_performance, competitor_metrics)
        opportunities.extend(market_gaps)
        
        # Generate recommendation
        recommendation = self._generate_strategic_recommendation(advantages, threats, opportunities)
        
        # Determine overall position
        if len(advantages) >= 2 and len(threats) <= 1:
            position = "LEADING"
        elif len(advantages) >= 1:
            position = "COMPETITIVE"
        else:
            position = "CHALLENGED"
        
        return MarketPosition(
            our_position=position,
            competitive_advantage=advantages,
            threats=threats,
            opportunities=opportunities,
            recommendation=recommendation
        )
    
    async def _calculate_competitor_metrics(self, activities: List[CompetitorActivity]) -> Dict:
        """Calculate performance metrics for competitors"""
        metrics = defaultdict(lambda: {
            'speed': [],
            'success_rate': 0,
            'profitability': [],
            'activity_frequency': 0
        })
        
        for activity in activities:
            comp_metrics = metrics[activity.competitor_id]
            
            # Execution speed
            if 'execution_speed' in activity.details:
                comp_metrics['speed'].append(activity.details['execution_speed'])
            
            # Profitability
            if 'profit_estimated' in activity.details:
                comp_metrics['profitability'].append(activity.details['profit_estimated'])
            
            comp_metrics['activity_frequency'] += 1
        
        # Calculate averages
        for competitor, comp_metrics in metrics.items():
            if comp_metrics['speed']:
                comp_metrics['speed'] = np.mean(comp_metrics['speed'])
            else:
                comp_metrics['speed'] = 0
                
            if comp_metrics['profitability']:
                comp_metrics['profitability'] = np.mean(comp_metrics['profitability'])
            else:
                comp_metrics['profitability'] = 0
        
        return metrics
    
    async def _identify_market_gaps(self, our_performance: Dict, competitor_metrics: Dict) -> List[str]:
        """Identify market gaps and opportunities"""
        opportunities = []
        
        # Analyze competitor weaknesses
        slow_competitors = [
            comp for comp, metrics in competitor_metrics.items()
            if metrics.get('speed', 0) > 1000  # Slower than 1 second
        ]
        
        if slow_competitors:
            opportunities.append(f"Exploit speed advantage against {', '.join(slow_competitors)}")
        
        # Analyze market coverage
        all_strategies = set()
        for metrics in competitor_metrics.values():
            if 'strategies' in metrics:
                all_strategies.update(metrics['strategies'])
        
        our_strategies = our_performance.get('active_strategies', [])
        uncovered_strategies = all_strategies - set(our_strategies)
        
        if uncovered_strategies:
            opportunities.append(f"Expand into uncovered strategies: {', '.join(uncovered_strategies)}")
        
        # Time-based opportunities
        current_hour = datetime.now().hour
        if 2 <= current_hour <= 6:  # Low activity hours
            opportunities.append("Increase activity during low-competition hours")
        
        return opportunities
    
    def _generate_strategic_recommendation(self, advantages: List[str], 
                                         threats: List[str], opportunities: List[str]) -> str:
        """Generate strategic recommendations"""
        if not threats and opportunities:
            return "AGGRESSIVE_EXPANSION: Leverage advantages to capture market opportunities"
        
        elif threats and opportunities:
            return "BALANCED_APPROACH: Address threats while pursuing key opportunities"
        
        elif threats and not opportunities:
            return "DEFENSIVE_POSITION: Focus on mitigating competitive threats"
        
        else:
            return "MAINTAIN_COURSE: Continue current strategy with monitoring"
    
    async def generate_competitive_intelligence_report(self) -> Dict:
        """Generate comprehensive competitive intelligence report"""
        recent_activities = [
            a for a in self.competitor_activities 
            if (datetime.now() - a.timestamp).total_seconds() < 86400  # Last 24 hours
        ]
        
        # Group activities by competitor
        activities_by_competitor = defaultdict(list)
        for activity in recent_activities:
            activities_by_competitor[activity.competitor_id].append(activity)
        
        # Calculate competitor rankings
        competitor_rankings = self._rank_competitors(activities_by_competitor)
        
        # Identify key trends
        trends = await self._identify_competitive_trends(recent_activities)
        
        return {
            'report_timestamp': datetime.now().isoformat(),
            'total_activities_monitored': len(recent_activities),
            'active_competitors': len(activities_by_competitor),
            'top_competitors': competitor_rankings[:5],
            'market_trends': trends,
            'strategic_alert_level': self._calculate_alert_level(recent_activities),
            'recommended_actions': self._generate_competitive_actions(competitor_rankings, trends)
        }
    
    def _rank_competitors(self, activities_by_competitor: Dict) -> List[Tuple[str, float]]:
        """Rank competitors by threat level"""
        rankings = []
        
        for competitor, activities in activities_by_competitor.items():
            # Calculate threat score
            total_impact = sum(a.impact_score for a in activities)
            frequency = len(activities)
            avg_profit = np.mean([a.details.get('profit_estimated', 0) for a in activities])
            
            threat_score = (total_impact * 0.4 + frequency * 0.3 + avg_profit * 0.3)
            
            rankings.append((competitor, threat_score))
        
        return sorted(rankings, key=lambda x: x[1], reverse=True)
    
    async def _identify_competitive_trends(self, activities: List[CompetitorActivity]) -> List[Dict]:
        """Identify competitive trends from activity data"""
        trends = []
        
        # Group by hour to identify patterns
        hourly_activity = defaultdict(int)
        for activity in activities:
            hour = activity.timestamp.hour
            hourly_activity[hour] += 1
        
        # Find peak activity hours
        if hourly_activity:
            peak_hour = max(hourly_activity.items(), key=lambda x: x[1])
            trends.append({
                'trend': 'PEAK_ACTIVITY_HOURS',
                'description': f'Peak competitor activity at {peak_hour[0]}:00',
                'impact': 'HIGH'
            })
        
        # Analyze strategy trends
        strategy_counts = defaultdict(int)
        for activity in activities:
            if activity.activity_type == 'ARBITRAGE':
                strategy = activity.details.get('strategy_type', 'UNKNOWN')
                strategy_counts[strategy] += 1
        
        if strategy_counts:
            dominant_strategy = max(strategy_counts.items(), key=lambda x: x[1])
            trends.append({
                'trend': 'DOMINANT_STRATEGY',
                'description': f'{dominant_strategy[0]} is the most common arbitrage strategy',
                'impact': 'MEDIUM'
            })
        
        return trends
    
    def _calculate_alert_level(self, activities: List[CompetitorActivity]) -> str:
        """Calculate competitive alert level"""
        if not activities:
            return "LOW"
        
        high_impact_count = sum(1 for a in activities if a.impact_score > 0.7)
        total_impact = sum(a.impact_score for a in activities)
        
        if high_impact_count > 10 or total_impact > 5:
            return "HIGH"
        elif high_impact_count > 5 or total_impact > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_competitive_actions(self, rankings: List[Tuple[str, float]], 
                                   trends: List[Dict]) -> List[str]:
        """Generate competitive action recommendations"""
        actions = []
        
        # Address top competitors
        if rankings:
            top_competitor = rankings[0][0]
            actions.append(f"Monitor {top_competitor} closely - highest threat level")
        
        # Address trends
        for trend in trends:
            if trend['impact'] == 'HIGH':
                actions.append(f"Develop counter-strategy for: {trend['description']}")
        
        # General strategic actions
        if len(rankings) > 5:
            actions.append("Consider market diversification - high competitor concentration")
        
        return actions
