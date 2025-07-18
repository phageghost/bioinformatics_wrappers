#!/usr/bin/env python3
"""Combined server entrypoint v2 - runs FastAPI and original MCP server"""

import asyncio
import logging
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CombinedServer:
    def __init__(self):
        self.fastapi_process = None
        self.mcp_process = None
        self.running = True
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.shutdown()
        
    def shutdown(self):
        """Shutdown both servers"""
        logger.info("Shutting down servers...")
        if self.fastapi_process:
            logger.info("Terminating FastAPI server...")
            self.fastapi_process.terminate()
            try:
                self.fastapi_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("FastAPI server didn't terminate gracefully, killing...")
                self.fastapi_process.kill()
                
        if self.mcp_process:
            logger.info("Terminating MCP server...")
            self.mcp_process.terminate()
            try:
                self.mcp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("MCP server didn't terminate gracefully, killing...")
                self.mcp_process.kill()
        
        logger.info("All servers shut down")

    async def run_fastapi(self):
        """Run the FastAPI server"""
        logger.info("Starting FastAPI server...")
        self.fastapi_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ])
        logger.info("FastAPI server started with PID: %d", self.fastapi_process.pid)
        return self.fastapi_process

    async def run_mcp_server(self):
        """Run the original MCP server"""
        logger.info("Starting MCP server...")
        # For now, we'll skip the MCP server since it's not working properly
        # Instead, we'll use the MCP-like endpoints in the FastAPI app
        logger.info("MCP server disabled - using MCP-like endpoints in FastAPI")
        self.mcp_process = None
        return self.mcp_process

    async def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        while self.running:
            # Check FastAPI process
            if self.fastapi_process and self.fastapi_process.poll() is not None:
                logger.error("FastAPI server died, restarting...")
                await self.run_fastapi()
                
            # Check MCP process (disabled for now)
            # if self.mcp_process and self.mcp_process.poll() is not None:
            #     logger.error("MCP server died, restarting...")
            #     await self.run_mcp_server()
                
            await asyncio.sleep(5)  # Check every 5 seconds

    async def main(self):
        """Run both servers with monitoring"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("Starting combined server...")
        
        try:
            # Start both servers
            await self.run_fastapi()
            await self.run_mcp_server()
            
            # Monitor processes
            await self.monitor_processes()
            
        except Exception as e:
            logger.error("Error in combined server: %s", e)
            self.shutdown()
            raise

if __name__ == '__main__':
    server = CombinedServer()
    asyncio.run(server.main()) 