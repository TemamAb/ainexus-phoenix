"""
AI-NEXUS v5.0 - REINFORCEMENT LEARNING AGENT MODULE
Advanced Deep Reinforcement Learning for Trading Strategy Optimization
Multi-agent RL with PPO, DQN, and Actor-Critic architectures
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Normal, Categorical
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import warnings
warnings.filterwarnings('ignore')

class RLAlgorithm(Enum):
    PPO = "ppo"
    DQN = "dqn"
    A2C = "a2c"
    SAC = "sac"
    TD3 = "td3"

class ActionSpace(Enum):
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"
    HYBRID = "hybrid"

class ExplorationStrategy(Enum):
    EPSILON_GREEDY = "epsilon_greedy"
    GAUSSIAN_NOISE = "gaussian_noise"
    OU_NOISE = "ou_noise"
    BOLTZMANN = "boltzmann"

@dataclass
class RLState:
    state_id: str
    timestamp: datetime
    market_features: np.ndarray
    portfolio_state: np.ndarray
    risk_metrics: np.ndarray
    metadata: Dict[str, Any]

@dataclass
class RLAction:
    action_id: str
    timestamp: datetime
    action_type: str
    action_values: np.ndarray
    confidence: float
    exploration_flag: bool
    metadata: Dict[str, Any]

@dataclass
class RLReward:
    reward_id: str
    timestamp: datetime
    immediate_reward: float
    shaped_reward: float
    risk_adjusted_reward: float
    components: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class TrainingEpisode:
    episode_id: str
    start_time: datetime
    end_time: datetime
    total_reward: float
    steps: int
    learning_progress: float
    metadata: Dict[str, Any]

class RLAgent:
    """
    Advanced Reinforcement Learning Agent for Trading Strategy Optimization
    Supports multiple RL algorithms and exploration strategies
    """
    
    def __init__(self, 
                 agent_id: str,
                 state_dim: int,
                 action_dim: int,
                 algorithm: RLAlgorithm = RLAlgorithm.PPO,
                 action_space: ActionSpace = ActionSpace.CONTINUOUS):
        
        self.agent_id = agent_id
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.algorithm = algorithm
        self.action_space = action_space
        
        # Training parameters
        self.training_params = {
            'learning_rate': 0.0003,
            'gamma': 0.99,
            'epsilon': 1.0,
            'epsilon_min': 0.01,
            'epsilon_decay': 0.995,
            'tau': 0.005,
            'batch_size': 64,
            'memory_size': 100000
        }
        
        # Neural networks
        self.actor = None
        self.critic = None
        self.target_actor = None
        self.target_critic = None
        
        # Experience replay
        self.memory = deque(maxlen=self.training_params['memory_size'])
        self.episode_history = deque(maxlen=1000)
        
        # Performance tracking
        self.performance_metrics = {
            'total_episodes': 0,
            'total_steps': 0,
            'best_reward': -np.inf,
            'avg_reward': 0.0,
            'learning_stability': 0.0
        }
        
        # Initialize networks and optimizers
        self._initialize_networks()
        self._initialize_optimizers()
        
        print(f"RL Agent initialized: {agent_id} using {algorithm.value}")
    
    def _initialize_networks(self):
        """Initialize neural networks based on algorithm"""
        
        if self.algorithm == RLAlgorithm.PPO:
            self.actor = PPONetwork(self.state_dim, self.action_dim, self.action_space)
            self.critic = CriticNetwork(self.state_dim)
            
        elif self.algorithm == RLAlgorithm.DQN:
            self.actor = DQNNetwork(self.state_dim, self.action_dim)
            self.target_actor = DQNNetwork(self.state_dim, self.action_dim)
            self._update_target_networks(tau=1.0)  # Hard update
            
        elif self.algorithm == RLAlgorithm.A2C:
            self.actor = ActorNetwork(self.state_dim, self.action_dim, self.action_space)
            self.critic = CriticNetwork(self.state_dim)
            
        elif self.algorithm == RLAlgorithm.SAC:
            self.actor = SACActor(self.state_dim, self.action_dim)
            self.critic = SACCritic(self.state_dim, self.action_dim)
            self.target_critic = SACCritic(self.state_dim, self.action_dim)
            
        elif self.algorithm == RLAlgorithm.TD3:
            self.actor = TD3Actor(self.state_dim, self.action_dim)
            self.critic = TD3Critic(self.state_dim, self.action_dim)
            self.target_actor = TD3Actor(self.state_dim, self.action_dim)
            self.target_critic = TD3Critic(self.state_dim, self.action_dim)
    
    def _initialize_optimizers(self):
        """Initialize optimizers"""
        
        self.actor_optimizer = optim.Adam(self.actor.parameters(), 
                                        lr=self.training_params['learning_rate'])
        
        if self.critic is not None:
            self.critic_optimizer = optim.Adam(self.critic.parameters(), 
                                             lr=self.training_params['learning_rate'])
    
    def get_action(self, state: RLState, training: bool = True) -> RLAction:
        """Get action from current policy"""
        
        state_tensor = self._state_to_tensor(state)
        
        if training:
            action, exploration_flag = self._explore_action(state_tensor)
        else:
            action, exploration_flag = self._exploit_action(state_tensor)
        
        # Convert to action object
        action_obj = RLAction(
            action_id=f"action_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now(),
            action_type=self.action_space.value,
            action_values=action.detach().numpy(),
            confidence=self._calculate_action_confidence(state_tensor, action),
            exploration_flag=exploration_flag,
            metadata={
                'algorithm': self.algorithm.value,
                'state_features': state.market_features.shape
            }
        )
        
        return action_obj
    
    def _explore_action(self, state: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        """Get exploratory action"""
        
        if self.algorithm == RLAlgorithm.DQN:
            return self._epsilon_greedy_action(state)
        elif self.algorithm in [RLAlgorithm.PPO, RLAlgorithm.A2C]:
            return self._stochastic_action(state)
        elif self.algorithm in [RLAlgorithm.SAC, RLAlgorithm.TD3]:
            return self._gaussian_noise_action(state)
        else:
            return self._exploit_action(state)
    
    def _exploit_action(self, state: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        """Get exploitative action (no exploration)"""
        
        with torch.no_grad():
            if self.algorithm == RLAlgorithm.DQN:
                q_values = self.actor(state)
                action = q_values.argmax(dim=-1)
            else:
                if self.action_space == ActionSpace.CONTINUOUS:
                    action_mean = self.actor(state)
                    action = torch.tanh(action_mean)  # Bound actions
                else:
                    action_probs = torch.softmax(self.actor(state), dim=-1)
                    action = action_probs.argmax(dim=-1)
        
        return action, False
    
    def _epsilon_greedy_action(self, state: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        """Epsilon-greedy exploration for DQN"""
        
        if np.random.random() <= self.training_params['epsilon']:
            # Random action
            if self.action_space == ActionSpace.DISCRETE:
                action = torch.randint(0, self.action_dim, (1,))
            else:
                action = torch.randn(self.action_dim)
            return action, True
        else:
            return self._exploit_action(state)
    
    def _stochastic_action(self, state: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        """Stochastic action sampling for policy gradients"""
        
        if self.action_space == ActionSpace.CONTINUOUS:
            action_mean = self.actor(state)
            action_std = torch.ones_like(action_mean) * 0.1
            distribution = Normal(action_mean, action_std)
            action = distribution.sample()
            action = torch.tanh(action)  # Bound to [-1, 1]
        else:
            action_logits = self.actor(state)
            distribution = Categorical(logits=action_logits)
            action = distribution.sample()
        
        return action, True
    
    def _gaussian_noise_action(self, state: torch.Tensor) -> Tuple[torch.Tensor, bool]:
        """Gaussian noise exploration for continuous actions"""
        
        action = self._exploit_action(state)[0]  # Get exploitative action
        noise = torch.randn_like(action) * 0.1
        noisy_action = action + noise
        noisy_action = torch.clamp(noisy_action, -1.0, 1.0)
        
        return noisy_action, True
    
    def _calculate_action_confidence(self, state: torch.Tensor, action: torch.Tensor) -> float:
        """Calculate confidence of action"""
        
        with torch.no_grad():
            if self.algorithm == RLAlgorithm.DQN:
                q_values = self.actor(state)
                max_q = q_values.max().item()
                confidence = max_q / 10.0  # Normalize
            else:
                # For policy methods, use value function estimate
                if self.critic is not None:
                    value = self.critic(state).item()
                    confidence = value / 100.0  # Normalize
                else:
                    confidence = 0.5
        
        return min(1.0, max(0.0, confidence))
    
    def store_experience(self, state: RLState, action: RLAction, reward: RLReward, next_state: RLState, done: bool):
        """Store experience in replay buffer"""
        
        experience = {
            'state': self._state_to_tensor(state),
            'action': torch.tensor(action.action_values, dtype=torch.float32),
            'reward': torch.tensor([reward.immediate_reward], dtype=torch.float32),
            'next_state': self._state_to_tensor(next_state),
            'done': torch.tensor([done], dtype=torch.float32)
        }
        
        self.memory.append(experience)
        self.performance_metrics['total_steps'] += 1
    
    def train(self, batch_size: int = None) -> Dict[str, float]:
        """Train the agent on a batch of experiences"""
        
        if batch_size is None:
            batch_size = self.training_params['batch_size']
        
        if len(self.memory) < batch_size:
            return {'loss': 0.0, 'q_value': 0.0, 'advantage': 0.0}
        
        # Sample batch
        batch = self._sample_batch(batch_size)
        
        # Algorithm-specific training
        if self.algorithm == RLAlgorithm.PPO:
            losses = self._train_ppo(batch)
        elif self.algorithm == RLAlgorithm.DQN:
            losses = self._train_dqn(batch)
        elif self.algorithm == RLAlgorithm.A2C:
            losses = self._train_a2c(batch)
        elif self.algorithm == RLAlgorithm.SAC:
            losses = self._train_sac(batch)
        elif self.algorithm == RLAlgorithm.TD3:
            losses = self._train_td3(batch)
        else:
            losses = {'loss': 0.0, 'q_value': 0.0}
        
        # Update exploration parameters
        self._update_exploration()
        
        return losses
    
    def _train_ppo(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """PPO training"""
        
        states = batch['state']
        actions = batch['action']
        rewards = batch['reward']
        next_states = batch['next_state']
        dones = batch['done']
        
        # Calculate advantages
        with torch.no_grad():
            values = self.critic(states)
            next_values = self.critic(next_states)
            advantages = rewards + self.training_params['gamma'] * next_values * (1 - dones) - values
        
        # Actor loss
        old_action_probs = self.actor(states).log_prob(actions)
        new_action_probs = self.actor(states).log_prob(actions)
        
        ratio = torch.exp(new_action_probs - old_action_probs)
        surrogate1 = ratio * advantages
        surrogate2 = torch.clamp(ratio, 0.8, 1.2) * advantages
        
        actor_loss = -torch.min(surrogate1, surrogate2).mean()
        
        # Critic loss
        critic_loss = nn.MSELoss()(values, rewards + self.training_params['gamma'] * next_values * (1 - dones))
        
        # Update networks
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        return {
            'actor_loss': actor_loss.item(),
            'critic_loss': critic_loss.item(),
            'advantage': advantages.mean().item()
        }
    
    def _train_dqn(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """DQN training"""
        
        states = batch['state']
        actions = batch['action'].long()
        rewards = batch['reward']
        next_states = batch['next_state']
        dones = batch['done']
        
        # Current Q values
        current_q_values = self.actor(states).gather(1, actions.unsqueeze(1))
        
        # Target Q values
        with torch.no_grad():
            next_q_values = self.target_actor(next_states).max(1)[0].unsqueeze(1)
            target_q_values = rewards + self.training_params['gamma'] * next_q_values * (1 - dones)
        
        # Compute loss
        loss = nn.MSELoss()(current_q_values, target_q_values)
        
        # Optimize
        self.actor_optimizer.zero_grad()
        loss.backward()
        self.actor_optimizer.step()
        
        # Update target network
        self._update_target_networks()
        
        return {
            'loss': loss.item(),
            'q_value': current_q_values.mean().item()
        }
    
    def _train_a2c(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """A2C training"""
        
        states = batch['state']
        actions = batch['action']
        rewards = batch['reward']
        next_states = batch['next_state']
        dones = batch['done']
        
        # Calculate advantages
        with torch.no_grad():
            values = self.critic(states)
            next_values = self.critic(next_states)
            advantages = rewards + self.training_params['gamma'] * next_values * (1 - dones) - values
        
        # Actor loss (policy gradient)
        if self.action_space == ActionSpace.CONTINUOUS:
            action_mean = self.actor(states)
            action_std = torch.ones_like(action_mean) * 0.1
            distribution = Normal(action_mean, action_std)
            log_probs = distribution.log_prob(actions).sum(dim=-1)
        else:
            action_logits = self.actor(states)
            distribution = Categorical(logits=action_logits)
            log_probs = distribution.log_prob(actions.squeeze())
        
        actor_loss = -(log_probs * advantages).mean()
        
        # Critic loss
        critic_loss = nn.MSELoss()(values, rewards + self.training_params['gamma'] * next_values * (1 - dones))
        
        # Update networks
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        return {
            'actor_loss': actor_loss.item(),
            'critic_loss': critic_loss.item(),
            'advantage': advantages.mean().item()
        }
    
    def _train_sac(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Soft Actor-Critic training"""
        # SAC implementation would go here
        return {'actor_loss': 0.0, 'critic_loss': 0.0, 'alpha_loss': 0.0}
    
    def _train_td3(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Twin Delayed DDPG training"""
        # TD3 implementation would go here
        return {'actor_loss': 0.0, 'critic_loss': 0.0}
    
    def _sample_batch(self, batch_size: int) -> Dict[str, torch.Tensor]:
        """Sample a batch from replay memory"""
        
        indices = np.random.choice(len(self.memory), batch_size, replace=False)
        batch = {key: [] for key in ['state', 'action', 'reward', 'next_state', 'done']}
        
        for idx in indices:
            experience = self.memory[idx]
            for key in batch.keys():
                batch[key].append(experience[key])
        
        # Stack tensors
        for key in batch.keys():
            batch[key] = torch.stack(batch[key])
        
        return batch
    
    def _update_target_networks(self, tau: float = None):
        """Update target networks"""
        
        if tau is None:
            tau = self.training_params['tau']
        
        if self.target_actor is not None and self.actor is not None:
            for target_param, param in zip(self.target_actor.parameters(), self.actor.parameters()):
                target_param.data.copy_(tau * param.data + (1.0 - tau) * target_param.data)
        
        if self.target_critic is not None and self.critic is not None:
            for target_param, param in zip(self.target_critic.parameters(), self.critic.parameters()):
                target_param.data.copy_(tau * param.data + (1.0 - tau) * target_param.data)
    
    def _update_exploration(self):
        """Update exploration parameters"""
        
        # Decay epsilon
        if self.training_params['epsilon'] > self.training_params['epsilon_min']:
            self.training_params['epsilon'] *= self.training_params['epsilon_decay']
    
    def _state_to_tensor(self, state: RLState) -> torch.Tensor:
        """Convert RLState to tensor"""
        
        # Combine all state features
        features = np.concatenate([
            state.market_features.flatten(),
            state.portfolio_state.flatten(),
            state.risk_metrics.flatten()
        ])
        
        return torch.FloatTensor(features).unsqueeze(0)
    
    def end_episode(self, episode_reward: float, steps: int, metadata: Dict[str, Any] = None):
        """End training episode and update metrics"""
        
        episode = TrainingEpisode(
            episode_id=f"episode_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            start_time=datetime.now() - timedelta(seconds=steps),
            end_time=datetime.now(),
            total_reward=episode_reward,
            steps=steps,
            learning_progress=self._calculate_learning_progress(),
            metadata=metadata or {}
        )
        
        self.episode_history.append(episode)
        self.performance_metrics['total_episodes'] += 1
        
        # Update performance metrics
        if episode_reward > self.performance_metrics['best_reward']:
            self.performance_metrics['best_reward'] = episode_reward
        
        # Update average reward
        recent_episodes = list(self.episode_history)[-10:]
        self.performance_metrics['avg_reward'] = np.mean([ep.total_reward for ep in recent_episodes])
        
        # Calculate learning stability
        rewards = [ep.total_reward for ep in recent_episodes]
        if len(rewards) >= 2:
            self.performance_metrics['learning_stability'] = 1.0 - (np.std(rewards) / (np.mean(rewards) + 1e-8))
    
    def _calculate_learning_progress(self) -> float:
        """Calculate learning progress"""
        
        if len(self.episode_history) < 10:
            return 0.0
        
        recent_rewards = [ep.total_reward for ep in list(self.episode_history)[-10:]]
        older_rewards = [ep.total_reward for ep in list(self.episode_history)[-20:-10]]
        
        if len(older_rewards) == 0:
            return 0.5
        
        progress = (np.mean(recent_rewards) - np.mean(older_rewards)) / (np.std(older_rewards) + 1e-8)
        return min(1.0, max(0.0, (progress + 1.0) / 2.0))
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        
        return {
            'agent_id': self.agent_id,
            'algorithm': self.algorithm.value,
            'performance_metrics': self.performance_metrics,
            'training_params': {
                'epsilon': self.training_params['epsilon'],
                'learning_rate': self.training_params['learning_rate'],
                'memory_size': len(self.memory)
            },
            'system_health': self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> float:
        """Calculate system health score"""
        
        health_factors = []
        
        # Memory health
        memory_health = min(1.0, len(self.memory) / 1000)
        health_factors.append(memory_health * 0.3)
        
        # Learning progress health
        learning_health = self.performance_metrics['learning_stability']
        health_factors.append(learning_health * 0.4)
        
        # Exploration health
        exploration_health = 1.0 - (self.training_params['epsilon'] - self.training_params['epsilon_min']) / (1.0 - self.training_params['epsilon_min'])
        health_factors.append(exploration_health * 0.3)
        
        return sum(health_factors)
    
    def save_model(self, filepath: str):
        """Save model to file"""
        
        checkpoint = {
            'actor_state_dict': self.actor.state_dict() if self.actor else None,
            'critic_state_dict': self.critic.state_dict() if self.critic else None,
            'target_actor_state_dict': self.target_actor.state_dict() if self.target_actor else None,
            'target_critic_state_dict': self.target_critic.state_dict() if self.target_critic else None,
            'actor_optimizer_state_dict': self.actor_optimizer.state_dict(),
            'critic_optimizer_state_dict': self.critic_optimizer.state_dict() if self.critic_optimizer else None,
            'performance_metrics': self.performance_metrics,
            'training_params': self.training_params
        }
        
        torch.save(checkpoint, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file"""
        
        checkpoint = torch.load(filepath)
        
        if self.actor and checkpoint['actor_state_dict']:
            self.actor.load_state_dict(checkpoint['actor_state_dict'])
        if self.critic and checkpoint['critic_state_dict']:
            self.critic.load_state_dict(checkpoint['critic_state_dict'])
        if self.target_actor and checkpoint['target_actor_state_dict']:
            self.target_actor.load_state_dict(checkpoint['target_actor_state_dict'])
        if self.target_critic and checkpoint['target_critic_state_dict']:
            self.target_critic.load_state_dict(checkpoint['target_critic_state_dict'])
        
        if self.actor_optimizer and checkpoint['actor_optimizer_state_dict']:
            self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer_state_dict'])
        if self.critic_optimizer and checkpoint['critic_optimizer_state_dict']:
            self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer_state_dict'])
        
        self.performance_metrics = checkpoint['performance_metrics']
        self.training_params.update(checkpoint['training_params'])
        
        print(f"Model loaded from {filepath}")

# Neural Network Definitions
class PPONetwork(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, action_space: ActionSpace):
        super().__init__()
        self.action_space = action_space
        
        self.shared_network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )
        
        if action_space == ActionSpace.CONTINUOUS:
            self.actor_mean = nn.Linear(128, action_dim)
            self.actor_log_std = nn.Parameter(torch.zeros(1, action_dim))
        else:
            self.actor = nn.Linear(128, action_dim)
    
    def forward(self, x):
        x = self.shared_network(x)
        
        if self.action_space == ActionSpace.CONTINUOUS:
            action_mean = self.actor_mean(x)
            action_std = torch.exp(self.actor_log_std)
            return Normal(action_mean, action_std)
        else:
            return self.actor(x)

