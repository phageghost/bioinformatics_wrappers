import os
import time
import tempfile
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.models import HealthResponse, SearchResponse
from tools.blast.api.blast_service import BLASTpService

version = open('VERSION', 'r', encoding='utf-8').read().strip()

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

# Initialize BLASTp service
blastp_service = BLASTpService(db_path=Path("blast_db"))


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
async def search_protein_sequence(sequence: str):
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
            if not blastp_service.validate_fasta_protein_file(Path(temp_file.name)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sequence format",
                )

            # Run SPIDER prediction
            success, message, result = blastp_service.run_blastp_search(
                Path(temp_file.name)
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
                        }
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
                    Path(temp_file.name)
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=message,
                    )
                processing_time = time.time() - start_time

                if hasattr(result, "report"):
                    report = result.report
                else:
                    report = "Unknown"

                result_text = f"""
BLASTp Search Results:
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
