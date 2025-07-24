"""
BLASTp FastAPI Application

This module provides a comprehensive FastAPI application that wraps the BLASTp
bioinformatics tool, offering both REST API endpoints and MCP-like endpoints for
AI agent integration. It serves as the main web interface for BLAST protein
sequence searches with full parameter customization and result processing.

The application provides:
- RESTful API endpoints for BLASTp searches
- MCP-like endpoints for AI agent integration
- Comprehensive error handling and validation
- CORS support for cross-origin requests
- Automatic OpenAPI documentation generation
- Health monitoring and tool information endpoints
- Temporary file management for sequence processing

REST API Endpoints:
- GET /: Root endpoint with API information
- GET /api/v1/blastp/health: Health check endpoint
- GET /api/v1/blastp/info: Tool information and metadata
- POST /api/v1/blastp/search: Protein sequence search with full parameter control
- GET /docs: Interactive API documentation (Swagger UI)
- GET /redoc: Alternative API documentation (ReDoc)

MCP-like Endpoints (AI Agent Integration):
- GET /mcp/tools: Discover available tools and their schemas
- POST /mcp/call: Execute tools with provided arguments

Search Parameters:
- sequence: Protein sequence to search (required)
- db_name: BLAST database name (default: "nr")
- evalue: E-value threshold (default: 0.001)
- max_target_seqs: Maximum target sequences (default: 20)
- outfmt: Output format specification (default: tabular with organism names)

Features:
- Automatic FASTA format validation
- Temporary file management with cleanup
- Comprehensive error handling with detailed messages
- Processing time measurement and reporting
- Cross-platform compatibility
- Container-ready with environment variable support
- Graceful error responses with proper HTTP status codes

Error Handling:
- 400: Bad Request (invalid sequence, missing parameters)
- 422: Validation Error (FastAPI automatic validation)
- 500: Internal Server Error (BLAST execution failures)
- Custom exception handlers for consistent error responses

Usage:
    # Start the server
    uvicorn app:app --host 0.0.0.0 --port 8000
    
    # Example REST API call
    curl -X POST "http://localhost:8000/api/v1/blastp/search" \
         -H "Content-Type: application/json" \
         -d '{"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"}'
    
    # Example MCP-like call
    curl -X POST "http://localhost:8000/mcp/call" \
         -H "Content-Type: application/json" \
         -d '{"name": "perform_blastp_search", "arguments": 
            {"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
             "db_name": "pdbaa", "evalue": 0.001, "max_target_seqs": 20, 
             }'

Environment Variables:
- BLAST_DB_PATH: Path to BLAST database directory (set by container)
- PORT: Server port (default: 8000, handled by run_combined_server.py)

Dependencies:
    - fastapi: Web framework for building APIs
    - uvicorn: ASGI server for running FastAPI
    - pydantic: Data validation and settings management
    - python-multipart: File upload support
    - aiofiles: Asynchronous file operations

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

try:
    # Try relative imports first (for when imported as part of a package)
    from .api.models import HealthResponse, SearchResponse, SearchRequest
    from .api.blast_service import BLASTpService
except ImportError:
    # Fall back to absolute imports (for when run as script or from local directory)
    from api.models import HealthResponse, SearchResponse, SearchRequest
    from api.blast_service import BLASTpService


version = open("VERSION", "r", encoding="utf-8").read().strip()


# Initialize BLASTp service
try:
    blastp_service = BLASTpService()
except ValueError as e:
    print("=" * 80)
    print("❌ BLAST API Configuration Error")
    print("=" * 80)
    print(str(e))
    print("=" * 80)
    print("The BLAST API cannot start without proper database configuration.")
    print("Please fix the configuration issue and restart the service.")
    print("=" * 80)
    import sys

    sys.exit(1)


# Initialize FastAPI app
app = FastAPI(
    title="BLASTp API",
    description="RESTful API wrapper for BLASTp: Basic Local Alignment Search Tool",
    version=version,
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


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "BLASTp API - Bioinformatics Tool Wrapper",
        "version": version,
        "docs": "/docs",
        "health": "/api/v1/blastp/health",
    }


@app.get("/api/v1/blastp/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy", timestamp=datetime.now(), tool="BLASTp", version=version
    )


@app.get("/api/v1/blastp/info", response_model=dict)
async def get_tool_info_rest():
    """Get information about the BLASTp tool"""
    return blastp_service.get_tool_info()


@app.post("/api/v1/blastp/search", response_model=SearchResponse)
async def search_protein_sequence(request: SearchRequest):
    """Search a protein sequence against a BLAST database"""
    start_time = time.time()

    # Validate sequence
    if not request.sequence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No sequence provided"
        )

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
        try:
            # Create FASTA format content - ensure sequence is on a single line
            fasta_content = f">sequence\n{request.sequence.strip()}\n"
            # Write FASTA content to temporary file
            temp_file.write(fasta_content.encode("utf-8"))
            temp_file.flush()

            # Validate FASTA format
            if not blastp_service.validate_fasta_protein_file(Path(temp_file.name)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sequence format",
                )

            # Run BLASTp search with all parameters
            success, message, result = blastp_service.run_blastp_search(
                fasta_fpath=Path(temp_file.name),
                db_name=request.db_name,
                evalue=request.evalue,
                max_target_seqs=request.max_target_seqs,
                outfmt=request.outfmt,
                output_format=request.output_format,
                query_sequence=request.sequence,
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
                )

            processing_time = time.time() - start_time

            return SearchResponse(
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
                "name": "perform_blastp_search",
                "title": "BLAST protein sequence",
                "description": "Search a protein sequence against a BLAST database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sequence": {
                            "type": "string",
                            "description": "Protein sequence to analyze",
                        },
                        "db_name": {
                            "type": "string",
                            "description": "BLAST database name (default: nr)",
                            "default": "nr",
                        },
                        "evalue": {
                            "type": "number",
                            "description": "E-value threshold (default: 0.001)",
                            "default": 0.001,
                        },
                        "max_target_seqs": {
                            "type": "integer",
                            "description": "Maximum number of target sequences (default: 20)",
                            "default": 20,
                        },
                        "outfmt": {
                            "type": "string",
                            "description": "Output format (default: 6 qseqid sseqid pident length \
evalue bitscore sscinames)",
                            "default": "6 qseqid sseqid pident length evalue bitscore sscinames",
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Response format: 'table' for formatted text or 'json' \
for structured data (default: table)",
                            "default": "table",
                            "enum": ["table", "json"],
                        },
                    },
                    "required": ["sequence"],
                },
            },
            {
                "name": "get_tool_info",
                "title": "Get Tool Info",
                "description": "Get information about the BLASTp tool",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
        ]
    }


@app.post("/mcp/call")
async def call_mcp_tool(request: dict):
    """Call an MCP-like tool with the provided arguments."""
    tool_name = request.get("name")
    arguments = request.get("arguments", {})

    if tool_name == "perform_blastp_search":
        sequence = arguments.get("sequence")
        if not sequence:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Sequence is required"
            )

        # Get all parameters with defaults
        db_name = arguments.get("db_name", "nr")
        evalue = arguments.get("evalue", 1e-3)
        max_target_seqs = arguments.get("max_target_seqs", 20)
        outfmt = arguments.get(
            "outfmt", "6 qseqid sseqid pident length evalue bitscore sscinames"
        )
        output_format = arguments.get("output_format", "table")

        start_time = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as temp_file:
            try:
                fasta_content = f">sequence\n{sequence.strip()}\n"
                temp_file.write(fasta_content.encode("utf-8"))
                temp_file.flush()
                if not blastp_service.validate_fasta_protein_file(Path(temp_file.name)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid sequence format",
                    )
                success, message, result = blastp_service.run_blastp_search(
                    fasta_fpath=Path(temp_file.name),
                    db_name=db_name,
                    evalue=evalue,
                    max_target_seqs=max_target_seqs,
                    outfmt=outfmt,
                    output_format=output_format,
                    query_sequence=sequence,
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=message,
                    )
                processing_time = time.time() - start_time

                if output_format.lower() == "json" and hasattr(result, "hits"):
                    # JSON format response
                    result_text = f"""
BLASTp Search Results (JSON Format):
- Status: Success
- Total Hits: {result.total_hits}
- Query Sequence: {result.query_sequence[:50]}{'...' if len(result.query_sequence) > 50 else ''}
- Processing Time: {round(processing_time, 2)}s

Top Hits:
"""
                    for i, hit in enumerate(result.hits[:5]):  # Show top 5 hits
                        result_text += f"""
{i+1}. {hit.subject_id}
   - Identity: {hit.percent_identity}%
   - Alignment Length: {hit.alignment_length}
   - E-value: {hit.evalue}
   - Bitscore: {hit.bitscore}
   - Organism: {hit.organism or 'Unknown'}
"""
                else:
                    # Table format response
                    if hasattr(result, "report"):
                        report = result.report
                    else:
                        report = "Unknown"

                    result_text = f"""
BLASTp Search Results (Table Format):
- Status: Success
- Report: {report}
- Message: {message}
- Processing Time: {round(processing_time, 2)}s
"""
                return {"content": [{"type": "text", "text": result_text}]}
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)

    elif tool_name == "get_tool_info":
        tool_info = blastp_service.get_tool_info()
        info_text = f"""
BLASTp Tool Information:
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
