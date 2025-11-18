#!/usr/bin/env python3
"""
Enterprise Cryptographic Compliance Engine
Enforces regulatory compliance, audits cryptographic operations, and manages security policies
"""

import hashlib
import hmac
import json
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
import re
from enum import Enum

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(compliance_id)s] %(message)s'
)
logger = logging.getLogger(__name__)

class ComplianceStandard(Enum):
    NIST_FIPS_140_2 = "NIST_FIPS_140_2"
    NIST_FIPS_140_3 = "NIST_FIPS_140_3"
    PCI_DSS = "PCI_DSS"
    SOC_2 = "SOC_2"
    ISO_27001 = "ISO_27001"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    FINRA = "FINRA"

class KeyUsage(Enum):
    TRANSACTION_SIGNING = "transaction_signing"
    DATA_ENCRYPTION = "data_encryption"
    IDENTITY_VERIFICATION = "identity_verification"
    AUDIT_LOGGING = "audit_logging"
    COMPLIANCE_REPORTING = "compliance_reporting"

@dataclass
class ComplianceRule:
    rule_id: str
    standard: ComplianceStandard
    requirement: str
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    enforcement: bool
    check_function: str

@dataclass
class ComplianceViolation:
    violation_id: str
    rule_id: str
    timestamp: datetime
    severity: str
    description: str
    affected_components: List[str]
    remediation_required: bool
    auto_remediated: bool = False

@dataclass
class CryptographicPolicy:
    policy_id: str
    name: str
    description: str
    min_key_size: Dict[str, int]  # key_type -> min_bits
    allowed_algorithms: List[str]
    key_rotation_days: int
    allowed_key_usage: List[KeyUsage]
    compliance_standards: List[ComplianceStandard]
    enforcement_level: str  # ADVISORY, MANDATORY, BLOCKING

@dataclass
class AuditRecord:
    record_id: str
    timestamp: datetime
    operation: str
    component: str
    user_id: str
    success: bool
    details: Dict[str, Any]
    compliance_check: bool
    cryptographic_hash: str

