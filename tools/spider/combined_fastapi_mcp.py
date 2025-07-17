#!/usr/bin/env python3
"""Combined FastAPI and FastMCP server"""

import asyncio
import logging
import tempfile
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Try to import MCP server
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.types import TextContent
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    FastMCP = None
    print(f"MCP not available: {e}")

from api.models import HealthResponse, PredictionResponse
from api.spider_service import SpiderService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SPIDER API",
    description="RESTful API wrapper for SPIDER: Stacking-based ensemble learning framework for accurate prediction of druggable proteins",
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

# Initialize MCP server if available
mcp_server = None
if MCP_AVAILABLE:
    print("MCP is available, initializing FastMCP server...")
    mcp_server = FastMCP(
        name="spider-bioinformatics",
        instructions="SPIDER: Stacking-based ensemble learning framework for accurate prediction of druggable proteins"
    )
    print("FastMCP server initialized successfully")
    
    # Add tools to MCP server
    @mcp_server.tool(
        name="predict_druggability",
        title="Predict Druggability",
        description="Predict druggability of a protein sequence using SPIDER"
    )
    async def predict_druggability(sequence: str):
        """Predict druggability of a protein sequence"""
        if not sequence:
            return [TextContent(type="text", text="Error: Sequence is required")]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
            try:
                fasta_content = f">sequence\n{sequence.strip()}\n"
                temp_file.write(fasta_content.encode("utf-8"))
                temp_file.flush()
                
                if not spider_service.validate_fasta_file(Path(temp_file.name)):
                    return [TextContent(type="text", text="Error: Invalid sequence format")]
                
                success, message, result = spider_service.run_spider_prediction(Path(temp_file.name))
                if not success:
                    return [TextContent(type="text", text=f"Error: SPIDER prediction failed: {message}")]
                
                if hasattr(result, 'label') and hasattr(result, 'probability'):
                    prediction = result.label
                    probability = result.probability
                else:
                    prediction = 'Unknown'
                    probability = 'Unknown'
                
                result_text = f"""
SPIDER Prediction Results:
- Status: Success
- Prediction: {prediction}
- Probability: {probability}
- Message: {message}
"""
                return [TextContent(type="text", text=result_text)]
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
    
    @mcp_server.tool(
        name="get_tool_info",
        title="Get Tool Info",
        description="Get information about the SPIDER tool"
    )
    async def get_tool_info():
        """Get information about the SPIDER tool"""
        tool_info = spider_service.get_tool_info()
        info_text = f"""
SPIDER Tool Information:
- Name: {tool_info.get('name', 'Unknown')}
- Version: {tool_info.get('version', 'Unknown')}
- Description: {tool_info.get('description', 'Unknown')}
- Input Format: {tool_info.get('input_format', 'Unknown')}
- Output Format: {tool_info.get('output_format', 'Unknown')}
"""
        return [TextContent(type="text", text=info_text)]
else:
    print("MCP is not available")

# FastAPI routes
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
async def get_tool_info():
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
    start_time = datetime.now()

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

            processing_time = (datetime.now() - start_time).total_seconds()

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

async def run_combined_server():
    """Run both FastAPI and FastMCP servers"""
    if MCP_AVAILABLE and mcp_server:
        print("Starting combined FastAPI and FastMCP servers...")
        # Run both servers concurrently
        await asyncio.gather(
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info"),
            mcp_server.run_streamable_http_async(host="0.0.0.0", port=8001)
        )
    else:
        print("Starting FastAPI server only...")
        await uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    asyncio.run(run_combined_server()) 