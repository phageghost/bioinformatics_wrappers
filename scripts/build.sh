#!/bin/bash
# Build script for bioinformatics tool wrappers

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
    echo "  --no-increment        Don't increment build number"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Build all services with versions from VERSION files"
    echo "  $0 --service spider    # Build only SPIDER service"
    echo "  $0 --version 1.3.0     # Build with specific version"
    echo "  $0 --platform amd64    # Build only AMD64 version"
    echo "  $0 --no-cache          # Build without cache"
    echo "  $0 --no-increment      # Build without incrementing build number"
}

# Function to read version from VERSION file
read_version() {
    local tool_name=$1
    local version_file="tools/$tool_name/VERSION"
    
    if [[ -f "$version_file" ]]; then
        cat "$version_file" | tr -d ' \t\n\r'
    else
        echo "latest"
    fi
}

# Function to increment build number
increment_build_number() {
    local tool_name=$1
    local version_file="tools/$tool_name/VERSION"
    local build_file="tools/$tool_name/BUILD"
    
    # Read current version
    local current_version=$(read_version "$tool_name")
    
    if [[ "$current_version" == "latest" ]]; then
        print_warning "Cannot increment build number for 'latest' version"
        echo "latest"
        return
    fi
    
    # Read current build number
    local current_build=0
    if [[ -f "$build_file" ]]; then
        current_build=$(cat "$build_file" | tr -d ' \t\n\r')
        if [[ ! "$current_build" =~ ^[0-9]+$ ]]; then
            current_build=0
        fi
    fi
    
    # Increment build number
    local new_build=$((current_build + 1))
    
    # Write new build number
    echo "$new_build" > "$build_file"
    
    # Return version with build number
    echo "${current_version}.${new_build}"
}

# Function to validate semver format
validate_semver() {
    local version=$1
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 1
    fi
    return 0
}

# Parse command line arguments
SERVICE=""
VERSION=""
PLATFORM="multi"
PUSH=false
NO_CACHE=false
NO_INCREMENT=false

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
        --no-increment)
            NO_INCREMENT=true
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

# Determine version and service
if [[ -n "$SERVICE" ]]; then
    if [[ -z "$VERSION" ]]; then
        BASE_VERSION=$(read_version "$SERVICE")
        if [[ "$NO_INCREMENT" == "true" ]]; then
            VERSION="$BASE_VERSION"
            print_status "Using $SERVICE version from VERSION file: $VERSION (no increment)"
        else
            VERSION=$(increment_build_number "$SERVICE")
            print_status "Using $SERVICE version with build number: $VERSION"
        fi
    else
        print_status "Using specified version: $VERSION"
    fi
    
    # Validate version format (skip for versions with build numbers)
    if [[ ! "$VERSION" =~ \.[0-9]+$ ]] && [[ "$VERSION" != "latest" ]] && ! validate_semver "$VERSION"; then
        print_warning "Version '$VERSION' doesn't follow semver format (x.y.z)"
    fi
    
    # Set up buildx for multi-arch builds
    if [[ "$PLATFORM" == "multi" ]]; then
        print_status "Setting up Docker buildx for multi-arch builds..."
        docker buildx create --use --name bioinformatics-builder 2>/dev/null || true
    fi
    
    # Build command based on platform
    if [[ "$PLATFORM" == "multi" ]]; then
        print_status "Building multi-arch image for $SERVICE version $VERSION"
        docker buildx build \
            --platform linux/amd64,linux/arm64 \
            -t "${SERVICE}-api:${VERSION}" \
            -t "${SERVICE}-api:latest" \
            --load \
            "./tools/$SERVICE"
    else
        print_status "Building $PLATFORM image for $SERVICE version $VERSION"
        docker buildx build \
            --platform "linux/$PLATFORM" \
            -t "${SERVICE}-api:${VERSION}-${PLATFORM}" \
            --load \
            "./tools/$SERVICE"
    fi
    
    print_success "Build completed successfully!"
    
    # Show built images
    print_status "Built images:"
    docker images | grep "${SERVICE}-api" | head -3
    
else
    # Build all services
    print_status "Building all services..."
    
    # For now, just build SPIDER since it's the only service
    BASE_VERSION=$(read_version "spider")
    if [[ "$NO_INCREMENT" == "true" ]]; then
        SPIDER_VERSION="$BASE_VERSION"
        print_status "Building SPIDER version: $SPIDER_VERSION (no increment)"
    else
        SPIDER_VERSION=$(increment_build_number "spider")
        print_status "Building SPIDER version with build number: $SPIDER_VERSION"
    fi
    
    if [[ "$PLATFORM" == "multi" ]]; then
        docker buildx create --use --name bioinformatics-builder 2>/dev/null || true
        docker buildx build \
            --platform linux/amd64,linux/arm64 \
            -t "spider-api:${SPIDER_VERSION}" \
            -t "spider-api:latest" \
            --load \
            "./tools/spider"
    else
        docker buildx build \
            --platform "linux/$PLATFORM" \
            -t "spider-api:${SPIDER_VERSION}-${PLATFORM}" \
            --load \
            "./tools/spider"
    fi
    
    print_success "Build completed successfully!"
    
    # Show built images
    print_status "Built images:"
    docker images | grep "spider-api" | head -3
fi 