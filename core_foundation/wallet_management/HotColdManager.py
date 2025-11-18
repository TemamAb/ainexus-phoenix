"""
Advanced Hot/Cold Wallet Management System
Secure management of hot (online) and cold (offline) wallets with automated transfers
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hmac
import hashlib
from cryptography.fernet import Fernet
import secrets

class WalletType(Enum):
    HOT = "hot"
    COLD = "cold"
    WARM = "warm"  # Semi-cold for frequent but secure operations

class TransferPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Wallet:
    address: str
    wallet_type: WalletType
    balance: float
    currency: str
    security_level: int
    last_activity: datetime
    is_active: bool
    metadata: Dict

@dataclass
class TransferRequest:
    request_id: str
    from_wallet: str
    to_wallet: str
    amount: float
    currency: str
    priority: TransferPriority
    status: str
    created_at: datetime
    executed_at: Optional[datetime]
    tx_hash: Optional[str]
    security_checks: List[str]

class HotColdManager:
    """
    Advanced hot/cold wallet management with automated security protocols
    and optimal fund allocation
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.wallets: Dict[str, Wallet] = {}
        self.transfer_requests: Dict[str, TransferRequest] = {}
        self.security_policies = self._load_security_policies()
        self.transfer_limits = self._load_transfer_limits()
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        self._initialize_default_wallets()
    
    def _setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _load_security_policies(self) -> Dict:
        """Load security policies for different wallet types"""
        return {
            WalletType.HOT: {
                "max_balance": 10.0,  # Maximum balance in hot wallet (ETH)
                "auto_sweep_threshold": 5.0,
                "multi_sig_required": False,
                "cooling_period": timedelta(hours=1),
                "max_daily_transfers": 50
            },
            WalletType.COLD: {
                "max_balance": float('inf'),
                "auto_sweep_threshold": None,
                "multi_sig_required": True,
                "cooling_period": timedelta(days=7),
                "max_daily_transfers": 5
            },
            WalletType.WARM: {
                "max_balance": 50.0,
                "auto_sweep_threshold": 25.0,
                "multi_sig_required": True,
                "cooling_period": timedelta(hours=6),
                "max_daily_transfers": 20
            }
        }
    
    def _load_transfer_limits(self) -> Dict:
        """Load transfer limits based on priority and wallet type"""
        return {
            TransferPriority.LOW: {
                "max_amount": 1.0,
                "timeframe": timedelta(hours=6)
            },
            TransferPriority.NORMAL: {
                "max_amount": 5.0,
                "timeframe": timedelta(hours=2)
            },
            TransferPriority.HIGH: {
                "max_amount": 10.0,
                "timeframe": timedelta(minutes=30)
            },
            TransferPriority.URGENT: {
                "max_amount": 2.0,
                "timeframe": timedelta(minutes=5)
            }
        }
    
    def _initialize_default_wallets(self):
        """Initialize with some default wallet structures"""
        # Example hot wallet for immediate operations
        hot_wallet = Wallet(
            address="0xHotWallet123456789...",
            wallet_type=WalletType.HOT,
            balance=2.5,
            currency="ETH",
            security_level=1,
            last_activity=datetime.now(),
            is_active=True,
            metadata={"purpose": "immediate_trading", "auto_sweep": True}
        )
        
        # Example cold wallet for long-term storage
        cold_wallet = Wallet(
            address="0xColdWallet987654321...",
            wallet_type=WalletType.COLD,
            balance=1000.0,
            currency="ETH",
            security_level=5,
            last_activity=datetime.now() - timedelta(days=30),
            is_active=True,
            metadata={"purpose": "long_term_storage", "insurance_covered": True}
        )
        
        # Example warm wallet for frequent secure operations
        warm_wallet = Wallet(
            address="0xWarmWallet456789123...",
            wallet_type=WalletType.WARM,
            balance=25.0,
            currency="ETH",
            security_level=3,
            last_activity=datetime.now() - timedelta(hours=2),
            is_active=True,
            metadata={"purpose": "strategic_operations", "multi_sig": True}
        )
        
        self.wallets = {
            hot_wallet.address: hot_wallet,
            cold_wallet.address: cold_wallet,
            warm_wallet.address: warm_wallet
        }
    
    async def register_wallet(self, address: str, wallet_type: WalletType, 
                            initial_balance: float = 0, currency: str = "ETH",
                            metadata: Dict = None) -> Wallet:
        """Register a new wallet in the management system"""
        if address in self.wallets:
            raise ValueError(f"Wallet already registered: {address}")
        
        wallet = Wallet(
            address=address,
            wallet_type=wallet_type,
            balance=initial_balance,
            currency=currency,
            security_level=self._calculate_security_level(wallet_type),
            last_activity=datetime.now(),
            is_active=True,
            metadata=metadata or {}
        )
        
        self.wallets[address] = wallet
        
        self.logger.info(f"Registered {wallet_type.value} wallet: {address}")
        
        # Emit wallet registered event
        await self._emit_wallet_event("wallet_registered", wallet)
        
        return wallet
    
    def _calculate_security_level(self, wallet_type: WalletType) -> int:
        """Calculate security level based on wallet type"""
        security_levels = {
            WalletType.HOT: 1,
            WalletType.WARM: 3,
            WalletType.COLD: 5
        }
        return security_levels.get(wallet_type, 1)
    
    async def request_transfer(self, from_wallet: str, to_wallet: str, 
                             amount: float, currency: str,
                             priority: TransferPriority = TransferPriority.NORMAL) -> TransferRequest:
        """Request a transfer between wallets"""
        # Validate wallets exist
        if from_wallet not in self.wallets:
            raise ValueError(f"Source wallet not found: {from_wallet}")
        
        if to_wallet not in self.wallets:
            raise ValueError(f"Destination wallet not found: {to_wallet}")
        
        source_wallet = self.wallets[from_wallet]
        dest_wallet = self.wallets[to_wallet]
        
        # Validate transfer
        validation_result = await self._validate_transfer(
            source_wallet, dest_wallet, amount, currency, priority
        )
        
        if not validation_result["valid"]:
            raise ValueError(f"Transfer validation failed: {validation_result['reason']}")
        
        # Create transfer request
        request_id = self._generate_request_id()
        transfer_request = TransferRequest(
            request_id=request_id,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=amount,
            currency=currency,
            priority=priority,
            status="PENDING_APPROVAL",
            created_at=datetime.now(),
            executed_at=None,
            tx_hash=None,
            security_checks=[]
        )
        
        self.transfer_requests[request_id] = transfer_request
        
        self.logger.info(f"Transfer request created: {request_id} for {amount} {currency}")
        
        # Perform security checks
        await self._perform_security_checks(transfer_request)
        
        return transfer_request
    
    async def _validate_transfer(self, source_wallet: Wallet, dest_wallet: Wallet,
                               amount: float, currency: str, 
                               priority: TransferPriority) -> Dict:
        """Validate transfer request against security policies"""
        # Check currency match
        if source_wallet.currency != currency or dest_wallet.currency != currency:
            return {"valid": False, "reason": "Currency mismatch"}
        
        # Check sufficient balance
        if source_wallet.balance < amount:
            return {"valid": False, "reason": "Insufficient balance"}
        
        # Check wallet-specific limits
        source_policy = self.security_policies[source_wallet.wallet_type]
        if amount > source_policy["max_balance"]:
            return {"valid": False, "reason": "Amount exceeds wallet maximum"}
        
        # Check transfer limits
        limit_info = self.transfer_limits[priority]
        if amount > limit_info["max_amount"]:
            return {"valid": False, "reason": f"Amount exceeds {priority.value} limit"}
        
        # Check cooling period for cold wallets
        if source_wallet.wallet_type == WalletType.COLD:
            time_since_last_activity = datetime.now() - source_wallet.last_activity
            if time_since_last_activity < source_policy["cooling_period"]:
                return {"valid": False, "reason": "Cold wallet in cooling period"}
        
        # Check daily transfer limits
        daily_transfers = self._get_daily_transfer_count(source_wallet.address)
        if daily_transfers >= source_policy["max_daily_transfers"]:
            return {"valid": False, "reason": "Daily transfer limit exceeded"}
        
        return {"valid": True, "reason": "Validation passed"}
    
    async def _perform_security_checks(self, transfer_request: TransferRequest):
        """Perform security checks on transfer request"""
        checks = []
        
        # Multi-signature check
        if self._requires_multi_sig(transfer_request):
            checks.append("MULTI_SIG_REQUIRED")
        
        # Amount anomaly check
        if self._is_amount_anomalous(transfer_request):
            checks.append("AMOUNT_ANOMALY_DETECTED")
        
        # Pattern analysis
        pattern_check = await self._analyze_transfer_pattern(transfer_request)
        if pattern_check:
            checks.append(pattern_check)
        
        # Time-based checks
        time_check = self._check_transfer_timing(transfer_request)
        if time_check:
            checks.append(time_check)
        
        transfer_request.security_checks = checks
        
        # Update status based on checks
        if any("ANOMALY" in check for check in checks):
            transfer_request.status = "SECURITY_HOLD"
        elif "MULTI_SIG_REQUIRED" in checks:
            transfer_request.status = "AWAITING_APPROVAL"
        else:
            transfer_request.status = "APPROVED"
        
        self.logger.info(f"Security checks completed for {transfer_request.request_id}: {checks}")
    
    def _requires_multi_sig(self, transfer_request: TransferRequest) -> bool:
        """Check if multi-signature is required"""
        source_wallet = self.wallets[transfer_request.from_wallet]
        policy = self.security_policies[source_wallet.wallet_type]
        
        # Multi-sig required for cold wallets and large amounts
        return (policy["multi_sig_required"] or 
                transfer_request.amount > self.transfer_limits[TransferPriority.NORMAL]["max_amount"])
    
    def _is_amount_anomalous(self, transfer_request: TransferRequest) -> bool:
        """Check if transfer amount is anomalous"""
        source_wallet = self.wallets[transfer_request.from_wallet]
        
        # Simple anomaly detection - in production, use ML models
        typical_amount = source_wallet.balance * 0.1  # 10% of balance is typical
        return transfer_request.amount > typical_amount * 3  # 3x typical amount
    
    async def _analyze_transfer_pattern(self, transfer_request: TransferRequest) -> Optional[str]:
        """Analyze transfer patterns for suspicious activity"""
        # Simplified pattern analysis
        recent_transfers = self._get_recent_transfers(transfer_request.from_wallet, hours=24)
        
        if len(recent_transfers) > 10:
            return "HIGH_FREQUENCY_TRANSFERS"
        
        total_recent_amount = sum(t.amount for t in recent_transfers)
        if total_recent_amount + transfer_request.amount > self.wallets[transfer_request.from_wallet].balance * 0.5:
            return "LARGE_VOLUME_OUTFLOW"
        
        return None
    
    def _check_transfer_timing(self, transfer_request: TransferRequest) -> Optional[str]:
        """Check for unusual transfer timing"""
        hour = transfer_request.created_at.hour
        
        # Unusual hours (late night/early morning)
        if 1 <= hour <= 4:
            return "UNUSUAL_TIMING"
        
        return None
    
    async def execute_transfer(self, request_id: str, 
                             approval_signatures: List[str] = None) -> TransferRequest:
        """Execute an approved transfer request"""
        if request_id not in self.transfer_requests:
            raise ValueError(f"Transfer request not found: {request_id}")
        
        transfer_request = self.transfer_requests[request_id]
        
        if transfer_request.status != "APPROVED":
            raise ValueError(f"Transfer not approved. Current status: {transfer_request.status}")
        
        # Verify multi-signature if required
        if self._requires_multi_sig(transfer_request):
            if not approval_signatures or len(approval_signatures) < 2:
                raise ValueError("Multi-signature approval required")
            
            if not self._verify_signatures(transfer_request, approval_signatures):
                raise ValueError("Invalid approval signatures")
        
        # Update wallet balances
        source_wallet = self.wallets[transfer_request.from_wallet]
        dest_wallet = self.wallets[transfer_request.to_wallet]
        
        source_wallet.balance -= transfer_request.amount
        dest_wallet.balance += transfer_request.amount
        
        # Update activity timestamps
        source_wallet.last_activity = datetime.now()
        dest_wallet.last_activity = datetime.now()
        
        # Update transfer request
        transfer_request.status = "EXECUTED"
        transfer_request.executed_at = datetime.now()
        transfer_request.tx_hash = self._generate_tx_hash()
        
        self.logger.info(f"Transfer executed: {request_id} - {transfer_request.amount} {transfer_request.currency}")
        
        # Emit transfer event
        await self._emit_transfer_event("transfer_executed", transfer_request)
        
        # Check if auto-sweep is needed
        await self._check_auto_sweep(source_wallet)
        
        return transfer_request
    
    def _verify_signatures(self, transfer_request: TransferRequest, 
                          signatures: List[str]) -> bool:
        """Verify multi-signature approvals"""
        # Simplified signature verification
        # In production, this would use proper cryptographic verification
        expected_message = f"{transfer_request.request_id}{transfer_request.amount}{transfer_request.currency}"
        
        for signature in signatures:
            # Basic validation - real implementation would use proper crypto
            if len(signature) < 10:
                return False
        
        return True
    
    async def _check_auto_sweep(self, wallet: Wallet):
        """Check if auto-sweep is needed for wallet"""
        policy = self.security_policies[wallet.wallet_type]
        
        if (policy["auto_sweep_threshold"] and 
            wallet.balance > policy["auto_sweep_threshold"]):
            
            excess_amount = wallet.balance - policy["auto_sweep_threshold"]
            cold_wallet = self._find_appropriate_cold_wallet(wallet.currency)
            
            if cold_wallet:
                await self.request_transfer(
                    from_wallet=wallet.address,
                    to_wallet=cold_wallet.address,
                    amount=excess_amount,
                    currency=wallet.currency,
                    priority=TransferPriority.LOW
                )
                self.logger.info(f"Auto-sweep initiated: {excess_amount} {wallet.currency} to cold storage")
    
    def _find_appropriate_cold_wallet(self, currency: str) -> Optional[Wallet]:
        """Find appropriate cold wallet for currency"""
        for wallet in self.wallets.values():
            if (wallet.wallet_type == WalletType.COLD and 
                wallet.currency == currency and 
                wallet.is_active):
                return wallet
        return None
    
    async def get_wallet_health_report(self) -> Dict:
        """Generate comprehensive wallet health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_wallets": len(self.wallets),
            "wallets_by_type": {},
            "total_balances": {},
            "security_alerts": [],
            "recommendations": []
        }
        
        # Analyze wallets by type
        for wallet_type in WalletType:
            type_wallets = [w for w in self.wallets.values() if w.wallet_type == wallet_type]
            report["wallets_by_type"][wallet_type.value] = len(type_wallets)
            
            # Calculate total balance by currency for this type
            for wallet in type_wallets:
                if wallet.currency not in report["total_balances"]:
                    report["total_balances"][wallet.currency] = {}
                if wallet_type.value not in report["total_balances"][wallet.currency]:
                    report["total_balances"][wallet.currency][wallet_type.value] = 0
                report["total_balances"][wallet.currency][wallet_type.value] += wallet.balance
        
        # Generate security alerts
        report["security_alerts"] = await self._generate_security_alerts()
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    async def _generate_security_alerts(self) -> List[Dict]:
        """Generate security alerts based on current state"""
        alerts = []
        
        for wallet in self.wallets.values():
            policy = self.security_policies[wallet.wallet_type]
            
            # Check for over-limit hot wallets
            if (wallet.wallet_type == WalletType.HOT and 
                wallet.balance > policy["max_balance"]):
                alerts.append({
                    "level": "HIGH",
                    "wallet": wallet.address,
                    "message": f"Hot wallet exceeds maximum balance: {wallet.balance} {wallet.currency}",
                    "suggestion": "Initiate immediate sweep to cold storage"
                })
            
            # Check for inactive cold wallets
            if (wallet.wallet_type == WalletType.COLD and 
                datetime.now() - wallet.last_activity > timedelta(days=90)):
                alerts.append({
                    "level": "MEDIUM",
                    "wallet": wallet.address,
                    "message": "Cold wallet inactive for 90+ days",
                    "suggestion": "Verify wallet accessibility and backup"
                })
        
        return alerts
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Calculate overall hot wallet exposure
        hot_balance = sum(w.balance for w in self.wallets.values() 
                         if w.wallet_type == WalletType.HOT)
        total_balance = sum(w.balance for w in self.wallets.values())
        
        hot_exposure = hot_balance / total_balance if total_balance > 0 else 0
        
        if hot_exposure > 0.1:  # More than 10% in hot wallets
            recommendations.append("Reduce hot wallet exposure - move funds to warm/cold storage")
        
        # Check for currency diversification
        currencies = set(w.currency for w in self.wallets.values())
        if len(currencies) < 3:
            recommendations.append("Consider diversifying across more currencies")
        
        return recommendations
    
    # Utility methods
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"txreq_{secrets.token_hex(8)}"
    
    def _generate_tx_hash(self) -> str:
        """Generate simulated transaction hash"""
        return f"0x{secrets.token_hex(32)}"
    
    def _get_daily_transfer_count(self, wallet_address: str) -> int:
        """Get daily transfer count for wallet"""
        today = datetime.now().date()
        return len([
            t for t in self.transfer_requests.values()
            if t.from_wallet == wallet_address and 
            t.created_at.date() == today and
            t.status == "EXECUTED"
        ])
    
    def _get_recent_transfers(self, wallet_address: str, hours: int) -> List[TransferRequest]:
        """Get recent transfers for wallet"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            t for t in self.transfer_requests.values()
            if (t.from_wallet == wallet_address or t.to_wallet == wallet_address) and
            t.created_at >= cutoff and
            t.status == "EXECUTED"
        ]
    
    async def _emit_wallet_event(self, event_type: str, wallet: Wallet):
        """Emit wallet-related events"""
        # In production, this would integrate with event bus
        self.logger.info(f"Wallet event {event_type}: {wallet.address}")
    
    async def _emit_transfer_event(self, event_type: str, transfer: TransferRequest):
        """Emit transfer-related events"""
        # In production, this would integrate with event bus
        self.logger.info(f"Transfer event {event_type}: {transfer.request_id}")

