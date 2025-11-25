"""
RISK INTELLIGENCE ENGINE
REF: Goldman Sachs MARQ + BlackRock Aladdin Risk Systems
Institutional-grade risk assessment and portfolio protection
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class RiskLevel(Enum):
    EXTREME = "extreme"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class RiskFactor(Enum):
    MARKET = "market"
    LIQUIDITY = "liquidity"
    CREDIT = "credit"
    OPERATIONAL = "operational"
    SYSTEMIC = "systemic"
    REGULATORY = "regulatory"

@dataclass
class RiskAssessment:
    """Goldman Sachs MARQ-inspired risk assessment"""
    portfolio_id: str
    overall_risk: RiskLevel
    risk_breakdown: Dict[RiskFactor, float]
    var_95: float
    var_99: float
    expected_shortfall: float
    stress_test_results: Dict[str, float]
    risk_metrics: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class RiskEvent:
    """BlackRock Aladdin-inspired risk event tracking"""
    event_id: str
    event_type: str
    severity: RiskLevel
    impact_estimate: float
    probability: float
    affected_assets: List[str]
    trigger_conditions: Dict[str, float]
    mitigation_plan: List[str]
    timestamp: datetime

class RiskIntelligenceEngine:
    """
    Goldman Sachs MARQ + BlackRock Aladdin inspired risk system
    Institutional-grade risk assessment and management
    """
    
    def __init__(self):
        self.risk_models = {}
        self.stress_scenarios = {}
        self.correlation_matrices = {}
        self.risk_thresholds = {}
        
        # BlackRock Aladdin-inspired configuration
        self.config = {
            'var_confidence': 0.95,
            'historical_lookback': 252,  # 1 year of trading days
            'monte_carlo_simulations': 10000,
            'stress_test_scenarios': {
                '2008_crisis': self._2008_crisis_scenario,
                '2020_covid': self._2020_covid_scenario,
                'flash_crash': self._flash_crash_scenario,
                'liquidity_crisis': self._liquidity_crisis_scenario
            }
        }
        
        # Risk factor weights (Goldman Sachs MARQ patterns)
        self.risk_weights = {
            RiskFactor.MARKET: 0.35,
            RiskFactor.LIQUIDITY: 0.25,
            RiskFactor.CREDIT: 0.15,
            RiskFactor.OPERATIONAL: 0.10,
            RiskFactor.SYSTEMIC: 0.10,
            RiskFactor.REGULATORY: 0.05
        }

    async def assess_portfolio_risk(self, 
                                  portfolio: Dict,
                                  market_data: Dict) -> RiskAssessment:
        """
        Goldman Sachs MARQ-inspired portfolio risk assessment
        """
        risk_breakdown = {}
        
        # Calculate risk metrics for each factor
        risk_calculations = [
            self._assess_market_risk(portfolio, market_data),
            self._assess_liquidity_risk(portfolio, market_data),
            self._assess_credit_risk(portfolio, market_data),
            self._assess_operational_risk(portfolio),
            self._assess_systemic_risk(market_data),
            self._assess_regulatory_risk(portfolio)
        ]
        
        results = await asyncio.gather(*risk_calculations)
        
        for risk_factor, result in zip(RiskFactor, results):
            risk_breakdown[risk_factor] = result['risk_score']
        
        # Calculate Value at Risk
        var_metrics = await self._calculate_var(portfolio, market_data)
        
        # Stress testing
        stress_results = await self._run_stress_tests(portfolio, market_data)
        
        # Overall risk score
        overall_risk = self._calculate_overall_risk(risk_breakdown)
        
        # Generate recommendations
        recommendations = await self._generate_risk_recommendations(
            risk_breakdown, var_metrics, stress_results
        )
        
        return RiskAssessment(
            portfolio_id=portfolio['id'],
            overall_risk=overall_risk,
            risk_breakdown=risk_breakdown,
            var_95=var_metrics['var_95'],
            var_99=var_metrics['var_99'],
            expected_shortfall=var_metrics['expected_shortfall'],
            stress_test_results=stress_results,
            risk_metrics=var_metrics,
            recommendations=recommendations,
            timestamp=datetime.now()
        )

    async def monitor_risk_events(self,
                                portfolio: Dict,
                                market_data: Dict) -> List[RiskEvent]:
        """
        Real-time risk event monitoring (BlackRock Aladdin patterns)
        """
        risk_events = []
        
        # Market structure events
        market_events = await self._monitor_market_events(market_data)
        risk_events.extend(market_events)
        
        # Liquidity events
        liquidity_events = await self._monitor_liquidity_events(portfolio, market_data)
        risk_events.extend(liquidity_events)
        
        # Portfolio-specific events
        portfolio_events = await self._monitor_portfolio_events(portfolio, market_data)
        risk_events.extend(portfolio_events)
        
        # Systemic risk events
        systemic_events = await self._monitor_systemic_events(market_data)
        risk_events.extend(systemic_events)
        
        return risk_events

    async def calculate_position_limits(self,
                                      portfolio: Dict,
                                      risk_appetite: Dict) -> Dict[str, float]:
        """
        Calculate position limits based on risk appetite
        """
        position_limits = {}
        
        # Risk-based position sizing
        for asset, position in portfolio['positions'].items():
            asset_risk = await self._calculate_asset_risk(asset, portfolio, risk_appetite)
            limit = self._calculate_position_limit(asset_risk, risk_appetite)
            position_limits[asset] = limit
        
        # Portfolio concentration limits
        concentration_limits = await self._calculate_concentration_limits(portfolio, risk_appetite)
        position_limits.update(concentration_limits)
        
        return position_limits

    async def _assess_market_risk(self, portfolio: Dict, market_data: Dict) -> Dict:
        """
        Assess market risk (price movements, volatility)
        """
        risk_indicators = []
        
        # Portfolio volatility
        portfolio_volatility = await self._calculate_portfolio_volatility(portfolio, market_data)
        risk_indicators.append({
            'indicator': 'portfolio_volatility',
            'value': portfolio_volatility,
            'risk_score': min(portfolio_volatility * 10, 1.0)  # Normalize to 0-1
        })
        
        # Beta exposure
        beta_exposure = await self._calculate_beta_exposure(portfolio, market_data)
        risk_indicators.append({
            'indicator': 'beta_exposure',
            'value': beta_exposure,
            'risk_score': min(abs(beta_exposure - 1) * 0.5, 1.0)
        })
        
        # Correlation risk
        correlation_risk = await self._calculate_correlation_risk(portfolio, market_data)
        risk_indicators.append({
            'indicator': 'correlation_risk',
            'value': correlation_risk,
            'risk_score': correlation_risk
        })
        
        overall_score = np.mean([ind['risk_score'] for ind in risk_indicators])
        
        return {
            'risk_score': overall_score,
            'indicators': risk_indicators,
            'factor': RiskFactor.MARKET
        }

    async def _assess_liquidity_risk(self, portfolio: Dict, market_data: Dict) -> Dict:
        """
        Assess liquidity risk (ability to enter/exit positions)
        """
        risk_indicators = []
        
        # Position size vs market depth
        for asset, position in portfolio['positions'].items():
            liquidity_ratio = await self._calculate_liquidity_ratio(asset, position, market_data)
            risk_indicators.append({
                'indicator': f'liquidity_ratio_{asset}',
                'value': liquidity_ratio,
                'risk_score': min(1 / liquidity_ratio if liquidity_ratio > 0 else 1.0, 1.0)
            })
        
        # Bid-ask spread analysis
        spread_risk = await self._calculate_spread_risk(portfolio, market_data)
        risk_indicators.append({
            'indicator': 'spread_risk',
            'value': spread_risk,
            'risk_score': min(spread_risk * 10, 1.0)
        })
        
        # Market impact cost
        impact_cost = await self._calculate_market_impact(portfolio, market_data)
        risk_indicators.append({
            'indicator': 'market_impact',
            'value': impact_cost,
            'risk_score': min(impact_cost * 20, 1.0)
        })
        
        overall_score = np.mean([ind['risk_score'] for ind in risk_indicators])
        
        return {
            'risk_score': overall_score,
            'indicators': risk_indicators,
            'factor': RiskFactor.LIQUIDITY
        }

    async def _calculate_var(self, portfolio: Dict, market_data: Dict) -> Dict[str, float]:
        """
        Calculate Value at Risk using multiple methods
        """
        var_results = {}
        
        # Historical VaR
        historical_var = await self._calculate_historical_var(portfolio, market_data)
        var_results['historical_var_95'] = historical_var['var_95']
        var_results['historical_var_99'] = historical_var['var_99']
        
        # Parametric VaR
        parametric_var = await self._calculate_parametric_var(portfolio, market_data)
        var_results['parametric_var_95'] = parametric_var['var_95']
        var_results['parametric_var_99'] = parametric_var['var_99']
        
        # Monte Carlo VaR
        monte_carlo_var = await self._calculate_monte_carlo_var(portfolio, market_data)
        var_results['monte_carlo_var_95'] = monte_carlo_var['var_95']
        var_results['monte_carlo_var_99'] = monte_carlo_var['var_99']
        
        # Expected Shortfall (CVaR)
        expected_shortfall = await self._calculate_expected_shortfall(portfolio, market_data)
        var_results['expected_shortfall'] = expected_shortfall
        
        # Use conservative estimate
        var_results['var_95'] = max(
            var_results['historical_var_95'],
            var_results['parametric_var_95'],
            var_results['monte_carlo_var_95']
        )
        
        var_results['var_99'] = max(
            var_results['historical_var_99'],
            var_results['parametric_var_99'],
            var_results['monte_carlo_var_99']
        )
        
        return var_results

    async def _run_stress_tests(self, portfolio: Dict, market_data: Dict) -> Dict[str, float]:
        """
        Run stress test scenarios (BlackRock Aladdin patterns)
        """
        stress_results = {}
        
        for scenario_name, scenario_func in self.config['stress_test_scenarios'].items():
            try:
                scenario_result = await scenario_func(portfolio, market_data)
                stress_results[scenario_name] = scenario_result
            except Exception as e:
                print(f"Stress test {scenario_name} failed: {e}")
                continue
        
        return stress_results

    async def _2008_crisis_scenario(self, portfolio: Dict, market_data: Dict) -> float:
        """2008 financial crisis stress scenario"""
        # Simulate 2008-style market movements
        # Equity markets down 40-50%
        # Credit spreads widen significantly
        # Liquidity evaporates
        portfolio_value = portfolio['total_value']
        crisis_loss = portfolio_value * 0.45  # 45% loss estimate
        
        return crisis_loss

    async def _2020_covid_scenario(self, portfolio: Dict, market_data: Dict) -> float:
        """COVID-19 market crash scenario"""
        # Simulate March 2020 market conditions
        # Rapid 30%+ declines
        # Extreme volatility
        # Liquidity concerns
        portfolio_value = portfolio['total_value']
        covid_loss = portfolio_value * 0.35  # 35% loss estimate
        
        return covid_loss

    async def _flash_crash_scenario(self, portfolio: Dict, market_data: Dict) -> float:
        """Flash crash scenario"""
        # Simulate 2010-style flash crash
        # Rapid 10%+ declines in minutes
        # Liquidity disappearance
        portfolio_value = portfolio['total_value']
        flash_loss = portfolio_value * 0.15  # 15% loss estimate
        
        return flash_loss

    async def _liquidity_crisis_scenario(self, portfolio: Dict, market_data: Dict) -> float:
        """Liquidity crisis scenario"""
        # Simulate liquidity drying up
        # Inability to execute at reasonable prices
        # Wide bid-ask spreads
        portfolio_value = portfolio['total_value']
        liquidity_loss = portfolio_value * 0.25  # 25% loss estimate
        
        return liquidity_loss

    async def _monitor_market_events(self, market_data: Dict) -> List[RiskEvent]:
        """Monitor for market structure risk events"""
        events = []
        
        # Volatility spikes
        volatility_events = await self._detect_volatility_spikes(market_data)
        events.extend(volatility_events)
        
        # Correlation breakdowns
        correlation_events = await self._detect_correlation_breakdowns(market_data)
        events.extend(correlation_events)
        
        # Market microstructure events
        microstructure_events = await self._detect_microstructure_events(market_data)
        events.extend(microstructure_events)
        
        return events

    def _calculate_overall_risk(self, risk_breakdown: Dict[RiskFactor, float]) -> RiskLevel:
        """Calculate overall risk level from breakdown"""
        weighted_risk = sum(
            risk_breakdown[factor] * self.risk_weights[factor] 
            for factor in RiskFactor
        )
        
        if weighted_risk >= 0.8:
            return RiskLevel.EXTREME
        elif weighted_risk >= 0.6:
            return RiskLevel.HIGH
        elif weighted_risk >= 0.4:
            return RiskLevel.MEDIUM
        elif weighted_risk >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    async def _generate_risk_recommendations(self,
                                           risk_breakdown: Dict,
                                           var_metrics: Dict,
                                           stress_results: Dict) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # High market risk recommendations
        if risk_breakdown[RiskFactor.MARKET] > 0.7:
            recommendations.extend([
                "Reduce portfolio beta exposure",
                "Implement dynamic hedging strategies",
                "Increase cash position for buying opportunities"
            ])
        
        # High liquidity risk recommendations
        if risk_breakdown[RiskFactor.LIQUIDITY] > 0.7:
            recommendations.extend([
                "Reduce position sizes in illiquid assets",
                "Implement staggered exit strategies",
                "Increase holding period for large positions"
            ])
        
        # VaR-based recommendations
        if var_metrics['var_95'] > portfolio['total_value'] * 0.1:
            recommendations.append("Reduce portfolio VaR through diversification")
        
        # Stress test recommendations
        max_stress_loss = max(stress_results.values()) if stress_results else 0
        if max_stress_loss > portfolio['total_value'] * 0.3:
            recommendations.append("Implement additional stress test hedging")
        
        return recommendations

    # Placeholder implementations for calculation methods
    async def _calculate_portfolio_volatility(self, portfolio: Dict, market_data: Dict) -> float:
        return 0.15  # 15% annualized volatility
    
    async def _calculate_beta_exposure(self, portfolio: Dict, market_data: Dict) -> float:
        return 1.2  # 20% more volatile than market
    
    async def _calculate_correlation_risk(self, portfolio: Dict, market_data: Dict) -> float:
        return 0.3  # Moderate correlation risk
    
    async def _calculate_liquidity_ratio(self, asset: str, position: Dict, market_data: Dict) -> float:
        return 0.1  # Position is 10% of daily volume
    
    async def _calculate_historical_var(self, portfolio: Dict, market_data: Dict) -> Dict[str, float]:
        return {'var_95': portfolio['total_value'] * 0.05, 'var_99': portfolio['total_value'] * 0.08}
    
    async def _calculate_expected_shortfall(self, portfolio: Dict, market_data: Dict) -> float:
        return portfolio['total_value'] * 0.10

# Usage example
async def main():
    """Example usage of Risk Intelligence Engine"""
    risk_engine = RiskIntelligenceEngine()
    
    # Sample portfolio
    portfolio = {
        'id': 'test_portfolio',
        'total_value': 1000000,
        'positions': {
            'ETH/USD': {'value': 300000, 'size': 100},
            'BTC/USD': {'value': 400000, 'size': 10},
            'USDC': {'value': 300000, 'size': 300000}
        }
    }
    
    # Sample market data
    market_data = {
        'ETH/USD': {'close': [3500, 3510, 3520, 3500, 3480]},
        'BTC/USD': {'close': [45000, 45200, 44800, 44600, 44400]}
    }
    
    # Risk assessment
    risk_assessment = await risk_engine.assess_portfolio_risk(portfolio, market_data)
    
    print(f"Overall Risk: {risk_assessment.overall_risk.value}")
    print(f"VaR 95%: ${risk_assessment.var_95:,.2f}")
    print(f"Recommendations: {risk_assessment.recommendations}")

if __name__ == "__main__":
    asyncio.run(main())
