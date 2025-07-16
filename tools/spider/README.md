# SPIDER API Wrapper

RESTful API wrapper for SPIDER: Stacking-based ensemble learning framework for accurate prediction of druggable proteins.

## Overview

SPIDER is a machine learning tool that predicts whether proteins are druggable based on their amino acid sequences. This wrapper provides a RESTful API interface to make SPIDER easily accessible for agentic workflows.

## Features

- **RESTful API**: Standardized HTTP endpoints for easy integration
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