#!/usr/bin/env python3
"""
AI-NEXUS Oracle Validation Engine
Multi-source validation with manipulation protection
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from statistics import median, mean
from dataclasses import dataclass
import time

@dataclass
class OracleSource:
    name: str
    url: str
    weight: float
    last_update: float
    reliability: float

class OracleValidator:
    def __init__(self, confidence_threshold: float = 0.95):
        self.sources = []
        self.confidence_threshold = confidence_threshold
        self.price_history = {}
        self.manipulation_detector = ManipulationDetector()
        
    def add_source(self, name: str, url: str, weight: float = 1.0):
        """Add oracle data source"""
        source = OracleSource(
            name=name,
            url=url,
            weight=weight,
            last_update=0,
            reliability=1.0
        )
        self.sources.append(source)
    
    async def get_validated_price(self, symbol: str) -> Dict:
        """Get validated price with confidence score"""
        # Fetch prices from all sources
        prices = await self._fetch_all_prices(symbol)
        
        if not prices:
            return {"error": "No prices available"}
        
        # Detect manipulation attempts
        manipulation_score = self.manipulation_detector.analyze(prices, symbol)
        
        if manipulation_score > 0.8:
            # High manipulation risk - use fallback mechanism
            return await self._get_fallback_price(symbol)
        
        # Calculate weighted median price
        validated_price = self._calculate_weighted_median(prices)
        confidence = self._calculate_confidence(prices, validated_price)
        
        # Update source reliability
        self._update_source_reliability(prices, validated_price)
        
        return {
            "symbol": symbol,
            "price": validated_price,
            "confidence": confidence,
            "manipulation_risk": manipulation_score,
            "sources_used": len(prices),
            "timestamp": time.time()
        }
    
    async def _fetch_all_prices(self, symbol: str) -> List[Dict]:
        """Fetch prices from all sources concurrently"""
        tasks = []
        for source in self.sources:
            task = self._fetch_source_price(source, symbol)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_prices = []
        for i, result in enumerate(results):
            if isinstance(result, dict) and 'price' in result:
                valid_prices.append({
                    'price': result['price'],
                    'source': self.sources[i].name,
                    'weight': self.sources[i].weight,
                    'timestamp': result.get('timestamp', time.time())
                })
        
        return valid_prices
    
    async def _fetch_source_price(self, source: OracleSource, symbol: str) -> Dict:
        """Fetch price from individual source"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                # This would be customized per oracle source
                if 'chainlink' in source.name.lower():
                    price = await self._fetch_chainlink_price(session, symbol)
                elif 'uniswap' in source.name.lower():
                    price = await self._fetch_uniswap_price(session, symbol)
                else:
                    # Generic API call
                    price = await self._fetch_generic_price(session, source.url, symbol)
                
                source.last_update = time.time()
                return {'price': price, 'timestamp': time.time()}
                
        except Exception as e:
            print(f"Error fetching from {source.name}: {e}")
            # Temporarily reduce reliability
            source.reliability *= 0.9
            raise e
    
    def _calculate_weighted_median(self, prices: List[Dict]) -> float:
        """Calculate weighted median price"""
        if not prices:
            return 0.0
        
        # Sort prices and create weighted list
        sorted_prices = sorted(prices, key=lambda x: x['price'])
        
        weighted_prices = []
        for price_data in sorted_prices:
            weight = price_data['weight'] * self._get_source_reliability(price_data['source'])
            count = max(1, int(weight * 100))
            weighted_prices.extend([price_data['price']] * count)
        
        return median(weighted_prices)
    
    def _calculate_confidence(self, prices: List[Dict], median_price: float) -> float:
        """Calculate confidence score based on price consensus"""
        if len(prices) < 2:
            return 0.5
        
        deviations = []
        for price_data in prices:
            deviation = abs(price_data['price'] - median_price) / median_price
            weight = price_data['weight'] * self._get_source_reliability(price_data['source'])
            deviations.append(deviation * weight)
        
        avg_deviation = mean(deviations)
        confidence = max(0, 1 - avg_deviation * 10)  # Convert to 0-1 scale
        
        return confidence
    
    def _get_source_reliability(self, source_name: str) -> float:
        """Get reliability score for source"""
        for source in self.sources:
            if source.name == source_name:
                return source.reliability
        return 0.5
    
    def _update_source_reliability(self, prices: List[Dict], validated_price: float):
        """Update source reliability based on performance"""
        for price_data in prices:
            for source in self.sources:
                if source.name == price_data['source']:
                    deviation = abs(price_data['price'] - validated_price) / validated_price
                    # Update reliability based on deviation
                    if deviation < 0.01:  # Within 1%
                        source.reliability = min(1.0, source.reliability + 0.01)
                    else:
                        source.reliability = max(0.1, source.reliability - deviation)
    
    async def _get_fallback_price(self, symbol: str) -> Dict:
        """Get fallback price when manipulation is detected"""
        # Use most reliable sources only
        reliable_sources = sorted(self.sources, key=lambda x: x.reliability, reverse=True)[:3]
        
        fallback_prices = []
        for source in reliable_sources:
            try:
                price_data = await self._fetch_source_price(source, symbol)
                fallback_prices.append(price_data['price'])
            except:
                continue
        
        if fallback_prices:
            fallback_price = median(fallback_prices)
            return {
                "symbol": symbol,
                "price": fallback_price,
                "confidence": 0.7,  # Reduced confidence
                "manipulation_risk": 0.9,
                "fallback_used": True,
                "sources_used": len(fallback_prices),
                "timestamp": time.time()
            }
        else:
            return {"error": "No fallback prices available"}
    
    async def _fetch_chainlink_price(self, session, symbol: str) -> float:
        """Fetch price from Chainlink oracle"""
        # Mock implementation
        return 1800.0  # ETH price
    
    async def _fetch_uniswap_price(self, session, symbol: str) -> float:
        """Fetch price from Uniswap pool"""
        # Mock implementation
        return 1795.0
    
    async def _fetch_generic_price(self, session, url: str, symbol: str) -> float:
        """Fetch price from generic API"""
        # Mock implementation
        return 1802.0

