# File: liquidity/liquidity_intelligence/LiquidityDepthAnalyzer.py
# 7P-PILLAR: CAPITAL-7P, BOT3-7P
# PURPOSE: Advanced liquidity analysis and depth prediction

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import time

class LiquidityTier(Enum):
    DEEP = "deep"           # > $10M liquidity
    MEDIUM = "medium"       # $1M - $10M liquidity  
    SHALLOW = "shallow"     # $100K - $1M liquidity
    VERY_SHALLOW = "very_shallow"  # < $100K liquidity

@dataclass
class LiquidityAnalysis:
    pool_address: str
    token_pair: str
    total_liquidity: float
    liquidity_tier: LiquidityTier
    depth_analysis: Dict
    concentration_risk: float
    predicted_slippage: Dict
    timestamp: float

class LiquidityDepthAnalyzer:
    """
    Advanced liquidity analysis for optimal trade execution
    Prevents market impact and optimizes trade sizing
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.liquidity_snapshots: Dict[str, List[LiquidityAnalysis]] = {}
        self.pool_characteristics: Dict[str, Dict] = {}
        self.logger = logging.getLogger('LiquidityDepthAnalyzer')
        
    async def analyze_pool_liquidity(self, pool_data: Dict) -> LiquidityAnalysis:
        """Comprehensive liquidity analysis for a pool"""
        try:
            # Calculate total liquidity
            total_liquidity = self.calculate_total_liquidity(pool_data)
            
            # Determine liquidity tier
            liquidity_tier = self.classify_liquidity_tier(total_liquidity)
            
            # Analyze liquidity depth
            depth_analysis = self.analyze_liquidity_depth(pool_data, total_liquidity)
            
            # Calculate concentration risk
            concentration_risk = self.calculate_concentration_risk(pool_data)
            
            # Predict slippage for different trade sizes
            predicted_slippage = self.predict_slippage(pool_data, total_liquidity)
            
            analysis = LiquidityAnalysis(
                pool_address=pool_data.get('address', 'unknown'),
                token_pair=pool_data.get('token_pair', 'unknown'),
                total_liquidity=total_liquidity,
                liquidity_tier=liquidity_tier,
                depth_analysis=depth_analysis,
                concentration_risk=concentration_risk,
                predicted_slippage=predicted_slippage,
                timestamp=time.time()
            )
            
            # Store analysis
            self.store_liquidity_snapshot(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Liquidity analysis error: {e}")
            raise
    
    def calculate_total_liquidity(self, pool_data: Dict) -> float:
        """Calculate total liquidity in USD"""
        try:
            # Extract token amounts and prices
            token0_amount = pool_data.get('token0_reserve', 0)
            token1_amount = pool_data.get('token1_reserve', 0)
            token0_price = pool_data.get('token0_price', 1.0)
            token1_price = pool_data.get('token1_price', 1.0)
            
            # Calculate liquidity in USD
            liquidity_usd = (token0_amount * token0_price) + (token1_amount * token1_price)
            
            return liquidity_usd
            
        except Exception as e:
            self.logger.warning(f"Liquidity calculation error: {e}")
            return 0.0
    
    def classify_liquidity_tier(self, liquidity_usd: float) -> LiquidityTier:
        """Classify pool into liquidity tier"""
        if liquidity_usd > 10_000_000:
            return LiquidityTier.DEEP
        elif liquidity_usd > 1_000_000:
            return LiquidityTier.MEDIUM
        elif liquidity_usd > 100_000:
            return LiquidityTier.SHALLOW
        else:
            return LiquidityTier.VERY_SHALLOW
    
    def analyze_liquidity_depth(self, pool_data: Dict, total_liquidity: float) -> Dict:
        """Analyze liquidity depth at different price levels"""
        depth_analysis = {
            'shallow_depth': 0.0,    # Liquidity within 1% of current price
            'medium_depth': 0.0,     # Liquidity within 5% of current price  
            'deep_depth': 0.0,       # Liquidity within 10% of current price
            'depth_ratio': 0.0,      # Ratio of deep to shallow liquidity
            'price_support': []       # Key support levels
        }
        
        try:
            # Simulate depth calculation (would use actual pool curve data)
            # For Uniswap V3, this would analyze ticks and liquidity
            current_price = pool_data.get('current_price', 1.0)
            
            # Mock depth calculation
            depth_analysis['shallow_depth'] = total_liquidity * 0.3  # 30% within 1%
            depth_analysis['medium_depth'] = total_liquidity * 0.6   # 60% within 5%
            depth_analysis['deep_depth'] = total_liquidity * 0.8     # 80% within 10%
            depth_analysis['depth_ratio'] = depth_analysis['deep_depth'] / max(1, depth_analysis['shallow_depth'])
            
            # Identify key support levels (simplified)
            price_levels = [current_price * (1 - i * 0.01) for i in range(1, 11)]  # 1% to 10% below
            depth_analysis['price_support'] = [
                {'price': price, 'liquidity': total_liquidity * (1 - i * 0.05)} 
                for i, price in enumerate(price_levels)
            ]
            
        except Exception as e:
            self.logger.warning(f"Depth analysis error: {e}")
        
        return depth_analysis
    
    def calculate_concentration_risk(self, pool_data: Dict) -> float:
        """Calculate liquidity concentration risk (0-1, higher = more risk)"""
        risk_score = 0.0
        
        try:
            # Factor 1: Pool size relative to typical pools
            total_liquidity = self.calculate_total_liquidity(pool_data)
            if total_liquidity < 100_000:
                risk_score += 0.4
            elif total_liquidity < 1_000_000:
                risk_score += 0.2
            
            # Factor 2: Token concentration (would analyze holder distribution)
            # For now, use simplified approach
            if pool_data.get('is_new_pool', False):
                risk_score += 0.3
            
            # Factor 3: Volume to liquidity ratio
            daily_volume = pool_data.get('volume_24h', 0)
            if total_liquidity > 0:
                volume_ratio = daily_volume / total_liquidity
                if volume_ratio > 1.0:  # High turnover
                    risk_score += 0.3
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Concentration risk calculation error: {e}")
            return 0.5
    
    def predict_slippage(self, pool_data: Dict, total_liquidity: float) -> Dict:
        """Predict slippage for different trade sizes"""
        slippage_predictions = {}
        
        try:
            trade_sizes = [1000, 5000, 10000, 50000, 100000]  # USD
            
            for size in trade_sizes:
                # Simplified slippage model
                # In production, would use actual pool curve mathematics
                size_ratio = size / max(1, total_liquidity)
                
                if size_ratio < 0.001:  # 0.1% of liquidity
                    slippage = size_ratio * 0.1  # 0.01% slippage
                elif size_ratio < 0.01:  # 1% of liquidity
                    slippage = size_ratio * 0.3  # 0.3% slippage
                elif size_ratio < 0.05:  # 5% of liquidity
                    slippage = size_ratio * 0.8  # 4% slippage
                else:
                    slippage = size_ratio * 2.0  # 10%+ slippage
                
                slippage_predictions[f"${size}"] = {
                    'slippage_percent': slippage * 100,
                    'size_ratio': size_ratio,
                    'acceptable': slippage < 0.01  # Less than 1% slippage
                }
                
        except Exception as e:
            self.logger.warning(f"Slippage prediction error: {e}")
        
        return slippage_predictions
    
    def store_liquidity_snapshot(self, analysis: LiquidityAnalysis):
        """Store liquidity analysis for historical tracking"""
        pool_key = f"{analysis.pool_address}_{analysis.token_pair}"
        
        if pool_key not in self.liquidity_snapshots:
            self.liquidity_snapshots[pool_key] = []
        
        self.liquidity_snapshots[pool_key].append(analysis)
        
        # Keep only last 1000 snapshots per pool
        if len(self.liquidity_snapshots[pool_key]) > 1000:
            self.liquidity_snapshots[pool_key] = self.liquidity_snapshots[pool_key][-1000:]
    
    def get_optimal_trade_size(self, pool_address: str, token_pair: str, max_slippage: float = 1.0) -> float:
        """Calculate optimal trade size to stay within max slippage"""
        try:
            # Get latest liquidity analysis
            pool_key = f"{pool_address}_{token_pair}"
            if pool_key not in self.liquidity_snapshots or not self.liquidity_snapshots[pool_key]:
                return 1000  # Default conservative size
            
            latest_analysis = self.liquidity_snapshots[pool_key][-1]
            total_liquidity = latest_analysis.total_liquidity
            
            # Calculate max size for given slippage
            # Using inverse of slippage model
            if max_slippage < 0.1:  # 0.1% slippage
                optimal_size = total_liquidity * 0.001  # 0.1% of liquidity
            elif max_slippage < 1.0:  # 1% slippage
                optimal_size = total_liquidity * 0.01   # 1% of liquidity
            else:
                optimal_size = total_liquidity * 0.05   # 5% of liquidity
            
            return min(optimal_size, 100000)  # Cap at $100K
            
        except Exception as e:
            self.logger.warning(f"Optimal trade size calculation error: {e}")
            return 5000  # Fallback size
    
    def identify_liquidity_opportunities(self, pools_data: List[Dict]) -> List[Dict]:
        """Identify pools with favorable liquidity conditions"""
        opportunities = []
        
        for pool_data in pools_data:
            try:
                analysis = asyncio.run(self.analyze_pool_liquidity(pool_data))
                
                # Criteria for good liquidity opportunity
                if (analysis.liquidity_tier in [LiquidityTier.DEEP, LiquidityTier.MEDIUM] and
                    analysis.concentration_risk < 0.3 and
                    analysis.depth_analysis['depth_ratio'] > 1.5):
                    
                    opportunity = {
                        'pool_address': analysis.pool_address,
                        'token_pair': analysis.token_pair,
                        'liquidity_tier': analysis.liquidity_tier.value,
                        'total_liquidity': analysis.total_liquidity,
                        'concentration_risk': analysis.concentration_risk,
                        'optimal_trade_size': self.get_optimal_trade_size(
                            analysis.pool_address, analysis.token_pair
                        ),
                        'timestamp': analysis.timestamp
                    }
                    
                    opportunities.append(opportunity)
                    
            except Exception as e:
                self.logger.warning(f"Opportunity identification error for pool {pool_data.get('address')}: {e}")
        
        # Sort by liquidity depth (descending)
        opportunities.sort(key=lambda x: x['total_liquidity'], reverse=True)
        
        return opportunities

# Example usage
if __name__ == "__main__":
    analyzer = LiquidityDepthAnalyzer({})
    print("LiquidityDepthAnalyzer initialized successfully")
