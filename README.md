# Bioinformatics Wrappers

Dockerized bioinformatics tools with API wrappers for both REST and MCP-like protocols, designed for agentic workflows and AI integration.

## 🚀 Overview

This repository contains Dockerized bioinformatics tools wrapped with both RESTful APIs and MCP-like endpoints for seamless integration into agentic workflows and AI applications. Each tool is containerized and exposed via standardized interfaces.

## 🏗️ Project Structure

```
bioinformatics_wrappers/
├── tools/                    # Individual tool implementations
│   ├── spider/              # SPIDER tool wrapper
│   │   ├── Dockerfile       # Docker configuration
│   │   ├── VERSION          # Tool version file
│   │   ├── BUILD            # Build number counter (auto-generated)
│   │   ├── api/             # Core API implementation
│   │   ├── app.py           # FastAPI application (REST + MCP-like)
│   │   ├── run_combined_server.py # Server entrypoint
│   │   ├── test_rest_api.py # REST API test suite
│   │   ├── test_mcp_endpoints.py # MCP endpoint test suite
│   │   ├── examples/        # Usage examples
│   │   ├── requirements.txt # Python dependencies
│   │   └── README.md        # Tool-specific documentation
│   ├── blast/               # BLAST tool wrapper (example)
│   │   ├── Dockerfile       # Docker configuration
│   │   ├── VERSION          # Tool version file
│   │   └── BUILD            # Build number counter (auto-generated)
│   └── [other_tools]/       # Future tool wrappers
├── docker-compose.yml       # Orchestration for all tools
├── scripts/                 # Utility scripts
│   └── build.sh            # Build script with auto-versioning and CI/CD
└── docs/                    # Documentation
```

## 🛠️ Available Tools

### SPIDER (Stacking-based Protein druggability prediction)
* **Description**: Stacking-based ensemble learning framework for accurate prediction of druggable proteins
* **Source**: https://github.com/plenoi/SPIDER
* **Port**: User-specified (defaults to 8000)
* **Protocols**: REST API + MCP-like endpoints
* **Input**: A single protein sequence (sequence only, no header)
* **Output**: Druggability prediction for the sequence, expressed as a float in the range 0-1

### BLAST (Basic Local Alignment Search Tool)
* **Description**: Protein sequence similarity search against BLAST databases with automatic database management
* **Source**: NCBI BLAST+ suite
* **Port**: User-specified (defaults to 8001)
* **Protocols**: REST API + MCP-like endpoints
* **Input**: Protein sequence in FASTA format
* **Output**: 
  - **Table format** (default): Formatted text report with ranked hits
  - **JSON format**: Structured data with individual hit details including identity, e-value, bitscore, and organism information
* **Features**:
  - Automatic database download and updates
  - Manual database management via API
  - Support for multiple BLAST databases (nr, pdbaa, mito, etc.)
  - Configurable auto-update behavior

## ⚡ Quick Start

### Using Docker Compose (Recommended)
```bash
# First, build all tools with auto-versioning
./scripts/build.sh

# Set up BLAST database directory (required for BLAST service)
export BLAST_DB_PATH=./blast_databases
mkdir -p $BLAST_DB_PATH

# Then start all tools
docker-compose up -d

# Start specific tool
docker-compose up -d spider

# View logs
docker-compose logs -f spider

# Stop all tools
docker-compose down
```

### BLAST Service Setup (Required)
The BLAST service requires a volume mapping for database storage. You have several options:

**Option 1: Environment Variable (Recommended)**
```bash
export BLAST_DB_PATH=./blast_databases
mkdir -p $BLAST_DB_PATH
docker-compose up -d blast
```

**Option 2: Direct Volume Mapping**
```bash
docker run -e BLAST_DB_PATH=/blast_db -v ./blast_databases:/blast_db blast-api:latest
```

**Option 3: Use the Setup Script**
```bash
./scripts/setup_blast.sh
```

**Troubleshooting:**
- If you see "BLAST_DB_PATH environment variable is required", run the setup script
- If you see permission errors, ensure the directory is writable: `chmod 755 ./blast_databases`
- For testing, use the smaller "pdbaa" database: `curl -X POST "http://localhost:8001/api/v1/blastp/search" -H "Content-Type: application/json" -d '{"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG", "db_name": "pdbaa"}'`

### Individual Tool Usage
```bash
# Build and run SPIDER
cd tools/spider
docker build -t spider-api .
docker run -p 8000:8000 spider-api
```

## 🏷️ Versioning and Building

### Version Management
Each tool has its own version file (`tools/{tool}/VERSION`) for independent versioning:

```bash
# View current version
cat tools/spider/VERSION

# Update version manually
echo "0.1.0" > tools/spider/VERSION
```

