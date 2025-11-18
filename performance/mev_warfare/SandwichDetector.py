"""
AI-NEXUS SANDWICH DETECTOR
Advanced detection and protection against sandwich attacks
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict

@dataclass
class SandwichAttack:
    frontrun_tx: Dict
    victim_tx: Dict
    backrun_tx: Dict
    profit_estimated: float
    confidence: float
    block_number: int

class SandwichDetector:
    def __init__(self, config):
        self.config = config
        self.detected_attacks = []
        self.attack_patterns = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        
    async def analyze_mempool_batch(self, pending_transactions: List[Dict]) -> List[SandwichAttack]:
        """Analyze batch of pending transactions for sandwich attacks"""
        potential_attacks = []
        
        # Group transactions by target contract and function
        grouped_txs = self._group_transactions(pending_transactions)
        
        for contract, txs in grouped_txs.items():
            if len(txs) >= 3:  # Minimum for sandwich attack
                attacks = await self._detect_sandwich_pattern(contract, txs)
                potential_attacks.extend(attacks)
        
        # Filter by confidence threshold
        confirmed_attacks = [
            attack for attack in potential_attacks 
            if attack.confidence > self.config.get('confidence_threshold', 0.8)
        ]
        
        self.detected_attacks.extend(confirmed_attacks)
        return confirmed_attacks
    
    def _group_transactions(self, transactions: List[Dict]) -> Dict:
        """Group transactions by target contract and function"""
        grouped = defaultdict(list)
        
        for tx in transactions:
            if tx.get('to'):  # Contract interaction
                key = f"{tx['to']}_{tx.get('input', '')[:10]}"  # Contract + function selector
                grouped[key].append(tx)
        
        return grouped
    
    async def _detect_sandwich_pattern(self, contract: str, transactions: List[Dict]) -> List[SandwichAttack]:
        """Detect sandwich attack patterns in transaction group"""
        attacks = []
        
        # Sort by gas price (potential frontruns will have higher gas)
        sorted_txs = sorted(transactions, key=lambda x: x.get('gasPrice', 0), reverse=True)
        
        for i, victim_tx in enumerate(sorted_txs):
            # Look for potential frontrun and backrun transactions
            potential_frontruns = sorted_txs[:i]  # Transactions with higher gas price
            potential_backruns = sorted_txs[i+1:]  # Transactions with lower gas price
            
            for frontrun in potential_frontruns:
                for backrun in potential_backruns:
                    if await self._is_sandwich_trio(frontrun, victim_tx, backrun):
                        confidence = self._calculate_sandwich_confidence(frontrun, victim_tx, backrun)
                        profit = self._estimate_sandwich_profit(frontrun, victim_tx, backrun)
                        
                        attack = SandwichAttack(
                            frontrun_tx=frontrun,
                            victim_tx=victim_tx,
                            backrun_tx=backrun,
                            profit_estimated=profit,
                            confidence=confidence,
                            block_number=victim_tx.get('blockNumber', 0)
                        )
                        
                        attacks.append(attack)
                        self.logger.warning(
                            f"íº¨ Sandwich Attack Detected: "
                            f"Profit: {profit:.4f} ETH, Confidence: {confidence:.2f}"
                        )
        
        return attacks
    
    async def _is_sandwich_trio(self, frontrun: Dict, victim: Dict, backrun: Dict) -> bool:
        """Check if three transactions form a sandwich attack"""
        # Same target contract
        if frontrun.get('to') != victim.get('to') != backrun.get('to'):
            return False
        
        # Similar function calls
        if not self._is_similar_function(frontrun, victim, backrun):
            return False
        
        # Gas price ordering (frontrun > victim > backrun)
        if not (frontrun.get('gasPrice', 0) > victim.get('gasPrice', 0) > backrun.get('gasPrice', 0)):
            return False
        
        # Timing proximity (within same block)
        if not self._is_same_block_proximity(frontrun, victim, backrun):
            return False
        
        # Economic incentive check
        if not self._has_economic_incentive(frontrun, victim, backrun):
            return False
        
        return True
    
    def _is_similar_function(self, frontrun: Dict, victim: Dict, backrun: Dict) -> bool:
        """Check if transactions call similar functions"""
        frontrun_input = frontrun.get('input', '')
        victim_input = victim.get('input', '')
        backrun_input = backrun.get('input', '')
        
        # Check if function selectors match
        if frontrun_input[:10] != victim_input[:10] != backrun_input[:10]:
            return False
        
        return True
    
    def _is_same_block_proximity(self, frontrun: Dict, victim: Dict, backrun: Dict) -> bool:
        """Check if transactions are in close proximity"""
        # Implementation would check block numbers and positions
        # For mempool analysis, we assume they're pending for same block
        return True
    
    def _has_economic_incentive(self, frontrun: Dict, victim: Dict, backrun: Dict) -> bool:
        """Check if sandwich attack has economic incentive"""
        # Estimate profit from price impact
        victim_value = victim.get('value', 0) / 1e18  # Convert to ETH
        estimated_profit = victim_value * 0.01  # Assume 1% profit from sandwich
        
        return estimated_profit > 0.001  # Minimum profit threshold (0.001 ETH)
    
    def _calculate_sandwich_confidence(self, frontrun: Dict, victim: Dict, backrun: Dict) -> float:
        """Calculate confidence score for sandwich attack detection"""
        confidence_factors = []
        
        # Gas price differential
        gas_diff_ratio = (frontrun.get('gasPrice', 0) - backrun.get('gasPrice', 0)) / frontrun.get('gasPrice', 1)
        confidence_factors.append(min(gas_diff_ratio, 1.0))
        
        # Transaction value (higher value = more likely attack)
        victim_value = victim.get('value', 0) / 1e18
        value_confidence = min(victim_value / 10, 1.0)  # Cap at 10 ETH
        confidence_factors.append(value_confidence)
        
        # Sender patterns (known attackers)
        sender_confidence = self._check_sender_reputation(frontrun.get('from'), backrun.get('from'))
        confidence_factors.append(sender_confidence)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _check_sender_reputation(self, frontrun_sender: str, backrun_sender: str) -> float:
        """Check sender reputation for known attack patterns"""
        # Implementation would check against known attacker addresses
        known_attackers = set()  # Would be populated from threat intelligence
        
        if frontrun_sender in known_attackers or backrun_sender in known_attackers:
            return 1.0
        elif frontrun_sender == backrun_sender:  # Same attacker
            return 0.9
        else:
            return 0.5  # Neutral
    
    def _estimate_sandwich_profit(self, frontrun: Dict, victim: Dict, backrun: Dict) -> float:
        """Estimate profit from sandwich attack"""
        victim_value = victim.get('value', 0) / 1e18
        
        # Simple estimation: assume 0.5-2% profit from sandwich
        # In production, this would use more sophisticated models
        profit_percentage = 0.01  # 1% estimated profit
        
        estimated_profit = victim_value * profit_percentage
        
        # Subtract gas costs
        frontrun_gas = (frontrun.get('gas', 0) * frontrun.get('gasPrice', 0)) / 1e18
        backrun_gas = (backrun.get('gas', 0) * backrun.get('gasPrice', 0)) / 1e18
        
        net_profit = estimated_profit - frontrun_gas - backrun_gas
        
        return max(0, net_profit)
    
    async def protect_against_sandwich(self, our_transaction: Dict) -> Dict:
        """Apply sandwich attack protection to our transaction"""
        protected_tx = our_transaction.copy()
        
        # Strategy 1: Use private transactions (Flashbots)
        if self.config.get('use_private_tx', True):
            protected_tx['is_private'] = True
        
        # Strategy 2: Adjust gas price to avoid being victim
        current_gas = protected_tx.get('gasPrice', 0)
        protected_tx['gasPrice'] = int(current_gas * 1.2)  # 20% higher to avoid being sandwiched
        
        # Strategy 3: Add slippage protection
        if 'input' in protected_tx:
            protected_tx['input'] = self._add_slippage_protection(protected_tx['input'])
        
        # Strategy 4: Use transaction bundling
        protected_tx['use_bundling'] = True
        
        return protected_tx
    
    def _add_slippage_protection(self, input_data: str) -> str:
        """Add slippage protection to transaction input"""
        # Implementation would modify transaction parameters
        # to include maximum slippage limits
        return input_data
    
    def get_attack_statistics(self, time_window: int = 3600) -> Dict:
        """Get sandwich attack statistics"""
        current_time = asyncio.get_event_loop().time()
        recent_attacks = [
            attack for attack in self.detected_attacks
            if current_time - attack.block_number * 15 < time_window  # Approximate block time
        ]
        
        total_profit = sum(attack.profit_estimated for attack in recent_attacks)
        avg_confidence = sum(attack.confidence for attack in recent_attacks) / len(recent_attacks) if recent_attacks else 0
        
        return {
            'total_attacks_detected': len(recent_attacks),
            'total_protected_profit_eth': total_profit,
            'average_confidence': avg_confidence,
            'attacks_per_hour': len(recent_attacks) / (time_window / 3600),
            'most_targeted_contract': self._get_most_targeted_contract(recent_attacks)
        }
    
    def _get_most_targeted_contract(self, attacks: List[SandwichAttack]) -> str:
        """Get most frequently targeted contract"""
        if not attacks:
            return "None"
        
        contract_counts = defaultdict(int)
        for attack in attacks:
            contract = attack.victim_tx.get('to', 'unknown')
            contract_counts[contract] += 1
        
        return max(contract_counts.items(), key=lambda x: x[1])[0]
