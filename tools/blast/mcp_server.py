import os
import logging

from fastmcp import FastMCP

try:
    from .api.blast_service import BLASTpService
except ImportError:
    from api.blast_service import BLASTpService

VERSION = open("VERSION", "r", encoding="utf-8").read().strip()
DEFAULT_BLAST_DB = os.getenv("DEFAULT_BLAST_DB", "swissprot")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize BLASTp service
try:
    blastp_service = BLASTpService()
except ValueError as e:
    print("=" * 80)
    print("❌ BLAST API Configuration Error")
    print("=" * 80)
    print(str(e))
    print("=" * 80)
    print("The BLAST API cannot start without proper database configuration.")
    print("Please fix the configuration issue and restart the service.")
    print("=" * 80)
    import sys

    sys.exit(1)

mcp = FastMCP(
    name="blastp",
    instructions="This server returns the results of BLASTp searches for a provided protein \
sequence against a specified NCBI BLAST database.",
)

@mcp.tool
def blastp_search_flexible_db_tabular(
    sequence: str,
    database: str = "swissprot",
    evalue: float = 1e-3,
    max_target_seqs: int = 20,
):
    """
    Search a protein sequence against a specified NCBI BLAST database.
    
    Args:
        sequence: Protein sequence to search (required)
        database: BLAST database name (default: swissprot, options: nr, pdbaa, mito, swissprot)
        evalue: E-value threshold for significance (default: 0.001)
        max_target_seqs: Maximum number of target sequences to return (default: 20)
    
    Returns:
        A table of BLAST search results with hits and alignment information
        
    Example:
        Search for a protein sequence against Swiss-Prot database:
        blastp_search(
            sequence="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
            database="swissprot",
            evalue=0.001,
            max_target_seqs=10
        )
    """
    logger.info(f"Running BLASTp search for sequence: {sequence} against database: {database} with evalue: {evalue} and max_target_seqs: {max_target_seqs}")
    search_results = blastp_service.run_blastp_search_from_sequence(
        sequence=sequence,
        database=database,
        evalue=evalue,
        max_target_seqs=max_target_seqs,
    )
    logger.info(f"BLASTp search results: {search_results}")
    return search_results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="BLASTp MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to (default: 8001)")
    
    args = parser.parse_args()
    
    logger.info(f"Starting FastMCP HTTP API server on {args.host}:{args.port}")
    # Use streamable-http transport for LangFlow compatibility
    mcp.run(transport='streamable-http', host=args.host, port=args.port)

