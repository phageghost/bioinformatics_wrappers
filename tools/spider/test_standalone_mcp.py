"""Test standalone MCP server"""

import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test standalone MCP server"""
    logger.info("Creating FastMCP server...")
    mcp_server = FastMCP(
        name="test-spider",
        instructions="Test SPIDER MCP server"
    )
    
    @mcp_server.tool(
        name="test_tool",
        title="Test Tool",
        description="A simple test tool"
    )
    async def test_tool():
        return [TextContent(type="text", text="Hello from test tool!")]
    
    logger.info("Creating MCP streamable HTTP app...")
    mcp_app = mcp_server.streamable_http_app()
    logger.info("MCP app created successfully")
    
    # Print routes
    logger.info("MCP app routes:")
    for route in mcp_app.routes:
        logger.info(f"  {route.path} -> {type(route).__name__}")
        if hasattr(route, 'app') and hasattr(route.app, 'routes'):
            logger.info(f"    Mounted app routes:")
            for sub_route in route.app.routes:
                logger.info(f"      {sub_route.path} -> {type(sub_route).__name__}")
        elif hasattr(route, 'app'):
            logger.info(f"    Mounted app type: {type(route.app)}")
    
    logger.info("Test completed")

if __name__ == '__main__':
    asyncio.run(main()) 