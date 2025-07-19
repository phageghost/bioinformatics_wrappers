#!/usr/bin/env python3
"""Comprehensive test script for SPIDER REST API endpoints"""

import requests
import json
import time
import argparse
from typing import Dict, Any

class SpiderRESTAPITester:
    """Test suite for SPIDER REST API"""
    
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
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/spider/health")
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "timestamp", "tool", "version"]
                if all(field in data for field in expected_fields):
                    self.log_test("Health Check", True, f"Status: {data['status']}, Tool: {data['tool']}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Missing fields: {expected_fields}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
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
                    self.log_test("Root Endpoint", False, f"Missing fields: {expected_fields}")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_tool_info_endpoint(self) -> bool:
        """Test the tool info endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/spider/info")
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["name", "version", "description"]
                if all(field in data for field in expected_fields):
                    self.log_test("Tool Info", True, f"Tool: {data['name']} v{data['version']}")
                    return True
                else:
                    self.log_test("Tool Info", False, f"Missing fields: {expected_fields}")
                    return False
            else:
                self.log_test("Tool Info", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Tool Info", False, f"Exception: {str(e)}")
            return False
    
    def test_prediction_endpoint_valid(self) -> bool:
        """Test prediction endpoint with valid sequence"""
        try:
            sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            response = self.session.post(
                f"{self.base_url}/api/v1/spider/predict",
                params={"sequence": sequence}
            )
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "message", "result", "processing_time", "timestamp"]
                if all(field in data for field in expected_fields):
                    result = data["result"]
                    if hasattr(result, "label") or "label" in result:
                        self.log_test("Prediction (Valid)", True, 
                                    f"Status: {data['status']}, Processing Time: {data['processing_time']}s")
                        return True
                    else:
                        self.log_test("Prediction (Valid)", False, "Result missing label field")
                        return False
                else:
                    self.log_test("Prediction (Valid)", False, f"Missing fields: {expected_fields}")
                    return False
            else:
                self.log_test("Prediction (Valid)", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Prediction (Valid)", False, f"Exception: {str(e)}")
            return False
    
    def test_prediction_endpoint_invalid(self) -> bool:
        """Test prediction endpoint with invalid sequence"""
        try:
            # Test with empty sequence
            response = self.session.post(
                f"{self.base_url}/api/v1/spider/predict",
                params={"sequence": ""}
            )
            if response.status_code == 400:
                self.log_test("Prediction (Invalid - Empty)", True, "Correctly rejected empty sequence")
                return True
            else:
                self.log_test("Prediction (Invalid - Empty)", False, 
                            f"Expected 400, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Prediction (Invalid - Empty)", False, f"Exception: {str(e)}")
            return False
    
    def test_prediction_endpoint_missing(self) -> bool:
        """Test prediction endpoint with missing sequence parameter"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/spider/predict")
            if response.status_code == 422:  # FastAPI validation error
                self.log_test("Prediction (Invalid - Missing)", True, "Correctly rejected missing sequence")
                return True
            else:
                self.log_test("Prediction (Invalid - Missing)", False, 
                            f"Expected 422, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Prediction (Invalid - Missing)", False, f"Exception: {str(e)}")
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
        except Exception as e:
            self.log_test("OpenAPI JSON", False, f"Exception: {str(e)}")
            return False
    
    def test_nonexistent_endpoint(self) -> bool:
        """Test that nonexistent endpoints return 404"""
        try:
            response = self.session.get(f"{self.base_url}/nonexistent")
            if response.status_code == 404:
                self.log_test("404 Handling", True, "Correctly returns 404 for nonexistent endpoint")
                return True
            else:
                self.log_test("404 Handling", False, f"Expected 404, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("404 Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("🧪 Testing SPIDER REST API Endpoints")
        print("=" * 50)
        
        tests = [
            self.test_health_endpoint,
            self.test_root_endpoint,
            self.test_tool_info_endpoint,
            self.test_prediction_endpoint_valid,
            self.test_prediction_endpoint_invalid,
            self.test_prediction_endpoint_missing,
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
            "results": self.test_results
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test SPIDER REST API endpoints')
    parser.add_argument('--port', type=int, default=8000, 
                       help='Port number for the API server (default: 8000)')
    parser.add_argument('--host', type=str, default='localhost',
                       help='Host for the API server (default: localhost)')
    
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    print(f"🧪 Testing SPIDER REST API at {base_url}")
    
    tester = SpiderRESTAPITester(base_url=base_url)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["passed"] == results["total"]:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main() 