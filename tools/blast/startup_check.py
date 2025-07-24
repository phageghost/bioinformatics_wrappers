#!/usr/bin/env python3
"""
BLAST API Startup Validation

This script validates the BLAST API configuration before starting the service.
It checks for proper volume mapping and database path configuration.
"""

import sys
from pathlib import Path

BLAST_DB_PATH = "/blast_db"

def validate_blast_configuration():
    """Validate BLAST configuration before startup"""
    print("🔍 Validating BLAST API Configuration...")
    db_path = Path(BLAST_DB_PATH)

    # Check if the path exists
    if not db_path.exists():
        print(f"❌ Required database directory {BLAST_DB_PATH} does not exist!")
        print("\n" + "=" * 60)
        print("🚨 CONFIGURATION ERROR")
        print("=" * 60)
        print(f"The BLAST API requires a volume mapping to {BLAST_DB_PATH} inside the container.")
        print("\nTo fix this, you must provide a volume mapping:")
        print("\nOption 1 - Using docker run:")
        print(f"  docker run -v /host/path:{BLAST_DB_PATH} blast-api")
        print("\nOption 2 - Using docker-compose:")
        print("  # In docker-compose.yml:")
        print("  blast:")
        print(f"    volumes:")
        print(f"      - ./blast_databases:{BLAST_DB_PATH}")
        print("\nThe directory must exist on the host before starting the container.")
        print("=" * 60)
        return False

    # Check if the path is writable
    try:
        test_file = db_path / ".startup_test"
        test_file.write_text("startup validation")
        test_file.unlink()
        print(f"✅ {BLAST_DB_PATH} exists and is writable.")
    except (OSError, IOError) as e:
        print(f"❌ {BLAST_DB_PATH} exists but is not writable: {e}")
        print("\n" + "=" * 60)
        print("🚨 PERMISSION ERROR")
        print("=" * 60)
        print(f"The BLAST database directory {BLAST_DB_PATH} is not writable.")
        print("\nPlease ensure:")
        print("1. The directory exists and has proper write permissions on the host.")
        print("2. If using Docker, the volume mapping is correct.")
        print("3. The host directory has appropriate permissions.")
        print("\nExample fix:")
        print("  mkdir -p ./blast_databases")
        print("  chmod 755 ./blast_databases")
        print("=" * 60)
        return False

    print("✅ BLAST API configuration validation passed!")
    return True

if __name__ == "__main__":
    if not validate_blast_configuration():
        sys.exit(1) 