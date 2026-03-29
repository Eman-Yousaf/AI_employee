#!/usr/bin/env python3
"""Gmail Authentication - Fixed for Windows with better error handling."""

import os
import json
import socket
import webbrowser
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]


def find_free_port(start_port=8080, max_port=8100):
    """Find a free port for the OAuth callback."""
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports found between {start_port} and {max_port}")


def authenticate_gmail(credentials_path: str = 'config/credentials.json',
                       token_path: str = 'config/token.json'):
    """Authenticate with Gmail with robust error handling."""

    creds_path = Path(credentials_path)
    token_file = Path(token_path)

    # Check credentials exist
    if not creds_path.exists():
        logger.error(f"❌ Credentials file not found: {creds_path.absolute()}")
        logger.error("\nTo fix this:")
        logger.error("1. Go to https://console.cloud.google.com/")
        logger.error("2. Create a project and enable Gmail API")
        logger.error("3. Create OAuth credentials (Desktop app)")
        logger.error(f"4. Download JSON and save to: {creds_path.absolute()}")
        return None

    creds = None

    # Load existing token if available
    if token_file.exists():
        try:
            logger.info(f"📂 Loading existing token from {token_path}...")
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            logger.info("✓ Token loaded")
        except Exception as e:
            logger.warning(f"⚠ Could not load existing token: {e}")

    # If credentials are valid, return them
    if creds and creds.valid:
        logger.info("✓ Credentials are valid")
        return creds

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("🔄 Refreshing expired token...")
            creds.refresh(Request())
            token_file.parent.mkdir(parents=True, exist_ok=True)
            token_file.write_text(creds.to_json())
            logger.info("✓ Token refreshed and saved")
            return creds
        except Exception as e:
            logger.error(f"❌ Token refresh failed: {e}")
            logger.info("🔄 Will re-authenticate...")
            creds = None

    # Run OAuth flow
    try:
        logger.info("🌐 Starting OAuth flow...")
        logger.info("   A browser window should open shortly...")

        # Find a free port
        port = find_free_port()
        logger.info(f"   Using port: {port}")

        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)

        # Run with better error handling
        try:
            creds = flow.run_local_server(
                port=port,
                open_browser=True,
                success_message="✓ Authentication successful! You can close this window.",
                authorization_prompt_message="Please authorize this application to access Gmail."
            )
        except Exception as e:
            logger.error(f"❌ OAuth flow failed: {e}")
            logger.info("\nTrying alternative method...")

            # Fallback: run without browser opening
            creds = flow.run_local_server(
                port=find_free_port(),
                open_browser=False,
                success_message="✓ Authentication successful!"
            )

        # Save token
        if creds:
            token_file.parent.mkdir(parents=True, exist_ok=True)
            token_file.write_text(creds.to_json())
            logger.info(f"✓ Token saved to {token_path}")
            return creds

    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Make sure credentials.json is valid and downloaded from Google Cloud Console")
        logger.error("2. Check that the OAuth consent screen is configured")
        logger.error("3. Try running as administrator if ports are blocked")
        logger.error("4. Disable VPN/proxy temporarily")
        return None


def verify_access(creds: Credentials) -> bool:
    """Verify Gmail API access works."""
    from googleapiclient.discovery import build

    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()

        logger.info(f"\n✅ Successfully authenticated!")
        logger.info(f"   Email: {profile.get('emailAddress', 'N/A')}")
        logger.info(f"   Messages: {profile.get('messagesTotal', 'N/A')}")
        logger.info(f"   Threads: {profile.get('threadsTotal', 'N/A')}")

        # Test fetching messages
        try:
            results = service.users().messages().list(userId='me', maxResults=1).execute()
            logger.info(f"   ✓ Can fetch messages")
        except Exception as e:
            logger.warning(f"   ⚠ Could not fetch messages: {e}")

        return True

    except Exception as e:
        logger.error(f"\n❌ Failed to verify access: {e}")
        return False


def print_manual_auth_instructions(creds_path: Path):
    """Print instructions for manual OAuth setup."""
    logger.info("\n" + "=" * 70)
    logger.info("MANUAL AUTHENTICATION INSTRUCTIONS")
    logger.info("=" * 70)
    logger.info("""
If automatic authentication keeps failing, try this:

1. Go to https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Make sure:
   - Application type is "Desktop app"
   - Authorized redirect URIs include: http://localhost:8080/
   - Status is "Enabled"

4. Try running this script with administrator privileges
5. Temporarily disable antivirus/firewall
6. Make sure no other app is using port 8080

Alternative: Use device flow authentication
Edit this script and change:
    creds = flow.run_local_server(...)
to:
    creds = flow.run_console()
(This will give you a URL to manually visit)
""")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Gmail API Authentication - Fixed Version')
    parser.add_argument('--credentials', default='config/credentials.json',
                        help='Path to credentials.json from Google Cloud Console')
    parser.add_argument('--token', default='config/token.json',
                        help='Path to save/load token.json')
    parser.add_argument('--force', action='store_true',
                        help='Force re-authentication even if token exists')

    args = parser.parse_args()

    print("=" * 70)
    print("Gmail API Authentication - Silver Tier")
    print("=" * 70)

    creds_path = Path(args.credentials)

    # If force flag, delete existing token
    if args.force:
        token_path = Path(args.token)
        if token_path.exists():
            token_path.unlink()
            logger.info("🗑 Existing token deleted (force re-auth)")

    creds = authenticate_gmail(args.credentials, args.token)

    if creds:
        verify_access(creds)
        print("\n✓ Authentication complete!")
        print(f"   You can now run: Gmail_Watcher.bat")
        return 0
    else:
        print_manual_auth_instructions(creds_path)
        print("\n❌ Authentication failed")
        return 1


if __name__ == '__main__':
    exit(main())
