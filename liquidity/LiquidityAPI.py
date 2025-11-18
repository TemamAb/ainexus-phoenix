"""
AI-NEXUS LIQUIDITY API
Enterprise-grade API for private liquidity access and management
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from aiohttp import web
import json
import logging
from datetime import datetime, timedelta
import hmac
import hashlib
import jwt
from cryptography.fernet import Fernet

class APIErrorCode(Enum):
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    RATE_LIMITED = 429
    INTERNAL_ERROR = 500

@dataclass
class APIResponse:
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    code: APIErrorCode = APIErrorCode.SUCCESS
    metadata: Optional[Dict] = None

@dataclass
class RateLimit:
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int

@dataclass
class APIClient:
    client_id: str
    name: str
    rate_limits: RateLimit
    permissions: List[str]
    is_active: bool
    created_at: datetime

class LiquidityAPI:
    """Enterprise Liquidity API for private pool access"""
    
    def __init__(self, config, private_pool_manager):
        self.config = config
        self.private_pool_manager = private_pool_manager
        self.logger = logging.getLogger(__name__)
        self.api_clients = {}
        self.rate_limits = {}
        self.access_tokens = {}
        
        # Initialize API
        self.initialize_api_clients()
        self.setup_rate_limiting()
    
    def initialize_api_clients(self):
        """Initialize registered API clients"""
        clients_config = self.config.get('api_clients', [])
        
        for client_config in clients_config:
            client = APIClient(
                client_id=client_config['client_id'],
                name=client_config['name'],
                rate_limits=RateLimit(
                    requests_per_minute=client_config.get('requests_per_minute', 100),
                    requests_per_hour=client_config.get('requests_per_hour', 1000),
                    requests_per_day=client_config.get('requests_per_day', 10000)
                ),
                permissions=client_config.get('permissions', []),
                is_active=client_config.get('is_active', True),
                created_at=datetime.now()
            )
            
            self.api_clients[client.client_id] = client
    
    def setup_rate_limiting(self):
        """Setup rate limiting system"""
        for client_id in self.api_clients.keys():
            self.rate_limits[client_id] = {
                'minute': {'count': 0, 'reset_time': datetime.now()},
                'hour': {'count': 0, 'reset_time': datetime.now()},
                'day': {'count': 0, 'reset_time': datetime.now()}
            }
    
    async def handle_request(self, request: web.Request) -> web.Response:
        """Handle API request with enterprise features"""
        start_time = datetime.now()
        
        try:
            # Extract and validate API key
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return await self.error_response("API key required", APIErrorCode.UNAUTHORIZED)
            
            # Validate client
            client = await self.validate_client(api_key)
            if not client:
                return await self.error_response("Invalid API key", APIErrorCode.UNAUTHORIZED)
            
            # Check rate limits
            if not await self.check_rate_limits(client.client_id):
                return await self.error_response("Rate limit exceeded", APIErrorCode.RATE_LIMITED)
            
            # Route request to appropriate handler
            response = await self.route_request(request, client)
            
            # Log request
            await self.log_request(request, client, response, start_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return await self.error_response("Internal server error", APIErrorCode.INTERNAL_ERROR)
    
    async def validate_client(self, api_key: str) -> Optional[APIClient]:
        """Validate API client"""
        for client in self.api_clients.values():
            if not client.is_active:
                continue
            
            # In production, this would use secure key validation
            expected_key = self.generate_client_key(client.client_id)
            if hmac.compare_digest(api_key, expected_key):
                return client
        
        return None
    
    def generate_client_key(self, client_id: str) -> str:
        """Generate client API key"""
        secret = self.config.get('api_secret', 'default-secret')
        message = f"{client_id}:{secret}"
        return hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def check_rate_limits(self, client_id: str) -> bool:
        """Check client rate limits"""
        client_limits = self.rate_limits[client_id]
        client = self.api_clients[client_id]
        now = datetime.now()
        
        # Check minute limit
        if now - client_limits['minute']['reset_time'] > timedelta(minutes=1):
            client_limits['minute'] = {'count': 0, 'reset_time': now}
        
        if client_limits['minute']['count'] >= client.rate_limits.requests_per_minute:
            return False
        
        # Check hour limit
        if now - client_limits['hour']['reset_time'] > timedelta(hours=1):
            client_limits['hour'] = {'count': 0, 'reset_time': now}
        
        if client_limits['hour']['count'] >= client.rate_limits.requests_per_hour:
            return False
        
        # Check day limit
        if now - client_limits['day']['reset_time'] > timedelta(days=1):
            client_limits['day'] = {'count': 0, 'reset_time': now}
        
        if client_limits['day']['count'] >= client.rate_limits.requests_per_day:
            return False
        
        # Increment counters
        client_limits['minute']['count'] += 1
        client_limits['hour']['count'] += 1
        client_limits['day']['count'] += 1
        
        return True
    
    async def route_request(self, request: web.Request, client: APIClient) -> web.Response:
        """Route request to appropriate handler"""
        path = request.path
        method = request.method
        
        # API endpoints routing
        if path == '/api/v1/pools' and method == 'GET':
            return await self.get_available_pools(request, client)
        elif path == '/api/v1/pools/{pool_id}/depth' and method == 'GET':
            return await self.get_pool_depth(request, client)
        elif path == '/api/v1/trades' and method == 'POST':
            return await self.execute_trade(request, client)
        elif path == '/api/v1/trades/{trade_id}' and method == 'GET':
            return await self.get_trade_status(request, client)
        elif path == '/api/v1/allocations' and method == 'POST':
            return await self.manage_allocation(request, client)
        elif path == '/api/v1/analytics' and method == 'GET':
            return await self.get_analytics(request, client)
        else:
            return await self.error_response("Endpoint not found", APIErrorCode.NOT_FOUND)
    
    async def get_available_pools(self, request: web.Request, client: APIClient) -> web.Response:
        """Get available private pools"""
        try:
            # Check permissions
            if 'read_pools' not in client.permissions:
                return await self.error_response("Insufficient permissions", APIErrorCode.FORBIDDEN)
            
            pools_data = []
            for pool_id, pool in self.private_pool_manager.private_pools.items():
                if pool.is_active:
                    pools_data.append({
                        'pool_id': pool.pool_id,
                        'name': pool.name,
                        'tier': pool.tier.value,
                        'tokens': pool.tokens,
                        'total_liquidity': pool.total_liquidity,
                        'fee_structure': pool.fee_structure,
                        'performance': pool.performance_metrics
                    })
            
            response = APIResponse(
                success=True,
                data={'pools': pools_data},
                metadata={
                    'total_pools': len(pools_data),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return web.json_response(response.__dict__)
            
        except Exception as e:
            self.logger.error(f"Get available pools failed: {e}")
            return await self.error_response("Failed to fetch pools", APIErrorCode.INTERNAL_ERROR)
    
    async def get_pool_depth(self, request: web.Request, client: APIClient) -> web.Response:
        """Get pool depth information"""
        try:
            pool_id = request.match_info.get('pool_id')
            
            # Check permissions
            if 'read_depth' not in client.permissions:
                return await self.error_response("Insufficient permissions", APIErrorCode.FORBIDDEN)
            
            # Get pool depth from manager
            depth_data = await self.private_pool_manager.get_pool_depth(pool_id)
            
            response = APIResponse(
                success=True,
                data=depth_data,
                metadata={
                    'pool_id': pool_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return web.json_response(response.__dict__)
            
        except Exception as e:
            self.logger.error(f"Get pool depth failed: {e}")
            return await self.error_response("Failed to fetch pool depth", APIErrorCode.INTERNAL_ERROR)
    
    async def execute_trade(self, request: web.Request, client: APIClient) -> web.Response:
        """Execute trade through private pool"""
        try:
            trade_data = await request.json()
            
            # Check permissions
            if 'execute_trades' not in client.permissions:
                return await self.error_response("Insufficient permissions", APIErrorCode.FORBIDDEN)
            
            # Validate trade data
            validation_result = await self.validate_trade_request(trade_data)
            if not validation_result['valid']:
                return await self.error_response(
                    f"Invalid trade request: {validation_result['error']}", 
                    APIErrorCode.BAD_REQUEST
                )
            
            # Execute trade
            trade_result = await self.private_pool_manager.execute_private_trade({
                **trade_data,
                'client_id': client.client_id
            })
            
            response = APIResponse(
                success=True,
                data=trade_result,
                metadata={
                    'trade_id': trade_result.get('trade_id'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return web.json_response(response.__dict__)
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            return await self.error_response("Trade execution failed", APIErrorCode.INTERNAL_ERROR)
    
    async def validate_trade_request(self, trade_data: Dict) -> Dict:
        """Validate trade request"""
        required_fields = ['pool_id', 'token_in', 'token_out', 'amount']
        
        for field in required_fields:
            if field not in trade_data:
                return {'valid': False, 'error': f'Missing field: {field}'}
        
        # Validate amount
        try:
            amount = float(trade_data['amount'])
            if amount <= 0:
                return {'valid': False, 'error': 'Amount must be positive'}
        except ValueError:
            return {'valid': False, 'error': 'Invalid amount format'}
        
        return {'valid': True}
    
    async def get_trade_status(self, request: web.Request, client: APIClient) -> web.Response:
        """Get trade status"""
        try:
            trade_id = request.match_info.get('trade_id')
            
            # Check permissions
            if 'read_trades' not in client.permissions:
                return await self.error_response("Insufficient permissions", APIErrorCode.FORBIDDEN)
            
            # Get trade status from manager
            trade_status = await self.private_pool_manager.get_trade_status(trade_id)
            
            if not trade_status:
                return await self.error_response("Trade not found", APIErrorCode.NOT_FOUND)
            
            response = APIResponse(
                success=True,
                data=trade_status,
                metadata={
                    'trade_id': trade_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return web.json_response(response.__dict__)
            
        except Exception as e:
            self.logger.error(f"Get trade status failed: {e}")
            return await self.error_response("Failed to fetch trade status", APIErrorCode.INTERNAL_ERROR)
    
    async def manage_allocation(self, request: web.Request, client: APIClient) -> web.Response:
        """Manage liquidity allocation"""
        try:
            allocation_data = await request.json()
            
            # Check permissions
            if 'manage_allocations' not in client.permissions:
                return await self.error_response("Insufficient permissions", APIErrorCode.FORBIDDEN)
            
            # Validate allocation data
            validation_result = await self.validate_allocation_request(allocation_data)
            if not validation_result['valid']:
                return await self.error_response(
                    f"Invalid allocation request: {validation_result['error']}", 
                    APIErrorCode.BAD_REQUEST
                )
            
            # Manage allocation
            allocation_result = await self.private_pool_manager.manage_liquidity_allocation({
                **allocation_data,
                'client_id': client.client_id
            })
            
            response = APIResponse(
                success=True,
                data=allocation_result,
                metadata={
                    'allocation_id': allocation_result.allocation_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return web.json_response(response.__dict__)
            
        except Exception as e:
            self.logger.error(f"Allocation management failed: {e}")
            return await self.error_response("Allocation management failed", APIErrorCode.INTERNAL_ERROR)
    
    async def validate_allocation_request(self, allocation_data: Dict) -> Dict:
        """Validate allocation request"""
        required_fields = ['pool_id', 'token', 'amount', 'strategy']
        
        for field in required_fields:
            if field not in allocation_data:
                return {'valid': False, 'error': f'Missing field: {field}'}
        
        # Validate strategy
        valid_strategies = ['balanced', 'optimized', 'conservative']
        if allocation_data['strategy'] not in valid_strategies:
            return {'valid': False, 'error': f'Invalid strategy. Must be one of: {valid_strategies}'}
        
        return {'valid': True}
    
    async def get_analytics(self, request: web.Request, client: APIClient) -> web.Response:
        """Get analytics data"""
        try:
            # Check permissions
            if 'read_analytics' not in client.permissions:
                return await self.error_response("Insufficient permissions", APIErrorCode.FORBIDDEN)
            
            # Get query parameters
            pool_id = request.query.get('pool_id')
            timeframe = request.query.get('timeframe', '24h')
            metric_type = request.query.get('metric_type', 'performance')
            
            # Get analytics data
            analytics_data = await self.private_pool_manager.get_pool_analytics(pool_id)
            
            response = APIResponse(
                success=True,
                data=analytics_data,
                metadata={
                    'pool_id': pool_id,
                    'timeframe': timeframe,
                    'metric_type': metric_type,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return web.json_response(response.__dict__)
            
        except Exception as e:
            self.logger.error(f"Get analytics failed: {e}")
            return await self.error_response("Failed to fetch analytics", APIErrorCode.INTERNAL_ERROR)
    
    async def error_response(self, error_message: str, error_code: APIErrorCode) -> web.Response:
        """Create error response"""
        response = APIResponse(
            success=False,
            error=error_message,
            code=error_code
        )
        
        return web.json_response(
            response.__dict__,
            status=error_code.value
        )
    
    async def log_request(self, request: web.Request, client: APIClient, 
                         response: web.Response, start_time: datetime):
        """Log API request"""
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        log_entry = {
            'client_id': client.client_id,
            'method': request.method,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote,
            'timestamp': start_time.isoformat(),
            'duration_ms': duration,
            'response_code': response.status,
            'query_params': dict(request.query)
        }
        
        self.logger.info(f"API Request: {log_entry}")
    
    async def generate_client_token(self, client: APIClient, expires_in: int = 3600) -> str:
        """Generate JWT token for client"""
        payload = {
            'client_id': client.client_id,
            'permissions': client.permissions,
            'exp': datetime.now() + timedelta(seconds=expires_in),
            'iat': datetime.now()
        }
        
        secret = self.config.get('jwt_secret', 'default-jwt-secret')
        token = jwt.encode(payload, secret, algorithm='HS256')
        
        return token
    
    async def validate_client_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token"""
        try:
            secret = self.config.get('jwt_secret', 'default-jwt-secret')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            
            # Check if client exists and is active
            client = self.api_clients.get(payload['client_id'])
            if not client or not client.is_active:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def get_api_usage_metrics(self, client_id: str = None) -> Dict:
        """Get API usage metrics"""
        metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'endpoint_usage': {},
            'client_usage': {}
        }
        
        # Implementation would aggregate from request logs
        # Placeholder implementation
        
        return metrics
    
    async def create_api_client(self, client_config: Dict) -> APIClient:
        """Create new API client"""
        client_id = self.generate_client_id()
        
        client = APIClient(
            client_id=client_id,
            name=client_config['name'],
            rate_limits=RateLimit(
                requests_per_minute=client_config.get('requests_per_minute', 100),
                requests_per_hour=client_config.get('requests_per_hour', 1000),
                requests_per_day=client_config.get('requests_per_day', 10000)
            ),
            permissions=client_config.get('permissions', []),
            is_active=True,
            created_at=datetime.now()
        )
        
        self.api_clients[client_id] = client
        self.setup_client_rate_limits(client_id)
        
        return client
    
    def generate_client_id(self) -> str:
        """Generate unique client ID"""
        timestamp = str(int(datetime.now().timestamp()))
        random_suffix = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        return f"client_{timestamp}_{random_suffix}"
    
    def setup_client_rate_limits(self, client_id: str):
        """Setup rate limits for new client"""
        self.rate_limits[client_id] = {
            'minute': {'count': 0, 'reset_time': datetime.now()},
            'hour': {'count': 0, 'reset_time': datetime.now()},
            'day': {'count': 0, 'reset_time': datetime.now()}
        }
    
    async def deactivate_client(self, client_id: str) -> bool:
        """Deactivate API client"""
        if client_id in self.api_clients:
            self.api_clients[client_id].is_active = False
            return True
        return False
    
    async def update_client_permissions(self, client_id: str, permissions: List[str]) -> bool:
        """Update client permissions"""
        if client_id in self.api_clients:
            self.api_clients[client_id].permissions = permissions
            return True
        return False
    
    async def get_client_analytics(self, client_id: str) -> Dict:
        """Get analytics for specific client"""
        client = self.api_clients.get(client_id)
        if not client:
            return {'error': 'Client not found'}
        
        return {
            'client_info': {
                'client_id': client.client_id,
                'name': client.name,
                'is_active': client.is_active,
                'created_at': client.created_at.isoformat()
            },
            'rate_limits': {
                'minute': client.rate_limits.requests_per_minute,
                'hour': client.rate_limits.requests_per_hour,
                'day': client.rate_limits.requests_per_day
            },
            'permissions': client.permissions,
            'usage_metrics': await self.get_client_usage_metrics(client_id)
        }
    
    async def get_client_usage_metrics(self, client_id: str) -> Dict:
        """Get usage metrics for client"""
        # Implementation would aggregate from request logs
        # Placeholder implementation
        return {
            'total_requests': 1500,
            'success_rate': 99.2,
            'average_response_time': 125,
            'most_used_endpoint': '/api/v1/pools',
            'last_request': datetime.now().isoformat()
        }

