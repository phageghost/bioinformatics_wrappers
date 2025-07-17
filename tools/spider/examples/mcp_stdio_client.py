"""STDIO MCP client for testing SPIDER MCP server"""

import asyncio
import logging

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test the SPIDER MCP STDIO server"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "api.mcp_server"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize(
                protocol_version='2024-11-05',
                client_info={
                    'name': 'spider-stdio-test-client',
                    'version': '1.0.0'
                },
                capabilities={}
            )
            logger.info('Connected to SPIDER MCP STDIO server')
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
            logger.info('\nMCP STDIO test completed successfully!')

if __name__ == '__main__':
    asyncio.run(main()) 