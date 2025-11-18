"""
AI-NEXUS v5.0 - ADAPTIVE MUTATOR MODULE
Advanced Strategy Mutation and Genetic Optimization
Intelligent mutation algorithms for strategy evolution
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random
import json
from copy import deepcopy
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class MutationType(Enum):
    PARAMETER_TWEAK = "parameter_tweak"
    STRATEGY_COMBINATION = "strategy_combination"
    TOPOLOGY_MUTATION = "topology_mutation"
    BEHAVIORAL_SHIFT = "behavioral_shift"
    INNOVATION = "innovation"

class MutationStrength(Enum):
    CONSERVATIVE = 0.1
    MODERATE = 0.3
    AGGRESSIVE = 0.5
    RADICAL = 0.8

@dataclass
class StrategyGene:
    gene_id: str
    strategy_type: str
    parameters: Dict[str, float]
    topology: Dict[str, Any]
    behavioral_traits: Dict[str, float]
    performance_metrics: Dict[str, float]
    creation_timestamp: datetime
    parent_ids: List[str]
    mutation_history: List[str]

@dataclass
class MutationResult:
    mutation_id: str
    original_gene: StrategyGene
    mutated_gene: StrategyGene
    mutation_type: MutationType
    strength: MutationStrength
    success_probability: float
    expected_improvement: float
    risk_assessment: Dict[str, float]

class AdaptiveMutator:
    """
    Advanced strategy mutation system with intelligent adaptation
    Implements sophisticated genetic algorithms for strategy evolution
    """
    
    def __init__(self):
        self.mutation_history = deque(maxlen=1000)
        self.performance_tracker = {}
        self.innovation_catalog = {}
        
        # Mutation parameters
        self.mutation_params = {
            'base_mutation_rate': 0.15,
            'adaptive_rate_adjustment': True,
            'diversity_threshold': 0.3,
            'innovation_probability': 0.05,
            'elite_preservation_rate': 0.1,
            'catastrophic_mutation_rate': 0.02
        }
        
        # Strategy parameter boundaries
        self.parameter_bounds = {
            'aggressiveness': (0.1, 0.9),
            'risk_tolerance': (0.05, 0.8),
            'lookback_period': (5, 200),
            'signal_threshold': (0.01, 0.5),
            'position_size': (0.01, 0.3),
            'stop_loss': (0.01, 0.2),
            'take_profit': (0.05, 0.5)
        }
        
        # Behavioral trait mappings
        self.behavioral_traits = {
            'market_regime_adaptation': (0.0, 1.0),
            'volatility_response': (0.0, 1.0),
            'momentum_sensitivity': (0.0, 1.0),
            'mean_reversion_bias': (0.0, 1.0),
            'trend_following_strength': (0.0, 1.0)
        }
        
        # Initialize mutation operators
        self._initialize_mutation_operators()
    
    def _initialize_mutation_operators(self):
        """Initialize various mutation operators"""
        
        self.mutation_operators = {
            MutationType.PARAMETER_TWEAK: self._parameter_tweak_mutation,
            MutationType.STRATEGY_COMBINATION: self._strategy_combination_mutation,
            MutationType.TOPOLOGY_MUTATION: self._topology_mutation,
            MutationType.BEHAVIORAL_SHIFT: self._behavioral_shift_mutation,
            MutationType.INNOVATION: self._innovation_mutation
        }
        
        # Mutation strength multipliers
        self.strength_multipliers = {
            MutationStrength.CONSERVATIVE: 0.1,
            MutationStrength.MODERATE: 0.3,
            MutationStrength.AGGRESSIVE: 0.5,
            MutationStrength.RADICAL: 0.8
        }
    
    def adaptive_mutation_rate(self, strategy_performance: Dict[str, float]) -> float:
        """Calculate adaptive mutation rate based on performance"""
        
        base_rate = self.mutation_params['base_mutation_rate']
        
        if not self.mutation_params['adaptive_rate_adjustment']:
            return base_rate
        
        # Adjust mutation rate based on performance metrics
        sharpe_ratio = strategy_performance.get('sharpe_ratio', 0)
        max_drawdown = strategy_performance.get('max_drawdown', 0)
        win_rate = strategy_performance.get('win_rate', 0.5)
        
        # Higher mutation for poor performers
        performance_score = (sharpe_ratio * 0.4 + 
                           (1 - min(max_drawdown, 1)) * 0.3 + 
                           win_rate * 0.3)
        
        if performance_score < 0.3:
            # Poor performance - increase mutation
            return min(0.5, base_rate * 2.0)
        elif performance_score > 0.7:
            # Good performance - conservative mutation
            return max(0.05, base_rate * 0.5)
        else:
            return base_rate
    
    def select_mutation_type(self, strategy_gene: StrategyGene) -> Tuple[MutationType, MutationStrength]:
        """Intelligently select mutation type and strength"""
        
        # Analyze strategy characteristics
        param_volatility = self._calculate_parameter_volatility(strategy_gene)
        behavioral_diversity = self._calculate_behavioral_diversity(strategy_gene)
        performance_stability = strategy_gene.performance_metrics.get('stability_score', 0.5)
        
        # Determine mutation type
        if random.random() < self.mutation_params['innovation_probability']:
            mutation_type = MutationType.INNOVATION
        elif param_volatility > 0.7:
            mutation_type = MutationType.BEHAVIORAL_SHIFT
        elif behavioral_diversity < self.mutation_params['diversity_threshold']:
            mutation_type = MutationType.TOPOLOGY_MUTATION
        elif len(strategy_gene.parent_ids) >= 2:
            mutation_type = MutationType.STRATEGY_COMBINATION
        else:
            mutation_type = MutationType.PARAMETER_TWEAK
        
        # Determine mutation strength
        if performance_stability > 0.8:
            strength = MutationStrength.CONSERVATIVE
        elif performance_stability > 0.5:
            strength = MutationStrength.MODERATE
        elif performance_stability > 0.2:
            strength = MutationStrength.AGGRESSIVE
        else:
            strength = MutationStrength.RADICAL
        
        return mutation_type, strength
    
    def mutate_strategy(self, strategy_gene: StrategyGene) -> MutationResult:
        """Perform intelligent strategy mutation"""
        
        # Calculate mutation probability
        mutation_rate = self.adaptive_mutation_rate(strategy_gene.performance_metrics)
        
        if random.random() > mutation_rate:
            # No mutation occurred
            return None
        
        # Select mutation type and strength
        mutation_type, strength = self.select_mutation_type(strategy_gene)
        
        # Perform mutation
        mutation_operator = self.mutation_operators[mutation_type]
        mutated_gene = mutation_operator(strategy_gene, strength)
        
        # Calculate success probability
        success_prob = self._calculate_success_probability(strategy_gene, mutated_gene, mutation_type)
        
        # Calculate expected improvement
        expected_improvement = self._calculate_expected_improvement(strategy_gene, mutated_gene)
        
        # Risk assessment
        risk_assessment = self._assess_mutation_risk(strategy_gene, mutated_gene)
        
        # Create mutation result
        mutation_result = MutationResult(
            mutation_id=f"mut_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            original_gene=strategy_gene,
            mutated_gene=mutated_gene,
            mutation_type=mutation_type,
            strength=strength,
            success_probability=success_prob,
            expected_improvement=expected_improvement,
            risk_assessment=risk_assessment
        )
        
        self.mutation_history.append(mutation_result)
        
        return mutation_result
    
    def _parameter_tweak_mutation(self, gene: StrategyGene, strength: MutationStrength) -> StrategyGene:
        """Perform parameter tweak mutation"""
        
        mutated_gene = deepcopy(gene)
        strength_multiplier = self.strength_multipliers[strength]
        
        # Select parameters to mutate
        params_to_mutate = random.sample(
            list(gene.parameters.keys()), 
            max(1, int(len(gene.parameters) * strength_multiplier))
        )
        
        for param in params_to_mutate:
            if param in self.parameter_bounds:
                current_value = gene.parameters[param]
                min_val, max_val = self.parameter_bounds[param]
                
                # Calculate mutation range
                value_range = max_val - min_val
                mutation_range = value_range * strength_multiplier
                
                # Apply mutation
                mutation = random.uniform(-mutation_range, mutation_range)
                new_value = max(min_val, min(max_val, current_value + mutation))
                
                mutated_gene.parameters[param] = new_value
        
        # Update mutation history
        mutated_gene.mutation_history.append(f"parameter_tweak_{strength.value}")
        mutated_gene.creation_timestamp = datetime.now()
        
        return mutated_gene
    
    def _strategy_combination_mutation(self, gene: StrategyGene, strength: MutationStrength) -> StrategyGene:
        """Combine strategies from parent genes"""
        
        # This would typically combine with another strategy gene
        # For now, create a hybrid of current parameters
        mutated_gene = deepcopy(gene)
        strength_multiplier = self.strength_multipliers[strength]
        
        # Create hybrid parameters
        for param in mutated_gene.parameters:
            if param in self.parameter_bounds:
                current_val = gene.parameters[param]
                min_val, max_val = self.parameter_bounds[param]
                
                # Blend with a virtual "partner" strategy
                partner_val = random.uniform(min_val, max_val)
                blend_ratio = random.uniform(0.2, 0.8) * strength_multiplier
                
                new_value = current_val * (1 - blend_ratio) + partner_val * blend_ratio
                mutated_gene.parameters[param] = max(min_val, min(max_val, new_value))
        
        # Update behavioral traits
        for trait in mutated_gene.behavioral_traits:
            current_trait = gene.behavioral_traits[trait]
            min_val, max_val = self.behavioral_traits.get(trait, (0.0, 1.0))
            
            # Modify behavioral trait
            trait_mutation = random.uniform(-0.3, 0.3) * strength_multiplier
            new_trait = max(min_val, min(max_val, current_trait + trait_mutation))
            mutated_gene.behavioral_traits[trait] = new_trait
        
        mutated_gene.mutation_history.append(f"strategy_combination_{strength.value}")
        mutated_gene.creation_timestamp = datetime.now()
        
        return mutated_gene
    
    def _topology_mutation(self, gene: StrategyGene, strength: MutationStrength) -> StrategyGene:
        """Mutate strategy topology and structure"""
        
        mutated_gene = deepcopy(gene)
        strength_multiplier = self.strength_multipliers[strength]
        
        # Modify topology elements
        topology_keys = list(gene.topology.keys())
        if topology_keys:
            elements_to_mutate = random.sample(
                topology_keys, 
                max(1, int(len(topology_keys) * strength_multiplier * 0.5))
            )
            
            for element in elements_to_mutate:
                if isinstance(gene.topology[element], (int, float)):
                    # Numeric topology parameter
                    current_val = gene.topology[element]
                    mutation = random.uniform(-0.5, 0.5) * strength_multiplier
                    mutated_gene.topology[element] = current_val + mutation
                elif isinstance(gene.topology[element], bool):
                    # Boolean toggle
                    if random.random() < strength_multiplier:
                        mutated_gene.topology[element] = not gene.topology[element]
                elif isinstance(gene.topology[element], str):
                    # String/enum mutation
                    if random.random() < strength_multiplier * 0.3:
                        # Simple string mutation - in practice would use valid alternatives
                        mutated_gene.topology[element] = f"mutated_{gene.topology[element]}"
        
        mutated_gene.mutation_history.append(f"topology_mutation_{strength.value}")
        mutated_gene.creation_timestamp = datetime.now()
        
        return mutated_gene
    
    def _behavioral_shift_mutation(self, gene: StrategyGene, strength: MutationStrength) -> StrategyGene:
        """Shift behavioral traits and characteristics"""
        
        mutated_gene = deepcopy(gene)
        strength_multiplier = self.strength_multipliers[strength]
        
        # Significant shifts in behavioral traits
        traits_to_shift = random.sample(
            list(gene.behavioral_traits.keys()),
            max(1, int(len(gene.behavioral_traits) * strength_multiplier))
        )
        
        for trait in traits_to_shift:
            current_val = gene.behavioral_traits[trait]
            min_val, max_val = self.behavioral_traits.get(trait, (0.0, 1.0))
            
            # Behavioral shift (larger than parameter tweaks)
            shift_magnitude = random.uniform(0.2, 0.8) * strength_multiplier
            shift_direction = random.choice([-1, 1])
            
            new_val = current_val + (shift_magnitude * shift_direction)
            mutated_gene.behavioral_traits[trait] = max(min_val, min(max_val, new_val))
        
        # Correlated parameter adjustments
        for param in mutated_gene.parameters:
            if random.random() < strength_multiplier * 0.5:
                current_val = gene.parameters[param]
                min_val, max_val = self.parameter_bounds.get(param, (current_val * 0.5, current_val * 1.5))
                
                correlated_shift = random.uniform(-0.2, 0.2) * strength_multiplier
                new_val = current_val + (correlated_shift * (max_val - min_val))
                mutated_gene.parameters[param] = max(min_val, min(max_val, new_val))
        
        mutated_gene.mutation_history.append(f"behavioral_shift_{strength.value}")
        mutated_gene.creation_timestamp = datetime.now()
        
        return mutated_gene
    
    def _innovation_mutation(self, gene: StrategyGene, strength: MutationStrength) -> StrategyGene:
        """Introduce innovative changes and novel approaches"""
        
        mutated_gene = deepcopy(gene)
        strength_multiplier = self.strength_multipliers[strength]
        
        # Radical parameter changes
        for param in mutated_gene.parameters:
            if random.random() < strength_multiplier:
                min_val, max_val = self.parameter_bounds.get(param, (0.0, 1.0))
                # Innovative jump to new value
                new_val = random.uniform(min_val, max_val)
                mutated_gene.parameters[param] = new_val
        
        # Introduce novel behavioral traits
        novel_traits = ['adaptive_learning_rate', 'regime_switch_sensitivity', 'market_microstructure_awareness']
        for novel_trait in novel_traits:
            if novel_trait not in mutated_gene.behavioral_traits and random.random() < strength_multiplier * 0.3:
                mutated_gene.behavioral_traits[novel_trait] = random.uniform(0.0, 1.0)
        
        # Topology innovations
        if random.random() < strength_multiplier * 0.5:
            innovative_elements = ['neural_embedding', 'attention_mechanism', 'multi_timeframe_fusion']
            for element in innovative_elements:
                if element not in mutated_gene.topology:
                    mutated_gene.topology[element] = random.choice([True, False])
        
        mutated_gene.mutation_history.append(f"innovation_{strength.value}")
        mutated_gene.creation_timestamp = datetime.now()
        
        # Record innovation
        innovation_id = f"innov_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.innovation_catalog[innovation_id] = {
            'timestamp': datetime.now(),
            'original_gene_id': gene.gene_id,
            'innovation_type': 'strategy_innovation',
            'changes_made': list(mutated_gene.parameters.keys())[:3]  # Sample of changes
        }
        
        return mutated_gene
    
    def _calculate_parameter_volatility(self, gene: StrategyGene) -> float:
        """Calculate volatility of strategy parameters"""
        
        if not gene.parameters:
            return 0.0
        
        param_values = list(gene.parameters.values())
        return np.std(param_values) if len(param_values) > 1 else 0.0
    
    def _calculate_behavioral_diversity(self, gene: StrategyGene) -> float:
        """Calculate diversity of behavioral traits"""
        
        if not gene.behavioral_traits:
            return 0.0
        
        trait_values = list(gene.behavioral_traits.values())
        unique_ratio = len(set(trait_values)) / len(trait_values)
        value_range = max(trait_values) - min(trait_values) if trait_values else 0.0
        
        return (unique_ratio + value_range) / 2
    
    def _calculate_success_probability(self, original: StrategyGene, mutated: StrategyGene, 
                                    mutation_type: MutationType) -> float:
        """Calculate probability of mutation success"""
        
        base_probability = 0.5
        
        # Adjust based on mutation type
        type_modifiers = {
            MutationType.PARAMETER_TWEAK: 0.7,
            MutationType.STRATEGY_COMBINATION: 0.6,
            MutationType.TOPOLOGY_MUTATION: 0.4,
            MutationType.BEHAVIORAL_SHIFT: 0.5,
            MutationType.INNOVATION: 0.3
        }
        
        base_probability *= type_modifiers.get(mutation_type, 0.5)
        
        # Adjust based on original performance
        original_performance = original.performance_metrics.get('sharpe_ratio', 0)
        if original_performance > 1.0:
            base_probability *= 0.8  # Good strategies harder to improve
        elif original_performance < 0:
            base_probability *= 1.2  # Poor strategies easier to improve
        
        return min(0.95, max(0.05, base_probability))
    
    def _calculate_expected_improvement(self, original: StrategyGene, mutated: StrategyGene) -> float:
        """Calculate expected performance improvement"""
        
        # Simplified improvement estimation
        original_sharpe = original.performance_metrics.get('sharpe_ratio', 0)
        
        # Estimate based on parameter changes and behavioral shifts
        param_changes = 0
        for param in original.parameters:
            if param in mutated.parameters:
                change = abs(original.parameters[param] - mutated.parameters[param])
                param_changes += change
        
        behavioral_changes = 0
        for trait in original.behavioral_traits:
            if trait in mutated.behavioral_traits:
                change = abs(original.behavioral_traits[trait] - mutated.behavioral_traits[trait])
                behavioral_changes += change
        
        total_changes = param_changes + behavioral_changes
        expected_improvement = total_changes * 0.1  # Simplified model
        
        return expected_improvement
    
    def _assess_mutation_risk(self, original: StrategyGene, mutated: StrategyGene) -> Dict[str, float]:
        """Assess risks associated with mutation"""
        
        risk_factors = {}
        
        # Parameter boundary risk
        boundary_violations = 0
        for param, value in mutated.parameters.items():
            if param in self.parameter_bounds:
                min_val, max_val = self.parameter_bounds[param]
                if value < min_val or value > max_val:
                    boundary_violations += 1
        
        risk_factors['boundary_risk'] = boundary_violations / len(mutated.parameters) if mutated.parameters else 0.0
        
        # Behavioral extreme risk
        extreme_traits = 0
        for trait, value in mutated.behavioral_traits.items():
            if value < 0.1 or value > 0.9:
                extreme_traits += 1
        
        risk_factors['extremism_risk'] = extreme_traits / len(mutated.behavioral_traits) if mutated.behavioral_traits else 0.0
        
        # Mutation magnitude risk
        total_param_change = 0
        for param in original.parameters:
            if param in mutated.parameters:
                change = abs(original.parameters[param] - mutated.parameters[param])
                total_param_change += change
        
        avg_param_change = total_param_change / len(original.parameters) if original.parameters else 0.0
        risk_factors['magnitude_risk'] = min(1.0, avg_param_change * 5)
        
        # Overall risk score
        risk_factors['overall_risk'] = (
            risk_factors['boundary_risk'] * 0.3 +
            risk_factors['extremism_risk'] * 0.3 +
            risk_factors['magnitude_risk'] * 0.4
        )
        
        return risk_factors
    
    def get_mutation_statistics(self) -> Dict[str, Any]:
        """Get statistics about mutation performance"""
        
        if not self.mutation_history:
            return {'total_mutations': 0, 'success_rate': 0.0}
        
        successful_mutations = [
            m for m in self.mutation_history 
            if m.expected_improvement > 0 and m.risk_assessment['overall_risk'] < 0.7
        ]
        
        success_rate = len(successful_mutations) / len(self.mutation_history)
        
        return {
            'total_mutations': len(self.mutation_history),
            'success_rate': success_rate,
            'mutation_type_distribution': self._get_mutation_type_distribution(),
            'avg_expected_improvement': np.mean([m.expected_improvement for m in self.mutation_history]),
            'avg_risk_score': np.mean([m.risk_assessment['overall_risk'] for m in self.mutation_history])
        }
    
    def _get_mutation_type_distribution(self) -> Dict[str, float]:
        """Get distribution of mutation types"""
        
        type_counts = {}
        for mutation in self.mutation_history:
            mutation_type = mutation.mutation_type.value
            type_counts[mutation_type] = type_counts.get(mutation_type, 0) + 1
        
        total = len(self.mutation_history)
        if total == 0:
            return {}
        
        return {mtype: count/total for mtype, count in type_counts.items()}
    
    def optimize_mutation_parameters(self, performance_data: Dict[str, List[float]]):
        """Optimize mutation parameters based on historical performance"""
        
        # Analyze which mutation types and strengths perform best
        successful_mutations = [
            m for m in self.mutation_history 
            if m.expected_improvement > 0.1 and m.risk_assessment['overall_risk'] < 0.5
        ]
        
        if successful_mutations:
            # Adjust base mutation rate based on success
            success_rate = len(successful_mutations) / len(self.mutation_history)
            if success_rate > 0.6:
                # High success - increase mutation rate
                self.mutation_params['base_mutation_rate'] = min(
                    0.3, self.mutation_params['base_mutation_rate'] * 1.1
                )
            elif success_rate < 0.3:
                # Low success - decrease mutation rate
                self.mutation_params['base_mutation_rate'] = max(
                    0.05, self.mutation_params['base_mutation_rate'] * 0.9
                )
            
            # Adjust innovation probability
            innovation_success = [
                m for m in successful_mutations 
                if m.mutation_type == MutationType.INNOVATION
            ]
            if innovation_success:
                innovation_rate = len(innovation_success) / len(successful_mutations)
                self.mutation_params['innovation_probability'] = min(
                    0.1, max(0.01, innovation_rate)
                )

# Example usage and testing
if __name__ == "__main__":
    # Create adaptive mutator
    mutator = AdaptiveMutator()
    
    # Create sample strategy gene
    sample_gene = StrategyGene(
        gene_id="gene_001",
        strategy_type="momentum_arbitrage",
        parameters={
            'aggressiveness': 0.5,
            'risk_tolerance': 0.2,
            'lookback_period': 50,
            'signal_threshold': 0.1,
            'position_size': 0.15,
            'stop_loss': 0.05,
            'take_profit': 0.2
        },
        topology={
            'use_ml_predictions': True,
            'multi_timeframe': True,
            'correlation_filtering': False
        },
        behavioral_traits={
            'market_regime_adaptation': 0.6,
            'volatility_response': 0.4,
            'momentum_sensitivity': 0.8,
            'mean_reversion_bias': 0.2,
            'trend_following_strength': 0.7
        },
        performance_metrics={
            'sharpe_ratio': 1.2,
            'max_drawdown': 0.15,
            'win_rate': 0.55,
            'stability_score': 0.7
        },
        creation_timestamp=datetime.now(),
        parent_ids=[],
        mutation_history=[]
    )
    
    # Perform mutation
    mutation_result = mutator.mutate_strategy(sample_gene)
    
    if mutation_result:
        print(f"Mutation performed: {mutation_result.mutation_type.value}")
        print(f"Success probability: {mutation_result.success_probability:.2f}")
        print(f"Expected improvement: {mutation_result.expected_improvement:.3f}")
        print(f"Overall risk: {mutation_result.risk_assessment['overall_risk']:.3f}")
        
        # Get statistics
        stats = mutator.get_mutation_statistics()
        print(f"\nMutation Statistics: {stats}")
