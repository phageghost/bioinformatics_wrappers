"""
blast_service.py

This module provides the BLASTpService class, which offers methods for running BLASTp protein
sequence searches using the BLAST+ command-line tools within a micromamba-managed environment. It
handles database path resolution, output management, and validation of input FASTA protein files.
output management, and validation of input FASTA protein files. The service is designed to be used
as part of a REST API for sequence search, supporting configuration via environment variables and
robust logging for monitoring and debugging.

Classes:
    BLASTpService: Service class for running BLASTp searches with configurable database and
    environment.

Constants:
    DEFAULT_EVALUE: Default e-value threshold for BLASTp searches.
    DEFAULT_MAX_TARGET_SEQS: Default maximum number of target sequences to return.
    DEFAULT_OUTFMT: Default BLASTp output format string.
    DEFAULT_HEADER: Default header for formatted BLASTp results.
    DEFAULT_BLAST_DB_NAME: Default BLAST database name.

Environment Variables:
    BLAST_DB_PATH: Path to the BLAST database directory.
    BLAST_MM_ENV: Name of the micromamba environment to use for running BLAST commands.
"""

import os
import subprocess
from pathlib import Path
from typing import Tuple, Union
import logging

try:
    # Try relative import first (for when imported as part of a package)
    from .models import BLASTpResult, BLASTpJSONResult, BLASTpHit
except ImportError:
    # Fall back to absolute import (for when run as script or from local directory)
    from models import BLASTpResult, BLASTpJSONResult, BLASTpHit

DEFAULT_EVALUE = 1e-3
DEFAULT_MAX_TARGET_SEQS = 20
DEFAULT_OUTFMT = "6 qseqid sseqid pident length evalue bitscore sscinames"
DEFAULT_HEADER = "rank\tid\tidentity%\talign_len\te-value\tbitscore\torganism"
DEFAULT_BLAST_DB_NAME = "nr"


