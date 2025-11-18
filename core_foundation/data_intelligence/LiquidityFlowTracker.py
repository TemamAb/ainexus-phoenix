#!/usr/bin/env python3
"""
Enterprise-Grade Liquidity Flow Tracking Engine
Real-time monitoring of cross-DEX liquidity movements with predictive analytics
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from web3 import Web3
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiquidityFlow:
    pool_address: str
    token_in: str
    token_out: str
    amount: Decimal
    direction: str
    timestamp: int
    dex: str
    block_number: int
    transaction_hash: str
    gas_used: int
    effective_price: Decimal

@dataclass
class FlowPattern:
    token_pair: Tuple[str, str]
    direction: str
    average_amount: Decimal
    frequency: Decimal
    volatility: Decimal
    confidence: float

class LiquidityFlowTracker:
    def __init__(self, web3_providers: Dict[str, Web3], dex_routers: List[str], 
                 config: Dict = None):
        self.web3_providers = web3_providers
        self.dex_routers = dex_routers
        self.config = config or {
            'flow_threshold': Decimal('50000'),  # $50k minimum
            'analysis_window': 3600,  # 1 hour
            'prediction_horizon': 300,  # 5 minutes
            'anomaly_threshold': 2.5  # Z-score threshold
        }
        
        self.flow_history: List[LiquidityFlow] = []
        self.pool_metrics: Dict[str, Dict] = {}
        self.flow_patterns: List[FlowPattern] = []
        self.anomaly_detector = ZScoreAnomalyDetector()
        self.pattern_analyzer = PatternAnalyzer()
        
        # Performance monitoring
        self.metrics = {
            'total_flows_processed': 0,
            'anomalies_detected': 0,
            'prediction_accuracy': 0.0
        }
        
        logger.info("LiquidityFlowTracker initialized with %d DEX routers", len(dex_routers))

    async def start_monitoring(self):
        """Start real-time liquidity flow monitoring"""
        logger.info("Starting liquidity flow monitoring")
        try:
            monitoring_tasks = []
            for chain_name, web3 in self.web3_providers.items():
                task = asyncio.create_task(
                    self._monitor_chain_flows(chain_name, web3)
                )
                monitoring_tasks.append(task)
            
            # Start pattern analysis in background
            analysis_task = asyncio.create_task(self._continuous_pattern_analysis())
            monitoring_tasks.append(analysis_task)
            
            await asyncio.gather(*monitoring_tasks)
            
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            raise

    async def _monitor_chain_flows(self, chain: str, web3: Web3):
        """Monitor liquidity flows for a specific blockchain"""
        logger.info(f"Monitoring liquidity flows on {chain}")
        
        last_block = web3.eth.block_number
        while True:
            try:
                current_block = web3.eth.block_number
                if current_block > last_block:
                    for block_num in range(last_block + 1, current_block + 1):
                        await self._process_block(chain, web3, block_num)
                    last_block = current_block
                
                await asyncio.sleep(2)  # Controlled polling
                
            except Exception as e:
                logger.error(f"Chain monitoring error on {chain}: {e}")
                await asyncio.sleep(10)

    async def _process_block(self, chain: str, web3: Web3, block_number: int):
        """Process a single block for liquidity flows"""
        try:
            block = web3.eth.get_block(block_number, full_transactions=True)
            
            for tx in block.transactions:
                if self._is_dex_transaction(tx):
                    flow = await self._extract_liquidity_flow(chain, web3, tx, block)
                    if flow and flow.amount >= self.config['flow_threshold']:
                        self.flow_history.append(flow)
                        self.metrics['total_flows_processed'] += 1
                        
                        # Check for anomalies
                        if self._detect_anomaly(flow):
                            self.metrics['anomalies_detected'] += 1
                            logger.warning(f"Anomalous flow detected: {flow}")
                        
        except Exception as e:
            logger.error(f"Block processing error: {e}")

    def _is_dex_transaction(self, tx) -> bool:
        """Check if transaction interacts with DEX router"""
        return tx.to and tx.to.lower() in [r.lower() for r in self.dex_routers]

    async def _extract_liquidity_flow(self, chain: str, web3: Web3, tx, block) -> Optional[LiquidityFlow]:
        """Extract liquidity flow information from transaction"""
        try:
            # Parse transaction receipt for detailed info
            receipt = web3.eth.get_transaction_receipt(tx.hash)
            
            # This would involve complex DEX-specific parsing
            # Simplified implementation - real version would use contract ABIs
            flow = LiquidityFlow(
                pool_address=tx.to,
                token_in="",  # Would be extracted from calldata
                token_out="",  # Would be extracted from calldata
                amount=Decimal(str(web3.from_wei(tx.value, 'ether'))),
                direction="in",  # Would be determined from swap direction
                timestamp=block.timestamp,
                dex=self._identify_dex(tx.to),
                block_number=block.number,
                transaction_hash=tx.hash.hex(),
                gas_used=receipt.gasUsed,
                effective_price=Decimal(str(web3.from_wei(tx.gasPrice * receipt.gasUsed, 'ether')))
            )
            
            return flow
            
        except Exception as e:
            logger.error(f"Flow extraction error: {e}")
            return None

    def _identify_dex(self, address: str) -> str:
        """Identify which DEX the transaction interacts with"""
        dex_mappings = {
            '0x7a250d5630b4cf539739df2c5dacb4c659f2488d': 'Uniswap V2',
            '0xe592427a0aece92de3edee1f18e0157c05861564': 'Uniswap V3',
            '0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f': 'SushiSwap',
        }
        return dex_mappings.get(address.lower(), 'Unknown DEX')

    def _detect_anomaly(self, flow: LiquidityFlow) -> bool:
        """Detect anomalous liquidity flows using statistical methods"""
        recent_flows = self._get_recent_flows(flow.token_in, flow.token_out, 3600)
        if len(recent_flows) < 10:  # Need sufficient data
            return False
            
        amounts = [f.amount for f in recent_flows]
        return self.anomaly_detector.detect(amounts, flow.amount)

    def _get_recent_flows(self, token_in: str, token_out: str, window_seconds: int) -> List[LiquidityFlow]:
        """Get recent flows for a token pair within time window"""
        cutoff = datetime.now().timestamp() - window_seconds
        return [
            f for f in self.flow_history
            if f.timestamp >= cutoff and 
            f.token_in == token_in and 
            f.token_out == token_out
        ]

    async def _continuous_pattern_analysis(self):
        """Continuous analysis of liquidity flow patterns"""
        while True:
            try:
                self.flow_patterns = self.pattern_analyzer.analyze_patterns(self.flow_history)
                await asyncio.sleep(300)  # Analyze every 5 minutes
            except Exception as e:
                logger.error(f"Pattern analysis error: {e}")
                await asyncio.sleep(60)

    def predict_liquidity_shocks(self, token_pair: Tuple[str, str]) -> List[Dict]:
        """Predict potential liquidity shocks for a token pair"""
        recent_flows = self._get_recent_flows(token_pair[0], token_pair[1], 3600)
        if not recent_flows:
            return []
            
        # Use time series analysis for prediction
        predictions = []
        flow_series = [float(f.amount) for f in recent_flows]
        
        # Simple moving average crossover detection
        if len(flow_series) >= 20:
            short_ma = np.mean(flow_series[-10:])
            long_ma = np.mean(flow_series[-20:])
            
            if short_ma > long_ma * 1.5:  # Significant uptick
                predictions.append({
                    'type': 'liquidity_influx',
                    'confidence': min(0.9, (short_ma - long_ma) / long_ma),
                    'magnitude': Decimal(str(short_ma - long_ma)),
                    'timeframe': 'short_term'
                })
                
        return predictions

    def get_flow_metrics(self, timeframe_hours: int = 24) -> Dict:
        """Get comprehensive flow metrics"""
        cutoff = datetime.now().timestamp() - (timeframe_hours * 3600)
        recent_flows = [f for f in self.flow_history if f.timestamp >= cutoff]
        
        if not recent_flows:
            return {}
            
        amounts = [float(f.amount) for f in recent_flows]
        
        return {
            'total_volume': Decimal(str(sum(amounts))),
            'average_flow': Decimal(str(np.mean(amounts))),
            'flow_volatility': Decimal(str(np.std(amounts))),
            'flow_count': len(recent_flows),
            'top_dexes': self._get_top_dexes(recent_flows),
            'anomaly_rate': self.metrics['anomalies_detected'] / max(1, self.metrics['total_flows_processed'])
        }

    def _get_top_dexes(self, flows: List[LiquidityFlow]) -> List[Dict]:
        """Get top DEXs by volume"""
        dex_volumes = {}
        for flow in flows:
            dex_volumes[flow.dex] = dex_volumes.get(flow.dex, 0) + float(flow.amount)
            
        return [
            {'dex': dex, 'volume': Decimal(str(volume))}
            for dex, volume in sorted(dex_volumes.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

class ZScoreAnomalyDetector:
    """Statistical anomaly detection using Z-scores"""
    
    def detect(self, historical_data: List[float], current_value: float, threshold: float = 2.5) -> bool:
        if len(historical_data) < 5:
            return False
            
        mean = np.mean(historical_data)
        std = np.std(historical_data)
        
        if std == 0:
            return False
            
        z_score = abs(current_value - mean) / std
        return z_score > threshold

class PatternAnalyzer:
    """Advanced pattern analysis for liquidity flows"""
    
    def analyze_patterns(self, flows: List[LiquidityFlow]) -> List[FlowPattern]:
        # Implement sophisticated pattern recognition
        # This would include ML-based pattern detection in production
        return []

# Factory function for dependency injection
def create_liquidity_tracker(web3_providers: Dict[str, Web3], 
                           dex_routers: List[str],
                           config: Dict = None) -> LiquidityFlowTracker:
    return LiquidityFlowTracker(web3_providers, dex_routers, config)

if __name__ == "__main__":
    # Example usage
    tracker = LiquidityFlowTracker({}, [])
    print("LiquidityFlowTracker initialized successfully")
