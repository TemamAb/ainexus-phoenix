"""
AI-NEXUS v5.0 - YIELD CURVE ARBITRAGE MODULE
Advanced Fixed Income and Yield Curve Arbitrage
Term structure, curve steepening/flattening, and cross-currency arbitrage
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import warnings
warnings.filterwarnings('ignore')

class YieldCurveStrategy(Enum):
    CURVE_STEEPENER = "curve_steepener"
    CURVE_FLATTENER = "curve_flattener"
    BUTTERFLY_TRADE = "butterfly_trade"
    CARRY_TRADE = "carry_trade"
    ROLL_DOWN_TRADE = "roll_down_trade"
    CROSS_CURRENCY_BASIS = "cross_currency_basis"

class TermStructure(Enum):
    SHORT_END = "short_end"      # 0-2 years
    BELLY = "belly"              # 2-10 years  
    LONG_END = "long_end"        # 10+ years
    FULL_CURVE = "full_curve"

class YieldCurveModel(Enum):
    NELSON_SIEGEL = "nelson_siegel"
    SVENSSON = "svensson"
    SPLINE = "spline"
    AFFINE = "affine"

@dataclass
class YieldCurve:
    curve_id: str
    timestamp: datetime
    currency: str
    tenors: List[float]  # in years
    yields: List[float]  # in decimal
    model_params: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class CurveSignal:
    signal_id: str
    timestamp: datetime
    strategy: YieldCurveStrategy
    currency_pair: Tuple[str, str]
    signal_strength: float
    expected_return: float
    risk_metrics: Dict[str, float]
    position_size: float
    entry_conditions: Dict[str, float]
    exit_conditions: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class CarryAnalysis:
    analysis_id: str
    timestamp: datetime
    currency: str
    carry_return: float
    roll_down_return: float
    duration_exposure: float
    convexity_exposure: float
    metadata: Dict[str, Any]

class YieldCurveArbitrageur:
    """
    Advanced Yield Curve Arbitrage System
    Multi-strategy fixed income arbitrage across currencies and tenors
    """
    
    def __init__(self):
        self.yield_curves = defaultdict(lambda: deque(maxlen=10000))
        self.curve_signals = deque(maxlen=5000)
        self.carry_analyses = deque(maxlen=1000)
        
        # Trading parameters
        self.trading_params = {
            'curve_lookback': 252,  # 1 year
            'min_curve_change': 0.001,  # 10 bps
            'max_duration_exposure': 5.0,  # 5 years duration
            'carry_threshold': 0.005,  # 50 bps minimum carry
            'roll_down_threshold': 0.002,  # 20 bps roll down
            'basis_threshold': 0.0015  # 15 bps cross-currency basis
        }
        
        # Strategy configurations
        self.strategy_configs = {
            YieldCurveStrategy.CURVE_STEEPENER: {
                'description': 'Bet on yield curve steepening',
                'steepening_threshold': 0.002,
                'duration_neutral': True,
                'tenor_pairs': [(2, 10), (5, 30)]
            },
            YieldCurveStrategy.CURVE_FLATTENER: {
                'description': 'Bet on yield curve flattening',
                'flattening_threshold': 0.002,
                'duration_neutral': True,
                'tenor_pairs': [(2, 10), (5, 30)]
            },
            YieldCurveStrategy.BUTTERFLY_TRADE: {
                'description': 'Butterfly trades on curve reshaping',
                'butterfly_threshold': 0.001,
                'tenor_combinations': [(2, 5, 10), (5, 10, 30)]
            },
            YieldCurveStrategy.CARRY_TRADE: {
                'description': 'Carry trades along the curve',
                'min_carry': 0.005,
                'roll_down_required': True,
                'tenor_range': (2, 10)
            },
            YieldCurveStrategy.ROLL_DOWN_TRADE: {
                'description': 'Roll down the curve trades',
                'min_roll_down': 0.003,
                'steep_curve_required': True,
                'tenor_range': (5, 10)
            },
            YieldCurveStrategy.CROSS_CURRENCY_BASIS: {
                'description': 'Cross-currency basis trades',
                'basis_threshold': 0.002,
                'currency_pairs': [('USD', 'EUR'), ('USD', 'JPY'), ('EUR', 'GBP')]
            }
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_signals': 0,
            'profitable_signals': 0,
            'total_pnl': 0.0,
            'carry_pnl': 0.0,
            'rolldown_pnl': 0.0,
            'curve_pnl': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
        
        # Initialize yield curve models
        self._initialize_yield_models()
        self._initialize_risk_models()
    
    def _initialize_yield_models(self):
        """Initialize yield curve modeling frameworks"""
        
        self.yield_models = {
            YieldCurveModel.NELSON_SIEGEL: NelsonSiegelModel(),
            YieldCurveModel.SVENSSON: SvenssonModel(),
            YieldCurveModel.SPLINE: SplineModel(),
            YieldCurveModel.AFFINE: AffineModel()
        }
    
    def _initialize_risk_models(self):
        """Initialize fixed income risk models"""
        
        self.risk_models = {
            'duration_calculator': DurationCalculator(),
            'convexity_calculator': ConvexityCalculator(),
            'var_model': FixedIncomeVaRModel(),
            'basis_risk_model': BasisRiskModel()
        }
    
    async def update_yield_curve(self, currency: str, yield_data: Dict[str, Any]):
        """Update yield curve data for a currency"""
        
        curve = YieldCurve(
            curve_id=f"curve_{currency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            currency=currency,
            tenors=yield_data.get('tenors', []),
            yields=yield_data.get('yields', []),
            model_params=yield_data.get('model_params', {}),
            metadata=yield_data.get('metadata', {})
        )
        
        self.yield_curves[currency].append(curve)
        
        print(f"Yield curve updated for {currency}")
    
    async def scan_curve_opportunities(self, 
                                     strategy: YieldCurveStrategy = None,
                                     currencies: List[str] = None) -> List[CurveSignal]:
        """Scan for yield curve arbitrage opportunities"""
        
        if currencies is None:
            currencies = list(self.yield_curves.keys())
        
        opportunities = []
        
        if strategy is None:
            # Scan all strategies
            for strategy_enum in YieldCurveStrategy:
                strategy_opportunities = await self._scan_strategy_opportunities(strategy_enum, currencies)
                opportunities.extend(strategy_opportunities)
        else:
            # Scan specific strategy
            opportunities = await self._scan_strategy_opportunities(strategy, currencies)
        
        # Filter and rank opportunities
        filtered_opportunities = self._filter_opportunities(opportunities)
        
        print(f"Found {len(filtered_opportunities)} yield curve opportunities")
        
        return filtered_opportunities
    
    async def _scan_strategy_opportunities(self, strategy: YieldCurveStrategy, currencies: List[str]) -> List[CurveSignal]:
        """Scan opportunities for specific strategy"""
        
        if strategy == YieldCurveStrategy.CURVE_STEEPENER:
            return await self._scan_curve_steepener(currencies)
        elif strategy == YieldCurveStrategy.CURVE_FLATTENER:
            return await self._scan_curve_flattener(currencies)
        elif strategy == YieldCurveStrategy.BUTTERFLY_TRADE:
            return await self._scan_butterfly_trade(currencies)
        elif strategy == YieldCurveStrategy.CARRY_TRADE:
            return await self._scan_carry_trade(currencies)
        elif strategy == YieldCurveStrategy.ROLL_DOWN_TRADE:
            return await self._scan_roll_down_trade(currencies)
        elif strategy == YieldCurveStrategy.CROSS_CURRENCY_BASIS:
            return await self._scan_cross_currency_basis(currencies)
        else:
            return []
    
    async def _scan_curve_steepener(self, currencies: List[str]) -> List[CurveSignal]:
        """Scan for curve steepening opportunities"""
        
        opportunities = []
        config = self.strategy_configs[YieldCurveStrategy.CURVE_STEEPENER]
        
        for currency in currencies:
            curve_analysis = await self._analyze_curve_shape(currency)
            if not curve_analysis:
                continue
            
            steepening_potential = curve_analysis.get('steepening_potential', 0)
            current_slope = curve_analysis.get('current_slope', 0)
            
            if (steepening_potential > config['steepening_threshold'] and 
                current_slope < self._get_historical_slope(currency) * 0.8):
                
                signal = await self._create_steepener_signal(currency, curve_analysis)
                if signal:
                    opportunities.append(signal)
        
        return opportunities
    
    async def _scan_curve_flattener(self, currencies: List[str]) -> List[CurveSignal]:
        """Scan for curve flattening opportunities"""
        
        opportunities = []
        config = self.strategy_configs[YieldCurveStrategy.CURVE_FLATTENER]
        
        for currency in currencies:
            curve_analysis = await self._analyze_curve_shape(currency)
            if not curve_analysis:
                continue
            
            flattening_potential = curve_analysis.get('flattening_potential', 0)
            current_slope = curve_analysis.get('current_slope', 0)
            
            if (flattening_potential > config['flattening_threshold'] and 
                current_slope > self._get_historical_slope(currency) * 1.2):
                
                signal = await self._create_flattener_signal(currency, curve_analysis)
                if signal:
                    opportunities.append(signal)
        
        return opportunities
    
    async def _scan_butterfly_trade(self, currencies: List[str]) -> List[CurveSignal]:
        """Scan for butterfly trade opportunities"""
        
        opportunities = []
        config = self.strategy_configs[YieldCurveStrategy.BUTTERFLY_TRADE]
        
        for currency in currencies:
            for tenor_combo in config['tenor_combinations']:
                butterfly_analysis = await self._analyze_butterfly(currency, tenor_combo)
                if not butterfly_analysis:
                    continue
                
                butterfly_value = butterfly_analysis.get('butterfly_value', 0)
                
                if abs(butterfly_value) > config['butterfly_threshold']:
                    signal = await self._create_butterfly_signal(currency, tenor_combo, butterfly_analysis)
                    if signal:
                        opportunities.append(signal)
        
        return opportunities
    
    async def _scan_carry_trade(self, currencies: List[str]) -> List[CurveSignal]:
        """Scan for carry trade opportunities"""
        
        opportunities = []
        config = self.strategy_configs[YieldCurveStrategy.CARRY_TRADE]
        
        for currency in currencies:
            carry_analysis = await self._analyze_carry(currency)
            if not carry_analysis:
                continue
            
            carry_return = carry_analysis.carry_return
            roll_down_return = carry_analysis.roll_down_return
            
            if (carry_return > config['min_carry'] and 
                (not config['roll_down_required'] or roll_down_return > 0)):
                
                signal = await self._create_carry_signal(currency, carry_analysis)
                if signal:
                    opportunities.append(signal)
        
        return opportunities
    
    async def _scan_roll_down_trade(self, currencies: List[str]) -> List[CurveSignal]:
        """Scan for roll down trade opportunities"""
        
        opportunities = []
        config = self.strategy_configs[YieldCurveStrategy.ROLL_DOWN_TRADE]
        
        for currency in currencies:
            roll_down_analysis = await self._analyze_roll_down(currency)
            if not roll_down_analysis:
                continue
            
            roll_down_return = roll_down_analysis.get('roll_down_return', 0)
            curve_steepness = roll_down_analysis.get('curve_steepness', 0)
            
            if (roll_down_return > config['min_roll_down'] and 
                (not config['steep_curve_required'] or curve_steepness > 0.01)):
                
                signal = await self._create_roll_down_signal(currency, roll_down_analysis)
                if signal:
                    opportunities.append(signal)
        
        return opportunities
    
    async def _scan_cross_currency_basis(self, currencies: List[str]) -> List[CurveSignal]:
        """Scan for cross-currency basis opportunities"""
        
        opportunities = []
        config = self.strategy_configs[YieldCurveStrategy.CROSS_CURRENCY_BASIS]
        
        for currency1, currency2 in config['currency_pairs']:
            if currency1 not in currencies or currency2 not in currencies:
                continue
            
            basis_analysis = await self._analyze_cross_currency_basis(currency1, currency2)
            if not basis_analysis:
                continue
            
            basis = basis_analysis.get('basis', 0)
            
            if abs(basis) > config['basis_threshold']:
                signal = await self._create_basis_signal(currency1, currency2, basis_analysis)
                if signal:
                    opportunities.append(signal)
        
        return opportunities
    
    async def _analyze_curve_shape(self, currency: str) -> Optional[Dict[str, Any]]:
        """Analyze yield curve shape and dynamics"""
        
        if currency not in self.yield_curves:
            return None
        
        curves = list(self.yield_curves[currency])
        if len(curves) < 2:
            return None
        
        current_curve = curves[-1]
        previous_curve = curves[-2]
        
        # Calculate curve slope (10y - 2y)
        slope_2s10s = self._calculate_slope(current_curve, 2, 10)
        previous_slope_2s10s = self._calculate_slope(previous_curve, 2, 10)
        
        # Calculate curve curvature (butterfly: 2s10s30s)
        butterfly_2s10s30s = self._calculate_butterfly(current_curve, 2, 10, 30)
        
        # Historical context
        historical_slope = self._get_historical_slope(currency)
        slope_percentile = self._get_slope_percentile(currency, slope_2s10s)
        
        return {
            'current_slope': slope_2s10s,
            'slope_change': slope_2s10s - previous_slope_2s10s,
            'butterfly_value': butterfly_2s10s30s,
            'historical_slope': historical_slope,
            'slope_percentile': slope_percentile,
            'steepening_potential': max(0, historical_slope - slope_2s10s),
            'flattening_potential': max(0, slope_2s10s - historical_slope)
        }
    
    def _calculate_slope(self, curve: YieldCurve, short_tenor: float, long_tenor: float) -> float:
        """Calculate yield curve slope between two tenors"""
        
        short_yield = self._interpolate_yield(curve, short_tenor)
        long_yield = self._interpolate_yield(curve, long_tenor)
        
        if short_yield is None or long_yield is None:
            return 0.0
        
        return long_yield - short_yield
    
    def _calculate_butterfly(self, curve: YieldCurve, short_tenor: float, medium_tenor: float, long_tenor: float) -> float:
        """Calculate butterfly value (2*medium - short - long)"""
        
        short_yield = self._interpolate_yield(curve, short_tenor)
        medium_yield = self._interpolate_yield(curve, medium_tenor)
        long_yield = self._interpolate_yield(curve, long_tenor)
        
        if None in [short_yield, medium_yield, long_yield]:
            return 0.0
        
        return 2 * medium_yield - short_yield - long_yield
    
    def _interpolate_yield(self, curve: YieldCurve, tenor: float) -> Optional[float]:
        """Interpolate yield for a given tenor"""
        
        if not curve.tenors or not curve.yields:
            return None
        
        # Simple linear interpolation
        tenors = np.array(curve.tenors)
        yields = np.array(curve.yields)
        
        if tenor in tenors:
            return yields[tenors == tenor][0]
        
        # Interpolate
        return np.interp(tenor, tenors, yields)
    
    def _get_historical_slope(self, currency: str, lookback: int = 63) -> float:
        """Get historical average slope"""
        
        if currency not in self.yield_curves:
            return 0.01  # Default 100 bps
        
        curves = list(self.yield_curves[currency])
        if len(curves) < lookback:
            return 0.01
        
        recent_curves = curves[-lookback:]
        slopes = [self._calculate_slope(curve, 2, 10) for curve in recent_curves]
        
        return np.mean(slopes) if slopes else 0.01
    
    def _get_slope_percentile(self, currency: str, current_slope: float, lookback: int = 252) -> float:
        """Get current slope percentile relative to history"""
        
        if currency not in self.yield_curves:
            return 0.5
        
        curves = list(self.yield_curves[currency])
        if len(curves) < lookback:
            return 0.5
        
        historical_slopes = [self._calculate_slope(curve, 2, 10) for curve in curves[-lookback:]]
        
        if not historical_slopes:
            return 0.5
        
        return np.mean(np.array(historical_slopes) < current_slope)
    
    async def _analyze_butterfly(self, currency: str, tenor_combo: Tuple[float, float, float]) -> Optional[Dict[str, Any]]:
        """Analyze butterfly trade opportunity"""
        
        if currency not in self.yield_curves:
            return None
        
        curves = list(self.yield_curves[currency])
        if not curves:
            return None
        
        current_curve = curves[-1]
        short_tenor, medium_tenor, long_tenor = tenor_combo
        
        butterfly_value = self._calculate_butterfly(current_curve, short_tenor, medium_tenor, long_tenor)
        
        # Historical comparison
        historical_butterflies = [
            self._calculate_butterfly(curve, short_tenor, medium_tenor, long_tenor)
            for curve in curves[-63:]  # 3 months
        ]
        
        historical_mean = np.mean(historical_butterflies) if historical_butterflies else 0
        historical_std = np.std(historical_butterflies) if len(historical_butterflies) > 1 else 0.001
        
        z_score = (butterfly_value - historical_mean) / historical_std if historical_std > 0 else 0
        
        return {
            'butterfly_value': butterfly_value,
            'historical_mean': historical_mean,
            'z_score': z_score,
            'tenor_combo': tenor_combo
        }
    
    async def _analyze_carry(self, currency: str) -> Optional[CarryAnalysis]:
        """Analyze carry trade opportunity"""
        
        if currency not in self.yield_curves:
            return None
        
        curves = list(self.yield_curves[currency])
        if not curves:
            return None
        
        current_curve = curves[-1]
        
        # Calculate carry for 5-year tenor
        five_year_yield = self._interpolate_yield(current_curve, 5)
        two_year_yield = self._interpolate_yield(current_curve, 2)
        
        if five_year_yield is None or two_year_yield is None:
            return None
        
        carry_return = five_year_yield - two_year_yield
        
        # Calculate roll down return
        roll_down_return = self._calculate_roll_down(current_curve, 5)
        
        # Calculate risk metrics
        duration_exposure = 3.0  # Approximate duration for 5y-2y spread
        convexity_exposure = 0.1  # Approximate convexity
        
        return CarryAnalysis(
            analysis_id=f"carry_{currency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            currency=currency,
            carry_return=carry_return,
            roll_down_return=roll_down_return,
            duration_exposure=duration_exposure,
            convexity_exposure=convexity_exposure,
            metadata={'tenor_pair': (2, 5)}
        )
    
    def _calculate_roll_down(self, curve: YieldCurve, target_tenor: float) -> float:
        """Calculate roll down return for a target tenor"""
        
        current_yield = self._interpolate_yield(curve, target_tenor)
        rolled_yield = self._interpolate_yield(curve, target_tenor - 0.25)  # 3-month roll down
        
        if current_yield is None or rolled_yield is None:
            return 0.0
        
        return current_yield - rolled_yield
    
    async def _analyze_roll_down(self, currency: str) -> Optional[Dict[str, Any]]:
        """Analyze roll down trade opportunity"""
        
        if currency not in self.yield_curves:
            return None
        
        curves = list(self.yield_curves[currency])
        if not curves:
            return None
        
        current_curve = curves[-1]
        
        # Analyze 5-year point roll down
        roll_down_5y = self._calculate_roll_down(current_curve, 5)
        curve_steepness = self._calculate_slope(current_curve, 2, 10)
        
        return {
            'roll_down_return': roll_down_5y,
            'curve_steepness': curve_steepness,
            'target_tenor': 5,
            'roll_period': 0.25  # 3 months
        }
    
    async def _analyze_cross_currency_basis(self, currency1: str, currency2: str) -> Optional[Dict[str, Any]]:
        """Analyze cross-currency basis opportunity"""
        
        if currency1 not in self.yield_curves or currency2 not in self.yield_curves:
            return None
        
        curves1 = list(self.yield_curves[currency1])
        curves2 = list(self.yield_curves[currency2])
        
        if not curves1 or not curves2:
            return None
        
        current_curve1 = curves1[-1]
        current_curve2 = curves2[-1]
        
        # Calculate 5-year yield difference as proxy for basis
        yield1_5y = self._interpolate_yield(current_curve1, 5)
        yield2_5y = self._interpolate_yield(current_curve2, 5)
        
        if yield1_5y is None or yield2_5y is None:
            return None
        
        basis = yield1_5y - yield2_5y
        
        # Historical basis analysis
        historical_basis = await self._get_historical_basis(currency1, currency2)
        basis_zscore = (basis - historical_basis['mean']) / historical_basis['std'] if historical_basis['std'] > 0 else 0
        
        return {
            'basis': basis,
            'historical_mean': historical_basis['mean'],
            'historical_std': historical_basis['std'],
            'z_score': basis_zscore,
            'currency_pair': (currency1, currency2)
        }
    
    async def _get_historical_basis(self, currency1: str, currency2: str, lookback: int = 63) -> Dict[str, float]:
        """Get historical basis statistics"""
        
        if currency1 not in self.yield_curves or currency2 not in self.yield_curves:
            return {'mean': 0, 'std': 0.001}
        
        curves1 = list(self.yield_curves[currency1])
        curves2 = list(self.yield_curves[currency2])
        
        min_len = min(len(curves1), len(curves2), lookback)
        if min_len < 10:
            return {'mean': 0, 'std': 0.001}
        
        basis_values = []
        for i in range(-min_len, 0):
            yield1 = self._interpolate_yield(curves1[i], 5)
            yield2 = self._interpolate_yield(curves2[i], 5)
            
            if yield1 is not None and yield2 is not None:
                basis_values.append(yield1 - yield2)
        
        if not basis_values:
            return {'mean': 0, 'std': 0.001}
        
        return {
            'mean': np.mean(basis_values),
            'std': np.std(basis_values)
        }
    
    async def _create_steepener_signal(self, currency: str, curve_analysis: Dict[str, Any]) -> Optional[CurveSignal]:
        """Create curve steepener signal"""
        
        steepening_potential = curve_analysis['steepening_potential']
        expected_return = steepening_potential * 0.8  # 80% of potential as expected return
        
        signal = CurveSignal(
            signal_id=f"steepener_{currency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            strategy=YieldCurveStrategy.CURVE_STEEPENER,
            currency_pair=(currency, currency),
            signal_strength=min(1.0, steepening_potential / 0.02),  # Normalize
            expected_return=expected_return,
            risk_metrics=await self._calculate_steepener_risk(currency, curve_analysis),
            position_size=self._calculate_position_size(expected_return, 0.02),
            entry_conditions={'steepening_potential': steepening_potential},
            exit_conditions={'steepening_potential': steepening_potential * 0.3},
            metadata=curve_analysis
        )
        
        return signal
    
    async def _create_flattener_signal(self, currency: str, curve_analysis: Dict[str, Any]) -> Optional[CurveSignal]:
        """Create curve flattener signal"""
        
        flattening_potential = curve_analysis['flattening_potential']
        expected_return = flattening_potential * 0.8
        
        signal = CurveSignal(
            signal_id=f"flattener_{currency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            strategy=YieldCurveStrategy.CURVE_FLATTENER,
            currency_pair=(currency, currency),
            signal_strength=min(1.0, flattening_potential / 0.02),
            expected_return=expected_return,
            risk_metrics=await self._calculate_flattener_risk(currency, curve_analysis),
            position_size=self._calculate_position_size(expected_return, 0.02),
            entry_conditions={'flattening_potential': flattening_potential},
            exit_conditions={'flattening_potential': flattening_potential * 0.3},
            metadata=curve_analysis
        )
        
        return signal
    
    async def _create_butterfly_signal(self, currency: str, tenor_combo: Tuple[float, float, float], 
                                     butterfly_analysis: Dict[str, Any]) -> Optional[CurveSignal]:
        """Create butterfly trade signal"""
        
        butterfly_value = butterfly_analysis['butterfly_value']
        expected_return = abs(butterfly_value) * 0.6
        
        signal = CurveSignal(
            signal_id=f"butterfly_{currency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            strategy=YieldCurveStrategy.BUTTERFLY_TRADE,
            currency_pair=(currency, currency),
            signal_strength=min(1.0, abs(butterfly_analysis['z_score']) / 2),
            expected_return=expected_return,
            risk_metrics={'var': abs(butterfly_value) * 1.5, 'curve_risk': 0.01},
            position_size=self._calculate_position_size(expected_return, 0.015),
            entry_conditions={'butterfly_value': butterfly_value, 'z_score': butterfly_analysis['z_score']},
            exit_conditions={'butterfly_value': butterfly_value * 0.4},
            metadata=butterfly_analysis
        )
        
        return signal
    
    async def _create_carry_signal(self, currency: str, carry_analysis: CarryAnalysis) -> Optional[CurveSignal]:
        """Create carry trade signal"""
        
        total_return = carry_analysis.carry_return + carry_analysis.roll_down_return
        
        signal = CurveSignal(
            signal_id=f"carry_{currency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            strategy=YieldCurveStrategy.CARRY_TRADE,
            currency_pair=(currency, currency),
            signal_strength=min(1.0, total_return / 0.01),  # Normalize to 100 bps
            expected_return=total_return,
            risk_metrics={
                'var': carry_analysis.carry_return * 2,
                'duration_risk': carry_analysis.duration_exposure * 0.01,  # 1% rate move
                'convexity_risk': carry_analysis.convexity_exposure * 0.0001
            },
            position_size=self._calculate_position_size(total_return, carry_analysis.duration_exposure * 0.01),
            entry_conditions={'carry_return': carry_analysis.carry_return, 'roll_down': carry_analysis.roll_down_return},
            exit_conditions={'carry_return': carry_analysis.carry_return * 0.5},
            metadata={'carry_analysis': carry_analysis}
        )
        
        return signal
    
    async def _create_roll_down_signal(self, currency: str, roll_down_analysis: Dict[str, Any]) -> Optional[CurveSignal]:
        """Create roll down trade signal"""
        
        roll_down_return = roll_down_analysis['roll_down_return']
        
        signal = CurveSignal(
            signal_id=f"rolldown_{currency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            strategy=YieldCurveStrategy.ROLL_DOWN_TRADE,
            currency_pair=(currency, currency),
            signal_strength=min(1.0, roll_down_return / 0.005),  # Normalize to 50 bps
            expected_return=roll_down_return,
            risk_metrics={'var': roll_down_return * 1.2, 'curve_risk': 0.008},
            position_size=self._calculate_position_size(roll_down_return, 0.01),
            entry_conditions={'roll_down_return': roll_down_return},
            exit_conditions={'roll_down_return': roll_down_return * 0.4},
            metadata=roll_down_analysis
        )
        
        return signal
    
    async def _create_basis_signal(self, currency1: str, currency2: str, basis_analysis: Dict[str, Any]) -> Optional[CurveSignal]:
        """Create cross-currency basis signal"""
        
        basis = basis_analysis['basis']
        expected_return = abs(basis) * 0.7
        
        signal = CurveSignal(
            signal_id=f"basis_{currency1}_{currency2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            strategy=YieldCurveStrategy.CROSS_CURRENCY_BASIS,
            currency_pair=(currency1, currency2),
            signal_strength=min(1.0, abs(basis_analysis['z_score']) / 2),
            expected_return=expected_return,
            risk_metrics={'var': abs(basis) * 1.8, 'fx_risk': 0.02, 'basis_risk': 0.005},
            position_size=self._calculate_position_size(expected_return, 0.025),
            entry_conditions={'basis': basis, 'z_score': basis_analysis['z_score']},
            exit_conditions={'basis': basis * 0.3},
            metadata=basis_analysis
        )
        
        return signal
    
    async def _calculate_steepener_risk(self, currency: str, curve_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk metrics for steepener trade"""
        
        return {
            'var': curve_analysis['steepening_potential'] * 1.5,
            'duration_risk': 2.0,  # Approximate duration exposure
            'curve_risk': 0.015,
            'liquidity_risk': 0.005
        }
    
    async def _calculate_flattener_risk(self, currency: str, curve_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate risk metrics for flattener trade"""
        
        return {
            'var': curve_analysis['flattening_potential'] * 1.5,
            'duration_risk': 2.0,
            'curve_risk': 0.015,
            'liquidity_risk': 0.005
        }
    
    def _calculate_position_size(self, expected_return: float, risk_estimate: float) -> float:
        """Calculate position size based on risk and return"""
        
        if risk_estimate <= 0:
            return 0.01
        
        # Kelly-inspired position sizing
        win_probability = 0.65  # Base win probability for yield curve trades
        kelly_fraction = win_probability - (1 - win_probability) / (expected_return / risk_estimate)
        
        position_size = max(0.005, min(0.1, kelly_fraction * 0.1))  # Cap at 10%
        return position_size
    
    def _filter_opportunities(self, opportunities: List[CurveSignal]) -> List[CurveSignal]:
        """Filter and rank opportunities"""
        
        return [
            opp for opp in opportunities
            if (opp.expected_return > 0.002 and  # Minimum 20 bps expected return
                opp.risk_metrics.get('var', 1) < 0.03 and  # Maximum 3% VaR
                opp.signal_strength > 0.4)  # Minimum signal strength
        ]
    
    async def execute_signal(self, signal: CurveSignal) -> Dict[str, Any]:
        """Execute yield curve arbitrage signal"""
        
        # In production, this would execute actual bond/futures trades
        execution_result = {
            'success': True,
            'execution_time': datetime.now(),
            'filled_quantity': signal.position_size * 1000000,  # $1M notional per 1% position
            'execution_yield': await self._get_execution_yield(signal),
            'fees': 0.0002,  # 2 bps fees
            'slippage': 0.0001  # 1 bp slippage
        }
        
        self.performance_metrics['total_signals'] += 1
        self.curve_signals.append(signal)
        
        print(f"Yield curve signal executed: {signal.signal_id}")
        
        return execution_result
    
    async def _get_execution_yield(self, signal: CurveSignal) -> float:
        """Get execution yield for signal"""
        # Simplified - in production, would get actual market yields
        return 0.02  # 2% yield
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        
        return {
            'total_signals': self.performance_metrics['total_signals'],
            'profitable_signals': self.performance_metrics['profitable_signals'],
            'total_pnl': self.performance_metrics['total_pnl'],
            'win_rate': (self.performance_metrics['profitable_signals'] / 
                        max(1, self.performance_metrics['total_signals'])),
            'sharpe_ratio': self.performance_metrics['sharpe_ratio'],
            'max_drawdown': self.performance_metrics['max_drawdown']
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        
        return {
            'active_signals': len(self.curve_signals),
            'monitored_currencies': len(self.yield_curves),
            'performance_metrics': self.get_performance_metrics(),
            'system_health': self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> float:
        """Calculate system health"""
        
        health_factors = []
        
        # Data quality health
        data_health = min(1.0, len([c for c in self.yield_curves.values() if len(c) >= 50]) / 
                         max(1, len(self.yield_curves)))
        health_factors.append(data_health * 0.3)
        
        # Signal quality health
        signal_health = self.performance_metrics.get('win_rate', 0.5)
        health_factors.append(signal_health * 0.4)
        
        # Activity health
        activity_health = min(1.0, self.performance_metrics['total_signals'] / 10)
        health_factors.append(activity_health * 0.3)
        
        return sum(health_factors)

# Supporting Model Classes
class NelsonSiegelModel:
    """Nelson-Siegel yield curve model"""
    pass

class SvenssonModel:
    """Svensson yield curve model"""
    pass

class SplineModel:
    """Spline yield curve model"""
    pass

class AffineModel:
    """Affine term structure model"""
    pass

class DurationCalculator:
    """Duration calculator for fixed income"""
    pass

class ConvexityCalculator:
    """Convexity calculator"""
    pass

class FixedIncomeVaRModel:
    """Fixed income VaR model"""
    pass

class BasisRiskModel:
    """Basis risk model"""
    pass

# Example usage
if __name__ == "__main__":
    async def demo():
        arbitrageur = YieldCurveArbitrageur()
        
        # Add sample yield curve data
        sample_curves = {
            'USD': {
                'tenors': [0.25, 0.5, 1, 2, 5, 10, 30],
                'yields': [0.005, 0.008, 0.012, 0.018, 0.025, 0.032, 0.038],
                'model_params': {},
                'metadata': {'source': 'treasury'}
            },
            'EUR': {
                'tenors': [0.25, 0.5, 1, 2, 5, 10, 30],
                'yields': [0.003, 0.005, 0.008, 0.012, 0.018, 0.025, 0.030],
                'model_params': {},
                'metadata': {'source': 'bund'}
            }
        }
        
        for currency, data in sample_curves.items():
            await arbitrageur.update_yield_curve(currency, data)
        
        # Scan for opportunities
        opportunities = await arbitrageur.scan_curve_opportunities()
        
        print(f"Found {len(opportunities)} yield curve opportunities")
        for opp in opportunities[:2]:  # Show first 2
            print(f"Signal: {opp.signal_id}, Strategy: {opp.strategy.value}")
            print(f"Expected Return: {opp.expected_return:.4f}, Strength: {opp.signal_strength:.3f}")
        
        # Execute first opportunity
        if opportunities:
            result = await arbitrageur.execute_signal(opportunities[0])
            print(f"Execution result: {result}")
        
        # Get status
        status = arbitrageur.get_system_status()
        print(f"System Status: {status}")
    
    import asyncio
    asyncio.run(demo())
