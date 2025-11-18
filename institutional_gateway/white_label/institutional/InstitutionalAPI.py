#!/usr/bin/env python3
"""
AI-NEXUS Institutional Gateway API
Enterprise-grade API for institutional clients and partners
"""

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import jwt
import hashlib
import uuid

# Security schemas
security = HTTPBearer()

# Pydantic models for API
class InstitutionalClient(BaseModel):
    client_id: str
    name: str
    tier: str  # enterprise, premium, basic
    permissions: List[str]
    rate_limit: int
    webhook_url: Optional[str]
    
class APIKeyRequest(BaseModel):
    client_name: str
    contact_email: str
    tier: str
    required_permissions: List[str]
    
class TradeExecutionRequest(BaseModel):
    strategy_id: str
    asset_pair: str
    amount: float
    execution_type: str  # immediate, twap, vwap
    max_slippage: Optional[float] = 0.01
    urgency: Optional[str] = "normal"
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 1000000:  # $1M limit per trade
            raise ValueError('Amount exceeds maximum trade size')
        return v
    
class PortfolioAllocationRequest(BaseModel):
    allocations: Dict[str, float]  # asset -> percentage
    
    @validator('allocations')
    def validate_allocations(cls, v):
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:  # Allow 1% tolerance
            raise ValueError('Allocations must sum to 100%')
        return v

