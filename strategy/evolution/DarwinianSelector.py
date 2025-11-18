"""
AI-NEXUS v5.0 - DARWINIAN SELECTOR MODULE
Natural Selection for Strategy Evolution with Multi-Objective Optimization
Evolutionary algorithm for strategy survival and propagation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random
from copy import deepcopy
from datetime import datetime, timedelta
from collections import deque, defaultdict
import warnings
warnings.filterwarnings('ignore')

class SelectionMethod(Enum):
    TOURNAMENT = "tournament"
    ROULETTE = "roulette"
    RANK_BASED = "rank_based"
    ELITISM = "elitism"
    NOVELTY = "novelty"

class FitnessObjective(Enum):
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    CONSISTENCY = "consistency"
    DIVERSITY = "diversity"
    INNOVATION = "innovation"

@dataclass
class StrategyPopulation:
    population_id: str
    strategies: List[Any]  # List of StrategyGene objects
    generation: int
    creation_timestamp: datetime
    fitness_scores: Dict[str, float]
    diversity_score: float
    average_fitness: float

@dataclass
class SelectionResult:
    selection_id: str
    selected_strategies: List[Any]
    rejected_strategies: List[Any]
    selection_method: SelectionMethod
    fitness_threshold: float
    diversity_impact: float
    generation_improvement: float

class DarwinianSelector:
    """
    Advanced natural selection system for strategy evolution
    Multi-objective optimization with diversity preservation
    """
    
    def __init__(self):
        self.population_history = deque(maxlen=50)
        self.fitness_tracker = defaultdict(lambda: deque(maxlen=100))
        self.selection_statistics = {}
        
        # Selection parameters
        self.selection_params = {
            'population_size': 100,
            'elite_preservation_count': 10,
            'mutation_rate': 0.15,
            'crossover_rate': 0.7,
            'diversity_threshold': 0.3,
            'novelty_bonus': 0.1,
            'aging_penalty': 0.01
        }
        
        # Fitness objectives and weights
        self.fitness_weights = {
            FitnessObjective.SHARPE_RATIO: 0.25,
            FitnessObjective.MAX_DRAWDOWN: 0.20,
            FitnessObjective.WIN_RATE: 0.15,
            FitnessObjective.PROFIT_FACTOR: 0.15,
            FitnessObjective.CONSISTENCY: 0.15,
            FitnessObjective.DIVERSITY: 0.05,
            FitnessObjective.INNOVATION: 0.05
        }
        
        # Selection method probabilities
        self.selection_methods = {
            SelectionMethod.TOURNAMENT: 0.4,
            SelectionMethod.ROULETTE: 0.2,
            SelectionMethod.RANK_BASED: 0.2,
            SelectionMethod.ELITISM: 0.1,
            SelectionMethod.NOVELTY: 0.1
        }
        
        # Initialize selection operators
        self._initialize_selection_operators()
    
    def _initialize_selection_operators(self):
        """Initialize selection operators"""
        
        self.selection_operators = {
            SelectionMethod.TOURNAMENT: self._tournament_selection,
            SelectionMethod.ROULETTE: self._roulette_selection,
            SelectionMethod.RANK_BASED: self._rank_based_selection,
            SelectionMethod.ELITISM: self._elitism_selection,
            SelectionMethod.NOVELTY: self._novelty_selection
        }
    
    def calculate_strategy_fitness(self, strategy: Any, market_regime: str = "normal") -> float:
        """Calculate comprehensive fitness score for a strategy"""
        
        performance = strategy.performance_metrics
        behavioral = strategy.behavioral_traits
        
        fitness_components = {}
        
        # Sharpe Ratio component
        sharpe = performance.get('sharpe_ratio', 0)
        fitness_components[FitnessObjective.SHARPE_RATIO] = self._normalize_sharpe(sharpe)
        
        # Max Drawdown component (inverse)
        max_dd = performance.get('max_drawdown', 1.0)
        fitness_components[FitnessObjective.MAX_DRAWDOWN] = 1.0 - min(max_dd, 1.0)
        
        # Win Rate component
        win_rate = performance.get('win_rate', 0.5)
        fitness_components[FitnessObjective.WIN_RATE] = self._normalize_win_rate(win_rate)
        
        # Profit Factor component
        profit_factor = performance.get('profit_factor', 1.0)
        fitness_components[FitnessObjective.PROFIT_FACTOR] = min(profit_factor / 3.0, 1.0)
        
        # Consistency component
        consistency = performance.get('consistency_score', 0.5)
        fitness_components[FitnessObjective.CONSISTENCY] = consistency
        
        # Diversity component
        diversity = self._calculate_strategy_diversity(strategy)
        fitness_components[FitnessObjective.DIVERSITY] = diversity
        
        # Innovation component
        innovation = self._calculate_innovation_score(strategy)
        fitness_components[FitnessObjective.INNOVATION] = innovation
        
        # Apply regime-specific adjustments
        regime_adjustment = self._calculate_regime_adjustment(strategy, market_regime)
        
        # Calculate weighted fitness
        total_fitness = 0.0
        total_weight = 0.0
        
        for objective, weight in self.fitness_weights.items():
            component_score = fitness_components.get(objective, 0.5)
            total_fitness += component_score * weight
            total_weight += weight
        
        if total_weight > 0:
            base_fitness = total_fitness / total_weight
        else:
            base_fitness = 0.5
        
        # Apply regime adjustment
        adjusted_fitness = base_fitness * regime_adjustment
        
        # Apply aging penalty for older strategies
        age_penalty = self._calculate_aging_penalty(strategy)
        final_fitness = adjusted_fitness * (1 - age_penalty)
        
        # Store fitness history
        self.fitness_tracker[strategy.gene_id].append(final_fitness)
        
        return max(0.0, min(1.0, final_fitness))
    
    def _normalize_sharpe(self, sharpe: float) -> float:
        """Normalize Sharpe ratio to 0-1 scale"""
        return min(1.0, max(0.0, (sharpe + 1.0) / 3.0))  # Map -1 to 2 into 0 to 1
    
    def _normalize_win_rate(self, win_rate: float) -> float:
        """Normalize win rate to 0-1 scale"""
        return min(1.0, max(0.0, (win_rate - 0.3) / 0.7))  # Map 0.3 to 1.0 into 0 to 1
    
    def _calculate_strategy_diversity(self, strategy: Any) -> float:
        """Calculate strategy diversity score"""
        
        # Parameter diversity
        param_values = list(strategy.parameters.values())
        param_diversity = np.std(param_values) if param_values else 0.0
        
        # Behavioral diversity
        behavioral_values = list(strategy.behavioral_traits.values())
        behavioral_diversity = np.std(behavioral_values) if behavioral_values else 0.0
        
        # Topology diversity
        topology_diversity = len(strategy.topology) / 10.0  # Normalize
        
        return (param_diversity + behavioral_diversity + topology_diversity) / 3.0
    
    def _calculate_innovation_score(self, strategy: Any) -> float:
        """Calculate innovation score based on mutation history"""
        
        innovation_events = [m for m in strategy.mutation_history if 'innovation' in m]
        
        if not strategy.mutation_history:
            return 0.5  # Base strategies get medium innovation score
        
        innovation_ratio = len(innovation_events) / len(strategy.mutation_history)
        
        # Recent innovations weighted higher
        recent_bonus = 0.0
        if innovation_events:
            # Simple recency bonus - in practice would use timestamps
            recent_bonus = min(0.3, len(innovation_events) * 0.1)
        
        return min(1.0, innovation_ratio + recent_bonus)
    
    def _calculate_regime_adjustment(self, strategy: Any, market_regime: str) -> float:
        """Calculate market regime adjustment factor"""
        
        regime_adaptation = strategy.behavioral_traits.get('market_regime_adaptation', 0.5)
        
        regime_factors = {
            'normal': 1.0,
            'high_volatility': 0.8 + (regime_adaptation * 0.4),  # 0.8 to 1.2
            'low_volatility': 0.9 + (regime_adaptation * 0.2),   # 0.9 to 1.1
            'trending': 1.0 + (regime_adaptation * 0.3),         # 1.0 to 1.3
            'ranging': 0.8 + (regime_adaptation * 0.4)           # 0.8 to 1.2
        }
        
        return regime_factors.get(market_regime, 1.0)
    
    def _calculate_aging_penalty(self, strategy: Any) -> float:
        """Calculate penalty for strategy age"""
        
        if not strategy.creation_timestamp:
            return 0.0
        
        age_days = (datetime.now() - strategy.creation_timestamp).days
        aging_penalty = min(0.5, age_days * self.selection_params['aging_penalty'])
        
        return aging_penalty
    
    def select_strategies(self, population: StrategyPopulation, 
                         target_size: int = None) -> SelectionResult:
        """Perform natural selection on strategy population"""
        
        if target_size is None:
            target_size = self.selection_params['population_size']
        
        # Calculate fitness for all strategies
        fitness_scores = {}
        for strategy in population.strategies:
            fitness = self.calculate_strategy_fitness(strategy)
            fitness_scores[strategy.gene_id] = fitness
        
        # Update population fitness
        population.fitness_scores = fitness_scores
        population.average_fitness = np.mean(list(fitness_scores.values())) if fitness_scores else 0.0
        
        # Select selection method
        selection_method = self._select_selection_method(population)
        
        # Perform selection
        selection_operator = self.selection_operators[selection_method]
        selected_strategies = selection_operator(population.strategies, fitness_scores, target_size)
        
        # Identify rejected strategies
        selected_ids = {s.gene_id for s in selected_strategies}
        rejected_strategies = [s for s in population.strategies if s.gene_id not in selected_ids]
        
        # Calculate diversity impact
        original_diversity = population.diversity_score
        new_diversity = self._calculate_population_diversity(selected_strategies)
        diversity_impact = new_diversity - original_diversity
        
        # Calculate generation improvement
        generation_improvement = self._calculate_generation_improvement(population, selected_strategies)
        
        # Create selection result
        selection_result = SelectionResult(
            selection_id=f"sel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            selected_strategies=selected_strategies,
            rejected_strategies=rejected_strategies,
            selection_method=selection_method,
            fitness_threshold=np.median(list(fitness_scores.values())) if fitness_scores else 0.0,
            diversity_impact=diversity_impact,
            generation_improvement=generation_improvement
        )
        
        # Update selection statistics
        self._update_selection_statistics(selection_result)
        
        return selection_result
    
    def _select_selection_method(self, population: StrategyPopulation) -> SelectionMethod:
        """Intelligently select selection method based on population state"""
        
        # Base probabilities
        base_probs = self.selection_methods.copy()
        
        # Adjust based on population diversity
        if population.diversity_score < self.selection_params['diversity_threshold']:
            # Low diversity - favor novelty and roulette selection
            base_probs[SelectionMethod.NOVELTY] *= 1.5
            base_probs[SelectionMethod.ROULETTE] *= 1.2
            base_probs[SelectionMethod.TOURNAMENT] *= 0.8
        
        # Adjust based on average fitness
        if population.average_fitness > 0.7:
            # High fitness - favor elitism
            base_probs[SelectionMethod.ELITISM] *= 1.3
        elif population.average_fitness < 0.3:
            # Low fitness - favor radical changes
            base_probs[SelectionMethod.NOVELTY] *= 1.4
            base_probs[SelectionMethod.RANK_BASED] *= 1.2
        
        # Normalize probabilities
        total_prob = sum(base_probs.values())
        if total_prob == 0:
            return SelectionMethod.TOURNAMENT
        
        normalized_probs = {method: prob/total_prob for method, prob in base_probs.items()}
        
        # Select method based on probabilities
        rand_val = random.random()
        cumulative_prob = 0.0
        
        for method, prob in normalized_probs.items():
            cumulative_prob += prob
            if rand_val <= cumulative_prob:
                return method
        
        return SelectionMethod.TOURNAMENT  # Fallback
    
    def _tournament_selection(self, strategies: List[Any], fitness_scores: Dict[str, float], 
                            target_size: int) -> List[Any]:
        """Tournament selection operator"""
        
        selected = []
        tournament_size = max(2, len(strategies) // 10)  # 10% tournament size
        
        # Always preserve elites
        elite_count = min(self.selection_params['elite_preservation_count'], target_size // 3)
        elites = self._select_elites(strategies, fitness_scores, elite_count)
        selected.extend(elites)
        
        # Tournament selection for remaining spots
        while len(selected) < target_size:
            # Random tournament
            tournament = random.sample(strategies, min(tournament_size, len(strategies)))
            
            # Find winner (highest fitness)
            winner = max(tournament, key=lambda s: fitness_scores.get(s.gene_id, 0))
            
            if winner not in selected:
                selected.append(winner)
        
        return selected
    
    def _roulette_selection(self, strategies: List[Any], fitness_scores: Dict[str, float],
                          target_size: int) -> List[Any]:
        """Roulette wheel selection operator"""
        
        selected = []
        
        # Calculate probabilities
        fitness_values = [fitness_scores.get(s.gene_id, 0.01) for s in strategies]
        total_fitness = sum(fitness_values)
        
        if total_fitness <= 0:
            # Fallback to random selection
            return random.sample(strategies, min(target_size, len(strategies)))
        
        probabilities = [f/total_fitness for f in fitness_values]
        
        # Roulette selection
        while len(selected) < target_size and len(selected) < len(strategies):
            rand_val = random.random()
            cumulative_prob = 0.0
            
            for i, strategy in enumerate(strategies):
                cumulative_prob += probabilities[i]
                if rand_val <= cumulative_prob and strategy not in selected:
                    selected.append(strategy)
                    break
        
        return selected
    
    def _rank_based_selection(self, strategies: List[Any], fitness_scores: Dict[str, float],
                            target_size: int) -> List[Any]:
        """Rank-based selection operator"""
        
        selected = []
        
        # Rank strategies by fitness
        ranked_strategies = sorted(strategies, 
                                 key=lambda s: fitness_scores.get(s.gene_id, 0), 
                                 reverse=True)
        
        # Assign ranks (1 is best)
        ranks = list(range(1, len(ranked_strategies) + 1))
        
        # Calculate rank-based probabilities (linear ranking)
        min_prob = 0.1  # Minimum probability for worst rank
        max_prob = 0.9  # Maximum probability for best rank
        
        total_ranks = len(ranks)
        probabilities = []
        
        for rank in ranks:
            prob = max_prob - (max_prob - min_prob) * (rank - 1) / (total_ranks - 1) if total_ranks > 1 else 1.0
            probabilities.append(prob)
        
        # Normalize probabilities
        total_prob = sum(probabilities)
        if total_prob > 0:
            probabilities = [p/total_prob for p in probabilities]
        
        # Rank-based selection
        while len(selected) < target_size and len(selected) < len(ranked_strategies):
            rand_val = random.random()
            cumulative_prob = 0.0
            
            for i, strategy in enumerate(ranked_strategies):
                cumulative_prob += probabilities[i]
                if rand_val <= cumulative_prob and strategy not in selected:
                    selected.append(strategy)
                    break
        
        return selected
    
    def _elitism_selection(self, strategies: List[Any], fitness_scores: Dict[str, float],
                         target_size: int) -> List[Any]:
        """Elitism selection operator"""
        
        # Simply select top performers
        sorted_strategies = sorted(strategies, 
                                 key=lambda s: fitness_scores.get(s.gene_id, 0), 
                                 reverse=True)
        
        return sorted_strategies[:target_size]
    
    def _novelty_selection(self, strategies: List[Any], fitness_scores: Dict[str, float],
                         target_size: int) -> List[Any]:
        """Novelty selection operator"""
        
        selected = []
        
        # Calculate novelty scores
        novelty_scores = {}
        for strategy in strategies:
            novelty = self._calculate_strategy_novelty(strategy, strategies)
            fitness = fitness_scores.get(strategy.gene_id, 0)
            
            # Combine novelty and fitness
            combined_score = (fitness * (1 - self.selection_params['novelty_bonus']) + 
                            novelty * self.selection_params['novelty_bonus'])
            novelty_scores[strategy.gene_id] = combined_score
        
        # Select based on novelty-enhanced scores
        sorted_by_novelty = sorted(strategies, 
                                 key=lambda s: novelty_scores.get(s.gene_id, 0), 
                                 reverse=True)
        
        return sorted_by_novelty[:target_size]
    
    def _select_elites(self, strategies: List[Any], fitness_scores: Dict[str, float],
                      elite_count: int) -> List[Any]:
        """Select elite strategies"""
        
        sorted_strategies = sorted(strategies, 
                                 key=lambda s: fitness_scores.get(s.gene_id, 0), 
                                 reverse=True)
        
        return sorted_strategies[:elite_count]
    
    def _calculate_strategy_novelty(self, strategy: Any, population: List[Any]) -> float:
        """Calculate novelty of a strategy compared to population"""
        
        if len(population) <= 1:
            return 1.0  # Only strategy is maximally novel
        
        # Calculate average distance to other strategies
        distances = []
        
        for other in population:
            if other.gene_id != strategy.gene_id:
                distance = self._calculate_strategy_distance(strategy, other)
                distances.append(distance)
        
        if not distances:
            return 1.0
        
        # Novelty is average distance (normalized)
        avg_distance = np.mean(distances)
        return min(1.0, avg_distance * 2)  # Scale to 0-1 range
    
    def _calculate_strategy_distance(self, strategy1: Any, strategy2: Any) -> float:
        """Calculate distance between two strategies"""
        
        # Parameter distance
        param_dist = 0.0
        common_params = set(strategy1.parameters.keys()) & set(strategy2.parameters.keys())
        if common_params:
            for param in common_params:
                val1 = strategy1.parameters[param]
                val2 = strategy2.parameters[param]
                param_dist += abs(val1 - val2)
            param_dist /= len(common_params)
        
        # Behavioral distance
        behavioral_dist = 0.0
        common_traits = set(strategy1.behavioral_traits.keys()) & set(strategy2.behavioral_traits.keys())
        if common_traits:
            for trait in common_traits:
                val1 = strategy1.behavioral_traits[trait]
                val2 = strategy2.behavioral_traits[trait]
                behavioral_dist += abs(val1 - val2)
            behavioral_dist /= len(common_traits)
        
        # Topology distance (simple)
        topology_dist = 0.0
        common_topology = set(strategy1.topology.keys()) & set(strategy2.topology.keys())
        if common_topology:
            matches = 0
            for element in common_topology:
                if strategy1.topology[element] == strategy2.topology[element]:
                    matches += 1
            topology_dist = 1.0 - (matches / len(common_topology))
        
        # Combined distance
        total_distance = (param_dist + behavioral_dist + topology_dist) / 3.0
        
        return total_distance
    
    def _calculate_population_diversity(self, strategies: List[Any]) -> float:
        """Calculate diversity of a population"""
        
        if len(strategies) <= 1:
            return 0.0
        
        pairwise_distances = []
        
        for i in range(len(strategies)):
            for j in range(i + 1, len(strategies)):
                distance = self._calculate_strategy_distance(strategies[i], strategies[j])
                pairwise_distances.append(distance)
        
        if not pairwise_distances:
            return 0.0
        
        return np.mean(pairwise_distances)
    
    def _calculate_generation_improvement(self, old_population: StrategyPopulation,
                                       new_strategies: List[Any]) -> float:
        """Calculate improvement from one generation to next"""
        
        if not old_population.fitness_scores:
            return 0.0
        
        # Calculate average fitness of new strategies
        new_fitness_scores = []
        for strategy in new_strategies:
            fitness = self.calculate_strategy_fitness(strategy)
            new_fitness_scores.append(fitness)
        
        if not new_fitness_scores:
            return 0.0
        
        old_avg_fitness = old_population.average_fitness
        new_avg_fitness = np.mean(new_fitness_scores)
        
        improvement = (new_avg_fitness - old_avg_fitness) / old_avg_fitness if old_avg_fitness > 0 else 0.0
        
        return improvement
    
    def _update_selection_statistics(self, selection_result: SelectionResult):
        """Update selection performance statistics"""
        
        method = selection_result.selection_method.value
        
        if method not in self.selection_statistics:
            self.selection_statistics[method] = {
                'count': 0,
                'avg_diversity_impact': 0.0,
                'avg_improvement': 0.0,
                'success_rate': 0.0
            }
        
        stats = self.selection_statistics[method]
        stats['count'] += 1
        
        # Update running averages
        n = stats['count']
        stats['avg_diversity_impact'] = (
            (stats['avg_diversity_impact'] * (n - 1) + selection_result.diversity_impact) / n
        )
        stats['avg_improvement'] = (
            (stats['avg_improvement'] * (n - 1) + selection_result.generation_improvement) / n
        )
        
        # Update success rate (positive improvement)
        if selection_result.generation_improvement > 0:
            current_success = stats.get('success_count', 0) + 1
            stats['success_count'] = current_success
            stats['success_rate'] = current_success / n
    
    def get_selection_performance(self) -> Dict[str, Any]:
        """Get selection performance statistics"""
        
        return {
            'total_selections': sum(stats['count'] for stats in self.selection_statistics.values()),
            'method_performance': self.selection_statistics,
            'overall_success_rate': self._calculate_overall_success_rate(),
            'best_performing_method': self._get_best_performing_method()
        }
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall selection success rate"""
        
        total_success = 0
        total_selections = 0
        
        for stats in self.selection_statistics.values():
            total_success += stats.get('success_count', 0)
            total_selections += stats['count']
        
        if total_selections == 0:
            return 0.0
        
        return total_success / total_selections
    
    def _get_best_performing_method(self) -> str:
        """Get best performing selection method"""
        
        if not self.selection_statistics:
            return "tournament"
        
        best_method = None
        best_success_rate = -1.0
        
        for method, stats in self.selection_statistics.items():
            success_rate = stats.get('success_rate', 0.0)
            if success_rate > best_success_rate:
                best_success_rate = success_rate
                best_method = method
        
        return best_method
    
    def optimize_selection_parameters(self, performance_data: Dict[str, List[float]]):
        """Optimize selection parameters based on historical performance"""
        
        # Adjust selection method probabilities based on performance
        performance_stats = self.get_selection_performance()
        method_performance = performance_stats['method_performance']
        
        if not method_performance:
            return
        
        # Calculate new probabilities based on success rates
        new_probs = {}
        total_success = 0
        
        for method in self.selection_methods:
            stats = method_performance.get(method, {})
            success_rate = stats.get('success_rate', 0.5)
            new_probs[method] = success_rate
            total_success += success_rate
        
        # Normalize and apply smoothing
        if total_success > 0:
            for method in new_probs:
                new_prob = new_probs[method] / total_success
                # Smooth with original probability
                original_prob = self.selection_methods[method]
                smoothed_prob = 0.7 * new_prob + 0.3 * original_prob
                self.selection_methods[method] = smoothed_prob
        
        # Adjust diversity threshold based on performance
        overall_success = performance_stats['overall_success_rate']
        if overall_success > 0.6:
            # High success - can afford more diversity
            self.selection_params['diversity_threshold'] = min(
                0.5, self.selection_params['diversity_threshold'] * 1.1
            )
        elif overall_success < 0.4:
            # Low success - focus on exploitation
            self.selection_params['diversity_threshold'] = max(
                0.1, self.selection_params['diversity_threshold'] * 0.9
            )

