#!/usr/bin/env python3
"""
Test script for MCP BLASTp client using streamable HTTP
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
    """List available MCP tools"""
    # FastMCP typically uses these endpoints
    urls_to_try = [
        f"http://{host}:{port}/tools/list",
        f"http://{host}:{port}/tools",
        f"http://{host}:{port}/mcp/tools",
        f"http://{host}:{port}/"
    ]
    
    for url in urls_to_try:
        try:
            logger.info(f"Trying to list MCP tools: {url}")
            headers = {"Accept": "application/json"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                logger.info(f"Success with endpoint: {url}")
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed with {url}: {e}")
            continue
    
    return {"error": "Could not find working endpoint"}


def call_mcp_tool(host: str, port: int, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool via HTTP"""
    # FastMCP typically uses these endpoints
    urls_to_try = [
        f"http://{host}:{port}/tools/call",
        f"http://{host}:{port}/mcp/call",
        f"http://{host}:{port}/call"
    ]
    
    payload = {
        "name": tool_name,
        "arguments": arguments
    }
    
    for url in urls_to_try:
        try:
            logger.info(f"Trying to call MCP tool: {url} with payload: {payload}")
            
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=300)
            if response.status_code == 200:
                logger.info(f"Success with endpoint: {url}")
                logger.info(f"MCP tool response status: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed with {url}: {e}")
            continue
    else:
        return {"error": "Could not find working call endpoint"}
    
    # Handle streaming response
    result = {"content": []}
    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode('utf-8'))
                if "content" in chunk:
                    result["content"].extend(chunk["content"])
            except json.JSONDecodeError:
                # Handle non-JSON chunks
                result["content"].append({"type": "text", "text": line.decode('utf-8')})
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Test MCP BLASTp client")
    parser.add_argument("--host", default="127.0.0.1", help="MCP server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8001, help="MCP server port (default: 8001)")
    parser.add_argument("--tool", default="blastp_search_flexible_db_tabular", help="MCP tool to test (default: blastp_search_flexible_db_tabular)")
    parser.add_argument("--sequence", default="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG", help="Sequence to test (default: MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG)")
    parser.add_argument("--database", default="swissprot", help="Database to test (default: swissprot)")
    parser.add_argument("--evalue", type=float, default=0.001, help="E-value threshold (default: 0.001)")
    parser.add_argument("--max_target_seqs", type=int, default=10, help="Maximum number of target sequences (default: 10)")
    args = parser.parse_args()
    
    # Test parameters
    
    logger.info(f"Testing MCP BLASTp client on {args.host}:{args.port}")
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
    for tool in tools_result.get("tools", []):
        logger.info(f"  - {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}")
    
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
    
    for content in result.get("content", []):
        if content.get("type") == "text":
            logger.info(content["text"])
        else:
            logger.info(json.dumps(content, indent=2))


if __name__ == "__main__":
    main() 