# Web server setup
async def create_api_server(config, private_pool_manager):
    """Create API web server"""
    api = LiquidityAPI(config, private_pool_manager)
    
    app = web.Application()
    
    # Add routes
    app.router.add_get('/api/v1/pools', api.handle_request)
    app.router.add_get('/api/v1/pools/{pool_id}/depth', api.handle_request)
    app.router.add_post('/api/v1/trades', api.handle_request)
    app.router.add_get('/api/v1/trades/{trade_id}', api.handle_request)
    app.router.add_post('/api/v1/allocations', api.handle_request)
    app.router.add_get('/api/v1/analytics', api.handle_request)
    
    # Health check endpoint
    app.router.add_get('/health', lambda request: web.json_response({'status': 'healthy'}))
    
    return app

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'api_clients': [
            {
                'client_id': 'arbitrage_fund_001',
                'name': 'Arbitrage Fund Alpha',
                'requests_per_minute': 500,
                'requests_per_hour': 5000,
                'permissions': ['read_pools', 'read_depth', 'execute_trades', 'read_trades']
            }
        ],
        'api_secret': 'secure-api-secret-123',
        'jwt_secret': 'secure-jwt-secret-456'
    }
    
    # In production, you would initialize with actual private pool manager
    private_pool_manager = None  # Placeholder
    
    # Create and run server
    app = create_api_server(config, private_pool_manager)
    web.run_app(app, host='0.0.0.0', port=8080)
