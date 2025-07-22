FROM python:3.12-slim

# Build arguments
ARG VERSION=latest
ARG TARGETARCH

# Set working directory
WORKDIR /app

Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    gcc \
    g++ \
    make \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Install micromamba properly
RUN if [ "$TARGETARCH" = "arm64" ]; then \
      ARCH=linux-aarch64 ; \
    else \
      ARCH=linux-64 ; \
    fi && \
    wget -qO- https://micro.mamba.pm/api/micromamba/${ARCH}/latest | tar -xvj bin/micromamba && \
    mv bin/micromamba /usr/local/bin/ && \
    micromamba shell init -s bash

# Initialize micromamba for the shell
SHELL ["/bin/bash", "-c"]

# Create API environment with Python 3.12 and API dependencies
COPY environment.yml .
RUN micromamba env create -f environment.yml

# Copy API wrapper files
COPY api/ ./api/
COPY app.py .
COPY run_combined_server.py .

# Create necessary directories
RUN mkdir -p /app/spider_tool/input /app/spider_tool/output

# Set environment variables
ENV PYTHONPATH=/app
ENV VERSION=${VERSION}
ENV PORT=8000

# Add labels for better image management
LABEL org.opencontainers.image.title="BLAST API"
LABEL org.opencontainers.image.description="REST API and MCP-like endpoints for BLAST sequence search"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.licenses="MIT"
LABEL maintainer="bioinformatics-wrappers"

# Health check (tries PORT env var, then common ports)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD bash -c 'port=${PORT:-8000}; curl -f http://localhost:$port/api/v1/spider/health' || exit 1

# Run the application using the API environment
CMD ["micromamba", "run", "-n", "api", "python", "run_combined_server.py"]