
from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: datetime
    tool: str
    version: str


class SearchRequest(BaseModel):

    fasta_fpath: str
    evalue: float
    max_target_seqs: int

class BLASTpResult(BaseModel):
    """Individual search result"""

    report: str


class SearchResponse(BaseModel):
    """Search response model"""

    status: str
    message: str
    result: BLASTpResult
    processing_time: float
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response model"""

    status: str
    error: str
    message: str
    timestamp: datetime
