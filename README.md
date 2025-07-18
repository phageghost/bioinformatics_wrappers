# Bioinformatics Wrappers

Dockerized bioinformatics tools with API wrappers for both REST and MCP-like protocols, designed for agentic workflows and AI integration.

## 🚀 Overview

This repository contains Dockerized bioinformatics tools wrapped with both RESTful APIs and MCP-like endpoints for seamless integration into agentic workflows and AI applications. Each tool is containerized and exposed via standardized interfaces.

## 🏗️ Project Structure

```
bioinformatics_wrappers/
├── tools/                    # Individual tool implementations
│   ├── spider/              # SPIDER tool wrapper
│   │   ├── Dockerfile       # Docker configuration
│   │   ├── api/             # Core API implementation
│   │   ├── app.py           # FastAPI application (REST + MCP-like)
│   │   ├── run_combined_v2.py # Server entrypoint
│   │   ├── test_rest_api.py # REST API test suite
│   │   ├── test_mcp_endpoints.py # MCP endpoint test suite
│   │   ├── examples/        # Usage examples
│   │   ├── requirements.txt # Python dependencies
│   │   └── README.md        # Tool-specific documentation
│   └── [other_tools]/       # Future tool wrappers
├── docker-compose.yml       # Orchestration for all tools
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

## 🛠️ Available Tools

### SPIDER (Stacking-based Protein druggability prediction)
* **Description**: Stacking-based ensemble learning framework for accurate prediction of druggable proteins
* **Source**: https://github.com/plenoi/SPIDER
* **Port**: 8000
* **Protocols**: REST API + MCP-like endpoints
* **Input**: Protein sequences (FASTA format)
* **Output**: Druggability predictions with confidence scores

## ⚡ Quick Start

### Using Docker Compose (Recommended)
```bash
# Start all tools
docker-compose up -d

# Start specific tool
docker-compose up -d spider

# View logs
docker-compose logs -f spider

# Stop all tools
docker-compose down
```

### Individual Tool Usage
```bash
# Build and run SPIDER
cd tools/spider
docker build -t spider-api .
docker run -p 8000:8000 spider-api
```

## 🔌 API Usage

### REST API Endpoints

#### Health Check
```bash
curl http://localhost:8000/api/v1/spider/health
```

#### Get Tool Information
```bash
curl http://localhost:8000/api/v1/spider/info
```

#### Predict Druggability
```bash
curl -X POST "http://localhost:8000/api/v1/spider/predict?sequence=MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
```

### MCP-like Endpoints (AI Agent Friendly)

#### List Available Tools
```bash
curl http://localhost:8000/mcp/tools
```

#### Call Tool (Get Tool Info)
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_tool_info", "arguments": {}}'
```

#### Call Tool (Predict Druggability)
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "predict_druggability", 
    "arguments": {
      "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    }
  }'
```

## 🧪 Testing

### Run REST API Tests
```bash
cd tools/spider
python test_rest_api.py
```

### Run MCP Endpoint Tests
```bash
cd tools/spider
python test_mcp_endpoints.py
```

### Run Both Test Suites
```bash
cd tools/spider
python test_rest_api.py && python test_mcp_endpoints.py
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Development

### Adding a New Tool
1. Create a new directory in `tools/`
2. Implement the API wrapper following the SPIDER pattern
3. Add Dockerfile and requirements
4. Create test suites for both REST and MCP endpoints
5. Update docker-compose.yml
6. Add documentation

### API Standards
All tools follow these conventions:

#### REST API
- Health check: `GET /api/v1/{tool}/health`
- Tool info: `GET /api/v1/{tool}/info`
- Prediction: `POST /api/v1/{tool}/predict`
- Standardized error responses
- Input validation

#### MCP-like Endpoints
- List tools: `GET /mcp/tools`
- Call tool: `POST /mcp/call`
- JSON Schema validation
- Consistent response format

## 🐳 Docker Details

### Container Architecture
- **Base Image**: Python 3.12-slim
- **Package Manager**: micromamba (conda alternative)
- **API Environment**: Python 3.12 with FastAPI
- **Tool Environment**: Python 3.9 (for SPIDER compatibility)
- **Single Port**: 8000 (both REST and MCP-like endpoints)

### Health Checks
- Automatic health monitoring
- Graceful shutdown handling
- Process monitoring and restart

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
