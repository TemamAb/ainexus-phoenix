#!/usr/bin/env python3
"""
AINEXUS PERMANENT UTF-8 NORMALIZATION ENGINE
Detects and fixes encoding issues across all project files
"""

import os
import sys
import chardet
import hashlib
from pathlib import Path

class UTF8Normalizer:
    def __init__(self):
        self.supported_extensions = {
            '.py', '.html', '.js', '.css', '.json', '.md', '.txt', 
            '.yaml', '.yml', '.xml', '.csv', '.sol'
        }
        self.files_fixed = 0
        self.files_checked = 0
        
    def detect_encoding(self, file_path):
        """Accurately detect file encoding"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
            # Use chardet for accurate detection
            detection = chardet.detect(raw_data)
            encoding = detection['encoding']
            confidence = detection['confidence']
            
            return encoding, confidence, raw_data
        except Exception as e:
            return None, 0, None
    
    def is_valid_utf8(self, raw_data):
        """Check if data is valid UTF-8"""
        try:
            raw_data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    
    def normalize_to_utf8(self, file_path, original_encoding, raw_data):
        """Convert any encoding to clean UTF-8"""
        try:
            # Decode from original encoding
            if original_encoding and original_encoding.lower() != 'utf-8':
                content = raw_data.decode(original_encoding, errors='replace')
            else:
                # Try to decode as UTF-8 with error replacement
                content = raw_data.decode('utf-8', errors='replace')
            
            # Remove BOM if present
            if content.startswith('\ufeff'):
                content = content[1:]
            
            # Remove other problematic Unicode characters
            content = self.clean_problematic_chars(content)
            
            # Write back as clean UTF-8 without BOM
            with open(file_path, 'w', encoding='utf-8', errors='strict') as f:
                f.write(content)
                
            return True
        except Exception as e:
            print(f"‚ùå Failed to normalize {file_path}: {str(e)}")
            return False
    
    def clean_problematic_chars(self, content):
        """Remove or replace problematic Unicode characters"""
        # Replace common problematic characters
        replacements = {
            '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '--', '\u2026': '...'
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        return content
    
    def create_file_hash(self, file_path):
        """Create hash to detect changes"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def scan_and_fix_directory(self, directory='.'):
        """Recursively scan and fix all files"""
        print(f"Ì¥ç Scanning {directory} for encoding issues...")
        
        for root, dirs, files in os.walk(directory):
            # Skip virtual environments and git directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if file extension is supported
                if file_path.suffix.lower() not in self.supported_extensions:
                    continue
                
                self.files_checked += 1
                
                # Get file stats and hash before changes
                original_hash = self.create_file_hash(file_path)
                
                # Detect encoding
                encoding, confidence, raw_data = self.detect_encoding(file_path)
                
                if not encoding:
                    print(f"‚ö†Ô∏è  Could not detect encoding: {file_path}")
                    continue
                
                # Check if already valid UTF-8
                if self.is_valid_utf8(raw_data) and encoding.lower() == 'utf-8':
                    continue
                
                # Normalize to UTF-8
                print(f"Ì¥Ñ Fixing {file_path} (detected: {encoding}, confidence: {confidence:.2f})")
                
                if self.normalize_to_utf8(file_path, encoding, raw_data):
                    # Verify the fix
                    new_hash = self.create_file_hash(file_path)
                    if new_hash != original_hash:
                        self.files_fixed += 1
                        print(f"‚úÖ Fixed: {file_path}")
                    else:
                        print(f"‚ÑπÔ∏è  No changes needed: {file_path}")
        
        return self.files_fixed, self.files_checked
    
    def create_pre_commit_hook(self):
        """Create git pre-commit hook for automatic UTF-8 validation"""
        hook_content = '''#!/bin/bash
# AINEXUS UTF-8 Pre-commit Hook
echo "Ì¥ç Checking file encodings..."
python3 utf8_normalize.py --check-only
if [ $? -ne 0 ]; then
    echo "‚ùå UTF-8 issues detected. Run: python3 utf8_normalize.py"
    exit 1
fi
echo "‚úÖ All files are UTF-8 compliant"
exit 0
'''
        
        hook_path = Path('.git/hooks/pre-commit')
        if hook_path.parent.exists():
            with open(hook_path, 'w') as f:
                f.write(hook_content)
            hook_path.chmod(0o755)
            print("‚úÖ Git pre-commit hook installed")

def main():
    normalizer = UTF8Normalizer()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check-only':
        # Check-only mode for CI/CD
        fixed, checked = normalizer.scan_and_fix_directory()
        if fixed > 0:
            print(f"‚ùå {fixed} files need UTF-8 normalization")
            sys.exit(1)
        else:
            print(f"‚úÖ All {checked} files are UTF-8 compliant")
            sys.exit(0)
    else:
        # Normalization mode
        fixed, checked = normalizer.scan_and_fix_directory()
        print(f"\nÌæØ NORMALIZATION COMPLETE:")
        print(f"   Ì≥ä Files checked: {checked}")
        print(f"   Ì¥ß Files fixed: {fixed}")
        print(f"   ‚úÖ Success rate: {(checked - fixed)/checked*100:.1f}%")
        
        # Install git hook
        normalizer.create_pre_commit_hook()

if __name__ == '__main__':
    main()
