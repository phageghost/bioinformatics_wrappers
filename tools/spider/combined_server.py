"""Combined server for SPIDER - supports both REST API and MCP protocol"""

import asyncio
import logging
import multiprocessing
import sys
from typing import Optional

import uvicorn

# Try to import MCP server
try:
    from api.mcp_server import SpiderMCPServer
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    SpiderMCPServer = None
    print(f"MCP not available: {e}")

from app import app as rest_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CombinedServer:
    """Server that can run both REST API and MCP server"""
    
    def __init__(self, rest_port: int = 8000, enable_mcp: bool = True, mcp_streamable_http: bool = False, mcp_host: str = "0.0.0.0", mcp_port: int = 81):
        self.rest_port = rest_port
        self.enable_mcp = enable_mcp and MCP_AVAILABLE
        self.mcp_streamable_http = mcp_streamable_http
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port
        self.rest_process: Optional[multiprocessing.Process] = None
        self.mcp_process: Optional[multiprocessing.Process] = None
        self.shutdown_event = multiprocessing.Event()
        
        if enable_mcp and not MCP_AVAILABLE:
            logger.warning("MCP not available - running REST API only")
    
    def start_rest_server(self):
        """Start the REST API server in a separate process"""
        def run_rest_server():
            uvicorn.run(
                rest_app,
                host="0.0.0.0",
                port=self.rest_port,
                log_level="info"
            )
        
        self.rest_process = multiprocessing.Process(target=run_rest_server)
        self.rest_process.start()
        logger.info(f"REST API server started on port {self.rest_port}")
    
    def start_mcp_server(self):
        """Start the MCP server in a separate process"""
        if not MCP_AVAILABLE:
            logger.warning("Cannot start MCP server - MCP package not available")
            return
        
        def run_mcp_server():
            try:
                if self.mcp_streamable_http:
                    asyncio.run(SpiderMCPServer().run_streamable_http(self.mcp_host, self.mcp_port))
                else:
                    asyncio.run(SpiderMCPServer().run_stdio())
            except KeyboardInterrupt:
                logger.info("MCP server stopped")
        
        self.mcp_process = multiprocessing.Process(target=run_mcp_server)
        self.mcp_process.start()
        if self.mcp_streamable_http:
            logger.info(f"MCP Streamable HTTP server started on http://{self.mcp_host}:{self.mcp_port}")
        else:
            logger.info("MCP stdio server started")
    
    def start(self):
        """Start both servers"""
        try:
            # Start REST API server
            self.start_rest_server()
            
            # Start MCP server if enabled and available
            if self.enable_mcp:
                self.start_mcp_server()
            
            logger.info("Combined server started successfully")
            logger.info(f"REST API available at: http://localhost:{self.rest_port}")
            if self.enable_mcp:
                if self.mcp_streamable_http:
                    logger.info(f"MCP Streamable HTTP available at: http://localhost:{self.mcp_port}")
                else:
                    logger.info("MCP server available via stdio")
            else:
                logger.info("MCP server not available")
            
            # Wait for shutdown signal
            while not self.shutdown_event.is_set():
                asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown both servers"""
        logger.info("Shutting down servers...")
        
        if self.rest_process and self.rest_process.is_alive():
            self.rest_process.terminate()
            self.rest_process.join(timeout=5)
            if self.rest_process.is_alive():
                self.rest_process.kill()
            logger.info("REST API server stopped")
        
        if self.mcp_process and self.mcp_process.is_alive():
            self.mcp_process.terminate()
            self.mcp_process.join(timeout=5)
            if self.mcp_process.is_alive():
                self.mcp_process.kill()
            logger.info("MCP server stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SPIDER Combined Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for REST API server (default: 8000)"
    )
    parser.add_argument(
        "--rest-only",
        action="store_true",
        help="Run only REST API server"
    )
    parser.add_argument(
        "--mcp-only",
        action="store_true",
        help="Run only MCP server"
    )
    parser.add_argument(
        "--mcp-streamable-http",
        action="store_true",
        help="Run MCP server over Streamable HTTP instead of stdio"
    )
    parser.add_argument(
        "--mcp-host",
        default="0.0.0.0",
        help="MCP Streamable HTTP host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--mcp-port",
        type=int,
        default=8001,
        help="MCP Streamable HTTP port (default: 8001)"
    )
    
    args = parser.parse_args()
    
    if args.rest_only:
        # Run only REST API
        logger.info("Starting REST API server only")
        uvicorn.run(rest_app, host="0.0.0.0", port=args.port)
    elif args.mcp_only:
        # Run only MCP server
        if not MCP_AVAILABLE:
            logger.error("MCP server not available - MCP package not installed")
            sys.exit(1)
        logger.info("Starting MCP server only")
        if args.mcp_streamable_http:
            asyncio.run(SpiderMCPServer().run_streamable_http(args.mcp_host, args.mcp_port))
        else:
            asyncio.run(SpiderMCPServer().run_stdio())
    else:
        # Run combined server
        server = CombinedServer(
            rest_port=args.port, 
            enable_mcp=True, 
            mcp_streamable_http=args.mcp_streamable_http,
            mcp_host=args.mcp_host,
            mcp_port=args.mcp_port
        )
        server.start()


if __name__ == "__main__":
    main() 