# Example usage
async def main():
    """Demo the hot/cold wallet manager"""
    manager = HotColdManager()
    
    print("🔐 Hot/Cold Wallet Management System")
    print("=" * 50)
    
    # Register a new warm wallet
    new_wallet = await manager.register_wallet(
        address="0xNewWarmWallet999...",
        wallet_type=WalletType.WARM,
        initial_balance=15.0,
        currency="ETH",
        metadata={"purpose": "defi_operations", "yield_farming": True}
    )
    
    print(f"Registered new wallet: {new_wallet.address}")
    
    # Request a transfer
    transfer_request = await manager.request_transfer(
        from_wallet="0xHotWallet123456789...",
        to_wallet="0xNewWarmWallet999...",
        amount=1.5,
        currency="ETH",
        priority=TransferPriority.NORMAL
    )
    
    print(f"Transfer request created: {transfer_request.request_id}")
    print(f"Status: {transfer_request.status}")
    print(f"Security checks: {transfer_request.security_checks}")
    
    # Execute transfer (if approved)
    if transfer_request.status == "APPROVED":
        executed_transfer = await manager.execute_transfer(transfer_request.request_id)
        print(f"Transfer executed: {executed_transfer.tx_hash}")
    
    # Generate health report
    health_report = await manager.get_wallet_health_report()
    print(f"Total wallets: {health_report['total_wallets']}")
    print(f"Security alerts: {len(health_report['security_alerts'])}")
    print(f"Recommendations: {health_report['recommendations']}")

if __name__ == "__main__":
    asyncio.run(main())