class BLASTpService:
    """Service class for running BLASTp searches"""

    def __init__(self, db_path: Path | str = None, mm_env: str = None):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing BLASTpService")

        db_path_env = os.environ.get("BLAST_DB_PATH")
        if not db_path and not db_path_env:
            self.logger.error("db_path not specified andBLAST_DB_PATH environment variable not set, complaining to user ...")
            raise ValueError(
                "BLAST_DB_PATH environment variable must be set for database storage.\n\n"
                "To fix this, you must provide a volume mapping for BLAST databases:\n\n"
                "Option 1 - Using docker run:\n"
                "  docker run -e BLAST_DB_PATH=/blast_db -v /host/path:/blast_db blast-api\n\n"
                "Option 2 - Using docker-compose (set BLAST_DB_PATH environment variable):\n"
                "  BLAST_DB_PATH=/path/to/blast/databases docker-compose up blast\n\n"
                "Option 3 - Using docker-compose with volume mapping:\n"
                "  # In docker-compose.yml:\n"
                "  blast:\n"
                "    environment:\n"
                "      - BLAST_DB_PATH=/blast_db\n"
                "    volumes:\n"
                "      - ./blast_databases:/blast_db\n\n"
                "The BLAST_DB_PATH must point to a writable directory where BLAST databases will \
be stored."
            )

        self.db_path = Path(db_path or db_path_env)
        self.logger.info(f"db_path: {self.db_path}")

        # Validate that the database path is writable
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            # Test write access
            test_file = self.db_path / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
        except (OSError, IOError) as e:
            self.logger.error(f"db path '{self.db_path}' is not writable: {str(e)}\n\n")
            raise ValueError(
                f"BLAST_DB_PATH '{self.db_path}' is not writable: {str(e)}\n\n"
                "Please ensure the directory exists and has proper write permissions.\n"
                "If using Docker, make sure the volume mapping is correct and the host directory \
is writable."
            ) from e

        self.output_path = Path("blast_output")
        self.logger.info("output_path: %s", self.output_path)
        self.output_path.mkdir(exist_ok=True)
        self.checked_dbs = set()
        self.mm_env = mm_env or os.environ.get("BLAST_MM_ENV", "blast")
        self.logger.info("mm_env: %s", self.mm_env)
        auto_update_env = os.environ.get("AUTO_UPDATE")
        if auto_update_env.lower() == "true":
            self.logger.info("AUTO_UPDATE is true, will auto update databases")
            self.auto_update = True
        else:
            self.logger.info("AUTO_UPDATE is not true, will not auto update databases")
            self.auto_update = False
 
    def _prefix_mm_env(self, cmd: list[str]) -> list[str]:
        return ["micromamba", "run", "-n", self.mm_env] + cmd

    def validate_fasta_protein_file(self, file_path: Path | str) -> bool:
        """Validate that the file is a valid FASTA protein file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                return False

            # Check if first line starts with '>'
            if not lines[0].strip().startswith(">"):
                return False

            # Basic FASTA format validation
            for _, line in enumerate(lines):
                line = line.strip()
                if line.startswith(">"):
                    # Header line - should not be empty
                    if len(line) <= 1:
                        return False
                else:
                    # Sequence line - should contain valid amino acid characters
                    if line and not all(
                        c in "ACDEFGHIKLMNPQRSTVWY" for c in line.upper()
                    ):
                        return False

            return True
        except (OSError, IOError, UnicodeDecodeError) as e:
            self.logger.error("Error validating FASTA file: %s", e)
            return False

    def download_db(self, db_name: str):
        """Download and update BLAST database"""
        if not self.auto_update:
            self.logger.info("AUTO_UPDATE is false, will not auto update databases")
            return

        cmd = self._prefix_mm_env(
            ["update_blastdb.pl", "--passive", "--decompress", db_name]
        )
        self.logger.info("Running update_blastdb.pl with command: %s", cmd)

        try:
            result = subprocess.run(
                cmd, cwd=self.db_path, check=True, capture_output=True, text=True
            )
            self.logger.info("update_blastdb.pl completed successfully")
            self.logger.debug("update_blastdb.pl stdout: %s", result.stdout)
        except subprocess.CalledProcessError as e:
            error_msg = (
                f"Failed to download BLAST database '{db_name}': {e}\n\n"
                f"Command: {' '.join(cmd)}\n"
                f"Working directory: {self.db_path}\n"
                f"Exit code: {e.returncode}\n"
                f"stdout: {e.stdout}\n"
                f"stderr: {e.stderr}\n\n"
                "Common solutions:\n"
                "1. Check internet connectivity\n"
                "2. Ensure BLAST_DB_PATH is writable\n"
                "3. Try a different database (e.g., 'pdbaa' instead of 'nr')\n"
                "4. Check available disk space\n"
                "5. Verify the database name is correct"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def run_blastp_search(
        self,
        fasta_fpath: Path | str,
        db_name: str = DEFAULT_BLAST_DB_NAME,
        evalue: float = DEFAULT_EVALUE,
        max_target_seqs: int = DEFAULT_MAX_TARGET_SEQS,
        outfmt: str = DEFAULT_OUTFMT,
        output_format: str = "table",
        query_sequence: str = "",
    ) -> Tuple[bool, str, Union[BLASTpResult, BLASTpJSONResult]]:
        """
        Run a BLASTp search using the provided protein FASTA file against the specified BLAST
              database.

        Args:
            fasta_fpath (Path | str): Path to the input protein FASTA file.
            db_name (str, optional): Name of the BLAST database to search against. Defaults to
                DEFAULT_BLAST_DB_NAME.
            evalue (float, optional): E-value threshold for reporting matches. Defaults to
                DEFAULT_EVALUE.
            max_target_seqs (int, optional): Maximum number of aligned sequences to keep. Defaults
                to DEFAULT_MAX_TARGET_SEQS.
            outfmt (str, optional): Output format for BLASTp results. Defaults to DEFAULT_OUTFMT.
            output_format (str, optional): Response format ("table" or "json"). Defaults to "table".
            query_sequence (str, optional): Original query sequence for JSON output. Defaults to "".

        Returns:
            Tuple[bool, str, Union[BLASTpResult, BLASTpJSONResult]]:
                - Success status (bool)
                - Message (str)
                - BLASTp result (BLASTpResult or BLASTpJSONResult)
        """
        output_fpath = self.output_path.joinpath("blastp_output.txt")
        db_fpath = self.db_path.joinpath(db_name)

        if not self.validate_fasta_protein_file(fasta_fpath):
            return False, "Invalid or missing FASTA file", []

        self.logger.info("New BLASTp search requested")
        self.logger.info("Validated protein FASTA file: %s", fasta_fpath)
        self.logger.info("DB name: %s", db_name)
        self.logger.info("E-value: %s", evalue)
        self.logger.info("Output path: %s", output_fpath)
        self.logger.info("DB path: %s", db_fpath)
        self.logger.info("Output format: %s", output_format)

        if db_name not in self.checked_dbs:
            self.logger.info("New db %s requested, running update_blastdb.pl", db_name)
            self.download_db(db_name)
            self.checked_dbs.add(db_name)

        # Build command
        cmd = self._prefix_mm_env(
            [
                "blastp",
                "-query",
                str(fasta_fpath),
                "-db",
                str(db_fpath),
                "-evalue",
                str(evalue),
                "-outfmt",
                outfmt,
                "-max_target_seqs",
                str(max_target_seqs),
                "-out",
                str(output_fpath),
            ]
        )

        self.logger.info("Running BLASTp search with command: %s", cmd)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
            )
            self.logger.info("BLASTp response: %s", result)

            if result.returncode != 0:
                error_msg = f"BLASTp execution failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg, []

            # Read results
            if not output_fpath.exists():
                error_msg = "BLASTp did not generate output file"
                self.logger.error(error_msg)
                return False, error_msg, []

            self.logger.info(
                "BLASTp output file content: %s",
                output_fpath.read_text(encoding="utf-8"),
            )

            # Parse results based on output format
            if output_format.lower() == "json":
                results = self._parse_blastp_json(output_fpath, query_sequence)
            else:
                results = self._parse_blastp_table(output_fpath)

            # Clean up
            if output_fpath.exists():
                output_fpath.unlink()

            return True, "Search completed successfully", results

        except subprocess.TimeoutExpired:
            error_msg = "BLASTp search timed out"
            self.logger.error(error_msg)
            return False, error_msg, []
        except (OSError, IOError, ValueError, RuntimeError) as e:
            error_msg = f"Error running BLASTp: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, []

    def _parse_blastp_table(
        self, output_file: Path, header: str = DEFAULT_HEADER
    ) -> BLASTpResult:
        try:
            output_lines = output_file.read_text().strip().split("\n")
            report_lines = [header]
            for line_idx, line in enumerate(output_lines):
                report_lines.append(f"{line_idx+1}\t{line}")

            result = BLASTpResult(
                report="\n".join(report_lines),
            )
            return result

        except (ValueError, IndexError, OSError, IOError) as e:
            self.logger.error("Error parsing BLASTp results: %s", e)
            return []

    def _parse_blastp_json(
        self, output_file: Path, query_sequence: str
    ) -> BLASTpJSONResult:
        """Parse BLASTp results into structured JSON format"""
        try:
            output_lines = output_file.read_text().strip().split("\n")
            hits = []

            for line_idx, line in enumerate(output_lines):
                if not line.strip():
                    continue

                # Parse tab-separated values
                # Format: qseqid sseqid pident length evalue bitscore sscinames
                parts = line.strip().split("\t")

                if len(parts) >= 6:
                    try:
                        hit = BLASTpHit(
                            rank=line_idx + 1,
                            query_id=parts[0],
                            subject_id=parts[1],
                            percent_identity=float(parts[2]),
                            alignment_length=int(parts[3]),
                            evalue=float(parts[4]),
                            bitscore=float(parts[5]),
                            organism=parts[6] if len(parts) > 6 else None,
                        )
                        hits.append(hit)
                    except (ValueError, IndexError) as e:
                        self.logger.warning(
                            "Skipping malformed line %d: %s", line_idx + 1, e
                        )
                        continue

            result = BLASTpJSONResult(
                hits=hits, total_hits=len(hits), query_sequence=query_sequence
            )
            return result

        except (ValueError, IndexError, OSError, IOError) as e:
            self.logger.error("Error parsing BLASTp JSON results: %s", e)
            return BLASTpJSONResult(
                hits=[], total_hits=0, query_sequence=query_sequence
            )

    def get_blastp_version(self) -> str:
        """Get the version of BLASTp"""
        cmd = self._prefix_mm_env(["blastp", "-version"])
        output = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output.stdout.strip()

    def get_tool_info(self) -> dict:
        """Get information about the BLASTp tool"""
        return {
            "name": "BLASTp",
            "version": self.get_blastp_version(),
            "description": "BLASTp is a protein-protein sequence alignment tool that uses a \
database of protein sequences to search for similar sequences in a query protein sequence.",
            "input_format": "FASTA",
        }
