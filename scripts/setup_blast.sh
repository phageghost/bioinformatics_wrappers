#!/bin/bash
# BLAST Setup Script
# This script helps set up the BLAST service with proper database configuration

set -e

echo "🚀 BLAST Service Setup"
echo "======================"

# Check if BLAST_DB_PATH is already set
if [ -n "$BLAST_DB_PATH" ]; then
    echo "✅ BLAST_DB_PATH is already set to: $BLAST_DB_PATH"
else
    echo "📁 Setting up BLAST database directory..."
    
    # Default to ./blast_databases in current directory
    DEFAULT_DB_PATH="./blast_databases"
    
    echo "Creating BLAST database directory: $DEFAULT_DB_PATH"
    mkdir -p "$DEFAULT_DB_PATH"
    
    # Set the environment variable
    export BLAST_DB_PATH="$DEFAULT_DB_PATH"
    
    echo "✅ BLAST_DB_PATH set to: $BLAST_DB_PATH"
    echo ""
    echo "💡 To make this permanent, add to your shell profile:"
    echo "   export BLAST_DB_PATH=\"$DEFAULT_DB_PATH\""
fi

# Check if the directory is writable
if [ -w "$BLAST_DB_PATH" ]; then
    echo "✅ Database directory is writable"
else
    echo "❌ Database directory is not writable: $BLAST_DB_PATH"
    echo "Please check permissions and try again."
    exit 1
fi

echo ""
echo "🔧 Next steps:"
echo "1. Build the BLAST image:"
echo "   ./scripts/build.sh --service blast"
echo ""
echo "2. Start the BLAST service:"
echo "   docker-compose up -d blast"
echo ""
echo "3. Test the service:"
echo "   curl http://localhost:8001/api/v1/blastp/health"
echo ""
echo "📚 For more information, see the README.md file" 