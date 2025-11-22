#!/usr/bin/env python3
"""
AINEXUS Deployment Certificate Verifier
Enterprise-grade certificate validation system
"""

import json
import hashlib
import hmac
from datetime import datetime

class CertificateVerifier:
    def __init__(self, verification_key):
        self.verification_key = verification_key
    
    def verify_certificate(self, certificate_path):
        """Verify AINEXUS deployment certificate"""
        try:
            with open(certificate_path, 'r') as f:
                certificate = json.load(f)
            
            # Extract signature data
            signature_data = certificate['certificate']['digitalSignature']
            expected_signature = signature_data['signature']
            certificate_id = certificate['certificate']['metadata']['certificateId']
            
            # Generate verification signature
            computed_signature = self.generate_signature(certificate_id)
            
            # Verify signature
            if computed_signature != expected_signature:
                return {
                    'valid': False,
                    'reason': 'Digital signature mismatch',
                    'certificate_id': certificate_id
                }
            
            # Verify certificate expiration
            valid_until = certificate['certificate']['metadata']['validUntil']
            if datetime.now() > datetime.fromisoformat(valid_until.replace('Z', '+00:00')):
                return {
                    'valid': False, 
                    'reason': 'Certificate expired',
                    'certificate_id': certificate_id
                }
            
            # Verify module deployment count
            deployed_modules = certificate['certificate']['executiveSummary']['successfullyDeployed']
            if deployed_modules != 45:
                return {
                    'valid': False,
                    'reason': f'Incomplete module deployment: {deployed_modules}/45',
                    'certificate_id': certificate_id
                }
            
            return {
                'valid': True,
                'certificate_id': certificate_id,
                'verification_time': datetime.now().isoformat(),
                'issued_to': certificate['certificate']['clientInformation']['clientWallet'],
                'platform_version': certificate['certificate']['metadata']['platformVersion']
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Verification error: {str(e)}'
            }
    
    def generate_signature(self, certificate_id):
        """Generate HMAC signature for verification"""
        return hmac.new(
            self.verification_key.encode(),
            certificate_id.encode(),
            hashlib.sha256
        ).hexdigest()

def main():
    verifier = CertificateVerifier('ainexus-verification-key-2024')
    
    # Verify sample certificate
    result = verifier.verify_certificate('Sample_Deployment_Certificate.json')
    
    print("í´ AINEXUS Certificate Verification")
    print("=" * 50)
    
    if result['valid']:
        print("â CERTIFICATE VALID")
        print(f"í³ Certificate ID: {result['certificate_id']}")
        print(f"í±¤ Issued To: {result['issued_to']}")
        print(f"ï¿½ï¿½ Platform Version: {result['platform_version']}")
        print(f"â° Verified At: {result['verification_time']}")
    else:
        print("â CERTIFICATE INVALID")
        print(f"í³ Certificate ID: {result.get('certificate_id', 'Unknown')}")
        print(f"íº« Reason: {result['reason']}")

if __name__ == "__main__":
    main()
