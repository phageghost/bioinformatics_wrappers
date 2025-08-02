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
    echo "  --list                List all available tools"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Build all services with versions from VERSION files"
    echo "  $0 --service spider    # Build only SPIDER service"
    echo "  $0 --version 1.3.0     # Build with specific version"
    echo "  $0 --platform amd64    # Build only AMD64 version"
    echo "  $0 --no-cache          # Build without cache"
    echo "  $0 --no-increment      # Build without incrementing build number"
    echo "  $0 --list              # List all available tools"
}

# Function to discover available tools
discover_tools() {
    local tools_dir="tools"
    local tools=()
    
    if [[ ! -d "$tools_dir" ]]; then
        print_error "Tools directory '$tools_dir' not found"
        return 1
    fi
    
    for tool_dir in "$tools_dir"/*/; do
        if [[ -d "$tool_dir" ]]; then
            local tool_name=$(basename "$tool_dir")
            # Check if it has a Dockerfile (indicating it's a buildable tool)
            if [[ -f "$tool_dir/Dockerfile" ]]; then
                tools+=("$tool_name")
            fi
        fi
    done
    
    echo "${tools[@]}"
}

# Function to list available tools
list_tools() {
    local tools=($(discover_tools))
    
    if [[ ${#tools[@]} -eq 0 ]]; then
        print_warning "No buildable tools found in tools/ directory"
        return
    fi
    
    print_status "Available tools:"
    for tool in "${tools[@]}"; do
        local version_file="tools/$tool/VERSION"
        local build_file="tools/$tool/BUILD"
        
        if [[ -f "$version_file" ]]; then
            local version=$(cat "$version_file" | tr -d ' \t\n\r')
            local build_info=""
            
            if [[ -f "$build_file" ]]; then
                local build_num=$(cat "$build_file" | tr -d ' \t\n\r')
                build_info=" (build $build_num)"
            fi
            
            echo "  $tool: $version$build_info"
        else
            echo "  $tool: no version file"
        fi
    done
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

# Function to build a single tool
build_tool() {
    local tool_name=$1
    local version=$2
    local platform=$3
    local no_increment=$4
    
    print_status "Building tool: $tool_name"
    
    # Determine version
    local final_version
    if [[ -n "$version" ]]; then
        final_version="$version"
        print_status "Using specified version: $final_version"
    else
        local base_version=$(read_version "$tool_name")
        if [[ "$no_increment" == "true" ]]; then
            final_version="$base_version"
            print_status "Using $tool_name version from VERSION file: $final_version (no increment)"
        else
            final_version=$(increment_build_number "$tool_name")
            print_status "Using $tool_name version with build number: $final_version"
        fi
    fi
    
    # Validate version format (skip for versions with build numbers)
    if [[ ! "$final_version" =~ \.[0-9]+$ ]] && [[ "$final_version" != "latest" ]] && ! validate_semver "$final_version"; then
        print_warning "Version '$final_version' doesn't follow semver format (x.y.z)"
    fi
    
    # Set up buildx for multi-arch builds
    if [[ "$platform" == "multi" ]]; then
        print_status "Setting up Docker buildx for multi-arch builds..."
        docker buildx create --use --name bioinformatics-builder 2>/dev/null || true
    fi
    
    # Prepare cache options
    local cache_opts=""
    if [[ "$NO_CACHE" == "true" ]]; then
        cache_opts="--no-cache"
        print_status "Building without cache"
    else
        cache_opts="--cache-from type=local,src=/tmp/.buildx-cache --cache-to type=local,dest=/tmp/.buildx-cache,mode=max"
        print_status "Building with cache"
    fi
    
    # Build command based on platform
    if [[ "$platform" == "multi" ]]; then
        print_status "Building multi-arch images for $tool_name version $final_version"
        
        # Build AMD64 version
        print_status "Building AMD64 version..."
        docker buildx build \
            --platform linux/amd64 \
            -t "${tool_name}-api:${final_version}-amd64" \
            $cache_opts \
            --load \
            "./tools/$tool_name"
        
        # Build ARM64 version
        print_status "Building ARM64 version..."
        docker buildx build \
            --platform linux/arm64 \
            -t "${tool_name}-api:${final_version}-arm64" \
            $cache_opts \
            --load \
            "./tools/$tool_name"
        
        # Create multi-arch manifest (latest tag)
        print_status "Creating multi-arch manifest..."
        docker manifest create --insecure "${tool_name}-api:${final_version}" \
            "${tool_name}-api:${final_version}-amd64" \
            "${tool_name}-api:${final_version}-arm64" 2>/dev/null || true
        
        docker manifest create --insecure "${tool_name}-api:latest" \
            "${tool_name}-api:${final_version}-amd64" \
            "${tool_name}-api:${final_version}-arm64" 2>/dev/null || true
        
        # Tag the native architecture as latest for local use
        local native_arch=$(uname -m)
        if [[ "$native_arch" == "x86_64" ]]; then
            docker tag "${tool_name}-api:${final_version}-amd64" "${tool_name}-api:latest"
            print_status "Tagged AMD64 image as latest (native architecture)"
        elif [[ "$native_arch" == "arm64" ]]; then
            docker tag "${tool_name}-api:${final_version}-arm64" "${tool_name}-api:latest"
            print_status "Tagged ARM64 image as latest (native architecture)"
        fi
        
    else
        print_status "Building $platform image for $tool_name version $final_version"
        docker buildx build \
            --platform "linux/$platform" \
            -t "${tool_name}-api:${final_version}-${platform}" \
            $cache_opts \
            --load \
            "./tools/$tool_name"
    fi
    
    print_success "Build completed for $tool_name!"
    
    # Show built images
    print_status "Built images for $tool_name:"
    docker images | grep "${tool_name}-api" | head -3
}

# Parse command line arguments
SERVICE=""
VERSION=""
PLATFORM="multi"
PUSH=false
NO_CACHE=false
NO_INCREMENT=false
LIST_TOOLS=false

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
        --list)
            LIST_TOOLS=true
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

# Handle list command
if [[ "$LIST_TOOLS" == "true" ]]; then
    list_tools
    exit 0
fi

# Validate platform
case "$PLATFORM" in
    "amd64"|"arm64"|"multi")
        ;;
    *)
        print_error "Invalid platform: $PLATFORM (use amd64, arm64, or multi)"
        exit 1
        ;;
esac

# Build logic
if [[ -n "$SERVICE" ]]; then
    # Build specific service
    if [[ ! -d "tools/$SERVICE" ]]; then
        print_error "Tool '$SERVICE' not found in tools/ directory"
        print_status "Available tools:"
        list_tools
        exit 1
    fi
    
    if [[ ! -f "tools/$SERVICE/Dockerfile" ]]; then
        print_error "Tool '$SERVICE' does not have a Dockerfile"
        exit 1
    fi
    
    build_tool "$SERVICE" "$VERSION" "$PLATFORM" "$NO_INCREMENT"
    
else
    # Build all services
    tools=($(discover_tools))
    
    if [[ ${#tools[@]} -eq 0 ]]; then
        print_error "No buildable tools found in tools/ directory"
        exit 1
    fi
    
    print_status "Building all tools: ${tools[*]}"
    
    for tool in "${tools[@]}"; do
        echo ""
        build_tool "$tool" "$VERSION" "$PLATFORM" "$NO_INCREMENT"
    done
    
    print_success "All builds completed successfully!"
fi 