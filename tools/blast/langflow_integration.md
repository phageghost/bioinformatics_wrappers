# LangFlow Integration Guide for FastMCP BLASTp Server

## Overview

This guide explains how to integrate the FastMCP BLASTp server with LangFlow for bioinformatics workflows.

## Server Configuration

The FastMCP server runs in **HTTP API mode** (not MCP protocol) for LangFlow compatibility:

```bash
# Start the server
python mcp_server.py --host 127.0.0.1 --port 8001
```

## API Endpoints

### 1. List Available Tools
```http
GET http://127.0.0.1:8001/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "blastp_search_flexible_db_tabular",
      "description": "Search a protein sequence against a specified NCBI BLAST database.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "sequence": {
            "type": "string",
            "description": "Protein sequence to search (required)"
          },
          "database": {
            "type": "string",
            "description": "BLAST database name (default: swissprot, options: nr, pdbaa, mito, swissprot)",
            "default": "swissprot"
          },
          "evalue": {
            "type": "number",
            "description": "E-value threshold for significance (default: 0.001)",
            "default": 0.001
          },
          "max_target_seqs": {
            "type": "integer",
            "description": "Maximum number of target sequences to return (default: 20)",
            "default": 20
          }
        },
        "required": ["sequence"]
      }
    }
  ]
}
```

### 2. Call Tool
```http
POST http://127.0.0.1:8001/tools/blastp_search_flexible_db_tabular
Content-Type: application/json
```

**Request Body:**
```json
{
  "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
  "database": "swissprot",
  "evalue": 0.001,
  "max_target_seqs": 10
}
```

**Response:**
```json
{
  "result": "BLAST search results in tabular format...",
  "status": "success"
}
```

## LangFlow Integration

### Method 1: HTTP Request Node

1. **Add HTTP Request Node** to your LangFlow workflow
2. **Configure the request:**
   - **URL**: `http://127.0.0.1:8001/tools/blastp_search_flexible_db_tabular`
   - **Method**: `POST`
   - **Headers**: `Content-Type: application/json`
   - **Body**: JSON with sequence and parameters

### Method 2: Custom Tool Node

1. **Create Custom Tool** in LangFlow
2. **Configure the tool:**
   - **Name**: `BLASTp Search`
   - **Description**: `Search protein sequences using BLASTp`
   - **Input Schema**: Use the schema from `/tools` endpoint
   - **HTTP Endpoint**: `http://127.0.0.1:8001/tools/blastp_search_flexible_db_tabular`

### Method 3: API Integration

```python
# Example Python code for LangFlow custom node
import requests
import json

def blastp_search(sequence: str, database: str = "swissprot", 
                  evalue: float = 0.001, max_target_seqs: int = 10):
    """BLASTp search function for LangFlow"""
    
    url = "http://127.0.0.1:8001/tools/blastp_search_flexible_db_tabular"
    payload = {
        "sequence": sequence,
        "database": database,
        "evalue": evalue,
        "max_target_seqs": max_target_seqs
    }
    
    response = requests.post(url, json=payload, timeout=60)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"BLASTp search failed: {response.text}")
```

## Example Workflow

1. **Input Node**: Protein sequence
2. **BLASTp Node**: Search sequence against database
3. **Processing Node**: Parse and analyze results
4. **Output Node**: Display results

## Testing

Use the provided test scripts:

```bash
# Test the server
python simple_test.py

# Test with custom parameters
python test_mcp_client.py --sequence "YOUR_SEQUENCE" --database "nr"
```

## Troubleshooting

### Common Issues

1. **Server not running**: Ensure `python mcp_server.py` is running on port 8001
2. **Connection refused**: Check if port 8001 is available
3. **Timeout errors**: BLAST searches can take time, increase timeout in LangFlow
4. **Invalid sequence**: Ensure protein sequence is valid (only amino acid letters)

### Debug Commands

```bash
# Check if server is running
curl http://127.0.0.1:8001/tools

# Test tool call
curl -X POST http://127.0.0.1:8001/tools/blastp_search_flexible_db_tabular \
  -H "Content-Type: application/json" \
  -d '{"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"}'
```

## Security Considerations

- **Local deployment**: Server runs on localhost by default
- **Production**: Use proper authentication and HTTPS for production deployments
- **Rate limiting**: Consider implementing rate limiting for production use
- **Input validation**: Server validates protein sequences automatically

## Performance Tips

- **Database selection**: Use smaller databases (swissprot) for faster searches
- **E-value threshold**: Higher thresholds (0.01) return more results faster
- **Max sequences**: Limit `max_target_seqs` for faster responses
- **Caching**: Consider caching results for repeated searches 