#!/usr/bin/env python3
"""
BLAST Combined Server Manager

This module provides a robust server management system for the BLAST API service,
combining FastAPI server execution with process monitoring and graceful shutdown
capabilities. It serves as the main entry point for running the BLAST API in
containerized environments.

The CombinedServer class provides:
- FastAPI server process management and execution
- Automatic process monitoring and restart capabilities
- Graceful shutdown handling with signal management
- Environment-based configuration (PORT, etc.)
- Comprehensive logging and error handling
- Health monitoring and recovery mechanisms

Key Features:
- Asynchronous process management using asyncio
- Signal handling for SIGINT and SIGTERM (graceful shutdown)
- Automatic restart of failed FastAPI processes
- Environment variable configuration support
- Detailed logging with structured output
- Timeout-based process termination
- Cross-platform compatibility

Server Management:
- Starts FastAPI server using uvicorn on configurable port
- Monitors server health every 5 seconds
- Automatically restarts server if it crashes
- Handles graceful shutdown on container stop signals
- Provides detailed logging of server lifecycle events

Environment Configuration:
- PORT: Server port (default: 8000)
- Other environment variables passed through to FastAPI app

Usage:
    python run_combined_server.py                    # Run with default port 8000
    PORT=4000 python run_combined_server.py         # Run on custom port
    docker run -e PORT=8000 blast-api:latest        # Run in container

Signal Handling:
- SIGINT (Ctrl+C): Graceful shutdown
- SIGTERM (docker stop): Graceful shutdown
- Automatic process restart on unexpected failures

Process Lifecycle:
1. Initialize server manager
2. Set up signal handlers
3. Start FastAPI server process
4. Monitor process health continuously
5. Restart on failure or shutdown on signal
6. Clean up resources on exit

Dependencies:
    - asyncio: Asynchronous I/O and process management
    - subprocess: Process creation and management
    - signal: Signal handling for graceful shutdown
    - logging: Structured logging and debugging
    - uvicorn: ASGI server for FastAPI (external dependency)

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""


import asyncio
import logging
import subprocess
import sys
import signal
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CombinedServer:
    """Manages FastAPI server process with monitoring and graceful shutdown capabilities."""

    def __init__(self):
        self.fastapi_process = None
        self.running = True

    def signal_handler(self, signum, frame):  # pylint: disable=unused-argument
        """Handle shutdown signals"""
        logger.info("Received signal %d, shutting down...", signum)
        self.running = False
        self.shutdown()

    def shutdown(self):
        """Shutdown FastAPI server"""
        logger.info("Shutting down server...")
        if self.fastapi_process:
            logger.info("Terminating FastAPI server...")
            self.fastapi_process.terminate()
            try:
                self.fastapi_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("FastAPI server didn't terminate gracefully, killing...")
                self.fastapi_process.kill()

        logger.info("Server shut down")

    async def run_fastapi(self):
        """Run the FastAPI server"""
        # Get port from environment variable, default to 8000
        port = os.environ.get("PORT", "8000")
        logger.info(
            "Starting FastAPI server with MCP-like endpoints on port %s...", port
        )
        self.fastapi_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app:app",
                "--host",
                "0.0.0.0",
                "--port",
                port,
            ]
        )
        logger.info(
            "FastAPI server started with PID: %d on port %s",
            self.fastapi_process.pid,
            port,
        )
        return self.fastapi_process

    async def monitor_process(self):
        """Monitor FastAPI process and restart if needed"""
        while self.running:
            # Check FastAPI process
            if self.fastapi_process and self.fastapi_process.poll() is not None:
                logger.error("FastAPI server died, restarting...")
                await self.run_fastapi()

            await asyncio.sleep(5)  # Check every 5 seconds

    async def main(self):
        """Run FastAPI server with monitoring"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info("Starting combined server...")

        try:
            # Start FastAPI server
            await self.run_fastapi()

            # Monitor process
            await self.monitor_process()

        except Exception as e:
            logger.error("Error in combined server: %s", e)
            self.shutdown()
            raise


if __name__ == "__main__":
    server = CombinedServer()
    asyncio.run(server.main())
