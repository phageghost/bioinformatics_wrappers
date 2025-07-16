#!/bin/bash

# Build all bioinformatics tool Docker images
# Usage: ./scripts/build_all.sh [tool_name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to build a specific tool
build_tool() {
    local tool_name=$1
    local tool_path="$PROJECT_ROOT/tools/$tool_name"
    
    if [ ! -d "$tool_path" ]; then
        print_error "Tool directory not found: $tool_path"
        return 1
    fi
    
    if [ ! -f "$tool_path/Dockerfile" ]; then
        print_error "Dockerfile not found for tool: $tool_name"
        return 1
    fi
    
    print_status "Building $tool_name..."
    cd "$tool_path"
    
    # Build the Docker image
    docker build -t "${tool_name}-api" .
    
    if [ $? -eq 0 ]; then
        print_status "Successfully built $tool_name"
    else
        print_error "Failed to build $tool_name"
        return 1
    fi
}

# Function to build all tools
build_all_tools() {
    print_status "Building all bioinformatics tools..."
    
    # Find all tool directories
    for tool_dir in "$PROJECT_ROOT/tools"/*/; do
        if [ -d "$tool_dir" ]; then
            tool_name=$(basename "$tool_dir")
            if [ -f "$tool_dir/Dockerfile" ]; then
                build_tool "$tool_name"
            else
                print_warning "No Dockerfile found for $tool_name, skipping..."
            fi
        fi
    done
    
    print_status "All tools built successfully!"
}

# Main execution
if [ $# -eq 0 ]; then
    # Build all tools
    build_all_tools
else
    # Build specific tool
    tool_name=$1
    build_tool "$tool_name"
fi

print_status "Build process completed!" 