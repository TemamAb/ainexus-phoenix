"""
AI-NEXUS v5.0 - DECISION AGENT MODULE
Advanced Autonomous Decision-Making Agent
Strategic decision formulation and execution planning
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

class DecisionType(Enum):
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    EMERGENCY = "emergency"

class DecisionFramework(Enum):
    UTILITY_MAXIMIZATION = "utility_maximization"
    SATISFICING = "satisficing"
    PROSPECT_THEORY = "prospect_theory"
    BAYESIAN = "bayesian"
    REINFORCEMENT_LEARNING = "reinforcement_learning"

class RiskAppetite(Enum):
    VERY_CONSERVATIVE = "very_conservative"
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"

@dataclass
class DecisionContext:
    context_id: str
    timestamp: datetime
    market_conditions: Dict[str, Any]
    portfolio_state: Dict[str, Any]
    risk_metrics: Dict[str, float]
    constraints: Dict[str, Any]
    objectives: List[str]
    metadata: Dict[str, Any]

@dataclass
class DecisionOption:
    option_id: str
    description: str
    action_plan: Dict[str, Any]
    expected_utility: float
    risk_metrics: Dict[str, float]
    resource_requirements: Dict[str, float]
    execution_complexity: float
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class FinalDecision:
    decision_id: str
    timestamp: datetime
    selected_option: DecisionOption
    decision_framework: DecisionFramework
    reasoning: str
    confidence: float
    risk_appetite: RiskAppetite
    execution_timeline: Dict[str, datetime]
    fallback_plan: Dict[str, Any]
    metadata: Dict[str, Any]

class DecisionAgent:
    """
    Advanced autonomous decision-making agent
    Formulates strategic decisions using multiple decision frameworks
    """
    
    def __init__(self, agent_id: str, capabilities: List[str], risk_appetite: RiskAppetite = RiskAppetite.MODERATE):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.risk_appetite = risk_appetite
        
        # Decision history
        self.decision_history = deque(maxlen=10000)
        self.performance_metrics = {}
        
        # Decision frameworks
        self.decision_frameworks = {}
        self.active_framework = DecisionFramework.UTILITY_MAXIMIZATION
        
        # Learning parameters
        self.learning_params = {
            'exploration_rate': 0.1,
            'learning_rate': 0.01,
            'discount_factor': 0.95,
            'memory_size': 1000
        }
        
        # Risk parameters based on appetite
        self.risk_parameters = self._initialize_risk_parameters()
        
        # Performance tracking
        self.performance_tracker = {
            'decisions_made': 0,
            'successful_decisions': 0,
            'avg_decision_quality': 0.0,
            'learning_progress': 0.0
        }
        
        # Initialize decision frameworks
        self._initialize_decision_frameworks()
        self._initialize_utility_functions()
    
    def _initialize_risk_parameters(self) -> Dict[str, Any]:
        """Initialize risk parameters based on risk appetite"""
        
        risk_profiles = {
            RiskAppetite.VERY_CONSERVATIVE: {
                'max_drawdown_tolerance': 0.05,
                'var_confidence': 0.99,
                'sharpe_target': 2.0,
                'position_size_limit': 0.05,
                'correlation_limit': 0.3
            },
            RiskAppetite.CONSERVATIVE: {
                'max_drawdown_tolerance': 0.08,
                'var_confidence': 0.95,
                'sharpe_target': 1.5,
                'position_size_limit': 0.10,
                'correlation_limit': 0.5
            },
            RiskAppetite.MODERATE: {
                'max_drawdown_tolerance': 0.12,
                'var_confidence': 0.90,
                'sharpe_target': 1.2,
                'position_size_limit': 0.15,
                'correlation_limit': 0.7
            },
            RiskAppetite.AGGRESSIVE: {
                'max_drawdown_tolerance': 0.18,
                'var_confidence': 0.85,
                'sharpe_target': 1.0,
                'position_size_limit': 0.25,
                'correlation_limit': 0.8
            },
            RiskAppetite.VERY_AGGRESSIVE: {
                'max_drawdown_tolerance': 0.25,
                'var_confidence': 0.80,
                'sharpe_target': 0.8,
                'position_size_limit': 0.35,
                'correlation_limit': 0.9
            }
        }
        
        return risk_profiles.get(self.risk_appetite, risk_profiles[RiskAppetite.MODERATE])
    
    def _initialize_decision_frameworks(self):
        """Initialize decision-making frameworks"""
        
        self.decision_frameworks = {
            DecisionFramework.UTILITY_MAXIMIZATION: {
                'description': 'Maximize expected utility',
                'parameters': {
                    'risk_aversion': 1.0,
                    'time_preference': 0.95,
                    'utility_function': 'cara'  # Constant Absolute Risk Aversion
                },
                'evaluate': self._evaluate_utility_maximization
            },
            
            DecisionFramework.SATISFICING: {
                'description': 'Satisficing decision making',
                'parameters': {
                    'aspiration_level': 0.7,
                    'search_depth': 3,
                    'acceptance_threshold': 0.6
                },
                'evaluate': self._evaluate_satisficing
            },
            
            DecisionFramework.PROSPECT_THEORY: {
                'description': 'Prospect theory with loss aversion',
                'parameters': {
                    'loss_aversion': 2.25,
                    'probability_weighting': 0.61,
                    'reference_point': 'status_quo'
                },
                'evaluate': self._evaluate_prospect_theory
            },
            
            DecisionFramework.BAYESIAN: {
                'description': 'Bayesian decision theory',
                'parameters': {
                    'prior_strength': 0.5,
                    'evidence_weight': 0.5,
                    'update_rate': 0.1
                },
                'evaluate': self._evaluate_bayesian
            },
            
            DecisionFramework.REINFORCEMENT_LEARNING: {
                'description': 'Reinforcement learning based decisions',
                'parameters': {
                    'exploration_rate': 0.1,
                    'learning_rate': 0.01,
                    'discount_factor': 0.95
                },
                'evaluate': self._evaluate_reinforcement_learning
            }
        }
    
    def _initialize_utility_functions(self):
        """Initialize utility functions for different frameworks"""
        
        self.utility_functions = {
            'cara': lambda x, risk_aversion: 1 - np.exp(-risk_aversion * x),
            'crra': lambda x, risk_aversion: (x ** (1 - risk_aversion)) / (1 - risk_aversion) if risk_aversion != 1 else np.log(x),
            'linear': lambda x, _: x,
            'quadratic': lambda x, risk_aversion: x - 0.5 * risk_aversion * (x ** 2)
        }
    
    async def make_decision(self, context: DecisionContext, decision_type: DecisionType = DecisionType.STRATEGIC) -> FinalDecision:
        """Make a strategic decision based on context and decision type"""
        
        # Generate decision options
        decision_options = await self._generate_decision_options(context, decision_type)
        
        if not decision_options:
            raise ValueError("No valid decision options generated")
        
        # Evaluate options using active framework
        framework = self.decision_frameworks[self.active_framework]
        evaluated_options = await framework['evaluate'](decision_options, context)
        
        # Select best option
        selected_option = self._select_best_option(evaluated_options, context)
        
        # Create final decision
        final_decision = FinalDecision(
            decision_id=f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now(),
            selected_option=selected_option,
            decision_framework=self.active_framework,
            reasoning=self._generate_decision_reasoning(selected_option, context),
            confidence=selected_option.confidence,
            risk_appetite=self.risk_appetite,
            execution_timeline=await self._create_execution_timeline(selected_option, context),
            fallback_plan=await self._create_fallback_plan(selected_option, context),
            metadata={
                'evaluated_options': len(evaluated_options),
                'decision_complexity': self._calculate_decision_complexity(context),
                'framework_parameters': framework['parameters']
            }
        )
        
        # Record decision
        self.decision_history.append(final_decision)
        self.performance_tracker['decisions_made'] += 1
        
        print(f"Decision made: {final_decision.decision_id} with confidence {final_decision.confidence:.3f}")
        
        return final_decision
    
    async def _generate_decision_options(self, context: DecisionContext, decision_type: DecisionType) -> List[DecisionOption]:
        """Generate possible decision options based on context"""
        
        options = []
        
        # Generate options based on decision type
        if decision_type == DecisionType.STRATEGIC:
            options.extend(await self._generate_strategic_options(context))
        elif decision_type == DecisionType.TACTICAL:
            options.extend(await self._generate_tactical_options(context))
        elif decision_type == DecisionType.OPERATIONAL:
            options.extend(await self._generate_operational_options(context))
        elif decision_type == DecisionType.EMERGENCY:
            options.extend(await self._generate_emergency_options(context))
        
        # Filter options based on constraints
        filtered_options = await self._filter_options_by_constraints(options, context.constraints)
        
        return filtered_options
    
    async def _generate_strategic_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate strategic decision options"""
        
        options = []
        market_conditions = context.market_conditions
        portfolio_state = context.portfolio_state
        
        # Option 1: Portfolio rebalancing
        if 'portfolio_management' in self.capabilities:
            rebalance_option = DecisionOption(
                option_id="rebalance_portfolio",
                description="Strategic portfolio rebalancing based on market conditions",
                action_plan={
                    'action': 'rebalance',
                    'target_allocation': await self._calculate_target_allocation(context),
                    'rebalancing_method': 'threshold_based',
                    'execution_strategy': 'gradual'
                },
                expected_utility=0.0,  # Will be calculated
                risk_metrics={},
                resource_requirements={'execution_time': 300, 'capital_required': 0},
                execution_complexity=0.6,
                confidence=0.7,
                metadata={'type': 'strategic_rebalancing'}
            )
            options.append(rebalance_option)
        
        # Option 2: Asset allocation shift
        if 'asset_allocation' in self.capabilities:
            allocation_option = DecisionOption(
                option_id="adjust_allocation",
                description="Adjust asset allocation based on market regime",
                action_plan={
                    'action': 'adjust_allocation',
                    'allocation_shift': await self._calculate_allocation_shift(context),
                    'transition_period': timedelta(hours=24),
                    'risk_adjustment': True
                },
                expected_utility=0.0,
                risk_metrics={},
                resource_requirements={'execution_time': 600, 'capital_required': 0},
                execution_complexity=0.8,
                confidence=0.6,
                metadata={'type': 'allocation_adjustment'}
            )
            options.append(allocation_option)
        
        # Option 3: Risk exposure adjustment
        if 'risk_management' in self.capabilities:
            risk_option = DecisionOption(
                option_id="adjust_risk_exposure",
                description="Adjust overall portfolio risk exposure",
                action_plan={
                    'action': 'adjust_risk',
                    'risk_target': self.risk_parameters['max_drawdown_tolerance'],
                    'exposure_adjustment': await self._calculate_risk_adjustment(context),
                    'hedging_strategy': 'dynamic'
                },
                expected_utility=0.0,
                risk_metrics={},
                resource_requirements={'execution_time': 450, 'capital_required': 0},
                execution_complexity=0.7,
                confidence=0.65,
                metadata={'type': 'risk_adjustment'}
            )
            options.append(risk_option)
        
        # Calculate metrics for each option
        for option in options:
            option.expected_utility = await self._calculate_expected_utility(option, context)
            option.risk_metrics = await self._calculate_option_risk(option, context)
        
        return options
    
    async def _generate_tactical_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate tactical decision options"""
        
        options = []
        
        # Tactical trading opportunities
        if 'tactical_trading' in self.capabilities:
            tactical_option = DecisionOption(
                option_id="tactical_adjustment",
                description="Tactical position adjustments based on short-term opportunities",
                action_plan={
                    'action': 'tactical_trade',
                    'opportunity_type': 'momentum',
                    'position_sizing': 'risk_based',
                    'time_horizon': 'short_term'
                },
                expected_utility=0.0,
                risk_metrics={},
                resource_requirements={'execution_time': 60, 'capital_required': context.portfolio_state.get('available_capital', 0) * 0.1},
                execution_complexity=0.4,
                confidence=0.5,
                metadata={'type': 'tactical_trading'}
            )
            options.append(tactical_option)
        
        return options
    
    async def _generate_operational_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate operational decision options"""
        
        options = []
        
        # Operational efficiency improvements
        if 'operational_optimization' in self.capabilities:
            operational_option = DecisionOption(
                option_id="operational_optimization",
                description="Optimize operational parameters and execution",
                action_plan={
                    'action': 'optimize_operations',
                    'parameters_to_optimize': ['slippage', 'latency', 'fees'],
                    'optimization_method': 'gradient_descent'
                },
                expected_utility=0.0,
                risk_metrics={},
                resource_requirements={'execution_time': 180, 'capital_required': 0},
                execution_complexity=0.3,
                confidence=0.8,
                metadata={'type': 'operational_optimization'}
            )
            options.append(operational_option)
        
        return options
    
    async def _generate_emergency_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate emergency decision options"""
        
        options = []
        
        # Emergency risk reduction
        emergency_option = DecisionOption(
            option_id="emergency_risk_reduction",
            description="Emergency measures to reduce risk exposure",
            action_plan={
                'action': 'emergency_hedge',
                'risk_reduction_target': 0.5,
                'execution_priority': 'immediate',
                'hedging_instruments': ['options', 'futures']
            },
            expected_utility=0.0,
            risk_metrics={},
            resource_requirements={'execution_time': 30, 'capital_required': context.portfolio_state.get('available_capital', 0) * 0.2},
            execution_complexity=0.9,
            confidence=0.9,
            metadata={'type': 'emergency_risk_management'}
        )
        options.append(emergency_option)
        
        return options
    
    async def _filter_options_by_constraints(self, options: List[DecisionOption], constraints: Dict[str, Any]) -> List[DecisionOption]:
        """Filter options based on constraints"""
        
        filtered_options = []
        
        for option in options:
            # Check resource constraints
            if 'max_execution_time' in constraints and option.resource_requirements['execution_time'] > constraints['max_execution_time']:
                continue
            
            if 'max_capital' in constraints and option.resource_requirements['capital_required'] > constraints['max_capital']:
                continue
            
            # Check complexity constraints
            if 'max_complexity' in constraints and option.execution_complexity > constraints['max_complexity']:
                continue
            
            filtered_options.append(option)
        
        return filtered_options
    
    async def _evaluate_utility_maximization(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using utility maximization framework"""
        
        evaluated_options = []
        
        for option in options:
            # Calculate utility using CARA utility function
            utility_function = self.utility_functions['cara']
            risk_aversion = self.decision_frameworks[DecisionFramework.UTILITY_MAXIMIZATION]['parameters']['risk_aversion']
            
            # Adjust expected utility for risk
            risk_adjusted_utility = utility_function(option.expected_utility, risk_aversion)
            
            # Apply time preference
            time_preference = self.decision_frameworks[DecisionFramework.UTILITY_MAXIMIZATION]['parameters']['time_preference']
            discounted_utility = risk_adjusted_utility * time_preference
            
            # Update option with calculated utility
            option.expected_utility = discounted_utility
            option.confidence = min(1.0, option.confidence * (1 + discounted_utility))
            
            evaluated_options.append(option)
        
        return evaluated_options
    
    async def _evaluate_satisficing(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using satisficing framework"""
        
        aspiration_level = self.decision_frameworks[DecisionFramework.SATISFICING]['parameters']['aspiration_level']
        acceptance_threshold = self.decision_frameworks[DecisionFramework.SATISFICING]['parameters']['acceptance_threshold']
        
        satisfactory_options = []
        
        for option in options:
            # Normalize expected utility to 0-1 scale
            normalized_utility = max(0.0, min(1.0, option.expected_utility))
            
            # Check if option meets aspiration level
            if normalized_utility >= aspiration_level and option.confidence >= acceptance_threshold:
                satisfactory_options.append(option)
        
        # If no satisfactory options, relax criteria
        if not satisfactory_options:
            relaxed_threshold = acceptance_threshold * 0.8
            for option in options:
                if option.confidence >= relaxed_threshold:
                    satisfactory_options.append(option)
        
        return satisfactory_options
    
    async def _evaluate_prospect_theory(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using prospect theory"""
        
        loss_aversion = self.decision_frameworks[DecisionFramework.PROSPECT_THEORY]['parameters']['loss_aversion']
        
        evaluated_options = []
        
        for option in options:
            # Calculate value function from prospect theory
            if option.expected_utility >= 0:
                # Gains domain
                value = option.expected_utility ** 0.88
            else:
                # Losses domain (apply loss aversion)
                value = -loss_aversion * ((-option.expected_utility) ** 1.0)
            
            # Update option value
            option.expected_utility = value
            evaluated_options.append(option)
        
        return evaluated_options
    
    async def _evaluate_bayesian(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using Bayesian decision theory"""
        
        evaluated_options = []
        
        for option in options:
            # Bayesian updating of confidence based on historical performance
            prior_success_rate = self.performance_tracker.get('success_rate', 0.5)
            option_likelihood = option.confidence
            
            # Bayesian update
            posterior_confidence = (prior_success_rate * option_likelihood) / (
                prior_success_rate * option_likelihood + (1 - prior_success_rate) * (1 - option_likelihood)
            )
            
            option.confidence = posterior_confidence
            evaluated_options.append(option)
        
        return evaluated_options
    
    async def _evaluate_reinforcement_learning(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using reinforcement learning"""
        
        # Simple Q-learning inspired evaluation
        learning_rate = self.decision_frameworks[DecisionFramework.REINFORCEMENT_LEARNING]['parameters']['learning_rate']
        
        evaluated_options = []
        
        for option in options:
            # Incorporate learning from past similar decisions
            similarity_score = await self._calculate_context_similarity(context)
            learning_bonus = self.performance_tracker['learning_progress'] * learning_rate
            
            option.expected_utility += learning_bonus * similarity_score
            option.confidence = min(1.0, option.confidence + learning_bonus)
            
            evaluated_options.append(option)
        
        return evaluated_options
    
    def _select_best_option(self, options: List[DecisionOption], context: DecisionContext) -> DecisionOption:
        """Select the best option from evaluated options"""
        
        if not options:
            raise ValueError("No options available for selection")
        
        # Multi-criteria decision making
        scored_options = []
        
        for option in options:
            score = self._calculate_option_score(option, context)
            scored_options.append((option, score))
        
        # Select option with highest score
        best_option, best_score = max(scored_options, key=lambda x: x[1])
        
        print(f"Selected option: {best_option.option_id} with score {best_score:.3f}")
        
        return best_option
    
    def _calculate_option_score(self, option: DecisionOption, context: DecisionContext) -> float:
        """Calculate comprehensive score for an option"""
        
        weights = {
            'utility': 0.4,
            'risk': 0.3,
            'confidence': 0.2,
            'complexity': 0.1
        }
        
        # Normalize components
        utility_score = max(0.0, min(1.0, option.expected_utility))
        
        # Risk score (higher is better - lower risk)
        max_drawdown = option.risk_metrics.get('max_drawdown', 0.2)
        risk_score = 1.0 - (max_drawdown / self.risk_parameters['max_drawdown_tolerance'])
        risk_score = max(0.0, min(1.0, risk_score))
        
        confidence_score = option.confidence
        
        # Complexity score (lower complexity is better)
        complexity_score = 1.0 - option.execution_complexity
        
        # Calculate weighted score
        total_score = (
            weights['utility'] * utility_score +
            weights['risk'] * risk_score +
            weights['confidence'] * confidence_score +
            weights['complexity'] * complexity_score
        )
        
        return total_score
    
    async def _calculate_expected_utility(self, option: DecisionOption, context: DecisionContext) -> float:
        """Calculate expected utility for a decision option"""
        
        base_utility = 0.0
        
        # Calculate based on option type
        if option.option_id == "rebalance_portfolio":
            base_utility = await self._calculate_rebalancing_utility(context)
        elif option.option_id == "adjust_allocation":
            base_utility = await self._calculate_allocation_utility(context)
        elif option.option_id == "adjust_risk_exposure":
            base_utility = await self._calculate_risk_adjustment_utility(context)
        elif option.option_id == "tactical_adjustment":
            base_utility = await self._calculate_tactical_utility(context)
        elif option.option_id == "operational_optimization":
            base_utility = await self._calculate_operational_utility(context)
        elif option.option_id == "emergency_risk_reduction":
            base_utility = await self._calculate_emergency_utility(context)
        
        # Adjust for confidence
        confidence_adjusted_utility = base_utility * option.confidence
        
        return max(-1.0, min(1.0, confidence_adjusted_utility))
    
    async def _calculate_rebalancing_utility(self, context: DecisionContext) -> float:
        """Calculate utility for portfolio rebalancing"""
        
        current_allocation = context.portfolio_state.get('current_allocation', {})
        target_allocation = await self._calculate_target_allocation(context)
        
        # Calculate misalignment
        misalignment = 0.0
        for asset, current_weight in current_allocation.items():
            target_weight = target_allocation.get(asset, 0.0)
            misalignment += abs(current_weight - target_weight)
        
        # Utility is inverse of misalignment
        utility = 1.0 - min(1.0, misalignment)
        
        return utility
    
    async def _calculate_target_allocation(self, context: DecisionContext) -> Dict[str, float]:
        """Calculate target portfolio allocation"""
        
        # Simplified target allocation calculation
        # In production, this would use sophisticated portfolio optimization
        
        market_regime = context.market_conditions.get('regime', 'neutral')
        
        if market_regime == 'bull':
            return {'BTC': 0.4, 'ETH': 0.3, 'SOL': 0.2, 'cash': 0.1}
        elif market_regime == 'bear':
            return {'BTC': 0.2, 'ETH': 0.2, 'SOL': 0.1, 'cash': 0.5}
        else:  # neutral
            return {'BTC': 0.3, 'ETH': 0.25, 'SOL': 0.15, 'cash': 0.3}
    
    async def _calculate_allocation_utility(self, context: DecisionContext) -> float:
        """Calculate utility for allocation adjustment"""
        
        current_regime = context.market_conditions.get('regime', 'neutral')
        portfolio_regime_alignment = context.portfolio_state.get('regime_alignment', 0.5)
        
        # Utility based on improving regime alignment
        utility = 1.0 - portfolio_regime_alignment
        
        return utility
    
    async def _calculate_risk_adjustment_utility(self, context: DecisionContext) -> float:
        """Calculate utility for risk adjustment"""
        
        current_risk = context.risk_metrics.get('portfolio_risk', 0.15)
        target_risk = self.risk_parameters['max_drawdown_tolerance']
        
        # Utility based on moving toward target risk
        risk_deviation = abs(current_risk - target_risk) / target_risk
        utility = 1.0 - min(1.0, risk_deviation)
        
        return utility
    
    async def _calculate_tactical_utility(self, context: DecisionContext) -> float:
        """Calculate utility for tactical adjustments"""
        
        market_volatility = context.market_conditions.get('volatility', 0.2)
        
        # Higher utility in moderate volatility environments
        optimal_volatility = 0.15
        volatility_deviation = abs(market_volatility - optimal_volatility) / optimal_volatility
        utility = 1.0 - min(1.0, volatility_deviation)
        
        return utility
    
    async def _calculate_operational_utility(self, context: DecisionContext) -> float:
        """Calculate utility for operational optimization"""
        
        # Base utility for operational improvements
        return 0.3  # Operational improvements generally have moderate utility
    
    async def _calculate_emergency_utility(self, context: DecisionContext) -> float:
        """Calculate utility for emergency measures"""
        
        risk_level = context.risk_metrics.get('risk_level', 0.5)
        
        # Higher utility when risk is high
        utility = min(1.0, risk_level * 2)
        
        return utility
    
    async def _calculate_option_risk(self, option: DecisionOption, context: DecisionContext) -> Dict[str, float]:
        """Calculate risk metrics for a decision option"""
        
        base_risk = context.risk_metrics.copy()
        
        # Adjust risk based on option type
        if option.option_id == "rebalance_portfolio":
            base_risk['execution_risk'] = 0.1
            base_risk['market_impact'] = 0.05
        elif option.option_id == "adjust_allocation":
            base_risk['transition_risk'] = 0.15
            base_risk['timing_risk'] = 0.1
        elif option.option_id == "adjust_risk_exposure":
            base_risk['model_risk'] = 0.2
        elif option.option_id == "tactical_adjustment":
            base_risk['timing_risk'] = 0.3
            base_risk['liquidity_risk'] = 0.1
        elif option.option_id == "emergency_risk_reduction":
            base_risk['execution_risk'] = 0.4
            base_risk['cost_risk'] = 0.2
        
        # Calculate max drawdown estimate
        base_risk['max_drawdown'] = base_risk.get('portfolio_risk', 0.15) * 1.5
        
        return base_risk
    
    async def _calculate_allocation_shift(self, context: DecisionContext) -> Dict[str, float]:
        """Calculate allocation shift based on market conditions"""
        
        current_allocation = context.portfolio_state.get('current_allocation', {})
        target_allocation = await self._calculate_target_allocation(context)
        
        shift = {}
        for asset in set(current_allocation.keys()) | set(target_allocation.keys()):
            current = current_allocation.get(asset, 0.0)
            target = target_allocation.get(asset, 0.0)
            shift[asset] = target - current
        
        return shift
    
    async def _calculate_risk_adjustment(self, context: DecisionContext) -> float:
        """Calculate risk adjustment factor"""
        
        current_risk = context.risk_metrics.get('portfolio_risk', 0.15)
        target_risk = self.risk_parameters['max_drawdown_tolerance']
        
        return (target_risk - current_risk) / current_risk
    
    def _generate_decision_reasoning(self, option: DecisionOption, context: DecisionContext) -> str:
        """Generate reasoning for the selected decision"""
        
        reasoning_templates = {
            "rebalance_portfolio": "Portfolio rebalancing recommended to maintain target allocation and manage risk.",
            "adjust_allocation": "Asset allocation adjustment suggested to align with current market regime.",
            "adjust_risk_exposure": "Risk exposure adjustment proposed to maintain target risk levels.",
            "tactical_adjustment": "Tactical opportunity identified for short-term position adjustment.",
            "operational_optimization": "Operational optimization recommended to improve execution efficiency.",
            "emergency_risk_reduction": "Emergency risk reduction measures required due to elevated market risk."
        }
        
        base_reasoning = reasoning_templates.get(option.option_id, "Strategic decision made based on comprehensive analysis.")
        
        # Add context-specific details
        market_regime = context.market_conditions.get('regime', 'unknown')
        risk_level = context.risk_metrics.get('risk_level', 0.5)
        
        details = f" Market regime: {market_regime}, Risk level: {risk_level:.2f}, Confidence: {option.confidence:.2f}."
        
        return base_reasoning + details
    
    async def _create_execution_timeline(self, option: DecisionOption, context: DecisionContext) -> Dict[str, datetime]:
        """Create execution timeline for the decision"""
        
        base_time = datetime.now()
        
        timeline = {
            'decision_made': base_time,
            'execution_start': base_time + timedelta(seconds=30),
            'expected_completion': base_time + timedelta(seconds=option.resource_requirements['execution_time']),
            'review_period': base_time + timedelta(hours=1)
        }
        
        return timeline
    
    async def _create_fallback_plan(self, option: DecisionOption, context: DecisionContext) -> Dict[str, Any]:
        """Create fallback plan for the decision"""
        
        fallback_actions = {
            "rebalance_portfolio": "Partial rebalancing with reduced position sizes",
            "adjust_allocation": "Gradual allocation shift over extended period",
            "adjust_risk_exposure": "Incremental risk adjustment with closer monitoring",
            "tactical_adjustment": "Reduce position size or cancel trade",
            "operational_optimization": "Revert to previous operational parameters",
            "emergency_risk_reduction": "Immediate full position liquidation"
        }
        
        return {
            'fallback_action': fallback_actions.get(option.option_id, "Monitor and reassess"),
            'trigger_conditions': ['execution_failure', 'market_regime_change', 'risk_threshold_breach'],
            'monitoring_frequency': 'high',
            'escalation_protocol': 'immediate'
        }
    
    async def _calculate_context_similarity(self, context: DecisionContext) -> float:
        """Calculate similarity to historical decision contexts"""
        
        if not self.decision_history:
            return 0.5  # Default similarity for no history
        
        # Simple similarity calculation based on market conditions
        current_regime = context.market_conditions.get('regime', 'neutral')
        current_volatility = context.market_conditions.get('volatility', 0.2)
        
        similarities = []
        
        for decision in list(self.decision_history)[-10:]:  # Last 10 decisions
            # Extract context from decision metadata
            decision_context = decision.metadata.get('decision_context', {})
            decision_regime = decision_context.get('market_regime', 'neutral')
            decision_volatility = decision_context.get('volatility', 0.2)
            
            # Calculate regime similarity
            regime_similarity = 1.0 if current_regime == decision_regime else 0.3
            
            # Calculate volatility similarity
            volatility_diff = abs(current_volatility - decision_volatility) / decision_volatility
            volatility_similarity = 1.0 - min(1.0, volatility_diff)
            
            # Combined similarity
            similarity = (regime_similarity + volatility_similarity) / 2
            similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.5
    
    def _calculate_decision_complexity(self, context: DecisionContext) -> float:
        """Calculate complexity of the decision context"""
        
        complexity_factors = []
        
        # Market condition complexity
        regime = context.market_conditions.get('regime', 'neutral')
        regime_complexity = {'bull': 0.3, 'bear': 0.8, 'neutral': 0.5, 'transition': 0.9}.get(regime, 0.5)
        complexity_factors.append(regime_complexity)
        
        # Portfolio complexity
        portfolio_size = len(context.portfolio_state.get('positions', {}))
        portfolio_complexity = min(1.0, portfolio_size / 20)
        complexity_factors.append(portfolio_complexity)
        
        # Risk complexity
        risk_metrics_count = len(context.risk_metrics)
        risk_complexity = min(1.0, risk_metrics_count / 10)
        complexity_factors.append(risk_complexity)
        
        return np.mean(complexity_factors)
    
    async def update_decision_framework(self, new_framework: DecisionFramework):
        """Update the active decision framework"""
        
        if new_framework in self.decision_frameworks:
            self.active_framework = new_framework
            print(f"Updated decision framework to: {new_framework.value}")
        else:
            raise ValueError(f"Unknown decision framework: {new_framework}")
    
    async def learn_from_outcome(self, decision_id: str, outcome: Dict[str, Any]):
        """Learn from decision outcomes to improve future decisions"""
        
        # Find the decision in history
        decision = None
        for d in self.decision_history:
            if d.decision_id == decision_id:
                decision = d
                break
        
        if not decision:
            print(f"Decision {decision_id} not found in history")
            return
        
        # Calculate decision quality
        actual_utility = outcome.get('actual_utility', 0.0)
        expected_utility = decision.selected_option.expected_utility
        utility_deviation = abs(actual_utility - expected_utility)
        
        decision_quality = 1.0 - min(1.0, utility_deviation)
        
        # Update performance metrics
        self.performance_tracker['avg_decision_quality'] = (
            (self.performance_tracker['avg_decision_quality'] * self.performance_tracker['decisions_made'] + decision_quality) /
            (self.performance_tracker['decisions_made'] + 1)
        )
        
        if decision_quality > 0.7:
            self.performance_tracker['successful_decisions'] += 1
        
        # Update learning progress
        self.performance_tracker['learning_progress'] = min(1.0, 
            self.performance_tracker['learning_progress'] + 0.01 * decision_quality
        )
        
        print(f"Learned from decision {decision_id}. Quality: {decision_quality:.3f}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and performance"""
        
        return {
            'agent_id': self.agent_id,
            'capabilities': self.capabilities,
            'risk_appetite': self.risk_appetite.value,
            'active_framework': self.active_framework.value,
            'performance_metrics': self.performance_tracker,
            'recent_decisions': len(self.decision_history),
            'system_health': self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> float:
        """Calculate overall system health"""
        
        health_factors = []
        
        # Decision quality health
        quality_health = self.performance_tracker['avg_decision_quality']
        health_factors.append(quality_health * 0.4)
        
        # Learning progress health
        learning_health = self.performance_tracker['learning_progress']
        health_factors.append(learning_health * 0.3)
        
        # Decision volume health (moderate activity is healthy)
        decision_volume = min(1.0, self.performance_tracker['decisions_made'] / 100)
        health_factors.append(decision_volume * 0.3)
        
        return sum(health_factors)

# Example usage
if __name__ == "__main__":
    # Create decision agent
    agent = DecisionAgent(
        agent_id="strategy_decision_agent_1",
        capabilities=['portfolio_management', 'asset_allocation', 'risk_management', 'tactical_trading'],
        risk_appetite=RiskAppetite.MODERATE
    )
    
    # Create sample decision context
    context = DecisionContext(
        context_id="market_analysis_001",
        timestamp=datetime.now(),
        market_conditions={
            'regime': 'bull',
            'volatility': 0.18,
            'trend_strength': 0.7,
            'liquidity': 'high'
        },
        portfolio_state={
            'current_allocation': {'BTC': 0.35, 'ETH': 0.25, 'SOL': 0.15, 'cash': 0.25},
            'total_value': 1000000,
            'available_capital': 50000,
            'regime_alignment': 0.6
        },
        risk_metrics={
            'portfolio_risk': 0.14,
            'max_drawdown': 0.08,
            'var_95': 0.12,
            'risk_level': 0.4
        },
        constraints={
            'max_execution_time': 600,
            'max_capital': 100000,
            'max_complexity': 0.8
        },
        objectives=['maximize_returns', 'manage_risk', 'maintain_liquidity'],
        metadata={'time_horizon': 'medium_term'}
    )
    
    async def demo():
        # Make strategic decision
        decision = await agent.make_decision(context, DecisionType.STRATEGIC)
        
        print(f"Decision ID: {decision.decision_id}")
        print(f"Selected Option: {decision.selected_option.option_id}")
        print(f"Confidence: {decision.confidence:.3f}")
        print(f"Reasoning: {decision.reasoning}")
        
        # Simulate learning from outcome
        outcome = {'actual_utility': 0.75}
        await agent.learn_from_outcome(decision.decision_id, outcome)
        
        # Get agent status
        status = agent.get_agent_status()
        print(f"Agent Health: {status['system_health']:.3f}")
    
    import asyncio
    asyncio.run(demo())
