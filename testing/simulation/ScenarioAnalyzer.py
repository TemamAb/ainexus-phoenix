#!/usr/bin/env python3
"""
Enterprise Scenario Analysis Engine
Advanced scenario modeling, simulation, and risk assessment for DeFi protocols
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure enterprise logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Scenario:
    scenario_id: str
    name: str
    description: str
    category: str  # MARKET, PROTOCOL, REGULATORY, TECHNICAL
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    probability: Decimal
    impact: Decimal
    triggers: List[str]
    mitigation_strategies: List[str]
    parameters: Dict[str, Any]

@dataclass
class ScenarioResult:
    scenario_id: str
    execution_time: datetime
    success: bool
    metrics: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]

@dataclass
class RiskFactor:
    factor_id: str
    name: str
    category: str
    current_value: Decimal
    threshold: Decimal
    weight: Decimal
    trend: str  # INCREASING, DECREASING, STABLE

class ScenarioAnalyzer:
    """
    Advanced scenario analysis engine for comprehensive risk modeling,
    stress testing, and protocol resilience assessment.
    """
    
    def __init__(self, web3_provider=None, config: Dict = None):
        self.web3_provider = web3_provider
        self.config = config or {
            'monte_carlo_simulations': 10000,
            'confidence_level': Decimal('0.95'),
            'risk_threshold': Decimal('0.1'),
            'max_scenario_duration': 3600,
            'data_retention_days': 30
        }
        
        self.scenario_library: Dict[str, Scenario] = {}
        self.analysis_results: List[ScenarioResult] = []
        self.risk_factors: Dict[str, RiskFactor] = {}
        
        # Statistical models
        self.risk_models = {}
        self.correlation_matrices = {}
        
        # Performance metrics
        self.metrics = {
            'total_scenarios_analyzed': 0,
            'high_risk_scenarios': 0,
            'false_positives': 0,
            'average_analysis_time': 0.0
        }
        
        self._initialize_scenario_library()
        self._initialize_risk_factors()
        logger.info("ScenarioAnalyzer initialized with comprehensive risk modeling")

    def _initialize_scenario_library(self):
        """Initialize comprehensive scenario library"""
        
        # Market Risk Scenarios
        self.scenario_library['MARKET_CRASH_50PCT'] = Scenario(
            scenario_id='MARKET_CRASH_50PCT',
            name='50% Market Crash',
            description='Simulate Black Swan market event with 50% price drops',
            category='MARKET',
            severity='CRITICAL',
            probability=Decimal('0.02'),
            impact=Decimal('0.8'),
            triggers=['liquidity_crisis', 'margin_calls', 'cascading_liquidations'],
            mitigation_strategies=['circuit_breakers', 'insurance_funds', 'protocol_pauses'],
            parameters={
                'price_drop': Decimal('0.5'),
                'volatility_spike': Decimal('3.0'),
                'liquidity_reduction': Decimal('0.8'),
                'recovery_time': 86400  # 24 hours
            }
        )
        
        self.scenario_library['FLASH_CRASH_30PCT'] = Scenario(
            scenario_id='FLASH_CRASH_30PCT',
            name='30% Flash Crash',
            description='Rapid price decline and recovery within minutes',
            category='MARKET',
            severity='HIGH',
            probability=Decimal('0.05'),
            impact=Decimal('0.4'),
            triggers=['algorithmic_trading', 'liquidity_gaps', 'oracle_manipulation'],
            mitigation_strategies=['time_weighted_oracles', 'circuit_breakers', 'liquidity_incentives'],
            parameters={
                'price_drop': Decimal('0.3'),
                'recovery_time': 300,  # 5 minutes
                'volume_spike': Decimal('10.0')
            }
        )
        
        # Protocol Risk Scenarios
        self.scenario_library['SMART_CONTRACT_EXPLOIT'] = Scenario(
            scenario_id='SMART_CONTRACT_EXPLOIT',
            name='Smart Contract Exploit',
            description='Critical vulnerability exploited in protocol contracts',
            category='PROTOCOL',
            severity='CRITICAL',
            probability=Decimal('0.01'),
            impact=Decimal('0.9'),
            triggers=['reentrancy', 'logic_error', 'access_control_failure'],
            mitigation_strategies=['formal_verification', 'bug_bounties', 'time_locks'],
            parameters={
                'tvl_at_risk': Decimal('0.3'),  # 30% of TVL
                'recovery_complexity': 'HIGH',
                'regulatory_impact': 'SEVERE'
            }
        )
        
        self.scenario_library['GOVERNANCE_ATTACK'] = Scenario(
            scenario_id='GOVERNANCE_ATTACK',
            name='Governance Attack',
            description='Malicious actor gains control of protocol governance',
            category='PROTOCOL',
            severity='HIGH',
            probability=Decimal('0.03'),
            impact=Decimal('0.7'),
            triggers=['token_accumulation', 'voter_apathy', 'proposal_fatigue'],
            mitigation_strategies=['multisig_controls', 'time_delays', 'quorum_requirements'],
            parameters={
                'attack_cost': Decimal('10000000'),  # $10M
                'time_to_detection': 604800,  # 7 days
                'reversibility': 'PARTIAL'
            }
        )
        
        # Liquidity Risk Scenarios
        self.scenario_library['LIQUIDITY_CRISIS'] = Scenario(
            scenario_id='LIQUIDITY_CRISIS',
            name='Liquidity Crisis',
            description='Significant liquidity withdrawal from protocol',
            category='LIQUIDITY',
            severity='HIGH',
            probability=Decimal('0.04'),
            impact=Decimal('0.6'),
            triggers=['yield_compression', 'regulatory_announcement', 'competitor_launch'],
            mitigation_strategies=['liquidity_mining', 'insurance_pools', 'protocol_owned_liquidity'],
            parameters={
                'liquidity_withdrawal': Decimal('0.7'),  # 70% withdrawal
                'price_impact': Decimal('0.4'),  # 40% price impact
                'recovery_difficulty': 'MEDIUM'
            }
        )
        
        # Regulatory Risk Scenarios
        self.scenario_library['REGULATORY_BAN'] = Scenario(
            scenario_id='REGULATORY_BAN',
            name='Regulatory Ban',
            description='Protocol banned in major jurisdiction',
            category='REGULATORY',
            severity='HIGH',
            probability=Decimal('0.02'),
            impact=Decimal('0.5'),
            triggers=['enforcement_action', 'legislative_change', 'political_pressure'],
            mitigation_strategies=['jurisdictional_arbitrage', 'legal_compliance', 'decentralized_infrastructure'],
            parameters={
                'jurisdiction_size': 'LARGE',  # US, EU, China
                'compliance_cost': Decimal('5000000'),  # $5M
                'user_impact': Decimal('0.3')  # 30% of users affected
            }
        )
        
        # Technical Risk Scenarios
        self.scenario_library['NETWORK_CONGESTION'] = Scenario(
            scenario_id='NETWORK_CONGESTION',
            name='Network Congestion',
            description='Blockchain network experiences severe congestion',
            category='TECHNICAL',
            severity='MEDIUM',
            probability=Decimal('0.08'),
            impact=Decimal('0.3'),
            triggers=['nft_mint', 'defi_launch', 'market_volatility'],
            mitigation_strategies=['layer2_solutions', 'gas_optimization', 'multi_chain_deployment'],
            parameters={
                'gas_price_multiplier': Decimal('50.0'),
                'confirmation_time': 1800,  # 30 minutes
                'transaction_failure_rate': Decimal('0.2')  # 20% failure
            }
        )
        
        logger.info(f"Initialized scenario library with {len(self.scenario_library)} scenarios")

    def _initialize_risk_factors(self):
        """Initialize risk factor monitoring"""
        
        self.risk_factors['TVL_CONCENTRATION'] = RiskFactor(
            factor_id='TVL_CONCENTRATION',
            name='TVL Concentration Risk',
            category='PROTOCOL',
            current_value=Decimal('0.15'),  # 15% in top position
            threshold=Decimal('0.25'),  # 25% threshold
            weight=Decimal('0.2'),
            trend='STABLE'
        )
        
        self.risk_factors['LIQUIDITY_DEPTH'] = RiskFactor(
            factor_id='LIQUIDITY_DEPTH',
            name='Liquidity Depth',
            category='MARKET',
            current_value=Decimal('5000000'),  # $5M liquidity
            threshold=Decimal('1000000'),  # $1M minimum
            weight=Decimal('0.15'),
            trend='INCREASING'
        )
        
        self.risk_factors['VOLATILITY_INDEX'] = RiskFactor(
            factor_id='VOLATILITY_INDEX',
            name='Market Volatility',
            category='MARKET',
            current_value=Decimal('0.02'),  # 2% daily volatility
            threshold=Decimal('0.05'),  # 5% threshold
            weight=Decimal('0.18'),
            trend='DECREASING'
        )
        
        self.risk_factors['GOVERNANCE_PARTICIPATION'] = RiskFactor(
            factor_id='GOVERNANCE_PARTICIPATION',
            name='Governance Participation',
            category='PROTOCOL',
            current_value=Decimal('0.08'),  # 8% participation
            threshold=Decimal('0.05'),  # 5% minimum
            weight=Decimal('0.12'),
            trend='STABLE'
        )
        
        self.risk_factors['CODE_COVERAGE'] = RiskFactor(
            factor_id='CODE_COVERAGE',
            name='Smart Contract Test Coverage',
            category='TECHNICAL',
            current_value=Decimal('0.85'),  # 85% coverage
            threshold=Decimal('0.8'),  # 80% minimum
            weight=Decimal('0.15'),
            trend='INCREASING'
        )
        
        self.risk_factors['REGULATORY_CLARITY'] = RiskFactor(
            factor_id='REGULATORY_CLARITY',
            name='Regulatory Clarity Score',
            category='REGULATORY',
            current_value=Decimal('0.6'),  # 60% clarity
            threshold=Decimal('0.4'),  # 40% minimum
            weight=Decimal('0.2'),
            trend='INCREASING'
        )

    async def analyze_scenario(self, scenario_id: str, custom_parameters: Dict = None) -> ScenarioResult:
        """
        Execute comprehensive scenario analysis with Monte Carlo simulation
        """
        start_time = datetime.utcnow()
        
        if scenario_id not in self.scenario_library:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        
        scenario = self.scenario_library[scenario_id]
        parameters = {**scenario.parameters, **(custom_parameters or {})}
        
        try:
            logger.info(f"Starting scenario analysis: {scenario.name}")
            
            # 1. Monte Carlo Simulation
            mc_results = await self._run_monte_carlo_simulation(scenario, parameters)
            
            # 2. Risk Assessment
            risk_assessment = await self._assess_scenario_risk(scenario, mc_results)
            
            # 3. Impact Analysis
            impact_analysis = await self._analyze_impact(scenario, parameters, mc_results)
            
            # 4. Generate Recommendations
            recommendations = self._generate_recommendations(scenario, risk_assessment, impact_analysis)
            
            # 5. Compile Results
            result = ScenarioResult(
                scenario_id=scenario_id,
                execution_time=datetime.utcnow(),
                success=True,
                metrics={
                    'monte_carlo_results': mc_results,
                    'impact_analysis': impact_analysis,
                    'risk_metrics': risk_assessment
                },
                risk_assessment=risk_assessment,
                recommendations=recommendations
            )
            
            self.analysis_results.append(result)
            self.metrics['total_scenarios_analyzed'] += 1
            
            if risk_assessment['overall_risk'] == 'HIGH':
                self.metrics['high_risk_scenarios'] += 1
            
            # Update analysis time
            analysis_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics['average_analysis_time'] = (
                self.metrics['average_analysis_time'] * (self.metrics['total_scenarios_analyzed'] - 1) + analysis_time
            ) / self.metrics['total_scenarios_analyzed']
            
            logger.info(f"Scenario analysis completed: {scenario.name}")
            return result
            
        except Exception as e:
            logger.error(f"Scenario analysis failed for {scenario_id}: {e}")
            return ScenarioResult(
                scenario_id=scenario_id,
                execution_time=datetime.utcnow(),
                success=False,
                metrics={},
                risk_assessment={},
                recommendations=[f"Analysis failed: {str(e)}"]
            )

    async def _run_monte_carlo_simulation(self, scenario: Scenario, parameters: Dict) -> Dict[str, Any]:
        """Execute Monte Carlo simulation for scenario analysis"""
        simulations = self.config['monte_carlo_simulations']
        results = {
            'loss_distribution': [],
            'recovery_times': [],
            'liquidity_impact': [],
            'user_impact': []
        }
        
        # Simulate based on scenario type
        if scenario.category == 'MARKET':
            await self._simulate_market_scenario(scenario, parameters, results, simulations)
        elif scenario.category == 'PROTOCOL':
            await self._simulate_protocol_scenario(scenario, parameters, results, simulations)
        elif scenario.category == 'LIQUIDITY':
            await self._simulate_liquidity_scenario(scenario, parameters, results, simulations)
        elif scenario.category == 'REGULATORY':
            await self._simulate_regulatory_scenario(scenario, parameters, results, simulations)
        elif scenario.category == 'TECHNICAL':
            await self._simulate_technical_scenario(scenario, parameters, results, simulations)
        
        # Calculate statistics
        stats_results = self._calculate_simulation_statistics(results)
        return {**results, **stats_results}

    async def _simulate_market_scenario(self, scenario: Scenario, parameters: Dict, results: Dict, simulations: int):
        """Simulate market risk scenarios"""
        price_drop = float(parameters['price_drop'])
        volatility_spike = float(parameters['volatility_spike'])
        liquidity_reduction = float(parameters['liquidity_reduction'])
        
        for _ in range(simulations):
            # Simulate price path with increased volatility
            price_path = self._simulate_gbm(
                initial_price=1.0,
                mu=-price_drop,  # Negative drift for crash
                sigma=0.02 * volatility_spike,  # Increased volatility
                steps=100
            )
            
            final_price = price_path[-1]
            loss = max(0, 1 - final_price)  # Percentage loss
            
            # Simulate liquidity impact
            liquidity_impact = liquidity_reduction * np.random.beta(2, 5)
            
            # Simulate recovery time (lognormal distribution)
            recovery_time = np.random.lognormal(np.log(3600), 0.5)  # 1 hour mean
            
            results['loss_distribution'].append(loss)
            results['liquidity_impact'].append(liquidity_impact)
            results['recovery_times'].append(recovery_time)
            results['user_impact'].append(loss * 0.8)  # 80% of loss impacts users

    async def _simulate_protocol_scenario(self, scenario: Scenario, parameters: Dict, results: Dict, simulations: int):
        """Simulate protocol risk scenarios"""
        tvl_at_risk = float(parameters['tvl_at_risk'])
        
        for _ in range(simulations):
            # Simulate exploit impact (heavy-tailed distribution)
            exploit_severity = np.random.pareto(2.5) * tvl_at_risk
            exploit_severity = min(exploit_severity, 1.0)  # Cap at 100%
            
            # Recovery complexity affects recovery time
            recovery_complexity = parameters.get('recovery_complexity', 'MEDIUM')
            complexity_multiplier = {'LOW': 0.5, 'MEDIUM': 1.0, 'HIGH': 2.0}[recovery_complexity]
            recovery_time = np.random.lognormal(np.log(86400), 0.8) * complexity_multiplier  # Days
            
            # User confidence impact
            user_impact = exploit_severity * np.random.beta(3, 2)
            
            results['loss_distribution'].append(exploit_severity)
            results['recovery_times'].append(recovery_time)
            results['user_impact'].append(user_impact)
            results['liquidity_impact'].append(exploit_severity * 1.2)  # Liquidity hit harder

    async def _simulate_liquidity_scenario(self, scenario: Scenario, parameters: Dict, results: Dict, simulations: int):
        """Simulate liquidity risk scenarios"""
        liquidity_withdrawal = float(parameters['liquidity_withdrawal'])
        price_impact = float(parameters['price_impact'])
        
        for _ in range(simulations):
            # Simulate withdrawal pattern
            actual_withdrawal = np.random.beta(2, 3) * liquidity_withdrawal
            
            # Price impact increases with withdrawal size
            actual_price_impact = price_impact * (actual_withdrawal / liquidity_withdrawal) * np.random.lognormal(0, 0.2)
            
            # Recovery based on protocol incentives
            recovery_difficulty = parameters.get('recovery_difficulty', 'MEDIUM')
            difficulty_multiplier = {'LOW': 0.7, 'MEDIUM': 1.0, 'HIGH': 1.5}[recovery_difficulty]
            recovery_time = np.random.lognormal(np.log(43200), 0.6) * difficulty_multiplier  # 12 hours mean
            
            results['loss_distribution'].append(actual_price_impact)
            results['liquidity_impact'].append(actual_withdrawal)
            results['recovery_times'].append(recovery_time)
            results['user_impact'].append(actual_price_impact * 0.6)  # 60% user impact

    async def _simulate_regulatory_scenario(self, scenario: Scenario, parameters: Dict, results: Dict, simulations: int):
        """Simulate regulatory risk scenarios"""
        user_impact = float(parameters['user_impact'])
        compliance_cost = float(parameters['compliance_cost']) / 1000000  # Normalize to millions
        
        for _ in range(simulations):
            # Regulatory impact varies by jurisdiction size
            jurisdiction_size = parameters.get('jurisdiction_size', 'MEDIUM')
            size_multiplier = {'SMALL': 0.5, 'MEDIUM': 1.0, 'LARGE': 1.5}[jurisdiction_size]
            
            actual_user_impact = user_impact * size_multiplier * np.random.beta(2, 3)
            actual_compliance_cost = compliance_cost * np.random.lognormal(0, 0.3)
            
            # Recovery time depends on legal complexity
            recovery_time = np.random.lognormal(np.log(2592000), 0.7)  # 30 days mean
            
            results['loss_distribution'].append(actual_compliance_cost)
            results['user_impact'].append(actual_user_impact)
            results['recovery_times'].append(recovery_time)
            results['liquidity_impact'].append(actual_user_impact * 0.4)  # 40% liquidity impact

    async def _simulate_technical_scenario(self, scenario: Scenario, parameters: Dict, results: Dict, simulations: int):
        """Simulate technical risk scenarios"""
        gas_price_multiplier = float(parameters['gas_price_multiplier'])
        failure_rate = float(parameters['transaction_failure_rate'])
        
        for _ in range(simulations):
            # Gas price volatility
            actual_gas_multiplier = gas_price_multiplier * np.random.lognormal(0, 0.4)
            
            # Transaction failure impact
            actual_failure_rate = failure_rate * np.random.beta(2, 4)
            
            # User experience degradation
            user_impact = actual_failure_rate * 0.8 + (actual_gas_multiplier / 100) * 0.2
            
            # Recovery time (network congestion typically resolves faster)
            recovery_time = np.random.lognormal(np.log(1800), 0.5)  # 30 minutes mean
            
            # Cost impact (gas expenses)
            cost_impact = (actual_gas_multiplier - 1) * 0.01  # 1% cost increase per 100x gas
            
            results['loss_distribution'].append(cost_impact)
            results['user_impact'].append(user_impact)
            results['recovery_times'].append(recovery_time)
            results['liquidity_impact'].append(actual_failure_rate * 0.3)  # 30% liquidity impact

    def _simulate_gbm(self, initial_price: float, mu: float, sigma: float, steps: int) -> np.ndarray:
        """Simulate Geometric Brownian Motion price path"""
        dt = 1.0 / steps
        prices = [initial_price]
        
        for _ in range(steps - 1):
            drift = (mu - 0.5 * sigma ** 2) * dt
            shock = sigma * np.sqrt(dt) * np.random.normal()
            new_price = prices[-1] * np.exp(drift + shock)
            prices.append(new_price)
            
        return np.array(prices)

    def _calculate_simulation_statistics(self, results: Dict) -> Dict[str, Any]:
        """Calculate comprehensive statistics from simulation results"""
        stats = {}
        
        for key, values in results.items():
            if values:  # Only calculate if we have data
                arr = np.array(values)
                stats[f'{key}_mean'] = float(np.mean(arr))
                stats[f'{key}_std'] = float(np.std(arr))
                stats[f'{key}_var95'] = float(np.percentile(arr, 95))
                stats[f'{key}_var99'] = float(np.percentile(arr, 99))
                stats[f'{key}_min'] = float(np.min(arr))
                stats[f'{key}_max'] = float(np.max(arr))
                stats[f'{key}_skew'] = float(stats.skew(arr))
                stats[f'{key}_kurtosis'] = float(stats.kurtosis(arr))
        
        return stats

    async def _assess_scenario_risk(self, scenario: Scenario, mc_results: Dict) -> Dict[str, Any]:
        """Comprehensive risk assessment for scenario"""
        
        # Extract key metrics
        var95_loss = mc_results.get('loss_distribution_var95', 0)
        var99_loss = mc_results.get('loss_distribution_var99', 0)
        avg_recovery_time = mc_results.get('recovery_times_mean', 0)
        max_user_impact = mc_results.get('user_impact_max', 0)
        
        # Calculate risk scores
        loss_severity_score = min(var95_loss * 2, 1.0)  # Normalize to 0-1
        recovery_difficulty_score = min(avg_recovery_time / 86400, 1.0)  # Normalize by 1 day
        user_impact_score = min(max_user_impact * 1.2, 1.0)  # Slight amplification
        
        # Combined risk score (weighted average)
        risk_score = (
            loss_severity_score * 0.4 +
            recovery_difficulty_score * 0.3 +
            user_impact_score * 0.3
        )
        
        # Determine risk level
        if risk_score > 0.7:
            risk_level = 'CRITICAL'
        elif risk_score > 0.5:
            risk_level = 'HIGH'
        elif risk_score > 0.3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'overall_risk': risk_level,
            'risk_score': risk_score,
            'loss_severity': loss_severity_score,
            'recovery_difficulty': recovery_difficulty_score,
            'user_impact': user_impact_score,
            'var_95': var95_loss,
            'var_99': var99_loss,
            'expected_loss': mc_results.get('loss_distribution_mean', 0)
        }

    async def _analyze_impact(self, scenario: Scenario, parameters: Dict, mc_results: Dict) -> Dict[str, Any]:
        """Analyze comprehensive impact of scenario"""
        
        avg_loss = mc_results.get('loss_distribution_mean', 0)
        avg_recovery = mc_results.get('recovery_times_mean', 0)
        avg_liquidity_impact = mc_results.get('liquidity_impact_mean', 0)
        avg_user_impact = mc_results.get('user_impact_mean', 0)
        
        return {
            'financial_impact': {
                'expected_loss': avg_loss,
                'liquidity_impact': avg_liquidity_impact,
                'recovery_cost': avg_loss * 0.1  # 10% of loss for recovery
            },
            'operational_impact': {
                'downtime': avg_recovery,
                'user_retention_impact': avg_user_impact,
                'reputation_damage': min(avg_user_impact * 1.5, 1.0)
            },
            'strategic_impact': {
                'competitive_position': max(0, 1 - avg_loss * 2),
                'growth_impact': max(0, 1 - avg_user_impact),
                'regulatory_scrutiny': min(avg_loss * 3, 1.0) if scenario.category == 'REGULATORY' else 0.1
            }
        }

    def _generate_recommendations(self, scenario: Scenario, risk_assessment: Dict, impact_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on scenario analysis"""
        
        recommendations = []
        risk_level = risk_assessment['overall_risk']
        
        # Base recommendations for all high-risk scenarios
        if risk_level in ['HIGH', 'CRITICAL']:
            recommendations.append("Implement immediate risk mitigation measures")
            recommendations.append("Increase monitoring and alerting for scenario triggers")
            recommendations.append("Review and update incident response plans")
        
        # Scenario-specific recommendations
        if scenario.category == 'MARKET':
            if risk_assessment['loss_severity'] > 0.6:
                recommendations.append("Implement dynamic circuit breakers for extreme market moves")
                recommendations.append("Diversify liquidity sources across multiple venues")
            
        elif scenario.category == 'PROTOCOL':
            if risk_assessment['recovery_difficulty'] > 0.5:
                recommendations.append("Establish emergency multisig controls with time delays")
                recommendations.append("Create protocol-owned insurance fund")
            
        elif scenario.category == 'LIQUIDITY':
            if impact_analysis['financial_impact']['liquidity_impact'] > 0.3:
                recommendations.append("Implement liquidity mining incentives during stress periods")
                recommendations.append("Establish protocol-owned liquidity positions")
            
        elif scenario.category == 'REGULATORY':
            if impact_analysis['strategic_impact']['regulatory_scrutiny'] > 0.5:
                recommendations.append("Engage legal counsel for jurisdictional compliance")
                recommendations.append("Implement geographic restrictions if necessary")
            
        elif scenario.category == 'TECHNICAL':
            if risk_assessment['user_impact'] > 0.4:
                recommendations.append("Deploy on multiple blockchain networks for redundancy")
                recommendations.append("Optimize gas usage and implement gas refund mechanisms")
        
        # Add scenario-specific mitigation strategies
        recommendations.extend(scenario.mitigation_strategies)
        
        return recommendations

    async def analyze_portfolio_scenarios(self, scenarios: List[str]) -> Dict[str, Any]:
        """Analyze multiple scenarios for portfolio risk assessment"""
        
        portfolio_results = {}
        correlation_analysis = {}
        
        for scenario_id in scenarios:
            result = await self.analyze_scenario(scenario_id)
            portfolio_results[scenario_id] = result
        
        # Calculate portfolio-level metrics
        total_risk_score = np.mean([r.risk_assessment['risk_score'] for r in portfolio_results.values()])
        worst_case_scenario = max(portfolio_results.values(), key=lambda x: x.risk_assessment['risk_score'])
        
        # Correlation analysis between scenarios
        loss_correlations = await self._calculate_scenario_correlations(portfolio_results)
        
        return {
            'portfolio_risk_score': total_risk_score,
            'worst_case_scenario': worst_case_scenario.scenario_id,
            'scenario_results': portfolio_results,
            'correlation_analysis': loss_correlations,
            'diversification_benefit': self._calculate_diversification_benefit(portfolio_results)
        }

    async def _calculate_scenario_correlations(self, portfolio_results: Dict[str, ScenarioResult]) -> Dict[str, float]:
        """Calculate correlations between different scenario impacts"""
        # This would involve more sophisticated correlation analysis
        # For now, return simplified correlations
        return {
            'market_protocol_correlation': 0.6,
            'liquidity_regulatory_correlation': 0.3,
            'technical_market_correlation': 0.4
        }

    def _calculate_diversification_benefit(self, portfolio_results: Dict[str, ScenarioResult]) -> float:
        """Calculate diversification benefit across scenarios"""
        individual_risks = [r.risk_assessment['risk_score'] for r in portfolio_results.values()]
        portfolio_risk = np.mean(individual_risks)
        
        # Simplified diversification benefit calculation
        benefit = 1 - (portfolio_risk / max(individual_risks)) if max(individual_risks) > 0 else 0
        return benefit

    def get_risk_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive risk dashboard"""
        
        recent_analyses = self.analysis_results[-10:]  # Last 10 analyses
        
        return {
            'risk_metrics': {
                'total_scenarios_analyzed': self.metrics['total_scenarios_analyzed'],
                'high_risk_scenarios': self.metrics['high_risk_scenarios'],
                'average_risk_score': np.mean([r.risk_assessment['risk_score'] for r in recent_analyses]) if recent_analyses else 0,
                'false_positive_rate': self.metrics['false_positives'] / max(1, self.metrics['total_scenarios_analyzed'])
            },
            'scenario_summary': {
                scenario_id: {
                    'name': scenario.name,
                    'severity': scenario.severity,
                    'probability': float(scenario.probability),
                    'last_analysis': next((r.execution_time for r in reversed(self.analysis_results) if r.scenario_id == scenario_id), None)
                }
                for scenario_id, scenario in self.scenario_library.items()
            },
            'risk_factors': {
                factor_id: {
                    'name': factor.name,
                    'current_value': float(factor.current_value),
                    'threshold': float(factor.threshold),
                    'status': 'OK' if factor.current_value <= factor.threshold else 'WARNING',
                    'trend': factor.trend
                }
                for factor_id, factor in self.risk_factors.items()
            },
            'recommendations': self._get_aggregate_recommendations()
        }

    def _get_aggregate_recommendations(self) -> List[str]:
        """Get aggregate recommendations across all analyses"""
        all_recommendations = []
        for result in self.analysis_results[-5:]:  # Last 5 analyses
            all_recommendations.extend(result.recommendations)
        
        # Return unique recommendations
        return list(set(all_recommendations))

# Factory function
def create_scenario_analyzer(web3_provider=None, config: Dict = None) -> ScenarioAnalyzer:
    return ScenarioAnalyzer(web3_provider, config)

if __name__ == "__main__":
    # Example usage
    analyzer = ScenarioAnalyzer()
    print("ScenarioAnalyzer initialized successfully")
    
    # Example scenario analysis
    import asyncio
    
    async def example_analysis():
        result = await analyzer.analyze_scenario('MARKET_CRASH_50PCT')
        print(f"Scenario analysis completed: {result.scenario_id}")
        print(f"Risk level: {result.risk_assessment['overall_risk']}")
        print(f"Recommendations: {result.recommendations[:3]}")
    
    asyncio.run(example_analysis())
