# File: advanced_ai/strategic_ai/AdaptiveLearning.py
# 7P-PILLAR: AIEVO-7P
# PURPOSE: Continuous AI learning and strategy adaptation

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import time

class LearningMode(Enum):
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    TRANSFER = "transfer_learning"
    META_LEARNING = "meta_learning"

@dataclass
class LearningEpisode:
    episode_id: str
    strategy: str
    environment_state: Dict
    action_taken: str
    reward: float
    learning_signal: float
    timestamp: float

class AdaptiveLearning:
    """
    Continuous learning system that adapts strategies based on market feedback
    Implements reinforcement learning and meta-learning for strategy improvement
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.learning_history = []
        self.strategy_performance = {}
        self.model_weights = {}
        self.learning_mode = LearningMode.EXPLORATION
        self.logger = logging.getLogger('AdaptiveLearning')
        
        # Initialize learning parameters
        self.learning_rate = config.get('learning_rate', 0.01)
        self.exploration_rate = config.get('exploration_rate', 0.1)
        self.discount_factor = config.get('discount_factor', 0.95)
        
    def record_learning_episode(self, 
                              strategy: str,
                              environment_state: Dict,
                              action_taken: str,
                              reward: float,
                              learning_signal: float = None) -> str:
        """Record a learning episode for strategy adaptation"""
        
        episode_id = f"episode_{int(time.time())}_{len(self.learning_history)}"
        
        if learning_signal is None:
            learning_signal = self._calculate_learning_signal(reward, environment_state)
        
        episode = LearningEpisode(
            episode_id=episode_id,
            strategy=strategy,
            environment_state=environment_state,
            action_taken=action_taken,
            reward=reward,
            learning_signal=learning_signal,
            timestamp=time.time()
        )
        
        self.learning_history.append(episode)
        
        # Update strategy performance
        self._update_strategy_performance(strategy, reward, learning_signal)
        
        # Adaptive learning update
        self._adaptive_learning_update(episode)
        
        self.logger.info(f"Recorded learning episode {episode_id} for strategy {strategy}")
        
        return episode_id
    
    def _calculate_learning_signal(self, reward: float, environment_state: Dict) -> float:
        """Calculate learning signal from reward and environment state"""
        # Base learning signal is the reward
        learning_signal = reward
        
        # Adjust based on market conditions
        market_volatility = environment_state.get('volatility', 0.2)
        if market_volatility > 0.5:
            # Reduce learning signal in high volatility (noisy environment)
            learning_signal *= 0.7
        
        # Adjust based on strategy complexity
        strategy_complexity = environment_state.get('strategy_complexity', 1)
        if strategy_complexity > 2:
            # Increase learning signal for complex strategies (more learning needed)
            learning_signal *= 1.2
        
        return learning_signal
    
    def _update_strategy_performance(self, strategy: str, reward: float, learning_signal: float):
        """Update performance metrics for a strategy"""
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = {
                'total_reward': 0,
                'episode_count': 0,
                'average_reward': 0,
                'learning_signals': [],
                'last_updated': time.time()
            }
        
        perf = self.strategy_performance[strategy]
        perf['total_reward'] += reward
        perf['episode_count'] += 1
        perf['average_reward'] = perf['total_reward'] / perf['episode_count']
        perf['learning_signals'].append(learning_signal)
        perf['last_updated'] = time.time()
        
        # Keep only recent learning signals
        if len(perf['learning_signals']) > 1000:
            perf['learning_signals'] = perf['learning_signals'][-1000:]
    
    def _adaptive_learning_update(self, episode: LearningEpisode):
        """Perform adaptive learning update based on episode"""
        strategy = episode.strategy
        
        if strategy not in self.model_weights:
            self.model_weights[strategy] = self._initialize_model_weights(strategy)
        
        # Q-learning update (simplified)
        current_weights = self.model_weights[strategy]
        learning_update = self.learning_rate * episode.learning_signal
        
        # Update weights based on learning signal
        for key in current_weights:
            if isinstance(current_weights[key], (int, float)):
                current_weights[key] += learning_update * np.random.uniform(-0.1, 0.1)
        
        self.model_weights[strategy] = current_weights
        
        # Adaptive exploration rate
        self._update_exploration_rate(episode)
        
        # Check for learning mode transition
        self._check_learning_mode_transition()
    
    def _initialize_model_weights(self, strategy: str) -> Dict:
        """Initialize model weights for a strategy"""
        base_weights = {
            'risk_tolerance': np.random.uniform(0.1, 0.9),
            'aggressiveness': np.random.uniform(0.1, 0.9),
            'patience': np.random.uniform(0.1, 0.9),
            'adaptability': np.random.uniform(0.1, 0.9),
            'learning_rate': self.learning_rate
        }
        
        # Strategy-specific weight initializations
        if 'arbitrage' in strategy.lower():
            base_weights.update({
                'slippage_tolerance': np.random.uniform(0.01, 0.05),
                'execution_speed': np.random.uniform(0.7, 1.0),
                'profit_threshold': np.random.uniform(0.001, 0.01)
            })
        elif 'market_making' in strategy.lower():
            base_weights.update({
                'spread_target': np.random.uniform(0.001, 0.01),
                'inventory_risk': np.random.uniform(0.1, 0.5),
                'rebalancing_frequency': np.random.uniform(0.8, 1.2)
            })
        
        return base_weights
    
    def _update_exploration_rate(self, episode: LearningEpisode):
        """Adaptively update exploration rate"""
        strategy_perf = self.strategy_performance.get(episode.strategy, {})
        
        if strategy_perf.get('episode_count', 0) > 100:
            avg_reward = strategy_perf.get('average_reward', 0)
            
            # Decrease exploration if performance is good and stable
            if avg_reward > 0 and self._is_performance_stable(episode.strategy):
                self.exploration_rate = max(0.01, self.exploration_rate * 0.99)
            else:
                # Increase exploration if performance is poor or unstable
                self.exploration_rate = min(0.5, self.exploration_rate * 1.01)
    
    def _is_performance_stable(self, strategy: str, window: int = 50) -> bool:
        """Check if strategy performance is stable"""
        strategy_perf = self.strategy_performance.get(strategy, {})
        learning_signals = strategy_perf.get('learning_signals', [])
        
        if len(learning_signals) < window:
            return False
        
        recent_signals = learning_signals[-window:]
        signal_variance = np.var(recent_signals)
        
        return signal_variance < 0.1  # Threshold for stability
    
    def _check_learning_mode_transition(self):
        """Check and update learning mode based on system state"""
        total_episodes = len(self.learning_history)
        
        if total_episodes < 100:
            self.learning_mode = LearningMode.EXPLORATION
        elif total_episodes < 1000:
            self.learning_mode = LearningMode.EXPLOITATION
        else:
            # Check if we have enough diverse experience for transfer learning
            unique_strategies = len(self.strategy_performance)
            if unique_strategies >= 5:
                self.learning_mode = LearningMode.TRANSFER
            else:
                self.learning_mode = LearningMode.EXPLOITATION
        
        # Special condition for meta-learning
        if (self.learning_mode == LearningMode.TRANSFER and 
            total_episodes > 5000 and 
            self._has_sufficient_meta_learning_data()):
            self.learning_mode = LearningMode.META_LEARNING
    
    def _has_sufficient_meta_learning_data(self) -> bool:
        """Check if we have sufficient data for meta-learning"""
        if len(self.learning_history) < 1000:
            return False
        
        # Check for diverse market conditions
        market_conditions = set()
        for episode in self.learning_history[-1000:]:
            market_state = episode.environment_state.get('market_regime', 'unknown')
            market_conditions.add(market_state)
        
        return len(market_conditions) >= 3
    
    def get_strategy_recommendation(self, 
                                  current_state: Dict,
                                  available_strategies: List[str]) -> Tuple[str, Dict]:
        """Get recommended strategy and parameters for current state"""
        
        if self.learning_mode == LearningMode.EXPLORATION:
            return self._exploration_recommendation(available_strategies, current_state)
        elif self.learning_mode == LearningMode.EXPLOITATION:
            return self._exploitation_recommendation(available_strategies, current_state)
        elif self.learning_mode == LearningMode.TRANSFER:
            return self._transfer_learning_recommendation(available_strategies, current_state)
        else:  # META_LEARNING
            return self._meta_learning_recommendation(available_strategies, current_state)
    
    def _exploration_recommendation(self, strategies: List[str], state: Dict) -> Tuple[str, Dict]:
        """Exploration: Try less-used or new strategies"""
        # Prioritize strategies with fewer episodes
        strategy_usage = {}
        for strategy in strategies:
            perf = self.strategy_performance.get(strategy, {'episode_count': 0})
            strategy_usage[strategy] = perf['episode_count']
        
        # Select least used strategy
        recommended_strategy = min(strategy_usage, key=strategy_usage.get)
        
        # Use base parameters with some exploration noise
        parameters = self.model_weights.get(recommended_strategy, {})
        noisy_parameters = self._add_exploration_noise(parameters)
        
        return recommended_strategy, noisy_parameters
    
    def _exploitation_recommendation(self, strategies: List[str], state: Dict) -> Tuple[str, Dict]:
        """Exploitation: Use best-performing strategies"""
        # Select strategy with highest average reward
        strategy_rewards = {}
        for strategy in strategies:
            perf = self.strategy_performance.get(strategy, {'average_reward': -np.inf})
            strategy_rewards[strategy] = perf['average_reward']
        
        recommended_strategy = max(strategy_rewards, key=strategy_rewards.get)
        parameters = self.model_weights.get(recommended_strategy, {})
        
        return recommended_strategy, parameters
    
    def _transfer_learning_recommendation(self, strategies: List[str], state: Dict) -> Tuple[str, Dict]:
        """Transfer learning: Adapt strategies from similar contexts"""
        # Find most similar historical context
        similar_episode = self._find_similar_episode(state)
        
        if similar_episode:
            # Use the strategy that worked in similar context
            recommended_strategy = similar_episode.strategy
            if recommended_strategy in strategies:
                # Transfer and adapt parameters
                base_parameters = self.model_weights.get(recommended_strategy, {})
                adapted_parameters = self._adapt_parameters(base_parameters, state, similar_episode.environment_state)
                return recommended_strategy, adapted_parameters
        
        # Fallback to exploitation
        return self._exploitation_recommendation(strategies, state)
    
    def _meta_learning_recommendation(self, strategies: List[str], state: Dict) -> Tuple[str, Dict]:
        """Meta-learning: Learn to learn across strategies and contexts"""
        # Use ensemble of strategies based on context similarity
        strategy_scores = {}
        
        for strategy in strategies:
            # Calculate context-aware score
            score = self._calculate_meta_learning_score(strategy, state)
            strategy_scores[strategy] = score
        
        recommended_strategy = max(strategy_scores, key=strategy_scores.get)
        
        # Meta-learned parameters
        meta_parameters = self._meta_learn_parameters(recommended_strategy, state)
        
        return recommended_strategy, meta_parameters
    
    def _find_similar_episode(self, current_state: Dict, n_similar: int = 5) -> Optional[LearningEpisode]:
        """Find similar historical episodes"""
        if not self.learning_history:
            return None
        
        # Calculate similarity scores
        similarities = []
        for episode in self.learning_history[-1000:]:  # Recent episodes
            similarity = self._calculate_state_similarity(current_state, episode.environment_state)
            similarities.append((similarity, episode))
        
        # Get most similar episodes
        similarities.sort(key=lambda x: x[0], reverse=True)
        similar_episodes = [ep for sim, ep in similarities[:n_similar] if sim > 0.7]
        
        if not similar_episodes:
            return None
        
        # Select episode with highest reward among similar ones
        best_episode = max(similar_episodes, key=lambda ep: ep.reward)
        return best_episode
    
    def _calculate_state_similarity(self, state1: Dict, state2: Dict) -> float:
        """Calculate similarity between two environment states"""
        common_keys = set(state1.keys()) & set(state2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            if isinstance(state1[key], (int, float)) and isinstance(state2[key], (int, float)):
                # Numerical similarity
                max_val = max(abs(state1[key]), abs(state2[key]), 1)  # Avoid division by zero
                similarity = 1 - abs(state1[key] - state2[key]) / max_val
                similarities.append(max(0, similarity))
            elif state1[key] == state2[key]:
                # Categorical similarity
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_meta_learning_score(self, strategy: str, state: Dict) -> float:
        """Calculate meta-learning score for strategy in given state"""
        base_score = self.strategy_performance.get(strategy, {}).get('average_reward', 0)
        
        # Adjust based on state similarity to historical performance
        similar_episodes = [ep for ep in self.learning_history 
                          if ep.strategy == strategy and ep.reward > 0]
        
        if not similar_episodes:
            return base_score
        
        # Calculate average performance in similar states
        similarity_scores = []
        for episode in similar_episodes[-100:]:  # Recent episodes
            similarity = self._calculate_state_similarity(state, episode.environment_state)
            weighted_reward = episode.reward * similarity
            similarity_scores.append(weighted_reward)
        
        if similarity_scores:
            meta_score = np.mean(similarity_scores)
            return (base_score + meta_score) / 2
        else:
            return base_score
    
    def _add_exploration_noise(self, parameters: Dict, noise_level: float = 0.1) -> Dict:
        """Add exploration noise to parameters"""
        noisy_parameters = parameters.copy()
        
        for key, value in noisy_parameters.items():
            if isinstance(value, (int, float)):
                noise = np.random.uniform(-noise_level, noise_level)
                noisy_parameters[key] = value * (1 + noise)
        
        return noisy_parameters
    
    def _adapt_parameters(self, base_parameters: Dict, current_state: Dict, historical_state: Dict) -> Dict:
        """Adapt parameters based on state differences"""
        adapted_parameters = base_parameters.copy()
        
        # Simple adaptation: adjust based on volatility difference
        current_vol = current_state.get('volatility', 0.2)
        historical_vol = historical_state.get('volatility', 0.2)
        
        vol_ratio = current_vol / max(historical_vol, 0.01)
        
        # Adjust risk parameters based on volatility
        if 'risk_tolerance' in adapted_parameters:
            adapted_parameters['risk_tolerance'] *= (1 / vol_ratio)
        
        if 'aggressiveness' in adapted_parameters:
            adapted_parameters['aggressiveness'] *= (1 / vol_ratio)
        
        return adapted_parameters
    
    def _meta_learn_parameters(self, strategy: str, state: Dict) -> Dict:
        """Generate meta-learned parameters for strategy and state"""
        base_parameters = self.model_weights.get(strategy, {})
        
        # Find optimal parameters for similar states
        similar_successful_episodes = [
            ep for ep in self.learning_history
            if ep.strategy == strategy and ep.reward > 0 and ep.learning_signal > 0
        ]
        
        if not similar_successful_episodes:
            return base_parameters
        
        # Use parameters from most successful similar episodes
        best_episodes = sorted(similar_successful_episodes, 
                             key=lambda ep: ep.reward, 
                             reverse=True)[:10]
        
        # Simple ensemble of successful parameters
        meta_parameters = base_parameters.copy()
        
        for episode in best_episodes:
            episode_weights = self.model_weights.get(episode.strategy, {})
            similarity = self._calculate_state_similarity(state, episode.environment_state)
            
            # Weighted average based on similarity and reward
            for key in meta_parameters:
                if (key in episode_weights and 
                    isinstance(meta_parameters[key], (int, float)) and 
                    isinstance(episode_weights[key], (int, float))):
                    
                    weight = similarity * episode.reward
                    meta_parameters[key] = (
                        meta_parameters[key] + episode_weights[key] * weight
                    ) / (1 + weight)
        
        return meta_parameters
    
    def get_learning_analytics(self) -> Dict:
        """Get comprehensive learning analytics"""
        total_episodes = len(self.learning_history)
        unique_strategies = len(self.strategy_performance)
        
        recent_episodes = self.learning_history[-100:] if self.learning_history else []
        recent_rewards = [ep.reward for ep in recent_episodes]
        
        analytics = {
            'total_episodes': total_episodes,
            'unique_strategies': unique_strategies,
            'learning_mode': self.learning_mode.value,
            'exploration_rate': self.exploration_rate,
            'learning_rate': self.learning_rate,
            'recent_performance': {
                'average_reward': np.mean(recent_rewards) if recent_rewards else 0,
                'reward_std': np.std(recent_rewards) if recent_rewards else 0,
                'success_rate': len([r for r in recent_rewards if r > 0]) / len(recent_rewards) if recent_rewards else 0
            },
            'strategy_rankings': self._get_strategy_rankings(),
            'learning_progress': self._calculate_learning_progress()
        }
        
        return analytics
    
    def _get_strategy_rankings(self) -> List[Dict]:
        """Get ranked list of strategies by performance"""
        rankings = []
        
        for strategy, perf in self.strategy_performance.items():
            rankings.append({
                'strategy': strategy,
                'episode_count': perf['episode_count'],
                'average_reward': perf['average_reward'],
                'total_reward': perf['total_reward'],
                'last_updated': perf['last_updated']
            })
        
        rankings.sort(key=lambda x: x['average_reward'], reverse=True)
        return rankings
    
    def _calculate_learning_progress(self) -> float:
        """Calculate overall learning progress (0-1)"""
        if len(self.learning_history) < 100:
            return len(self.learning_history) / 100
        
        # Use improvement in recent performance vs historical
        recent_window = 100
        historical_window = 500
        
        if len(self.learning_history) < historical_window:
            return 0.5
        
        recent_episodes = self.learning_history[-recent_window:]
        historical_episodes = self.learning_history[-historical_window:-recent_window]
        
        recent_rewards = [ep.reward for ep in recent_episodes]
        historical_rewards = [ep.reward for ep in historical_episodes]
        
        if not recent_rewards or not historical_rewards:
            return 0.5
        
        recent_avg = np.mean(recent_rewards)
        historical_avg = np.mean(historical_rewards)
        
        if historical_avg == 0:
            return 0.5
        
        progress = recent_avg / historical_avg - 1
        return max(0, min(1, (progress + 0.5)))  # Normalize to 0-1

# Example usage
if __name__ == "__main__":
    adaptive_learner = AdaptiveLearning({
        'learning_rate': 0.01,
        'exploration_rate': 0.1,
        'discount_factor': 0.95
    })
    print("AdaptiveLearning initialized successfully")
