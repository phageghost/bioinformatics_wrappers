# Quick Start Guide

Get up and running with the bioinformatics tool wrappers in minutes!

## Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)
- curl (for testing APIs)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/bioinformatics_wrappers.git
cd bioinformatics_wrappers

# Verify the structure
ls -la
```

## Step 2: Start the Services

### Option A: Using Docker Compose (Recommended)

```bash
# Start all tools
docker-compose up -d

# Or start just SPIDER
docker-compose up -d spider
```

### Option B: Individual Docker Build

```bash
# Build SPIDER
cd tools/spider
docker build -t spider-api .
docker run -p 8000:8000 spider-api
```

## Step 3: Verify Installation

```bash
# Check if SPIDER is running
curl http://localhost:8000/api/v1/spider/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00",
#   "tool": "SPIDER",
#   "version": "1.0.0"
# }
```

## Step 4: Test the API

### Using the Test Script

```bash
# Run the automated test
python scripts/test_api.py spider
```

### Manual Testing

```bash
# Get tool information
curl http://localhost:8000/api/v1/spider/info

# Submit a FASTA file for prediction
curl -X POST "http://localhost:8000/api/v1/spider/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@tools/spider/test_data/sample_proteins.fasta"
```

## Step 5: View API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 6: Use in Your Workflow

### Python Example

```python
import requests

# Submit protein sequences for prediction
with open('proteins.fasta', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/v1/spider/predict',
        files=files
    )

if response.status_code == 200:
    results = response.json()
    print(f"Processed {results['total_sequences']} sequences")
    for result in results['results']:
        print(f"{result['sequence_header']}: {result['label']}")
```

### JavaScript Example

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
  console.log('Results:', response.data);
})
.catch(error => {
  console.error('Error:', error.response.data);
});
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Kill the process or use a different port
   docker run -p 8001:8000 spider-api
   ```

2. **Docker build fails**
   ```bash
   # Check Docker logs
   docker-compose logs spider
   
   # Rebuild without cache
   docker-compose build --no-cache spider
   ```

3. **API not responding**
   ```bash
   # Check container status
   docker-compose ps
   
   # Check container logs
   docker-compose logs spider
   
   # Restart the service
   docker-compose restart spider
   ```

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service health
docker inspect spider-api | grep Health -A 10
```

## Next Steps

1. **Add More Tools**: Follow the API standards in `docs/API_STANDARDS.md`
2. **Customize**: Modify the Docker configurations for your environment
3. **Scale**: Use Docker Swarm or Kubernetes for production deployment
4. **Monitor**: Add logging and monitoring solutions

## Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Report problems on GitHub
- **Examples**: See `tools/spider/` for implementation examples

## Production Deployment

For production use, consider:

- **Security**: Add authentication and HTTPS
- **Monitoring**: Implement logging and metrics
- **Scaling**: Use load balancers and multiple instances
- **Backup**: Set up data persistence and backups
- **Updates**: Implement automated deployment pipelines 