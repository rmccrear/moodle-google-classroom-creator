import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Setup OAuth
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials',
    'https://www.googleapis.com/auth/classroom.topics',
    'https://www.googleapis.com/auth/classroom.coursework.students'
]

def get_cached_credentials():
    """Get cached credentials or authenticate if needed"""
    creds = None
    
    # Ensure temp_data directory exists
    os.makedirs('temp_data', exist_ok=True)
    
    # The file token.pickle stores the user's access and refresh tokens
    token_path = 'temp_data/token.pickle'
    
    # Load existing credentials if available
    if os.path.exists(token_path):
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            print("🔑 Using cached credentials")
        except Exception as e:
            print(f"⚠️  Error loading cached credentials: {e}")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("🔄 Refreshed expired credentials")
            except Exception as e:
                print(f"⚠️  Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            print("🔐 Authenticating with Google...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Authentication successful")
        
        # Save the credentials for the next run
        try:
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            print("💾 Credentials cached for future use")
        except Exception as e:
            print(f"⚠️  Error saving credentials: {e}")
    
    return creds

def clear_cached_credentials():
    """Clear cached credentials"""
    token_path = 'temp_data/token.pickle'
    if os.path.exists(token_path):
        os.remove(token_path)
        print("🗑️  Cached credentials cleared")
    else:
        print("ℹ️  No cached credentials found")

def get_credential_info():
    """Get information about cached credentials"""
    token_path = 'temp_data/token.pickle'
    
    if not os.path.exists(token_path):
        print("ℹ️  No cached credentials found")
        return None
    
    try:
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        print("🔑 Cached Credentials Info:")
        print(f"  Valid: {creds.valid}")
        print(f"  Expired: {creds.expired}")
        print(f"  Has refresh token: {creds.refresh_token is not None}")
        print(f"  Scopes: {creds.scopes}")
        
        return creds
    except Exception as e:
        print(f"❌ Error reading cached credentials: {e}")
        return None 