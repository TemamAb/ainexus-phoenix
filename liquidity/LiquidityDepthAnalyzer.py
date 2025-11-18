"""
AI-NEXUS LIQUIDITY DEPTH ANALYZER
Comprehensive liquidity depth analysis and market microstructure insights
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

class DepthLevel(Enum):
    SHALLOW = "shallow"
    MEDIUM = "medium"
    DEEP = "deep"
    VERY_DEEP = "very_deep"

class MarketRegime(Enum):
    NORMAL = "normal"
    STRESS = "stress"
    CRISIS = "crisis"
    RECOVERY = "recovery"

@dataclass
class DepthAnalysis:
    timestamp: int
    pool_address: str
    token_pair: Tuple[str, str]
    depth_level: DepthLevel
    market_regime: MarketRegime
    depth_metrics: Dict
    order_book_imbalance: float
    liquidity_concentration: float
    support_resistance_levels: List[float]
    risk_metrics: Dict

@dataclass
class DepthAlert:
    alert_id: str
    pool_address: str
    alert_type: str
    severity: str
    message: str
    timestamp: int
    metrics: Dict
    action_required: bool

class LiquidityDepthAnalyzer:
    """Advanced liquidity depth analysis engine"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.depth_history = {}
        self.regime_models = {}
        self.risk_thresholds = config.get('risk_thresholds', {
            'imbalance_threshold': 0.3,
            'concentration_threshold': 0.7,
            'depth_threshold': 100000,  # $100k
            'volatility_threshold': 0.05
        })
        
    async def analyze_liquidity_depth(self, pool_data: Dict, order_book: Optional[Dict] = None) -> DepthAnalysis:
        """Comprehensive liquidity depth analysis"""
        try:
            # Calculate depth metrics
            depth_metrics = await self.calculate_depth_metrics(pool_data, order_book)
            
            # Determine depth level
            depth_level = await self.determine_depth_level(depth_metrics)
            
            # Analyze market regime
            market_regime = await self.analyze_market_regime(pool_data, depth_metrics)
            
            # Calculate order book imbalance
            imbalance = await self.calculate_order_book_imbalance(order_book)
            
            # Analyze liquidity concentration
            concentration = await self.analyze_liquidity_concentration(pool_data, order_book)
            
            # Identify support/resistance levels
            support_resistance = await self.identify_support_resistance(order_book)
            
            # Calculate risk metrics
            risk_metrics = await self.calculate_risk_metrics(depth_metrics, imbalance, concentration)
            
            analysis = DepthAnalysis(
                timestamp=int(pd.Timestamp.now().timestamp()),
                pool_address=pool_data['address'],
                token_pair=pool_data['token_pair'],
                depth_level=depth_level,
                market_regime=market_regime,
                depth_metrics=depth_metrics,
                order_book_imbalance=imbalance,
                liquidity_concentration=concentration,
                support_resistance_levels=support_resistance,
                risk_metrics=risk_metrics
            )
            
            # Store analysis history
            await self.store_depth_history(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Depth analysis failed: {e}")
            raise
    
    async def calculate_depth_metrics(self, pool_data: Dict, order_book: Optional[Dict]) -> Dict:
        """Calculate comprehensive depth metrics"""
        metrics = {}
        
        # Basic liquidity metrics
        metrics['total_liquidity'] = pool_data.get('liquidity', 0)
        metrics['bid_liquidity'] = await self.calculate_bid_liquidity(order_book)
        metrics['ask_liquidity'] = await self.calculate_ask_liquidity(order_book)
        
        # Depth at different levels
        for level in [0.001, 0.005, 0.01, 0.02, 0.05]:  # 0.1% to 5% price impact
            metrics[f'depth_{int(level*100)}bp'] = await self.calculate_depth_at_impact(order_book, level)
        
        # Liquidity distribution metrics
        metrics['liquidity_gini'] = await self.calculate_liquidity_gini(order_book)
        metrics['depth_skewness'] = await self.calculate_depth_skewness(order_book)
        metrics['liquidity_entropy'] = await self.calculate_liquidity_entropy(order_book)
        
        # Resilience metrics
        metrics['liquidity_resilience'] = await self.calculate_liquidity_resilience(pool_data, order_book)
        metrics['market_impact_coefficient'] = await self.calculate_market_impact_coefficient(pool_data)
        
        # Temporal metrics
        metrics['depth_volatility'] = await self.calculate_depth_volatility(pool_data['address'])
        metrics['liquidity_persistence'] = await self.calculate_liquidity_persistence(pool_data['address'])
        
        return metrics
    
    async def calculate_bid_liquidity(self, order_book: Optional[Dict]) -> float:
        """Calculate total bid-side liquidity"""
        if not order_book or 'bids' not in order_book:
            return 0
        
        return sum(bid['quantity'] * bid['price'] for bid in order_book['bids'])
    
    async def calculate_ask_liquidity(self, order_book: Optional[Dict]) -> float:
        """Calculate total ask-side liquidity"""
        if not order_book or 'asks' not in order_book:
            return 0
        
        return sum(ask['quantity'] * ask['price'] for ask in order_book['asks'])
    
    async def calculate_depth_at_impact(self, order_book: Optional[Dict], max_impact: float) -> float:
        """Calculate available liquidity at specified maximum price impact"""
        if not order_book:
            return 0
        
        mid_price = await self.calculate_mid_price(order_book)
        max_price_change = mid_price * max_impact
        
        # Calculate depth on both sides within price impact limit
        bid_depth = await self.calculate_side_depth(order_book['bids'], mid_price, max_price_change, 'bid')
        ask_depth = await self.calculate_side_depth(order_book['asks'], mid_price, max_price_change, 'ask')
        
        return (bid_depth + ask_depth) / 2
    
    async def calculate_side_depth(self, orders: List[Dict], mid_price: float, max_change: float, side: str) -> float:
        """Calculate depth for one side within price change limit"""
        if not orders:
            return 0
        
        total_depth = 0
        current_price = mid_price
        
        for order in orders:
            if side == 'bid':
                price_diff = mid_price - order['price']
            else:  # ask
                price_diff = order['price'] - mid_price
            
            if price_diff <= max_change:
                total_depth += order['quantity'] * order['price']
            else:
                break
        
        return total_depth
    
    async def calculate_mid_price(self, order_book: Dict) -> float:
        """Calculate mid price from order book"""
        if not order_book or not order_book.get('bids') or not order_book.get('asks'):
            return 0
        
        best_bid = order_book['bids'][0]['price']
        best_ask = order_book['asks'][0]['price']
        
        return (best_bid + best_ask) / 2
    
    async def calculate_liquidity_gini(self, order_book: Optional[Dict]) -> float:
        """Calculate Gini coefficient for liquidity distribution"""
        if not order_book:
            return 0.5  # Default moderate inequality
        
        # Combine bid and ask liquidity
        all_orders = order_book.get('bids', []) + order_book.get('asks', [])
        if not all_orders:
            return 0.5
        
        # Extract liquidity amounts
        liquidities = [order['quantity'] * order['price'] for order in all_orders]
        liquidities.sort()
        
        # Calculate Gini coefficient
        n = len(liquidities)
        if n == 0:
            return 0.5
        
        total = sum(liquidities)
        if total == 0:
            return 0.5
        
        # Gini calculation
        gini_sum = sum((i + 1) * liquidity for i, liquidity in enumerate(liquidities))
        gini = (2 * gini_sum) / (n * total) - (n + 1) / n
        
        return max(0, min(1, gini))
    
    async def calculate_depth_skewness(self, order_book: Optional[Dict]) -> float:
        """Calculate skewness of liquidity distribution"""
        if not order_book:
            return 0
        
        # Use order sizes for skewness calculation
        order_sizes = []
        for side in ['bids', 'asks']:
            if side in order_book:
                order_sizes.extend([order['quantity'] for order in order_book[side]])
        
        if len(order_sizes) < 3:
            return 0
        
        return float(stats.skew(order_sizes))
    
    async def calculate_liquidity_entropy(self, order_book: Optional[Dict]) -> float:
        """Calculate entropy of liquidity distribution"""
        if not order_book:
            return 0
        
        # Combine all orders
        all_orders = order_book.get('bids', []) + order_book.get('asks', [])
        if not all_orders:
            return 0
        
        # Calculate liquidity proportions
        liquidities = [order['quantity'] * order['price'] for order in all_orders]
        total_liquidity = sum(liquidities)
        
        if total_liquidity == 0:
            return 0
        
        # Calculate entropy
        proportions = [l / total_liquidity for l in liquidities]
        entropy = -sum(p * np.log2(p) for p in proportions if p > 0)
        
        # Normalize by maximum possible entropy
        max_entropy = np.log2(len(liquidities))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return float(normalized_entropy)
    
    async def calculate_liquidity_resilience(self, pool_data: Dict, order_book: Optional[Dict]) -> float:
        """Calculate liquidity resilience score"""
        # Factors affecting resilience
        factors = []
        
        # Depth diversity
        gini = await self.calculate_liquidity_gini(order_book)
        factors.append(1 - gini)  # More equal distribution = higher resilience
        
        # Market maker presence (estimated)
        mm_presence = await self.estimate_market_maker_presence(order_book)
        factors.append(mm_presence)
        
        # Historical stability
        stability = await self.assess_historical_stability(pool_data['address'])
        factors.append(stability)
        
        # Overall resilience score
        return float(np.mean(factors))
    
    async def estimate_market_maker_presence(self, order_book: Optional[Dict]) -> float:
        """Estimate market maker presence based on order patterns"""
        if not order_book:
            return 0.5
        
        # Analyze order size consistency and spread
        bid_sizes = [order['quantity'] for order in order_book.get('bids', [])]
        ask_sizes = [order['quantity'] for order in order_book.get('asks', [])]
        
        if not bid_sizes or not ask_sizes:
            return 0.5
        
        # Check for consistent order sizes (market maker characteristic)
        bid_std = np.std(bid_sizes) if len(bid_sizes) > 1 else 0
        ask_std = np.std(ask_sizes) if len(ask_sizes) > 1 else 0
        
        size_consistency = 1 - (bid_std + ask_std) / (np.mean(bid_sizes) + np.mean(ask_sizes))
        
        return max(0, min(1, size_consistency))
    
    async def assess_historical_stability(self, pool_address: str) -> float:
        """Assess historical liquidity stability"""
        # Implementation would analyze historical depth data
        # Placeholder implementation
        return 0.8
    
    async def calculate_market_impact_coefficient(self, pool_data: Dict) -> float:
        """Calculate market impact coefficient"""
        # Simplified implementation
        liquidity = pool_data.get('liquidity', 1)
        return 1.0 / liquidity  # Inverse relationship with liquidity
    
    async def calculate_depth_volatility(self, pool_address: str) -> float:
        """Calculate depth volatility over time"""
        # Implementation would use historical depth data
        # Placeholder implementation
        return 0.1
    
    async def calculate_liquidity_persistence(self, pool_address: str) -> float:
        """Calculate liquidity persistence score"""
        # Implementation would analyze how long liquidity stays
        # Placeholder implementation
        return 0.7
    
    async def determine_depth_level(self, depth_metrics: Dict) -> DepthLevel:
        """Determine liquidity depth level"""
        total_liquidity = depth_metrics.get('total_liquidity', 0)
        depth_1bp = depth_metrics.get('depth_1bp', 0)  # Depth at 0.01% impact
        
        if total_liquidity < 100000 or depth_1bp < 10000:
            return DepthLevel.SHALLOW
        elif total_liquidity < 1000000 or depth_1bp < 50000:
            return DepthLevel.MEDIUM
        elif total_liquidity < 10000000 or depth_1bp < 200000:
            return DepthLevel.DEEP
        else:
            return DepthLevel.VERY_DEEP
    
    async def analyze_market_regime(self, pool_data: Dict, depth_metrics: Dict) -> MarketRegime:
        """Analyze current market regime"""
        volatility = pool_data.get('volatility', 0)
        depth_volatility = depth_metrics.get('depth_volatility', 0)
        resilience = depth_metrics.get('liquidity_resilience', 0)
        
        if volatility > 0.1 or depth_volatility > 0.15:
            return MarketRegime.CRISIS
        elif volatility > 0.05 or depth_volatility > 0.1:
            return MarketRegime.STRESS
        elif resilience > 0.7 and volatility < 0.02:
            return MarketRegime.RECOVERY
        else:
            return MarketRegime.NORMAL
    
    async def calculate_order_book_imbalance(self, order_book: Optional[Dict]) -> float:
        """Calculate order book imbalance"""
        if not order_book:
            return 0
        
        bid_liquidity = await self.calculate_bid_liquidity(order_book)
        ask_liquidity = await self.calculate_ask_liquidity(order_book)
        
        total_liquidity = bid_liquidity + ask_liquidity
        if total_liquidity == 0:
            return 0
        
        imbalance = (bid_liquidity - ask_liquidity) / total_liquidity
        return float(imbalance)
    
    async def analyze_liquidity_concentration(self, pool_data: Dict, order_book: Optional[Dict]) -> float:
        """Analyze liquidity concentration"""
        if not order_book:
            return 0.5
        
        # Calculate what percentage of liquidity is in top N orders
        all_orders = order_book.get('bids', []) + order_book.get('asks', [])
        if not all_orders:
            return 0.5
        
        # Sort by size
        orders_sorted = sorted(all_orders, key=lambda x: x['quantity'] * x['price'], reverse=True)
        total_liquidity = sum(order['quantity'] * order['price'] for order in orders_sorted)
        
        if total_liquidity == 0:
            return 0.5
        
        # Calculate concentration in top 20% of orders
        top_count = max(1, len(orders_sorted) // 5)
        top_liquidity = sum(order['quantity'] * order['price'] for order in orders_sorted[:top_count])
        
        concentration = top_liquidity / total_liquidity
        return float(concentration)
    
    async def identify_support_resistance_levels(self, order_book: Optional[Dict]) -> List[float]:
        """Identify key support and resistance levels"""
        if not order_book:
            return []
        
        levels = []
        
        # Analyze bid side for support levels
        bid_levels = await self.identize_price_levels(order_book.get('bids', []), 'support')
        levels.extend(bid_levels)
        
        # Analyze ask side for resistance levels
        ask_levels = await self.identize_price_levels(order_book.get('asks', []), 'resistance')
        levels.extend(ask_levels)
        
        return sorted(levels)
    
    async def identize_price_levels(self, orders: List[Dict], level_type: str) -> List[float]:
        """Identify significant price levels"""
        if not orders:
            return []
        
        # Group orders by price levels (within 0.1% range)
        price_levels = {}
        for order in orders:
            price = order['price']
            # Round to significant level
            level = round(price, 3)  # Adjust precision as needed
            
            if level not in price_levels:
                price_levels[level] = 0
            
            price_levels[level] += order['quantity']
        
        # Find levels with significant liquidity
        significant_levels = []
        total_liquidity = sum(price_levels.values())
        
        for price, liquidity in price_levels.items():
            if liquidity / total_liquidity > 0.05:  # 5% threshold
                significant_levels.append(price)
        
        return significant_levels
    
    async def calculate_risk_metrics(self, depth_metrics: Dict, imbalance: float, concentration: float) -> Dict:
        """Calculate comprehensive risk metrics"""
        risk_metrics = {}
        
        # Depth risk
        total_liquidity = depth_metrics.get('total_liquidity', 0)
        risk_metrics['depth_risk'] = max(0, 1 - (total_liquidity / self.risk_thresholds['depth_threshold']))
        
        # Imbalance risk
        risk_metrics['imbalance_risk'] = min(1, abs(imbalance) / self.risk_thresholds['imbalance_threshold'])
        
        # Concentration risk
        risk_metrics['concentration_risk'] = min(1, concentration / self.risk_thresholds['concentration_threshold'])
        
        # Resilience risk
        resilience = depth_metrics.get('liquidity_resilience', 0.5)
        risk_metrics['resilience_risk'] = 1 - resilience
        
        # Overall risk score (weighted average)
        weights = {
            'depth_risk': 0.3,
            'imbalance_risk': 0.25,
            'concentration_risk': 0.25,
            'resilience_risk': 0.2
        }
        
        risk_metrics['overall_risk'] = sum(
            risk_metrics[risk] * weight 
            for risk, weight in weights.items()
        )
        
        # Risk level classification
        if risk_metrics['overall_risk'] < 0.3:
            risk_metrics['risk_level'] = 'LOW'
        elif risk_metrics['overall_risk'] < 0.6:
            risk_metrics['risk_level'] = 'MEDIUM'
        else:
            risk_metrics['risk_level'] = 'HIGH'
        
        return risk_metrics
    
    async def store_depth_history(self, analysis: DepthAnalysis):
        """Store depth analysis in history"""
        key = analysis.pool_address
        
        if key not in self.depth_history:
            self.depth_history[key] = []
        
        self.depth_history[key].append(analysis)
        
        # Keep only last 1000 analyses per pool
        if len(self.depth_history[key]) > 1000:
            self.depth_history[key].pop(0)
    
    async def generate_depth_alerts(self, analysis: DepthAnalysis) -> List[DepthAlert]:
        """Generate alerts based on depth analysis"""
        alerts = []
        
        # High risk alert
        if analysis.risk_metrics['risk_level'] == 'HIGH':
            alerts.append(DepthAlert(
                alert_id=f"high_risk_{analysis.timestamp}",
                pool_address=analysis.pool_address,
                alert_type="HIGH_RISK_DEPTH",
                severity="HIGH",
                message=f"High liquidity risk detected: {analysis.risk_metrics['overall_risk']:.2f}",
                timestamp=analysis.timestamp,
                metrics=analysis.risk_metrics,
                action_required=True
            ))
        
        # Shallow depth alert
        if analysis.depth_level == DepthLevel.SHALLOW:
            alerts.append(DepthAlert(
                alert_id=f"shallow_depth_{analysis.timestamp}",
                pool_address=analysis.pool_address,
                alert_type="SHALLOW_DEPTH",
                severity="MEDIUM",
                message="Shallow liquidity depth detected",
                timestamp=analysis.timestamp,
                metrics=analysis.depth_metrics,
                action_required=False
            ))
        
        # High concentration alert
        if analysis.liquidity_concentration > self.risk_thresholds['concentration_threshold']:
            alerts.append(DepthAlert(
                alert_id=f"high_concentration_{analysis.timestamp}",
                pool_address=analysis.pool_address,
                alert_type="HIGH_CONCENTRATION",
                severity="MEDIUM",
                message=f"High liquidity concentration: {analysis.liquidity_concentration:.2f}",
                timestamp=analysis.timestamp,
                metrics={'concentration': analysis.liquidity_concentration},
                action_required=False
            ))
        
        # Market stress alert
        if analysis.market_regime == MarketRegime.STRESS:
            alerts.append(DepthAlert(
                alert_id=f"market_stress_{analysis.timestamp}",
                pool_address=analysis.pool_address,
                alert_type="MARKET_STRESS",
                severity="HIGH",
                message="Market stress regime detected",
                timestamp=analysis.timestamp,
                metrics={'regime': analysis.market_regime.value},
                action_required=True
            ))
        
        return alerts
    
    async def get_depth_analytics(self, pool_address: str, timeframe: str = '24h') -> Dict:
        """Get analytics for depth analysis history"""
        if pool_address not in self.depth_history:
            return {"error": "No depth data available"}
        
        history = self.depth_history[pool_address]
        
        # Filter by timeframe
        timeframe_ms = self.get_timeframe_ms(timeframe)
        recent_history = [
            h for h in history 
            if (pd.Timestamp.now().timestamp() - h.timestamp) < timeframe_ms
        ]
        
        if not recent_history:
            return {"error": "No data for specified timeframe"}
        
        analytics = {
            "total_analyses": len(recent_history),
            "depth_level_distribution": self.analyze_depth_level_distribution(recent_history),
            "market_regime_distribution": self.analyze_regime_distribution(recent_history),
            "risk_metrics_trend": self.analyze_risk_trends(recent_history),
            "liquidity_quality_score": await self.calculate_liquidity_quality_score(recent_history),
            "recommendations": await self.generate_depth_recommendations(recent_history)
        }
        
        return analytics
    
    def analyze_depth_level_distribution(self, history: List[DepthAnalysis]) -> Dict:
        """Analyze distribution of depth levels"""
        distribution = {}
        for level in DepthLevel:
            distribution[level.value] = len([h for h in history if h.depth_level == level])
        
        return distribution
    
    def analyze_regime_distribution(self, history: List[DepthAnalysis]) -> Dict:
        """Analyze distribution of market regimes"""
        distribution = {}
        for regime in MarketRegime:
            distribution[regime.value] = len([h for h in history if h.market_regime == regime])
        
        return distribution
    
    def analyze_risk_trends(self, history: List[DepthAnalysis]) -> Dict:
        """Analyze trends in risk metrics"""
        if len(history) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        risk_scores = [h.risk_metrics['overall_risk'] for h in history]
        
        return {
            "average_risk": np.mean(risk_scores),
            "risk_volatility": np.std(risk_scores),
            "risk_trend": "increasing" if risk_scores[-1] > risk_scores[0] else "decreasing",
            "min_risk": min(risk_scores),
            "max_risk": max(risk_scores)
        }
    
    async def calculate_liquidity_quality_score(self, history: List[DepthAnalysis]) -> float:
        """Calculate overall liquidity quality score"""
        if not history:
            return 0.5
        
        scores = []
        
        for analysis in history:
            # Factors for quality score
            depth_score = 1 - analysis.risk_metrics['depth_risk']
            resilience_score = analysis.depth_metrics.get('liquidity_resilience', 0.5)
            concentration_score = 1 - analysis.risk_metrics['concentration_risk']
            
            # Weighted quality score
            quality = (depth_score * 0.4) + (resilience_score * 0.4) + (concentration_score * 0.2)
            scores.append(quality)
        
        return float(np.mean(scores))
    
    async def generate_depth_recommendations(self, history: List[DepthAnalysis]) -> List[Dict]:
        """Generate recommendations based on depth analysis"""
        recommendations = []
        
        if not history:
            return recommendations
        
        current_analysis = history[-1]
        analytics = await self.get_depth_analytics(current_analysis.pool_address, '24h')
        
        # Risk-based recommendations
        if current_analysis.risk_metrics['risk_level'] == 'HIGH':
            recommendations.append({
                "type": "RISK_MITIGATION",
                "priority": "HIGH",
                "message": "Implement aggressive risk mitigation strategies",
                "suggestions": [
                    "Reduce position sizes",
                    "Increase slippage tolerance",
                    "Use multiple execution venues",
                    "Monitor closely for regime changes"
                ]
            })
        
        # Depth improvement recommendations
        if current_analysis.depth_level == DepthLevel.SHALLOW:
            recommendations.append({
                "type": "LIQUIDITY_ENHANCEMENT",
                "priority": "MEDIUM",
                "message": "Consider liquidity enhancement strategies",
                "suggestions": [
                    "Explore alternative pools with better depth",
                    "Coordinate with market makers",
                    "Use batched executions to reduce impact",
                    "Monitor for depth improvement opportunities"
                ]
            })
        
        # Concentration reduction recommendations
        if current_analysis.liquidity_concentration > 0.7:
            recommendations.append({
                "type": "DIVERSIFICATION",
                "priority": "MEDIUM",
                "message": "High concentration detected - diversify execution",
                "suggestions": [
                    "Split large orders across multiple venues",
                    "Use time-weighted execution strategies",
                    "Monitor for concentration reduction opportunities"
                ]
            })
        
        return recommendations
    
    def get_timeframe_ms(self, timeframe: str) -> int:
        """Convert timeframe string to milliseconds"""
        timeframes = {
            '1h': 3600000,
            '6h': 21600000,
            '24h': 86400000,
            '7d': 604800000,
            '30d': 2592000000
        }
        
        return timeframes.get(timeframe, 86400000)
    
    async def visualize_depth_analysis(self, analysis: DepthAnalysis, save_path: Optional[str] = None):
        """Create visualization of depth analysis"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'Liquidity Depth Analysis - {analysis.pool_address}', fontsize=16)
            
            # 1. Depth metrics radar chart
            await self.create_depth_radar_chart(analysis, ax1)
            
            # 2. Risk metrics bar chart
            await self.create_risk_bar_chart(analysis, ax2)
            
            # 3. Historical trend (if available)
            await self.create_historical_trend_chart(analysis.pool_address, ax3)
            
            # 4. Market regime analysis
            await self.create_regime_analysis_chart(analysis, ax4)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Depth analysis visualization saved to: {save_path}")
            
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Visualization failed: {e}")
    
    async def create_depth_radar_chart(self, analysis: DepthAnalysis, ax):
        """Create radar chart for depth metrics"""
        # Implementation would create radar chart
        # Placeholder implementation
        ax.text(0.5, 0.5, 'Depth Radar Chart', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Depth Metrics Radar')
    
    async def create_risk_bar_chart(self, analysis: DepthAnalysis, ax):
        """Create bar chart for risk metrics"""
        risks = analysis.risk_metrics
        risk_types = ['Depth Risk', 'Imbalance Risk', 'Concentration Risk', 'Resilience Risk']
        risk_values = [risks['depth_risk'], risks['imbalance_risk'], risks['concentration_risk'], risks['resilience_risk']]
        
        bars = ax.bar(risk_types, risk_values, color=['red' if v > 0.6 else 'orange' if v > 0.3 else 'green' for v in risk_values])
        ax.set_ylabel('Risk Score')
        ax.set_title('Risk Metrics Breakdown')
        ax.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, value in zip(bars, risk_values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.2f}', 
                   ha='center', va='bottom')
    
    async def create_historical_trend_chart(self, pool_address: str, ax):
        """Create historical trend chart"""
        # Implementation would use historical data
        # Placeholder implementation
        ax.text(0.5, 0.5, 'Historical Trend Chart', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Historical Depth Trends')
    
    async def create_regime_analysis_chart(self, analysis: DepthAnalysis, ax):
        """Create market regime analysis chart"""
        regimes = [r.value for r in MarketRegime]
        regime_colors = {'normal': 'green', 'stress': 'orange', 'crisis': 'red', 'recovery': 'blue'}
        
        # Simple pie chart for regime distribution (if historical data available)
        if analysis.pool_address in self.depth_history:
            history = self.depth_history[analysis.pool_address][-100:]  # Last 100 analyses
            regime_counts = {r.value: 0 for r in MarketRegime}
            
            for h in history:
                regime_counts[h.market_regime.value] += 1
            
            total = sum(regime_counts.values())
            if total > 0:
                sizes = [count/total for count in regime_counts.values()]
                colors = [regime_colors[regime] for regime in regime_counts.keys()]
                
                ax.pie(sizes, labels=regime_counts.keys(), colors=colors, autopct='%1.1f%%')
                ax.set_title('Market Regime Distribution (Recent)')
                return
        
        # Fallback: current regime only
        ax.text(0.5, 0.5, f'Current Regime: {analysis.market_regime.value}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=14,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=regime_colors[analysis.market_regime.value], alpha=0.7))
        ax.set_title('Current Market Regime')

# Example usage
if __name__ == "__main__":
    analyzer = LiquidityDepthAnalyzer({})
    
    # Example pool data
    pool_data = {
        'address': '0x123...',
        'token_pair': ('WETH', 'USDC'),
        'liquidity': 1500000,
        'volatility': 0.02
    }
    
    # Example order book
    order_book = {
        'bids': [
            {'price': 1999, 'quantity': 10},
            {'price': 1998, 'quantity': 15},
            {'price': 1997, 'quantity': 20}
        ],
        'asks': [
            {'price': 2001, 'quantity': 12},
            {'price': 2002, 'quantity': 18},
            {'price': 2003, 'quantity': 25}
        ]
    }
    
    # Run analysis
    async def example():
        analysis = await analyzer.analyze_liquidity_depth(pool_data, order_book)
        print(f"Depth Level: {analysis.depth_level.value}")
        print(f"Market Regime: {analysis.market_regime.value}")
        print(f"Overall Risk: {analysis.risk_metrics['overall_risk']:.2f} ({analysis.risk_metrics['risk_level']})")
        
        alerts = await analyzer.generate_depth_alerts(analysis)
        for alert in alerts:
            print(f"Alert: {alert.message} (Severity: {alert.severity})")
    
    asyncio.run(example())
