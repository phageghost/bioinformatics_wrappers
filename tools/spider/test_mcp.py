#!/usr/bin/env python3
"""Test script for SPIDER MCP server"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.mcp_server import SpiderMCPServer


async def test_mcp_server():
    """Test the MCP server functionality"""
    print("Testing SPIDER MCP Server...")
    
    # Create server instance
    server = SpiderMCPServer()
    
    # Test tool listing
    print("\n1. Testing tool listing...")
    tools_result = await server.server._handlers['tools/list']()
    print(f"Available tools: {len(tools_result.tools)}")
    for tool in tools_result.tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test tool info
    print("\n2. Testing get_tool_info...")
    info_result = await server._handle_get_tool_info({})
    print("Tool info result:")
    for content in info_result.content:
        print(content.text)
    
    # Test prediction
    print("\n3. Testing predict_druggability...")
    test_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    pred_result = await server._handle_predict_druggability({"sequence": test_sequence})
    print("Prediction result:")
    for content in pred_result.content:
        print(content.text)
    
    print("\nMCP server test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 