#!/usr/bin/env python3
"""
Example: Using BLAST API with JSON Output

This example demonstrates how to use the BLAST API with the new JSON output format.
It shows both the REST API and MCP-like endpoints with JSON responses.
"""

import requests
import json


def example_rest_api_json():
    """Example of using the REST API with JSON output"""

    # API endpoint
    url = "http://localhost:8000/api/v1/blastp/search"

    # Request payload with JSON output format
    payload = {
        "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
        "db_name": "pdbaa",
        "evalue": 0.001,
        "max_target_seqs": 5,
        "output_format": "json",  # Request JSON output
    }

    print("REST API Example - JSON Output:")
    print("=" * 50)
    print(f"Request URL: {url}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response structure:")
            print(f"Status: {result['status']}")
            print(f"Processing time: {result['processing_time']}s")
            print(f"Total hits: {result['result']['total_hits']}")
            print(f"Query sequence: {result['result']['query_sequence'][:30]}...")

            print("\nTop hits:")
            for i, hit in enumerate(result["result"]["hits"][:3]):
                print(f"  {i+1}. {hit['subject_id']}")
                print(f"     Identity: {hit['percent_identity']}%")
                print(f"     E-value: {hit['evalue']}")
                print(f"     Organism: {hit['organism']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_mcp_json():
    """Example of using the MCP-like endpoint with JSON output"""

    # MCP endpoint
    url = "http://localhost:8000/mcp/call"

    # Request payload
    payload = {
        "name": "perform_blastp_search",
        "arguments": {
            "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
            "db_name": "pdbaa",
            "evalue": 0.001,
            "max_target_seqs": 5,
            "output_format": "json",  # Request JSON output
        },
    }

    print("\nMCP-like API Example - JSON Output:")
    print("=" * 50)
    print(f"Request URL: {url}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response:")
            print(result["content"][0]["text"])
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")


def compare_formats():
    """Compare table vs JSON output formats"""

    url = "http://localhost:8000/api/v1/blastp/search"
    sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"

    print("\nFormat Comparison:")
    print("=" * 50)

    # Test table format
    table_payload = {
        "sequence": sequence,
        "db_name": "pdbaa",
        "evalue": 0.001,
        "max_target_seqs": 3,
        "output_format": "table",
    }

    # Test JSON format
    json_payload = {
        "sequence": sequence,
        "db_name": "pdbaa",
        "evalue": 0.001,
        "max_target_seqs": 3,
        "output_format": "json",
    }

    try:
        # Table format
        table_response = requests.post(url, json=table_payload)
        if table_response.status_code == 200:
            table_result = table_response.json()
            print("📊 Table Format:")
            print(f"  Response type: {type(table_result['result'])}")
            print(f"  Has 'report' field: {'report' in table_result['result']}")
            print(f"  Report preview: {table_result['result']['report'][:100]}...")

        # JSON format
        json_response = requests.post(url, json=json_payload)
        if json_response.status_code == 200:
            json_result = json_response.json()
            print("\n🔢 JSON Format:")
            print(f"  Response type: {type(json_result['result'])}")
            print(f"  Has 'hits' field: {'hits' in json_result['result']}")
            print(f"  Total hits: {json_result['result']['total_hits']}")
            print(f"  First hit: {json_result['result']['hits'][0]['subject_id']}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("BLAST API JSON Output Examples")
    print("=" * 60)
    print("This example demonstrates the new JSON output format feature.")
    print("Make sure the BLAST server is running on localhost:8000\n")

    example_rest_api_json()
    example_mcp_json()
    compare_formats()

    print("\n" + "=" * 60)
    print("Summary:")
    print("- Use 'output_format': 'json' to get structured JSON responses")
    print("- Use 'output_format': 'table' (default) for formatted text output")
    print("- JSON format provides structured data for programmatic access")
    print("- Table format provides human-readable formatted output")
