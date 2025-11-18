"""
AI-NEXUS v5.0 - RPC Load Balancer
7P-PILLAR: BOT11-PERF
PURPOSE: Sub-millisecond execution infrastructure
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import heapq

class NodeHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class LoadBalanceStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LATENCY_BASED = "latency_based"
    COST_BASED = "cost_based"
    HYBRID = "hybrid"

@dataclass
class NodeMetrics:
    node_id: str
    endpoint: str
    response_time: float
    success_rate: float
    error_count: int
    request_count: int
    last_checked: float
    health: NodeHealth
    chain_id: int
    provider: str
    cost_per_request: float

@dataclass
class LoadBalanceDecision:
    node_id: str
    endpoint: str
    confidence: float
    expected_latency: float
    fallback_nodes: List[str]
    strategy_used: LoadBalanceStrategy

class RPCLoadBalancer:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.nodes: Dict[str, NodeMetrics] = {}
        self.request_history: List[Tuple[str, float, bool]] = []
        
        self.load_balance_strategy = LoadBalanceStrategy.HYBRID
        self.health_check_interval = config.get('health_check_interval', 10)
        self.max_response_time = config.get('max_response_time', 1000)
        self.min_success_rate = config.get('min_success_rate', 0.95)
        
        self.current_node_index = 0
        self.performance_weights = {
            'latency': 0.5,
            'success_rate': 0.3,
            'cost': 0.2
        }
        
        self.initialize_nodes()
        self.start_health_monitoring()

    def initialize_nodes(self):
        """Initialize RPC nodes from configuration"""
        nodes_config = self.config.get('rpc_nodes', {})
        
        for chain, chain_nodes in nodes_config.items():
            for node_config in chain_nodes:
                node_id = f"{chain}_{node_config['provider']}"
                
                self.nodes[node_id] = NodeMetrics(
                    node_id=node_id,
                    endpoint=node_config['endpoint'],
                    response_time=0.0,
                    success_rate=1.0,
                    error_count=0,
                    request_count=0,
                    last_checked=time.time(),
                    health=NodeHealth.UNKNOWN,
                    chain_id=node_config.get('chain_id', 1),
                    provider=node_config['provider'],
                    cost_per_request=node_config.get('cost_per_request', 0.0)
                )
        
        self.logger.info(f"Initialized {len(self.nodes)} RPC nodes")

    async def get_optimal_node(self, chain_id: int, method: str = "eth_call", priority: str = "latency") -> LoadBalanceDecision:
        """Get optimal RPC node for request"""
        available_nodes = [
            node for node in self.nodes.values()
            if node.chain_id == chain_id and node.health in [NodeHealth.HEALTHY, NodeHealth.DEGRADED]
        ]
        
        if not available_nodes:
            raise Exception(f"No healthy nodes available for chain {chain_id}")
        
        # Select node based on strategy
        if self.load_balance_strategy == LoadBalanceStrategy.LATENCY_BASED:
            selected_node = await self.select_by_latency(available_nodes, method)
        elif self.load_balance_strategy == LoadBalanceStrategy.COST_BASED:
            selected_node = await self.select_by_cost(available_nodes, method)
        elif self.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            selected_node = await self.select_round_robin(available_nodes)
        else:  # HYBRID
            selected_node = await self.select_hybrid(available_nodes, method, priority)
        
        # Get fallback nodes
        fallback_nodes = await self.select_fallback_nodes(available_nodes, selected_node.node_id)
        
        return LoadBalanceDecision(
            node_id=selected_node.node_id,
            endpoint=selected_node.endpoint,
            confidence=self.calculate_confidence(selected_node),
            expected_latency=selected_node.response_time,
            fallback_nodes=fallback_nodes,
            strategy_used=self.load_balance_strategy
        )

    async def select_by_latency(self, nodes: List[NodeMetrics], method: str) -> NodeMetrics:
        """Select node based on lowest latency"""
        weighted_nodes = []
        
        for node in nodes:
            method_factor = self.get_method_latency_factor(method)
            adjusted_latency = node.response_time * method_factor
            success_penalty = (1.0 - node.success_rate) * 100
            total_score = adjusted_latency + success_penalty
            weighted_nodes.append((total_score, node))
        
        weighted_nodes.sort(key=lambda x: x[0])
        return weighted_nodes[0][1]

    async def select_by_cost(self, nodes: List[NodeMetrics], method: str) -> NodeMetrics:
        """Select node based on lowest cost"""
        scored_nodes = []
        
        for node in nodes:
            cost_score = node.cost_per_request * 1000
            perf_penalty = node.response_time * 0.1
            total_score = cost_score + perf_penalty
            scored_nodes.append((total_score, node))
        
        scored_nodes.sort(key=lambda x: x[0])
        return scored_nodes[0][1]

    async def select_round_robin(self, nodes: List[NodeMetrics]) -> NodeMetrics:
        """Select node using round-robin strategy"""
        if not hasattr(self, 'rr_node_index'):
            self.rr_node_index = 0
        
        node = nodes[self.rr_node_index % len(nodes)]
        self.rr_node_index += 1
        return node

    async def select_hybrid(self, nodes: List[NodeMetrics], method: str, priority: str) -> NodeMetrics:
        """Select node using hybrid strategy"""
        scored_nodes = []
        
        for node in nodes:
            score = await self.calculate_node_score(node, method, priority)
            scored_nodes.append((score, node))
        
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        return scored_nodes[0][1]

    async def calculate_node_score(self, node: NodeMetrics, method: str, priority: str) -> float:
        """Calculate comprehensive node score"""
        latency_score = self.normalize_latency(node.response_time)
        success_score = node.success_rate
        cost_score = 1.0 - min(node.cost_per_request * 100, 1.0)
        
        method_factor = self.get_method_priority_factor(method, priority)
        
        if priority == "latency":
            weights = {'latency': 0.6, 'success_rate': 0.3, 'cost': 0.1}
        elif priority == "reliability":
            weights = {'latency': 0.2, 'success_rate': 0.7, 'cost': 0.1}
        elif priority == "cost":
            weights = {'latency': 0.1, 'success_rate': 0.3, 'cost': 0.6}
        else:  # balanced
            weights = self.performance_weights
        
        composite_score = (
            latency_score * weights['latency'] +
            success_score * weights['success_rate'] +
            cost_score * weights['cost']
        )
        
        return composite_score * method_factor

    def normalize_latency(self, latency: float) -> float:
        """Normalize latency to 0-1 scale (lower latency = higher score)"""
        return max(0.0, 1.0 - (latency / self.max_response_time))

    def get_method_latency_factor(self, method: str) -> float:
        """Get latency factor for specific RPC method"""
        factors = {
            'eth_call': 1.0,
            'eth_getBalance': 1.0,
            'eth_getTransactionReceipt': 1.1,
            'eth_sendRawTransaction': 1.3,
            'eth_estimateGas': 1.2,
            'eth_getLogs': 1.5
        }
        return factors.get(method, 1.0)

    def get_method_priority_factor(self, method: str, priority: str) -> float:
        """Get priority factor for method and priority combination"""
        base_factors = {
            'latency': {
                'eth_call': 1.2,
                'eth_sendRawTransaction': 1.5,
                'eth_estimateGas': 1.3
            },
            'reliability': {
                'eth_sendRawTransaction': 1.4,
                'eth_getTransactionReceipt': 1.3
            },
            'cost': {
                'eth_getLogs': 1.3,
                'eth_call': 1.1
            }
        }
        
        return base_factors.get(priority, {}).get(method, 1.0)

    async def select_fallback_nodes(self, available_nodes: List[NodeMetrics], primary_node_id: str, count: int = 2) -> List[str]:
        """Select fallback nodes for redundancy"""
        candidate_nodes = [node for node in available_nodes if node.node_id != primary_node_id]
        
        scored_nodes = []
        for node in candidate_nodes:
            score = await self.calculate_node_score(node, "eth_call", "balanced")
            scored_nodes.append((score, node))
        
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        return [node.node_id for _, node in scored_nodes[:count]]

    def calculate_confidence(self, node: NodeMetrics) -> float:
        """Calculate confidence score for node selection"""
        base_confidence = node.success_rate
        
        recent_requests = [
            req for req in self.request_history 
            if req[0] == node.node_id and req[1] > time.time() - 300
        ]
        
        if recent_requests:
            recent_success_rate = sum(1 for req in recent_requests if req[2]) / len(recent_requests)
            stability_factor = min(recent_success_rate / node.success_rate, 1.0)
        else:
            stability_factor = 1.0
        
        health_factor = 1.0 if node.health == NodeHealth.HEALTHY else 0.7
        
        return base_confidence * stability_factor * health_factor

    async def execute_request(self, chain_id: int, method: str, params: List, priority: str = "latency") -> Dict:
        """Execute RPC request through load balancer"""
        max_retries = 3
        
        for retry_count in range(max_retries):
            try:
                decision = await self.get_optimal_node(chain_id, method, priority)
                node = self.nodes[decision.node_id]
                
                start_time = time.time()
                success = False
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            node.endpoint,
                            json={
                                "jsonrpc": "2.0",
                                "method": method,
                                "params": params,
                                "id": 1
                            },
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            result = await response.json()
                            success = True
                            
                except Exception as e:
                    self.logger.warning(f"Request to {node.node_id} failed: {e}")
                    success = False
                    result = None
                
                latency = (time.time() - start_time) * 1000
                await self.update_node_metrics(node.node_id, latency, success)
                
                if success:
                    return result
                else:
                    # Try fallback nodes
                    for fallback_id in decision.fallback_nodes:
                        try:
                            fallback_node = self.nodes[fallback_id]
                            self.logger.info(f"Trying fallback node: {fallback_id}")
                            
                            async with aiohttp.ClientSession() as session:
                                async with session.post(
                                    fallback_node.endpoint,
                                    json={
                                        "jsonrpc": "2.0",
                                        "method": method,
                                        "params": params,
                                        "id": 1
                                    },
                                    timeout=aiohttp.ClientTimeout(total=10)
                                ) as response:
                                    result = await response.json()
                                    success = True
                                    latency = (time.time() - start_time) * 1000
                                    
                                    await self.update_node_metrics(fallback_id, latency, success)
                                    return result
                                    
                        except Exception as e:
                            self.logger.warning(f"Fallback node {fallback_id} also failed: {e}")
                            continue
                    
            except Exception as e:
                self.logger.error(f"All nodes failed for request: {e}")
                if retry_count < max_retries - 1:
                    await asyncio.sleep(0.1 * (retry_count + 1))
        
        raise Exception(f"Failed to execute RPC request after {max_retries} retries")

    async def update_node_metrics(self, node_id: str, latency: float, success: bool):
        """Update node performance metrics"""
        if node_id not in self.nodes:
            return
            
        node = self.nodes[node_id]
        
        # Update response time (exponential moving average)
        if node.response_time == 0:
            node.response_time = latency
        else:
            alpha = 0.3
            node.response_time = alpha * latency + (1 - alpha) * node.response_time
        
        # Update success rate
        node.request_count += 1
        if not success:
            node.error_count += 1
        
        node.success_rate = 1.0 - (node.error_count / node.request_count)
        node.last_checked = time.time()
        
        # Update health status
        await self.update_node_health(node)
        
        # Store request history
        self.request_history.append((node_id, time.time(), success))
        
        # Clean old history
        cutoff_time = time.time() - 3600
        self.request_history = [
            req for req in self.request_history if req[1] > cutoff_time
        ]

    async def update_node_health(self, node: NodeMetrics):
        """Update node health status based on metrics"""
        if node.success_rate < self.min_success_rate:
            node.health = NodeHealth.UNHEALTHY
        elif node.response_time > self.max_response_time * 2:
            node.health = NodeHealth.UNHEALTHY
        elif node.response_time > self.max_response_time:
            node.health = NodeHealth.DEGRADED
        elif node.success_rate >= self.min_success_rate and node.response_time <= self.max_response_time:
            node.health = NodeHealth.HEALTHY
        else:
            node.health = NodeHealth.UNKNOWN

    def start_health_monitoring(self):
        """Start continuous health monitoring"""
        async def health_monitor():
            while True:
                try:
                    await self.perform_health_checks()
                    await asyncio.sleep(self.health_check_interval)
                except Exception as e:
                    self.logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(10)
        
        asyncio.create_task(health_monitor())

    async def perform_health_checks(self):
        """Perform health checks on all nodes"""
        health_check_tasks = []
        
        for node_id, node in self.nodes.items():
            task = self.check_node_health(node)
            health_check_tasks.append(task)
        
        await asyncio.gather(*health_check_tasks, return_exceptions=True)

    async def check_node_health(self, node: NodeMetrics):
        """Check health of a specific node"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    node.endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_blockNumber",
                        "params": [],
                        "id": 1
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        latency = (time.time() - start_time) * 1000
                        await self.update_node_metrics(node.node_id, latency, True)
                    else:
                        await self.update_node_metrics(node.node_id, self.max_response_time * 2, False)
                        
        except Exception as e:
            self.logger.debug(f"Health check failed for {node.node_id}: {e}")
            await self.update_node_metrics(node.node_id, self.max_response_time * 2, False)

    def get_performance_dashboard(self) -> Dict:
        """Get performance dashboard data"""
        healthy_nodes = [node for node in self.nodes.values() if node.health == NodeHealth.HEALTHY]
        degraded_nodes = [node for node in self.nodes.values() if node.health == NodeHealth.DEGRADED]
        unhealthy_nodes = [node for node in self.nodes.values() if node.health == NodeHealth.UNHEALTHY]
        
        if healthy_nodes:
            avg_latency = statistics.mean(node.response_time for node in healthy_nodes)
            avg_success = statistics.mean(node.success_rate for node in healthy_nodes)
        else:
            avg_latency = 0
            avg_success = 0
        
        return {
            "total_nodes": len(self.nodes),
            "healthy_nodes": len(healthy_nodes),
            "degraded_nodes": len(degraded_nodes),
            "unhealthy_nodes": len(unhealthy_nodes),
            "average_latency_ms": avg_latency,
            "average_success_rate": avg_success,
            "load_balance_strategy": self.load_balance_strategy.value,
            "recent_requests": len([r for r in self.request_history if r[1] > time.time() - 300])
        }
