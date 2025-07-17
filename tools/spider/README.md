# SPIDER API Wrapper

RESTful API wrapper for SPIDER: Stacking-based ensemble learning framework for accurate prediction of druggable proteins.

## Overview

SPIDER is a machine learning tool that predicts whether proteins are druggable based on their amino acid sequences. This wrapper provides both a RESTful API interface and MCP (Model Context Protocol) support to make SPIDER easily accessible for agentic workflows.

## Features

- **RESTful API**: Standardized HTTP endpoints for easy integration
- **MCP Support**: Model Context Protocol for AI agent integration
- **File Upload**: Accept FASTA format protein sequence files
- **Validation**: Automatic FASTA format validation
- **Structured Output**: JSON responses with prediction results
- **Error Handling**: Comprehensive error handling and logging
- **Health Checks**: Built-in health monitoring
- **Docker Support**: Containerized for easy deployment

## API Endpoints

### Health Check
```http
GET /api/v1/spider/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "tool": "SPIDER",
  "version": "1.0.0"
}
```

### Tool Information
```http
GET /api/v1/spider/info
```

**Response:**
```json
{
  "name": "SPIDER",
  "version": "1.0",
  "description": "Stacking-based ensemble learning framework for accurate prediction of druggable proteins",
  "input_format": "FASTA",
  "output_format": "CSV",
  "home_directory": "/app/spider_tool"
}
```

### Protein Prediction
```http
POST /api/v1/spider/predict
Content-Type: multipart/form-data
```

**Request:** Upload a FASTA file with protein sequences

**Response:**
```json
{
  "status": "success",
  "message": "Prediction completed successfully",
  "results": [
    {
      "sequence_header": ">protein1",
      "label": "Druggable",
      "probability": 0.85
    },
    {
      "sequence_header": ">protein2", 
      "label": "Non-druggable",
      "probability": 0.23
    }
  ],
  "total_sequences": 2,
  "processing_time": 12.5,
  "timestamp": "2024-01-15T10:30:00"
}
```

## Input Format

The API accepts FASTA format files containing protein sequences:

```
>protein1
MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG
>protein2
MKLLIVGFLFLAAAGVILGAVLALPGNLEGLLDKYGTSKKCLLDYKDDDDKCLLDYKDDDDK
```

## Output Format

The API returns structured JSON with:
- **sequence_header**: The FASTA header for each protein
- **label**: Prediction label ("Druggable" or "Non-druggable")
- **probability**: Confidence score (0.0 to 1.0)

## Usage Examples

### Using curl
```bash
# Health check
curl http://localhost:8000/api/v1/spider/health

# Submit prediction
curl -X POST "http://localhost:8000/api/v1/spider/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@proteins.fasta"
```

### Using Python
```python
import requests

# Submit FASTA file for prediction
with open('proteins.fasta', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/v1/spider/predict',
        files=files
    )

if response.status_code == 200:
    results = response.json()
    for result in results['results']:
        print(f"{result['sequence_header']}: {result['label']} ({result['probability']:.2f})")
```

### Using JavaScript/Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('proteins.fasta'));

axios.post('http://localhost:8000/api/v1/spider/predict', form, {
  headers: form.getHeaders()
})
.then(response => {
  console.log(response.data);
})
.catch(error => {
  console.error('Error:', error.response.data);
});
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- **400 Bad Request**: Invalid file format or missing file
- **500 Internal Server Error**: SPIDER execution failed

Error response format:
```json
{
  "status": "error",
  "error": "Invalid FASTA file format",
  "message": "Invalid FASTA file format",
  "timestamp": "2024-01-15T10:30:00"
}
```

## MCP (Model Context Protocol) Support

The SPIDER service also supports the Model Context Protocol (MCP), enabling integration with AI agents and assistants. The service uses a dual-environment setup:

- **Base Environment (Python 3.12)**: Runs the REST API and MCP server
- **Virtual Environment (Python 3.9)**: Runs SPIDER with its specific dependencies

### MCP Tools Available

1. **predict_druggability**: Predict druggability of a protein sequence
   - Input: `{"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"}`
   - Output: Prediction results with status, prediction, and probability

2. **get_tool_info**: Get information about the SPIDER tool
   - Input: `{}`
   - Output: Tool information including name, version, and description

### Running MCP Server

#### Standalone MCP Server
```bash
# Run only MCP server
python combined_server.py --mcp-only
```

#### Combined Server (REST + MCP)
```bash
# Run both REST API and MCP server
python combined_server.py

# Run with custom port
python combined_server.py --port 8001
```

#### REST API Only
```bash
# Run only REST API server
python combined_server.py --rest-only
```

### MCP Client Example

```python
import asyncio
from mcp.client import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "api.mcp_server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, client_info={
            'name': 'spider-client',
            'version': '1.0.0'
        }) as session:
            # Initialize session (no arguments in MCP 1.11.0)
            await session.initialize()  # No arguments
            
            # Predict druggability
            result = await session.call_tool("predict_druggability", {
                "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
            })
            
            if result.content:
                print(result.content[0].text)

asyncio.run(main())
```

### MCP Configuration

For MCP clients, use the configuration in `mcp_config.json`:

```json
{
  "mcpServers": {
    "spider-bioinformatics": {
      "command": "python",
      "args": ["-m", "api.mcp_server"],
      "env": {
        "PYTHONPATH": "/app",
        "SPIDER_HOME": "/app/spider_tool"
      }
    }
  }
}
```

### Docker with MCP

To run the container with MCP support:

```bash
# Build and run with combined server
docker build -t spider-api .
docker run -p 8000:8000 spider-api python combined_server.py

# Or run MCP only
docker run spider-api python combined_server.py --mcp-only

# Or run REST API only
docker run -p 8000:8000 spider-api python combined_server.py --rest-only
```

The Docker container uses a dual-environment setup:
- Python 3.12 base environment for the API and MCP server
- Python 3.9 virtual environment for SPIDER dependencies

## Docker Usage

### Build and Run
```bash
# Build the image
docker build -t spider-api .

# Run the container
docker run -p 8000:8000 spider-api
```

### Using Docker Compose
```bash
# Start the service
docker-compose up -d spider

# View logs
docker-compose logs spider
```

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python app.py
```

### Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/spider/health

# Test with sample FASTA file
curl -X POST "http://localhost:8000/api/v1/spider/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_proteins.fasta"
```

## Configuration

Environment variables:
- `SPIDER_HOME`: Path to SPIDER tool installation (default: `/app/spider_tool`)
- `PYTHONPATH`: Python path for imports (default: `/app`)

## Limitations

- Maximum file size: 10MB
- Supported formats: FASTA (.fasta, .fa, .fas)
- Processing timeout: 5 minutes
- Concurrent requests: Limited by available system resources

## Troubleshooting

### Common Issues

1. **File format error**: Ensure your file is in valid FASTA format
2. **Timeout error**: Large files may take longer to process
3. **Memory error**: Very large files may exceed container memory limits

### Logs
Check container logs for detailed error information:
```bash
docker logs <container_id>
```

## License

This wrapper is licensed under the MIT License. The underlying SPIDER tool has its own license.