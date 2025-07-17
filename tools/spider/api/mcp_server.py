"""MCP Server for SPIDER Bioinformatics Tool"""

import asyncio
import logging
import tempfile
import os
import argparse
from pathlib import Path
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http import StreamableHTTPServerTransport
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

from .spider_service import SpiderService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpiderMCPServer:
    """MCP Server for SPIDER protein druggability prediction"""
    def __init__(self):
        self.server = Server('spider-bioinformatics')
        self.spider_service = SpiderService()
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name='predict_druggability',
                        description='Predict druggability of a protein sequence using SPIDER',
                        inputSchema={
                            'type': 'object',
                            'properties': {
                                'sequence': {
                                    'type': 'string',
                                    'description': 'Protein sequence to analyze'
                                }
                            },
                            'required': ['sequence']
                        }
                    ),
                    Tool(
                        name='get_tool_info',
                        description='Get information about the SPIDER tool',
                        inputSchema={
                            'type': 'object',
                            'properties': {},
                            'required': []
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            try:
                if name == 'predict_druggability':
                    return await self._handle_predict_druggability(arguments)
                elif name == 'get_tool_info':
                    return await self._handle_get_tool_info(arguments)
                else:
                    raise ValueError(f'Unknown tool: {name}')
            except Exception as e:
                logger.error('Error in tool call %s: %s', name, str(e))
                return CallToolResult(
                    content=[
                        TextContent(
                            type='text',
                            text=f'Error: {str(e)}'
                        )
                    ],
                    isError=True
                )

    async def _handle_predict_druggability(self, arguments: Dict[str, Any]) -> CallToolResult:
        sequence = arguments.get('sequence')
        if not sequence:
            raise ValueError('Sequence is required')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
            try:
                fasta_content = f'>sequence\n{sequence.strip()}\n'
                temp_file.write(fasta_content.encode('utf-8'))
                temp_file.flush()
                if not self.spider_service.validate_fasta_file(Path(temp_file.name)):
                    raise ValueError('Invalid sequence format')
                success, message, result = self.spider_service.run_spider_prediction(Path(temp_file.name))
                if not success:
                    raise ValueError(f'SPIDER prediction failed: {message}')
                if hasattr(result, 'label') and hasattr(result, 'probability'):
                    prediction = result.label
                    probability = result.probability
                else:
                    prediction = 'Unknown'
                    probability = 'Unknown'
                result_text = f"""
SPIDER Prediction Results:
- Status: Success
- Prediction: {prediction}
- Probability: {probability}
- Message: {message}
"""
                return CallToolResult(
                    content=[
                        TextContent(
                            type='text',
                            text=result_text
                        )
                    ]
                )
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)

    async def _handle_get_tool_info(self, arguments: Dict[str, Any]) -> CallToolResult:
        tool_info = self.spider_service.get_tool_info()
        info_text = f"""
SPIDER Tool Information:
- Name: {tool_info.get('name', 'Unknown')}
- Version: {tool_info.get('version', 'Unknown')}
- Description: {tool_info.get('description', 'Unknown')}
- Input Format: {tool_info.get('input_format', 'Unknown')}
- Output Format: {tool_info.get('output_format', 'Unknown')}
"""
        return CallToolResult(
            content=[
                TextContent(
                    type='text',
                    text=info_text
                )
            ]
        )

    async def run_stdio(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name='spider-bioinformatics',
                    server_version='1.0.0',
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={},
                    ),
                ),
            )

    async def run_streamable_http(self, host: str = '0.0.0.0', port: int = 8001):
        transport = StreamableHTTPServerTransport(mcp_session_id=None)
        logger.info('MCP Streamable HTTP server running on http://%s:%d', host, port)
        async with transport.connect() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name='spider-bioinformatics',
                    server_version='1.0.0',
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={},
                    ),
                ),
            )

def parse_args():
    parser = argparse.ArgumentParser(description='SPIDER MCP Server')
    parser.add_argument('--streamable-http', action='store_true', help='Run Streamable HTTP server')
    parser.add_argument('--host', default='0.0.0.0', help='host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8001, help='port (default: 8001)')
    return parser.parse_args()

async def main():
    args = parse_args()
    server = SpiderMCPServer()
    if args.streamable_http:
        await server.run_streamable_http(args.host, args.port)
    else:
        await server.run_stdio()

if __name__ == '__main__':
    asyncio.run(main()) 