"""
AI-NEXUS v5.0 - INSURANCE MANAGER MODULE
Advanced DeFi Insurance and Risk Mitigation System
Smart contract insurance, protocol failure protection, and capital guarantee mechanisms
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import asyncio
import warnings
warnings.filterwarnings('ignore')

class InsuranceType(Enum):
    SMART_CONTRACT = "smart_contract"
    PROTOCOL_FAILURE = "protocol_failure"
    STABLECOIN_DEpeg = "stablecoin_depeg"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    FRONT_RUNNING = "front_running"
    ORACLE_MANIPULATION = "oracle_manipulation"
    BRIDGE_FAILURE = "bridge_failure"

class CoverageTier(Enum):
    BASIC = "basic"  # 50% coverage
    STANDARD = "standard"  # 75% coverage
    PREMIUM = "premium"  # 90% coverage
    ENTERPRISE = "enterprise"  # 95% coverage

@dataclass
class InsurancePolicy:
    policy_id: str
    insurance_type: InsuranceType
    coverage_tier: CoverageTier
    insured_amount: float
    premium_rate: float
    coverage_percentage: float
    deductible: float
    start_date: datetime
    end_date: datetime
    status: str
    metadata: Dict[str, Any]

@dataclass
class InsuranceClaim:
    claim_id: str
    policy_id: str
    incident_type: str
    claimed_amount: float
    incident_details: Dict[str, Any]
    submission_date: datetime
    status: str
    payout_amount: float
    investigation_result: Dict[str, Any]

@dataclass
class RiskAssessment:
    assessment_id: str
    timestamp: datetime
    protocol_risk: float
    market_risk: float
    technical_risk: float
    counterparty_risk: float
    overall_risk: float
    recommended_coverage: CoverageTier
    premium_suggestion: float

class InsuranceManager:
    """
    Advanced DeFi insurance management system
    Provides comprehensive coverage for various DeFi risks
    """
    
    def __init__(self):
        self.active_policies = {}
        self.insurance_providers = {}
        self.claim_history = deque(maxlen=10000)
        self.risk_assessments = deque(maxlen=5000)
        
        # Insurance parameters
        self.insurance_params = {
            'base_premium_rates': {
                InsuranceType.SMART_CONTRACT: 0.025,  # 2.5% annual
                InsuranceType.PROTOCOL_FAILURE: 0.015,
                InsuranceType.STABLECOIN_DEpeg: 0.010,
                InsuranceType.LIQUIDITY_PROVIDER: 0.020,
                InsuranceType.FRONT_RUNNING: 0.030,
                InsuranceType.ORACLE_MANIPULATION: 0.025,
                InsuranceType.BRIDGE_FAILURE: 0.035
            },
            'coverage_tiers': {
                CoverageTier.BASIC: 0.50,
                CoverageTier.STANDARD: 0.75,
                CoverageTier.PREMIUM: 0.90,
                CoverageTier.ENTERPRISE: 0.95
            },
            'deductible_rates': {
                CoverageTier.BASIC: 0.10,
                CoverageTier.STANDARD: 0.05,
                CoverageTier.PREMIUM: 0.02,
                CoverageTier.ENTERPRISE: 0.01
            },
            'max_coverage_per_protocol': 10000000,  # $10M
            'risk_adjustment_factor': 1.5
        }
        
        # Risk models
        self.risk_models = {}
        self.protocol_risk_scores = {}
        
        # Performance metrics
        self.performance_metrics = {
            'total_premiums_collected': 0.0,
            'total_claims_paid': 0.0,
            'active_policies_count': 0,
            'claims_ratio': 0.0,
            'average_claim_amount': 0.0
        }
        
        # Initialize insurance providers
        self._initialize_insurance_providers()
        self._initialize_risk_models()
    
    def _initialize_insurance_providers(self):
        """Initialize insurance providers and their parameters"""
        
        self.insurance_providers = {
            'nexus_mutual': {
                'name': 'Nexus Mutual',
                'coverage_types': [InsuranceType.SMART_CONTRACT, InsuranceType.PROTOCOL_FAILURE],
                'max_coverage': 5000000,
                'credit_rating': 'AA',
                'premium_multiplier': 1.0
            },
            'unslashed_finance': {
                'name': 'Unslashed Finance',
                'coverage_types': [InsuranceType.SMART_CONTRACT, InsuranceType.ORACLE_MANIPULATION],
                'max_coverage': 3000000,
                'credit_rating': 'A',
                'premium_multiplier': 1.1
            },
            'armor_fi': {
                'name': 'ArmorFi',
                'coverage_types': [InsuranceType.PROTOCOL_FAILURE, InsuranceType.FRONT_RUNNING],
                'max_coverage': 2000000,
                'credit_rating': 'BBB',
                'premium_multiplier': 1.2
            },
            'bridge_mutual': {
                'name': 'Bridge Mutual',
                'coverage_types': [InsuranceType.BRIDGE_FAILURE, InsuranceType.STABLECOIN_DEpeg],
                'max_coverage': 1500000,
                'credit_rating': 'A',
                'premium_multiplier': 1.15
            }
        }
    
    def _initialize_risk_models(self):
        """Initialize risk assessment models"""
        
        self.risk_models = {
            'protocol_risk': {
                'factors': ['tvl', 'age', 'audit_status', 'team_reputation', 'governance_score'],
                'weights': [0.3, 0.15, 0.25, 0.2, 0.1]
            },
            'market_risk': {
                'factors': ['volatility', 'liquidity_depth', 'correlation_market', 'sentiment_score'],
                'weights': [0.4, 0.3, 0.2, 0.1]
            },
            'technical_risk': {
                'factors': ['code_complexity', 'upgrade_frequency', 'bug_bounty', 'test_coverage'],
                'weights': [0.35, 0.2, 0.25, 0.2]
            },
            'counterparty_risk': {
                'factors': ['centralization', 'custodian_rating', 'insurance_coverage', 'legal_structure'],
                'weights': [0.4, 0.3, 0.2, 0.1]
            }
        }
    
    async def assess_risk(self, protocol_data: Dict[str, Any], 
                         market_data: Dict[str, Any]) -> RiskAssessment:
        """Comprehensive risk assessment for insurance underwriting"""
        
        # Calculate individual risk components
        protocol_risk = await self._calculate_protocol_risk(protocol_data)
        market_risk = await self._calculate_market_risk(market_data)
        technical_risk = await self._calculate_technical_risk(protocol_data)
        counterparty_risk = await self._calculate_counterparty_risk(protocol_data)
        
        # Calculate overall risk score
        overall_risk = (
            protocol_risk * 0.35 +
            market_risk * 0.25 +
            technical_risk * 0.25 +
            counterparty_risk * 0.15
        )
        
        # Determine recommended coverage tier
        recommended_coverage = self._determine_coverage_tier(overall_risk)
        
        # Calculate premium suggestion
        premium_suggestion = self._calculate_premium_suggestion(
            overall_risk, recommended_coverage
        )
        
        assessment = RiskAssessment(
            assessment_id=f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now(),
            protocol_risk=protocol_risk,
            market_risk=market_risk,
            technical_risk=technical_risk,
            counterparty_risk=counterparty_risk,
            overall_risk=overall_risk,
            recommended_coverage=recommended_coverage,
            premium_suggestion=premium_suggestion
        )
        
        self.risk_assessments.append(assessment)
        
        return assessment
    
    async def _calculate_protocol_risk(self, protocol_data: Dict[str, Any]) -> float:
        """Calculate protocol-specific risk score"""
        
        risk_model = self.risk_models['protocol_risk']
        factors = risk_model['factors']
        weights = risk_model['weights']
        
        risk_score = 0.0
        
        for factor, weight in zip(factors, weights):
            factor_value = self._get_protocol_factor_value(protocol_data, factor)
            risk_score += factor_value * weight
        
        return min(1.0, risk_score)
    
    async def _calculate_market_risk(self, market_data: Dict[str, Any]) -> float:
        """Calculate market risk score"""
        
        risk_model = self.risk_models['market_risk']
        factors = risk_model['factors']
        weights = risk_model['weights']
        
        risk_score = 0.0
        
        for factor, weight in zip(factors, weights):
            factor_value = self._get_market_factor_value(market_data, factor)
            risk_score += factor_value * weight
        
        return min(1.0, risk_score)
    
    async def _calculate_technical_risk(self, protocol_data: Dict[str, Any]) -> float:
        """Calculate technical risk score"""
        
        risk_model = self.risk_models['technical_risk']
        factors = risk_model['factors']
        weights = risk_model['weights']
        
        risk_score = 0.0
        
        for factor, weight in zip(factors, weights):
            factor_value = self._get_technical_factor_value(protocol_data, factor)
            risk_score += factor_value * weight
        
        return min(1.0, risk_score)
    
    async def _calculate_counterparty_risk(self, protocol_data: Dict[str, Any]) -> float:
        """Calculate counterparty risk score"""
        
        risk_model = self.risk_models['counterparty_risk']
        factors = risk_model['factors']
        weights = risk_model['weights']
        
        risk_score = 0.0
        
        for factor, weight in zip(factors, weights):
            factor_value = self._get_counterparty_factor_value(protocol_data, factor)
            risk_score += factor_value * weight
        
        return min(1.0, risk_score)
    
    def _get_protocol_factor_value(self, protocol_data: Dict[str, Any], factor: str) -> float:
        """Get value for protocol risk factor"""
        
        if factor == 'tvl':
            tvl = protocol_data.get('tvl', 0)
            # Higher TVL generally means lower risk (up to a point)
            return max(0.1, 1.0 - min(1.0, tvl / 1000000000))  # Normalize to 0-1
        
        elif factor == 'age':
            age_days = protocol_data.get('age_days', 0)
            # Older protocols are generally more established
            return max(0.3, 1.0 - min(1.0, age_days / 365))
        
        elif factor == 'audit_status':
            audits = protocol_data.get('audits', [])
            audit_score = len(audits) * 0.2
            return max(0.1, 1.0 - min(1.0, audit_score))
        
        elif factor == 'team_reputation':
            reputation = protocol_data.get('team_reputation', 0.5)
            return 1.0 - reputation  # Invert so higher reputation = lower risk
        
        elif factor == 'governance_score':
            governance = protocol_data.get('governance_score', 0.5)
            return 1.0 - governance
        
        return 0.5
    
    def _get_market_factor_value(self, market_data: Dict[str, Any], factor: str) -> float:
        """Get value for market risk factor"""
        
        if factor == 'volatility':
            volatility = market_data.get('volatility_30d', 0.5)
            return min(1.0, volatility * 2)
        
        elif factor == 'liquidity_depth':
            liquidity = market_data.get('liquidity_depth', 0)
            return max(0.1, 1.0 - min(1.0, liquidity / 10000000))
        
        elif factor == 'correlation_market':
            correlation = market_data.get('correlation_btc', 0.5)
            return abs(correlation)  # High correlation can be risky
        
        elif factor == 'sentiment_score':
            sentiment = market_data.get('market_sentiment', 0.5)
            return 1.0 - sentiment  # Lower sentiment = higher risk
        
        return 0.5
    
    def _get_technical_factor_value(self, protocol_data: Dict[str, Any], factor: str) -> float:
        """Get value for technical risk factor"""
        
        if factor == 'code_complexity':
            complexity = protocol_data.get('code_complexity', 0.5)
            return complexity
        
        elif factor == 'upgrade_frequency':
            upgrades = protocol_data.get('upgrade_frequency', 0)
            # Moderate upgrade frequency is best
            if upgrades < 2:
                return 0.7  # Infrequent updates can be risky
            elif upgrades > 10:
                return 0.8  # Too frequent updates can be risky
            else:
                return 0.3
        
        elif factor == 'bug_bounty':
            bounty = protocol_data.get('bug_bounty_size', 0)
            return max(0.1, 1.0 - min(1.0, bounty / 1000000))
        
        elif factor == 'test_coverage':
            coverage = protocol_data.get('test_coverage', 0.5)
            return 1.0 - coverage  # Higher coverage = lower risk
        
        return 0.5
    
    def _get_counterparty_factor_value(self, protocol_data: Dict[str, Any], factor: str) -> float:
        """Get value for counterparty risk factor"""
        
        if factor == 'centralization':
            centralization = protocol_data.get('centralization_score', 0.5)
            return centralization
        
        elif factor == 'custodian_rating':
            rating = protocol_data.get('custodian_rating', 0.5)
            return 1.0 - rating
        
        elif factor == 'insurance_coverage':
            coverage = protocol_data.get('existing_insurance', 0)
            return max(0.1, 1.0 - min(1.0, coverage / 1000000))
        
        elif factor == 'legal_structure':
            structure = protocol_data.get('legal_structure_score', 0.5)
            return 1.0 - structure
        
        return 0.5
    
    def _determine_coverage_tier(self, overall_risk: float) -> CoverageTier:
        """Determine appropriate coverage tier based on risk"""
        
        if overall_risk < 0.3:
            return CoverageTier.ENTERPRISE
        elif overall_risk < 0.5:
            return CoverageTier.PREMIUM
        elif overall_risk < 0.7:
            return CoverageTier.STANDARD
        else:
            return CoverageTier.BASIC
    
    def _calculate_premium_suggestion(self, overall_risk: float, 
                                   coverage_tier: CoverageTier) -> float:
        """Calculate premium suggestion based on risk and coverage"""
        
        base_premium = overall_risk * 0.05  # Base 5% for high risk
        
        # Adjust for coverage tier
        tier_multipliers = {
            CoverageTier.BASIC: 0.8,
            CoverageTier.STANDARD: 1.0,
            CoverageTier.PREMIUM: 1.3,
            CoverageTier.ENTERPRISE: 1.6
        }
        
        premium = base_premium * tier_multipliers[coverage_tier]
        
        return min(0.15, max(0.005, premium))  # Cap between 0.5% and 15%
    
    async def purchase_insurance(self, 
                               insurance_type: InsuranceType,
                               coverage_tier: CoverageTier,
                               insured_amount: float,
                               protocol_data: Dict[str, Any],
                               market_data: Dict[str, Any]) -> InsurancePolicy:
        """Purchase insurance policy"""
        
        # Risk assessment
        risk_assessment = await self.assess_risk(protocol_data, market_data)
        
        # Calculate premium
        base_premium_rate = self.insurance_params['base_premium_rates'][insurance_type]
        risk_adjusted_premium = base_premium_rate * (1 + risk_assessment.overall_risk * 2)
        
        # Calculate coverage percentage
        coverage_percentage = self.insurance_params['coverage_tiers'][coverage_tier]
        
        # Calculate deductible
        deductible_rate = self.insurance_params['deductible_rates'][coverage_tier]
        deductible = insured_amount * deductible_rate
        
        # Find suitable insurance provider
        provider = self._select_insurance_provider(insurance_type, insured_amount)
        
        # Create policy
        policy = InsurancePolicy(
            policy_id=f"policy_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            insurance_type=insurance_type,
            coverage_tier=coverage_tier,
            insured_amount=insured_amount,
            premium_rate=risk_adjusted_premium,
            coverage_percentage=coverage_percentage,
            deductible=deductible,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=365),  # 1 year policy
            status='active',
            metadata={
                'provider': provider['name'],
                'risk_assessment_id': risk_assessment.assessment_id,
                'annual_premium': insured_amount * risk_adjusted_premium,
                'max_payout': insured_amount * coverage_percentage
            }
        )
        
        # Store policy
        self.active_policies[policy.policy_id] = policy
        self.performance_metrics['active_policies_count'] += 1
        self.performance_metrics['total_premiums_collected'] += insured_amount * risk_adjusted_premium
        
        print(f"Insurance policy purchased: {policy.policy_id}")
        print(f"Coverage: {coverage_percentage:.1%} of ${insured_amount:,.2f}")
        print(f"Premium rate: {risk_adjusted_premium:.3%} annually")
        
        return policy
    
    def _select_insurance_provider(self, insurance_type: InsuranceType, 
                                 insured_amount: float) -> Dict[str, Any]:
        """Select appropriate insurance provider"""
        
        suitable_providers = []
        
        for provider_id, provider in self.insurance_providers.items():
            if (insurance_type in provider['coverage_types'] and 
                insured_amount <= provider['max_coverage']):
                suitable_providers.append((provider_id, provider))
        
        if not suitable_providers:
            # Fallback to first provider (would implement more sophisticated logic)
            return list(self.insurance_providers.values())[0]
        
        # Select provider with best credit rating
        credit_ratings = {'AAA': 6, 'AA': 5, 'A': 4, 'BBB': 3, 'BB': 2, 'B': 1}
        
        best_provider = max(suitable_providers, 
                          key=lambda x: credit_ratings.get(x[1]['credit_rating'], 0))
        
        return best_provider[1]
    
    async def submit_claim(self, 
                          policy_id: str,
                          incident_type: str,
                          claimed_amount: float,
                          incident_details: Dict[str, Any]) -> InsuranceClaim:
        """Submit insurance claim"""
        
        policy = self.active_policies.get(policy_id)
        
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        if policy.status != 'active':
            raise ValueError(f"Policy {policy_id} is not active")
        
        # Validate claim against policy
        if not self._is_claim_valid(policy, incident_type, claimed_amount):
            raise ValueError("Claim is not valid for this policy")
        
        # Create claim
        claim = InsuranceClaim(
            claim_id=f"claim_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            policy_id=policy_id,
            incident_type=incident_type,
            claimed_amount=claimed_amount,
            incident_details=incident_details,
            submission_date=datetime.now(),
            status='submitted',
            payout_amount=0.0,
            investigation_result={}
        )
        
        # Start claim investigation
        asyncio.create_task(self._investigate_claim(claim))
        
        self.claim_history.append(claim)
        
        print(f"Insurance claim submitted: {claim.claim_id}")
        print(f"Policy: {policy_id}, Claimed amount: ${claimed_amount:,.2f}")
        
        return claim
    
    def _is_claim_valid(self, policy: InsurancePolicy, incident_type: str, 
                       claimed_amount: float) -> bool:
        """Validate if claim is valid for the policy"""
        
        # Check if incident type is covered
        if incident_type != policy.insurance_type.value:
            return False
        
        # Check if claimed amount is reasonable
        max_claimable = policy.insured_amount * policy.coverage_percentage
        if claimed_amount > max_claimable:
            return False
        
        # Check if claim is within policy period
        if datetime.now() > policy.end_date:
            return False
        
        return True
    
    async def _investigate_claim(self, claim: InsuranceClaim):
        """Investigate insurance claim (asynchronous)"""
        
        print(f"Investigating claim: {claim.claim_id}")
        
        # Simulate investigation process
        await asyncio.sleep(2)  # Simulate investigation time
        
        # Determine claim validity (simplified)
        is_valid = await self._validate_claim_evidence(claim)
        
        if is_valid:
            # Calculate payout
            payout = await self._calculate_payout(claim)
            claim.payout_amount = payout
            claim.status = 'approved'
            claim.investigation_result = {
                'investigation_status': 'completed',
                'valid_claim': True,
                'payout_calculation': f'Calculated based on policy terms',
                'investigator': 'AI-NEXUS_Claims_System'
            }
            
            # Update performance metrics
            self.performance_metrics['total_claims_paid'] += payout
            
            print(f"Claim {claim.claim_id} approved. Payout: ${payout:,.2f}")
            
        else:
            claim.status = 'rejected'
            claim.investigation_result = {
                'investigation_status': 'completed',
                'valid_claim': False,
                'rejection_reason': 'Insufficient evidence or policy violation',
                'investigator': 'AI-NEXUS_Claims_System'
            }
            
            print(f"Claim {claim.claim_id} rejected")
        
        # Update claims ratio
        total_premiums = self.performance_metrics['total_premiums_collected']
        total_claims = self.performance_metrics['total_claims_paid']
        self.performance_metrics['claims_ratio'] = (
            total_claims / total_premiums if total_premiums > 0 else 0.0
        )
    
    async def _validate_claim_evidence(self, claim: InsuranceClaim) -> bool:
        """Validate claim evidence (simplified implementation)"""
        
        # In production, this would involve sophisticated evidence verification
        # For demo, approve 80% of claims
        return np.random.random() < 0.8
    
    async def _calculate_payout(self, claim: InsuranceClaim) -> float:
        """Calculate insurance payout"""
        
        policy = self.active_policies[claim.policy_id]
        
        # Apply deductible
        amount_after_deductible = max(0, claim.claimed_amount - policy.deductible)
        
        # Apply coverage percentage
        payout = amount_after_deductible * policy.coverage_percentage
        
        # Cap at maximum payout
        max_payout = policy.insured_amount * policy.coverage_percentage
        payout = min(payout, max_payout)
        
        return payout
    
    async def get_coverage_recommendations(self, 
                                         portfolio_value: float,
                                         risk_tolerance: str) -> Dict[str, Any]:
        """Get insurance coverage recommendations"""
        
        # Base coverage percentages based on risk tolerance
        base_coverage = {
            'conservative': 0.8,  # 80% coverage
            'moderate': 0.6,      # 60% coverage
            'aggressive': 0.4     # 40% coverage
        }
        
        coverage_pct = base_coverage.get(risk_tolerance, 0.6)
        recommended_coverage = portfolio_value * coverage_pct
        
        # Recommended insurance types based on portfolio composition
        recommended_types = [
            InsuranceType.SMART_CONTRACT,
            InsuranceType.PROTOCOL_FAILURE,
            InsuranceType.STABLECOIN_DEpeg
        ]
        
        return {
            'recommended_coverage_amount': recommended_coverage,
            'coverage_percentage': coverage_pct,
            'recommended_insurance_types': [t.value for t in recommended_types],
            'estimated_annual_premium': recommended_coverage * 0.02,  # 2% estimate
            'risk_tolerance': risk_tolerance
        }
    
    def get_insurance_portfolio(self) -> Dict[str, Any]:
        """Get current insurance portfolio overview"""
        
        total_insured = sum(p.insured_amount for p in self.active_policies.values())
        total_premiums = sum(p.insured_amount * p.premium_rate 
                           for p in self.active_policies.values())
        
        coverage_by_type = defaultdict(float)
        for policy in self.active_policies.values():
            coverage_by_type[policy.insurance_type.value] += policy.insured_amount
        
        return {
            'total_policies': len(self.active_policies),
            'total_insured_value': total_insured,
            'total_annual_premiums': total_premiums,
            'coverage_by_type': dict(coverage_by_type),
            'claims_history': len(self.claim_history),
            'performance_metrics': self.performance_metrics
        }
    
    def cancel_policy(self, policy_id: str) -> bool:
        """Cancel insurance policy"""
        
        policy = self.active_policies.get(policy_id)
        
        if not policy:
            return False
        
        policy.status = 'cancelled'
        self.performance_metrics['active_policies_count'] -= 1
        
        print(f"Policy {policy_id} cancelled")
        return True
    
    def get_policy_status(self, policy_id: str) -> Dict[str, Any]:
        """Get policy status and details"""
        
        policy = self.active_policies.get(policy_id)
        
        if not policy:
            return {'error': 'Policy not found'}
        
        # Calculate days remaining
        days_remaining = (policy.end_date - datetime.now()).days
        
        # Get related claims
        policy_claims = [c for c in self.claim_history if c.policy_id == policy_id]
        
        return {
            'policy_id': policy.policy_id,
            'status': policy.status,
            'insured_amount': policy.insured_amount,
            'coverage_percentage': policy.coverage_percentage,
            'premium_rate': policy.premium_rate,
            'days_remaining': days_remaining,
            'claims_count': len(policy_claims),
            'total_payouts': sum(c.payout_amount for c in policy_claims)
        }

# Example usage
if __name__ == "__main__":
    # Create insurance manager
    insurance_mgr = InsuranceManager()
    
    # Sample protocol data
    sample_protocol = {
        'tvl': 500000000,  # $500M
        'age_days': 450,
        'audits': ['audit1', 'audit2', 'audit3'],
        'team_reputation': 0.8,
        'governance_score': 0.7,
        'code_complexity': 0.6,
        'upgrade_frequency': 5,
        'bug_bounty_size': 500000,
        'test_coverage': 0.85,
        'centralization_score': 0.4,
        'custodian_rating': 0.9,
        'existing_insurance': 1000000,
        'legal_structure_score': 0.8
    }
    
    # Sample market data
    sample_market = {
        'volatility_30d': 0.6,
        'liquidity_depth': 20000000,
        'correlation_btc': 0.7,
        'market_sentiment': 0.6
    }
    
    # Demo insurance purchase
    async def demo():
        # Risk assessment
        risk_assessment = await insurance_mgr.assess_risk(sample_protocol, sample_market)
        print(f"Risk Assessment: Overall risk = {risk_assessment.overall_risk:.3f}")
        print(f"Recommended coverage: {risk_assessment.recommended_coverage.value}")
        print(f"Premium suggestion: {risk_assessment.premium_suggestion:.3%}")
        
        # Purchase insurance
        policy = await insurance_mgr.purchase_insurance(
            insurance_type=InsuranceType.SMART_CONTRACT,
            coverage_tier=CoverageTier.PREMIUM,
            insured_amount=1000000,  # $1M coverage
            protocol_data=sample_protocol,
            market_data=sample_market
        )
        
        # Get coverage recommendations
        recommendations = await insurance_mgr.get_coverage_recommendations(
            portfolio_value=5000000,
            risk_tolerance='moderate'
        )
        print(f"Coverage Recommendations: ${recommendations['recommended_coverage_amount']:,.2f}")
        
        # Get portfolio overview
        portfolio = insurance_mgr.get_insurance_portfolio()
        print(f"Insurance Portfolio: {portfolio['total_policies']} policies")
    
    asyncio.run(demo())