class DQNNetwork(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )
    
    def forward(self, x):
        return self.network(x)

class ActorNetwork(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, action_space: ActionSpace):
        super().__init__()
        self.action_space = action_space
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )
        
        if action_space == ActionSpace.CONTINUOUS:
            self.output = nn.Linear(128, action_dim)
        else:
            self.output = nn.Linear(128, action_dim)
    
    def forward(self, x):
        x = self.network(x)
        
        if self.action_space == ActionSpace.CONTINUOUS:
            return torch.tanh(self.output(x))
        else:
            return self.output(x)

class CriticNetwork(nn.Module):
    def __init__(self, state_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
    
    def forward(self, x):
        return self.network(x)

# Additional network classes for other algorithms
class SACActor(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        # SAC actor implementation
        pass

class SACCritic(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        # SAC critic implementation
        pass

class TD3Actor(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        # TD3 actor implementation
        pass

class TD3Critic(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        # TD3 critic implementation
        pass

# Example usage
if __name__ == "__main__":
    # Create RL agent
    agent = RLAgent(
        agent_id="trading_agent_1",
        state_dim=50,  # Market features + portfolio state + risk metrics
        action_dim=5,   # Buy/Sell/Hold positions
        algorithm=RLAlgorithm.PPO,
        action_space=ActionSpace.CONTINUOUS
    )
    
    # Example training loop
    def demo_training():
        for episode in range(10):
            # Simulate environment
            state = RLState(
                state_id=f"state_{episode}",
                timestamp=datetime.now(),
                market_features=np.random.randn(20),
                portfolio_state=np.random.randn(10),
                risk_metrics=np.random.randn(20),
                metadata={}
            )
            
            total_reward = 0
            for step in range(100):
                # Get action
                action = agent.get_action(state, training=True)
                
                # Simulate environment step (would be real trading environment)
                next_state = RLState(
                    state_id=f"state_{episode}_{step}",
                    timestamp=datetime.now(),
                    market_features=np.random.randn(20),
                    portfolio_state=np.random.randn(10),
                    risk_metrics=np.random.randn(20),
                    metadata={}
                )
                
                # Simulate reward (would be real trading reward)
                reward = RLReward(
                    reward_id=f"reward_{episode}_{step}",
                    timestamp=datetime.now(),
                    immediate_reward=np.random.randn(),
                    shaped_reward=np.random.randn(),
                    risk_adjusted_reward=np.random.randn(),
                    components={'pnl': 0.1, 'risk': -0.05},
                    metadata={}
                )
                
                # Store experience
                agent.store_experience(state, action, reward, next_state, done=False)
                
                # Train
                if step % 10 == 0:
                    losses = agent.train()
                    print(f"Episode {episode}, Step {step}, Loss: {losses}")
                
                total_reward += reward.immediate_reward
                state = next_state
            
            # End episode
            agent.end_episode(total_reward, 100)
            print(f"Episode {episode} completed, Total Reward: {total_reward:.3f}")
    
    demo_training()
    
    # Get agent status
    status = agent.get_agent_status()
    print(f"Agent Status: {status}")
