"""
QUANTUMNEX v1.0 - MULTI-AGENT ORCHESTRATOR
Advanced Multi-Agent System Coordination and Management
Quantum-Speed Agent Collaboration for Complex Strategy Execution
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

class AgentType(Enum):
    DECISION_AGENT = "decision_agent"
    DETECTION_AGENT = "detection_agent"
    EXECUTION_AGENT = "execution_agent"
    RISK_AGENT = "risk_agent"
    MONITORING_AGENT = "monitoring_agent"

class AgentStatus(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"

class CoordinationMode(Enum):
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    HYBRID = "hybrid"

@dataclass
class AgentConfig:
    agent_type: AgentType
    capabilities: List[str]
    resource_limits: Dict[str, float]
    learning_parameters: Dict[str, Any]
    performance_weights: Dict[str, float] = field(default_factory=lambda: {
        'success_rate': 0.4,
        'efficiency': 0.3,
        'reliability': 0.3
    })

@dataclass
class AgentState:
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    capabilities: List[str]
    performance_metrics: Dict[str, float]
    resource_usage: Dict[str, float]
    last_heartbeat: datetime
    task_queue: List[Dict] = field(default_factory=list)
    completed_tasks: int = 0
    failed_tasks: int = 0

@dataclass
class Task:
    task_id: str
    task_type: str
    priority: int
    requirements: List[str]
    input_data: Dict[str, Any]
    deadline: Optional[datetime] = None
    assigned_agent: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CoordinationResult:
    coordination_id: str
    task_id: str
    participating_agents: List[str]
    result: Dict[str, Any]
    coordination_mode: CoordinationMode
    timestamp: datetime
    success: bool = True

class MultiAgentOrchestrator:
    """
    Advanced multi-agent system orchestrator for QuantumNex
    Manages collaborative-competitive agent interactions with enterprise-grade reliability
    """
    
    def __init__(self, coordination_mode: CoordinationMode = CoordinationMode.HYBRID):
        self.coordination_mode = coordination_mode
        self.agents: Dict[str, AgentState] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.coordination_history: List[CoordinationResult] = []
        
        self.performance_metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'coordination_events': 0,
            'avg_task_completion_time': 0.0,
            'agent_utilization': {},
            'system_throughput': 0.0,
            'error_rate': 0.0
        }
        
        # Agent capability registry
        self.capability_registry = defaultdict(list)
        
        # Learning and adaptation parameters
        self.learning_parameters = {
            'collaboration_threshold': 0.7,
            'competition_threshold': 0.3,
            'trust_decay_rate': 0.95,
            'performance_weight': 0.6,
            'adaptation_rate': 0.1
        }
        
        # Trust scores between agents
        self.trust_scores: Dict[Tuple[str, str], float] = {}
        
        # Task history for learning
        self.task_history: deque = deque(maxlen=10000)
        
        self.is_running = False
        self._monitor_task = None
        print("✅ Multi-Agent Orchestrator initialized")

    async def initialize(self):
        """Initialize the multi-agent system with enterprise reliability"""
        print("🚀 Initializing QuantumNex Multi-Agent System...")
        
        try:
            # Initialize core agents
            await self._initialize_core_agents()
            
            # Start agent monitoring
            self.is_running = True
            self._monitor_task = asyncio.create_task(self._monitor_agents())
            
            # Start performance optimization
            asyncio.create_task(self._optimize_system_performance())
            
            print("✅ Multi-Agent System initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Multi-Agent System: {e}")
            raise

    async def _initialize_core_agents(self):
        """Initialize core agent types for QuantumNex with comprehensive capabilities"""
        core_agents = [
            (AgentType.DECISION_AGENT, [
                'strategy_planning', 'risk_assessment', 'portfolio_optimization',
                'market_analysis', 'signal_generation'
            ]),
            (AgentType.DETECTION_AGENT, [
                'opportunity_detection', 'anomaly_detection', 'pattern_recognition',
                'arbitrage_identification', 'market_regime_detection'
            ]),
            (AgentType.EXECUTION_AGENT, [
                'trade_execution', 'order_management', 'slippage_optimization',
                'liquidity_aggregation', 'cross_chain_execution'
            ]),
            (AgentType.RISK_AGENT, [
                'exposure_monitoring', 'position_sizing', 'drawdown_control',
                'volatility_assessment', 'compliance_checking'
            ]),
            (AgentType.MONITORING_AGENT, [
                'system_health', 'performance_tracking', 'latency_monitoring',
                'resource_utilization', 'alert_management'
            ])
        ]
        
        initialization_tasks = []
        for agent_type, capabilities in core_agents:
            task = self.create_agent(agent_type, capabilities)
            initialization_tasks.append(task)
        
        # Wait for all agents to initialize
        await asyncio.gather(*initialization_tasks, return_exceptions=True)

    async def create_agent(self, agent_type: AgentType, capabilities: List[str]) -> str:
        """Create and register a new agent with comprehensive configuration"""
        agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Determine resource limits based on agent type
        resource_limits = self._get_resource_limits(agent_type)
        
        agent_config = AgentConfig(
            agent_type=agent_type,
            capabilities=capabilities,
            resource_limits=resource_limits,
            learning_parameters={
                'learning_rate': 0.01,
                'exploration_rate': 0.1,
                'adaptation_speed': 0.05
            }
        )
        
        agent_state = AgentState(
            agent_id=agent_id,
            agent_type=agent_type,
            status=AgentStatus.INITIALIZING,
            capabilities=capabilities,
            performance_metrics={
                'success_rate': 1.0,  # Start optimistic
                'avg_processing_time': 0.0,
                'reliability_score': 1.0,
                'efficiency_score': 1.0,
                'throughput': 0.0
            },
            resource_usage={
                'memory_usage': 0.0,
                'cpu_usage': 0.0,
                'active_tasks': 0,
                'network_usage': 0.0
            },
            last_heartbeat=datetime.now()
        )
        
        # Register agent
        self.agents[agent_id] = agent_state
        self.agent_configs[agent_id] = agent_config
        
        # Update capability registry
        for capability in capabilities:
            self.capability_registry[capability].append(agent_id)
        
        # Initialize trust scores with all existing agents
        for other_agent_id in self.agents:
            if other_agent_id != agent_id:
                self.trust_scores[(agent_id, other_agent_id)] = 0.5
                self.trust_scores[(other_agent_id, agent_id)] = 0.5
        
        # Simulate agent initialization with proper error handling
        try:
            await asyncio.sleep(0.05)  # Simulate initialization time
            agent_state.status = AgentStatus.ACTIVE
            
            print(f"✅ Created agent: {agent_id} with capabilities: {capabilities}")
            
            return agent_id
            
        except Exception as e:
            print(f"❌ Failed to create agent {agent_id}: {e}")
            agent_state.status = AgentStatus.ERROR
            raise

    def _get_resource_limits(self, agent_type: AgentType) -> Dict[str, float]:
        """Get appropriate resource limits based on agent type"""
        base_limits = {
            'max_memory': 1024,  # MB
            'max_processing_time': 60,  # seconds
            'max_concurrent_tasks': 5,
            'max_network_bandwidth': 100  # MB/s
        }
        
        # Adjust limits based on agent type
        limits_adjustments = {
            AgentType.DECISION_AGENT: {'max_memory': 2048, 'max_concurrent_tasks': 3},
            AgentType.DETECTION_AGENT: {'max_concurrent_tasks': 8, 'max_processing_time': 30},
            AgentType.EXECUTION_AGENT: {'max_concurrent_tasks': 10, 'max_processing_time': 10},
            AgentType.RISK_AGENT: {'max_memory': 512, 'max_concurrent_tasks': 15},
            AgentType.MONITORING_AGENT: {'max_concurrent_tasks': 20, 'max_processing_time': 5}
        }
        
        limits = base_limits.copy()
        if agent_type in limits_adjustments:
            limits.update(limits_adjustments[agent_type])
            
        return limits

    async def submit_task(self, task_type: str, requirements: List[str], 
                         input_data: Dict[str, Any], priority: int = 1,
                         deadline: Optional[datetime] = None) -> str:
        """Submit a task to the multi-agent system with comprehensive validation"""
        # Validate inputs
        if not requirements:
            raise ValueError("Task must have at least one requirement")
        
        if not input_data:
            raise ValueError("Task must have input data")
        
        task_id = f"TASK_{uuid.uuid4().hex[:8]}"
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=max(1, min(10, priority)),  # Clamp priority between 1-10
            requirements=requirements,
            input_data=input_data,
            deadline=deadline
        )
        
        # Add to task queue with priority sorting
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda x: (x.priority, x.created_at), reverse=True)
        
        print(f"📥 Submitted task: {task_id} - Type: {task_type} - Priority: {priority}")
        
        # Trigger asynchronous task assignment
        asyncio.create_task(self._assign_tasks())
        
        return task_id

    async def _assign_tasks(self):
        """Assign tasks to appropriate agents with load balancing"""
        if not self.task_queue:
            return
        
        assigned_tasks = []
        max_assignments_per_cycle = min(10, len(self.task_queue))
        
        for task in self.task_queue[:max_assignments_per_cycle]:
            if task.status != "pending":
                continue
            
            try:
                # Find suitable agents for this task
                suitable_agents = self._find_suitable_agents(task)
                
                if suitable_agents:
                    # Select best agent based on coordination mode
                    selected_agent = self._select_agent_for_task(task, suitable_agents)
                    
                    if selected_agent:
                        task.assigned_agent = selected_agent
                        task.status = "assigned"
                        
                        # Add to agent's task queue with metadata
                        self.agents[selected_agent].task_queue.append({
                            'task_id': task.task_id,
                            'task_type': task.task_type,
                            'input_data': task.input_data,
                            'deadline': task.deadline,
                            'assigned_at': datetime.now(),
                            'priority': task.priority
                        })
                        
                        assigned_tasks.append(task)
                        print(f"🎯 Assigned task {task.task_id} to agent {selected_agent}")
                
                else:
                    # No suitable agents found
                    if task.deadline and task.deadline < datetime.now():
                        task.status = "expired"
                        assigned_tasks.append(task)
                        print(f"⏰ Task {task.task_id} expired before assignment")
                        
            except Exception as e:
                print(f"❌ Error assigning task {task.task_id}: {e}")
                task.status = "error"
                assigned_tasks.append(task)
        
        # Remove assigned/expired/error tasks from queue
        for task in assigned_tasks:
            if task in self.task_queue:
                self.task_queue.remove(task)
        
        # Process assigned tasks
        for task in assigned_tasks:
            if task.status == "assigned" and task.assigned_agent:
                asyncio.create_task(self._process_agent_task(task.assigned_agent, task.task_id))

    def _find_suitable_agents(self, task: Task) -> List[str]:
        """Find agents suitable for the task requirements with capacity checking"""
        suitable_agents = set()
        
        # Find agents with required capabilities
        for requirement in task.requirements:
            if requirement in self.capability_registry:
                suitable_agents.update(self.capability_registry[requirement])
        
        if not suitable_agents:
            return []
        
        # Filter by agent status, capacity, and health
        suitable_agents = [
            agent_id for agent_id in suitable_agents
            if (self.agents[agent_id].status == AgentStatus.ACTIVE and
                len(self.agents[agent_id].task_queue) < 
                self.agent_configs[agent_id].resource_limits['max_concurrent_tasks'] and
                self.agents[agent_id].performance_metrics['reliability_score'] > 0.3)
        ]
        
        return suitable_agents

    def _select_agent_for_task(self, task: Task, suitable_agents: List[str]) -> Optional[str]:
        """Select the best agent for the task based on coordination mode and performance"""
        if not suitable_agents:
            return None
            
        if len(suitable_agents) == 1:
            return suitable_agents[0]
        
        if self.coordination_mode == CoordinationMode.COLLABORATIVE:
            return self._select_agent_collaborative(task, suitable_agents)
        elif self.coordination_mode == CoordinationMode.COMPETITIVE:
            return self._select_agent_competitive(task, suitable_agents)
        else:  # HYBRID
            return self._select_agent_hybrid(task, suitable_agents)

    def _select_agent_collaborative(self, task: Task, agents: List[str]) -> str:
        """Select agent collaboratively considering overall system efficiency"""
        agent_scores = {}
        
        for agent_id in agents:
            agent_state = self.agents[agent_id]
            agent_config = self.agent_configs[agent_id]
            
            # Performance score (weighted combination)
            metrics = agent_state.performance_metrics
            performance_score = (
                metrics['success_rate'] * agent_config.performance_weights['success_rate'] +
                metrics['efficiency_score'] * agent_config.performance_weights['efficiency'] +
                metrics['reliability_score'] * agent_config.performance_weights['reliability']
            )
            
            # Load score (prefer less loaded agents)
            current_load = len(agent_state.task_queue)
            max_load = agent_config.resource_limits['max_concurrent_tasks']
            load_score = 1 - (current_load / max_load) if max_load > 0 else 1.0
            
            # Capability match score
            capability_match = len(set(task.requirements) & set(agent_state.capabilities))
            capability_score = capability_match / len(task.requirements)
            
            # Trust score (average trust with other agents)
            trust_score = np.mean([
                self.trust_scores.get((agent_id, other_id), 0.5)
                for other_id in self.agents if other_id != agent_id
            ])
            
            # Combined collaborative score
            total_score = (
                performance_score * 0.35 +
                load_score * 0.25 +
                capability_score * 0.25 +
                trust_score * 0.15
            )
            
            agent_scores[agent_id] = max(0.0, min(1.0, total_score))
        
        return max(agent_scores.items(), key=lambda x: x[1])[0]

    def _select_agent_competitive(self, task: Task, agents: List[str]) -> str:
        """Select agent competitively (auction-based selection)"""
        bids = {}
        
        for agent_id in agents:
            agent_state = self.agents[agent_id]
            
            # Base bid on performance, capability, and urgency
            performance = agent_state.performance_metrics['success_rate']
            capability_match = len(set(task.requirements) & set(agent_state.capabilities))
            efficiency = agent_state.performance_metrics['efficiency_score']
            
            # Competitive bid with some randomness for exploration
            base_bid = performance * capability_match * efficiency
            bid_variation = np.random.uniform(0.9, 1.1)  # ±10% variation
            bid = base_bid * bid_variation * (task.priority / 10.0)
            
            bids[agent_id] = bid
        
        return max(bids.items(), key=lambda x: x[1])[0]

    def _select_agent_hybrid(self, task: Task, agents: List[str]) -> str:
        """Select agent using hybrid approach based on task characteristics"""
        # Use collaborative selection for high-priority or complex tasks
        if task.priority >= 8 or len(task.requirements) > 3:
            return self._select_agent_collaborative(task, agents)
        # Use competitive selection for low-priority or simple tasks
        elif task.priority <= 3:
            return self._select_agent_competitive(task, agents)
        else:
            # Balanced approach for medium priority
            collaborative_score = self._select_agent_collaborative(task, agents)
            competitive_score = self._select_agent_competitive(task, agents)
            
            # Prefer collaborative for better system health, but allow some competition
            return collaborative_score if np.random.random() > 0.3 else competitive_score

    async def _process_agent_task(self, agent_id: str, task_id: str):
        """Process a task assigned to an agent with comprehensive error handling"""
        if agent_id not in self.agents:
            print(f"❌ Agent {agent_id} not found for task {task_id}")
            return
        
        agent_state = self.agents[agent_id]
        start_time = datetime.now()
        
        try:
            # Find the task in agent's queue
            task_item = next((t for t in agent_state.task_queue if t['task_id'] == task_id), None)
            if not task_item:
                print(f"❌ Task {task_id} not found in agent {agent_id} queue")
                return
            
            # Update agent resource usage
            agent_state.resource_usage['active_tasks'] += 1
            
            # Simulate task processing with variable complexity
            base_processing_time = self._calculate_processing_time(task_item['task_type'])
            processing_time = base_processing_time * np.random.uniform(0.8, 1.2)
            
            await asyncio.sleep(min(processing_time, 5.0))  # Cap at 5 seconds for simulation
            
            # Determine success based on agent reliability and task complexity
            success_probability = agent_state.performance_metrics['reliability_score']
            success = np.random.random() < success_probability
            
            # Generate comprehensive task result
            result_data = {
                'success': success,
                'processing_time': processing_time,
                'result': self._generate_task_result(task_item['task_type'], success),
                'timestamp': datetime.now(),
                'agent_id': agent_id,
                'resource_usage': {
                    'cpu': np.random.uniform(0.1, 0.5),
                    'memory': np.random.uniform(10, 100)
                }
            }
            
            # Update agent performance metrics
            self._update_agent_performance(agent_id, success, processing_time)
            
            # Update trust scores with other agents
            self._update_trust_scores(agent_id, success)
            
            # Handle task completion
            await self._handle_task_completion(agent_id, task_id, result_data, start_time)
            
        except asyncio.CancelledError:
            print(f"⚠️ Task {task_id} processing cancelled for agent {agent_id}")
            await self._handle_task_completion(agent_id, task_id, {
                'success': False,
                'error': 'Task cancelled',
                'timestamp': datetime.now()
            }, start_time)
            
        except Exception as e:
            print(f"❌ Error processing task {task_id} by agent {agent_id}: {e}")
            await self._handle_task_completion(agent_id, task_id, {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }, start_time)
            
        finally:
            # Always clean up agent resource usage
            if agent_id in self.agents:
                self.agents[agent_id].resource_usage['active_tasks'] = max(0, 
                    self.agents[agent_id].resource_usage['active_tasks'] - 1)
                
            # Remove from agent's queue
            if agent_id in self.agents:
                agent_state.task_queue = [t for t in agent_state.task_queue if t['task_id'] != task_id]

    def _calculate_processing_time(self, task_type: str) -> float:
        """Calculate expected processing time based on task type"""
        processing_times = {
            'strategy_planning': 2.0,
            'risk_assessment': 1.5,
            'opportunity_detection': 0.5,
            'trade_execution': 0.2,
            'market_analysis': 1.0,
            'anomaly_detection': 0.8,
            'pattern_recognition': 1.2
        }
        return processing_times.get(task_type, 1.0)

    def _generate_task_result(self, task_type: str, success: bool) -> Dict[str, Any]:
        """Generate realistic task results based on task type and success"""
        if not success:
            return {'error': 'Task execution failed', 'recommendation': 'retry'}
        
        base_results = {
            'strategy_planning': {
                'recommended_action': 'BUY' if np.random.random() > 0.5 else 'SELL',
                'confidence': np.random.uniform(0.7, 0.95),
                'time_horizon': np.random.choice(['SHORT', 'MEDIUM', 'LONG'])
            },
            'risk_assessment': {
                'risk_level': np.random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'max_drawdown': np.random.uniform(0.01, 0.1),
                'var_95': np.random.uniform(0.02, 0.15)
            },
            'opportunity_detection': {
                'opportunity_type': np.random.choice(['ARBITRAGE', 'MOMENTUM', 'MEAN_REVERSION']),
                'expected_return': np.random.uniform(0.005, 0.05),
                'time_window_minutes': np.random.randint(1, 30)
            },
            'trade_execution': {
                'executed_price': np.random.uniform(100, 500),
                'slippage': np.random.uniform(0.001, 0.01),
                'fill_rate': np.random.uniform(0.8, 1.0)
            }
        }
        
        return base_results.get(task_type, {'status': 'completed', 'details': 'Task executed successfully'})

    async def _handle_task_completion(self, agent_id: str, task_id: str, result: Dict, start_time: datetime = None):
        """Handle task completion and update system state comprehensively"""
        completion_time = (datetime.now() - start_time).total_seconds() if start_time else 0
        
        if result['success']:
            self.performance_metrics['tasks_completed'] += 1
            if agent_id in self.agents:
                self.agents[agent_id].completed_tasks += 1
            print(f"✅ Task {task_id} completed successfully by agent {agent_id} in {completion_time:.2f}s")
        else:
            self.performance_metrics['tasks_failed'] += 1
            if agent_id in self.agents:
                self.agents[agent_id].failed_tasks += 1
            print(f"❌ Task {task_id} failed by agent {agent_id}. Error: {result.get('error', 'Unknown')}")
        
        # Add to task history for learning
        self.task_history.append({
            'task_id': task_id,
            'agent_id': agent_id,
            'success': result['success'],
            'processing_time': completion_time,
            'timestamp': datetime.now()
        })
        
        # Update system performance metrics
        self._update_system_metrics()

    def _update_agent_performance(self, agent_id: str, success: bool, processing_time: float):
        """Update agent performance metrics with adaptive learning"""
        if agent_id not in self.agents:
            return
            
        agent_state = self.agents[agent_id]
        metrics = agent_state.performance_metrics
        
        # Adaptive learning rate based on recent performance
        recent_tasks = [t for t in list(self.task_history)[-20:] if t['agent_id'] == agent_id]
        learning_rate = 0.1 if len(recent_tasks) < 10 else 0.05
        
        # Update success rate (exponential moving average)
        current_success = 1.0 if success else 0.0
        metrics['success_rate'] = (learning_rate * current_success + 
                                 (1 - learning_rate) * metrics['success_rate'])
        
        # Update processing time (handle division by zero)
        if processing_time > 0:
            metrics['avg_processing_time'] = (learning_rate * processing_time + 
                                            (1 - learning_rate) * metrics['avg_processing_time'])
        
        # Update reliability score with non-linear adjustments
        if success:
            reliability_boost = 0.02 * (1 - metrics['reliability_score'])  # Larger boost when reliability is low
            metrics['reliability_score'] = min(1.0, metrics['reliability_score'] + reliability_boost)
        else:
            reliability_penalty = 0.05 * metrics['reliability_score']  # Larger penalty when reliability is high
            metrics['reliability_score'] = max(0.1, metrics['reliability_score'] - reliability_penalty)
        
        # Update efficiency score (inverse of processing time normalized)
        max_expected_time = 10.0  # Maximum expected processing time in seconds
        efficiency = 1.0 - (min(processing_time, max_expected_time) / max_expected_time)
        metrics['efficiency_score'] = (learning_rate * efficiency + 
                                     (1 - learning_rate) * metrics['efficiency_score'])
        
        # Update throughput (tasks per minute)
        total_tasks = agent_state.completed_tasks + agent_state.failed_tasks
        if total_tasks > 0:
            metrics['throughput'] = agent_state.completed_tasks / total_tasks * 60  # Normalized to per minute

    def _update_trust_scores(self, agent_id: str, success: bool):
        """Update trust scores between agents based on performance"""
        trust_change = 0.05 if success else -0.1
        
        for other_agent_id in self.agents:
            if other_agent_id != agent_id:
                # Update trust in both directions
                trust_key_forward = (agent_id, other_agent_id)
                trust_key_backward = (other_agent_id, agent_id)
                
                if trust_key_forward in self.trust_scores:
                    self.trust_scores[trust_key_forward] = max(0.1, min(1.0,
                        self.trust_scores[trust_key_forward] + trust_change))
                
                if trust_key_backward in self.trust_scores:
                    self.trust_scores[trust_key_backward] = max(0.1, min(1.0,
                        self.trust_scores[trust_key_backward] + trust_change))

    def _update_system_metrics(self):
        """Update overall system performance metrics comprehensively"""
        total_tasks = self.performance_metrics['tasks_completed'] + self.performance_metrics['tasks_failed']
        
        # Update average task completion time
        if total_tasks > 0:
            recent_tasks = list(self.task_history)[-100:]  # Last 100 tasks
            if recent_tasks:
                avg_time = np.mean([t['processing_time'] for t in recent_tasks if t['processing_time'] > 0])
                self.performance_metrics['avg_task_completion_time'] = avg_time
        
        # Update agent utilization
        for agent_id, agent_state in self.agents.items():
            max_tasks = self.agent_configs[agent_id].resource_limits['max_concurrent_tasks']
            current_tasks = len(agent_state.task_queue)
            utilization = current_tasks / max_tasks if max_tasks > 0 else 0.0
            self.performance_metrics['agent_utilization'][agent_id] = utilization
        
        # Update system throughput and error rate
        if total_tasks > 0:
            self.performance_metrics['system_throughput'] = self.performance_metrics['tasks_completed'] / total_tasks
            self.performance_metrics['error_rate'] = self.performance_metrics['tasks_failed'] / total_tasks

    async def coordinate_agents(self, task_id: str, agent_ids: List[str], 
                               coordination_mode: CoordinationMode) -> CoordinationResult:
        """Coordinate multiple agents for complex task execution"""
        self.performance_metrics['coordination_events'] += 1
        
        print(f"🤝 Coordinating agents {agent_ids} for task {task_id} using {coordination_mode.value} mode")
        
        # Validate agent availability
        available_agents = [aid for aid in agent_ids if aid in self.agents and 
                          self.agents[aid].status == AgentStatus.ACTIVE]
        
        if not available_agents:
            return CoordinationResult(
                coordination_id=f"COORD_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                participating_agents=[],
                result={'error': 'No available agents for coordination'},
                coordination_mode=coordination_mode,
                timestamp=datetime.now(),
                success=False
            )
        
        try:
            # Simulate coordination process with timeout
            coordination_results = {}
            coordination_tasks = []
            
            for agent_id in available_agents:
                task = self._get_agent_contribution(agent_id, task_id)
                coordination_tasks.append(task)
            
            # Wait for all contributions with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*coordination_tasks, return_exceptions=True),
                timeout=10.0
            )
            
            # Process results
            for i, agent_id in enumerate(available_agents):
                if i < len(results) and not isinstance(results[i], Exception):
                    coordination_results[agent_id] = results[i]
                else:
                    coordination_results[agent_id] = {
                        'agent_id': agent_id,
                        'contribution': 0.0,
                        'confidence': 0.0,
                        'error': 'Coordination timeout or error'
                    }
            
            # Combine results based on coordination mode
            combined_result = self._combine_coordination_results(coordination_results, coordination_mode)
            
            coordination_result = CoordinationResult(
                coordination_id=f"COORD_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                participating_agents=available_agents,
                result=combined_result,
                coordination_mode=coordination_mode,
                timestamp=datetime.now(),
                success=True
            )
            
            self.coordination_history.append(coordination_result)
            
            return coordination_result
            
        except asyncio.TimeoutError:
            error_result = CoordinationResult(
                coordination_id=f"COORD_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                participating_agents=available_agents,
                result={'error': 'Coordination timeout'},
                coordination_mode=coordination_mode,
                timestamp=datetime.now(),
                success=False
            )
            self.coordination_history.append(error_result)
            return error_result

    async def _get_agent_contribution(self, agent_id: str, task_id: str) -> Dict:
        """Get contribution from an agent for coordination with realistic simulation"""
        # Simulate agent processing time based on agent type
        processing_time = np.random.uniform(0.1, 1.0)
        await asyncio.sleep(processing_time)
        
        # Generate realistic contribution based on agent type
        agent_type = self.agents[agent_id].agent_type
        contribution_base = np.random.uniform(0.3, 0.9)
        confidence_base = np.random.uniform(0.5, 0.95)
        
        # Adjust based on agent performance
        performance_boost = self.agents[agent_id].performance_metrics['success_rate'] * 0.2
        contribution = min(1.0, contribution_base + performance_boost)
        confidence = min(1.0, confidence_base + performance_boost)
        
        return {
            'agent_id': agent_id,
            'agent_type': agent_type.value,
            'contribution': contribution,
            'confidence': confidence,
            'processing_time': processing_time,
            'timestamp': datetime.now()
        }

    def _combine_coordination_results(self, results: Dict[str, Dict], 
                                    mode: CoordinationMode) -> Dict:
        """Combine coordination results based on mode with sophisticated algorithms"""
        if not results:
            return {'error': 'No results to combine'}
        
        if mode == CoordinationMode.COLLABORATIVE:
            # Weighted average based on confidence and performance
            weighted_contributions = []
            total_weight = 0
            
            for agent_id, result in results.items():
                if 'error' not in result:
                    # Weight by confidence and agent reliability
                    agent_weight = (result['confidence'] * 
                                  self.agents[agent_id].performance_metrics['reliability_score'])
                    weighted_contributions.append(result['contribution'] * agent_weight)
                    total_weight += agent_weight
            
            if total_weight > 0:
                combined_value = sum(weighted_contributions) / total_weight
            else:
                combined_value = np.mean([r['contribution'] for r in results.values()])
                
        elif mode == CoordinationMode.COMPETITIVE:
            # Select the best contribution (highest confidence * contribution)
            best_score = -1
            best_contribution = 0
            
            for agent_id, result in results.items():
                if 'error' not in result:
                    score = result['contribution'] * result['confidence']
                    if score > best_score:
                        best_score = score
                        best_contribution = result['contribution']
            
            combined_value = best_contribution if best_score >= 0 else 0.0
            
        else:  # HYBRID
            # Blend collaborative and competitive approaches
            collaborative_result = self._combine_coordination_results(results, CoordinationMode.COLLABORATIVE)
            competitive_result = self._combine_coordination_results(results, CoordinationMode.COMPETITIVE)
            
            # Weight based on result quality
            collaborative_quality = np.mean([r['confidence'] for r in results.values()])
            combined_value = (collaborative_result.get('combined_value', 0) * collaborative_quality +
                            competitive_result.get('combined_value', 0) * (1 - collaborative_quality))
        
        return {
            'combined_value': combined_value,
            'participating_agents': list(results.keys()),
            'individual_contributions': results,
            'combined_mode': mode.value,
            'combined_at': datetime.now()
        }

    async def _monitor_agents(self):
        """Continuous monitoring of agent health and performance"""
        while self.is_running:
            try:
                current_time = datetime.now()
                agents_to_remove = []
                
                for agent_id, agent_state in self.agents.items():
                    # Check agent heartbeat
                    time_since_heartbeat = (current_time - agent_state.last_heartbeat).total_seconds()
                    
                    if time_since_heartbeat > 300:  # 5 minutes without heartbeat
                        print(f"⚠️ Agent {agent_id} appears unresponsive. Time since heartbeat: {time_since_heartbeat:.1f}s")
                        agent_state.status = AgentStatus.ERROR
                    
                    # Update resource usage simulation
                    agent_state.resource_usage['memory_usage'] = np.random.uniform(10, 200)
                    agent_state.resource_usage['cpu_usage'] = np.random.uniform(0.1, 0.8)
                    agent_state.resource_usage['network_usage'] = np.random.uniform(1, 50)
                    
                    # Simulate heartbeat for active agents
                    if agent_state.status == AgentStatus.ACTIVE:
                        agent_state.last_heartbeat = current_time
                    
                    # Remove terminated agents
                    if agent_state.status == AgentStatus.TERMINATED:
                        agents_to_remove.append(agent_id)
                
                # Clean up terminated agents
                for agent_id in agents_to_remove:
                    await self._remove_agent(agent_id)
                
                # Log system status periodically
                if int(current_time.timestamp()) % 60 == 0:  # Every minute
                    active_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.ACTIVE)
                    print(f"📊 System Status: {active_agents}/{len(self.agents)} agents active, "
                          f"{len(self.task_queue)} tasks queued, "
                          f"{self.performance_metrics['tasks_completed']} tasks completed")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"❌ Error in agent monitoring: {e}")
                await asyncio.sleep(30)  # Longer delay on error

    async def _optimize_system_performance(self):
        """Continuous system performance optimization"""
        while self.is_running:
            try:
                # Adaptive learning parameter adjustment
                total_tasks = self.performance_metrics['tasks_completed'] + self.performance_metrics['tasks_failed']
                if total_tasks > 100:
                    success_rate = self.performance_metrics['tasks_completed'] / total_tasks
                    
                    # Adjust collaboration threshold based on success rate
                    if success_rate < 0.8:
                        self.learning_parameters['collaboration_threshold'] = min(0.9, 
                            self.learning_parameters['collaboration_threshold'] + 0.05)
                    elif success_rate > 0.9:
                        self.learning_parameters['collaboration_threshold'] = max(0.5,
                            self.learning_parameters['collaboration_threshold'] - 0.02)
                
                # Clean up old coordination history
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.coordination_history = [
                    coord for coord in self.coordination_history 
                    if coord.timestamp > cutoff_time
                ]
                
                # Trim task history if too large
                if len(self.task_history) > self.task_history.maxlen:
                    self.task_history = deque(list(self.task_history)[-self.task_history.maxlen:])
                
                await asyncio.sleep(60)  # Optimize every minute
                
            except Exception as e:
                print(f"❌ Error in performance optimization: {e}")
                await asyncio.sleep(120)  # Longer delay on error

    async def _remove_agent(self, agent_id: str):
        """Safely remove an agent from the system"""
        if agent_id in self.agents:
            agent_state = self.agents[agent_id]
            
            # Reassign any pending tasks
            if agent_state.task_queue:
                print(f"🔄 Reassigning {len(agent_state.task_queue)} tasks from agent {agent_id}")
                for task_item in agent_state.task_queue:
                    # Resubmit tasks to the system
                    await self.submit_task(
                        task_type=task_item['task_type'],
                        requirements=[],  # Will be determined by original task
                        input_data=task_item['input_data'],
                        priority=task_item.get('priority', 1)
                    )
            
            # Remove from capability registry
            for capability in agent_state.capabilities:
                if agent_id in self.capability_registry[capability]:
                    self.capability_registry[capability].remove(agent_id)
            
            # Remove trust scores
            trust_keys_to_remove = [k for k in self.trust_scores.keys() if agent_id in k]
            for key in trust_keys_to_remove:
                del self.trust_scores[key]
            
            # Remove agent
            del self.agents[agent_id]
            del self.agent_configs[agent_id]
            
            print(f"🗑️ Removed agent: {agent_id}")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status report"""
        active_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.ACTIVE)
        total_tasks = self.performance_metrics['tasks_completed'] + self.performance_metrics['tasks_failed']
        
        return {
            'system_health': {
                'total_agents': len(self.agents),
                'active_agents': active_agents,
                'queued_tasks': len(self.task_queue),
                'system_uptime': 'N/A',  # Would be calculated from start time
                'is_running': self.is_running
            },
            'performance_metrics': self.performance_metrics.copy(),
            'agent_summary': {
                agent_id: {
                    'type': state.agent_type.value,
                    'status': state.status.value,
                    'capabilities': state.capabilities,
                    'performance': state.performance_metrics,
                    'current_load': len(state.task_queue)
                }
                for agent_id, state in self.agents.items()
            },
            'coordination_stats': {
                'total_coordination_events': len(self.coordination_history),
                'recent_coordination_success_rate': np.mean([
                    1 if coord.success else 0 
                    for coord in list(self.coordination_history)[-10:]
                ]) if self.coordination_history else 0.0
            }
        }

    async def shutdown(self):
        """Gracefully shutdown the multi-agent system"""
        print("🛑 Shutting down Multi-Agent Orchestrator...")
        
        self.is_running = False
        
        # Cancel monitoring task
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Set all agents to terminated status
        for agent_id in list(self.agents.keys()):
            self.agents[agent_id].status = AgentStatus.TERMINATED
        
        print("✅ Multi-Agent Orchestrator shutdown complete")

# Example usage and testing
async def main():
    """Example demonstration of the MultiAgentOrchestrator"""
    orchestrator = MultiAgentOrchestrator()
    
    try:
        # Initialize the system
        await orchestrator.initialize()
        
        # Submit some example tasks
        tasks = []
        for i in range(5):
            task_id = await orchestrator.submit_task(
                task_type='opportunity_detection',
                requirements=['opportunity_detection', 'pattern_recognition'],
                input_data={'market': 'ETH-USDT', 'timeframe': '5m'},
                priority=np.random.randint(1, 10)
            )
            tasks.append(task_id)
        
        # Wait for tasks to process
        await asyncio.sleep(10)
        
        # Get system status
        status = await orchestrator.get_system_status()
        print(f"System Status: {status['system_health']}")
        
        # Demonstrate coordination
        if len(orchestrator.agents) >= 2:
            agent_ids = list(orchestrator.agents.keys())[:2]
            coord_result = await orchestrator.coordinate_agents(
                task_id="TEST_COORD",
                agent_ids=agent_ids,
                coordination_mode=CoordinationMode.COLLABORATIVE
            )
            print(f"Coordination Result: {coord_result.result}")
        
    finally:
        # Clean shutdown
        await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(main())