#!/usr/bin/env python3
"""
Simple test script for FastMCP BLASTp HTTP API server
"""

import requests
import json
import sys

def test_server():
    """Test the FastMCP HTTP API server endpoints"""
    base_url = "http://127.0.0.1:8001"
    
    print("Testing FastMCP BLASTp HTTP API server...")
    print("=" * 50)
    
    # Test tools endpoint
    try:
        response = requests.get(f"{base_url}/tools", timeout=5)
        print(f"Tools endpoint: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()
            print("✅ Tools endpoint working")
            print(f"Available tools: {json.dumps(tools, indent=2)}")
        else:
            print(f"❌ Tools endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Tools endpoint failed: {e}")
        return False
    
    # Test tool call
    try:
        test_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
        payload = {
            "sequence": test_sequence,
            "database": "swissprot",
            "evalue": 0.001,
            "max_target_seqs": 5
        }
        
        response = requests.post(
            f"{base_url}/tools/blastp_search_flexible_db_tabular",
            json=payload,
            timeout=60
        )
        print(f"Tool call: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Tool call successful")
            print(f"Result: {json.dumps(result, indent=2)[:500]}...")
        else:
            print(f"❌ Tool call failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Tool call failed: {e}")
        return False
    
    print("=" * 50)
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1) 