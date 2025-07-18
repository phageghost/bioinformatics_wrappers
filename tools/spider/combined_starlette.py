from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.applications import Starlette
import tempfile
import os
from pathlib import Path
from datetime import datetime

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import MCP server
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.types import TextContent
    MCP_AVAILABLE = True
    logger.info("MCP library imported successfully")
except ImportError as e:
    MCP_AVAILABLE = False
    FastMCP = None
    logger.error(f"MCP not available: {e}")

from api.models import HealthResponse, PredictionResponse
from api.spider_service import SpiderService

# --- FastAPI app (REST) ---
app = FastAPI(
    title="SPIDER API",
    description="RESTful API wrapper for SPIDER: Stacking-based ensemble learning framework for accurate prediction of druggable proteins",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

spider_service = SpiderService()

@app.get("/", response_model=dict)
async def root():
    return {
        "message": "SPIDER API - Bioinformatics Tool Wrapper",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/spider/health",
    }

@app.get("/v1/spider/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy", timestamp=datetime.now(), tool="SPIDER", version="1.0.0"
    )

@app.get("/v1/spider/info", response_model=dict)
async def get_tool_info():
    return spider_service.get_tool_info()

@app.post("/v1/spider/predict", response_model=PredictionResponse)
async def predict_druggable_proteins(sequence: str):
    start_time = datetime.now()
    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No sequence provided"
        )
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
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
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
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )

# --- MCP FastMCP app ---
if MCP_AVAILABLE:
    logger.info("Creating FastMCP server...")
    mcp_server = FastMCP(
        name="spider-bioinformatics",
        instructions="SPIDER: Stacking-based ensemble learning framework for accurate prediction of druggable proteins"
    )
    logger.info("FastMCP server created successfully")
    
    @mcp_server.tool(
        name="predict_druggability",
        title="Predict Druggability",
        description="Predict druggability of a protein sequence using SPIDER"
    )
    async def mcp_predict_druggability(sequence: str):
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
    async def mcp_get_tool_info():
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
    
    logger.info("Creating MCP streamable HTTP app...")
    mcp_app = mcp_server.streamable_http_app()
    logger.info("MCP streamable HTTP app created successfully")
    
    # Use the original MCP app as-is
    logger.info("Using original MCP app")
else:
    mcp_app = None
    logger.warning("MCP not available, skipping MCP app creation")

# --- Starlette multiplexer ---
logger.info("Creating Starlette routes...")
routes = []
if mcp_app:
    logger.info("Adding FastAPI route at /api")
    routes.append(Mount("/api", app))
    logger.info("Adding MCP route at /mcp")
    routes.append(Mount("/mcp", mcp_app))
else:
    logger.warning("No MCP app available, using FastAPI at root")
    routes.append(Mount("/", app))

logger.info("Creating Starlette app...")
starlette_app = Starlette(routes=routes)
logger.info("Starlette app created successfully") 