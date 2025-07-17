#!/usr/bin/env python3
"""Test MCP server in stdio mode"""

import asyncio
import subprocess
import sys
import logging

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_stdio():
    """Test the MCP server in stdio mode"""
    logger.info("Testing MCP server in stdio mode...")
    
    # Create server parameters to run the MCP server in stdio mode
    server_params = StdioServerParameters(
        command="docker",
        args=["exec", "-i", "spider-api", "micromamba", "run", "-n", "api", "python", "-m", "api.mcp_server"],
        cwd="."
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write, client_info={
                'name': 'spider-stdio-test-client',
                'version': '1.0.0'
            }) as session:
                # Initialize the session
                await session.initialize()
                logger.info('Connected to SPIDER MCP stdio server')
                
                # List available tools
                tools = await session.list_tools()
                logger.info('Available tools:')
                for tool in tools.tools:
                    logger.info('  - %s: %s', tool.name, tool.description)
                
                # Test get_tool_info
                logger.info('\n=== Testing get_tool_info ===')
                result = await session.call_tool('get_tool_info', {})
                if result.content:
                    logger.info('Tool info:')
                    for content in result.content:
                        if hasattr(content, 'text'):
                            logger.info(content.text)
                
                # Test predict_druggability
                logger.info('\n=== Testing predict_druggability ===')
                sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
                result = await session.call_tool('predict_druggability', {'sequence': sequence})
                if result.content:
                    logger.info('Prediction result:')
                    for content in result.content:
                        if hasattr(content, 'text'):
                            logger.info(content.text)
                else:
                    logger.error('No content in result')
                
                logger.info('\nMCP stdio test completed successfully!')
                
    except Exception as e:
        logger.error('Error testing MCP stdio: %s', str(e))
        raise

if __name__ == '__main__':
    asyncio.run(test_mcp_stdio()) 