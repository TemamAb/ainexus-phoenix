#!/usr/bin/env python3
"""
AI-NEXUS Genetic Strategy Evolution Engine
Darwinian selection for arbitrage strategies
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
import random

@dataclass
class StrategyGene:
    id: str
    parameters: Dict[str, float]
    fitness: float
    age: int

class StrategyGeneticEngine:
    def __init__(self, population_size: int = 100, mutation_rate: float = 0.01):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population: List[StrategyGene] = []
        self.generation = 0
        
    def initialize_population(self, parameter_ranges: Dict[str, Tuple[float, float]]):
        """Initialize random population within parameter ranges"""
        self.population = []
        for i in range(self.population_size):
            parameters = {}
            for param, (min_val, max_val) in parameter_ranges.items():
                parameters[param] = random.uniform(min_val, max_val)
            
            gene = StrategyGene(
                id=f"gen_{self.generation}_{i}",
                parameters=parameters,
                fitness=0.0,
                age=0
            )
            self.population.append(gene)
    
    def evaluate_fitness(self, performance_data: Dict[str, float]):
        """Evaluate fitness based on strategy performance"""
        for gene in self.population:
            # Multi-objective fitness: Sharpe ratio, win rate, profit factor
            sharpe_ratio = performance_data.get(f"{gene.id}_sharpe", 0)
            win_rate = performance_data.get(f"{gene.id}_win_rate", 0)
            profit_factor = performance_data.get(f"{gene.id}_profit_factor", 0)
            
            gene.fitness = (sharpe_ratio * 0.4 + win_rate * 0.3 + profit_factor * 0.3)
    
    def selection(self) -> List[StrategyGene]:
        """Tournament selection for reproduction"""
        selected = []
        tournament_size = 5
        
        while len(selected) < self.population_size:
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected
    
    def crossover(self, parent1: StrategyGene, parent2: StrategyGene) -> StrategyGene:
        """Single-point crossover between two parents"""
        child_params = {}
        crossover_point = random.choice(list(parent1.parameters.keys()))
        
        for param in parent1.parameters.keys():
            if random.random() < 0.5:
                child_params[param] = parent1.parameters[param]
            else:
                child_params[param] = parent2.parameters[param]
        
        return StrategyGene(
            id=f"gen_{self.generation + 1}_{len(self.population)}",
            parameters=child_params,
            fitness=0.0,
            age=0
        )
    
    def mutate(self, gene: StrategyGene, parameter_ranges: Dict[str, Tuple[float, float]]):
        """Apply random mutations to genes"""
        for param, (min_val, max_val) in parameter_ranges.items():
            if random.random() < self.mutation_rate:
                # Gaussian mutation around current value
                current_val = gene.parameters[param]
                new_val = current_val + random.gauss(0, (max_val - min_val) * 0.1)
                gene.parameters[param] = max(min_val, min(max_val, new_val))
    
    def evolve_generation(self, performance_data: Dict[str, float], 
                         parameter_ranges: Dict[str, Tuple[float, float]]):
        """Execute one generation of evolution"""
        self.evaluate_fitness(performance_data)
        selected_parents = self.selection()
        
        new_population = []
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(selected_parents, 2)
            child = self.crossover(parent1, parent2)
            self.mutate(child, parameter_ranges)
            new_population.append(child)
        
        self.population = new_population
        self.generation += 1
        
        # Return best performing strategy
        return max(self.population, key=lambda x: x.fitness)
