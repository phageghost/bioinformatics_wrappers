#!/usr/bin/env python3
"""
Test script for bioinformatics tool APIs
Usage: python scripts/test_api.py [tool_name] [endpoint]
"""

import sys
import requests
import json
import time
from pathlib import Path
from typing import Optional

# API base URLs
API_BASE_URLS = {
    'spider': 'http://localhost:8000',
    # Add more tools here as they're implemented
}

def test_health_endpoint(base_url: str, tool_name: str) -> bool:
    """Test the health endpoint for a tool"""
    try:
        url = f"{base_url}/api/v1/{tool_name}/health"
        print(f"Testing health endpoint: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_info_endpoint(base_url: str, tool_name: str) -> bool:
    """Test the info endpoint for a tool"""
    try:
        url = f"{base_url}/api/v1/{tool_name}/info"
        print(f"Testing info endpoint: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Info endpoint passed: {data}")
            return True
        else:
            print(f"❌ Info endpoint failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Info endpoint error: {e}")
        return False

def test_prediction_endpoint(base_url: str, tool_name: str, test_file_path: Optional[str] = None) -> bool:
    """Test the prediction endpoint for a tool"""
    try:
        url = f"{base_url}/api/v1/{tool_name}/predict"
        print(f"Testing prediction endpoint: {url}")
        
        # Create a test FASTA file if none provided
        if not test_file_path:
            test_file_path = create_test_fasta_file(tool_name)
        
        if not Path(test_file_path).exists():
            print(f"❌ Test file not found: {test_file_path}")
            return False
        
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction endpoint passed:")
            print(f"   Status: {data.get('status')}")
            print(f"   Total sequences: {data.get('total_sequences')}")
            print(f"   Processing time: {data.get('processing_time')}s")
            return True
        else:
            print(f"❌ Prediction endpoint failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Prediction endpoint error: {e}")
        return False

def create_test_fasta_file(tool_name: str) -> str:
    """Create a test FASTA file for the specified tool"""
    test_file_path = f"test_{tool_name}_sequences.fasta"
    
    # Different test sequences for different tools
    if tool_name == 'spider':
        content = """>test_protein_1
MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG
>test_protein_2
MKLLIVGFLFLAAAGVILGAVLALPGNLEGLLDKYGTSKKCLLDYKDDDDKCLLDYKDDDDK
>test_protein_3
MKLIVGFLFLAAAGVILGAVLALPGNLEGLLDKYGTSKKCLLDYKDDDDKCLLDYKDDDDK"""
    else:
        # Generic test sequence
        content = """>test_sequence_1
MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"""
    
    with open(test_file_path, 'w') as f:
        f.write(content)
    
    print(f"Created test file: {test_file_path}")
    return test_file_path

def test_all_endpoints(tool_name: str, base_url: str) -> bool:
    """Test all endpoints for a specific tool"""
    print(f"\n🧪 Testing {tool_name.upper()} API endpoints...")
    print("=" * 50)
    
    success = True
    
    # Test health endpoint
    if not test_health_endpoint(base_url, tool_name):
        success = False
    
    print()
    
    # Test info endpoint
    if not test_info_endpoint(base_url, tool_name):
        success = False
    
    print()
    
    # Test prediction endpoint
    if not test_prediction_endpoint(base_url, tool_name):
        success = False
    
    print()
    
    if success:
        print(f"✅ All {tool_name} endpoints passed!")
    else:
        print(f"❌ Some {tool_name} endpoints failed!")
    
    return success

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_api.py [tool_name] [test_file_path]")
        print("Available tools:", list(API_BASE_URLS.keys()))
        sys.exit(1)
    
    tool_name = sys.argv[1].lower()
    test_file_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if tool_name not in API_BASE_URLS:
        print(f"❌ Unknown tool: {tool_name}")
        print(f"Available tools: {list(API_BASE_URLS.keys())}")
        sys.exit(1)
    
    base_url = API_BASE_URLS[tool_name]
    
    # Test all endpoints
    success = test_all_endpoints(tool_name, base_url)
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 