### CI/CD Build Numbering
The build script automatically increments a build number (4th version component) for each build:

```bash
# First build creates: 0.1.0.1
./scripts/build.sh --service spider

# Second build creates: 0.1.0.2
./scripts/build.sh --service spider

# Build without incrementing (uses base version)
./scripts/build.sh --service spider --no-increment
```

Build numbers are stored in `tools/{tool}/BUILD` files and persist across builds.

### Building with Auto-Versioning
The build script automatically reads VERSION files and creates properly tagged images:

```bash
# Build all tools with versions from VERSION files
./scripts/build.sh

# List all available tools
./scripts/build.sh --list

# Build specific tool
./scripts/build.sh --service spider

# Build with specific version (overrides VERSION file)
./scripts/build.sh --service spider --version 1.3.0

# Build for specific platform
./scripts/build.sh --service spider --platform amd64
./scripts/build.sh --service spider --platform arm64
./scripts/build.sh --service spider --platform multi

# Build without cache
./scripts/build.sh --service spider --no-cache

# Build without incrementing build number
./scripts/build.sh --service spider --no-increment
```

### Tool Discovery
The build script automatically discovers all available tools by scanning the `tools/` directory for subdirectories containing `Dockerfile` files:

```bash
# List all available tools and their versions
./scripts/build.sh --list

# Example output:
# [INFO] Available tools:
#   blast: 1.0.0 (build 1)
#   spider: 0.1.0 (build 5)
```

### Image Tagging
Images are automatically tagged with versions:
- `spider-api:0.1.0.1` - Multi-arch image with build number
- `spider-api:0.1.0.2` - Next build number
- `spider-api:latest` - Latest version
- `spider-api:0.1.0.1-amd64` - AMD64 specific version with build number
- `spider-api:0.1.0.1-arm64` - ARM64 specific version with build number

### Manual Docker Compose Building
```bash
# Build with custom version
VERSION=0.1.0 docker-compose build spider

# Build all services
docker-compose build
```

## 🔄 Build and Run Workflow

### Two-Step Process
The system uses a **two-step workflow** for optimal CI/CD integration:

1. **Build Step** (using build script):
   ```bash
   # Build all tools with auto-versioning
   ./scripts/build.sh
   
   # Build specific tool
   ./scripts/build.sh --service spider
   ```
   - Creates versioned images: `spider-api:0.1.0.5`, `blast-api:1.0.0.2`
   - Tags latest: `spider-api:latest`, `blast-api:latest`

2. **Run Step** (using docker-compose):
   ```bash
   # Run all tools
   docker-compose up -d
   
   # Run specific tool
   docker-compose up -d spider
   ```
   - Uses `:latest` images created by build script
   - No building during runtime (faster startup)

### Why This Approach?
- **Separation of Concerns**: Build once, run many times
- **CI/CD Friendly**: Build in CI, deploy with docker-compose
- **Version Control**: Each build gets unique version number
- **Fast Deployment**: No build time during deployment
- **Rollback Ready**: Can easily switch to previous versions

## 🔌 API Usage

### REST API Endpoints

#### Health Check
```bash
curl http://localhost:8000/api/v1/spider/health
```

#### Get Tool Information
```bash
curl http://localhost:8000/api/v1/spider/info
```

#### Predict Druggability
```bash
curl -X POST "http://localhost:8000/api/v1/spider/predict?sequence=MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
```

### MCP-like Endpoints (AI Agent Friendly)

#### List Available Tools
```bash
curl http://localhost:8000/mcp/tools
```

#### Call Tool (Get Tool Info)
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_tool_info", "arguments": {}}'
```

#### Call Tool (Predict Druggability)
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "predict_druggability", 
    "arguments": {
      "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    }
  }'
```

### BLAST API Usage

#### Health Check
```bash
curl http://localhost:8000/api/v1/blastp/health
```

#### Get Tool Information
```bash
curl http://localhost:8000/api/v1/blastp/info
```

#### Search Protein Sequence (Table Format - Default)
```bash
curl -X POST "http://localhost:8000/api/v1/blastp/search" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
    "db_name": "nr",
    "evalue": 0.001,
    "max_target_seqs": 10,
    "output_format": "table"
  }'
```

#### Search Protein Sequence (JSON Format)
```bash
curl -X POST "http://localhost:8000/api/v1/blastp/search" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
    "db_name": "nr",
    "evalue": 0.001,
    "max_target_seqs": 10,
    "output_format": "json"
  }'
```

#### MCP-like BLAST Search (JSON Format)
```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "perform_blastp_search", 
    "arguments": {
      "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
      "db_name": "nr",
      "evalue": 0.001,
      "max_target_seqs": 10,
      "output_format": "json"
    }
  }'
```

