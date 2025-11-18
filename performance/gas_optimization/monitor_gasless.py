"""
AI-NEXUS GASLESS TRANSACTION MONITOR
Monitoring and analytics for gasless transaction infrastructure
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
from web3 import Web3
import json

class GaslessTxStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"

class RelayService(Enum):
    GSN = "gsn"
    OPEN_GSN = "open_gsn"
    BICONOMY = "biconomy"
    GELATO = "gelato"
    CUSTOM = "custom"

@dataclass
class GaslessTransaction:
    tx_id: str
    user_address: str
    relay_service: RelayService
    status: GaslessTxStatus
    created_at: datetime
    submitted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    gas_used: Optional[int] = None
    gas_price: Optional[int] = None
    relayer_address: Optional[str] = None
    tx_hash: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class RelayServiceHealth:
    service: RelayService
    is_healthy: bool
    response_time: float
    success_rate: float
    last_check: datetime
    metrics: Dict[str, Any]

class GaslessTransactionMonitor:
    """Gasless transaction monitoring and analytics engine"""
    
    def __init__(self, config, web3_provider):
        self.config = config
        self.web3 = web3_provider
        self.logger = logging.getLogger(__name__)
        
        self.transactions = {}
        self.relay_services = {}
        self.health_metrics = {}
        
        self.initialize_relay_services()
    
    def initialize_relay_services(self):
        """Initialize relay service configurations"""
        services_config = self.config.get('relay_services', {})
        
        for service_name, service_config in services_config.items():
            service = RelayService(service_name)
            self.relay_services[service] = {
                'config': service_config,
                'health': RelayServiceHealth(
                    service=service,
                    is_healthy=True,
                    response_time=0.0,
                    success_rate=1.0,
                    last_check=datetime.now(),
                    metrics={}
                )
            }
    
    async def monitor_gasless_transaction(self, tx_data: Dict) -> GaslessTransaction:
        """Monitor gasless transaction from submission to confirmation"""
        tx_id = self.generate_tx_id()
        
        transaction = GaslessTransaction(
            tx_id=tx_id,
            user_address=tx_data['user_address'],
            relay_service=RelayService(tx_data['relay_service']),
            status=GaslessTxStatus.PENDING,
            created_at=datetime.now(),
            metadata=tx_data.get('metadata', {})
        )
        
        # Store transaction
        self.transactions[tx_id] = transaction
        
        self.logger.info(f"Monitoring gasless transaction: {tx_id}")
        
        # Start monitoring process
        asyncio.create_task(self.monitor_transaction_lifecycle(transaction))
        
        return transaction
    
    async def monitor_transaction_lifecycle(self, transaction: GaslessTransaction):
        """Monitor transaction through its entire lifecycle"""
        try:
            # Wait for submission
            await self.wait_for_submission(transaction)
            
            if transaction.status == GaslessTxStatus.SUBMITTED:
                # Wait for confirmation
                await self.wait_for_confirmation(transaction)
            
            # Update relay service metrics
            await self.update_relay_service_metrics(transaction)
            
            self.logger.info(f"Transaction {transaction.tx_id} completed with status: {transaction.status.value}")
            
        except Exception as e:
            transaction.status = GaslessTxStatus.FAILED
            transaction.error = str(e)
            self.logger.error(f"Transaction monitoring failed for {transaction.tx_id}: {e}")
    
    async def wait_for_submission(self, transaction: GaslessTransaction):
        """Wait for transaction to be submitted to blockchain"""
        max_wait_time = self.config.get('submission_timeout', 300)  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # Check if transaction has been submitted
            tx_status = await self.check_transaction_status(transaction)
            
            if tx_status == GaslessTxStatus.SUBMITTED:
                transaction.status = GaslessTxStatus.SUBMITTED
                transaction.submitted_at = datetime.now()
                return
            
            await asyncio.sleep(5)  # Check every 5 seconds
        
        # Timeout reached
        transaction.status = GaslessTxStatus.EXPIRED
        transaction.error = "Submission timeout exceeded"
    
    async def wait_for_confirmation(self, transaction: GaslessTransaction):
        """Wait for transaction confirmation"""
        max_wait_time = self.config.get('confirmation_timeout', 600)  # 10 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # Check if transaction is confirmed
            tx_status = await self.check_transaction_status(transaction)
            
            if tx_status == GaslessTxStatus.CONFIRMED:
                transaction.status = GaslessTxStatus.CONFIRMED
                transaction.confirmed_at = datetime.now()
                return
            
            if tx_status == GaslessTxStatus.FAILED:
                transaction.status = GaslessTxStatus.FAILED
                return
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        # Timeout reached
        transaction.status = GaslessTxStatus.FAILED
        transaction.error = "Confirmation timeout exceeded"
    
    async def check_transaction_status(self, transaction: GaslessTransaction) -> GaslessTxStatus:
        """Check current status of transaction"""
        try:
            # Implementation would query the specific relay service
            # Placeholder implementation
            if not transaction.tx_hash:
                # Simulate submission process
                if (datetime.now() - transaction.created_at).total_seconds() > 30:
                    transaction.tx_hash = f"0x{int(time.time()):x}"
                    transaction.relayer_address = "0xRelayer123"
                    return GaslessTxStatus.SUBMITTED
                else:
                    return GaslessTxStatus.PENDING
            
            else:
                # Simulate confirmation process
                if (datetime.now() - transaction.submitted_at).total_seconds() > 60:
                    transaction.gas_used = 21000
                    transaction.gas_price = Web3.to_wei(30, 'gwei')
                    return GaslessTxStatus.CONFIRMED
                else:
                    return GaslessTxStatus.SUBMITTED
        
        except Exception as e:
            self.logger.error(f"Status check failed for {transaction.tx_id}: {e}")
            return GaslessTxStatus.FAILED
    
    async def update_relay_service_metrics(self, transaction: GaslessTransaction):
        """Update metrics for relay service"""
        service = transaction.relay_service
        
        if service not in self.health_metrics:
            self.health_metrics[service] = {
                'total_transactions': 0,
                'successful_transactions': 0,
                'failed_transactions': 0,
                'total_gas_used': 0,
                'total_response_time': 0.0
            }
        
        metrics = self.health_metrics[service]
        metrics['total_transactions'] += 1
        
        if transaction.status == GaslessTxStatus.CONFIRMED:
            metrics['successful_transactions'] += 1
            if transaction.gas_used:
                metrics['total_gas_used'] += transaction.gas_used
            
            # Calculate response time
            if transaction.created_at and transaction.confirmed_at:
                response_time = (transaction.confirmed_at - transaction.created_at).total_seconds()
                metrics['total_response_time'] += response_time
        
        elif transaction.status == GaslessTxStatus.FAILED:
            metrics['failed_transactions'] += 1
    
    async def get_relay_service_health(self, service: RelayService) -> RelayServiceHealth:
        """Get health status for relay service"""
        if service not in self.relay_services:
            raise ValueError(f"Unknown relay service: {service}")
        
        service_data = self.relay_services[service]
        metrics = self.health_metrics.get(service, {})
        
        total_tx = metrics.get('total_transactions', 0)
        successful_tx = metrics.get('successful_transactions', 0)
        
        success_rate = successful_tx / total_tx if total_tx > 0 else 1.0
        avg_response_time = metrics.get('total_response_time', 0) / successful_tx if successful_tx > 0 else 0
        
        # Check current health
        is_healthy = await self.check_service_health(service)
        
        health = RelayServiceHealth(
            service=service,
            is_healthy=is_healthy,
            response_time=avg_response_time,
            success_rate=success_rate,
            last_check=datetime.now(),
            metrics=metrics
        )
        
        # Update service health
        service_data['health'] = health
        
        return health
    
    async def check_service_health(self, service: RelayService) -> bool:
        """Check current health of relay service"""
        try:
            service_config = self.relay_services[service]['config']
            
            # Implementation would check service endpoints
            # Placeholder implementation
            await asyncio.sleep(0.1)  # Simulate health check
            
            # Simulate occasional failures
            return True  # Always healthy for now
        
        except Exception as e:
            self.logger.error(f"Health check failed for {service.value}: {e}")
            return False
    
    async def get_transaction_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics for gasless transactions"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_tx = [tx for tx in self.transactions.values() if tx.created_at >= cutoff_time]
        
        total_transactions = len(recent_tx)
        successful_tx = len([tx for tx in recent_tx if tx.status == GaslessTxStatus.CONFIRMED])
        failed_tx = len([tx for tx in recent_tx if tx.status == GaslessTxStatus.FAILED])
        
        # Service breakdown
        service_breakdown = {}
        for service in RelayService:
            service_tx = [tx for tx in recent_tx if tx.relay_service == service]
            service_breakdown[service.value] = {
                'count': len(service_tx),
                'success_rate': len([tx for tx in service_tx if tx.status == GaslessTxStatus.CONFIRMED]) / len(service_tx) if service_tx else 0
            }
        
        # Gas usage analytics
        confirmed_tx = [tx for tx in recent_tx if tx.status == GaslessTxStatus.CONFIRMED and tx.gas_used]
        total_gas_used = sum(tx.gas_used for tx in confirmed_tx)
        avg_gas_used = total_gas_used / len(confirmed_tx) if confirmed_tx else 0
        
        # Response time analytics
        response_times = []
        for tx in confirmed_tx:
            if tx.created_at and tx.confirmed_at:
                response_time = (tx.confirmed_at - tx.created_at).total_seconds()
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'timeframe_hours': hours,
            'total_transactions': total_transactions,
            'successful_transactions': successful_tx,
            'failed_transactions': failed_tx,
            'success_rate': successful_tx / total_transactions if total_transactions > 0 else 0,
            'service_breakdown': service_breakdown,
            'gas_usage': {
                'total_gas_used': total_gas_used,
                'average_gas_used': avg_gas_used,
                'gas_savings': await self.calculate_gas_savings(recent_tx)
            },
            'performance': {
                'average_response_time': avg_response_time,
                'min_response_time': min(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0
            }
        }
    
    async def calculate_gas_savings(self, transactions: List[GaslessTransaction]) -> Dict[str, Any]:
        """Calculate gas savings from gasless transactions"""
        confirmed_tx = [tx for tx in transactions if tx.status == GaslessTxStatus.CONFIRMED]
        
        if not confirmed_tx:
            return {'total_eth_saved': 0, 'total_usd_saved': 0}
        
        # Calculate gas costs if users paid
        total_gas_cost_eth = 0
        for tx in confirmed_tx:
            if tx.gas_used and tx.gas_price:
                gas_cost = tx.gas_used * tx.gas_price
                total_gas_cost_eth += Web3.from_wei(gas_cost, 'ether')
        
        # Assume relay services charge 10% of gas costs
        relay_service_cost_eth = total_gas_cost_eth * 0.10
        user_savings_eth = total_gas_cost_eth - relay_service_cost_eth
        
        # Convert to USD (placeholder rate)
        eth_usd_rate = 2000  # $2000 per ETH
        user_savings_usd = user_savings_eth * eth_usd_rate
        
        return {
            'total_eth_saved': user_savings_eth,
            'total_usd_saved': user_savings_usd,
            'transactions_analyzed': len(confirmed_tx)
        }
    
    async def get_service_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for relay service optimization"""
        recommendations = []
        
        for service in RelayService:
            health = await self.get_relay_service_health(service)
            analytics = await self.get_transaction_analytics()
            service_analytics = analytics['service_breakdown'].get(service.value, {})
            
            if not health.is_healthy:
                recommendations.append({
                    'service': service.value,
                    'type': 'HEALTH',
                    'priority': 'HIGH',
                    'message': f'Relay service {service.value} is unhealthy',
                    'suggestion': 'Investigate service connectivity and consider failover'
                })
            
            if service_analytics.get('success_rate', 1.0) < 0.9:
                recommendations.append({
                    'service': service.value,
                    'type': 'RELIABILITY',
                    'priority': 'MEDIUM',
                    'message': f'Low success rate for {service.value}: {service_analytics["success_rate"]:.1%}',
                    'suggestion': 'Review transaction patterns and service configuration'
                })
        
        # Overall recommendations
        analytics = await self.get_transaction_analytics()
        if analytics['success_rate'] < 0.95:
            recommendations.append({
                'service': 'all',
                'type': 'OVERALL_RELIABILITY',
                'priority': 'MEDIUM',
                'message': f'Overall success rate below target: {analytics["success_rate"]:.1%}',
                'suggestion': 'Implement additional failover mechanisms and monitoring'
            })
        
        return recommendations
    
    def generate_tx_id(self) -> str:
        """Generate unique transaction ID"""
        timestamp = int(time.time())
        random_suffix = str(timestamp)[-6:]
        return f"GASLESS-{timestamp}-{random_suffix}"
    
    async def get_transaction(self, tx_id: str) -> Optional[GaslessTransaction]:
        """Get transaction by ID"""
        return self.transactions.get(tx_id)
    
    async def search_transactions(self, user_address: Optional[str] = None,
                                service: Optional[RelayService] = None,
                                status: Optional[GaslessTxStatus] = None,
                                hours: int = 24) -> List[GaslessTransaction]:
        """Search transactions by criteria"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        transactions = [tx for tx in self.transactions.values() if tx.created_at >= cutoff_time]
        
        if user_address:
            transactions = [tx for tx in transactions if tx.user_address.lower() == user_address.lower()]
        
        if service:
            transactions = [tx for tx in transactions if tx.relay_service == service]
        
        if status:
            transactions = [tx for tx in transactions if tx.status == status]
        
        return sorted(transactions, key=lambda x: x.created_at, reverse=True)

# Example usage
if __name__ == "__main__":
    # Mock web3 provider for example
    class MockWeb3:
        @staticmethod
        def to_wei(value, unit):
            return int(value * 1e9)  # Simple conversion for example
    
    web3 = MockWeb3()
    
    monitor = GaslessTransactionMonitor({
        'relay_services': {
            'biconomy': {'endpoint': 'https://api.biconomy.io'},
            'gelato': {'endpoint': 'https://relay.gelato.digital'}
        },
        'submission_timeout': 300,
        'confirmation_timeout': 600
    }, web3)
    
    async def example():
        # Monitor a gasless transaction
        tx_data = {
            'user_address': '0xUser123456789',
            'relay_service': 'biconomy',
            'metadata': {
                'contract_address': '0xContract123',
                'function_name': 'transfer',
                'parameters': {'to': '0xRecipient', 'value': 1000}
            }
        }
        
        transaction = await monitor.monitor_gasless_transaction(tx_data)
        print(f"Monitoring transaction: {transaction.tx_id}")
        
        # Wait a bit for monitoring
        await asyncio.sleep(2)
        
        # Get transaction status
        tx_status = await monitor.get_transaction(transaction.tx_id)
        print(f"Transaction status: {tx_status.status.value}")
        
        # Get analytics
        analytics = await monitor.get_transaction_analytics()
        print(f"Total transactions (24h): {analytics['total_transactions']}")
        print(f"Success rate: {analytics['success_rate']:.1%}")
        
        # Get recommendations
        recommendations = await monitor.get_service_recommendations()
        for rec in recommendations:
            print(f"Recommendation: {rec['message']}")
    
    asyncio.run(example())
