"""
SPIDER API Package

This package contains the core API components for the SPIDER bioinformatics tool wrapper.
It provides the service layer, data models, and MCP server implementation for protein
druggability prediction.

Modules:
    - models: Pydantic data models for API requests and responses
    - spider_service: Core service layer for SPIDER tool integration

The API package serves as the bridge between the FastAPI web layer and the underlying
SPIDER bioinformatics tool, providing:
- Data validation and serialization
- Business logic and tool execution
- MCP protocol support for AI agent integration
- Error handling and result processing

Author: Bioinformatics Wrappers Team
Version: 1.0.0
License: MIT
"""

from . import blast_service, models
