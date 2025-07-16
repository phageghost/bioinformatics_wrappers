# API Standards for Bioinformatics Tool Wrappers

This document defines the standards that all bioinformatics tool wrappers in this project must follow to ensure consistency and interoperability.

## Overview

All bioinformatics tool wrappers should provide a RESTful API with standardized endpoints, error handling, and response formats. This enables easy integration into agentic workflows and ensures a consistent developer experience.

## Base URL Structure

All APIs should follow this URL structure:
```
http://localhost:{port}/api/v1/{tool_name}/{endpoint}
```

Where:
- `{port}`: Unique port for each tool (8000, 8001, 8002, etc.)
- `{tool_name}`: Lowercase name of the tool (spider, blast, etc.)
- `{endpoint}`: Specific API endpoint

## Required Endpoints

### 1. Health Check
**Endpoint:** `GET /api/v1/{tool_name}/health`

**Purpose:** Check if the tool is running and healthy

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "tool": "TOOL_NAME",
  "version": "1.0.0"
}
```

### 2. Tool Information
**Endpoint:** `GET /api/v1/{tool_name}/info`

**Purpose:** Get information about the tool and its capabilities

**Response:**
```json
{
  "name": "TOOL_NAME",
  "version": "1.0",
  "description": "Tool description",
  "input_format": "FASTA",
  "output_format": "CSV",
  "home_directory": "/app/tool_name"
}
```

### 3. Prediction/Analysis
**Endpoint:** `POST /api/v1/{tool_name}/predict` (or `/analyze`, `/run`, etc.)

**Purpose:** Execute the main functionality of the tool

**Request:** File upload via multipart/form-data

**Response:**
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "results": [...],
  "total_sequences": 10,
  "processing_time": 12.5,
  "timestamp": "2024-01-15T10:30:00"
}
```

## Response Models

### Success Response
All successful responses should include:
- `status`: "success"
- `message`: Human-readable success message
- `timestamp`: ISO 8601 timestamp
- Tool-specific data fields

### Error Response
All error responses should follow this format:
```json
{
  "status": "error",
  "error": "Error type",
  "message": "Detailed error message",
  "timestamp": "2024-01-15T10:30:00"
}
```

## HTTP Status Codes

Use appropriate HTTP status codes:
- `200 OK`: Successful operation
- `400 Bad Request`: Invalid input (file format, missing parameters)
- `500 Internal Server Error`: Tool execution failed
- `503 Service Unavailable`: Tool temporarily unavailable

## File Upload Standards

### Supported Formats
- Accept common bioinformatics file formats
- Validate file format before processing
- Provide clear error messages for unsupported formats

### File Size Limits
- Set reasonable file size limits (e.g., 10MB)
- Return appropriate error for oversized files

### File Validation
- Validate file format and content
- Check for required headers or structure
- Provide specific error messages for validation failures

## Error Handling

### Validation Errors
- Return 400 status code for validation errors
- Provide specific error messages
- Include field-level error details when appropriate

### Processing Errors
- Return 500 status code for processing errors
- Log detailed error information
- Provide user-friendly error messages

### Timeout Handling
- Set appropriate timeouts for long-running operations
- Return timeout errors with clear messages
- Consider implementing async processing for very long operations

## Logging Standards

### Log Levels
- `INFO`: Normal operations, successful requests
- `WARNING`: Non-critical issues, deprecated features
- `ERROR`: Failed operations, exceptions
- `DEBUG`: Detailed debugging information

### Log Format
Include in logs:
- Timestamp
- Request ID (if applicable)
- Tool name
- Operation type
- Processing time
- Error details (for errors)

## Docker Standards

### Dockerfile Requirements
- Use official Python base images
- Install system dependencies first
- Copy requirements and install Python packages
- Set appropriate working directory
- Expose port 8000
- Include health check
- Use non-root user when possible

### Environment Variables
- `TOOL_HOME`: Path to tool installation
- `PYTHONPATH`: Python path for imports
- Tool-specific configuration variables

### Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/{tool_name}/health || exit 1
```

## Testing Standards

### Required Tests
- Health endpoint test
- Info endpoint test
- Prediction/analysis endpoint test
- Error handling test
- File validation test

### Test Data
- Provide sample input files for testing
- Include both valid and invalid test cases
- Document expected outputs

## Documentation Standards

### README Requirements
Each tool wrapper should include:
- Tool description and purpose
- API endpoint documentation
- Input/output format specifications
- Usage examples
- Error handling information
- Docker usage instructions
- Troubleshooting guide

### API Documentation
- Use OpenAPI/Swagger for API documentation
- Include example requests and responses
- Document all error codes and messages
- Provide interactive testing interface

## Security Considerations

### Input Validation
- Validate all input files and parameters
- Sanitize file names and paths
- Check file content for malicious code

### Resource Limits
- Set memory and CPU limits
- Implement request rate limiting
- Monitor resource usage

### Access Control
- Consider authentication for production use
- Implement API key validation if needed
- Log access attempts

## Performance Standards

### Response Times
- Health checks: < 1 second
- Info endpoints: < 1 second
- Processing endpoints: Varies by tool complexity

### Resource Usage
- Monitor memory usage
- Implement cleanup procedures
- Handle concurrent requests appropriately

## Versioning

### API Versioning
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Include version in API responses
- Maintain backward compatibility when possible

### Breaking Changes
- Document breaking changes clearly
- Provide migration guides
- Support multiple API versions if needed

## Monitoring and Observability

### Metrics
- Request count and response times
- Error rates and types
- Resource usage (CPU, memory, disk)
- Processing queue length

### Health Monitoring
- Implement comprehensive health checks
- Monitor dependent services
- Alert on critical failures

## Implementation Checklist

When implementing a new tool wrapper, ensure:

- [ ] All required endpoints are implemented
- [ ] Response models follow standards
- [ ] Error handling is comprehensive
- [ ] File validation is implemented
- [ ] Docker configuration is correct
- [ ] Health checks are working
- [ ] Tests are written and passing
- [ ] Documentation is complete
- [ ] Logging is implemented
- [ ] Security considerations are addressed

## Example Implementation

See the SPIDER tool wrapper (`tools/spider/`) for a complete example of these standards in practice. 