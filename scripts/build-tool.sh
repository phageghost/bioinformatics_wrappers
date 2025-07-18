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
    echo "Usage: $0 <tool_name> [options]"
    echo ""
    echo "Options:"
    echo "  --version <version>    Override version from VERSION file"
    echo "  --platform <arch>      Build for specific platform (amd64, arm64, or multi)"
    echo "  --push                 Push to registry after building"
    echo "  --export <file>        Export to tarball"
    echo "  --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 spider                    # Build SPIDER with version from VERSION file"
    echo "  $0 spider --version 1.3.0    # Build SPIDER with specific version"
    echo "  $0 spider --platform amd64   # Build only AMD64 version"
    echo "  $0 spider --export spider.tar # Export to tarball"
}

# Parse command line arguments
TOOL_NAME=""
VERSION=""
PLATFORM="multi"
PUSH=false
EXPORT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
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
        --export)
            EXPORT_FILE="$2"
            shift 2
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
            if [[ -z "$TOOL_NAME" ]]; then
                TOOL_NAME="$1"
            else
                print_error "Multiple tool names specified"
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if tool name is provided
if [[ -z "$TOOL_NAME" ]]; then
    print_error "Tool name is required"
    show_usage
    exit 1
fi

# Check if tool directory exists
TOOL_DIR="tools/$TOOL_NAME"
if [[ ! -d "$TOOL_DIR" ]]; then
    print_error "Tool directory '$TOOL_DIR' not found"
    exit 1
fi

# Read version from VERSION file if not specified
if [[ -z "$VERSION" ]]; then
    VERSION_FILE="$TOOL_DIR/VERSION"
    if [[ -f "$VERSION_FILE" ]]; then
        VERSION=$(cat "$VERSION_FILE" | tr -d ' \t\n\r')
        print_status "Using version from $VERSION_FILE: $VERSION"
    else
        print_error "No VERSION file found in $TOOL_DIR and no --version specified"
        exit 1
    fi
fi

# Validate version format (simple semver check)
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_warning "Version '$VERSION' doesn't follow semver format (x.y.z)"
fi

# Set up buildx if not already configured
if ! docker buildx inspect --bootstrap >/dev/null 2>&1; then
    print_status "Setting up Docker buildx..."
    docker buildx create --use --name bioinformatics-builder || true
fi

# Determine platform flags
case "$PLATFORM" in
    "amd64")
        PLATFORM_FLAG="--platform linux/amd64"
        IMAGE_TAG="${TOOL_NAME}-api:${VERSION}-amd64"
        ;;
    "arm64")
        PLATFORM_FLAG="--platform linux/arm64"
        IMAGE_TAG="${TOOL_NAME}-api:${VERSION}-arm64"
        ;;
    "multi")
        PLATFORM_FLAG="--platform linux/amd64,linux/arm64"
        IMAGE_TAG="${TOOL_NAME}-api:${VERSION}"
        ;;
    *)
        print_error "Invalid platform: $PLATFORM (use amd64, arm64, or multi)"
        exit 1
        ;;
esac

print_status "Building $TOOL_NAME version $VERSION for platform: $PLATFORM"
print_status "Image tag: $IMAGE_TAG"

# Build the image
cd "$TOOL_DIR"
print_status "Building from directory: $(pwd)"

if [[ "$PLATFORM" == "multi" ]]; then
    # Multi-arch build
    docker buildx build $PLATFORM_FLAG \
        -t "$IMAGE_TAG" \
        -t "${TOOL_NAME}-api:latest" \
        --push \
        .
    
    print_success "Multi-arch image built and pushed: $IMAGE_TAG"
else
    # Single arch build
    docker buildx build $PLATFORM_FLAG \
        -t "$IMAGE_TAG" \
        --load \
        .
    
    print_success "Single-arch image built: $IMAGE_TAG"
    
    # Export to tarball if requested
    if [[ -n "$EXPORT_FILE" ]]; then
        print_status "Exporting to tarball: $EXPORT_FILE"
        docker save "$IMAGE_TAG" -o "$EXPORT_FILE"
        print_success "Image exported to: $EXPORT_FILE"
    fi
fi

# Show image info
print_status "Image information:"
docker images | grep "$TOOL_NAME-api" | head -3

print_success "Build completed successfully!" 