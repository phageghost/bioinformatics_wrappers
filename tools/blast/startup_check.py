#!/usr/bin/env python3
"""
BLAST API Startup Validation

This script validates the BLAST API configuration before starting the service.
It checks for proper volume mapping and database path configuration.
"""

import os
import sys
from pathlib import Path


def validate_blast_configuration():
    """Validate BLAST configuration before startup"""
    
    print("🔍 Validating BLAST API Configuration...")
    
    # Check if BLAST_DB_PATH is set
    blast_db_path = os.environ.get("BLAST_DB_PATH")
    if not blast_db_path:
        print("❌ BLAST_DB_PATH environment variable is not set!")
        print("\n" + "=" * 60)
        print("🚨 CONFIGURATION ERROR")
        print("=" * 60)
        print("The BLAST API requires a volume mapping for database storage.")
        print("\nTo fix this, you must provide a volume mapping:")
        print("\nOption 1 - Using docker run:")
        print("  docker run -e BLAST_DB_PATH=/blast_db -v /host/path:/blast_db blast-api")
        print("\nOption 2 - Using docker-compose (set BLAST_DB_PATH environment variable):")
        print("  BLAST_DB_PATH=/path/to/blast/databases docker-compose up blast")
        print("\nOption 3 - Using docker-compose with volume mapping:")
        print("  # In docker-compose.yml:")
        print("  blast:")
        print("    environment:")
        print("      - BLAST_DB_PATH=/blast_db")
        print("    volumes:")
        print("      - ./blast_databases:/blast_db")
        print("\nThe BLAST_DB_PATH must point to a writable directory.")
        print("=" * 60)
        return False
    
    # Check if the path exists and is writable
    db_path = Path(blast_db_path)
    try:
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Test write access
        test_file = db_path / ".startup_test"
        test_file.write_text("startup validation")
        test_file.unlink()
        
        print(f"✅ BLAST_DB_PATH is valid: {blast_db_path}")
        print(f"✅ Database directory is writable")
        
    except (OSError, IOError) as e:
        print(f"❌ BLAST_DB_PATH '{blast_db_path}' is not writable: {e}")
        print("\n" + "=" * 60)
        print("🚨 PERMISSION ERROR")
        print("=" * 60)
        print("The BLAST database directory is not writable.")
        print("\nPlease ensure:")
        print("1. The directory exists and has proper write permissions")
        print("2. If using Docker, the volume mapping is correct")
        print("3. The host directory has appropriate permissions")
        print("\nExample fix:")
        print("  mkdir -p ./blast_databases")
        print("  chmod 755 ./blast_databases")
        print("  export BLAST_DB_PATH=./blast_databases")
        print("=" * 60)
        return False
    
    # Check available disk space (optional but helpful)
    try:
        import shutil
        total, used, free = shutil.disk_usage(db_path)
        free_gb = free // (1024**3)
        
        if free_gb < 1:
            print(f"⚠️  Warning: Only {free_gb}GB free space available")
            print("   BLAST databases can be large (several GB)")
        else:
            print(f"✅ Sufficient disk space: {free_gb}GB available")
            
    except ImportError:
        # shutil.disk_usage not available in older Python versions
        pass
    
    print("✅ BLAST API configuration validation passed!")
    return True


if __name__ == "__main__":
    if not validate_blast_configuration():
        sys.exit(1) 