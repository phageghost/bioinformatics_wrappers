import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Tuple
import logging

from api.models import PredictionResult


# Add SPIDER tool to Python path
SPIDER_HOME = os.getenv("SPIDER_HOME", "/app/spider_tool")
sys.path.insert(0, SPIDER_HOME)


class SpiderService:
    """Service class for running SPIDER predictions"""

    def __init__(self):
        self.spider_home = Path(SPIDER_HOME)
        self.input_path = self.spider_home / "input"
        self.output_path = self.spider_home / "output"
        self.model_path = self.spider_home / "model"

        # Ensure directories exist
        self.input_path.mkdir(exist_ok=True)
        self.output_path.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def validate_fasta_file(self, file_path: Path) -> bool:
        """Validate that the file is a valid FASTA file"""
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
        except Exception as e:
            self.logger.error("Error validating FASTA file: %s", e)
            return False

    def run_spider_prediction(
        self, fasta_file_path: Path
    ) -> Tuple[bool, str, PredictionResult]:
        """Run SPIDER prediction on the provided FASTA file"""
        try:
            # Copy input file to SPIDER input directory
            input_fpath = self.input_path.joinpath("seq.fasta")
            shutil.copy2(fasta_file_path, input_fpath)
            
            # Debug: Check what was written to the file
            with open(input_fpath, "r", encoding="utf-8") as f:
                file_content = f.read()
                self.logger.info("Input file path: %s", input_fpath)
                self.logger.info("File content written to SPIDER input: %s", file_content)
                self.logger.info("File size: %d bytes", len(file_content))

            # Change to SPIDER directory
            original_cwd = os.getcwd()
            os.chdir(self.spider_home)

            # Run SPIDER
            self.logger.info("Starting SPIDER prediction...")
            self.logger.info("SPIDER home: %s", self.spider_home)
            self.logger.info("SPIDER input path: %s", self.input_path)
            self.logger.info("SPIDER output path: %s", self.output_path)
            self.logger.info("SPIDER model path: %s", self.model_path)
            self.logger.info("SPIDER input file: %s", input_fpath)
            result = subprocess.run(
                ["python", "spider.py"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
            )

            # Return to original directory
            os.chdir(original_cwd)

            if result.returncode != 0:
                error_msg = f"SPIDER execution failed: {result.stderr}"
                self.logger.error(error_msg)
                return False, error_msg, []

            # Read results
            output_fpath = self.output_path.joinpath("predict_result.csv")
            if not output_fpath.exists():
                error_msg = "SPIDER did not generate output file"
                self.logger.error(error_msg)
                return False, error_msg, []

            self.logger.info("SPIDER output file: %s", output_fpath)
            self.logger.info("SPIDER output file content: %s", output_fpath.read_text())
            # Parse results
            results = self._parse_spider_results(output_fpath)

            # Clean up
            if input_fpath.exists():
                input_fpath.unlink()
            if output_fpath.exists():
                output_fpath.unlink()

            return True, "Prediction completed successfully", results

        except subprocess.TimeoutExpired:
            error_msg = "SPIDER prediction timed out"
            self.logger.error(error_msg)
            return False, error_msg, []
        except Exception as e:
            error_msg = f"Error running SPIDER: {str(e)}, {e.__traceback__}"
            self.logger.error(error_msg)
            return False, error_msg, []

    def _parse_spider_results(self, output_file: Path) -> PredictionResult:
        """Parse SPIDER output CSV file into structured results"""
        try:
            output = output_file.read_text().strip()
            output = output.split('\n')
            if len(output) > 1:
                raise ValueError("SPIDER output contains multiple lines")
            
            splat = output[0].split(',')
            result = PredictionResult(
                    label=splat[1],
                    probability=float(splat[2]),
            )
            return result
        
        except Exception as e:
            self.logger.error("Error parsing SPIDER results: %s", e)
            return []

    def get_tool_info(self) -> dict:
        """Get information about the SPIDER tool"""
        return {
            "name": "SPIDER",
            "version": "1.0",
            "description": "Stacking-based ensemble learning framework for accurate prediction of druggable proteins",
            "input_format": "FASTA",
            "output_format": "CSV",
            "home_directory": str(self.spider_home),
        }
