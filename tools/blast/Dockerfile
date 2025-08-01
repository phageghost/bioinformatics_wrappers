FROM python:3.12-slim@sha256:9c1d9ed7593f2552a4ea47362ec0d2ddf5923458a53d0c8e30edf8b398c94a31

# Build arguments
ARG VERSION=latest
ARG TARGETARCH

# Set working directory
WORKDIR /app

#Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Install micromamba properly (version 2.3.0)
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

# Create environments from YAML files
COPY environment-api.yml environment-blast.yml .
RUN micromamba env create -f environment-api.yml && micromamba env create -f environment-blast.yml

# Copy API wrapper files
COPY api/ ./api/
COPY app.py .
COPY run_combined_server.py .
COPY startup_check.py .
COPY VERSION .

# Create necessary directories
RUN mkdir -p /app/blast_output

# Set environment variables
ENV BLAST_DB_PATH=/blast_db
ENV PYTHONPATH=/app
ENV VERSION=${VERSION}
ENV PORT=8000
ENV AUTO_UPDATE=false

# Add labels for better image management
LABEL org.opencontainers.image.title="BLAST API"
LABEL org.opencontainers.image.description="REST API and MCP-like endpoints for BLAST sequence search. REQUIRES BLAST_DB_PATH environment variable and volume mount for database storage."
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.licenses="MIT"
LABEL maintainer="bioinformatics-wrappers"

# Health check with better error reporting
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD bash -c 'port=${PORT:-8000}; curl -f http://localhost:$port/api/v1/blastp/health || (echo "Health check failed. Check if BLAST_DB_PATH is properly configured." && exit 1)'

# Run startup validation and then the application
CMD micromamba run -n api python startup_check.py && micromamba run -n api python run_combined_server.py