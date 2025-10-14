#!/bin/bash
set -e

# --- Configuration & Argument Parsing ---
TARGET=$1

# Check if a valid target was provided
if [[ "$TARGET" != "review" && "$TARGET" != "package" ]]; then
    echo "Error: Invalid or missing target." >&2
    echo "Usage: $0 [review | package]" >&2
    echo "  review  - Build the source zip for extensions.gnome.org review" >&2
    echo "  package - Build the installable package for GitHub Releases" >&2
    exit 1
fi

# Read the UUID directly from the metadata.json inside the extension directory
if ! EXTENSION_UUID=$(jq -r '.uuid' extension/metadata.json); then
    echo "Error: Could not parse UUID from extension/metadata.json." >&2
    echo "Please ensure 'jq' is installed and the file is correct." >&2
    exit 1
fi

BUILD_DIR="build_temp" # A temporary directory for packaging

# Set the output filename and compilation flag based on the target
if [ "$TARGET" == "review" ]; then
    ZIP_FILE="${EXTENSION_UUID}-review.zip"
    COMPILE_SCHEMAS=false
    echo "Building SOURCE zip for extensions.gnome.org review..."
else # Target is "package"
    ZIP_FILE="${EXTENSION_UUID}.zip"
    COMPILE_SCHEMAS=true
    echo "Building installable PACKAGE for GitHub Releases..."
fi

# --- Main Script ---
# 1. Clean up previous build artifacts
echo "Cleaning up old build files..."
rm -rf "$BUILD_DIR"
# Clean up both possible zip file names to be safe
rm -f "${EXTENSION_UUID}.zip" "${EXTENSION_UUID}-review.zip"

# 2. Create a fresh build directory
mkdir -p "$BUILD_DIR"

# 3. Copy the entire contents of the 'extension' directory
echo "Copying all extension files..."
cp -r extension/* "$BUILD_DIR/"

# 4. Compile the GSettings schema (conditionally)
if [ "$COMPILE_SCHEMAS" = true ]; then
    echo "Compiling GSettings schema for local build..."
    glib-compile-schemas "$BUILD_DIR/schemas/"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to compile schemas. Aborting." >&2
        exit 1
    fi
else
    echo "Skipping schema compilation as per extensions.gnome.org requirements."
fi

# 5. Create the zip archive from the build directory
echo "Creating zip file: $ZIP_FILE..."
(cd "$BUILD_DIR" && zip -r "../$ZIP_FILE" . -x ".*" -x "__MACOSX")

# 6. Clean up the temporary build directory
echo "Cleaning up temporary directory..."
rm -rf "$BUILD_DIR"

# 7. Final success message
echo "Build successful! Archive created at: $ZIP_FILE"