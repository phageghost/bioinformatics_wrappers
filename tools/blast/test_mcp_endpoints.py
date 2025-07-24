#!/usr/bin/env python3
"""
BLAST MCP-like Endpoints Test Suite

This module provides comprehensive testing for the BLAST MCP-like endpoints that enable
AI agent integration. It tests the Model Context Protocol (MCP) compatible interface
that allows AI agents to discover and call BLAST tools programmatically.

The BlastMCPEndpointTester class provides:
- Automated testing of MCP-like tool discovery endpoints
- Validation of tool schemas and input/output formats
- Testing of tool execution with various parameter combinations
- Error condition testing and edge case handling
- Performance timing and detailed logging
- Configurable test parameters (host, port)

Test Coverage:
- Tool discovery endpoint (/mcp/tools)
- Tool schema validation and structure verification
- Tool execution endpoint (/mcp/call) with valid parameters
- Tool execution with invalid/missing parameters
- Error handling for unknown tools and malformed requests
- Content-Type header handling
- MCP endpoint structure compliance

Key Features:
- Command-line argument parsing for flexible testing
- Detailed test result logging with emoji indicators
- Configurable base URL for different environments
- Comprehensive error handling and reporting
- Summary statistics and pass/fail reporting
- MCP protocol compliance validation

Usage:
    python test_mcp_endpoints.py [--host HOST] [--port PORT]

    Examples:
        python test_mcp_endpoints.py                    # Test localhost:8001
        python test_mcp_endpoints.py --port 4000        # Test localhost:4000
        python test_mcp_endpoints.py --host 192.168.1.100 --port 8001

MCP Protocol Features Tested:
- Tool discovery and metadata
- Input schema validation
- Tool execution with arguments
- Error handling and status codes
- Response format compliance
- Content-Type handling

Dependencies:
    - requests: HTTP client for API testing
    - argparse: Command-line argument parsing
    - json: JSON response parsing
    - typing: Type hints for better code documentation

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""


import argparse
from typing import Dict, Any
import requests


class BlastMCPEndpointTester:
    """Test suite for BLAST MCP-like endpoints"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append(
            {"test": test_name, "success": success, "details": details}
        )

    def test_list_tools_endpoint(self) -> bool:
        """Test the list tools endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/mcp/tools")
            if response.status_code == 200:
                data = response.json()
                if "tools" in data and isinstance(data["tools"], list):
                    tools = data["tools"]
                    expected_tools = ["perform_blastp_search", "get_tool_info"]
                    tool_names = [tool["name"] for tool in tools]

                    if all(tool in tool_names for tool in expected_tools):
                        self.log_test(
                            "List Tools",
                            True,
                            f"Found {len(tools)} tools: {', '.join(tool_names)}",
                        )
                        return True
                    else:
                        self.log_test(
                            "List Tools",
                            False,
                            f"Missing expected tools. Found: {tool_names}",
                        )
                        return False
                else:
                    self.log_test("List Tools", False, "Response missing 'tools' array")
                    return False
            else:
                self.log_test(
                    "List Tools", False, f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("List Tools", False, f"Exception: {str(e)}")
            return False

    def test_tool_schemas(self) -> bool:
        """Test that tools have proper schemas"""
        try:
            response = self.session.get(f"{self.base_url}/mcp/tools")
            if response.status_code == 200:
                data = response.json()
                tools = data["tools"]

                for tool in tools:
                    if "inputSchema" not in tool:
                        self.log_test(
                            "Tool Schemas",
                            False,
                            f"Tool {tool.get('name', 'unknown')} missing inputSchema",
                        )
                        return False

                self.log_test(
                    "Tool Schemas", True, f"All {len(tools)} tools have proper schemas"
                )
                return True
            else:
                self.log_test("Tool Schemas", False, f"HTTP {response.status_code}")
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Tool Schemas", False, f"Exception: {str(e)}")
            return False

    def test_get_tool_info_call(self) -> bool:
        """Test calling the get_tool_info tool"""
        try:
            payload = {"name": "get_tool_info", "arguments": {}}
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 200:
                data = response.json()
                if "content" in data and isinstance(data["content"], list):
                    content = data["content"]
                    if len(content) > 0 and "text" in content[0]:
                        text = content[0]["text"]
                        if "BLASTp Tool Information" in text:
                            self.log_test(
                                "Get Tool Info Call",
                                True,
                                "Successfully retrieved tool information",
                            )
                            return True
                        else:
                            self.log_test(
                                "Get Tool Info Call",
                                False,
                                "Response doesn't contain expected tool info",
                            )
                            return False
                    else:
                        self.log_test(
                            "Get Tool Info Call",
                            False,
                            "Response missing content or text",
                        )
                        return False
                else:
                    self.log_test(
                        "Get Tool Info Call", False, "Response missing 'content' array"
                    )
                    return False
            else:
                self.log_test(
                    "Get Tool Info Call",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Get Tool Info Call", False, f"Exception: {str(e)}")
            return False

    def test_perform_blastp_search_call_valid(self) -> bool:
        """Test calling perform_blastp_search with valid sequence"""
        try:
            sequence = (
                "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            )
            payload = {
                "name": "perform_blastp_search",
                "arguments": {"sequence": sequence, "db_name": "pdbaa"},
            }
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 200:
                data = response.json()
                if "content" in data and isinstance(data["content"], list):
                    content = data["content"]
                    if len(content) > 0 and "text" in content[0]:
                        text = content[0]["text"]
                        if (
                            "BLASTp Search Results" in text
                            and "Status: Success" in text
                        ):
                            self.log_test(
                                "Perform BLASTp Search (Valid)",
                                True,
                                "Successfully performed BLASTp search",
                            )
                            return True
                        else:
                            self.log_test(
                                "Perform BLASTp Search (Valid)",
                                False,
                                "Response doesn't contain expected search results",
                            )
                            return False
                    else:
                        self.log_test(
                            "Perform BLASTp Search (Valid)",
                            False,
                            "Response missing content or text",
                        )
                        return False
                else:
                    self.log_test(
                        "Perform BLASTp Search (Valid)",
                        False,
                        "Response missing 'content' array",
                    )
                    return False
            else:
                self.log_test(
                    "Perform BLASTp Search (Valid)",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test(
                "Perform BLASTp Search (Valid)", False, f"Exception: {str(e)}"
            )
            return False

    def test_perform_blastp_search_call_invalid_empty(self) -> bool:
        """Test calling perform_blastp_search with empty sequence"""
        try:
            payload = {"name": "perform_blastp_search", "arguments": {"sequence": ""}}
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 400:
                self.log_test(
                    "Perform BLASTp Search (Invalid - Empty)",
                    True,
                    "Correctly rejected empty sequence",
                )
                return True
            else:
                self.log_test(
                    "Perform BLASTp Search (Invalid - Empty)",
                    False,
                    f"Expected 400, got {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test(
                "Perform BLASTp Search (Invalid - Empty)", False, f"Exception: {str(e)}"
            )
            return False

    def test_perform_blastp_search_call_invalid_missing(self) -> bool:
        """Test calling perform_blastp_search with missing sequence"""
        try:
            payload = {"name": "perform_blastp_search", "arguments": {}}
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 400:
                self.log_test(
                    "Perform BLASTp Search (Invalid - Missing)",
                    True,
                    "Correctly rejected missing sequence",
                )
                return True
            else:
                self.log_test(
                    "Perform BLASTp Search (Invalid - Missing)",
                    False,
                    f"Expected 400, got {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test(
                "Perform BLASTp Search (Invalid - Missing)",
                False,
                f"Exception: {str(e)}",
            )
            return False

    def test_perform_blastp_search_call_with_parameters(self) -> bool:
        """Test calling perform_blastp_search with all parameters"""
        try:
            sequence = (
                "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            )
            payload = {
                "name": "perform_blastp_search",
                "arguments": {
                    "sequence": sequence,
                    "db_name": "pdbaa",
                    "evalue": 0.01,
                    "max_target_seqs": 5,
                    "outfmt": "6 qseqid sseqid pident length evalue bitscore",
                },
            }
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 200:
                data = response.json()
                if "content" in data and isinstance(data["content"], list):
                    content = data["content"]
                    if len(content) > 0 and "text" in content[0]:
                        text = content[0]["text"]
                        if (
                            "BLASTp Search Results" in text
                            and "Status: Success" in text
                        ):
                            self.log_test(
                                "Perform BLASTp Search (With Parameters)",
                                True,
                                "Successfully performed BLASTp search with custom parameters",
                            )
                            return True
                        else:
                            self.log_test(
                                "Perform BLASTp Search (With Parameters)",
                                False,
                                "Response doesn't contain expected search results",
                            )
                            return False
                    else:
                        self.log_test(
                            "Perform BLASTp Search (With Parameters)",
                            False,
                            "Response missing content or text",
                        )
                        return False
                else:
                    self.log_test(
                        "Perform BLASTp Search (With Parameters)",
                        False,
                        "Response missing 'content' array",
                    )
                    return False
            else:
                self.log_test(
                    "Perform BLASTp Search (With Parameters)",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test(
                "Perform BLASTp Search (With Parameters)", False, f"Exception: {str(e)}"
            )
            return False

    def test_unknown_tool_call(self) -> bool:
        """Test calling an unknown tool"""
        try:
            payload = {"name": "unknown_tool", "arguments": {}}
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 400:
                self.log_test(
                    "Unknown Tool Call", True, "Correctly rejected unknown tool"
                )
                return True
            else:
                self.log_test(
                    "Unknown Tool Call",
                    False,
                    f"Expected 400, got {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Unknown Tool Call", False, f"Exception: {str(e)}")
            return False

    def test_malformed_json(self) -> bool:
        """Test handling of malformed JSON"""
        try:
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                data="invalid json",
            )
            if response.status_code == 422:  # FastAPI validation error
                self.log_test(
                    "Malformed JSON", True, "Correctly rejected malformed JSON"
                )
                return True
            else:
                self.log_test(
                    "Malformed JSON", False, f"Expected 422, got {response.status_code}"
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Malformed JSON", False, f"Exception: {str(e)}")
            return False

    def test_missing_content_type(self) -> bool:
        """Test handling of missing Content-Type header"""
        try:
            payload = {"name": "get_tool_info", "arguments": {}}
            response = self.session.post(
                f"{self.base_url}/mcp/call", json=payload  # No Content-Type header
            )
            if response.status_code == 200:  # FastAPI can handle this
                self.log_test(
                    "Missing Content-Type",
                    True,
                    "Successfully handled missing Content-Type",
                )
                return True
            else:
                self.log_test(
                    "Missing Content-Type",
                    False,
                    f"Unexpected status: {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Missing Content-Type", False, f"Exception: {str(e)}")
            return False

    def test_mcp_endpoint_structure(self) -> bool:
        """Test that MCP endpoints follow expected structure"""
        try:
            # Test tools endpoint structure
            response = self.session.get(f"{self.base_url}/mcp/tools")
            if response.status_code == 200:
                data = response.json()
                tools = data["tools"]

                for tool in tools:
                    required_fields = ["name", "title", "description", "inputSchema"]
                    if not all(field in tool for field in required_fields):
                        self.log_test(
                            "MCP Endpoint Structure",
                            False,
                            f"Tool {tool.get('name', 'unknown')} missing required fields",
                        )
                        return False

                self.log_test(
                    "MCP Endpoint Structure",
                    True,
                    "All tools have required MCP structure",
                )
                return True
            else:
                self.log_test(
                    "MCP Endpoint Structure", False, f"HTTP {response.status_code}"
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("MCP Endpoint Structure", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("🧪 Testing BLAST MCP-like Endpoints")
        print("=" * 50)

        tests = [
            self.test_list_tools_endpoint,
            self.test_tool_schemas,
            self.test_get_tool_info_call,
            self.test_perform_blastp_search_call_valid,
            self.test_perform_blastp_search_call_with_parameters,
            self.test_perform_blastp_search_call_invalid_empty,
            self.test_perform_blastp_search_call_invalid_missing,
            self.test_unknown_tool_call,
            self.test_malformed_json,
            self.test_missing_content_type,
            self.test_mcp_endpoint_structure,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if test():
                passed += 1

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! MCP-like endpoints are working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "results": self.test_results,
        }


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test BLAST MCP-like endpoints")
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port number for the API server (default: 8001)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for the API server (default: localhost)",
    )

    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    print(f"🧪 Testing BLAST MCP-like endpoints at {base_url}")

    tester = BlastMCPEndpointTester(base_url=base_url)
    results = tester.run_all_tests()

    # Exit with appropriate code
    if results["passed"] == results["total"]:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
