"""
QUANTUMNEX v1.0 - DECISION AGENT
Advanced Strategic Decision-Making Agent
Quantum-Speed Strategy Selection and Risk Assessment
"""

import numpy as np
import pandas as pd
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DecisionType(Enum):
    STRATEGIC = "strategic"
    TACTICAL = "tactical" 
    OPERATIONAL = "operational"
    EMERGENCY = "emergency"

class DecisionFramework(Enum):
    UTILITY_MAXIMIZATION = "utility_maximization"
    PROSPECT_THEORY = "prospect_theory"
    BAYESIAN = "bayesian"
    REINFORCEMENT_LEARNING = "reinforcement_learning"

class RiskAppetite(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class DecisionContext:
    context_id: str
    timestamp: datetime
    market_conditions: Dict[str, Any]
    portfolio_state: Dict[str, Any]
    risk_metrics: Dict[str, float]
    constraints: Dict[str, Any]
    objectives: List[str]

@dataclass
class DecisionOption:
    option_id: str
    description: str
    action_plan: Dict[str, Any]
    expected_utility: float
    risk_metrics: Dict[str, float]
    confidence: float

class DecisionAgent:
    """
    Advanced autonomous decision-making agent for QuantumNex
    Formulates strategic decisions using multiple decision frameworks
    """
    
    def __init__(self, agent_id: str, risk_appetite: RiskAppetite = RiskAppetite.MODERATE):
        self.agent_id = agent_id
        self.risk_appetite = risk_appetite
        
        # Decision history and learning
        self.decision_history = []
        self.performance_metrics = {
            'decisions_made': 0,
            'successful_decisions': 0,
            'avg_decision_quality': 0.0
        }
        
        # Risk parameters based on appetite
        self.risk_parameters = self._initialize_risk_parameters()
        
        # Decision frameworks
        self.decision_frameworks = {
            DecisionFramework.UTILITY_MAXIMIZATION: {
                'description': 'Maximize expected utility',
                'evaluate': self._evaluate_utility_maximization
            },
            DecisionFramework.PROSPECT_THEORY: {
                'description': 'Prospect theory with loss aversion',
                'evaluate': self._evaluate_prospect_theory
            },
            DecisionFramework.BAYESIAN: {
                'description': 'Bayesian decision theory',
                'evaluate': self._evaluate_bayesian
            }
        }
        
        self.active_framework = DecisionFramework.UTILITY_MAXIMIZATION
        
        print(f"âœ… Decision Agent {agent_id} initialized with {risk_appetite.value} risk appetite")

    def _initialize_risk_parameters(self) -> Dict[str, Any]:
        """Initialize risk parameters based on risk appetite"""
        risk_profiles = {
            RiskAppetite.CONSERVATIVE: {
                'max_drawdown_tolerance': 0.05,
                'position_size_limit': 0.05,
                'profit_threshold': 0.002,
                'confidence_threshold': 0.8
            },
            RiskAppetite.MODERATE: {
                'max_drawdown_tolerance': 0.10,
                'position_size_limit': 0.10,
                'profit_threshold': 0.0015,
                'confidence_threshold': 0.7
            },
            RiskAppetite.AGGRESSIVE: {
                'max_drawdown_tolerance': 0.15,
                'position_size_limit': 0.15,
                'profit_threshold': 0.001,
                'confidence_threshold': 0.6
            }
        }
        
        return risk_profiles.get(self.risk_appetite, risk_profiles[RiskAppetite.MODERATE])

    async def make_decision(self, context: DecisionContext) -> DecisionOption:
        """
        Make strategic decision based on context and active framework
        """
        print(f"í¾¯ Decision Agent making decision for context: {context.context_id}")
        
        # Generate decision options
        decision_options = await self._generate_decision_options(context)
        
        if not decision_options:
            raise ValueError("No valid decision options generated")
        
        # Evaluate options using active framework
        framework = self.decision_frameworks[self.active_framework]
        evaluated_options = await framework['evaluate'](decision_options, context)
        
        # Select best option
        selected_option = self._select_best_option(evaluated_options, context)
        
        # Update performance metrics
        self.decision_history.append({
            'timestamp': datetime.now(),
            'context': context,
            'decision': selected_option,
            'framework': self.active_framework
        })
        
        self.performance_metrics['decisions_made'] += 1
        
        print(f"âœ… Decision made: {selected_option.option_id} with confidence {selected_option.confidence:.3f}")
        
        return selected_option

    async def _generate_decision_options(self, context: DecisionContext) -> List[DecisionOption]:
        """Generate possible decision options based on context"""
        options = []
        
        # Market regime analysis
        market_regime = context.market_conditions.get('regime', 'neutral')
        volatility = context.market_conditions.get('volatility', 0.2)
        
        # Option 1: Aggressive arbitrage (high risk, high reward)
        if volatility > 0.15 and market_regime in ['volatile', 'transition']:
            aggressive_option = DecisionOption(
                option_id="aggressive_arbitrage",
                description="High-frequency arbitrage in volatile market",
                action_plan={
                    'strategy': 'aggressive_arbitrage',
                    'position_size': self.risk_parameters['position_size_limit'] * 0.8,
                    'profit_target': self.risk_parameters['profit_threshold'] * 2,
                    'stop_loss': self.risk_parameters['max_drawdown_tolerance'] * 0.5
                },
                expected_utility=0.0,
                risk_metrics={'volatility_exposure': 0.8, 'liquidity_risk': 0.6},
                confidence=0.0
            )
            options.append(aggressive_option)
        
        # Option 2: Conservative arbitrage (low risk, steady profit)
        conservative_option = DecisionOption(
            option_id="conservative_arbitrage",
            description="Conservative cross-chain arbitrage",
            action_plan={
                'strategy': 'conservative_arbitrage',
                'position_size': self.risk_parameters['position_size_limit'] * 0.4,
                'profit_target': self.risk_parameters['profit_threshold'],
                'stop_loss': self.risk_parameters['max_drawdown_tolerance'] * 0.3
            },
            expected_utility=0.0,
            risk_metrics={'volatility_exposure': 0.3, 'liquidity_risk': 0.2},
            confidence=0.0
        )
        options.append(conservative_option)
        
        # Option 3: Market making (steady income)
        if market_regime in ['stable', 'bull']:
            market_making_option = DecisionOption(
                option_id="market_making",
                description="Automated market making strategy",
                action_plan={
                    'strategy': 'market_making',
                    'position_size': self.risk_parameters['position_size_limit'] * 0.6,
                    'spread_target': 0.002,
                    'inventory_management': 'dynamic'
                },
                expected_utility=0.0,
                risk_metrics={'inventory_risk': 0.5, 'impermanent_loss_risk': 0.4},
                confidence=0.0
            )
            options.append(market_making_option)
        
        # Calculate metrics for each option
        for option in options:
            option.expected_utility = await self._calculate_expected_utility(option, context)
            option.confidence = await self._calculate_confidence(option, context)
        
        return options

    async def _evaluate_utility_maximization(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using utility maximization framework"""
        evaluated_options = []
        
        for option in options:
            # Risk-adjusted utility calculation
            risk_adjustment = 1.0 - sum(option.risk_metrics.values()) / len(option.risk_metrics)
            risk_adjusted_utility = option.expected_utility * risk_adjustment
            
            # Apply time preference (future utility discount)
            time_preference = 0.95
            discounted_utility = risk_adjusted_utility * time_preference
            
            option.expected_utility = discounted_utility
            evaluated_options.append(option)
        
        return evaluated_options

    async def _evaluate_prospect_theory(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using prospect theory"""
        evaluated_options = []
        loss_aversion = 2.25  # Standard loss aversion coefficient
        
        for option in options:
            if option.expected_utility >= 0:
                # Gains domain
                value = option.expected_utility ** 0.88
            else:
                # Losses domain (apply loss aversion)
                value = -loss_aversion * ((-option.expected_utility) ** 1.0)
            
            option.expected_utility = value
            evaluated_options.append(option)
        
        return evaluated_options

    async def _evaluate_bayesian(self, options: List[DecisionOption], context: DecisionContext) -> List[DecisionOption]:
        """Evaluate options using Bayesian decision theory"""
        evaluated_options = []
        
        # Prior success rate from history
        prior_success_rate = self.performance_metrics.get('success_rate', 0.5)
        
        for option in options:
            # Bayesian updating of confidence
            option_likelihood = option.confidence
            posterior_confidence = (prior_success_rate * option_likelihood) / (
                prior_success_rate * option_likelihood + (1 - prior_success_rate) * (1 - option_likelihood)
            )
            
            option.confidence = posterior_confidence
            option.expected_utility *= posterior_confidence
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
        
        print(f"í¿† Selected option: {best_option.option_id} with score {best_score:.3f}")
        
        return best_option

    def _calculate_option_score(self, option: DecisionOption, context: DecisionContext) -> float:
        """Calculate comprehensive score for an option"""
        weights = {
            'utility': 0.5,
            'risk': 0.3,
            'confidence': 0.2
        }
        
        # Normalize components
        utility_score = max(0.0, min(1.0, option.expected_utility * 10))  # Scale utility
        
        # Risk score (higher is better - lower risk)
        avg_risk = sum(option.risk_metrics.values()) / len(option.risk_metrics)
        risk_score = 1.0 - avg_risk
        
        confidence_score = option.confidence
        
        # Calculate weighted score
        total_score = (
            weights['utility'] * utility_score +
            weights['risk'] * risk_score +
            weights['confidence'] * confidence_score
        )
        
        return total_score

    async def _calculate_expected_utility(self, option: DecisionOption, context: DecisionContext) -> float:
        """Calculate expected utility for a decision option"""
        base_utility = 0.0
        
        # Calculate based on option type and market conditions
        if option.option_id == "aggressive_arbitrage":
            base_utility = 0.8  # High potential in volatile markets
        elif option.option_id == "conservative_arbitrage":
            base_utility = 0.6  # Steady but lower returns
        elif option.option_id == "market_making":
            base_utility = 0.5  # Consistent but limited upside
        
        # Adjust for market conditions
        market_regime = context.market_conditions.get('regime', 'neutral')
        if market_regime == 'volatile' and option.option_id == "aggressive_arbitrage":
            base_utility *= 1.3
        elif market_regime == 'stable' and option.option_id == "market_making":
            base_utility *= 1.2
        
        return max(-1.0, min(1.0, base_utility))

    async def _calculate_confidence(self, option: DecisionOption, context: DecisionContext) -> float:
        """Calculate confidence score for an option"""
        base_confidence = 0.7
        
        # Adjust based on risk metrics
        risk_factor = 1.0 - sum(option.risk_metrics.values()) / len(option.risk_metrics)
        
        # Market condition adjustment
        market_volatility = context.market_conditions.get('volatility', 0.2)
        volatility_factor = 1.0 - min(1.0, market_volatility * 2)
        
        confidence = base_confidence * risk_factor * volatility_factor
        
        return max(0.1, min(0.95, confidence))

    def update_decision_framework(self, new_framework: DecisionFramework):
        """Update the active decision framework"""
        if new_framework in self.decision_frameworks:
            self.active_framework = new_framework
            print(f"í´„ Updated decision framework to: {new_framework.value}")
        else:
            raise ValueError(f"Unknown decision framework: {new_framework}")

    async def learn_from_outcome(self, decision_id: str, outcome: Dict[str, Any]):
        """Learn from decision outcomes to improve future decisions"""
        # Find the decision in history
        decision_record = next(
            (d for d in self.decision_history if d['decision'].option_id == decision_id), 
            None
        )
        
        if not decision_record:
            print(f"Decision {decision_id} not found in history")
            return
        
        # Calculate decision quality
        actual_utility = outcome.get('actual_utility', 0.0)
        expected_utility = decision_record['decision'].expected_utility
        utility_deviation = abs(actual_utility - expected_utility)
        
        decision_quality = 1.0 - min(1.0, utility_deviation)
        
        # Update performance metrics
        self.performance_metrics['avg_decision_quality'] = (
            (self.performance_metrics['avg_decision_quality'] * self.performance_metrics['decisions_made'] + decision_quality) /
            (self.performance_metrics['decisions_made'] + 1)
        )
        
        if decision_quality > 0.7:
            self.performance_metrics['successful_decisions'] += 1
        
        print(f"í³š Learned from decision {decision_id}. Quality: {decision_quality:.3f}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and performance"""
        return {
            'agent_id': self.agent_id,
            'risk_appetite': self.risk_appetite.value,
            'active_framework': self.active_framework.value,
            'performance_metrics': self.performance_metrics,
            'recent_decisions': len(self.decision_history),
            'decision_quality': self.performance_metrics['avg_decision_quality']
        }

# Example usage
async def main():
    """Example usage of Decision Agent"""
    agent = DecisionAgent("quantum_decision_1", RiskAppetite.MODERATE)
    
    # Create sample decision context
    context = DecisionContext(
        context_id="market_analysis_001",
        timestamp=datetime.now(),
        market_conditions={
            'regime': 'volatile',
            'volatility': 0.25,
            'trend': 'mixed',
            'liquidity': 'high'
        },
        portfolio_state={
            'total_value': 100000,
            'available_capital': 25000,
            'current_positions': 3
        },
        risk_metrics={
            'current_drawdown': 0.02,
            'var_95': 0.08,
            'sharpe_ratio': 1.2
        },
        constraints={
            'max_drawdown': 0.10,
            'max_position_size': 0.15
        },
        objectives=['maximize_returns', 'manage_risk', 'maintain_liquidity']
    )
    
    # Make decision
    decision = await agent.make_decision(context)
    
    print(f"Decision: {decision.option_id}")
    print(f"Confidence: {decision.confidence:.3f}")
    print(f"Expected Utility: {decision.expected_utility:.3f}")
    
    # Show agent status
    status = agent.get_agent_status()
    print(f"Agent Status: {status}")

if __name__ == "__main__":
    asyncio.run(main())
