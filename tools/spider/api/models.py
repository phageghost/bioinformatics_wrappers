from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: datetime
    tool: str
    version: str


class PredictionRequest(BaseModel):
    """Prediction request model"""

    filename: str
    file_size: int


class PredictionResult(BaseModel):
    """Individual prediction result"""

    label: str
    probability: float


class PredictionResponse(BaseModel):
    """Prediction response model"""

    status: str
    message: str
    result: PredictionResult
    processing_time: float
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response model"""

    status: str
    error: str
    message: str
    timestamp: datetime