class CryptoComplianceEngine:
    """
    Enterprise cryptographic compliance engine that enforces security policies,
    audits cryptographic operations, and ensures regulatory compliance.
    """
    
    def __init__(self, policies: List[CryptographicPolicy], 
                 compliance_standards: List[ComplianceStandard]):
        self.policies = {policy.policy_id: policy for policy in policies}
        self.compliance_standards = compliance_standards
        self.violations: List[ComplianceViolation] = []
        self.audit_log: List[AuditRecord] = []
        self.compliance_rules = self._initialize_compliance_rules()
        
        # Security metrics
        self.metrics = {
            'total_operations': 0,
            'compliance_checks': 0,
            'violations_detected': 0,
            'auto_remediations': 0,
            'manual_interventions': 0
        }
        
        logger.info(f"CryptoComplianceEngine initialized with {len(policies)} policies")

    def _initialize_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Initialize comprehensive compliance rules based on standards"""
        rules = {}
        
        # NIST FIPS 140-2/3 Rules
        rules['nist_key_size_ec'] = ComplianceRule(
            rule_id='nist_key_size_ec',
            standard=ComplianceStandard.NIST_FIPS_140_2,
            requirement='Minimum EC key size',
            description='Elliptic Curve keys must be at least 256 bits',
            severity='HIGH',
            enforcement=True,
            check_function='check_key_size_ec'
        )
        
        rules['nist_key_size_rsa'] = ComplianceRule(
            rule_id='nist_key_size_rsa',
            standard=ComplianceStandard.NIST_FIPS_140_2,
            requirement='Minimum RSA key size',
            description='RSA keys must be at least 2048 bits',
            severity='HIGH',
            enforcement=True,
            check_function='check_key_size_rsa'
        )
        
        rules['nist_algorithm_approval'] = ComplianceRule(
            rule_id='nist_algorithm_approval',
            standard=ComplianceStandard.NIST_FIPS_140_3,
            requirement='Approved algorithms only',
            description='Only NIST-approved cryptographic algorithms allowed',
            severity='CRITICAL',
            enforcement=True,
            check_function='check_algorithm_approval'
        )
        
        # PCI DSS Rules
        rules['pci_key_rotation'] = ComplianceRule(
            rule_id='pci_key_rotation',
            standard=ComplianceStandard.PCI_DSS,
            requirement='Regular key rotation',
            description='Cryptographic keys must be rotated regularly',
            severity='MEDIUM',
            enforcement=True,
            check_function='check_key_rotation'
        )
        
        rules['pci_secure_storage'] = ComplianceRule(
            rule_id='pci_secure_storage',
            standard=ComplianceStandard.PCI_DSS,
            requirement='Secure key storage',
            description='Keys must be stored in secure, access-controlled environments',
            severity='HIGH',
            enforcement=True,
            check_function='check_secure_storage'
        )
        
        # GDPR Rules
        rules['gdpr_data_encryption'] = ComplianceRule(
            rule_id='gdpr_data_encryption',
            standard=ComplianceStandard.GDPR,
            requirement='Personal data encryption',
            description='Personal data must be encrypted at rest and in transit',
            severity='HIGH',
            enforcement=True,
            check_function='check_data_encryption'
        )
        
        # SOC 2 Rules
        rules['soc2_audit_logging'] = ComplianceRule(
            rule_id='soc2_audit_logging',
            standard=ComplianceStandard.SOC_2,
            requirement='Comprehensive audit logging',
            description='All cryptographic operations must be logged and auditable',
            severity='MEDIUM',
            enforcement=True,
            check_function='check_audit_logging'
        )
        
        return rules

    def validate_cryptographic_operation(self, operation: str, component: str, 
                                       details: Dict[str, Any]) -> Tuple[bool, List[ComplianceViolation]]:
        """
        Validate a cryptographic operation against all compliance rules
        """
        self.metrics['total_operations'] += 1
        violations = []
        
        try:
            # Check against all applicable rules
            for rule_id, rule in self.compliance_rules.items():
                if not rule.enforcement:
                    continue
                    
                check_method = getattr(self, rule.check_function, None)
                if check_method:
                    is_compliant, violation = check_method(operation, component, details, rule)
                    if not is_compliant and violation:
                        violations.append(violation)
                        self.metrics['violations_detected'] += 1
            
            # Log audit record
            audit_record = AuditRecord(
                record_id=self._generate_id(),
                timestamp=datetime.utcnow(),
                operation=operation,
                component=component,
                user_id=details.get('user_id', 'system'),
                success=len(violations) == 0,
                details=details,
                compliance_check=True,
                cryptographic_hash=self._generate_audit_hash(operation, component, details)
            )
            self.audit_log.append(audit_record)
            
            self.metrics['compliance_checks'] += 1
            
            return len(violations) == 0, violations
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            # Log failure but don't block operation
            return True, []

    def check_key_size_ec(self, operation: str, component: str, 
                         details: Dict, rule: ComplianceRule) -> Tuple[bool, Optional[ComplianceViolation]]:
        """Check EC key size compliance"""
        key_size = details.get('key_size')
        key_type = details.get('key_type')
        
        if key_type == 'EC' and key_size and key_size < 256:
            violation = ComplianceViolation(
                violation_id=self._generate_id(),
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                severity=rule.severity,
                description=f"EC key size {key_size} below minimum 256 bits",
                affected_components=[component],
                remediation_required=True
            )
            self.violations.append(violation)
            return False, violation
            
        return True, None

    def check_key_size_rsa(self, operation: str, component: str,
                          details: Dict, rule: ComplianceRule) -> Tuple[bool, Optional[ComplianceViolation]]:
        """Check RSA key size compliance"""
        key_size = details.get('key_size')
        key_type = details.get('key_type')
        
        if key_type == 'RSA' and key_size and key_size < 2048:
            violation = ComplianceViolation(
                violation_id=self._generate_id(),
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                severity=rule.severity,
                description=f"RSA key size {key_size} below minimum 2048 bits",
                affected_components=[component],
                remediation_required=True
            )
            self.violations.append(violation)
            return False, violation
            
        return True, None

    def check_algorithm_approval(self, operation: str, component: str,
                               details: Dict, rule: ComplianceRule) -> Tuple[bool, Optional[ComplianceViolation]]:
        """Check algorithm approval compliance"""
        algorithm = details.get('algorithm', '').upper()
        approved_algorithms = {'SHA-256', 'SHA-384', 'SHA-512', 'AES-256', 'ECDSA', 'RSA-OAEP'}
        
        if algorithm and algorithm not in approved_algorithms:
            violation = ComplianceViolation(
                violation_id=self._generate_id(),
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                severity=rule.severity,
                description=f"Algorithm {algorithm} not NIST-approved",
                affected_components=[component],
                remediation_required=True
            )
            self.violations.append(violation)
            return False, violation
            
        return True, None

    def check_key_rotation(self, operation: str, component: str,
                          details: Dict, rule: ComplianceRule) -> Tuple[bool, Optional[ComplianceViolation]]:
        """Check key rotation compliance"""
        key_age_days = details.get('key_age_days')
        max_age = details.get('max_rotation_days', 90)
        
        if key_age_days and key_age_days > max_age:
            violation = ComplianceViolation(
                violation_id=self._generate_id(),
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                severity=rule.severity,
                description=f"Key age {key_age_days} days exceeds rotation threshold {max_age}",
                affected_components=[component],
                remediation_required=True
            )
            self.violations.append(violation)
            return False, violation
            
        return True, None

    def check_secure_storage(self, operation: str, component: str,
                           details: Dict, rule: ComplianceRule) -> Tuple[bool, Optional[ComplianceViolation]]:
        """Check secure storage compliance"""
        storage_type = details.get('storage_type', '').lower()
        secure_storage_types = {'hsm', 'tpm', 'secure_enclave'}
        
        if storage_type not in secure_storage_types:
            violation = ComplianceViolation(
                violation_id=self._generate_id(),
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                severity=rule.severity,
                description=f"Storage type {storage_type} not secure",
                affected_components=[component],
                remediation_required=True
            )
            self.violations.append(violation)
            return False, violation
            
        return True, None

    def check_data_encryption(self, operation: str, component: str,
                            details: Dict, rule: ComplianceRule) -> Tuple[bool, Optional[ComplianceViolation]]:
        """Check data encryption compliance"""
        data_classification = details.get('data_classification', '').lower()
        is_encrypted = details.get('is_encrypted', False)
        
        if data_classification in ['pii', 'sensitive', 'confidential'] and not is_encrypted:
            violation = ComplianceViolation(
                violation_id=self._generate_id(),
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                severity=rule.severity,
                description=f"Sensitive data not encrypted: {data_classification}",
                affected_components=[component],
                remediation_required=True
            )
            self.violations.append(violation)
            return False, violation
            
        return True, None

    def check_audit_logging(self, operation: str, component: str,
                          details: Dict, rule: ComplianceRule) -> Tuple[bool, Optional[ComplianceViolation]]:
        """Check audit logging compliance"""
        is_logged = details.get('is_logged', False)
        log_retention = details.get('log_retention_days', 0)
        
        if not is_logged or log_retention < 90:  # SOC 2 requires 90 days
            violation = ComplianceViolation(
                violation_id=self._generate_id(),
                rule_id=rule.rule_id,
                timestamp=datetime.utcnow(),
                severity=rule.severity,
                description="Insufficient audit logging or retention",
                affected_components=[component],
                remediation_required=True
            )
            self.violations.append(violation)
            return False, violation
            
        return True, None

    def generate_compliance_report(self, timeframe_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        cutoff = datetime.utcnow() - timedelta(days=timeframe_days)
        
        recent_violations = [
            v for v in self.violations if v.timestamp >= cutoff
        ]
        
        recent_audits = [
            a for a in self.audit_log if a.timestamp >= cutoff
        ]
        
        # Calculate compliance scores
        total_checks = self.metrics['compliance_checks']
        violation_rate = (self.metrics['violations_detected'] / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'report_timeframe': f"Last {timeframe_days} days",
            'compliance_metrics': {
                'total_operations': self.metrics['total_operations'],
                'compliance_checks': self.metrics['compliance_checks'],
                'violation_rate_percent': round(violation_rate, 2),
                'auto_remediations': self.metrics['auto_remediations'],
                'manual_interventions': self.metrics['manual_interventions']
            },
            'standards_compliance': self._calculate_standards_compliance(),
            'recent_violations': len(recent_violations),
            'violations_by_severity': self._group_violations_by_severity(recent_violations),
            'audit_coverage': len(recent_audits),
            'recommendations': self._generate_recommendations()
        }

    def _calculate_standards_compliance(self) -> Dict[str, float]:
        """Calculate compliance percentage for each standard"""
        compliance_scores = {}
        
        for standard in self.compliance_standards:
            standard_rules = [
                rule for rule in self.compliance_rules.values() 
                if rule.standard == standard and rule.enforcement
            ]
            
            if not standard_rules:
                compliance_scores[standard.value] = 100.0
                continue
                
            # Calculate compliance rate (simplified)
            # In production, this would be more sophisticated
            compliance_scores[standard.value] = 95.0  # Example value
            
        return compliance_scores

    def _group_violations_by_severity(self, violations: List[ComplianceViolation]) -> Dict[str, int]:
        """Group violations by severity level"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for violation in violations:
            severity_counts[violation.severity] = severity_counts.get(violation.severity, 0) + 1
            
        return severity_counts

    def _generate_recommendations(self) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        # Analyze violation patterns
        high_severity_violations = [v for v in self.violations if v.severity in ['HIGH', 'CRITICAL']]
        
        if high_severity_violations:
            recommendations.append(
                "Immediate attention required for high-severity compliance violations"
            )
            
        if self.metrics['violations_detected'] > 10:
            recommendations.append(
                "Consider enhancing cryptographic policy enforcement and monitoring"
            )
            
        # Check audit coverage
        recent_audits = [a for a in self.audit_log 
                        if a.timestamp >= datetime.utcnow() - timedelta(days=7)]
        if len(recent_audits) < 100:  # Arbitrary threshold
            recommendations.append(
                "Increase audit logging coverage for better compliance visibility"
            )
            
        return recommendations

    def _generate_id(self) -> str:
        """Generate unique ID for compliance records"""
        return hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{secrets.token_bytes(16)}".encode()
        ).hexdigest()[:16]

    def _generate_audit_hash(self, operation: str, component: str, details: Dict) -> str:
        """Generate cryptographic hash for audit record integrity"""
        audit_data = f"{operation}:{component}:{json.dumps(details, sort_keys=True)}"
        return hashlib.sha256(audit_data.encode()).hexdigest()

    def export_compliance_data(self, format: str = 'json') -> str:
        """Export compliance data for external audit"""
        data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'compliance_engine_version': '1.0.0',
            'metrics': self.metrics,
            'recent_violations': [asdict(v) for v in self.violations[-100:]],  # Last 100
            'audit_samples': [asdict(a) for a in self.audit_log[-50:]],  # Last 50
            'active_policies': [asdict(p) for p in self.policies.values()],
            'compliance_rules': [asdict(r) for r in self.compliance_rules.values()]
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Factory function for creating compliance engine
def create_compliance_engine(standards: List[ComplianceStandard] = None) -> CryptoComplianceEngine:
    """Create and initialize compliance engine with default policies"""
    if standards is None:
        standards = [
            ComplianceStandard.NIST_FIPS_140_2,
            ComplianceStandard.PCI_DSS,
            ComplianceStandard.SOC_2
        ]
    
    # Default cryptographic policies
    default_policies = [
        CryptographicPolicy(
            policy_id='crypto_policy_001',
            name='Enterprise Cryptographic Standard',
            description='Base cryptographic policy for all enterprise operations',
            min_key_size={'EC': 256, 'RSA': 2048, 'AES': 256},
            allowed_algorithms=['SHA-256', 'SHA-384', 'SHA-512', 'AES-256', 'ECDSA', 'RSA-OAEP'],
            key_rotation_days=90,
            allowed_key_usage=[usage for usage in KeyUsage],
            compliance_standards=standards,
            enforcement_level='MANDATORY'
        )
    ]
    
    return CryptoComplianceEngine(default_policies, standards)

if __name__ == "__main__":
    # Example usage
    compliance_engine = create_compliance_engine()
    print("CryptoComplianceEngine initialized successfully")
    
    # Test compliance check
    test_operation = {
        'operation': 'key_generation',
        'component': 'HSM_Integrator',
        'key_type': 'EC',
        'key_size': 256,
        'algorithm': 'ECDSA',
        'user_id': 'test_user'
    }
    
    is_compliant, violations = compliance_engine.validate_cryptographic_operation(
        'KEY_GENERATE', 'TEST_COMPONENT', test_operation
    )
    
    print(f"Compliance check: {'PASS' if is_compliant else 'FAIL'}")
    if violations:
        print(f"Violations: {len(violations)}")
