#!/usr/bin/env python3
"""Test MCP server directly"""

import asyncio
import logging
import subprocess
import sys
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_server():
    """Test the MCP server directly"""
    logger.info("Testing MCP server directly...")
    
    # Start MCP server
    logger.info("Starting MCP server...")
    process = subprocess.Popen([
        sys.executable, "-m", "api.mcp_server", 
        "--streamable-http", "--host", "0.0.0.0", "--port", "8001"
    ])
    
    # Wait a bit for server to start
    time.sleep(3)
    
    # Test with curl
    logger.info("Testing with curl...")
    try:
        result = subprocess.run([
            "curl", "-v", "http://localhost:8001/mcp"
        ], capture_output=True, text=True, timeout=10)
        logger.info("Curl result: %s", result.stdout)
        logger.info("Curl error: %s", result.stderr)
    except subprocess.TimeoutExpired:
        logger.error("Curl timed out")
    except Exception as e:
        logger.error("Curl error: %s", e)
    
    # Clean up
    logger.info("Terminating MCP server...")
    process.terminate()
    process.wait()

if __name__ == '__main__':
    asyncio.run(test_mcp_server()) 