# Example usage
if __name__ == "__main__":
    # Create Darwinian selector
    selector = DarwinianSelector()
    
    # Create sample population
    sample_strategies = []
    for i in range(50):
        # Create sample strategy genes (simplified)
        strategy = type('StrategyGene', (), {
            'gene_id': f"gene_{i}",
            'performance_metrics': {
                'sharpe_ratio': random.uniform(-1.0, 2.0),
                'max_drawdown': random.uniform(0.05, 0.4),
                'win_rate': random.uniform(0.4, 0.7),
                'profit_factor': random.uniform(0.8, 3.0),
                'consistency_score': random.uniform(0.3, 0.9)
            },
            'behavioral_traits': {
                'market_regime_adaptation': random.uniform(0.0, 1.0),
                'volatility_response': random.uniform(0.0, 1.0)
            },
            'parameters': {
                'aggressiveness': random.uniform(0.1, 0.9),
                'risk_tolerance': random.uniform(0.05, 0.8)
            },
            'topology': {'feature_count': random.randint(5, 20)},
            'mutation_history': [],
            'creation_timestamp': datetime.now() - timedelta(days=random.randint(0, 30))
        })()
        sample_strategies.append(strategy)
    
    population = StrategyPopulation(
        population_id="pop_001",
        strategies=sample_strategies,
        generation=1,
        creation_timestamp=datetime.now(),
        fitness_scores={},
        diversity_score=0.5,
        average_fitness=0.0
    )
    
    # Perform selection
    selection_result = selector.select_strategies(population, target_size=20)
    
    print(f"Selection Method: {selection_result.selection_method.value}")
    print(f"Selected {len(selection_result.selected_strategies)} strategies")
    print(f"Diversity Impact: {selection_result.diversity_impact:.3f}")
    print(f"Generation Improvement: {selection_result.generation_improvement:.3f}")
    
    # Get performance statistics
    performance = selector.get_selection_performance()
    print(f"\nSelection Performance: {performance}")
