"""Streamable HTTP MCP client for testing SPIDER MCP server"""

import asyncio
import logging

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test the SPIDER MCP Streamable HTTP server"""
    async with streamablehttp_client(url='http://localhost:8001') as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize(
                protocol_version='2024-11-05',
                client_info={
                    'name': 'spider-streamable-http-test-client',
                    'version': '1.0.0'
                },
                capabilities={}
            )
            logger.info('Connected to SPIDER MCP Streamable HTTP server')
            # List available tools
            tools = await session.list_tools()
            logger.info('Available tools:')
            for tool in tools.tools:
                logger.info('  - %s: %s', tool.name, tool.description)
            # Example 1: Get tool information
            logger.info('\n=== Getting tool information ===')
            result = await session.call_tool('get_tool_info', {})
            if result.content:
                logger.info('Tool info:')
                for content in result.content:
                    if hasattr(content, 'text'):
                        logger.info(content.text)
            # Example 2: Predict druggability
            logger.info('\n=== Predicting druggability ===')
            sequence = 'MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG'
            result = await session.call_tool('predict_druggability', {'sequence': sequence})
            if result.content:
                logger.info('Prediction result:')
                for content in result.content:
                    if hasattr(content, 'text'):
                        logger.info(content.text)
            else:
                logger.error('No content in result')
            logger.info('\nMCP Streamable HTTP test completed successfully!')

if __name__ == '__main__':
    asyncio.run(main()) 