#!/usr/bin/env python3
"""
Debug script to see what FastMCP server exposes
"""

import requests
import json

def debug_server(host: str, port: int):
    """Debug what endpoints the FastMCP server exposes"""
    base_url = f"http://{host}:{port}"
    
    # Try common endpoints for FastMCP 2.0
    endpoints_to_try = [
        "/",
        "/health",
        "/tools",
        "/tools/list", 
        "/mcp/tools",
        "/mcp/call",
        "/call",
        "/api/tools",
        "/api/call",
        "/docs",
        "/openapi.json"
    ]
    
    print(f"Debugging FastMCP server at {base_url}")
    print("=" * 50)
    
    for endpoint in endpoints_to_try:
        url = base_url + endpoint
        print(f"\nTrying: {url}")
        
        try:
            # Try GET
            response = requests.get(url, timeout=5)
            print(f"  GET: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"  Response: {response.text[:200]}...")
        except Exception as e:
            print(f"  GET Error: {e}")
        
        try:
            # Try POST with empty JSON
            response = requests.post(url, json={}, timeout=5)
            print(f"  POST: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"  Response: {response.text[:200]}...")
        except Exception as e:
            print(f"  POST Error: {e}")

if __name__ == "__main__":
    debug_server("127.0.0.1", 8002) 