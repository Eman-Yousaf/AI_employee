#!/usr/bin/env python3
"""MCP Email Client - Direct client to call Email MCP server."""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Optional


def call_email_mcp(tool: str, params: Dict, credentials_path: str = None, token_path: str = None) -> Dict:
    """Call Email MCP server with a tool request."""

    # Set environment variables for credentials
    env = os.environ.copy()
    if credentials_path:
        env['GMAIL_CREDENTIALS'] = credentials_path
    if token_path:
        env['GMAIL_TOKEN'] = token_path

    # Default paths
    if 'GMAIL_CREDENTIALS' not in env:
        env['GMAIL_CREDENTIALS'] = str(Path(__file__).parent.parent / 'config' / 'credentials.json')
    if 'GMAIL_TOKEN' not in env:
        env['GMAIL_TOKEN'] = str(Path(__file__).parent.parent / 'config' / 'token.json')

    # MCP server path
    mcp_server = Path(__file__).parent.parent / '.claude' / 'skills' / 'email-mcp' / 'servers' / 'email_mcp.py'

    if not mcp_server.exists():
        return {"success": False, "error": f"MCP server not found: {mcp_server}"}

    # Create the MCP request
    request = {
        "tool": tool,
        "params": params
    }

    try:
        # Run the MCP server and send the request
        result = subprocess.run(
            [sys.executable, str(mcp_server)],
            input=json.dumps(request) + "\n",
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"MCP server error: {result.stderr}",
                "stdout": result.stdout
            }

        # Parse the response
        # The server might output multiple lines, take the last valid JSON
        lines = result.stdout.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line:
                try:
                    response = json.loads(line)
                    return response
                except json.JSONDecodeError:
                    continue

        return {
            "success": False,
            "error": "Could not parse MCP response",
            "raw_output": result.stdout
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "MCP call timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_email(to: str, subject: str, body: str, is_html: bool = False,
               cc: list = None, bcc: list = None,
               credentials_path: str = None, token_path: str = None) -> Dict:
    """Send an email using Email MCP."""
    params = {
        "to": to,
        "subject": subject,
        "body": body,
        "is_html": is_html
    }
    if cc:
        params["cc"] = cc
    if bcc:
        params["bcc"] = bcc

    return call_email_mcp("email_send", params, credentials_path, token_path)


def create_draft(to: str, subject: str, body: str, is_html: bool = False,
                 credentials_path: str = None, token_path: str = None) -> Dict:
    """Create a draft email using Email MCP."""
    params = {
        "to": to,
        "subject": subject,
        "body": body,
        "is_html": is_html
    }
    return call_email_mcp("email_draft", params, credentials_path, token_path)


def search_emails(query: str, max_results: int = 10,
                  credentials_path: str = None, token_path: str = None) -> Dict:
    """Search emails using Email MCP."""
    params = {
        "query": query,
        "max_results": max_results
    }
    return call_email_mcp("email_search", params, credentials_path, token_path)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='MCP Email Client')
    parser.add_argument('--tool', required=True,
                        choices=['email_send', 'email_draft', 'email_search', 'tools/list'],
                        help='MCP tool to call')
    parser.add_argument('--params', help='JSON parameters for the tool')
    parser.add_argument('--credentials', help='Path to credentials.json')
    parser.add_argument('--token', help='Path to token.json')

    args = parser.parse_args()

    # Parse params
    params = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"Error parsing params: {e}")
            sys.exit(1)

    # Call the MCP
    result = call_email_mcp(args.tool, params, args.credentials, args.token)

    # Output result
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
