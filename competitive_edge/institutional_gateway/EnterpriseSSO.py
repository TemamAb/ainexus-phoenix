"""
AI-NEXUS v5.0 - ENTERPRISE SINGLE SIGN-ON (SSO) MODULE
Advanced institutional authentication and authorization system
Multi-protocol SSO, MFA, and enterprise security integration
"""

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import hashlib
import base64
import json
from collections import defaultdict, deque

class SSOProtocol(Enum):
    SAML_2_0 = "saml_2_0"
    OIDC = "openid_connect"
    OAuth_2_0 = "oauth_2_0"
    LDAP = "ldap"
    ACTIVE_DIRECTORY = "active_directory"
    CUSTOM_JWT = "custom_jwt"

class AuthLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class MFAFactor(Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"
    PUSH_NOTIFICATION = "push_notification"

@dataclass
class EnterpriseUser:
    user_id: str
    enterprise_id: str
    username: str
    email: str
    auth_level: AuthLevel
    mfa_factors: List[MFAFactor]
    permissions: Dict[str, List[str]]
    metadata: Dict[str, Any]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

@dataclass
class SSOSession:
    session_id: str
    user_id: str
    enterprise_id: str
    protocol: SSOProtocol
    issued_at: datetime
    expires_at: datetime
    access_token: str
    refresh_token: str
    mfa_verified: bool
    ip_address: str
    user_agent: str
    metadata: Dict[str, Any]

@dataclass
class EnterpriseConfig:
    enterprise_id: str
    name: str
    supported_protocols: List[SSOProtocol]
    mfa_required: bool
    session_timeout: int  # minutes
    max_concurrent_sessions: int
    allowed_domains: List[str]
    security_policies: Dict[str, Any]
    metadata: Dict[str, Any]

class EnterpriseSSO:
    """
    Advanced Enterprise Single Sign-On System
    Multi-protocol authentication for institutional clients
    """
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.enterprises = {}
        self.active_sessions = defaultdict(list)
        self.failed_attempts = defaultdict(int)
        
        # Security configurations
        self.security_config = {
            'max_failed_attempts': 5,
            'lockout_duration': 900,  # 15 minutes
            'session_timeout': 1440,  # 24 hours
            'refresh_token_lifetime': 43200,  # 30 days
            'jwt_secret': self._generate_jwt_secret(),
            'password_min_length': 12,
            'mfa_required_for_admin': True
        }
        
        # Initialize cryptographic keys
        self._initialize_crypto_keys()
        
        # Performance tracking
        self.auth_metrics = {
            'total_logins': 0,
            'failed_logins': 0,
            'mfa_attempts': 0,
            'session_creations': 0,
            'token_refreshes': 0
        }
    
    def _initialize_crypto_keys(self):
        """Initialize cryptographic keys for JWT and encryption"""
        
        # Generate RSA key pair for JWT signing
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        self.public_key = self.private_key.public_key()
        
        # Generate encryption key for sensitive data
        self.encryption_key = secrets.token_bytes(32)
    
    def _generate_jwt_secret(self) -> str:
        """Generate JWT secret"""
        return secrets.token_urlsafe(64)
    
    async def register_enterprise(self, config: EnterpriseConfig) -> bool:
        """Register a new enterprise client"""
        
        if config.enterprise_id in self.enterprises:
            return False
        
        self.enterprises[config.enterprise_id] = config
        print(f"Enterprise registered: {config.name} ({config.enterprise_id})")
        return True
    
    async def create_enterprise_user(self, user_data: Dict[str, Any]) -> Optional[EnterpriseUser]:
        """Create a new enterprise user"""
        
        enterprise_id = user_data.get('enterprise_id')
        if enterprise_id not in self.enterprises:
            return None
        
        user_id = f"user_{enterprise_id}_{secrets.token_urlsafe(8)}"
        
        user = EnterpriseUser(
            user_id=user_id,
            enterprise_id=enterprise_id,
            username=user_data['username'],
            email=user_data['email'],
            auth_level=AuthLevel(user_data.get('auth_level', 'basic')),
            mfa_factors=user_data.get('mfa_factors', []),
            permissions=user_data.get('permissions', {}),
            metadata=user_data.get('metadata', {}),
            created_at=datetime.now(),
            last_login=None,
            is_active=True
        )
        
        # Hash and store password
        password_hash = self._hash_password(user_data['password'])
        user.metadata['password_hash'] = password_hash
        
        self.users[user_id] = user
        print(f"Enterprise user created: {user.username} ({user_id})")
        
        return user
    
    async def authenticate_user(self, identifier: str, password: str, 
                              protocol: SSOProtocol, ip_address: str,
                              user_agent: str) -> Tuple[bool, Optional[SSOSession], str]:
        """Authenticate user with credentials"""
        
        user = self._find_user_by_identifier(identifier)
        if not user:
            self.auth_metrics['failed_logins'] += 1
            return False, None, "User not found"
        
        # Check if account is locked
        if self._is_account_locked(user.user_id):
            return False, None, "Account temporarily locked due to failed attempts"
        
        # Verify password
        if not self._verify_password(password, user.metadata.get('password_hash', '')):
            self.failed_attempts[user.user_id] += 1
            self.auth_metrics['failed_logins'] += 1
            return False, None, "Invalid credentials"
        
        # Reset failed attempts on successful login
        self.failed_attempts[user.user_id] = 0
        
        # Check if MFA is required
        enterprise = self.enterprises.get(user.enterprise_id)
        mfa_required = (enterprise and enterprise.mfa_required) or \
                      (user.auth_level in [AuthLevel.ADMIN, AuthLevel.SUPER_ADMIN] and 
                       self.security_config['mfa_required_for_admin'])
        
        # Create session
        session = await self._create_session(
            user, protocol, ip_address, user_agent, mfa_verified=not mfa_required
        )
        
        # Update user last login
        user.last_login = datetime.now()
        
        self.auth_metrics['total_logins'] += 1
        self.auth_metrics['session_creations'] += 1
        
        message = "Authentication successful" if not mfa_required else "MFA verification required"
        return True, session, message
    
    async def verify_mfa(self, session_id: str, factor: MFAFactor, 
                        code: str) -> Tuple[bool, Optional[SSOSession]]:
        """Verify multi-factor authentication"""
        
        session = self.sessions.get(session_id)
        if not session:
            return False, None
        
        user = self.users.get(session.user_id)
        if not user:
            return False, None
        
        self.auth_metrics['mfa_attempts'] += 1
        
        # Simplified MFA verification (in production, integrate with actual MFA providers)
        if await self._verify_mfa_code(user, factor, code):
            session.mfa_verified = True
            session.metadata['mfa_factor'] = factor.value
            session.metadata['mfa_verified_at'] = datetime.now()
            
            print(f"MFA verified for user: {user.username}")
            return True, session
        else:
            return False, None
    
    async def refresh_token(self, refresh_token: str) -> Optional[SSOSession]:
        """Refresh access token"""
        
        # Find session by refresh token
        session = next((s for s in self.sessions.values() 
                       if s.refresh_token == refresh_token), None)
        
        if not session or session.expires_at < datetime.now():
            return None
        
        # Create new session with updated tokens
        user = self.users.get(session.user_id)
        if not user:
            return None
        
        new_session = await self._create_session(
            user, session.protocol, session.ip_address, 
            session.user_agent, mfa_verified=session.mfa_verified
        )
        
        # Invalidate old session
        await self.invalidate_session(session.session_id)
        
        self.auth_metrics['token_refreshes'] += 1
        return new_session
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session"""
        
        if session_id not in self.sessions:
            return False
        
        session = self.sessions.pop(session_id)
        
        # Remove from active sessions
        if session.user_id in self.active_sessions:
            self.active_sessions[session.user_id] = [
                s for s in self.active_sessions[session.user_id]
                if s.session_id != session_id
            ]
        
        print(f"Session invalidated: {session_id}")
        return True
    
    async def validate_access_token(self, access_token: str) -> Tuple[bool, Optional[EnterpriseUser]]:
        """Validate access token and return user"""
        
        try:
            # Verify JWT signature and expiration
            payload = jwt.decode(
                access_token, 
                self.security_config['jwt_secret'],
                algorithms=['HS256']
            )
            
            session_id = payload.get('session_id')
            session = self.sessions.get(session_id)
            
            if not session or session.expires_at < datetime.now():
                return False, None
            
            user = self.users.get(session.user_id)
            if not user or not user.is_active:
                return False, None
            
            return True, user
            
        except jwt.InvalidTokenError:
            return False, None
    
    def _find_user_by_identifier(self, identifier: str) -> Optional[EnterpriseUser]:
        """Find user by username or email"""
        
        for user in self.users.values():
            if user.username == identifier or user.email == identifier:
                return user
        return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def _is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        
        failed_count = self.failed_attempts.get(user_id, 0)
        return failed_count >= self.security_config['max_failed_attempts']
    
    async def _create_session(self, user: EnterpriseUser, protocol: SSOProtocol,
                            ip_address: str, user_agent: str, 
                            mfa_verified: bool) -> SSOSession:
        """Create a new SSO session"""
        
        session_id = f"session_{secrets.token_urlsafe(16)}"
        
        # Generate tokens
        access_token = self._generate_access_token(session_id, user)
        refresh_token = secrets.token_urlsafe(32)
        
        # Calculate expiration
        issued_at = datetime.now()
        expires_at = issued_at + timedelta(
            minutes=self.security_config['session_timeout']
        )
        
        session = SSOSession(
            session_id=session_id,
            user_id=user.user_id,
            enterprise_id=user.enterprise_id,
            protocol=protocol,
            issued_at=issued_at,
            expires_at=expires_at,
            access_token=access_token,
            refresh_token=refresh_token,
            mfa_verified=mfa_verified,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                'auth_level': user.auth_level.value,
                'created_at': issued_at.isoformat()
            }
        )
        
        self.sessions[session_id] = session
        self.active_sessions[user.user_id].append(session)
        
        # Enforce maximum concurrent sessions
        await self._enforce_session_limits(user.user_id)
        
        return session
    
    def _generate_access_token(self, session_id: str, user: EnterpriseUser) -> str:
        """Generate JWT access token"""
        
        payload = {
            'session_id': session_id,
            'user_id': user.user_id,
            'enterprise_id': user.enterprise_id,
            'auth_level': user.auth_level.value,
            'exp': datetime.now() + timedelta(
                minutes=self.security_config['session_timeout']
            ),
            'iat': datetime.now()
        }
        
        return jwt.encode(
            payload, 
            self.security_config['jwt_secret'],
            algorithm='HS256'
        )
    
    async def _verify_mfa_code(self, user: EnterpriseUser, factor: MFAFactor, 
                             code: str) -> bool:
        """Verify MFA code (simplified implementation)"""
        
        # In production, integrate with actual MFA providers
        # This is a simplified mock implementation
        
        if factor == MFAFactor.TOTP:
            # Mock TOTP verification
            return len(code) == 6 and code.isdigit()
        
        elif factor == MFAFactor.SMS:
            # Mock SMS verification
            return len(code) == 6 and code.isdigit()
        
        elif factor == MFAFactor.EMAIL:
            # Mock email verification
            return len(code) == 8 and code.isalnum()
        
        elif factor == MFAFactor.BIOMETRIC:
            # Mock biometric verification
            return code == "biometric_verified"
        
        else:
            return False
    
    async def _enforce_session_limits(self, user_id: str):
        """Enforce maximum concurrent sessions per user"""
        
        enterprise_id = self.users[user_id].enterprise_id
        enterprise = self.enterprises.get(enterprise_id)
        
        if not enterprise:
            return
        
        max_sessions = enterprise.max_concurrent_sessions
        user_sessions = self.active_sessions.get(user_id, [])
        
        if len(user_sessions) > max_sessions:
            # Remove oldest sessions
            user_sessions.sort(key=lambda s: s.issued_at)
            sessions_to_remove = user_sessions[:-max_sessions]
            
            for session in sessions_to_remove:
                await self.invalidate_session(session.session_id)
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, List[str]]:
        """Get user permissions"""
        
        user = self.users.get(user_id)
        if not user:
            return {}
        
        return user.permissions
    
    async def check_permission(self, user_id: str, resource: str, 
                             action: str) -> bool:
        """Check if user has permission for resource action"""
        
        permissions = await self.get_user_permissions(user_id)
        resource_perms = permissions.get(resource, [])
        
        return action in resource_perms
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system authentication metrics"""
        
        return {
            'total_users': len(self.users),
            'total_enterprises': len(self.enterprises),
            'active_sessions': sum(len(sessions) for sessions in self.active_sessions.values()),
            'authentication_metrics': self.auth_metrics,
            'failed_attempts': dict(self.failed_attempts)
        }
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.expires_at < current_time
        ]
        
        for session_id in expired_sessions:
            await self.invalidate_session(session_id)
        
        print(f"Cleaned up {len(expired_sessions)} expired sessions")

