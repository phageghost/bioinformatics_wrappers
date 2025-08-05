#!/usr/bin/env python3
"""
Test script for FastMCP BLASTp HTTP API client (LangFlow compatible)
"""

import argparse
import json
import requests
import sys
from typing import Dict, Any
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_mcp_tools(host: str, port: int) -> Dict[str, Any]:
    """List available MCP tools using FastMCP HTTP API"""
    url = f"http://{host}:{port}/tools"
    
    try:
        logger.info(f"Listing MCP tools: {url}")
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            logger.info(f"Success with endpoint: {url}")
            return response.json()
        else:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {"error": f"Request failed: {e}"}


def call_mcp_tool(host: str, port: int, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool via FastMCP HTTP API"""
    url = f"http://{host}:{port}/tools/{tool_name}"
    
    try:
        logger.info(f"Calling MCP tool: {url} with arguments: {arguments}")
        
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = requests.post(url, json=arguments, headers=headers, timeout=300)
        
        if response.status_code == 200:
            logger.info(f"Success with endpoint: {url}")
            logger.info(f"MCP tool response status: {response.status_code}")
            return response.json()
        else:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {"error": f"Request failed: {e}"}


def main():
    parser = argparse.ArgumentParser(description="Test FastMCP BLASTp HTTP API client")
    parser.add_argument("--host", default="127.0.0.1", help="MCP server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8001, help="MCP server port (default: 8001)")
    parser.add_argument("--tool", default="blastp_search_flexible_db_tabular", help="MCP tool to test (default: blastp_search_flexible_db_tabular)")
    parser.add_argument("--sequence", default="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG", help="Sequence to test (default: MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG)")
    parser.add_argument("--database", default="swissprot", help="Database to test (default: swissprot)")
    parser.add_argument("--evalue", type=float, default=0.001, help="E-value threshold (default: 0.001)")
    parser.add_argument("--max_target_seqs", type=int, default=10, help="Maximum number of target sequences (default: 10)")
    args = parser.parse_args()
    
    # Test parameters
    
    logger.info(f"Testing FastMCP HTTP API client on {args.host}:{args.port}")
    logger.info(f"Tool: {args.tool}")
    logger.info(f"Sequence: {args.sequence[:50]}...")
    logger.info(f"Database: {args.database}")
    logger.info(f"E-value: {args.evalue}")
    logger.info(f"Max target sequences: {args.max_target_seqs}")
    logger.info("-" * 60)
    
    # First, list available tools
    logger.info("Listing available MCP tools...")
    tools_result = list_mcp_tools(args.host, args.port)
    if "error" in tools_result:
        logger.error(f"❌ Failed to list tools: {tools_result['error']}")
        sys.exit(1)
    
    logger.info("Available tools:")
    if "tools" in tools_result:
        for tool in tools_result["tools"]:
            logger.info(f"  - {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}")
    else:
        logger.info(f"Server response: {json.dumps(tools_result, indent=2)}")
    
    logger.info("-" * 60)
    
    # Call the MCP tool
    result = call_mcp_tool(
        host=args.host,
        port=args.port,
        tool_name=args.tool,
        arguments={
            "sequence": args.sequence,
            "database": args.database,
            "evalue": args.evalue,
            "max_target_seqs": args.max_target_seqs
        }
    )
    
    # Display results
    if "error" in result:
        logger.error(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    logger.info("✅ MCP call successful!")
    logger.info("\nResults:")
    logger.info(json.dumps(result, indent=2))


if __name__ == "__main__":
    main() 