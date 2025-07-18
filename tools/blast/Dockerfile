FROM python:3.12-slim

# Build arguments
ARG VERSION=latest
ARG TARGETARCH

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV VERSION=${VERSION}

# Add labels for better image management
LABEL org.opencontainers.image.title="BLAST Bioinformatics API"
LABEL org.opencontainers.image.description="REST API and MCP-like endpoints for BLAST sequence alignment"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.source="https://blast.ncbi.nlm.nih.gov/"
LABEL org.opencontainers.image.licenses="MIT"
LABEL maintainer="bioinformatics-wrappers"

# Expose port
EXPOSE 8000

# Simple health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Mock command (in real implementation, this would run the actual BLAST API)
CMD ["echo", "BLAST API would run here"] 