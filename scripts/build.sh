#!/bin/bash
# Build script for bioinformatics tool wrappers using docker-compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --service <name>       Build specific service (default: all)"
    echo "  --version <version>    Override version from VERSION files"
    echo "  --platform <arch>      Build for specific platform (amd64, arm64, or multi)"
    echo "  --push                 Push to registry after building"
    echo "  --no-cache            Build without cache"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Build all services with versions from VERSION files"
    echo "  $0 --service spider    # Build only SPIDER service"
    echo "  $0 --version 1.3.0     # Build with specific version"
    echo "  $0 --platform amd64    # Build only AMD64 version"
    echo "  $0 --no-cache          # Build without cache"
}

# Parse command line arguments
SERVICE=""
VERSION=""
PLATFORM="multi"
PUSH=false
NO_CACHE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --service)
            SERVICE="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        -*)
            print_error "Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            print_error "Unexpected argument $1"
            show_usage
            exit 1
            ;;
    esac
done

# Change to project root
cd "$(dirname "$0")/.."

# Validate platform
case "$PLATFORM" in
    "amd64"|"arm64"|"multi")
        ;;
    *)
        print_error "Invalid platform: $PLATFORM (use amd64, arm64, or multi)"
        exit 1
        ;;
esac

# Set up environment variables
if [[ -n "$VERSION" ]]; then
    export VERSION="$VERSION"
    print_status "Using specified version: $VERSION"
else
    # Read version from VERSION file if it exists
    if [[ -f "tools/spider/VERSION" ]]; then
        SPIDER_VERSION=$(cat tools/spider/VERSION | tr -d ' \t\n\r')
        export VERSION="$SPIDER_VERSION"
        print_status "Using SPIDER version from VERSION file: $VERSION"
    else
        export VERSION="latest"
        print_warning "No VERSION file found, using 'latest'"
    fi
fi

# Set up buildx for multi-arch builds
if [[ "$PLATFORM" == "multi" ]]; then
    print_status "Setting up Docker buildx for multi-arch builds..."
    docker buildx create --use --name bioinformatics-builder 2>/dev/null || true
fi

# Build command
BUILD_CMD="docker-compose build"

if [[ -n "$SERVICE" ]]; then
    BUILD_CMD="$BUILD_CMD $SERVICE"
    print_status "Building service: $SERVICE"
else
    print_status "Building all services"
fi

if [[ "$NO_CACHE" == "true" ]]; then
    BUILD_CMD="$BUILD_CMD --no-cache"
    print_status "Building without cache"
fi

# Execute build
print_status "Executing: $BUILD_CMD"
print_status "Version: $VERSION"
print_status "Platform: $PLATFORM"

eval "$BUILD_CMD"

if [[ $? -eq 0 ]]; then
    print_success "Build completed successfully!"
    
    # Show built images
    print_status "Built images:"
    docker images | grep "spider-api" | head -3
    
    if [[ "$PUSH" == "true" ]]; then
        print_status "Pushing images to registry..."
        docker-compose push
        print_success "Images pushed successfully!"
    fi
else
    print_error "Build failed!"
    exit 1
fi 