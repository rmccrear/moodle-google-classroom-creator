#!/usr/bin/env python3
"""
Authentication Management Script
Manages cached Google API credentials
"""

from auth_cache import get_cached_credentials, clear_cached_credentials, get_credential_info

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Authentication Management")
        print("=" * 30)
        print("Usage:")
        print("  python manage_auth.py status     # Check credential status")
        print("  python manage_auth.py clear      # Clear cached credentials")
        print("  python manage_auth.py test       # Test authentication")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        print("🔍 Checking credential status...")
        get_credential_info()
    
    elif command == 'clear':
        print("🗑️  Clearing cached credentials...")
        clear_cached_credentials()
    
    elif command == 'test':
        print("🧪 Testing authentication...")
        try:
            creds = get_cached_credentials()
            if creds and creds.valid:
                print("✅ Authentication successful!")
                print(f"   Valid: {creds.valid}")
                print(f"   Expired: {creds.expired}")
            else:
                print("❌ Authentication failed")
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main() 