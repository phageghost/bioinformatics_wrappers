#!/usr/bin/env python3
"""
Combined Server Entrypoint Module

This module provides the main entrypoint for running the SPIDER API server in a Docker
container. It manages the FastAPI application process with monitoring and graceful
shutdown capabilities.

The CombinedServer class handles:
- Starting the FastAPI server with configurable port
- Process monitoring and automatic restart on failure
- Signal handling for graceful shutdown (SIGINT, SIGTERM)
- Environment variable configuration (PORT)
- Logging and error reporting

Key Features:
- Environment-based port configuration (defaults to 8000)
- Automatic process restart on failure
- Graceful shutdown with timeout handling
- Comprehensive logging for Docker environments
- Signal handling for container orchestration

Usage:
    This module is typically executed as the main entrypoint in Docker containers.
    It reads the PORT environment variable and starts the FastAPI server accordingly.

Environment Variables:
    PORT: Server port (default: 8000)

Dependencies:
    - asyncio: Asynchronous I/O
    - subprocess: Process management
    - uvicorn: ASGI server for FastAPI
    - signal: Signal handling

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
