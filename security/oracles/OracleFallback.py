"""
AI-NEXUS v5.0 - ORACLE FALLBACK MODULE
Advanced oracle failure detection and graceful degradation system
Multi-source validation and emergency price feeds
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from statistics import median
import warnings
warnings.filterwarnings('ignore')

class OracleStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNRELIABLE = "unreliable"
    FAILED = "failed"

class FallbackStrategy(Enum):
    MULTI_SOURCE_CONSENSUS = "multi_source_consensus"
    TIME_WEIGHTED_AVERAGE = "time_weighted_average"
    MEDIAN_PRICE = "median_price"
    LAST_KNOWN_GOOD = "last_known_good"
    EMERGENCY_FEED = "emergency_feed"

@dataclass
class OracleHealth:
    oracle_id: str
    status: OracleStatus
    response_time: float
    success_rate: float
    price_deviation: float
    last_update: float
    error_count: int

@dataclass
class FallbackResult:
    strategy_used: FallbackStrategy
    final_price: float
    confidence: float
    sources_used: List[str]
    fallback_reason: str
    recovery_estimate: float

class OracleFallbackSystem:
    """
    Advanced oracle fallback and failure recovery system
    Ensures continuous price feed availability during oracle failures
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.oracle_health: Dict[str, OracleHealth] = {}
        self.fallback_history: List[FallbackResult] = []
        self.emergency_feeds: Dict[str, float] = {}
        
        # Oracle configurations
        self.oracle_configs = {
            'chainlink': {'endpoint': 'https://api.chainlink.com', 'weight': 0.4},
            'band_protocol': {'endpoint': 'https://api.bandprotocol.com', 'weight': 0.3},
            'uniswap_v3': {'endpoint': 'https://api.uniswap.org', 'weight': 0.2},
            'internal_feed': {'endpoint': 'internal', 'weight': 0.1}
        }
        
        # Fallback thresholds
        self.thresholds = {
            'max_response_time': 5.0,  # seconds
            'min_success_rate': 0.95,
            'max_price_deviation': 0.05,  # 5%
            'health_check_interval': 30  # seconds
        }
        
        self.initialize_oracle_health()
        self.start_health_monitoring()
    
    def initialize_oracle_health(self):
        """Initialize health tracking for all oracles"""
        for oracle_id in self.oracle_configs.keys():
            self.oracle_health[oracle_id] = OracleHealth(
                oracle_id=oracle_id,
                status=OracleStatus.HEALTHY,
                response_time=0.0,
                success_rate=1.0,
                price_deviation=0.0,
                last_update=time.time(),
                error_count=0
            )
        
        print("í»¡ï¸ Oracle Fallback System Initialized")
        print(f"Monitoring {len(self.oracle_health)} oracles")
    
    def start_health_monitoring(self):
        """Start background health monitoring"""
        asyncio.create_task(self.continuous_health_monitoring())
    
    async def continuous_health_monitoring(self):
        """Continuously monitor oracle health"""
        while True:
            try:
                await self.perform_health_checks()
                await asyncio.sleep(self.thresholds['health_check_interval'])
            except Exception as e:
                print(f"Health monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retry
    
    async def perform_health_checks(self):
        """Perform health checks on all oracles"""
        check_tasks = []
        
        for oracle_id in self.oracle_health.keys():
            task = asyncio.create_task(self.check_single_oracle(oracle_id))
            check_tasks.append(task)
        
        # Wait for all checks to complete
        await asyncio.gather(*check_tasks, return_exceptions=True)
    
    async def check_single_oracle(self, oracle_id: str):
        """Check health of a single oracle"""
        try:
            start_time = time.time()
            
            # Simulate health check (would be actual API calls)
            await asyncio.sleep(0.1)
            
            response_time = time.time() - start_time
            
            # Update health metrics
            health = self.oracle_health[oracle_id]
            health.response_time = response_time
            health.last_update = time.time()
            
            # Determine status based on metrics
            new_status = self.determine_oracle_status(health)
            health.status = new_status
            
            if new_status != OracleStatus.HEALTHY:
                print(f"âš ï¸ Oracle {oracle_id} status: {new_status.value}")
                
        except Exception as e:
            print(f"âŒ Health check failed for {oracle_id}: {e}")
            self.handle_oracle_error(oracle_id)
    
    def determine_oracle_status(self, health: OracleHealth) -> OracleStatus:
        """Determine oracle status based on health metrics"""
        if health.error_count > 5:
            return OracleStatus.FAILED
        
        if health.response_time > self.thresholds['max_response_time']:
            return OracleStatus.DEGRADED
        
        if health.success_rate < self.thresholds['min_success_rate']:
            return OracleStatus.UNRELIABLE
        
        if health.price_deviation > self.thresholds['max_price_deviation']:
            return OracleStatus.UNRELIABLE
        
        return OracleStatus.HEALTHY
    
    def handle_oracle_error(self, oracle_id: str):
        """Handle oracle error and update health metrics"""
        health = self.oracle_health[oracle_id]
        health.error_count += 1
        health.success_rate = max(0.0, health.success_rate - 0.05)
        
        if health.error_count >= 3:
            health.status = OracleStatus.FAILED
            print(f"í´´ Oracle {oracle_id} marked as FAILED")
    
    async def get_price_with_fallback(self, asset: str) -> FallbackResult:
        """
        Get price with automatic fallback handling
        Returns best available price with fallback strategy details
        """
        try:
            # Try primary oracle first
            primary_price = await self.try_primary_oracle(asset)
            if primary_price['success']:
                return FallbackResult(
                    strategy_used=FallbackStrategy.MULTI_SOURCE_CONSENSUS,
                    final_price=primary_price['price'],
                    confidence=0.95,
                    sources_used=[primary_price['oracle_id']],
                    fallback_reason="primary_oracle_healthy",
                    recovery_estimate=0.0
                )
            
            # Primary oracle failed, use fallback
            fallback_result = await self.execute_fallback_strategy(asset)
            return fallback_result
            
        except Exception as e:
            print(f"âŒ Price fetch failed with all fallbacks: {e}")
            # Ultimate fallback to emergency feed
            return await self.use_emergency_feed(asset, "complete_failure")
    
    async def try_primary_oracle(self, asset: str) -> Dict:
        """Try to get price from primary oracle"""
        primary_oracle = 'chainlink'  # Default primary
        
        health = self.oracle_health.get(primary_oracle)
        if health and health.status == OracleStatus.HEALTHY:
            try:
                price = await self.fetch_from_oracle(primary_oracle, asset)
                return {
                    'success': True,
                    'price': price,
                    'oracle_id': primary_oracle
                }
            except Exception as e:
                print(f"Primary oracle failed: {e}")
                self.handle_oracle_error(primary_oracle)
        
        return {'success': False}
    
    async def execute_fallback_strategy(self, asset: str) -> FallbackResult:
        """Execute fallback strategy for price retrieval"""
        # Get prices from all healthy oracles
        oracle_prices = await self.get_healthy_oracle_prices(asset)
        
        if len(oracle_prices) >= 3:
            # Multiple healthy sources - use consensus
            return await self.multi_source_consensus(oracle_prices, asset)
        elif len(oracle_prices) == 2:
            # Two sources - use weighted average
            return await self.two_source_fallback(oracle_prices, asset)
        elif len(oracle_prices) == 1:
            # Single source - use with caution
            return await self.single_source_fallback(oracle_prices[0], asset)
        else:
            # No healthy oracles - use emergency feed
            return await self.use_emergency_feed(asset, "no_healthy_oracles")
    
    async def get_healthy_oracle_prices(self, asset: str) -> List[Dict]:
        """Get prices from all healthy oracles"""
        healthy_prices = []
        
        for oracle_id, health in self.oracle_health.items():
            if health.status in [OracleStatus.HEALTHY, OracleStatus.DEGRADED]:
                try:
                    price = await self.fetch_from_oracle(oracle_id, asset)
                    healthy_prices.append({
                        'oracle_id': oracle_id,
                        'price': price,
                        'health': health
                    })
                except Exception as e:
                    print(f"Oracle {oracle_id} fetch failed: {e}")
                    self.handle_oracle_error(oracle_id)
        
        return healthy_prices
    
    async def multi_source_consensus(self, oracle_prices: List[Dict], asset: str) -> FallbackResult:
        """Use multi-source consensus for price determination"""
        prices = [op['price'] for op in oracle_prices]
        oracle_ids = [op['oracle_id'] for op in oracle_prices]
        
        # Remove outliers using IQR method
        filtered_prices = self.remove_price_outliers(prices)
        
        if len(filtered_prices) >= 2:
            # Use median of filtered prices
            final_price = median(filtered_prices)
            confidence = 0.85
        else:
            # Fall back to simple median
            final_price = median(prices)
            confidence = 0.75
        
        return FallbackResult(
            strategy_used=FallbackStrategy.MULTI_SOURCE_CONSENSUS,
            final_price=final_price,
            confidence=confidence,
            sources_used=oracle_ids,
            fallback_reason="multi_source_consensus",
            recovery_estimate=0.0
        )
    
    async def two_source_fallback(self, oracle_prices: List[Dict], asset: str) -> FallbackResult:
        """Fallback strategy for two available sources"""
        prices = [op['price'] for op in oracle_prices]
        oracle_ids = [op['oracle_id'] for op in oracle_prices]
        
        # Calculate weighted average based on oracle health
        weights = []
        for op in oracle_prices:
            weight = self.calculate_oracle_weight(op['health'])
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Calculate weighted average
        final_price = sum(p * w for p, w in zip(prices, normalized_weights))
        
        # Confidence based on price agreement
        price_diff = abs(prices[0] - prices[1]) / min(prices)
        confidence = max(0.7, 1.0 - price_diff * 10)
        
        return FallbackResult(
            strategy_used=FallbackStrategy.TIME_WEIGHTED_AVERAGE,
            final_price=final_price,
            confidence=confidence,
            sources_used=oracle_ids,
            fallback_reason="two_source_fallback",
            recovery_estimate=0.0
        )
    
    async def single_source_fallback(self, oracle_price: Dict, asset: str) -> FallbackResult:
        """Fallback strategy for single available source"""
        confidence = 0.6  # Low confidence for single source
        
        # Additional validation for single source
        try:
            # Cross-check with historical data
            historical_validation = await self.validate_against_history(
                oracle_price['price'], asset
            )
            if historical_validation['valid']:
                confidence = 0.7
        except:
            pass  # Historical validation failed, use base confidence
        
        return FallbackResult(
            strategy_used=FallbackStrategy.LAST_KNOWN_GOOD,
            final_price=oracle_price['price'],
            confidence=confidence,
            sources_used=[oracle_price['oracle_id']],
            fallback_reason="single_source_available",
            recovery_estimate=60.0  # 1 minute recovery estimate
        )
    
    async def use_emergency_feed(self, asset: str, reason: str) -> FallbackResult:
        """Use emergency price feed as last resort"""
        emergency_price = await self.get_emergency_price(asset)
        
        return FallbackResult(
            strategy_used=FallbackStrategy.EMERGENCY_FEED,
            final_price=emergency_price,
            confidence=0.5,  # Low confidence for emergency feed
            sources_used=['emergency_feed'],
            fallback_reason=reason,
            recovery_estimate=300.0  # 5 minute recovery estimate
        )
    
    async def fetch_from_oracle(self, oracle_id: str, asset: str) -> float:
        """Fetch price from specific oracle"""
        config = self.oracle_configs.get(oracle_id, {})
        
        if oracle_id == 'internal_feed':
            # Internal feed simulation
            return await self.get_internal_price(asset)
        
        # Simulate API call to external oracle
        await asyncio.sleep(0.05)  # Simulate network latency
        
        # Mock price data - in practice would call actual API
        base_prices = {
            'ETH': 2500.0,
            'BTC': 45000.0,
            'SOL': 100.0,
            'AVAX': 40.0
        }
        
        base_price = base_prices.get(asset, 100.0)
        
        # Add some random variation
        variation = random.uniform(-0.01, 0.01)  # Â±1% variation
        return base_price * (1 + variation)
    
    async def get_internal_price(self, asset: str) -> float:
        """Get price from internal calculation (DEX prices, etc.)"""
        # Simulate internal price calculation
        await asyncio.sleep(0.02)
        
        base_prices = {
            'ETH': 2500.0,
            'BTC': 45000.0,
            'SOL': 100.0,
            'AVAX': 40.0
        }
        
        base_price = base_prices.get(asset, 100.0)
        variation = random.uniform(-0.02, 0.02)  # Internal feed has more variation
        return base_price * (1 + variation)
    
    async def get_emergency_price(self, asset: str) -> float:
        """Get emergency price from backup sources"""
        # Could use:
        # 1. CEX prices via API
        # 2. Historical averages
        # 3. Manual input
        # 4. Cross-chain price feeds
        
        base_prices = {
            'ETH': 2500.0,
            'BTC': 45000.0,
            'SOL': 100.0,
            'AVAX': 40.0
        }
        
        return base_prices.get(asset, 100.0)
    
    def remove_price_outliers(self, prices: List[float]) -> List[float]:
        """Remove price outliers using IQR method"""
        if len(prices) < 3:
            return prices
        
        sorted_prices = sorted(prices)
        q1 = np.percentile(sorted_prices, 25)
        q3 = np.percentile(sorted_prices, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [p for p in prices if lower_bound <= p <= upper_bound]
    
    def calculate_oracle_weight(self, health: OracleHealth) -> float:
        """Calculate weight for oracle based on health metrics"""
        base_weight = self.oracle_configs.get(health.oracle_id, {}).get('weight', 0.1)
        
        # Adjust based on health metrics
        response_factor = max(0.0, 1.0 - (health.response_time / self.thresholds['max_response_time']))
        success_factor = health.success_rate
        deviation_factor = max(0.0, 1.0 - (health.price_deviation / self.thresholds['max_price_deviation']))
        
        # Combined adjustment
        health_adjustment = (response_factor + success_factor + deviation_factor) / 3.0
        
        return base_weight * health_adjustment
    
    async def validate_against_history(self, price: float, asset: str) -> Dict:
        """Validate price against historical data"""
        # This would compare against recent price history
        # For now, return simple validation
        return {
            'valid': True,
            'deviation': 0.02,  # 2% deviation from expected
            'confidence': 0.8
        }
    
    def get_system_health_report(self) -> Dict:
        """Get comprehensive system health report"""
        healthy_count = sum(1 for h in self.oracle_health.values() 
                          if h.status == OracleStatus.HEALTHY)
        total_count = len(self.oracle_health)
        
        avg_response_time = np.mean([h.response_time for h in self.oracle_health.values()])
        avg_success_rate = np.mean([h.success_rate for h in self.oracle_health.values()])
        
        return {
            'total_oracles': total_count,
            'healthy_oracles': healthy_count,
            'health_ratio': healthy_count / total_count,
            'average_response_time': avg_response_time,
            'average_success_rate': avg_success_rate,
            'recent_fallbacks': len([f for f in self.fallback_history 
                                   if time.time() - f.recovery_estimate < 3600]),
            'oracle_details': {
                oracle_id: {
                    'status': health.status.value,
                    'response_time': health.response_time,
                    'success_rate': health.success_rate,
                    'error_count': health.error_count
                }
                for oracle_id, health in self.oracle_health.items()
            }
        }
    
    async def simulate_oracle_failure(self, oracle_id: str):
        """Simulate oracle failure for testing"""
        if oracle_id in self.oracle_health:
            health = self.oracle_health[oracle_id]
            health.status = OracleStatus.FAILED
            health.error_count = 10
            print(f"í´´ Simulated failure for oracle: {oracle_id}")
    
    async def simulate_oracle_recovery(self, oracle_id: str):
        """Simulate oracle recovery for testing"""
        if oracle_id in self.oracle_health:
            health = self.oracle_health[oracle_id]
            health.status = OracleStatus.HEALTHY
            health.error_count = 0
            health.success_rate = 1.0
            print(f"âœ… Simulated recovery for oracle: {oracle_id}")

# Example usage
async def main():
    """Example usage of Oracle Fallback System"""
    fallback_system = OracleFallbackSystem()
    
    # Wait for initial health checks
    await asyncio.sleep(1)
    
    # Get price with fallback protection
    assets = ['ETH', 'BTC', 'SOL']
    
    for asset in assets:
        result = await fallback_system.get_price_with_fallback(asset)
        
        print(f"\ní²° {asset} Price Result:")
        print(f"  Price: ${result.final_price:,.2f}")
        print(f"  Strategy: {result.strategy_used.value}")
        print(f"  Confidence: {result.confidence:.1%}")
        print(f"  Sources: {', '.join(result.sources_used)}")
        print(f"  Fallback Reason: {result.fallback_reason}")
    
    # Get system health report
    health_report = fallback_system.get_system_health_report()
    print(f"\ní»¡ï¸ System Health Report:")
    print(f"  Healthy Oracles: {health_report['healthy_oracles']}/{health_report['total_oracles']}")
    print(f"  Health Ratio: {health_report['health_ratio']:.1%}")
    print(f"  Avg Response Time: {health_report['average_response_time']:.3f}s")
    
    # Simulate an oracle failure and see fallback in action
    print(f"\ní´¥ Simulating Chainlink oracle failure...")
    await fallback_system.simulate_oracle_failure('chainlink')
    
    # Get price after simulated failure
    eth_result = await fallback_system.get_price_with_fallback('ETH')
    print(f"  Post-failure strategy: {eth_result.strategy_used.value}")
    print(f"  Sources used: {', '.join(eth_result.sources_used)}")

if __name__ == "__main__":
    import random
    asyncio.run(main())