class InstitutionalAPI:
    """Institutional Gateway API implementation"""
    
    def __init__(self):
        self.app = FastAPI(
            title="AI-NEXUS Institutional API",
            description="Enterprise-grade arbitrage trading API for institutional clients",
            version="2.0.0",
            docs_url="/institutional/docs",
            redoc_url="/institutional/redoc"
        )
        
        self.setup_middleware()
        self.setup_routes()
        self.clients = {}  # In production, this would be a database
        self.api_keys = {}  # API key storage
        
    def setup_middleware(self):
        """Setup API middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://partner.ainexus.com", "https://clientportal.ainexus.com"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.post("/institutional/api-keys/request")
        async def request_api_key(request: APIKeyRequest, 
                                credentials: HTTPAuthorizationCredentials = Security(security)):
            """Request new API key for institutional client"""
            await self.verify_admin_credentials(credentials)
            
            client_id = str(uuid.uuid4())
            api_key = self.generate_api_key(client_id)
            
            client = InstitutionalClient(
                client_id=client_id,
                name=request.client_name,
                tier=request.tier,
                permissions=request.required_permissions,
                rate_limit=self.get_rate_limit(request.tier),
                webhook_url=None
            )
            
            self.clients[client_id] = client
            self.api_keys[api_key] = client_id
            
            return {
                "client_id": client_id,
                "api_key": api_key,
                "rate_limit": client.rate_limit,
                "permissions": client.permissions
            }
        
        @self.app.get("/institutional/strategies")
        async def get_available_strategies(credentials: HTTPAuthorizationCredentials = Security(security)):
            """Get available arbitrage strategies"""
            client = await self.verify_client_credentials(credentials)
            
            strategies = await self.get_strategies_for_tier(client.tier)
            return {"strategies": strategies}
        
        @self.app.post("/institutional/execute-trade")
        async def execute_trade(request: TradeExecutionRequest,
                              credentials: HTTPAuthorizationCredentials = Security(security)):
            """Execute trade through institutional gateway"""
            client = await self.verify_client_credentials(credentials)
            
            # Check permissions
            if "trade_execution" not in client.permissions:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Execute trade
            execution_result = await self.execute_institutional_trade(client, request)
            
            return execution_result
        
        @self.app.get("/institutional/portfolio")
        async def get_portfolio(credentials: HTTPAuthorizationCredentials = Security(security)):
            """Get client portfolio overview"""
            client = await self.verify_client_credentials(credentials)
            
            portfolio = await self.get_client_portfolio(client.client_id)
            return portfolio
        
        @self.app.post("/institutional/portfolio/allocate")
        async def allocate_portfolio(request: PortfolioAllocationRequest,
                                   credentials: HTTPAuthorizationCredentials = Security(security)):
            """Set portfolio allocation strategy"""
            client = await self.verify_client_credentials(credentials)
            
            allocation_result = await self.set_portfolio_allocation(client.client_id, request.allocations)
            return allocation_result
        
        @self.app.get("/institutional/performance")
        async def get_performance(timeframe: str = "30d",
                                credentials: HTTPAuthorizationCredentials = Security(security)):
            """Get performance metrics"""
            client = await self.verify_client_credentials(credentials)
            
            performance = await self.get_client_performance(client.client_id, timeframe)
            return performance
        
        @self.app.post("/institutional/webhooks")
        async def set_webhook(webhook_url: str,
                            credentials: HTTPAuthorizationCredentials = Security(security)):
            """Set webhook for real-time notifications"""
            client = await self.verify_client_credentials(credentials)
            
            self.clients[client.client_id].webhook_url = webhook_url
            return {"status": "webhook_configured"}
    
    async def verify_admin_credentials(self, credentials: HTTPAuthorizationCredentials):
        """Verify admin-level credentials"""
        # In production, this would verify against a proper auth system
        if credentials.credentials != "admin-secret-key":
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    async def verify_client_credentials(self, credentials: HTTPAuthorizationCredentials):
        """Verify client API credentials"""
        api_key = credentials.credentials
        client_id = self.api_keys.get(api_key)
        
        if not client_id:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        client = self.clients.get(client_id)
        if not client:
            raise HTTPException(status_code=401, detail="Client not found")
        
        return client
    
    def generate_api_key(self, client_id: str) -> str:
        """Generate secure API key"""
        secret = "institutional-secret-salt"  # In production, use proper secret
        raw_key = f"{client_id}:{secret}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def get_rate_limit(self, tier: str) -> int:
        """Get rate limit based on client tier"""
        limits = {
            "enterprise": 1000,  # 1000 requests per minute
            "premium": 500,
            "basic": 100
        }
        return limits.get(tier, 100)
    
    async def get_strategies_for_tier(self, tier: str) -> List[Dict]:
        """Get available strategies for client tier"""
        base_strategies = [
            {
                "id": "triangular_arb",
                "name": "Triangular Arbitrage",
                "description": "Cross-exchange triangular arbitrage",
                "risk_level": "medium",
                "min_capital": 1000
            },
            {
                "id": "flash_loan_arb",
                "name": "Flash Loan Arbitrage", 
                "description": "Capital-efficient flash loan arbitrage",
                "risk_level": "high",
                "min_capital": 5000
            }
        ]
        
        if tier == "enterprise":
            base_strategies.extend([
                {
                    "id": "cross_chain_arb",
                    "name": "Cross-Chain Arbitrage",
                    "description": "Atomic cross-chain arbitrage",
                    "risk_level": "high", 
                    "min_capital": 10000
                },
                {
                    "id": "institutional_flow",
                    "name": "Institutional Flow Trading",
                    "description": "Trade based on institutional order flow",
                    "risk_level": "medium",
                    "min_capital": 50000
                }
            ])
        
        return base_strategies
    
    async def execute_institutional_trade(self, client: InstitutionalClient, 
                                        request: TradeExecutionRequest) -> Dict:
        """Execute institutional trade"""
        # Verify strategy access
        if not await self.client_has_strategy_access(client.client_id, request.strategy_id):
            raise HTTPException(status_code=403, detail="Strategy access denied")
        
        # Execute through institutional execution engine
        from execution.institutional_executor import InstitutionalExecutor
        
        executor = InstitutionalExecutor()
        execution_result = await executor.execute_trade(
            client_id=client.client_id,
            strategy_id=request.strategy_id,
            asset_pair=request.asset_pair,
            amount=request.amount,
            execution_type=request.execution_type,
            max_slippage=request.max_slippage,
            urgency=request.urgency
        )
        
        # Send webhook notification if configured
        if client.webhook_url:
            await self.send_webhook_notification(client.webhook_url, execution_result)
        
        return execution_result
    
    async def client_has_strategy_access(self, client_id: str, strategy_id: str) -> bool:
        """Check if client has access to specific strategy"""
        # In production, this would check against client permissions
        # For now, all enterprise clients have access to all strategies
        client = self.clients.get(client_id)
        return client and client.tier == "enterprise"
    
    async def get_client_portfolio(self, client_id: str) -> Dict:
        """Get client portfolio data"""
        # This would fetch from portfolio management system
        return {
            "total_value": 1000000.0,
            "cash_balance": 150000.0,
            "positions": [
                {"asset": "BTC", "quantity": 5.0, "value": 150000.0},
                {"asset": "ETH", "quantity": 100.0, "value": 180000.0},
                {"asset": "USDC", "quantity": 500000.0, "value": 500000.0}
            ],
            "performance": {
                "daily_return": 0.0025,
                "weekly_return": 0.015,
                "monthly_return": 0.045
            }
        }
    
    async def set_portfolio_allocation(self, client_id: str, allocations: Dict[str, float]) -> Dict:
        """Set portfolio allocation strategy"""
        # This would update portfolio management system
        from portfolio.allocation_engine import AllocationEngine
        
        engine = AllocationEngine()
        result = await engine.set_client_allocation(client_id, allocations)
        
        return {
            "status": "allocation_updated",
            "target_allocations": allocations,
            "rebalancing_required": result.get('rebalancing_required', False)
        }
    
    async def get_client_performance(self, client_id: str, timeframe: str) -> Dict:
        """Get client performance metrics"""
        # This would fetch from performance tracking system
        return {
            "timeframe": timeframe,
            "total_return": 0.1245,
            "sharpe_ratio": 1.85,
            "max_drawdown": 0.045,
            "volatility": 0.125,
            "success_rate": 0.78,
            "total_trades": 245,
            "profitable_trades": 191
        }
    
    async def send_webhook_notification(self, webhook_url: str, data: Dict):
        """Send webhook notification to client"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=data) as response:
                    if response.status == 200:
                        print(f"Webhook notification sent successfully to {webhook_url}")
                    else:
                        print(f"Webhook notification failed: {response.status}")
        except Exception as e:
            print(f"Webhook error: {e}")

