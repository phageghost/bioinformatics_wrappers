#!/bin/bash
# Version management script for bioinformatics tool wrappers

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
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  show [tool]           Show version(s) for tool(s)"
    echo "  set <tool> <version>  Set version for specific tool"
    echo "  bump <tool> [type]    Bump version for tool (patch, minor, major)"
    echo "  list                  List all tools and their versions"
    echo "  validate              Validate all version files"
    echo ""
    echo "Examples:"
    echo "  $0 show spider        # Show SPIDER version"
    echo "  $0 show               # Show all versions"
    echo "  $0 set spider 1.3.0   # Set SPIDER to version 1.3.0"
    echo "  $0 bump spider minor  # Bump SPIDER minor version"
    echo "  $0 list               # List all tools"
}

# Function to validate semver format
validate_semver() {
    local version=$1
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 1
    fi
    return 0
}

# Function to bump version
bump_version() {
    local version=$1
    local bump_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $bump_type in
        "major")
            echo "$((major + 1)).0.0"
            ;;
        "minor")
            echo "$major.$((minor + 1)).0"
            ;;
        "patch"|*)
            echo "$major.$minor.$((patch + 1))"
            ;;
    esac
}

# Function to show version
show_version() {
    local tool_name=$1
    
    if [[ -n "$tool_name" ]]; then
        local version_file="tools/$tool_name/VERSION"
        if [[ -f "$version_file" ]]; then
            local version=$(cat "$version_file" | tr -d ' \t\n\r')
            echo "$tool_name: $version"
        else
            print_warning "No VERSION file found for $tool_name"
        fi
    else
        # Show all versions
        for tool_dir in tools/*/; do
            if [[ -d "$tool_dir" ]]; then
                local tool_name=$(basename "$tool_dir")
                local version_file="$tool_dir/VERSION"
                if [[ -f "$version_file" ]]; then
                    local version=$(cat "$version_file" | tr -d ' \t\n\r')
                    echo "$tool_name: $version"
                else
                    echo "$tool_name: no version file"
                fi
            fi
        done
    fi
}

# Function to set version
set_version() {
    local tool_name=$1
    local version=$2
    
    if [[ -z "$tool_name" || -z "$version" ]]; then
        print_error "Tool name and version are required"
        exit 1
    fi
    
    local tool_dir="tools/$tool_name"
    if [[ ! -d "$tool_dir" ]]; then
        print_error "Tool directory '$tool_dir' not found"
        exit 1
    fi
    
    if ! validate_semver "$version"; then
        print_error "Invalid version format: $version (expected x.y.z)"
        exit 1
    fi
    
    local version_file="$tool_dir/VERSION"
    echo "$version" > "$version_file"
    print_success "Set $tool_name version to $version"
}

# Function to bump version
bump_version_cmd() {
    local tool_name=$1
    local bump_type=${2:-patch}
    
    if [[ -z "$tool_name" ]]; then
        print_error "Tool name is required"
        exit 1
    fi
    
    local version_file="tools/$tool_name/VERSION"
    if [[ ! -f "$version_file" ]]; then
        print_error "No VERSION file found for $tool_name"
        exit 1
    fi
    
    local current_version=$(cat "$version_file" | tr -d ' \t\n\r')
    local new_version=$(bump_version "$current_version" "$bump_type")
    
    echo "$new_version" > "$version_file"
    print_success "Bumped $tool_name version from $current_version to $new_version"
}

# Function to list all tools
list_tools() {
    print_status "Available tools and their versions:"
    echo ""
    
    for tool_dir in tools/*/; do
        if [[ -d "$tool_dir" ]]; then
            local tool_name=$(basename "$tool_dir")
            local version_file="$tool_dir/VERSION"
            if [[ -f "$version_file" ]]; then
                local version=$(cat "$version_file" | tr -d ' \t\n\r')
                echo "  $tool_name: $version"
            else
                echo "  $tool_name: no version file"
            fi
        fi
    done
}

# Function to validate all versions
validate_versions() {
    local has_errors=false
    
    print_status "Validating all version files..."
    
    for tool_dir in tools/*/; do
        if [[ -d "$tool_dir" ]]; then
            local tool_name=$(basename "$tool_dir")
            local version_file="$tool_dir/VERSION"
            
            if [[ -f "$version_file" ]]; then
                local version=$(cat "$version_file" | tr -d ' \t\n\r')
                if validate_semver "$version"; then
                    print_success "$tool_name: $version ✓"
                else
                    print_error "$tool_name: $version ✗ (invalid format)"
                    has_errors=true
                fi
            else
                print_warning "$tool_name: no version file"
            fi
        fi
    done
    
    if [[ "$has_errors" == "true" ]]; then
        print_error "Validation failed - some versions are invalid"
        exit 1
    else
        print_success "All versions are valid!"
    fi
}

# Main script logic
COMMAND=$1
shift

case $COMMAND in
    "show")
        show_version "$1"
        ;;
    "set")
        set_version "$1" "$2"
        ;;
    "bump")
        bump_version_cmd "$1" "$2"
        ;;
    "list")
        list_tools
        ;;
    "validate")
        validate_versions
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac 