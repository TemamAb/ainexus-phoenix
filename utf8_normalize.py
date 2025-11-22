#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMPLE UTF-8 NORMALIZATION
Basic encoding fix for deployment
"""

import os
import sys

def simple_utf8_check():
    """Basic UTF-8 validation"""
    files_to_check = ['app.py', 'validate_deployment.py', 'utf8_normalize.py']
    
    for file in files_to_check:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ {file} - UTF-8 OK")
            except UnicodeDecodeError:
                print(f"❌ {file} - UTF-8 issue")
                return False
    return True

if __name__ == '__main__':
    if simple_utf8_check():
        print("✅ All files are UTF-8 compliant")
        sys.exit(0)
    else:
        print("❌ UTF-8 issues detected")
        sys.exit(1)
