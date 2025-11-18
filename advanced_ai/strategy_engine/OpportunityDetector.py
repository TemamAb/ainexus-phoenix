"""
AI-NEXUS v5.0 - OPPORTUNITY DETECTOR MODULE
Advanced Multi-Dimensional Arbitrage and Market Inefficiency Detection
Real-time opportunity identification across multiple protocols and chains
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import asyncio
import warnings
warnings.filterwarnings('ignore')

class OpportunityType(Enum):
    SIMPLE_ARBITRAGE = "simple_arbitrage"
    TRIANGULAR_ARBITRAGE = "triangular_arbitrage"
    CROSS_CHAIN_ARBITRAGE = "cross_chain_arbitrage"
    FUNDING_RATE_ARBITRAGE = "funding_rate_arbitrage"
    LIQUIDITY_MINING_ARBITRAGE = "liquidity_mining_arbitrage"
    MEV_ARBITRAGE = "mev_arbitrage"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    VOLATILITY_ARBITRAGE = "volatility_arbitrage"

class OpportunityConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ArbitrageOpportunity:
    opportunity_id: str
    opportunity_type: OpportunityType
    timestamp: datetime
    assets_involved: List[str]
    protocols_involved: List[str]
    expected_profit: float
    expected_profit_percentage: float
    confidence: OpportunityConfidence
    execution_complexity: float
    time_sensitivity: timedelta
    risk_metrics: Dict[str, float]
    required_capital: float
    metadata: Dict[str, Any]

@dataclass
class MarketInefficiency:
    inefficiency_id: str
    timestamp: datetime
    asset_pair: Tuple[str, str]
    inefficiency_type: str
    magnitude: float
    duration: timedelta
    cause: str
    persistence_score: float
    metadata: Dict[str, Any]

class OpportunityDetector:
    """
    Advanced multi-dimensional opportunity detection system
    Identifies arbitrage opportunities and market inefficiencies in real-time
    """
    
    def __init__(self):
        self.detected_opportunities = deque(maxlen=10000)
        self.market_inefficiencies = deque(maxlen=5000)
        self.opportunity_models = {}
        
        # Detection parameters
        self.detection_params = {
            'min_profit_threshold': 0.001,  # 0.1% minimum profit
            'max_execution_time': timedelta(seconds=30),
            'min_confidence_threshold': 0.6,
            'max_slippage_tolerance': 0.005,  # 0.5%
            'gas_cost_multiplier': 1.2,
            'risk_adjustment_factor': 0.8,
            'lookback_period': timedelta(minutes=5)
        }
        
        # Protocol configurations
        self.protocol_configs = {
            'uniswap_v3': {'fee_tier': 0.003, 'gas_estimate': 150000},
            'sushiswap': {'fee_tier': 0.003, 'gas_estimate': 180000},
            'curve': {'fee_tier': 0.0004, 'gas_estimate': 250000},
            'balancer': {'fee_tier': 0.002, 'gas_estimate': 220000},
            'pancakeswap': {'fee_tier': 0.0025, 'gas_estimate': 160000}
        }
        
        # Performance tracking
        self.performance_metrics = {
            'opportunities_detected': 0,
            'profitable_opportunities': 0,
            'false_positives': 0,
            'avg_detection_time': 0.0,
            'success_rate': 1.0
        }
        
        # Initialize detection engines
        self._initialize_detection_engines()
        self._initialize_risk_models()
    
    def _initialize_detection_engines(self):
        """Initialize specialized detection engines"""
        
        self.opportunity_models = {
            'simple_arbitrage': SimpleArbitrageEngine(),
            'triangular_arbitrage': TriangularArbitrageEngine(),
            'cross_chain_arbitrage': CrossChainArbitrageEngine(),
            'funding_rate_arbitrage': FundingRateArbitrageEngine(),
            'statistical_arbitrage': StatisticalArbitrageEngine(),
            'mev_arbitrage': MEVArbitrageEngine()
        }
        
        # Market data aggregator
        self.market_aggregator = MarketDataAggregator()
        
        # Gas price predictor
        self.gas_predictor = GasPricePredictor()
    
    def _initialize_risk_models(self):
        """Initialize risk assessment models"""
        
        self.risk_models = {
            'slippage_risk': SlippageRiskModel(),
            'impermanent_loss_risk': ImpermanentLossRiskModel(),
            'smart_contract_risk': SmartContractRiskModel(),
            'liquidity_risk': LiquidityRiskModel(),
            'front_running_risk': FrontRunningRiskModel()
        }
    
    async def detect_opportunities(self, 
                                 market_data: Dict[str, Any],
                                 protocol_data: Dict[str, Any],
                                 chain_data: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Main opportunity detection method"""
        
        detection_start = datetime.now()
        all_opportunities = []
        
        # Simple arbitrage opportunities
        simple_arb_opps = await self._detect_simple_arbitrage(market_data, protocol_data)
        all_opportunities.extend(simple_arb_opps)
        
        # Triangular arbitrage opportunities
        triangular_arb_opps = await self._detect_triangular_arbitrage(market_data, protocol_data)
        all_opportunities.extend(triangular_arb_opps)
        
        # Cross-chain arbitrage opportunities
        cross_chain_opps = await self._detect_cross_chain_arbitrage(market_data, chain_data)
        all_opportunities.extend(cross_chain_opps)
        
        # Funding rate arbitrage opportunities
        funding_opps = await self._detect_funding_rate_arbitrage(market_data)
        all_opportunities.extend(funding_opps)
        
        # Statistical arbitrage opportunities
        statistical_opps = await self._detect_statistical_arbitrage(market_data)
        all_opportunities.extend(statistical_opps)
        
        # MEV opportunities
        mev_opps = await self._detect_mev_opportunities(market_data, protocol_data)
        all_opportunities.extend(mev_opps)
        
        # Filter and rank opportunities
        filtered_opportunities = await self._filter_opportunities(all_opportunities)
        
        # Update detection history
        for opportunity in filtered_opportunities:
            self.detected_opportunities.append(opportunity)
            self.performance_metrics['opportunities_detected'] += 1
        
        # Update performance metrics
        detection_time = (datetime.now() - detection_start).total_seconds()
        self._update_detection_metrics(detection_time, len(filtered_opportunities))
        
        return filtered_opportunities
    
    async def _detect_simple_arbitrage(self, 
                                     market_data: Dict[str, Any],
                                     protocol_data: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Detect simple two-point arbitrage opportunities"""
        
        opportunities = []
        engine = self.opportunity_models['simple_arbitrage']
        
        try:
            # Get price data across different protocols
            price_matrix = await self.market_aggregator.build_price_matrix(market_data)
            
            # Find arbitrage opportunities
            arb_opportunities = await engine.find_opportunities(price_matrix, protocol_data)
            
            for arb in arb_opportunities:
                # Calculate expected profit
                expected_profit = await self._calculate_expected_profit(arb, 'simple_arbitrage')
                
                if expected_profit > self.detection_params['min_profit_threshold']:
                    # Assess risk
                    risk_metrics = await self._assess_opportunity_risk(arb, 'simple_arbitrage')
                    
                    # Calculate confidence
                    confidence = await self._calculate_confidence(arb, risk_metrics, expected_profit)
                    
                    opportunity = ArbitrageOpportunity(
                        opportunity_id=f"arb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        opportunity_type=OpportunityType.SIMPLE_ARBITRAGE,
                        timestamp=datetime.now(),
                        assets_involved=arb['assets'],
                        protocols_involved=arb['protocols'],
                        expected_profit=expected_profit,
                        expected_profit_percentage=expected_profit,
                        confidence=confidence,
                        execution_complexity=arb.get('complexity', 0.3),
                        time_sensitivity=timedelta(seconds=15),
                        risk_metrics=risk_metrics,
                        required_capital=arb.get('required_capital', 1000),
                        metadata={
                            'price_discrepancy': arb['price_diff'],
                            'liquidity_available': arb.get('liquidity', 0),
                            'gas_estimate': arb.get('gas_estimate', 0)
                        }
                    )
                    
                    opportunities.append(opportunity)
                    print(f"Simple arbitrage detected: {expected_profit:.3%} profit")
        
        except Exception as e:
            print(f"Error in simple arbitrage detection: {e}")
        
        return opportunities
    
    async def _detect_triangular_arbitrage(self,
                                         market_data: Dict[str, Any],
                                         protocol_data: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Detect triangular arbitrage opportunities"""
        
        opportunities = []
        engine = self.opportunity_models['triangular_arbitrage']
        
        try:
            # Get triangular price data
            triangular_data = await self.market_aggregator.build_triangular_matrix(market_data)
            
            # Find triangular arbitrage opportunities
            tri_arb_opportunities = await engine.find_triangular_opportunities(triangular_data)
            
            for arb in tri_arb_opportunities:
                expected_profit = await self._calculate_expected_profit(arb, 'triangular_arbitrage')
                
                if expected_profit > self.detection_params['min_profit_threshold']:
                    risk_metrics = await self._assess_opportunity_risk(arb, 'triangular_arbitrage')
                    confidence = await self._calculate_confidence(arb, risk_metrics, expected_profit)
                    
                    opportunity = ArbitrageOpportunity(
                        opportunity_id=f"tri_arb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        opportunity_type=OpportunityType.TRIANGULAR_ARBITRAGE,
                        timestamp=datetime.now(),
                        assets_involved=arb['assets'],
                        protocols_involved=arb['protocols'],
                        expected_profit=expected_profit,
                        expected_profit_percentage=expected_profit,
                        confidence=confidence,
                        execution_complexity=arb.get('complexity', 0.6),
                        time_sensitivity=timedelta(seconds=10),
                        risk_metrics=risk_metrics,
                        required_capital=arb.get('required_capital', 5000),
                        metadata={
                            'triangle_path': arb['path'],
                            'exchange_rates': arb['rates'],
                            'transaction_count': arb.get('tx_count', 3)
                        }
                    )
                    
                    opportunities.append(opportunity)
                    print(f"Triangular arbitrage detected: {expected_profit:.3%} profit")
        
        except Exception as e:
            print(f"Error in triangular arbitrage detection: {e}")
        
        return opportunities
    
    async def _detect_cross_chain_arbitrage(self,
                                          market_data: Dict[str, Any],
                                          chain_data: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Detect cross-chain arbitrage opportunities"""
        
        opportunities = []
        engine = self.opportunity_models['cross_chain_arbitrage']
        
        try:
            # Get cross-chain price data
            cross_chain_data = await self.market_aggregator.build_cross_chain_matrix(market_data, chain_data)
            
            # Find cross-chain opportunities
            cross_chain_opps = await engine.find_cross_chain_opportunities(cross_chain_data)
            
            for opp in cross_chain_opps:
                expected_profit = await self._calculate_expected_profit(opp, 'cross_chain_arbitrage')
                
                if expected_profit > self.detection_params['min_profit_threshold'] * 2:  # Higher threshold for cross-chain
                    risk_metrics = await self._assess_opportunity_risk(opp, 'cross_chain_arbitrage')
                    confidence = await self._calculate_confidence(opp, risk_metrics, expected_profit)
                    
                    opportunity = ArbitrageOpportunity(
                        opportunity_id=f"cross_chain_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        opportunity_type=OpportunityType.CROSS_CHAIN_ARBITRAGE,
                        timestamp=datetime.now(),
                        assets_involved=opp['assets'],
                        protocols_involved=opp['protocols'],
                        expected_profit=expected_profit,
                        expected_profit_percentage=expected_profit,
                        confidence=confidence,
                        execution_complexity=opp.get('complexity', 0.8),
                        time_sensitivity=timedelta(minutes=2),
                        risk_metrics=risk_metrics,
                        required_capital=opp.get('required_capital', 10000),
                        metadata={
                            'chains_involved': opp['chains'],
                            'bridge_fees': opp.get('bridge_fees', 0),
                            'bridge_risks': opp.get('bridge_risks', {})
                        }
                    )
                    
                    opportunities.append(opportunity)
                    print(f"Cross-chain arbitrage detected: {expected_profit:.3%} profit")
        
        except Exception as e:
            print(f"Error in cross-chain arbitrage detection: {e}")
        
        return opportunities
    
    async def _detect_funding_rate_arbitrage(self, market_data: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Detect funding rate arbitrage opportunities"""
        
        opportunities = []
        engine = self.opportunity_models['funding_rate_arbitrage']
        
        try:
            # Get funding rate data
            funding_data = market_data.get('funding_rates', {})
            
            # Find funding rate opportunities
            funding_opps = await engine.find_funding_opportunities(funding_data)
            
            for opp in funding_opps:
                expected_profit = await self._calculate_expected_profit(opp, 'funding_rate_arbitrage')
                
                if expected_profit > self.detection_params['min_profit_threshold']:
                    risk_metrics = await self._assess_opportunity_risk(opp, 'funding_rate_arbitrage')
                    confidence = await self._calculate_confidence(opp, risk_metrics, expected_profit)
                    
                    opportunity = ArbitrageOpportunity(
                        opportunity_id=f"funding_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        opportunity_type=OpportunityType.FUNDING_RATE_ARBITRAGE,
                        timestamp=datetime.now(),
                        assets_involved=opp['assets'],
                        protocols_involved=opp['protocols'],
                        expected_profit=expected_profit,
                        expected_profit_percentage=expected_profit,
                        confidence=confidence,
                        execution_complexity=opp.get('complexity', 0.5),
                        time_sensitivity=timedelta(hours=8),  # Funding periods
                        risk_metrics=risk_metrics,
                        required_capital=opp.get('required_capital', 20000),
                        metadata={
                            'funding_rates': opp['rates'],
                            'next_funding_time': opp.get('next_funding', None),
                            'basis_risk': opp.get('basis_risk', 0)
                        }
                    )
                    
                    opportunities.append(opportunity)
                    print(f"Funding rate arbitrage detected: {expected_profit:.3%} profit")
        
        except Exception as e:
            print(f"Error in funding rate arbitrage detection: {e}")
        
        return opportunities
    
    async def _detect_statistical_arbitrage(self, market_data: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Detect statistical arbitrage opportunities"""
        
        opportunities = []
        engine = self.opportunity_models['statistical_arbitrage']
        
        try:
            # Get historical price data for pairs
            historical_data = market_data.get('historical_prices', {})
            
            # Find statistical arbitrage opportunities
            stat_arb_opps = await engine.find_statistical_opportunities(historical_data)
            
            for opp in stat_arb_opps:
                expected_profit = await self._calculate_expected_profit(opp, 'statistical_arbitrage')
                
                if expected_profit > self.detection_params['min_profit_threshold']:
                    risk_metrics = await self._assess_opportunity_risk(opp, 'statistical_arbitrage')
                    confidence = await self._calculate_confidence(opp, risk_metrics, expected_profit)
                    
                    opportunity = ArbitrageOpportunity(
                        opportunity_id=f"stat_arb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        opportunity_type=OpportunityType.STATISTICAL_ARBITRAGE,
                        timestamp=datetime.now(),
                        assets_involved=opp['assets'],
                        protocols_involved=opp['protocols'],
                        expected_profit=expected_profit,
                        expected_profit_percentage=expected_profit,
                        confidence=confidence,
                        execution_complexity=opp.get('complexity', 0.7),
                        time_sensitivity=timedelta(hours=24),
                        risk_metrics=risk_metrics,
                        required_capital=opp.get('required_capital', 15000),
                        metadata={
                            'z_score': opp.get('z_score', 0),
                            'half_life': opp.get('half_life', 0),
                            'correlation_strength': opp.get('correlation', 0)
                        }
                    )
                    
                    opportunities.append(opportunity)
                    print(f"Statistical arbitrage detected: {expected_profit:.3%} profit")
        
        except Exception as e:
            print(f"Error in statistical arbitrage detection: {e}")
        
        return opportunities
    
    async def _detect_mev_opportunities(self,
                                      market_data: Dict[str, Any],
                                      protocol_data: Dict[str, Any]) -> List[ArbitrageOpportunity]:
        """Detect MEV (Miner Extractable Value) opportunities"""
        
        opportunities = []
        engine = self.opportunity_models['mev_arbitrage']
        
        try:
            # Get MEV-related data
            mev_data = {
                'pending_transactions': market_data.get('pending_txs', []),
                'mempool_data': market_data.get('mempool', {}),
                'block_data': market_data.get('block_info', {})
            }
            
            # Find MEV opportunities
            mev_opps = await engine.find_mev_opportunities(mev_data, protocol_data)
            
            for opp in mev_opps:
                expected_profit = await self._calculate_expected_profit(opp, 'mev_arbitrage')
                
                if expected_profit > self.detection_params['min_profit_threshold']:
                    risk_metrics = await self._assess_opportunity_risk(opp, 'mev_arbitrage')
                    confidence = await self._calculate_confidence(opp, risk_metrics, expected_profit)
                    
                    opportunity = ArbitrageOpportunity(
                        opportunity_id=f"mev_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        opportunity_type=OpportunityType.MEV_ARBITRAGE,
                        timestamp=datetime.now(),
                        assets_involved=opp['assets'],
                        protocols_involved=opp['protocols'],
                        expected_profit=expected_profit,
                        expected_profit_percentage=expected_profit,
                        confidence=confidence,
                        execution_complexity=opp.get('complexity', 0.9),
                        time_sensitivity=timedelta(seconds=5),
                        risk_metrics=risk_metrics,
                        required_capital=opp.get('required_capital', 5000),
                        metadata={
                            'mev_type': opp.get('mev_type', 'unknown'),
                            'competition_level': opp.get('competition', 0),
                            'bundle_requirements': opp.get('bundle_req', {})
                        }
                    )
                    
                    opportunities.append(opportunity)
                    print(f"MEV opportunity detected: {expected_profit:.3%} profit")
        
        except Exception as e:
            print(f"Error in MEV opportunity detection: {e}")
        
        return opportunities
    
    async def _calculate_expected_profit(self, opportunity: Dict[str, Any], 
                                       opportunity_type: str) -> float:
        """Calculate expected profit after accounting for costs"""
        
        gross_profit = opportunity.get('gross_profit', 0)
        
        # Calculate costs
        gas_cost = await self._estimate_gas_cost(opportunity, opportunity_type)
        slippage_cost = await self._estimate_slippage_cost(opportunity)
        protocol_fees = await self._calculate_protocol_fees(opportunity)
        
        total_costs = gas_cost + slippage_cost + protocol_fees
        
        # Risk adjustment
        risk_adjustment = self.detection_params['risk_adjustment_factor']
        net_profit = (gross_profit - total_costs) * risk_adjustment
        
        return max(0.0, net_profit)
    
    async def _estimate_gas_cost(self, opportunity: Dict[str, Any], 
                               opportunity_type: str) -> float:
        """Estimate gas costs for opportunity execution"""
        
        # Get current gas price
        current_gas_price = await self.gas_predictor.get_current_gas_price()
        
        # Estimate gas usage based on opportunity type
        base_gas_estimates = {
            'simple_arbitrage': 200000,
            'triangular_arbitrage': 350000,
            'cross_chain_arbitrage': 500000,
            'funding_rate_arbitrage': 300000,
            'statistical_arbitrage': 400000,
            'mev_arbitrage': 600000
        }
        
        base_gas = base_gas_estimates.get(opportunity_type, 300000)
        
        # Adjust for complexity
        complexity = opportunity.get('complexity', 0.5)
        adjusted_gas = base_gas * (1 + complexity)
        
        # Calculate gas cost
        gas_cost_eth = (adjusted_gas * current_gas_price) / 1e18  # Convert to ETH
        eth_price = 2000  # Would get from market data
        gas_cost_usd = gas_cost_eth * eth_price
        
        return gas_cost_usd
    
    async def _estimate_slippage_cost(self, opportunity: Dict[str, Any]) -> float:
        """Estimate slippage costs"""
        
        required_capital = opportunity.get('required_capital', 1000)
        slippage_rate = opportunity.get('slippage_estimate', 0.002)  # 0.2% default
        
        return required_capital * slippage_rate
    
    async def _calculate_protocol_fees(self, opportunity: Dict[str, Any]) -> float:
        """Calculate protocol fees"""
        
        protocols = opportunity.get('protocols', [])
        required_capital = opportunity.get('required_capital', 1000)
        
        total_fees = 0.0
        
        for protocol in protocols:
            fee_config = self.protocol_configs.get(protocol, {'fee_tier': 0.003})
            total_fees += required_capital * fee_config['fee_tier']
        
        return total_fees
    
    async def _assess_opportunity_risk(self, opportunity: Dict[str, Any], 
                                     opportunity_type: str) -> Dict[str, float]:
        """Comprehensive risk assessment for opportunity"""
        
        risk_metrics = {}
        
        # Slippage risk
        slippage_risk = await self.risk_models['slippage_risk'].assess(opportunity)
        risk_metrics['slippage_risk'] = slippage_risk
        
        # Liquidity risk
        liquidity_risk = await self.risk_models['liquidity_risk'].assess(opportunity)
        risk_metrics['liquidity_risk'] = liquidity_risk
        
        # Smart contract risk
        contract_risk = await self.risk_models['smart_contract_risk'].assess(opportunity)
        risk_metrics['smart_contract_risk'] = contract_risk
        
        # Front-running risk
        front_run_risk = await self.risk_models['front_running_risk'].assess(opportunity)
        risk_metrics['front_running_risk'] = front_run_risk
        
        # Opportunity-specific risks
        if opportunity_type == 'cross_chain_arbitrage':
            bridge_risk = opportunity.get('bridge_risk', 0.3)
            risk_metrics['bridge_risk'] = bridge_risk
        
        elif opportunity_type == 'statistical_arbitrage':
            model_risk = opportunity.get('model_risk', 0.4)
            risk_metrics['model_risk'] = model_risk
        
        # Overall risk score
        overall_risk = np.mean(list(risk_metrics.values()))
        risk_metrics['overall_risk'] = overall_risk
        
        return risk_metrics
    
    async def _calculate_confidence(self, opportunity: Dict[str, Any],
                                  risk_metrics: Dict[str, float],
                                  expected_profit: float) -> OpportunityConfidence:
        """Calculate confidence level for opportunity"""
        
        base_confidence = 0.5
        
        # Adjust based on profit size
        profit_boost = min(0.3, expected_profit * 10)  # Scale profit impact
        base_confidence += profit_boost
        
        # Adjust based on risk
        overall_risk = risk_metrics.get('overall_risk', 0.5)
        risk_penalty = overall_risk * 0.4
        base_confidence -= risk_penalty
        
        # Adjust based on liquidity
        liquidity = opportunity.get('liquidity_score', 0.5)
        liquidity_boost = liquidity * 0.2
        base_confidence += liquidity_boost
        
        # Convert to confidence enum
        if base_confidence >= 0.8:
            return OpportunityConfidence.VERY_HIGH
        elif base_confidence >= 0.7:
            return OpportunityConfidence.HIGH
        elif base_confidence >= 0.6:
            return OpportunityConfidence.MEDIUM
        else:
            return OpportunityConfidence.LOW
    
    async def _filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter opportunities based on various criteria"""
        
        filtered = []
        
        for opportunity in opportunities:
            # Check minimum profit threshold
            if opportunity.expected_profit < self.detection_params['min_profit_threshold']:
                continue
            
            # Check confidence threshold
            confidence_value = {
                OpportunityConfidence.LOW: 0.6,
                OpportunityConfidence.MEDIUM: 0.7,
                OpportunityConfidence.HIGH: 0.8,
                OpportunityConfidence.VERY_HIGH: 0.9
            }
            
            min_confidence = confidence_value.get(opportunity.confidence, 0.7)
            if min_confidence < self.detection_params['min_confidence_threshold']:
                continue
            
            # Check execution time
            if opportunity.time_sensitivity < timedelta(seconds=5):
                # Too time-sensitive, likely to fail
                continue
            
            # Check risk levels
            overall_risk = opportunity.risk_metrics.get('overall_risk', 0.5)
            if overall_risk > 0.8:
                continue
            
            filtered.append(opportunity)
        
        # Sort by expected profit (descending)
        filtered.sort(key=lambda x: x.expected_profit, reverse=True)
        
        return filtered
    
    async def detect_market_inefficiencies(self, market_data: Dict[str, Any]) -> List[MarketInefficiency]:
        """Detect persistent market inefficiencies"""
        
        inefficiencies = []
        
        # Price inefficiencies
        price_ineffs = await self._detect_price_inefficiencies(market_data)
        inefficiencies.extend(price_ineffs)
        
        # Liquidity inefficiencies
        liquidity_ineffs = await self._detect_liquidity_inefficiencies(market_data)
        inefficiencies.extend(liquidity_ineffs)
        
        # Structural inefficiencies
        structural_ineffs = await self._detect_structural_inefficiencies(market_data)
        inefficiencies.extend(structural_ineffs)
        
        # Update inefficiency history
        for inefficiency in inefficiencies:
            self.market_inefficiencies.append(inefficiency)
        
        return inefficiencies
    
    async def _detect_price_inefficiencies(self, market_data: Dict[str, Any]) -> List[MarketInefficiency]:
        """Detect price-based market inefficiencies"""
        
        inefficiencies = []
        
        # Check for persistent price discrepancies
        price_data = market_data.get('price_comparisons', {})
        
        for asset_pair, comparisons in price_data.items():
            for comp in comparisons:
                price_diff = comp.get('price_difference', 0)
                duration = comp.get('duration', timedelta(0))
                
                if (abs(price_diff) > 0.01 and  # 1% difference
                    duration > timedelta(minutes=10)):  # Persistent
                    
                    inefficiency = MarketInefficiency(
                        inefficiency_id=f"price_ineff_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        timestamp=datetime.now(),
                        asset_pair=asset_pair.split('-'),
                        inefficiency_type='price_discrepancy',
                        magnitude=abs(price_diff),
                        duration=duration,
                        cause=comp.get('cause', 'unknown'),
                        persistence_score=min(1.0, duration.total_seconds() / 3600),  # Scale to hours
                        metadata={
                            'protocols_involved': comp.get('protocols', []),
                            'average_volume': comp.get('volume', 0)
                        }
                    )
                    
                    inefficiencies.append(inefficiency)
                    print(f"Price inefficiency detected: {asset_pair} - {price_diff:.3%}")
        
        return inefficiencies
    
    async def _detect_liquidity_inefficiencies(self, market_data: Dict[str, Any]) -> List[MarketInefficiency]:
        """Detect liquidity-based market inefficiencies"""
        
        inefficiencies = []
        
        liquidity_data = market_data.get('liquidity_analysis', {})
        
        for pool_id, analysis in liquidity_data.items():
            concentration = analysis.get('concentration_ratio', 0)
            slippage_profile = analysis.get('slippage_profile', {})
            
            if concentration > 0.8:  # Highly concentrated
                inefficiency = MarketInefficiency(
                    inefficiency_id=f"liq_ineff_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    timestamp=datetime.now(),
                    asset_pair=analysis.get('assets', ['unknown', 'unknown']),
                    inefficiency_type='liquidity_concentration',
                    magnitude=concentration,
                    duration=timedelta(hours=24),  # Assume persistent
                    cause='high_liquidity_concentration',
                    persistence_score=0.8,
                    metadata={
                        'pool_id': pool_id,
                        'slippage_impact': slippage_profile
                    }
                )
                
                inefficiencies.append(inefficiency)
                print(f"Liquidity inefficiency detected: {pool_id} - concentration: {concentration:.1%}")
        
        return inefficiencies
    
    async def _detect_structural_inefficiencies(self, market_data: Dict[str, Any]) -> List[MarketInefficiency]:
        """Detect structural market inefficiencies"""
        
        inefficiencies = []
        
        # Check for regulatory or structural barriers
        structural_data = market_data.get('structural_analysis', {})
        
        for barrier_type, analysis in structural_data.items():
            impact = analysis.get('impact_score', 0)
            if impact > 0.7:  # Significant impact
                inefficiency = MarketInefficiency(
                    inefficiency_id=f"struct_ineff_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    timestamp=datetime.now(),
                    asset_pair=['market_wide', 'structural'],
                    inefficiency_type=barrier_type,
                    magnitude=impact,
                    duration=timedelta(days=30),  # Long-term structural
                    cause=analysis.get('cause', 'structural_barrier'),
                    persistence_score=0.9,
                    metadata={
                        'description': analysis.get('description', ''),
                        'affected_assets': analysis.get('affected_assets', []),
                        'potential_solutions': analysis.get('solutions', [])
                    }
                )
                
                inefficiencies.append(inefficiency)
                print(f"Structural inefficiency detected: {barrier_type} - impact: {impact:.1%}")
        
        return inefficiencies
    
    def _update_detection_metrics(self, detection_time: float, opportunities_count: int):
        """Update performance metrics"""
        
        total_detections = self.performance_metrics['opportunities_detected']
        current_avg = self.performance_metrics['avg_detection_time']
        
        if total_detections > 0:
            self.performance_metrics['avg_detection_time'] = (
                (current_avg * (total_detections - opportunities_count) + 
                 detection_time * opportunities_count) / total_detections
            )
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get opportunity detection statistics"""
        
        recent_opportunities = list(self.detected_opportunities)[-1000:]  # Last 1000
        
        type_counts = defaultdict(int)
        total_profit = 0.0
        
        for opportunity in recent_opportunities:
            type_counts[opportunity.opportunity_type.value] += 1
            total_profit += opportunity.expected_profit
        
        return {
            'total_opportunities_detected': self.performance_metrics['opportunities_detected'],
            'recent_opportunities': len(recent_opportunities),
            'type_distribution': dict(type_counts),
            'avg_expected_profit': total_profit / len(recent_opportunities) if recent_opportunities else 0,
            'detection_performance': self.performance_metrics
        }
    
    def update_detection_parameters(self, new_params: Dict[str, Any]):
        """Update detection parameters"""
        
        self.detection_params.update(new_params)
        print("Updated detection parameters")

# Supporting Classes
class SimpleArbitrageEngine:
    async def find_opportunities(self, price_matrix: Dict[str, Any], protocol_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implementation for simple arbitrage detection
        return []

class TriangularArbitrageEngine:
    async def find_triangular_opportunities(self, triangular_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

class CrossChainArbitrageEngine:
    async def find_cross_chain_opportunities(self, cross_chain_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

class FundingRateArbitrageEngine:
    async def find_funding_opportunities(self, funding_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

class StatisticalArbitrageEngine:
    async def find_statistical_opportunities(self, historical_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

class MEVArbitrageEngine:
    async def find_mev_opportunities(self, mev_data: Dict[str, Any], protocol_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

class MarketDataAggregator:
    async def build_price_matrix(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    async def build_triangular_matrix(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}
    
    async def build_cross_chain_matrix(self, market_data: Dict[str, Any], chain_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

class GasPricePredictor:
    async def get_current_gas_price(self) -> float:
        return 30.0  # gwei

class SlippageRiskModel:
    async def assess(self, opportunity: Dict[str, Any]) -> float:
        return 0.3

class LiquidityRiskModel:
    async def assess(self, opportunity: Dict[str, Any]) -> float:
        return 0.2

class SmartContractRiskModel:
    async def assess(self, opportunity: Dict[str, Any]) -> float:
        return 0.4

class FrontRunningRiskModel:
    async def assess(self, opportunity: Dict[str, Any]) -> float:
        return 0.5

class ImpermanentLossRiskModel:
    async def assess(self, opportunity: Dict[str, Any]) -> float:
        return 0.3

# Example usage
if __name__ == "__main__":
    # Create opportunity detector
    detector = OpportunityDetector()
    
    # Sample market data
    sample_market_data = {
        'price_comparisons': {
            'ETH-USDC': [
                {
                    'protocols': ['uniswap_v3', 'sushiswap'],
                    'price_difference': 0.005,  # 0.5%
                    'duration': timedelta(minutes=15),
                    'cause': 'liquidity_imbalance',
                    'volume': 1000000
                }
            ]
        },
        'liquidity_analysis': {
            'pool_1': {
                'assets': ['ETH', 'USDC'],
                'concentration_ratio': 0.85,
                'slippage_profile': {'1%': 50000, '5%': 200000}
            }
        },
        'funding_rates': {
            'ETH-USD': {'rate': 0.0002, 'next_funding': datetime.now() + timedelta(hours=8)}
        }
    }
    
    # Sample protocol data
    sample_protocol_data = {
        'uniswap_v3': {'liquidity': 50000000, 'fee_tier': 0.003},
        'sushiswap': {'liquidity': 30000000, 'fee_tier': 0.003}
    }
    
    # Detect opportunities
    async def demo():
        opportunities = await detector.detect_opportunities(
            sample_market_data, sample_protocol_data, {}
        )
        
        print(f"Detected {len(opportunities)} opportunities:")
        for opp in opportunities[:3]:  # Show top 3
            print(f" - {opp.opportunity_type.value}: {opp.expected_profit:.3%} profit "
                  f"(confidence: {opp.confidence.value})")
        
        # Detect inefficiencies
        inefficiencies = await detector.detect_market_inefficiencies(sample_market_data)
        print(f"Detected {len(inefficiencies)} market inefficiencies")
        
        # Get statistics
        stats = detector.get_detection_statistics()
        print(f"Detection Statistics: {stats}")
    
    import asyncio
    asyncio.run(demo())
