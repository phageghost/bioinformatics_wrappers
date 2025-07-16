# bioinformatics_wrappers
Dockerized bioinformatics tools with API wrappers intended for use in agentic workflows

## Overview
This repository contains Dockerized bioinformatics tools wrapped with RESTful APIs for easy integration into agentic workflows. Each tool is containerized and exposed via a standardized API interface.

## Project Structure
```
bioinformatics_wrappers/
├── tools/                    # Individual tool implementations
│   ├── spider/              # SPIDER tool wrapper
│   │   ├── Dockerfile       # Docker configuration
│   │   ├── api/             # API implementation
│   │   ├── app.py           # FastAPI application
│   │   ├── requirements.txt # Python dependencies
│   │   └── README.md        # Tool-specific documentation
│   └── [other_tools]/       # Future tool wrappers
├── docker-compose.yml       # Orchestration for all tools
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

## Available Tools

### SPIDER
* **Description**: Stacking-based ensemble learning framework for accurate prediction of druggable proteins
* **Source code**: https://github.com/plenoi/SPIDER
* **API Endpoint**: `/api/v1/spider`
* **Input**: FASTA sequence file
* **Output**: CSV with predictions (sequence header, label, probability)

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Start all tools
docker-compose up -d

# Start specific tool
docker-compose up -d spider
```

### Individual Tool Usage
```bash
# Build and run SPIDER
cd tools/spider
docker build -t spider-api .
docker run -p 8000:8000 spider-api
```

## API Usage

### SPIDER API
```bash
# Submit a FASTA file for prediction
curl -X POST "http://localhost:8000/api/v1/spider/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_sequence.fasta"

# Check API health
curl "http://localhost:8000/api/v1/spider/health"
```

## Development

### Adding a New Tool
1. Create a new directory in `tools/`
2. Implement the API wrapper following the existing pattern
3. Add Dockerfile and requirements
4. Update docker-compose.yml
5. Add documentation

### API Standards
All tools follow these API conventions:
- Health check endpoint: `GET /api/v1/{tool}/health`
- Prediction endpoint: `POST /api/v1/{tool}/predict`
- Standardized error responses
- Input validation and file handling
