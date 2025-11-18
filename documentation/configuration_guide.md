# Configuration Guide

## Wallet Setup

### Basic Wallet Registration

```python
from core_foundation.wallet_management import MultiWalletOrchestrator
from core_foundation.wallet_management import WalletRole

# Initialize the wallet orchestrator
orchestrator = MultiWalletOrchestrator()

# Register a hot trading wallet
await orchestrator.register_wallet(
    address="0x742d35Cc6634C0532925a3b8Dc9F1a...",
    role=WalletRole.HOT_TRADING,
    balance=10.0,
    currency="ETH",
    network="ethereum"
)

# Register a cold storage wallet
await orchestrator.register_wallet(
    address="0x89205A3A3b2A69De6Dbf7f01ED13B2...",
    role=WalletRole.COLD_STORAGE,
    balance=1000.0,
    currency="ETH", 
    network="ethereum",
    metadata={"hardware_wallet": True, "insured": True}
)