'''
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
'''

import os
import subprocess
from pathlib import Path
from typing import Tuple
import logging

try:
    # Try relative import first (for when imported as part of a package)
    from .models import BLASTpResult
except ImportError:
    # Fall back to absolute import (for when run as script or from local directory)
    from models import BLASTpResult

DEFAULT_EVALUE = 1e-3
DEFAULT_MAX_TARGET_SEQS = 20
DEFAULT_OUTFMT = "6 qseqid sseqid pident length evalue bitscore sscinames"
DEFAULT_HEADER = "rank\tid\tidentity%\talign_len\te-value\tbitscore\torganism"
DEFAULT_BLAST_DB_NAME = "nr"


class BLASTpService:
    """Service class for running BLASTp searches"""

    def __init__(self, db_path: Path | str = None, mm_env: str = None):
        db_path_env = os.environ.get("BLAST_DB_PATH")
        if not db_path and not db_path_env:
            raise ValueError(
                "BLAST_DB_PATH environment variable must be set for database storage. "
                "Example: docker run -e BLAST_DB_PATH=/blast_db -v /host/path:/blast_db your-image"
            )
        self.db_path = Path(db_path or db_path_env)
        self.output_path = Path("blast_output")
        self.output_path.mkdir(exist_ok=True)
        self.checked_dbs = set()
        self.mm_env = mm_env or os.environ.get("BLAST_MM_ENV", "blast")

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

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
        """Download the requested BLAST database"""
        self.logger.info(
            "Downloading BLAST database (if not already downloaded): %s", db_name
        )
        self.db_path.mkdir(exist_ok=True)

        self.logger.info("Moving to BLAST database path: %s", self.db_path)
        cwd = os.getcwd()
        os.chdir(self.db_path)

        cmd = self._prefix_mm_env(
            ["update_blastdb.pl", "--decompress", "--verbose", str(db_name)]
        )
        self.logger.info("Running update_blastdb.pl with command: %s", cmd)
        output = subprocess.run(cmd, check=True, capture_output=True, text=True)
        self.logger.info("Output: %s", output)

        os.chdir(cwd)

    def run_blastp_search(
        self,
        fasta_fpath: Path | str,
        db_name: str = DEFAULT_BLAST_DB_NAME,
        evalue: float = DEFAULT_EVALUE,
        max_target_seqs: int = DEFAULT_MAX_TARGET_SEQS,
        outfmt: str = DEFAULT_OUTFMT,
    ) -> Tuple[bool, str, BLASTpResult]:
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

        Returns:
            Tuple[bool, str, BLASTpResult]:
                - Success status (bool)
                - Message (str)
                - BLASTp result (BLASTpResult)
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
            # Parse results
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
