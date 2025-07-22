"""
SPIDER API Data Models

This module defines Pydantic data models for the SPIDER API, providing type safety,
validation, and serialization for all API requests and responses.

The models ensure consistent data structures across the API and provide automatic
validation of incoming requests and outgoing responses. They also serve as the
foundation for OpenAPI/Swagger documentation generation.

Models:
    - HealthResponse: Health check endpoint response
    - PredictionRequest: Protein prediction request (legacy, unused)
    - PredictionResult: Individual prediction result with label and probability
    - PredictionResponse: Complete prediction response with metadata
    - ErrorResponse: Standardized error response format

Key Features:
- Automatic validation of request/response data
- Type hints for better IDE support and documentation
- Consistent error response format
- ISO 8601 timestamp handling
- OpenAPI schema generation

Usage:
    These models are used throughout the FastAPI application for request/response
    validation and serialization. They ensure type safety and consistent API
    behavior across all endpoints.

Dependencies:
    - pydantic: Data validation and serialization
    - datetime: Timestamp handling

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""
from datetime import datetime

from pydantic import BaseModel


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