# Example usage
if __name__ == "__main__":
    async def demo():
        sso = EnterpriseSSO()
        
        # Register enterprise
        enterprise_config = EnterpriseConfig(
            enterprise_id="ent_12345",
            name="Global Investment Bank",
            supported_protocols=[SSOProtocol.SAML_2_0, SSOProtocol.OIDC],
            mfa_required=True,
            session_timeout=480,  # 8 hours
            max_concurrent_sessions=3,
            allowed_domains=["gibank.com"],
            security_policies={
                "password_policy": "complex",
                "session_timeout": 480,
                "mfa_required": True
            },
            metadata={"industry": "finance", "tier": "premium"}
        )
        
        await sso.register_enterprise(enterprise_config)
        
        # Create enterprise user
        user_data = {
            'enterprise_id': 'ent_12345',
            'username': 'john.trader',
            'email': 'john.trader@gibank.com',
            'password': 'SecurePass123!',
            'auth_level': 'admin',
            'mfa_factors': [MFAFactor.TOTP, MFAFactor.EMAIL],
            'permissions': {
                'trading': ['read', 'write', 'execute'],
                'risk': ['read', 'write'],
                'reports': ['read']
            },
            'metadata': {'department': 'trading', 'location': 'NYC'}
        }
        
        user = await sso.create_enterprise_user(user_data)
        
        # Authenticate user
        success, session, message = await sso.authenticate_user(
            identifier='john.trader',
            password='SecurePass123!',
            protocol=SSOProtocol.OIDC,
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        print(f"Authentication: {success}, Message: {message}")
        
        if success and session and not session.mfa_verified:
            # Verify MFA
            mfa_success, verified_session = await sso.verify_mfa(
                session.session_id, MFAFactor.TOTP, "123456"
            )
            print(f"MFA Verification: {mfa_success}")
        
        # Get system metrics
        metrics = sso.get_system_metrics()
        print(f"System Metrics: {metrics}")
    
    asyncio.run(demo())
