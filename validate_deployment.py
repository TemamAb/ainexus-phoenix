#!/usr/bin/env python3
"""
AINEXUS DEPLOYMENT UTF-8 VALIDATOR
Ensures all files are UTF-8 compliant before deployment
"""

import sys
from utf8_normalize import UTF8Normalizer

def validate_deployment():
    """Validate all files are UTF-8 compliant before deployment"""
    print("Ì∫Ä AINEXUS DEPLOYMENT UTF-8 VALIDATION")
    print("=" * 50)
    
    normalizer = UTF8Normalizer()
    fixed, checked = normalizer.scan_and_fix_directory()
    
    if fixed > 0:
        print(f"\n‚ùå DEPLOYMENT BLOCKED: {fixed} files had encoding issues")
        print("Ì¥Ñ Fixed automatically. Please review and commit changes.")
        sys.exit(1)
    else:
        print(f"\n‚úÖ DEPLOYMENT READY: All {checked} files are UTF-8 compliant")
        sys.exit(0)

if __name__ == '__main__':
    validate_deployment()
