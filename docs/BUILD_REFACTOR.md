# Build Process Refactoring

## Overview

The build process has been refactored to use micromamba exclusively with environment YAML files instead of pip requirements files. This provides better dependency management, reproducibility, and consistency across all tools.

## Changes Made

### 1. **BLAST Tool** (`tools/blast/`)
- ✅ Already using micromamba exclusively
- ✅ Environment files: `environment-api.yml` and `environment-blast.yml`
- ✅ All packages locked to exact versions with build strings
- ✅ Base image locked to SHA256: `9c1d9ed7593f2552a4ea47362ec0d2ddf5923458a53d0c8e30edf8b398c94a31`

### 2. **SPIDER Tool** (`tools/spider/`)
- ✅ **Refactored to use micromamba exclusively**
- ✅ **Created environment files**: `environment-api.yml` and `environment-spider.yml`
- ✅ **Removed pip requirements files**: `requirements.txt` and `requirements-spider.txt`
- ✅ **Updated Dockerfile** to use environment YAML files
- ✅ **All packages locked to exact versions** with build strings
- ✅ **Base image locked** to same SHA256 as BLAST tool

## Environment Structure

### API Environment (Both Tools)
- **Python**: 3.12.11
- **Key packages**: FastAPI, Uvicorn, Pydantic, Aiofiles
- **Total packages**: 67 (including dependencies)

### BLAST Environment
- **Python**: 3.12.11
- **Key packages**: BLAST, Entrez Direct, NCBI VDB
- **Total packages**: 67 (including dependencies)

### SPIDER Environment
- **Python**: 3.9.23
- **Key packages**: scikit-learn, numpy, pandas, scipy, biopython
- **Total packages**: 42 (including dependencies)

## Benefits

1. **Reproducibility**: Exact package versions ensure consistent builds
2. **Dependency Resolution**: micromamba provides better dependency resolution than pip
3. **Channel Management**: Proper use of conda-forge and bioconda channels
4. **Build Speed**: micromamba is faster than conda for environment creation
5. **Consistency**: All tools now use the same build approach
6. **Locking**: All packages are locked to specific versions and build strings

## Build Commands

### BLAST Tool
```bash
cd tools/blast
docker build -t blast-api .
```

### SPIDER Tool
```bash
cd tools/spider
docker build -t spider-api .
```

## Environment Files

### `environment-api.yml`
- Contains all API dependencies for both tools
- Uses conda-forge channel
- Python 3.12.11 with exact build string

### `environment-blast.yml`
- Contains BLAST-specific dependencies
- Uses conda-forge and bioconda channels
- Python 3.12.11 with exact build string

### `environment-spider.yml`
- Contains SPIDER-specific dependencies
- Uses conda-forge channel
- Python 3.9.23 with exact build string

## Version Locking

All packages are locked to exact versions including build strings:
- Example: `fastapi=0.116.1=h26c32bb_1`
- This ensures complete reproducibility across different build environments
- Build strings are architecture-specific and ensure binary compatibility

## Base Image

Both tools now use the same locked base image:
- `python:3.12-slim@sha256:9c1d9ed7593f2552a4ea47362ec0d2ddf5923458a53d0c8e30edf8b398c94a31`

## micromamba Version

- Version: 2.3.0
- Installed from official micromamba distribution
- Supports both x86_64 and ARM64 architectures 