#!/usr/bin/env python3
"""Simple client for MCP-like endpoints"""

import requests
import json

def test_mcp_like_endpoints():
    """Test the MCP-like endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing MCP-like endpoints...")
    
    # Test 1: List tools
    print("\n1. Listing available tools...")
    try:
        response = requests.get(f"{base_url}/mcp/tools")
        if response.status_code == 200:
            tools = response.json()
            print("Available tools:")
            for tool in tools["tools"]:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error listing tools: {e}")
    
    # Test 2: Get tool info
    print("\n2. Getting tool info...")
    try:
        response = requests.post(f"{base_url}/mcp/call", json={
            "name": "get_tool_info",
            "arguments": {}
        })
        if response.status_code == 200:
            result = response.json()
            print("Tool info:")
            for content in result["content"]:
                print(content["text"])
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error getting tool info: {e}")
    
    # Test 3: Predict druggability
    print("\n3. Predicting druggability...")
    sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    try:
        response = requests.post(f"{base_url}/mcp/call", json={
            "name": "predict_druggability",
            "arguments": {
                "sequence": sequence
            }
        })
        if response.status_code == 200:
            result = response.json()
            print("Prediction result:")
            for content in result["content"]:
                print(content["text"])
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error predicting druggability: {e}")
    
    print("\nMCP-like endpoint test completed!")

if __name__ == '__main__':
    test_mcp_like_endpoints() 