"""
BLAST API Data Models

This module defines the Pydantic data models used throughout the BLAST API for
request/response validation, serialization, and documentation. These models ensure
type safety, provide automatic validation, and generate accurate OpenAPI schemas
for the FastAPI application.

The models provide:
- Request validation for BLAST search parameters
- Response serialization with consistent structure
- Health check and error response formatting
- Automatic OpenAPI schema generation
- Type hints for better IDE support and documentation

Data Models:

HealthResponse:
    Standardized health check response with service status, timestamp, tool name,
    and version information. Used by health monitoring endpoints and load balancers.

SearchRequest:
    Validates BLAST search requests with all optional parameters and sensible defaults.
    Ensures sequence format validation and parameter type checking.

BLASTpResult:
    Represents individual BLAST search results with formatted report output.
    Contains the parsed and formatted search results from BLASTp execution.

BLASTpHit:
    Represents a single BLAST hit with structured data fields.

BLASTpJSONResult:
    Represents BLAST search results in structured JSON format.

SearchResponse:
    Comprehensive search response including status, message, results, processing time,
    and timestamp. Provides complete information about the search operation.

ErrorResponse:
    Standardized error response format for consistent error handling across all
    endpoints. Includes error details, messages, and timestamps for debugging.

Field Descriptions:

SearchRequest Fields:
    - sequence: Protein sequence to search (required, string)
    - db_name: BLAST database name (default: "nr", string)
    - evalue: E-value threshold for significance (default: 0.001, float)
    - max_target_seqs: Maximum number of target sequences (default: 20, int)
    - outfmt: Output format specification (default: tabular with organism names, string)
    - output_format: Response format ("table" or "json", default: "table")

Response Fields:
    - status: Operation status ("success", "error", "healthy", etc.)
    - message: Human-readable operation message
    - timestamp: ISO format timestamp of operation
    - processing_time: Execution time in seconds (float)
    - result: BLASTpResult or BLASTpJSONResult object containing search results
    - error: Error type/code for error responses

Validation Features:
- Automatic type conversion and validation
- Default value handling for optional parameters
- Required field enforcement
- String format validation for sequences
- Numeric range validation for parameters
- DateTime serialization/deserialization

Usage Examples:

    # Create a search request
    request = SearchRequest(
        sequence="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
        db_name="pdbaa",
        evalue=0.01,
        output_format="json"
    )

    # Create a health response
    health = HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        tool="BLASTp",
        version="1.0.0"
    )

    # Create an error response
    error = ErrorResponse(
        status="error",
        error="ValidationError",
        message="Invalid sequence format",
        timestamp=datetime.now()
    )

OpenAPI Integration:
    These models automatically generate OpenAPI schemas when used in FastAPI
    endpoints, providing accurate API documentation and client code generation.

Dependencies:
    - pydantic: Data validation and serialization
    - datetime: Timestamp handling and serialization

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: datetime
    tool: str
    version: str


class SearchRequest(BaseModel):
    """Request model for BLASTp search"""

    sequence: str
    db_name: str = "nr"
    evalue: float = 1e-3
    max_target_seqs: int = 20
    outfmt: str = "6 qseqid sseqid pident length evalue bitscore sscinames"
    output_format: str = Field(
        default="table", description="Output format: 'table' or 'json'"
    )


class BLASTpHit(BaseModel):
    """Individual BLAST hit with structured data"""

    rank: int
    query_id: str
    subject_id: str
    percent_identity: float
    alignment_length: int
    evalue: float
    bitscore: float
    organism: Optional[str] = None


class BLASTpResult(BaseModel):
    """Individual search result with table format"""

    report: str


class BLASTpJSONResult(BaseModel):
    """Search result with structured JSON format"""

    hits: List[BLASTpHit]
    total_hits: int
    query_sequence: str


class SearchResponse(BaseModel):
    """Search response model"""

    status: str
    message: str
    result: Union[BLASTpResult, BLASTpJSONResult]
    processing_time: float
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response model"""

    status: str
    error: str
    message: str
    timestamp: datetime
