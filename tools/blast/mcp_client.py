#!/usr/bin/env python3
"""
MCP client for BLASTp server using the MCP protocol
"""

import json
import requests
import uuid
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client for communicating with MCP servers"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8002):
        self.base_url = f"http://{host}:{port}/mcp"
        self.session_id = str(uuid.uuid4())
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "MCP-Session-ID": self.session_id
        }
    
    def _make_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method
        }
        if params:
            payload["params"] = params
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": f"Request failed: {e}"}
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP session"""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "blastp-test-client",
                "version": "1.0.0"
            }
        }
        return self._make_request("initialize", params)
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return self._make_request("tools/list")
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        params = {
            "name": name,
            "arguments": arguments
        }
        return self._make_request("tools/call", params)


def main():
    """Test the MCP client"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP BLASTp client")
    parser.add_argument("--host", default="127.0.0.1", help="MCP server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8002, help="MCP server port (default: 8002)")
    parser.add_argument("--sequence", default="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG", help="Sequence to test")
    args = parser.parse_args()
    
    client = MCPClient(args.host, args.port)
    
    print("Testing MCP BLASTp client...")
    print("=" * 50)
    
    # Initialize the session
    print("Initializing MCP session...")
    init_result = client.initialize()
    if "error" in init_result:
        print(f"❌ Initialization failed: {init_result['error']}")
        return
    
    print("✅ Session initialized")
    print(f"Session ID: {client.session_id}")
    
    # List tools
    print("\nListing available tools...")
    tools_result = client.list_tools()
    if "error" in tools_result:
        print(f"❌ Failed to list tools: {tools_result['error']}")
        return
    
    print("✅ Tools listed successfully")
    if "result" in tools_result and "tools" in tools_result["result"]:
        for tool in tools_result["result"]["tools"]:
            print(f"  - {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}")
    
    # Call the BLAST tool
    print(f"\nCalling BLAST tool with sequence: {args.sequence[:50]}...")
    call_result = client.call_tool(
        "blastp_search_flexible_db_tabular",
        {
            "sequence": args.sequence,
            "database": "swissprot",
            "evalue": 0.001,
            "max_target_seqs": 5
        }
    )
    
    if "error" in call_result:
        print(f"❌ Tool call failed: {call_result['error']}")
        return
    
    print("✅ Tool call successful")
    print("Result:")
    print(json.dumps(call_result, indent=2))


if __name__ == "__main__":
    main() 