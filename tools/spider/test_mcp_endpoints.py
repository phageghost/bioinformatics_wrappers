#!/usr/bin/env python3
"""
SPIDER MCP-like Endpoints Test Suite

This module provides comprehensive testing for the SPIDER MCP-like endpoints that
enable AI agent integration. It tests the MCP-compatible interface that allows
AI agents to discover and call SPIDER tools programmatically.

The SpiderMCPEndpointTester class provides:
- Automated testing of MCP-like endpoint functionality
- Tool discovery and schema validation testing
- Tool execution with various input parameters
- Error handling and edge case testing
- Response format validation for AI agent compatibility

Test Coverage:
- Tool listing endpoint (/mcp/tools)
- Tool schema validation and structure
- predict_druggability tool execution
- get_tool_info tool execution
- Invalid tool name handling
- Malformed request handling
- Missing Content-Type header handling
- Response format validation for MCP compatibility

Key Features:
- Command-line argument parsing for flexible testing
- Detailed test result logging and reporting
- Configurable base URL for different environments
- Comprehensive error handling and reporting
- MCP protocol compliance validation
- Summary statistics and pass/fail reporting

MCP-like Endpoints:
- GET /mcp/tools: List available tools with schemas
- POST /mcp/call: Execute tools with JSON arguments

Usage:
    python test_mcp_endpoints.py [--host HOST] [--port PORT]

    Examples:
        python test_mcp_endpoints.py                    # Test localhost:8000
        python test_mcp_endpoints.py --port 4000        # Test localhost:4000
        python test_mcp_endpoints.py --host 192.168.1.100 --port 8000

Dependencies:
    - requests: HTTP client for API testing
    - argparse: Command-line argument parsing
    - json: JSON request/response handling
    - time: Performance timing

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""


import argparse
from typing import Dict, Any
import requests


class SpiderMCPEndpointTester:
    """Test suite for SPIDER MCP-like endpoints"""

    def __init__(self, base_url: str = "http://localhost:8000"):
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
                    expected_tools = ["predict_druggability", "get_tool_info"]
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
                        if "SPIDER Tool Information" in text:
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

    def test_predict_druggability_call_valid(self) -> bool:
        """Test calling predict_druggability with valid sequence"""
        try:
            sequence = (
                "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            )
            payload = {
                "name": "predict_druggability",
                "arguments": {"sequence": sequence},
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
                            "SPIDER Prediction Results" in text
                            and "Status: Success" in text
                        ):
                            self.log_test(
                                "Predict Druggability (Valid)",
                                True,
                                "Successfully predicted druggability",
                            )
                            return True
                        else:
                            self.log_test(
                                "Predict Druggability (Valid)",
                                False,
                                "Response doesn't contain expected prediction",
                            )
                            return False
                    else:
                        self.log_test(
                            "Predict Druggability (Valid)",
                            False,
                            "Response missing content or text",
                        )
                        return False
                else:
                    self.log_test(
                        "Predict Druggability (Valid)",
                        False,
                        "Response missing 'content' array",
                    )
                    return False
            else:
                self.log_test(
                    "Predict Druggability (Valid)",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Predict Druggability (Valid)", False, f"Exception: {str(e)}")
            return False

    def test_predict_druggability_call_invalid_empty(self) -> bool:
        """Test calling predict_druggability with empty sequence"""
        try:
            payload = {"name": "predict_druggability", "arguments": {"sequence": ""}}
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 400:
                self.log_test(
                    "Predict Druggability (Invalid - Empty)",
                    True,
                    "Correctly rejected empty sequence",
                )
                return True
            else:
                self.log_test(
                    "Predict Druggability (Invalid - Empty)",
                    False,
                    f"Expected 400, got {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test(
                "Predict Druggability (Invalid - Empty)", False, f"Exception: {str(e)}"
            )
            return False

    def test_predict_druggability_call_invalid_missing(self) -> bool:
        """Test calling predict_druggability with missing sequence"""
        try:
            payload = {"name": "predict_druggability", "arguments": {}}
            response = self.session.post(
                f"{self.base_url}/mcp/call",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code == 400:
                self.log_test(
                    "Predict Druggability (Invalid - Missing)",
                    True,
                    "Correctly rejected missing sequence",
                )
                return True
            else:
                self.log_test(
                    "Predict Druggability (Invalid - Missing)",
                    False,
                    f"Expected 400, got {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test(
                "Predict Druggability (Invalid - Missing)",
                False,
                f"Exception: {str(e)}",
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
        print("🧪 Testing SPIDER MCP-like Endpoints")
        print("=" * 50)

        tests = [
            self.test_list_tools_endpoint,
            self.test_tool_schemas,
            self.test_get_tool_info_call,
            self.test_predict_druggability_call_valid,
            self.test_predict_druggability_call_invalid_empty,
            self.test_predict_druggability_call_invalid_missing,
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
    parser = argparse.ArgumentParser(description="Test SPIDER MCP-like endpoints")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for the API server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host for the API server (default: localhost)",
    )

    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"
    print(f"🧪 Testing SPIDER MCP-like endpoints at {base_url}")

    tester = SpiderMCPEndpointTester(base_url=base_url)
    results = tester.run_all_tests()

    # Exit with appropriate code
    if results["passed"] == results["total"]:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
