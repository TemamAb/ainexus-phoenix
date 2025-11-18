#!/usr/bin/env python3
"""
AI-NEXUS Main Application Entry Point
Enterprise-grade arbitrage system orchestrator
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Gauge, Histogram

# Metrics
ARBITRAGE_ATTEMPTS = Counter('arbitrage_attempts_total', 'Total arbitrage attempts')
ARBITRAGE_SUCCESS = Counter('arbitrage_success_total', 'Successful arbitrage executions')
ARBITRAGE_PROFIT = Histogram('arbitrage_profit_usd', 'Arbitrage profit distribution')
ACTIVE_STRATEGIES = Gauge('active_strategies', 'Number of active strategies')

# Core system components
from core.ai_intelligence import AIIntelligenceEngine
from execution.arbitrage_engine import ArbitrageEngine
from risk.risk_manager import RiskManager
from data.market_data import MarketDataFeed

class AINexusApplication:
    """Main AI-NEXUS application orchestrator"""
    
    def __init__(self):
        self.is_running = False
        self.components = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Configure application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ai-nexus.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize all system components"""
        self.logger.info("Initializing AI-NEXUS application...")
        
        try:
            # Initialize core components
            self.components['ai_engine'] = AIIntelligenceEngine()
            self.components['arbitrage_engine'] = ArbitrageEngine()
            self.components['risk_manager'] = RiskManager()
            self.components['market_data'] = MarketDataFeed()
            
            # Initialize components
            for name, component in self.components.items():
                if hasattr(component, 'initialize'):
                    await component.initialize()
                self.logger.info(f"Initialized {name}")
            
            self.is_running = True
            self.logger.info("AI-NEXUS application initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            raise
    
    async def start(self):
        """Start the main application loop"""
        self.logger.info("Starting AI-NEXUS main loop...")
        
        while self.is_running:
            try:
                # Main arbitrage cycle
                await self.run_arbitrage_cycle()
                
                # Health check and monitoring
                await self.perform_health_checks()
                
                # Brief pause between cycles
                await asyncio.sleep(0.1)  # 100ms between cycles
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Longer pause on error
    
    async def run_arbitrage_cycle(self):
        """Execute single arbitrage cycle"""
        try:
            # Get market data
            market_data = await self.components['market_data'].get_latest()
            
            # Analyze opportunities with AI
            opportunities = await self.components['ai_engine'].analyze_opportunities(market_data)
            
            # Filter by risk
            approved_opportunities = await self.components['risk_manager'].evaluate_opportunities(opportunities)
            
            # Execute arbitrage
            for opportunity in approved_opportunities:
                ARBITRAGE_ATTEMPTS.inc()
                
                result = await self.components['arbitrage_engine'].execute_arbitrage(opportunity)
                
                if result['success']:
                    ARBITRAGE_SUCCESS.inc()
                    ARBITRAGE_PROFIT.observe(result['profit'])
                    self.logger.info(f"Arbitrage executed: ${result['profit']:.2f} profit")
                else:
                    self.logger.warning(f"Arbitrage failed: {result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            self.logger.error(f"Arbitrage cycle error: {e}")
    
    async def perform_health_checks(self):
        """Perform system health checks"""
        for name, component in self.components.items():
            if hasattr(component, 'health_check'):
                health = await component.health_check()
                if not health.get('healthy', True):
                    self.logger.warning(f"Component {name} health check failed: {health}")
    
    async def shutdown(self):
        """Graceful application shutdown"""
        self.logger.info("Shutting down AI-NEXUS application...")
        self.is_running = False
        
        # Shutdown components in reverse order
        for name, component in reversed(self.components.items()):
            if hasattr(component, 'shutdown'):
                await component.shutdown()
            self.logger.info(f"Shutdown {name}")
        
        self.logger.info("AI-NEXUS application shutdown complete")

# FastAPI Application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    application = AINexusApplication()
    await application.initialize()
    app.state.application = application
    
    # Start main loop in background
    asyncio.create_task(application.start())
    
    yield
    
    # Shutdown
    await application.shutdown()

# Create FastAPI app
app = FastAPI(
    title="AI-NEXUS Arbitrage System",
    description="Enterprise-grade DeFi arbitrage trading system",
    version="5.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# API Routes
@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "status": "operational",
        "system": "AI-NEXUS Arbitrage Engine",
        "version": "5.0.0",
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    app_state = app.state.application
    
    health_status = {
        "status": "healthy",
        "components": {},
        "timestamp": asyncio.get_event_loop().time()
    }
    
    # Check component health
    for name, component in app_state.components.items():
        if hasattr(component, 'health_check'):
            try:
                component_health = await component.health_check()
                health_status["components"][name] = component_health
                
                if not component_health.get('healthy', True):
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"][name] = {"healthy": False, "error": str(e)}
                health_status["status"] = "unhealthy"
    
    return health_status

@app.get("/performance")
async def performance_metrics():
    """Get performance metrics"""
    return {
        "arbitrage_attempts": ARBITRAGE_ATTEMPTS._value.get(),
        "arbitrage_success": ARBITRAGE_SUCCESS._value.get(),
        "active_strategies": ACTIVE_STRATEGIES._value.get(),
        "timestamp": asyncio.get_event_loop().time()
    }

@app.post("/strategies/{strategy_id}/enable")
async def enable_strategy(strategy_id: str):
    """Enable specific arbitrage strategy"""
    # Implementation would enable specific strategy
    return {"status": "enabled", "strategy_id": strategy_id}

@app.post("/strategies/{strategy_id}/disable")
async def disable_strategy(strategy_id: str):
    """Disable specific arbitrage strategy"""
    # Implementation would disable specific strategy
    return {"status": "disabled", "strategy_id": strategy_id}

@app.get("/opportunities")
async def get_opportunities():
    """Get current arbitrage opportunities"""
    app_state = app.state.application
    opportunities = await app_state.components['ai_engine'].get_current_opportunities()
    return {"opportunities": opportunities}

# Signal handlers for graceful shutdown
def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logging.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(app.state.application.shutdown())

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        log_level="info"
    )
