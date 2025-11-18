"""
AI-NEXUS CROSS-CHAIN ATOMICITY
True atomic cross-chain arbitrage execution with failover management
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from web3 import Web3
from enum import Enum

class CrossChainStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"

@dataclass
class CrossChainOperation:
    operation_id: str
    chains: List[str]
    transactions: Dict[str, str]  # chain -> tx_hash
    status: CrossChainStatus
    start_time: float
    timeout: float
    rollback_triggered: bool = False

@dataclass
class AtomicArbitrage:
    opportunity_id: str
    source_chain: str
    target_chain: str
    expected_profit: float
    required_capital: float
    execution_path: List[Dict]
    timeout_blocks: int

class CrossChainAtomic:
    def __init__(self, config):
        self.config = config
        self.active_operations = {}
        self.chain_providers = {}  # chain -> Web3 provider
        self.bridge_managers = {}
        self.failover_manager = None
        self.htlc_manager = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize chain connections
        self._initialize_chain_connections()
    
    def _initialize_chain_connections(self):
        """Initialize connections to multiple chains"""
        chains = self.config.get('supported_chains', [])
        
        for chain in chains:
            try:
                provider_url = self.config['chain_configs'][chain]['rpc_url']
                self.chain_providers[chain] = Web3(Web3.HTTPProvider(provider_url))
                self.logger.info(f"Connected to {chain}")
            except Exception as e:
                self.logger.error(f"Failed to connect to {chain}: {e}")
    
    async def execute_atomic_arbitrage(self, arbitrage: AtomicArbitrage) -> CrossChainOperation:
        """Execute atomic cross-chain arbitrage"""
        operation_id = f"atomic_arb_{int(time.time())}_{arbitrage.opportunity_id}"
        
        operation = CrossChainOperation(
            operation_id=operation_id,
            chains=[arbitrage.source_chain, arbitrage.target_chain],
            transactions={},
            status=CrossChainStatus.PENDING,
            start_time=time.time(),
            timeout=time.time() + (arbitrage.timeout_blocks * 15)  # Assume 15s block time
        )
        
        self.active_operations[operation_id] = operation
        
        try:
            # Step 1: Lock capital on source chain
            source_tx_hash = await self._lock_source_capital(arbitrage, operation)
            operation.transactions[arbitrage.source_chain] = source_tx_hash
            
            # Step 2: Execute on target chain
            target_tx_hash = await self._execute_target_arbitrage(arbitrage, operation)
            operation.transactions[arbitrage.target_chain] = target_tx_hash
            
            # Step 3: Verify both transactions
            success = await self._verify_atomic_completion(operation)
            
            if success:
                operation.status = CrossChainStatus.COMPLETED
                self.logger.info(f"Atomic arbitrage completed: {operation_id}")
            else:
                operation.status = CrossChainStatus.FAILED
                await self._trigger_rollback(operation, arbitrage)
            
        except Exception as e:
            self.logger.error(f"Atomic arbitrage failed: {e}")
            operation.status = CrossChainStatus.FAILED
            await self._trigger_rollback(operation, arbitrage)
        
        return operation
    
    async def _lock_source_capital(self, arbitrage: AtomicArbitrage, 
                                 operation: CrossChainOperation) -> str:
        """Lock capital on source chain using HTLC"""
        source_chain = arbitrage.source_chain
        provider = self.chain_providers.get(source_chain)
        
        if not provider:
            raise Exception(f"No provider for chain: {source_chain}")
        
        try:
            # Create Hash Time Lock Contract (HTLC) transaction
            htlc_tx = await self._create_htlc_transaction(arbitrage, provider)
            
            # Send transaction
            signed_tx = provider.eth.account.sign_transaction(htlc_tx, 
                                                             private_key=self.config['private_key'])
            tx_hash = provider.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for confirmation
            receipt = await self._wait_for_transaction(tx_hash.hex(), source_chain)
            
            if receipt['status'] == 1:
                return tx_hash.hex()
            else:
                raise Exception("HTLC transaction failed")
                
        except Exception as e:
            self.logger.error(f"Source capital locking failed: {e}")
            raise
    
    async def _execute_target_arbitrage(self, arbitrage: AtomicArbitrage, 
                                      operation: CrossChainOperation) -> str:
        """Execute arbitrage on target chain"""
        target_chain = arbitrage.target_chain
        provider = self.chain_providers.get(target_chain)
        
        if not provider:
            raise Exception(f"No provider for chain: {target_chain}")
        
        try:
            # Verify source chain lock before proceeding
            source_verified = await self._verify_source_lock(arbitrage, operation)
            if not source_verified:
                raise Exception("Source chain lock verification failed")
            
            # Execute arbitrage on target chain
            arb_tx = await self._create_arbitrage_transaction(arbitrage, provider)
            
            signed_tx = provider.eth.account.sign_transaction(arb_tx, 
                                                             private_key=self.config['private_key'])
            tx_hash = provider.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for confirmation
            receipt = await self._wait_for_transaction(tx_hash.hex(), target_chain)
            
            if receipt['status'] == 1:
                return tx_hash.hex()
            else:
                raise Exception("Arbitrage transaction failed")
                
        except Exception as e:
            self.logger.error(f"Target arbitrage execution failed: {e}")
            raise
    
    async def _verify_source_lock(self, arbitrage: AtomicArbitrage, 
                                operation: CrossChainOperation) -> bool:
        """Verify that capital is locked on source chain"""
        source_chain = arbitrage.source_chain
        source_tx_hash = operation.transactions.get(source_chain)
        
        if not source_tx_hash:
            return False
        
        provider = self.chain_providers[source_chain]
        
        try:
            receipt = provider.eth.get_transaction_receipt(source_tx_hash)
            if receipt and receipt['status'] == 1:
                # Check HTLC contract state
                htlc_contract = self._get_htlc_contract(provider)
                lock_event = htlc_contract.events.LockCreated().process_receipt(receipt)
                return len(lock_event) > 0
        except Exception as e:
            self.logger.error(f"Source lock verification failed: {e}")
        
        return False
    
    async def _verify_atomic_completion(self, operation: CrossChainOperation) -> bool:
        """Verify that all chain operations completed successfully"""
        for chain, tx_hash in operation.transactions.items():
            provider = self.chain_providers.get(chain)
            if not provider:
                self.logger.error(f"No provider for chain: {chain}")
                return False
            
            try:
                receipt = provider.eth.get_transaction_receipt(tx_hash)
                if not receipt or receipt['status'] != 1:
                    self.logger.error(f"Transaction failed on {chain}: {tx_hash}")
                    return False
            except Exception as e:
                self.logger.error(f"Transaction verification failed on {chain}: {e}")
                return False
        
        return True
    
    async def _trigger_rollback(self, operation: CrossChainOperation, 
                              arbitrage: AtomicArbitrage):
        """Trigger rollback for failed atomic operation"""
        if operation.rollback_triggered:
            return
        
        operation.rollback_triggered = True
        operation.status = CrossChainStatus.ROLLBACK
        
        self.logger.info(f"Initiating rollback for operation: {operation.operation_id}")
        
        try:
            # Unlock capital on source chain
            source_chain = arbitrage.source_chain
            source_tx_hash = operation.transactions.get(source_chain)
            
            if source_tx_hash:
                await self._unlock_source_capital(arbitrage, operation)
            
            # Additional cleanup for target chain if needed
            target_chain = arbitrage.target_chain
            target_tx_hash = operation.transactions.get(target_chain)
            
            if target_tx_hash:
                await self._cleanup_target_chain(arbitrage, operation)
                
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
    
    async def _unlock_source_capital(self, arbitrage: AtomicArbitrage, 
                                   operation: CrossChainOperation):
        """Unlock capital on source chain after failure"""
        source_chain = arbitrage.source_chain
        provider = self.chain_providers[source_chain]
        
        try:
            htlc_contract = self._get_htlc_contract(provider)
            unlock_tx = htlc_contract.functions.refund().build_transaction({
                'from': self.config['wallet_address'],
                'gas': 100000,
                'gasPrice': provider.eth.gas_price
            })
            
            signed_tx = provider.eth.account.sign_transaction(unlock_tx, 
                                                             private_key=self.config['private_key'])
            tx_hash = provider.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = await self._wait_for_transaction(tx_hash.hex(), source_chain)
            if receipt['status'] == 1:
                self.logger.info(f"Capital unlocked on {source_chain}")
            else:
                self.logger.error(f"Capital unlock failed on {source_chain}")
                
        except Exception as e:
            self.logger.error(f"Capital unlock failed: {e}")
    
    async def _cleanup_target_chain(self, arbitrage: AtomicArbitrage, 
                                  operation: CrossChainOperation):
        """Clean up any partial state on target chain"""
        # Implementation depends on specific arbitrage logic
        pass
    
    async def _create_htlc_transaction(self, arbitrage: AtomicArbitrage, 
                                     provider: Web3) -> Dict:
        """Create HTLC transaction for capital locking"""
        htlc_contract = self._get_htlc_contract(provider)
        
        # Generate secret hash for atomic swap
        secret = self._generate_secret()
        secret_hash = Web3.keccak(text=secret)
        
        tx = htlc_contract.functions.lock(
            arbitrage.required_capital,
            secret_hash,
            arbitrage.timeout_blocks
        ).build_transaction({
            'from': self.config['wallet_address'],
            'value': arbitrage.required_capital,
            'gas': 200000,
            'gasPrice': provider.eth.gas_price
        })
        
        return tx
    
    async def _create_arbitrage_transaction(self, arbitrage: AtomicArbitrage, 
                                          provider: Web3) -> Dict:
        """Create arbitrage transaction for target chain"""
        # This would be implemented based on specific arbitrage strategy
        # Placeholder implementation
        
        arbitrage_contract = self._get_arbitrage_contract(provider)
        
        tx = arbitrage_contract.functions.executeArbitrage(
            arbitrage.execution_path
        ).build_transaction({
            'from': self.config['wallet_address'],
            'gas': 500000,
            'gasPrice': provider.eth.gas_price
        })
        
        return tx
    
    def _get_htlc_contract(self, provider: Web3):
        """Get HTLC contract instance"""
        # This would return actual HTLC contract
        # Placeholder implementation
        return None
    
    def _get_arbitrage_contract(self, provider: Web3):
        """Get arbitrage contract instance"""
        # This would return actual arbitrage contract
        # Placeholder implementation
        return None
    
    def _generate_secret(self) -> str:
        """Generate secret for HTLC"""
        import secrets
        return secrets.token_hex(32)
    
    async def _wait_for_transaction(self, tx_hash: str, chain: str, 
                                  timeout: int = 120) -> Dict:
        """Wait for transaction confirmation with timeout"""
        provider = self.chain_providers[chain]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                receipt = provider.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    return receipt
                await asyncio.sleep(3)
            except Exception as e:
                self.logger.error(f"Error waiting for transaction: {e}")
                await asyncio.sleep(3)
        
        raise Exception(f"Transaction timeout for {tx_hash} on {chain}")
    
    async def monitor_active_operations(self):
        """Monitor and manage active cross-chain operations"""
        while True:
            try:
                current_time = time.time()
                completed_operations = []
                
                for op_id, operation in self.active_operations.items():
                    # Check for timeouts
                    if current_time > operation.timeout and operation.status == CrossChainStatus.EXECUTING:
                        self.logger.warning(f"Operation timeout: {op_id}")
                        operation.status = CrossChainStatus.FAILED
                        await self._trigger_rollback(operation, None)  # Would need arbitrage context
                    
                    # Clean up completed operations
                    if operation.status in [CrossChainStatus.COMPLETED, CrossChainStatus.FAILED]:
                        if current_time > operation.timeout + 300:  # 5 minutes after completion
                            completed_operations.append(op_id)
                
                # Remove completed operations
                for op_id in completed_operations:
                    del self.active_operations[op_id]
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Operation monitoring error: {e}")
                await asyncio.sleep(10)
    
    def get_operation_status(self, operation_id: str) -> Optional[CrossChainOperation]:
        """Get status of specific operation"""
        return self.active_operations.get(operation_id)
    
    def get_active_operations(self) -> Dict[str, CrossChainOperation]:
        """Get all active operations"""
        return self.active_operations.copy()
    
    async def get_cross_chain_metrics(self) -> Dict:
        """Get cross-chain operation metrics"""
        total_operations = len(self.active_operations)
        completed = sum(1 for op in self.active_operations.values() 
                       if op.status == CrossChainStatus.COMPLETED)
        failed = sum(1 for op in self.active_operations.values() 
                    if op.status == CrossChainStatus.FAILED)
        
        success_rate = completed / total_operations if total_operations > 0 else 0
        
        return {
            'total_operations': total_operations,
            'completed_operations': completed,
            'failed_operations': failed,
            'success_rate': success_rate,
            'active_chains': list(self.chain_providers.keys()),
            'avg_execution_time': self._calculate_avg_execution_time()
        }
    
    def _calculate_avg_execution_time(self) -> float:
        """Calculate average execution time for completed operations"""
        completed_times = []
        
        for operation in self.active_operations.values():
            if operation.status == CrossChainStatus.COMPLETED:
                execution_time = operation.timeout - operation.start_time
                completed_times.append(execution_time)
        
        return sum(completed_times) / len(completed_times) if completed_times else 0
