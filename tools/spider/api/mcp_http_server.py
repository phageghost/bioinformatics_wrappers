"""HTTP server wrapper for MCP server"""

import asyncio
import logging
import json
import tempfile
import os
from pathlib import Path
from typing import Any, Dict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import Tool, TextContent
from .spider_service import SpiderService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server"""
    
    def __init__(self, *args, mcp_server=None, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/mcp':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'MCP Server is running')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/mcp':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse the request
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Handle the request
                response = self.handle_mcp_request(request_data)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                logger.error('Error handling request: %s', e)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def handle_mcp_request(self, request_data):
        """Handle MCP request"""
        # This is a simplified implementation
        # In a real implementation, you would need to handle the full MCP protocol
        return {'status': 'ok', 'message': 'MCP request received'}

class MCPHTTPServer:
    """HTTP server wrapper for MCP server"""
    
    def __init__(self, host='0.0.0.0', port=8001):
        self.host = host
        self.port = port
        self.server = None
        self.mcp_server = SpiderMCPServer()
    
    def start(self):
        """Start the HTTP server"""
        logger.info('Starting MCP HTTP server on http://%s:%d', self.host, self.port)
        
        # Create a custom handler class with the MCP server
        class Handler(MCPHTTPHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, mcp_server=self.mcp_server, **kwargs)
        
        self.server = HTTPServer((self.host, self.port), Handler)
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        logger.info('MCP HTTP server started')
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info('MCP HTTP server stopped')

class SpiderMCPServer:
    """MCP Server for SPIDER protein druggability prediction"""
    def __init__(self):
        self.server = Server('spider-bioinformatics')
        self.spider_service = SpiderService()
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools():
            return [
                Tool(
                    name='predict_druggability',
                    title='Predict Druggability',
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
                    title='Get Tool Info',
                    description='Get information about the SPIDER tool',
                    inputSchema={
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]):
            try:
                if name == 'predict_druggability':
                    return await self._handle_predict_druggability(arguments)
                elif name == 'get_tool_info':
                    return await self._handle_get_tool_info(arguments)
                else:
                    raise ValueError(f'Unknown tool: {name}')
            except Exception as e:
                logger.error('Error in tool call %s: %s', name, str(e))
                return [
                    TextContent(
                        type='text',
                        text=f'Error: {str(e)}'
                    )
                ]

    async def _handle_predict_druggability(self, arguments: Dict[str, Any]):
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
                return [
                    TextContent(
                        type='text',
                        text=result_text
                    )
                ]
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)

    async def _handle_get_tool_info(self, arguments: Dict[str, Any]):
        tool_info = self.spider_service.get_tool_info()
        info_text = f"""
SPIDER Tool Information:
- Name: {tool_info.get('name', 'Unknown')}
- Version: {tool_info.get('version', 'Unknown')}
- Description: {tool_info.get('description', 'Unknown')}
- Input Format: {tool_info.get('input_format', 'Unknown')}
- Output Format: {tool_info.get('output_format', 'Unknown')}
"""
        return [
            TextContent(
                type='text',
                text=info_text
            )
        ]

def main():
    """Main function"""
    server = MCPHTTPServer()
    try:
        server.start()
        # Keep the server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Shutting down...')
        server.stop()

if __name__ == '__main__':
    main() 