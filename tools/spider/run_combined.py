#!/usr/bin/env python3
"""Combined server entrypoint - runs FastAPI and standalone MCP server"""

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_fastapi():
    """Run the FastAPI server"""
    logger.info("Starting FastAPI server...")
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ])
    logger.info("FastAPI server started")
    return process

async def run_mcp_server():
    """Run the standalone MCP server"""
    logger.info("Starting MCP server...")
    process = subprocess.Popen([
        sys.executable, "-m", "api.mcp_server", 
        "--streamable-http", "--host", "0.0.0.0", "--port", "8001"
    ])
    logger.info("MCP server started")
    return process

async def main():
    """Run both servers"""
    logger.info("Starting combined server...")
    
    # Start both servers
    fastapi_process = await run_fastapi()
    mcp_process = await run_mcp_server()
    
    try:
        # Wait for both processes
        logger.info("Both servers started. Waiting for completion...")
        fastapi_process.wait()
        mcp_process.wait()
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
        fastapi_process.terminate()
        mcp_process.terminate()
        fastapi_process.wait()
        mcp_process.wait()
        logger.info("Servers shut down")

if __name__ == '__main__':
    asyncio.run(main()) 