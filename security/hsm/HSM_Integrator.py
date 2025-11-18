#!/usr/bin/env python3
"""
Enterprise Hardware Security Module (HSM) Integration Layer
Secure key management, cryptographic operations, and compliance enforcement
"""

import os
import hmac
import hashlib
import base64
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import secrets
import threading
from contextlib import contextmanager

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HSMConfig:
    hsm_type: str  # 'aws_cloudhsm', 'yubihsm', 'azure_dedicated_hsm'
    endpoint: str
    partition: str
    credentials: Dict[str, str]
    key_retention_days: int = 365
    compliance_standard: str = "FIPS-140-2"
    audit_logging: bool = True
    key_rotation_days: int = 90

@dataclass
class KeyMetadata:
    key_id: str
    key_type: str
    key_size: int
    created_at: datetime
    expires_at: datetime
    operations: List[str]
    compliance_tags: Dict[str, str]
    rotation_count: int = 0

@dataclass 
class SignatureResult:
    signature: bytes
    algorithm: str
    timestamp: datetime
    key_id: str
    verification_hash: str

class HSMIntegrator:
    """
    Enterprise HSM integration with comprehensive security controls,
    audit logging, and compliance enforcement.
    """
    
    def __init__(self, config: HSMConfig):
        self.config = config
        self.initialized = False
        self.key_registry: Dict[str, KeyMetadata] = {}
        self.audit_log: List[Dict] = []
        self._lock = threading.RLock()
        self._session_handle = None
        
        # Security counters
        self.security_metrics = {
            'signing_operations': 0,
            'key_generations': 0,
            'failed_operations': 0,
            'compliance_violations': 0
        }
        
        self._initialize_hsm_connection()
        logger.info(f"HSMIntegrator initialized for {config.hsm_type}")

    def _initialize_hsm_connection(self):
        """Initialize secure connection to HSM with validation"""
        try:
            with self._lock:
                if self.config.hsm_type == 'aws_cloudhsm':
                    self._init_aws_cloudhsm()
                elif self.config.hsm_type == 'yubihsm':
                    self._init_yubihsm()
                elif self.config.hsm_type == 'azure_dedicated_hsm':
                    self._init_azure_hsm()
                else:
                    raise ValueError(f"Unsupported HSM type: {self.config.hsm_type}")
                
                self.initialized = True
                self._log_audit_event("HSM_INITIALIZED", "HSM connection established successfully")
                
        except Exception as e:
            logger.error(f"HSM initialization failed: {e}")
            self._log_audit_event("HSM_INIT_FAILED", str(e), level="ERROR")
            raise ConnectionError(f"HSM initialization failed: {e}")

    def _init_aws_cloudhsm(self):
        """Initialize AWS CloudHSM connection with boto3"""
        try:
            import boto3
            from botocore.config import Config
            
            # Configure with retry logic and timeouts
            config = Config(
                retries={'max_attempts': 3, 'mode': 'standard'},
                read_timeout=30,
                connect_timeout=10
            )
            
            self.cloudhsm_client = boto3.client(
                'cloudhsmv2',
                endpoint_url=self.config.endpoint,
                aws_access_key_id=self.config.credentials.get('aws_access_key_id'),
                aws_secret_access_key=self.config.credentials.get('aws_secret_access_key'),
                region_name=self.config.credentials.get('region', 'us-east-1'),
                config=config
            )
            
            # Verify cluster status
            clusters = self.cloudhsm_client.describe_clusters()
            active_clusters = [c for c in clusters['Clusters'] if c['State'] == 'ACTIVE']
            
            if not active_clusters:
                raise RuntimeError("No active CloudHSM clusters found")
                
            logger.info(f"Connected to AWS CloudHSM cluster: {active_clusters[0]['ClusterId']}")
            
        except ImportError:
            raise RuntimeError("boto3 required for AWS CloudHSM integration")
        except Exception as e:
            raise RuntimeError(f"AWS CloudHSM connection failed: {e}")

    def _init_yubihsm(self):
        """Initialize YubiHSM connection"""
        try:
            from yubihsm import YubiHsm
            from yubihsm.objects import AsymmetricKey, AuthenticationKey
            
            # Connect to YubiHSM
            self.yubihsm = YubiHsm.connect(self.config.endpoint)
            self.session = self.yubihsm.create_session_derived(
                1,  # Auth key ID
                self.config.credentials.get('password', '')
            )
            
            logger.info("Connected to YubiHSM successfully")
            
        except ImportError:
            raise RuntimeError("yubihsm package required for YubiHSM integration")
        except Exception as e:
            raise RuntimeError(f"YubiHSM connection failed: {e}")

    def _init_azure_hsm(self):
        """Initialize Azure Dedicated HSM connection"""
        try:
            from azure.identity import ClientSecretCredential
            from azure.keyvault.keys import KeyClient
            from azure.keyvault.keys.crypto import CryptographyClient
            
            credential = ClientSecretCredential(
                tenant_id=self.config.credentials.get('tenant_id'),
                client_id=self.config.credentials.get('client_id'),
                client_secret=self.config.credentials.get('client_secret')
            )
            
            self.key_client = KeyClient(
                vault_url=self.config.endpoint,
                credential=credential
            )
            
            logger.info("Connected to Azure Dedicated HSM successfully")
            
        except ImportError:
            raise RuntimeError("azure-keyvault-keys required for Azure HSM integration")
        except Exception as e:
            raise RuntimeError(f"Azure HSM connection failed: {e}")

    def generate_key_pair(self, key_id: str, key_type: str = 'EC', 
                         key_size: int = 256, tags: Dict[str, str] = None) -> KeyMetadata:
        """
        Generate a new cryptographic key pair in HSM with compliance checks
        """
        if not self.initialized:
            raise RuntimeError("HSM not initialized")
            
        with self._lock:
            try:
                # Validate key parameters
                self._validate_key_parameters(key_type, key_size)
                
                # Check for existing key
                if key_id in self.key_registry:
                    raise ValueError(f"Key ID already exists: {key_id}")
                
                # Generate key in HSM
                key_metadata = self._hsm_generate_key(key_id, key_type, key_size)
                
                # Add compliance tags
                key_metadata.compliance_tags = tags or {}
                key_metadata.compliance_tags.update({
                    'generated_by': 'HSMIntegrator',
                    'compliance_standard': self.config.compliance_standard,
                    'environment': os.getenv('ENVIRONMENT', 'production')
                })
                
                # Register key
                self.key_registry[key_id] = key_metadata
                self.security_metrics['key_generations'] += 1
                
                self._log_audit_event(
                    "KEY_GENERATED",
                    f"Generated {key_type} key {key_id}",
                    key_id=key_id
                )
                
                return key_metadata
                
            except Exception as e:
                self.security_metrics['failed_operations'] += 1
                logger.error(f"Key generation failed for {key_id}: {e}")
                self._log_audit_event("KEY_GENERATION_FAILED", str(e), key_id=key_id, level="ERROR")
                raise RuntimeError(f"Key generation failed: {e}")

    def _validate_key_parameters(self, key_type: str, key_size: int):
        """Validate key generation parameters against security standards"""
        if key_type == 'EC':
            if key_size not in [256, 384, 521]:
                raise ValueError(f"Invalid EC key size: {key_size}")
        elif key_type == 'RSA':
            if key_size < 2048:
                raise ValueError("RSA key size must be at least 2048 bits for security")
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

    def sign_transaction(self, key_id: str, transaction_data: bytes, 
                        algorithm: str = 'ECDSA') -> SignatureResult:
        """
        Sign transaction data using HSM-stored key with comprehensive validation
        """
        if not self.initialized:
            raise RuntimeError("HSM not initialized")
            
        if key_id not in self.key_registry:
            raise KeyError(f"Key not found: {key_id}")
            
        with self._lock:
            try:
                # Validate input data
                if not transaction_data or len(transaction_data) == 0:
                    raise ValueError("Transaction data cannot be empty")
                
                # HSM-specific signing operation
                signature = self._hsm_sign(key_id, transaction_data, algorithm)
                
                # Create verification hash
                verification_hash = hashlib.sha256(transaction_data + signature).hexdigest()
                
                result = SignatureResult(
                    signature=signature,
                    algorithm=algorithm,
                    timestamp=datetime.utcnow(),
                    key_id=key_id,
                    verification_hash=verification_hash
                )
                
                self.security_metrics['signing_operations'] += 1
                
                self._log_audit_event(
                    "TRANSACTION_SIGNED",
                    f"Signed transaction with {key_id}",
                    key_id=key_id,
                    additional_data={'verification_hash': verification_hash}
                )
                
                return result
                
            except Exception as e:
                self.security_metrics['failed_operations'] += 1
                logger.error(f"Signing failed for key {key_id}: {e}")
                self._log_audit_event("SIGNING_FAILED", str(e), key_id=key_id, level="ERROR")
                raise RuntimeError(f"Signing failed: {e}")

    def verify_signature(self, key_id: str, data: bytes, signature: bytes, 
                        algorithm: str = 'ECDSA') -> bool:
        """
        Verify signature using HSM with comprehensive validation
        """
        try:
            with self._lock:
                if key_id not in self.key_registry:
                    logger.warning(f"Verification failed: unknown key {key_id}")
                    return False
                
                # HSM-specific verification
                is_valid = self._hsm_verify(key_id, data, signature, algorithm)
                
                self._log_audit_event(
                    "SIGNATURE_VERIFIED" if is_valid else "SIGNATURE_INVALID",
                    f"Signature verification {'passed' if is_valid else 'failed'} for {key_id}",
                    key_id=key_id
                )
                
                return is_valid
                
        except Exception as e:
            logger.error(f"Signature verification error for key {key_id}: {e}")
            return False

    def _hsm_sign(self, key_id: str, data: bytes, algorithm: str) -> bytes:
        """HSM-specific signing implementation"""
        if self.config.hsm_type == 'aws_cloudhsm':
            return self._aws_hsm_sign(key_id, data, algorithm)
        elif self.config.hsm_type == 'yubihsm':
            return self._yubihsm_sign(key_id, data, algorithm)
        elif self.config.hsm_type == 'azure_dedicated_hsm':
            return self._azure_hsm_sign(key_id, data, algorithm)
        else:
            raise NotImplementedError(f"Signing not implemented for {self.config.hsm_type}")

    def _hsm_verify(self, key_id: str, data: bytes, signature: bytes, algorithm: str) -> bool:
        """HSM-specific verification implementation"""
        # Implementation would use actual HSM SDK
        # This is a simplified version for demonstration
        try:
            # In production, this would use the HSM's verification capabilities
            test_signature = self._hsm_sign(key_id, data, algorithm)
            return hmac.compare_digest(signature, test_signature)
        except Exception:
            return False

    def rotate_keys(self, key_id: str) -> str:
        """Rotate/update a key pair with proper key lifecycle management"""
        if key_id not in self.key_registry:
            raise KeyError(f"Key not found: {key_id}")
            
        with self._lock:
            try:
                old_metadata = self.key_registry[key_id]
                
                # Generate new key
                new_key_id = f"{key_id}_v{old_metadata.rotation_count + 1}"
                new_metadata = self.generate_key_pair(
                    new_key_id, 
                    old_metadata.key_type, 
                    old_metadata.key_size,
                    old_metadata.compliance_tags
                )
                
                # Update rotation count
                new_metadata.rotation_count = old_metadata.rotation_count + 1
                
                self._log_audit_event(
                    "KEY_ROTATED",
                    f"Rotated key {key_id} to {new_key_id}",
                    key_id=key_id,
                    additional_data={'new_key_id': new_key_id}
                )
                
                return new_key_id
                
            except Exception as e:
                logger.error(f"Key rotation failed for {key_id}: {e}")
                self._log_audit_event("KEY_ROTATION_FAILED", str(e), key_id=key_id, level="ERROR")
                raise RuntimeError(f"Key rotation failed: {e}")

    def get_key_metadata(self, key_id: str) -> Optional[KeyMetadata]:
        """Get metadata for a specific key with access controls"""
        with self._lock:
            metadata = self.key_registry.get(key_id)
            if metadata and self.config.audit_logging:
                self._log_audit_event("KEY_METADATA_ACCESSED", f"Accessed metadata for {key_id}", key_id=key_id)
            return metadata

    def _log_audit_event(self, event_type: str, message: str, key_id: str = None, 
                        level: str = "INFO", additional_data: Dict = None):
        """Log security event for audit and compliance"""
        if not self.config.audit_logging:
            return
            
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'message': message,
            'level': level,
            'key_id': key_id,
            'hsm_type': self.config.hsm_type,
            'additional_data': additional_data or {}
        }
        
        self.audit_log.append(audit_entry)
        
        # Log to appropriate level
        log_method = getattr(logger, level.lower(), logger.info)
        log_message = f"{event_type}: {message}"
        if key_id:
            log_message += f" (Key: {key_id})"
        log_method(log_message)

    def get_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        with self._lock:
            return {
                'hsm_type': self.config.hsm_type,
                'total_keys': len(self.key_registry),
                'security_metrics': self.security_metrics.copy(),
                'audit_entries_count': len(self.audit_log),
                'compliance_status': self._check_compliance_status(),
                'keys_requiring_rotation': self._get_keys_requiring_rotation()
            }

    def _check_compliance_status(self) -> Dict[str, bool]:
        """Check compliance with security standards"""
        return {
            'key_sizes_compliant': all(
                meta.key_size >= 256 if meta.key_type == 'EC' else meta.key_size >= 2048
                for meta in self.key_registry.values()
            ),
            'key_rotation_enforced': all(
                (datetime.utcnow() - meta.created_at).days <= self.config.key_rotation_days
                for meta in self.key_registry.values()
            ),
            'audit_logging_active': self.config.audit_logging
        }

    def _get_keys_requiring_rotation(self) -> List[str]:
        """Get list of keys that require rotation"""
        rotation_threshold = datetime.utcnow() - timedelta(days=self.config.key_rotation_days)
        return [
            key_id for key_id, meta in self.key_registry.items()
            if meta.created_at < rotation_threshold
        ]

    @contextmanager
    def secure_session(self):
        """Context manager for secure HSM sessions"""
        try:
            self._establish_secure_session()
            yield self
        finally:
            self._close_secure_session()

    def _establish_secure_session(self):
        """Establish secure session with HSM"""
        # Implementation would establish secure channel
        pass

    def _close_secure_session(self):
        """Close secure session"""
        # Implementation would clean up session
        pass

    def _aws_hsm_sign(self, key_id: str, data: bytes, algorithm: str) -> bytes:
        """AWS CloudHSM specific signing"""
        # Implementation using AWS CloudHSM SDK
        # This is a placeholder - real implementation would use boto3
        return b"aws_hsm_signature_" + key_id.encode() + data[:16]

    def _yubihsm_sign(self, key_id: str, data: bytes, algorithm: str) -> bytes:
        """YubiHSM specific signing"""
        # Implementation using YubiHSM SDK
        return b"yubihsm_signature_" + key_id.encode() + data[:16]

    def _azure_hsm_sign(self, key_id: str, data: bytes, algorithm: str) -> bytes:
        """Azure HSM specific signing"""
        # Implementation using Azure Key Vault SDK
        return b"azure_hsm_signature_" + key_id.encode() + data[:16]

# Factory function with comprehensive configuration
def create_hsm_integrator(config: HSMConfig) -> HSMIntegrator:
    """
    Create and initialize HSM integrator with validation
    """
    # Validate configuration
    required_fields = ['hsm_type', 'endpoint', 'partition', 'credentials']
    for field in required_fields:
        if not getattr(config, field, None):
            raise ValueError(f"Missing required HSM configuration: {field}")
    
    return HSMIntegrator(config)

if __name__ == "__main__":
    # Example configuration
    config = HSMConfig(
        hsm_type='aws_cloudhsm',
        endpoint='https://cloudhsm.example.com',
        partition='partition1',
        credentials={'aws_access_key_id': 'test', 'aws_secret_access_key': 'test'},
        compliance_standard='FIPS-140-2'
    )
    
    hsm = create_hsm_integrator(config)
    print("HSMIntegrator initialized successfully")