### BLAST Database Management

The BLAST API includes advanced database management features for automatic updates and manual database downloads.

#### Auto-Update Feature
The BLAST service automatically downloads and updates databases on first use when the `AUTO_UPDATE` environment variable is set to `true`:

```bash
# Enable auto-update (default behavior)
docker run -e AUTO_UPDATE=true -e BLAST_DB_PATH=/blast_db -v ./blast_databases:/blast_db blast-api:latest

# Disable auto-update
docker run -e AUTO_UPDATE=false -e BLAST_DB_PATH=/blast_db -v ./blast_databases:/blast_db blast-api:latest
```

**How it works:**
- When a search is performed with a new database name, the service automatically downloads it
- Databases are cached and reused for subsequent searches
- Only downloads each database once per container instance

#### Manual Database Download (REST API)
```bash
# Download a specific database
curl -X POST "http://localhost:8001/api/v1/blastp/download_db" \
  -H "Content-Type: application/json" \
  -d '{"db": "mito"}'

# Response:
{
  "status": "success",
  "message": "Successfully downloaded database 'mito'",
  "db_name": "mito",
  "processing_time": 45.2,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Manual Database Download (MCP API)
```bash
# Download database via MCP endpoint
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "download_blast_database",
    "arguments": {
      "db": "mito"
    }
  }'
```

#### Available BLAST Databases
Common database names include:
- `nr` - Non-redundant protein sequences (large, ~200GB)
- `pdbaa` - PDB protein sequences (smaller, good for testing)
- `mito` - Mitochondrial protein sequences
- `swissprot` - Swiss-Prot protein sequences
- `refseq_protein` - RefSeq protein sequences

**Database Selection Tips:**
- Use `pdbaa` for quick testing and development
- Use `mito` for mitochondrial protein analysis
- Use `nr` for comprehensive searches (requires significant disk space)
- Check available databases at: https://ftp.ncbi.nlm.nih.gov/blast/db/

## 📊 Output Formats

### BLAST Output Format Comparison

The BLAST API supports two output formats controlled by the `output_format` parameter:

#### Table Format (Default: `output_format: "table"`)
Returns a formatted text report suitable for human reading:
```json
{
  "status": "success",
  "result": {
    "report": "rank\tid\tidentity%\talign_len\te-value\tbitscore\torganism\n1\tsp|P12345|TEST1_HUMAN\t95.2\t156\t2.3e-45\t180.5\tHomo sapiens\n..."
  }
}
```

#### JSON Format (`output_format: "json"`)
Returns structured data suitable for programmatic access:
```json
{
  "status": "success",
  "result": {
    "hits": [
      {
        "rank": 1,
        "query_id": "sequence",
        "subject_id": "sp|P12345|TEST1_HUMAN",
        "percent_identity": 95.2,
        "alignment_length": 156,
        "evalue": 2.3e-45,
        "bitscore": 180.5,
        "organism": "Homo sapiens"
      }
    ],
    "total_hits": 10,
    "query_sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
  }
}
```

**Use Cases:**
- **Table format**: Human-readable reports, display in terminals, simple text processing
- **JSON format**: Programmatic integration, data analysis, automated workflows, AI agent processing

## 🧪 Testing

### Run REST API Tests
```bash
cd tools/spider
python test_rest_api.py
```

### Run MCP Endpoint Tests
```bash
cd tools/spider
python test_mcp_endpoints.py
```

### Run Both Test Suites
```bash
cd tools/spider
python test_rest_api.py && python test_mcp_endpoints.py
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Development

### Adding a New Tool
1. Create a new directory in `tools/`
2. Implement the API wrapper following the SPIDER pattern
3. Add Dockerfile and requirements
4. Create test suites for both REST and MCP endpoints
5. Update docker-compose.yml
6. Add documentation

### API Standards
All tools follow these conventions:

#### REST API
- Health check: `GET /api/v1/{tool}/health`
- Tool info: `GET /api/v1/{tool}/info`
- Prediction: `POST /api/v1/{tool}/predict`
- Standardized error responses
- Input validation

#### MCP-like Endpoints
- List tools: `GET /mcp/tools`
- Call tool: `POST /mcp/call`
- JSON Schema validation
- Consistent response format

## 🐳 Docker Details

### Container Architecture
- **Base Image**: Python 3.12-slim
- **Package Manager**: micromamba (conda alternative)
- **API Environment**: Python 3.12 with FastAPI
- **Tool Environment**: Python 3.9 (for SPIDER compatibility)
- **Single Port**: 8000 (both REST and MCP-like endpoints)

### Health Checks
- Automatic health monitoring
- Graceful shutdown handling
- Process monitoring and restart

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
