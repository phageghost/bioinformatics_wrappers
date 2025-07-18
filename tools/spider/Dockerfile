FROM python:3.12-slim

# Build arguments
ARG VERSION=latest
ARG TARGETARCH

# Set working directory
WORKDIR /app

# Install system dependencies including build tools
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
COPY requirements.txt .
RUN micromamba create -n api python=3.12 -y && \
    micromamba run -n api pip install --no-cache-dir -r requirements.txt

# Clone SPIDER repository
RUN git clone https://github.com/plenoi/SPIDER.git /app/spider_tool

# Create conda environment for SPIDER with Python 3.9
COPY requirements-spider.txt .
RUN micromamba create -n spider python=3.9 -y && \
    micromamba run -n spider pip install --no-cache-dir -r requirements-spider.txt

# Copy API wrapper files
COPY api/ ./api/
COPY app.py .
COPY run_combined_v2.py .

# Create necessary directories
RUN mkdir -p /app/spider_tool/input /app/spider_tool/output

# Set environment variables
ENV PYTHONPATH=/app
ENV SPIDER_HOME=/app/spider_tool
ENV SPIDER_ENV=spider
ENV VERSION=${VERSION}

# Add labels for better image management
LABEL org.opencontainers.image.title="SPIDER Bioinformatics API"
LABEL org.opencontainers.image.description="REST API and MCP-like endpoints for SPIDER protein druggability prediction"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.source="https://github.com/plenoi/SPIDER"
LABEL org.opencontainers.image.licenses="MIT"
LABEL maintainer="bioinformatics-wrappers"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/spider/health || exit 1

# Run the application using the API environment
CMD ["micromamba", "run", "-n", "api", "python", "run_combined_v2.py"]