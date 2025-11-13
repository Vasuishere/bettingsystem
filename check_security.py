#!/usr/bin/env python3
"""
Pre-commit security check script
Run this before pushing to GitHub to ensure no credentials are exposed
"""

import os
import sys

# Sensitive patterns to check for
SENSITIVE_PATTERNS = [
    'AVNS_',  # Aiven password prefix
    'pg-3791265f',  # Your Aiven host
    ':17441',  # Your Aiven port
]

# Files that should be ignored (never committed)
IGNORED_FILES = [
    '.env',
    'db.sqlite3',
    '__pycache__',
    '.pyc',
]

# Files to check (will be committed)
FILES_TO_CHECK = [
    '.env.example',
    'mymainserver/settings.py',
    'DEPLOYMENT.md',
    'DEPLOYMENT_CHECKLIST.md',
    'SECURITY_NOTICE.md',
    'README.md',
]

def check_file_for_secrets(filepath):
    """Check if file contains sensitive information"""
    if not os.path.exists(filepath):
        return True, None
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return True, None
        
    for pattern in SENSITIVE_PATTERNS:
        if pattern in content:
            return False, pattern
    
    return True, None

def main():
    print("🔐 Running security check before commit...\n")
    
    all_safe = True
    
    for filepath in FILES_TO_CHECK:
        safe, pattern = check_file_for_secrets(filepath)
        
        if safe:
            print(f"✅ {filepath} - Clean")
        else:
            print(f"❌ {filepath} - CONTAINS SENSITIVE DATA: {pattern}")
            all_safe = False
    
    print("\n" + "="*50)
    
    if all_safe:
        print("✅ SAFE TO COMMIT - No credentials found!")
        print("\nYou can now run:")
        print("  git add .")
        print("  git commit -m 'Your message'")
        print("  git push origin main")
        return 0
    else:
        print("❌ UNSAFE - Credentials detected!")
        print("\nPlease remove sensitive data before committing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
