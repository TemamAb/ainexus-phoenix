"""
AI-NEXUS v5.0 - EXECUTION AGENT MODULE
Advanced Trade Execution and Order Management Agent
Intelligent order routing with slippage optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import uuid
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    ICEBERG = "iceberg"
    TWAP = "twap"

class OrderStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ExecutionStrategy(Enum):
    AGGRESSIVE = "aggressive"
    PASSIVE = "passive"
    NEUTRAL = "neutral"
    DARK_POOL = "dark_pool"
    ATOMIC = "atomic"

@dataclass
class Order:
    order_id: str
    order_type: OrderType
    asset: str
    quantity: float
    price: Optional[float] = None
    side: str = "buy"  # "buy" or "sell"
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = None
    exchange: str = ""
    execution_strategy: ExecutionStrategy = ExecutionStrategy.NEUTRAL
    time_in_force: str = "GTC"  # Good Till Cancelled
    metadata: Dict[str, Any] = None

@dataclass
class ExecutionResult:
    execution_id: str
    order_id: str
    fill_price: float
    fill_quantity: float
    fees: float
    slippage: float
    execution_time: timedelta
    timestamp: datetime
    exchange: str
    status: OrderStatus
    metadata: Dict[str, Any]

@dataclass
class MarketConditions:
    liquidity: float
    spread: float
    volatility: float
    volume: float
    order_book_depth: Dict[str, List[float]]

class ExecutionAgent:
    """
    Advanced execution agent for intelligent trade execution
    Optimizes order routing, timing, and execution strategy
    """
    
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or f"execution_agent_{uuid.uuid4().hex[:8]}"
        self.order_history = []
        self.execution_history = []
        self.performance_metrics = {
            'orders_executed': 0,
            'total_volume': 0.0,
            'avg_slippage': 0.0,
            'success_rate': 0.0,
            'avg_execution_time': timedelta(0),
            'recent_performance': deque(maxlen=100)
        }
        
        # Exchange connectivity
        self.connected_exchanges = {}
        self.exchange_performance = {}
        
        # Execution parameters
        self.execution_params = {
            'max_slippage': 0.002,      # 0.2% maximum slippage
            'max_execution_time': 30,   # 30 seconds maximum
            'min_liquidity': 10000,     # $10k minimum liquidity
            'fee_structure': {
                'maker': 0.001,         # 0.1% maker fee
                'taker': 0.002          # 0.2% taker fee
            }
        }
        
        # Initialize execution strategies
        self._initialize_execution_strategies()
        
        # Slippage models
        self.slippage_models = {}
        
        # Order management
        self.pending_orders = {}
        self.active_orders = {}
    
    def _initialize_execution_strategies(self):
        """Initialize execution strategies and parameters"""
        
        self.execution_strategies = {
            ExecutionStrategy.AGGRESSIVE: {
                'slippage_tolerance': 0.005,
                'time_priority': 0.9,
                'price_priority': 0.1,
                'description': 'Prioritize speed over price'
            },
            ExecutionStrategy.PASSIVE: {
                'slippage_tolerance': 0.001,
                'time_priority': 0.1,
                'price_priority': 0.9,
                'description': 'Prioritize price over speed'
            },
            ExecutionStrategy.NEUTRAL: {
                'slippage_tolerance': 0.002,
                'time_priority': 0.5,
                'price_priority': 0.5,
                'description': 'Balance between speed and price'
            },
            ExecutionStrategy.DARK_POOL: {
                'slippage_tolerance': 0.001,
                'time_priority': 0.7,
                'price_priority': 0.3,
                'description': 'Use dark pools for large orders'
            },
            ExecutionStrategy.ATOMIC: {
                'slippage_tolerance': 0.003,
                'time_priority': 1.0,
                'price_priority': 0.0,
                'description': 'Atomic execution across multiple venues'
            }
        }
    
    async def connect_to_exchange(self, exchange_name: str, credentials: Dict = None):
        """Connect to trading exchange"""
        
        # Simulate exchange connection
        await asyncio.sleep(0.1)
        
        self.connected_exchanges[exchange_name] = {
            'connected': True,
            'last_heartbeat': datetime.now(),
            'latency': np.random.uniform(10, 100),  # ms
            'fee_structure': self.execution_params['fee_structure'],
            'order_limits': {
                'min_order_size': 10,
                'max_order_size': 100000,
                'rate_limit': 100  # orders per second
            }
        }
        
        print(f"Connected to {exchange_name}")
    
    async def create_order(self, 
                         asset: str,
                         quantity: float,
                         order_type: OrderType,
                         side: str,
                         execution_strategy: ExecutionStrategy = ExecutionStrategy.NEUTRAL,
                         price: Optional[float] = None,
                         time_in_force: str = "GTC") -> Order:
        """Create and submit a new order"""
        
        order_id = f"ORDER_{uuid.uuid4().hex[:8]}"
        
        order = Order(
            order_id=order_id,
            order_type=order_type,
            asset=asset,
            quantity=quantity,
            price=price,
            side=side,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            execution_strategy=execution_strategy,
            time_in_force=time_in_force,
            metadata={
                'created_by': self.agent_id,
                'strategy_params': self.execution_strategies[execution_strategy]
            }
        )
        
        # Add to order history
        self.order_history.append(order)
        self.pending_orders[order_id] = order
        
        print(f"Created order {order_id}: {side} {quantity} {asset} at {price if price else 'market'}")
        
        # Automatically execute the order
        asyncio.create_task(self._execute_order(order))
        
        return order
    
    async def _execute_order(self, order: Order) -> ExecutionResult:
        """Execute an order using optimal execution strategy"""
        
        start_time = datetime.now()
        
        try:
            # Select best exchange for execution
            selected_exchange = await self._select_execution_venue(order)
            order.exchange = selected_exchange
            
            # Update order status
            order.status = OrderStatus.SENT
            self.active_orders[order.order_id] = order
            
            # Execute based on order type
            if order.order_type == OrderType.MARKET:
                result = await self._execute_market_order(order, selected_exchange)
            elif order.order_type == OrderType.LIMIT:
                result = await self._execute_limit_order(order, selected_exchange)
            elif order.order_type == OrderType.TWAP:
                result = await self._execute_twap_order(order, selected_exchange)
            else:
                result = await self._execute_market_order(order, selected_exchange)  # Default
            
            execution_time = datetime.now() - start_time
            
            # Create execution result
            execution_result = ExecutionResult(
                execution_id=f"EXEC_{uuid.uuid4().hex[:8]}",
                order_id=order.order_id,
                fill_price=result['fill_price'],
                fill_quantity=result['fill_quantity'],
                fees=result['fees'],
                slippage=result['slippage'],
                execution_time=execution_time,
                timestamp=datetime.now(),
                exchange=selected_exchange,
                status=result['status'],
                metadata={
                    'execution_strategy': order.execution_strategy.value,
                    'venue_selection_reason': result.get('venue_reason', 'optimal_liquidity'),
                    'order_type': order.order_type.value
                }
            )
            
            # Update order status
            order.status = result['status']
            
            # Remove from active orders
            if order.order_id in self.active_orders:
                del self.active_orders[order.order_id]
            
            # Add to execution history
            self.execution_history.append(execution_result)
            
            # Update performance metrics
            self._update_performance_metrics(execution_result)
            
            print(f"Executed order {order.order_id}: {result['status'].value} "
                  f"at {result['fill_price']} with {result['slippage']:.4f} slippage")
            
            return execution_result
            
        except Exception as e:
            print(f"Order execution failed for {order.order_id}: {e}")
            
            # Mark order as failed
            order.status = OrderStatus.REJECTED
            
            # Create failed execution result
            failed_result = ExecutionResult(
                execution_id=f"EXEC_{uuid.uuid4().hex[:8]}",
                order_id=order.order_id,
                fill_price=0.0,
                fill_quantity=0.0,
                fees=0.0,
                slippage=0.0,
                execution_time=datetime.now() - start_time,
                timestamp=datetime.now(),
                exchange=order.exchange,
                status=OrderStatus.REJECTED,
                metadata={'error': str(e)}
            )
            
            self.execution_history.append(failed_result)
            
            return failed_result
    
    async def _select_execution_venue(self, order: Order) -> str:
        """Select optimal execution venue for the order"""
        
        available_exchanges = list(self.connected_exchanges.keys())
        
        if not available_exchanges:
            return "uniswap"  # Default
        
        # Score exchanges based on multiple factors
        exchange_scores = {}
        
        for exchange in available_exchanges:
            score = 0.0
            
            # Liquidity score
            liquidity_score = self._get_exchange_liquidity_score(exchange, order.asset)
            score += liquidity_score * 0.4
            
            # Fee score (lower fees = higher score)
            fee_structure = self.connected_exchanges[exchange]['fee_structure']
            fee_score = 1.0 - (fee_structure['taker'] / 0.01)  # Normalize to 1%
            score += fee_score * 0.3
            
            # Latency score (lower latency = higher score)
            latency = self.connected_exchanges[exchange]['latency']
            latency_score = 1.0 - (latency / 200)  # Normalize to 200ms
            score += max(0, latency_score) * 0.2
            
            # Reliability score (from historical performance)
            reliability_score = self._get_exchange_reliability(exchange)
            score += reliability_score * 0.1
            
            exchange_scores[exchange] = score
        
        # Select best exchange
        best_exchange = max(exchange_scores.items(), key=lambda x: x[1])[0]
        
        return best_exchange
    
    async def _execute_market_order(self, order: Order, exchange: str) -> Dict[str, Any]:
        """Execute market order"""
        
        # Simulate market order execution
        await asyncio.sleep(0.05)  # Simulate network latency
        
        # Get current market price (would come from real market data)
        current_price = await self._get_current_market_price(order.asset, exchange)
        
        # Calculate slippage based on order size and market conditions
        slippage = await self._calculate_slippage(order, exchange, current_price)
        
        # Apply slippage to fill price
        if order.side == "buy":
            fill_price = current_price * (1 + slippage)
        else:  # sell
            fill_price = current_price * (1 - slippage)
        
        # Calculate fees
        fees = await self._calculate_fees(order, exchange, fill_price, order.quantity)
        
        # Simulate execution (usually fully filled for market orders)
        fill_quantity = order.quantity
        
        return {
            'fill_price': fill_price,
            'fill_quantity': fill_quantity,
            'fees': fees,
            'slippage': slippage,
            'status': OrderStatus.FILLED,
            'venue_reason': 'market_order_execution'
        }
    
    async def _execute_limit_order(self, order: Order, exchange: str) -> Dict[str, Any]:
        """Execute limit order"""
        
        if order.price is None:
            raise ValueError("Limit order requires price")
        
        # Simulate limit order execution (more complex in reality)
        await asyncio.sleep(0.1)
        
        # Get current market price
        current_price = await self._get_current_market_price(order.asset, exchange)
        
        # Check if limit order can be filled
        if (order.side == "buy" and current_price <= order.price) or \
           (order.side == "sell" and current_price >= order.price):
            # Order can be filled at limit price or better
            fill_price = order.price
            slippage = 0.0  # No slippage for limit orders filled at limit price
            fill_quantity = order.quantity
            status = OrderStatus.FILLED
        else:
            # Order cannot be filled immediately
            fill_price = 0.0
            slippage = 0.0
            fill_quantity = 0.0
            status = OrderStatus.PENDING  # Would remain open in real implementation
        
        # Calculate fees (maker fees for limit orders)
        fees = await self._calculate_fees(order, exchange, fill_price, fill_quantity)
        
        return {
            'fill_price': fill_price,
            'fill_quantity': fill_quantity,
            'fees': fees,
            'slippage': slippage,
            'status': status,
            'venue_reason': 'limit_order_execution'
        }
    
    async def _execute_twap_order(self, order: Order, exchange: str) -> Dict[str, Any]:
        """Execute Time-Weighted Average Price order"""
        
        # TWAP execution splits order over time to minimize market impact
        num_slices = 5  # Split into 5 slices
        slice_quantity = order.quantity / num_slices
        
        total_filled = 0.0
        total_cost = 0.0
        total_fees = 0.0
        total_slippage = 0.0
        
        for i in range(num_slices):
            # Wait between slices (simulate time distribution)
            if i > 0:
                await asyncio.sleep(1.0)  # 1 second between slices
            
            # Execute slice as market order
            slice_order = Order(
                order_id=f"{order.order_id}_SLICE_{i}",
                order_type=OrderType.MARKET,
                asset=order.asset,
                quantity=slice_quantity,
                side=order.side,
                timestamp=datetime.now()
            )
            
            slice_result = await self._execute_market_order(slice_order, exchange)
            
            total_filled += slice_result['fill_quantity']
            total_cost += slice_result['fill_price'] * slice_result['fill_quantity']
            total_fees += slice_result['fees']
            total_slippage += slice_result['slippage']
        
        # Calculate average fill price
        avg_fill_price = total_cost / total_filled if total_filled > 0 else 0.0
        avg_slippage = total_slippage / num_slices
        
        return {
            'fill_price': avg_fill_price,
            'fill_quantity': total_filled,
            'fees': total_fees,
            'slippage': avg_slippage,
            'status': OrderStatus.FILLED,
            'venue_reason': 'twap_execution'
        }
    
    async def _get_current_market_price(self, asset: str, exchange: str) -> float:
        """Get current market price for asset on exchange"""
        # In reality, this would query exchange API
        # Using mock prices for demonstration
        
        base_prices = {
            'ETH': 1800.0,
            'BTC': 30000.0,
            'SOL': 95.0,
            'USDC': 1.0
        }
        
        # Extract base asset from pair (simplified)
        base_asset = asset.split('/')[0] if '/' in asset else asset
        
        price = base_prices.get(base_asset, 100.0)
        
        # Add some random variation
        price_variation = np.random.normal(0, 0.001)  # 0.1% variation
        return price * (1 + price_variation)
    
    async def _calculate_slippage(self, order: Order, exchange: str, current_price: float) -> float:
        """Calculate expected slippage for order"""
        
        # Slippage model based on order size and market conditions
        order_size_ratio = order.quantity / await self._get_exchange_liquidity(order.asset, exchange)
        
        # Base slippage from order size
        size_slippage = order_size_ratio * 0.1  # 10% impact for full liquidity usage
        
        # Market condition adjustment
        volatility = await self._get_market_volatility(order.asset)
        volatility_slippage = volatility * 0.5
        
        # Strategy adjustment
        strategy_params = self.execution_strategies[order.execution_strategy]
        strategy_slippage = strategy_params['slippage_tolerance'] * 0.5
        
        total_slippage = size_slippage + volatility_slippage + strategy_slippage
        
        # Cap at maximum allowed slippage
        return min(total_slippage, self.execution_params['max_slippage'])
    
    async def _calculate_fees(self, order: Order, exchange: str, fill_price: float, fill_quantity: float) -> float:
        """Calculate trading fees"""
        
        if exchange not in self.connected_exchanges:
            return 0.0
        
        fee_structure = self.connected_exchanges[exchange]['fee_structure']
        
        # Determine if maker or taker fee applies
        if order.order_type == OrderType.LIMIT and order.status == OrderStatus.FILLED:
            fee_rate = fee_structure['maker']
        else:
            fee_rate = fee_structure['taker']
        
        trade_value = fill_price * fill_quantity
        fees = trade_value * fee_rate
        
        return fees
    
    def _get_exchange_liquidity_score(self, exchange: str, asset: str) -> float:
        """Get liquidity score for exchange and asset"""
        # Simplified liquidity scoring
        base_liquidity = {
            'uniswap': 0.9,
            'sushiswap': 0.7,
            'binance': 0.95,
            'coinbase': 0.85
        }
        
        return base_liquidity.get(exchange, 0.5)
    
    async def _get_exchange_liquidity(self, asset: str, exchange: str) -> float:
        """Get available liquidity for asset on exchange"""
        # Mock liquidity values
        base_liquidity = {
            'uniswap': 5000000,
            'sushiswap': 3000000,
            'binance': 10000000,
            'coinbase': 8000000
        }
        
        return base_liquidity.get(exchange, 1000000)
    
    def _get_exchange_reliability(self, exchange: str) -> float:
        """Get exchange reliability score from historical performance"""
        # Simplified reliability scoring
        base_reliability = {
            'uniswap': 0.95,
            'sushiswap': 0.85,
            'binance': 0.98,
            'coinbase': 0.97
        }
        
        return base_reliability.get(exchange, 0.8)
    
    async def _get_market_volatility(self, asset: str) -> float:
        """Get current market volatility for asset"""
        # Mock volatility values
        base_volatility = {
            'ETH': 0.25,
            'BTC': 0.20,
            'SOL': 0.35,
            'USDC': 0.01
        }
        
        # Extract base asset from pair
        base_asset = asset.split('/')[0] if '/' in asset else asset
        return base_volatility.get(base_asset, 0.2)
    
    def _update_performance_metrics(self, execution_result: ExecutionResult):
        """Update agent performance metrics"""
        
        self.performance_metrics['orders_executed'] += 1
        self.performance_metrics['total_volume'] += execution_result.fill_quantity
        
        # Update average slippage
        recent_slippages = [e.slippage for e in self.execution_history[-100:]]
        self.performance_metrics['avg_slippage'] = np.mean(recent_slippages) if recent_slippages else 0.0
        
        # Update success rate
        successful_executions = len([e for e in self.execution_history if e.status == OrderStatus.FILLED])
        total_executions = len(self.execution_history)
        self.performance_metrics['success_rate'] = successful_executions / total_executions if total_executions > 0 else 0.0
        
        # Update average execution time
        recent_times = [e.execution_time for e in self.execution_history[-100:]]
        if recent_times:
            total_seconds = sum(t.total_seconds() for t in recent_times)
            self.performance_metrics['avg_execution_time'] = timedelta(seconds=total_seconds / len(recent_times))
        
        # Update recent performance
        performance_score = (1 - execution_result.slippage) * (1 if execution_result.status == OrderStatus.FILLED else 0)
        self.performance_metrics['recent_performance'].append(performance_score)
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an active order"""
        
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order.status = OrderStatus.CANCELLED
            
            # Simulate cancellation
            await asyncio.sleep(0.02)
            
            # Remove from active orders
            del self.active_orders[order_id]
            
            print(f"Cancelled order {order_id}")
            return True
        
        return False
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and performance"""
        
        return {
            'agent_id': self.agent_id,
            'connected_exchanges': list(self.connected_exchanges.keys()),
            'active_orders': len(self.active_orders),
            'orders_executed': self.performance_metrics['orders_executed'],
            'success_rate': self.performance_metrics['success_rate'],
            'avg_slippage': self.performance_metrics['avg_slippage'],
            'avg_execution_time': self.performance_metrics['avg_execution_time'].total_seconds(),
            'total_volume': self.performance_metrics['total_volume']
        }

# Example usage
async def main():
    execution_agent = ExecutionAgent()
    
    # Connect to exchanges
    await execution_agent.connect_to_exchange("uniswap")
    await execution_agent.connect_to_exchange("sushiswap")
    await execution_agent.connect_to_exchange("binance")
    
    # Create and execute sample orders
    print("Creating sample orders...")
    
    # Market order
    market_order = await execution_agent.create_order(
        asset="ETH/USDC",
        quantity=10.0,  # 10 ETH
        order_type=OrderType.MARKET,
        side="buy",
        execution_strategy=ExecutionStrategy.AGGRESSIVE
    )
    
    # Limit order
    limit_order = await execution_agent.create_order(
        asset="BTC/USDC",
        quantity=1.0,   # 1 BTC
        order_type=OrderType.LIMIT,
        side="sell",
        price=30500.0,
        execution_strategy=ExecutionStrategy.PASSIVE
    )
    
    # TWAP order
    twap_order = await execution_agent.create_order(
        asset="SOL/USDC", 
        quantity=100.0,  # 100 SOL
        order_type=OrderType.TWAP,
        side="buy",
        execution_strategy=ExecutionStrategy.NEUTRAL
    )
    
    # Wait for executions to complete
    await asyncio.sleep(2)
    
    # Get agent status
    status = execution_agent.get_agent_status()
    print(f"\nExecution Agent Status: {status}")
    
    # Show recent executions
    recent_executions = execution_agent.execution_history[-3:]
    print(f"\nRecent Executions:")
    for exec_result in recent_executions:
        print(f"- {exec_result.order_id}: {exec_result.status.value} at {exec_result.fill_price} "
              f"(slippage: {exec_result.slippage:.4f})")

if __name__ == "__main__":
    asyncio.run(main())
