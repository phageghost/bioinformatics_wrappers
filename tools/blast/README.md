# BLAST API Wrapper

A containerized REST and MCP API for NCBI BLASTp protein sequence search, designed for agentic workflows and easy integration.

---

## 🚀 Overview

This service wraps the BLAST+ `blastp` tool with a FastAPI-based REST API and MCP-like endpoints for programmatic and agentic use. It supports custom database selection, output formats (table or JSON), and robust error handling.

---

## 🏗️ Build Instructions

### 1. Docker Build (Recommended)

```bash
# From the project root
cd tools/blast
# Build the Docker image
DOCKER_BUILDKIT=1 docker build -t blast-api .
```

### 2. Local (Dev) Environment

- Requires Python 3.12+
- Install dependencies from `environment-api.yml` and `environment-blast.yml` (preferably using micromamba or conda)

---

## 🚦 Deployment

### 1. Docker Compose (Recommended)

Ensure you have a BLAST database directory on your host (e.g., `./blast_databases`).

```bash
# From the project root
export BLAST_DB_PATH=./blast_databases
mkdir -p $BLAST_DB_PATH
# Start the BLAST service
BLAST_DB_PATH=$BLAST_DB_PATH docker-compose up -d blast
```

- **Port mapping:** Host port 8001 → container port 8000 (default: `8001:8000`)
- **Volume binding:** Host directory (e.g., `./blast_databases`) → `/blast_db` in the container

#### Example docker-compose.yml snippet:
```yaml
blast:
  image: blast-api:latest
  container_name: blast-api
  ports:
    - "8001:8000"
  volumes:
    - ./blast_databases:/blast_db
  restart: unless-stopped
```

### 2. Docker Run (Manual)

```bash
docker run -p 8001:8000 -v /absolute/path/to/blast_databases:/blast_db blast-api:latest
```

---

## 🔌 REST API Usage

### Endpoints
- `GET /api/v1/blastp/health` — Health check
- `GET /api/v1/blastp/info` — Tool info
- `POST /api/v1/blastp/search` — Run a BLASTp search
- `POST /api/v1/blastp/download_db` — Download and update BLAST database

### Search Parameters
- `sequence` (str, required): Protein sequence (FASTA or raw)
- `db_name` (str, optional): BLAST database (default: `nr`)
- `evalue` (float, optional): E-value threshold (default: `0.001`)
- `max_target_seqs` (int, optional): Max hits (default: `20`)
- `output_format` (str, optional): `table` (default) or `json`

### Example: Table Output (default)
```bash
curl -X POST "http://localhost:8001/api/v1/blastp/search" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
    "db_name": "pdbaa",
    "output_format": "table"
  }'
```

### Example: JSON Output
```bash
curl -X POST "http://localhost:8001/api/v1/blastp/search" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
    "db_name": "pdbaa",
    "output_format": "json"
  }'
```

### Example: Health Check
```bash
curl http://localhost:8001/api/v1/blastp/health
```

### Example: Download Database
```bash
curl -X POST "http://localhost:8001/api/v1/blastp/download_db" \
  -H "Content-Type: application/json" \
  -d '{"db": "mito"}'
```

---

## 🤖 MCP API Usage

### Tool Discovery
```bash
curl http://localhost:8001/mcp/tools
```

### Example: Perform BLASTp Search via MCP
```bash
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "perform_blastp_search",
    "arguments": {
      "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
      "db_name": "pdbaa",
      "output_format": "json"
    }
  }'
```

### Example: Download Database via MCP
```bash
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "download_blast_database",
    "arguments": {
      "db": "mito"
    }
  }'
```

---

## 🗄️ Database Management

### Auto-Update Feature
The BLAST service automatically downloads and updates databases on first use when the `AUTO_UPDATE` environment variable is set to `true` (default behavior).

**How it works:**
- When a search is performed with a new database name, the service automatically downloads it
- Databases are cached and reused for subsequent searches
- Only downloads each database once per container instance

**Configuration:**
```bash
# Enable auto-update (default)
docker run -e AUTO_UPDATE=true -e BLAST_DB_PATH=/blast_db -v ./blast_databases:/blast_db blast-api:latest

# Disable auto-update
docker run -e AUTO_UPDATE=false -e BLAST_DB_PATH=/blast_db -v ./blast_databases:/blast_db blast-api:latest
```

### Manual Database Management
You can manually download and update databases using the API endpoints:

**REST API:**
```bash
# Download a specific database
curl -X POST "http://localhost:8001/api/v1/blastp/download_db" \
  -H "Content-Type: application/json" \
  -d '{"db": "mito"}'
```

**MCP API:**
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

### Available Databases
Common BLAST database names:
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

---

## 🛠️ Troubleshooting

- **Startup fails with missing `/blast_db`:**
  - Ensure you have a volume mapping from a host directory to `/blast_db` in the container.
  - Example: `-v /host/path:/blast_db` (docker run) or `./blast_databases:/blast_db` (docker-compose)
- **Permission errors:**
  - Make sure the host directory is writable by the container user.
  - Example fix: `chmod 755 ./blast_databases`
- **Database not found:**
  - Use a smaller test database like `pdbaa` for quick tests.
  - The default is `nr`, which is large and may require significant disk space and download time.
- **Health check fails:**
  - Check logs for configuration errors or permission issues.

---

## 📚 More Information

- See the main project [README.md](../../README.md) for advanced usage, development, and CI/CD details.
- For questions or issues, open an issue on the project repository.

--- 