# Institutional Executor
class InstitutionalExecutor:
    """Institutional trade execution engine"""
    
    async def execute_trade(self, client_id: str, strategy_id: str, asset_pair: str,
                          amount: float, execution_type: str, max_slippage: float, 
                          urgency: str) -> Dict:
        """Execute institutional trade"""
        
        # Get best execution venue
        venue = await self.select_execution_venue(asset_pair, amount, execution_type)
        
        # Calculate expected slippage
        slippage_prediction = await self.predict_slippage(asset_pair, amount, execution_type)
        
        # Execute trade
        execution_details = await self.execute_on_venue(
            venue, asset_pair, amount, execution_type, max_slippage
        )
        
        return {
            "execution_id": str(uuid.uuid4()),
            "client_id": client_id,
            "strategy_id": strategy_id,
            "asset_pair": asset_pair,
            "amount": amount,
            "execution_type": execution_type,
            "venue": venue,
            "executed_price": execution_details['price'],
            "slippage": execution_details['slippage'],
            "fees": execution_details['fees'],
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def select_execution_venue(self, asset_pair: str, amount: float, 
                                   execution_type: str) -> str:
        """Select optimal execution venue"""
        # This would use smart order routing
        venues = await self.get_available_venues(asset_pair)
        
        # Score venues based on liquidity, fees, and execution quality
        venue_scores = {}
        for venue in venues:
            score = await self.score_venue(venue, asset_pair, amount, execution_type)
            venue_scores[venue] = score
        
        return max(venue_scores, key=venue_scores.get)
    
    async def get_available_venues(self, asset_pair: str) -> List[str]:
        """Get available trading venues for asset pair"""
        # This would query venue connectivity
        return ["binance_institutional", "coinbase_prime", "kraken_pro"]
    
    async def score_venue(self, venue: str, asset_pair: str, amount: float, 
                         execution_type: str) -> float:
        """Score venue for execution quality"""
        # This would consider liquidity, fees, latency, etc.
        base_score = 0.8  # Base score
        
        # Adjust for venue-specific factors
        if venue == "binance_institutional":
            base_score += 0.1  # High liquidity bonus
        
        return base_score
    
    async def predict_slippage(self, asset_pair: str, amount: float, 
                             execution_type: str) -> float:
        """Predict execution slippage"""
        # This would use sophisticated slippage models
        base_slippage = 0.001  # 0.1% base
        
        # Adjust for trade size and market conditions
        if amount > 50000:
            base_slippage *= 2  # Higher slippage for large trades
        
        return base_slippage
    
    async def execute_on_venue(self, venue: str, asset_pair: str, amount: float,
                             execution_type: str, max_slippage: float) -> Dict:
        """Execute trade on specific venue"""
        # This would use venue-specific API
        # Mock execution for demonstration
        return {
            "price": 1800.50,  # Executed price
            "slippage": 0.0005,  # 0.05% slippage
            "fees": amount * 0.001,  # 0.1% fees
            "venue_order_id": f"{venue}_order_{uuid.uuid4()}"
        }

# Run the API
if __name__ == "__main__":
    import uvicorn
    
    api = InstitutionalAPI()
    
    uvicorn.run(
        api.app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