class ManipulationDetector:
    def __init__(self):
        self.price_history = {}
        self.volume_history = {}
    
    def analyze(self, prices: List[Dict], symbol: str) -> float:
        """Analyze for price manipulation attempts"""
        if len(prices) < 3:
            return 0.0
        
        current_prices = [p['price'] for p in prices]
        median_price = median(current_prices)
        
        # Check for outliers
        outliers = self._detect_outliers(current_prices, median_price)
        
        # Check price volatility
        volatility = self._calculate_volatility(current_prices)
        
        # Check consensus
        consensus = self._calculate_consensus(current_prices, median_price)
        
        manipulation_score = (outliers * 0.4 + volatility * 0.3 + (1 - consensus) * 0.3)
        return min(manipulation_score, 1.0)
    
    def _detect_outliers(self, prices: List[float], median_price: float) -> float:
        """Detect price outliers"""
        if not prices:
            return 0.0
        
        deviations = [abs(p - median_price) / median_price for p in prices]
        outlier_threshold = 0.05  # 5% deviation
        
        outlier_count = sum(1 for d in deviations if d > outlier_threshold)
        return outlier_count / len(prices)
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 2:
            return 0.0
        
        returns = [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]
        volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5
        return min(volatility * 10, 1.0)  # Normalize to 0-1
    
    def _calculate_consensus(self, prices: List[float], median_price: float) -> float:
        """Calculate price consensus"""
        if not prices:
            return 1.0
        
        deviations = [abs(p - median_price) / median_price for p in prices]
        avg_deviation = sum(deviations) / len(deviations)
        consensus = 1 - min(avg_deviation * 10, 1.0)
        return consensus
