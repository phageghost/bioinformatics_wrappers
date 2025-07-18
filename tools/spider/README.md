# SPIDER API Wrapper

RESTful API and MCP-like endpoint wrapper for SPIDER: Stacking-based ensemble learning framework for accurate prediction of druggable proteins.

## 🚀 Overview

SPIDER is a machine learning tool that predicts whether proteins are druggable based on their amino acid sequences. This wrapper provides both a RESTful API interface and MCP-like endpoints to make SPIDER easily accessible for agentic workflows and AI applications.

## ✨ Features

- **RESTful API**: Standardized HTTP endpoints for easy integration
- **MCP-like Endpoints**: AI agent-friendly interface following MCP patterns
- **Sequence Input**: Accept protein sequences directly via API
- **Validation**: Automatic sequence format validation
- **Structured Output**: JSON responses with prediction results
- **Error Handling**: Comprehensive error handling and logging
- **Health Checks**: Built-in health monitoring
- **Docker Support**: Containerized for easy deployment
- **Single Port**: Both REST and MCP-like endpoints on port 8000

## 🔌 API Endpoints

### REST API Endpoints

#### Health Check
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

#### Tool Information
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

#### Protein Prediction
```http
POST /api/v1/spider/predict?sequence=<protein_sequence>
```

**Request:** Query parameter with protein sequence

**Response:**
```json
{
  "status": "success",
  "message": "Prediction completed successfully",
  "result": {
    "label": "Druggable",
    "probability": 0.85
  },
  "processing_time": 1.34,
  "timestamp": "2024-01-15T10:30:00"
}
```

### MCP-like Endpoints (AI Agent Friendly)

#### List Available Tools
```http
GET /mcp/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "predict_druggability",
      "title": "Predict Druggability",
      "description": "Predict druggability of a protein sequence using SPIDER",
      "inputSchema": {
        "type": "object",
        "properties": {
          "sequence": {
            "type": "string",
            "description": "Protein sequence to analyze"
          }
        },
        "required": ["sequence"]
      }
    },
    {
      "name": "get_tool_info",
      "title": "Get Tool Info",
      "description": "Get information about the SPIDER tool",
      "inputSchema": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  ]
}
```

#### Call Tool
```http
POST /mcp/call
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "predict_druggability",
  "arguments": {
    "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "\nSPIDER Prediction Results:\n- Status: Success\n- Prediction: Negative\n- Probability: 0.01781960028124742\n- Message: Prediction completed successfully\n- Processing Time: 1.34s\n"
    }
  ]
}
```

## 📝 Input Format

The API accepts protein sequences in various formats:

### REST API
- **Query Parameter**: Direct sequence string
- **Example**: `?sequence=MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG`

### MCP-like Endpoints
- **JSON Payload**: Structured JSON with tool name and arguments
- **Example**: `{"name": "predict_druggability", "arguments": {"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"}}`

## 📊 Output Format

### REST API Response
- **status**: Success/error status
- **message**: Human-readable message
- **result**: Prediction object with label and probability
- **processing_time**: Time taken for prediction (seconds)
- **timestamp**: ISO timestamp

### MCP-like Response
- **content**: Array of content objects
- **type**: Content type (always "text")
- **text**: Formatted text response

## 🧪 Usage Examples

### REST API Examples

#### Using curl
```bash
# Health check
curl http://localhost:8000/api/v1/spider/health

# Get tool info
curl http://localhost:8000/api/v1/spider/info

# Predict druggability
curl -X POST "http://localhost:8000/api/v1/spider/predict?sequence=MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
```

#### Using Python
```python
import requests

# Health check
response = requests.get('http://localhost:8000/api/v1/spider/health')
print(response.json())

# Predict druggability
sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
response = requests.post(
    'http://localhost:8000/api/v1/spider/predict',
    params={'sequence': sequence}
)

if response.status_code == 200:
    result = response.json()
    print(f"Prediction: {result['result']['label']}")
    print(f"Probability: {result['result']['probability']:.3f}")
```

### MCP-like Endpoints Examples

#### Using curl
```bash
# List available tools
curl http://localhost:8000/mcp/tools

# Get tool info
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_tool_info", "arguments": {}}'

# Predict druggability
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "predict_druggability", 
    "arguments": {
      "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    }
  }'
```

#### Using Python
```python
import requests

# List tools
response = requests.get('http://localhost:8000/mcp/tools')
tools = response.json()
print(f"Available tools: {[tool['name'] for tool in tools['tools']]}")

# Call tool
payload = {
    "name": "predict_druggability",
    "arguments": {
        "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    }
}

response = requests.post(
    'http://localhost:8000/mcp/call',
    headers={'Content-Type': 'application/json'},
    json=payload
)

if response.status_code == 200:
    result = response.json()
    print(result['content'][0]['text'])
```

## 🚨 Error Handling

The API returns appropriate HTTP status codes and error messages:

- **400 Bad Request**: Invalid sequence or missing parameters
- **422 Unprocessable Entity**: Malformed JSON or validation errors
- **500 Internal Server Error**: SPIDER execution failed

### Error Response Format
```json
{
  "status": "error",
  "error": "Invalid sequence format",
  "message": "Invalid sequence format",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Start the service
docker-compose up -d spider

# View logs
docker-compose logs -f spider

# Stop the service
docker-compose down
```

### Manual Docker Build
```bash
# Build the image
docker build -t spider-api .

# Run the container
docker run -p 8000:8000 spider-api
```

## 🧪 Testing

### Run REST API Tests
```bash
python test_rest_api.py
```

### Run MCP Endpoint Tests
```bash
python test_mcp_endpoints.py
```

### Run All Tests
```bash
python test_rest_api.py && python test_mcp_endpoints.py
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Development

### Architecture
- **FastAPI**: Modern Python web framework
- **Dual Environment**: Python 3.12 for API, Python 3.9 for SPIDER
- **micromamba**: Lightweight conda environment manager
- **Single Container**: Both REST and MCP-like endpoints in one container

### Key Files
- `app.py`: Main FastAPI application with both REST and MCP-like endpoints
- `run_combined_server.py`: Server entrypoint with process management
- `api/spider_service.py`: Core SPIDER integration logic
- `test_rest_api.py`: Comprehensive REST API test suite
- `test_mcp_endpoints.py`: Comprehensive MCP endpoint test suite

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.