#!/usr/bin/env python3
"""
BLAST REST API Test Suite

This module provides comprehensive testing for the BLAST REST API endpoints.
It includes automated tests for all API functionality including health checks,
tool information, search endpoints, and error handling.

The BlastRESTAPITester class provides:
- Automated testing of all REST API endpoints
- Validation of response formats and data structures
- Error condition testing and edge case handling
- Performance timing and logging
- Configurable test parameters (host, port)

Test Coverage:
- Health check endpoint (/api/v1/blastp/health)
- Tool information endpoint (/api/v1/blastp/info)
- Search endpoint with valid sequences
- Search endpoint with invalid/missing parameters
- Error handling and status codes
- Response format validation
- Documentation endpoint accessibility

Key Features:
- Command-line argument parsing for flexible testing
- Detailed test result logging and reporting
- Configurable base URL for different environments
- Comprehensive error handling and reporting
- Summary statistics and pass/fail reporting

Usage:
    python test_rest_api.py [--host HOST] [--port PORT]

    Examples:
        python test_rest_api.py                    # Test localhost:8000
        python test_rest_api.py --port 4000        # Test localhost:4000
        python test_rest_api.py --host 192.168.1.100 --port 8000

Dependencies:
    - requests: HTTP client for API testing
    - argparse: Command-line argument parsing
    - json: JSON response parsing
    - time: Performance timing

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""


import argparse
from typing import Dict, Any

import requests


class BlastRESTAPITester:
    """Test suite for BLAST REST API"""

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

    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/blastp/health")
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "timestamp", "tool", "version"]
                if all(field in data for field in expected_fields):
                    self.log_test(
                        "Health Check",
                        True,
                        f"Status: {data['status']}, Tool: {data['tool']}",
                    )
                    return True
                else:
                    self.log_test(
                        "Health Check", False, f"Missing fields: {expected_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "Health Check",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["message", "version", "docs", "health"]
                if all(field in data for field in expected_fields):
                    self.log_test("Root Endpoint", True, f"Message: {data['message']}")
                    return True
                else:
                    self.log_test(
                        "Root Endpoint", False, f"Missing fields: {expected_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "Root Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_tool_info_endpoint(self) -> bool:
        """Test the tool info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/blastp/info")
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["name", "version", "description"]
                if all(field in data for field in expected_fields):
                    self.log_test(
                        "Tool Info", True, f"Tool: {data['name']} v{data['version']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Tool Info", False, f"Missing fields: {expected_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "Tool Info", False, f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Tool Info", False, f"Exception: {str(e)}")
            return False

    def test_search_endpoint_valid(self) -> bool:
        """Test search endpoint with valid sequence (table format)"""
        try:
            sequence = (
                "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            )
            response = self.session.post(
                f"{self.base_url}/api/v1/blastp/search",
                json={"sequence": sequence, "db_name": "pdbaa", "output_format": "table"},
            )
            if response.status_code == 200:
                data = response.json()
                expected_fields = [
                    "status",
                    "message",
                    "result",
                    "processing_time",
                    "timestamp",
                ]
                if all(field in data for field in expected_fields):
                    result = data["result"]
                    if hasattr(result, "report") or "report" in result:
                        self.log_test(
                            "Search (Valid - Table)",
                            True,
                            (
                                f"Status: {data['status']}, "
                                f"Processing Time: {data['processing_time']}s"
                            ),
                        )
                        return True
                    else:
                        self.log_test(
                            "Search (Valid - Table)", False, "Result missing report field"
                        )
                        return False
                else:
                    self.log_test(
                        "Search (Valid - Table)",
                        False,
                        f"Missing fields: {expected_fields}",
                    )
                    return False
            else:
                self.log_test(
                    "Search (Valid - Table)",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Search (Valid - Table)", False, f"Exception: {str(e)}")
            return False

    def test_search_endpoint_json_format(self) -> bool:
        """Test search endpoint with JSON output format"""
        try:
            sequence = (
                "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            )
            response = self.session.post(
                f"{self.base_url}/api/v1/blastp/search",
                json={"sequence": sequence, "db_name": "pdbaa", "output_format": "json"},
            )
            if response.status_code == 200:
                data = response.json()
                expected_fields = [
                    "status",
                    "message",
                    "result",
                    "processing_time",
                    "timestamp",
                ]
                if all(field in data for field in expected_fields):
                    result = data["result"]
                    # Check for JSON format specific fields
                    if "hits" in result and "total_hits" in result and "query_sequence" in result:
                        hits = result["hits"]
                        if isinstance(hits, list) and len(hits) > 0:
                            # Check structure of first hit
                            first_hit = hits[0]
                            hit_fields = ["rank", "query_id", "subject_id", "percent_identity", 
                                        "alignment_length", "evalue", "bitscore"]
                            if all(field in first_hit for field in hit_fields):
                                self.log_test(
                                    "Search (Valid - JSON)",
                                    True,
                                    (
                                        f"Status: {data['status']}, "
                                        f"Total Hits: {result['total_hits']}, "
                                        f"Processing Time: {data['processing_time']}s"
                                    ),
                                )
                                return True
                            else:
                                self.log_test(
                                    "Search (Valid - JSON)", 
                                    False, 
                                    f"Hit missing fields: {hit_fields}"
                                )
                                return False
                        else:
                            self.log_test(
                                "Search (Valid - JSON)", False, "No hits in results"
                            )
                            return False
                    else:
                        self.log_test(
                            "Search (Valid - JSON)", 
                            False, 
                            "Result missing JSON format fields (hits, total_hits, query_sequence)"
                        )
                        return False
                else:
                    self.log_test(
                        "Search (Valid - JSON)",
                        False,
                        f"Missing fields: {expected_fields}",
                    )
                    return False
            else:
                self.log_test(
                    "Search (Valid - JSON)",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Search (Valid - JSON)", False, f"Exception: {str(e)}")
            return False

    def test_search_endpoint_invalid(self) -> bool:
        """Test search endpoint with invalid sequence"""
        try:
            # Test with empty sequence
            response = self.session.post(
                f"{self.base_url}/api/v1/blastp/search", json={"sequence": ""}
            )
            if response.status_code == 400:  # API returns 400 for empty sequence
                self.log_test(
                    "Search (Invalid - Empty)",
                    True,
                    "Correctly rejected empty sequence",
                )
                return True
            else:
                self.log_test(
                    "Search (Invalid - Empty)",
                    False,
                    f"Expected 400, got {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Search (Invalid - Empty)", False, f"Exception: {str(e)}")
            return False

    def test_search_endpoint_missing(self) -> bool:
        """Test search endpoint with missing sequence parameter"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/blastp/search")
            if response.status_code == 422:  # FastAPI validation error
                self.log_test(
                    "Search (Invalid - Missing)",
                    True,
                    "Correctly rejected missing sequence",
                )
                return True
            else:
                self.log_test(
                    "Search (Invalid - Missing)",
                    False,
                    f"Expected 422, got {response.status_code}",
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("Search (Invalid - Missing)", False, f"Exception: {str(e)}")
            return False

    def test_documentation_endpoints(self) -> bool:
        """Test documentation endpoints"""
        try:
            # Test OpenAPI JSON
            response = self.session.get(f"{self.base_url}/openapi.json")
            if response.status_code == 200:
                self.log_test("OpenAPI JSON", True, "Documentation available")
                return True
            else:
                self.log_test("OpenAPI JSON", False, f"HTTP {response.status_code}")
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("OpenAPI JSON", False, f"Exception: {str(e)}")
            return False

    def test_nonexistent_endpoint(self) -> bool:
        """Test that nonexistent endpoints return 404"""
        try:
            response = self.session.get(f"{self.base_url}/nonexistent")
            if response.status_code == 404:
                self.log_test(
                    "404 Handling",
                    True,
                    "Correctly returns 404 for nonexistent endpoint",
                )
                return True
            else:
                self.log_test(
                    "404 Handling", False, f"Expected 404, got {response.status_code}"
                )
                return False
        except (requests.RequestException, ValueError) as e:
            self.log_test("404 Handling", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("🧪 Testing BLAST REST API Endpoints")
        print("=" * 50)

        tests = [
            self.test_health_endpoint,
            self.test_root_endpoint,
            self.test_tool_info_endpoint,
            self.test_search_endpoint_valid,
            self.test_search_endpoint_json_format,
            self.test_search_endpoint_invalid,
            self.test_search_endpoint_missing,
            self.test_documentation_endpoints,
            self.test_nonexistent_endpoint,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if test():
                passed += 1

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! REST API is working correctly.")
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
    parser = argparse.ArgumentParser(description="Test BLAST REST API endpoints")
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
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
    print(f"🧪 Testing BLAST REST API at {base_url}")

    tester = BlastRESTAPITester(base_url=base_url)
    results = tester.run_all_tests()

    # Exit with appropriate code
    if results["passed"] == results["total"]:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
