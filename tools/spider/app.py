"""
SPIDER API - FastAPI Application Module

This module provides a RESTful API wrapper for SPIDER (Stacking-based ensemble learning
framework for accurate prediction of druggable proteins). It includes both traditional
REST endpoints and MCP-like endpoints for AI agent integration.

The application serves as a bridge between the SPIDER bioinformatics tool and modern
web applications, providing:
- RESTful API endpoints for protein druggability prediction
- MCP-like endpoints for AI agent compatibility
- Health monitoring and tool information endpoints
- Comprehensive error handling and validation

Key Features:
- Single-port deployment (both REST and MCP-like endpoints)
- Automatic sequence validation and FASTA format handling
- Structured JSON responses with prediction results
- CORS support for cross-origin requests
- OpenAPI/Swagger documentation generation

Endpoints:
- GET /: Root endpoint with API information
- GET /api/v1/spider/health: Health check endpoint
- GET /api/v1/spider/info: Tool information endpoint
- POST /api/v1/spider/predict: Protein druggability prediction
- GET /mcp/tools: List available MCP-like tools
- POST /mcp/call: Execute MCP-like tool calls

Dependencies:
- FastAPI: Web framework
- MCP (optional): Model Context Protocol support
- SPIDER Service: Core bioinformatics functionality

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""

import os
import time
import tempfile
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.models import HealthResponse, PredictionResponse
from api.spider_service import SpiderService

# Initialize FastAPI app
app = FastAPI(
    title="SPIDER API",
    description="RESTful API wrapper for SPIDER: Stacking-based ensemble learning framework for\
accurate prediction of druggable proteins",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SPIDER service
spider_service = SpiderService()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SPIDER API - Bioinformatics Tool Wrapper",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/spider/health",
    }


@app.get("/api/v1/spider/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy", timestamp=datetime.now(), tool="SPIDER", version="1.0.0"
    )


@app.get("/api/v1/spider/info", response_model=dict)
async def get_tool_info_rest():
    """Get information about the SPIDER tool"""
    return spider_service.get_tool_info()


@app.post("/api/v1/spider/predict", response_model=PredictionResponse)
async def predict_druggable_proteins(sequence: str):
    """
    Predict druggability of a protein sequence

    Args:
        sequence: a string containing a protein sequences

    Returns:
        Prediction results with label and probability
    """
    start_time = time.time()

    # Validate file
    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No sequence provided"
        )

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
        try:
            # Create FASTA format content - ensure sequence is on a single line
            fasta_content = f">sequence\n{sequence.strip()}\n"
            # Write FASTA content to temporary file
            temp_file.write(fasta_content.encode("utf-8"))
            temp_file.flush()

            # Validate FASTA format
            if not spider_service.validate_fasta_file(Path(temp_file.name)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sequence format",
                )

            # Run SPIDER prediction
            success, message, result = spider_service.run_spider_prediction(
                Path(temp_file.name)
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
                )

            processing_time = time.time() - start_time

            return PredictionResponse(
                status="success",
                message=message,
                result=result,
                processing_time=round(processing_time, 2),
                timestamp=datetime.now(),
            )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


# MCP-like endpoints for AI agents
@app.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP-like tools for AI agent integration."""
    return {
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
                            "description": "Protein sequence to analyze",
                        }
                    },
                    "required": ["sequence"],
                },
            },
            {
                "name": "get_tool_info",
                "title": "Get Tool Info",
                "description": "Get information about the SPIDER tool",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
        ]
    }


@app.post("/mcp/call")
async def call_mcp_tool(request: dict):
    """Call an MCP-like tool with the provided arguments."""
    tool_name = request.get("name")
    arguments = request.get("arguments", {})

    if tool_name == "predict_druggability":
        sequence = arguments.get("sequence")
        if not sequence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Sequence is required"
            )

        start_time = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
            try:
                fasta_content = f">sequence\n{sequence.strip()}\n"
                temp_file.write(fasta_content.encode("utf-8"))
                temp_file.flush()
                if not spider_service.validate_fasta_file(Path(temp_file.name)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid sequence format",
                    )
                success, message, result = spider_service.run_spider_prediction(
                    Path(temp_file.name)
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=message,
                    )
                processing_time = time.time() - start_time

                if hasattr(result, "label") and hasattr(result, "probability"):
                    prediction = result.label
                    probability = result.probability
                else:
                    prediction = "Unknown"
                    probability = "Unknown"

                result_text = f"""
SPIDER Prediction Results:
- Status: Success
- Prediction: {prediction}
- Probability: {probability}
- Message: {message}
- Processing Time: {round(processing_time, 2)}s
"""
                return {"content": [{"type": "text", "text": result_text}]}
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)

    elif tool_name == "get_tool_info":
        tool_info = spider_service.get_tool_info()
        info_text = f"""
SPIDER Tool Information:
- Name: {tool_info.get('name', 'Unknown')}
- Version: {tool_info.get('version', 'Unknown')}
- Description: {tool_info.get('description', 'Unknown')}
- Input Format: {tool_info.get('input_format', 'Unknown')}
- Output Format: {tool_info.get('output_format', 'Unknown')}
"""
        return {"content": [{"type": "text", "text": info_text}]}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown tool: {tool_name}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
    """Custom exception handler for HTTP errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail,
            "message": str(exc.detail),
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(_, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
