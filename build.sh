#!/bin/bash
set -e

# --- Configuration & Argument Parsing ---
TARGET=$1

# Check if a valid target was provided
if [[ "$TARGET" != "review" && "$TARGET" != "package" && "$TARGET" != "update-templates" ]]; then
    echo "Error: Invalid or missing target." >&2
    echo "Usage: $0 [review | package | update-templates]" >&2
    echo "  review           - Build the source zip for extensions.gnome.org review" >&2
    echo "  package          - Build the installable package for GitHub Releases" >&2
    echo "  update-templates - Only update translation template files" >&2
    exit 1
fi

# Read the UUID directly from the metadata.json inside the extension directory
if ! EXTENSION_UUID=$(jq -r '.uuid' extension/metadata.json); then
    echo "Error: Could not parse UUID from extension/metadata.json." >&2
    echo "Please ensure 'jq' is installed and the file is correct." >&2
    exit 1
fi

# --- Update Templates Function ---
update_translation_templates() {
    # This part runs every time, so your templates are always up-to-date.
    echo "Updating translation templates..."

    # Update the UI strings template (from .js files)
    xgettext --from-code=UTF-8 -o po/all-in-one-clipboard.pot -k_ -L JavaScript extension/*.js extension/features/**/*.js extension/utilities/*.js

    # Update the DATA strings template (from .json files) using our Python script
    ./build-aux/extract-data-strings.py po/all-in-one-clipboard-content.pot extension/data

    # Safely merge any new strings into the language files (e.g., all-in-one-clipboard@fr.po)
    echo "Merging new strings into language files..."
    for po_file in po/*.po; do
        if [ -f "$po_file" ]; then
            # Figure out which template to use based on the filename
            if [[ "$po_file" == *"all-in-one-clipboard-content"* ]]; then
                msgmerge --update "$po_file" po/all-in-one-clipboard-content.pot
            else
                msgmerge --update "$po_file" po/all-in-one-clipboard.pot
            fi
        fi
    done
    echo "Translation templates are up-to-date."
}

# --- Update Templates Flag ---
# If the target is "update-templates", just run that function and exit
if [ "$TARGET" == "update-templates" ]; then
    update_translation_templates
    exit 0
fi

# --- Build Directory ---
BUILD_DIR="build_temp" # A temporary directory for packaging

# --- Build Type Flags ---
if [ "$TARGET" == "review" ]; then
    ZIP_FILE="${EXTENSION_UUID}-review.zip"
    COMPILE_ASSETS=false
    echo "Building SOURCE zip for extensions.gnome.org review..."
else # Target is "package"
    ZIP_FILE="${EXTENSION_UUID}.zip"
    COMPILE_ASSETS=true
    echo "Building installable PACKAGE for GitHub Releases..."
fi

# --- Main Script ---
# 1. Clean up previous build artifacts
echo "Cleaning up old build files..."
rm -rf "$BUILD_DIR"
# Clean up both possible zip file names to be safe
rm -f "${EXTENSION_UUID}.zip" "${EXTENSION_UUID}-review.zip"

# Update templates ONLY for the 'package' build, not for 'review'.
if [ "$COMPILE_ASSETS" = true ]; then
    update_translation_templates
fi

# 2. Create a fresh build directory
mkdir -p "$BUILD_DIR"

# 3. Copy the entire contents of the 'extension' directory
echo "Copying all extension files..."
cp -r extension/* "$BUILD_DIR/"

# 4. Compile schemas and translations (conditionally)
if [ "$COMPILE_ASSETS" = true ]; then
    echo "Compiling GSettings schema for local build..."
    glib-compile-schemas "$BUILD_DIR/schemas/"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to compile schemas. Aborting." >&2
        exit 1
    fi

    # --- Compile Translations ---
    echo "Compiling translation files..."
    mkdir -p "$BUILD_DIR/locale"
    # Loop through every .po file
    for po_file in po/*.po; do
        if [ -f "$po_file" ]; then
            # Get the language code
            lang_code=$(basename "$po_file" .po | cut -d'@' -f2)
            # If no '@' is present, it's not a valid language file for us, so skip.
            if [[ "$lang_code" == $(basename "$po_file" .po) ]]; then continue; fi

            # Get the domain (the part before '@')
            domain=$(basename "$po_file" .po | cut -d'@' -f1)

            # Create the final directory for this language inside the build target
            mkdir -p "$BUILD_DIR/locale/$lang_code/LC_MESSAGES"

            # Compile the .po file into a .mo file directly into the build directory
            echo "  - Compiling $po_file -> $domain.mo for language '$lang_code'"
            msgfmt --output-file="$BUILD_DIR/locale/$lang_code/LC_MESSAGES/$domain.mo" "$po_file"
        fi
    done
else
    echo "Skipping schema and translation compilation for review build."
fi

# 5. Create the zip archive from the build directory
echo "Creating zip file: $ZIP_FILE..."
(cd "$BUILD_DIR" && zip -r "../$ZIP_FILE" . -x ".*" -x "__MACOSX")

# 6. Clean up the temporary build directory
echo "Cleaning up temporary directory..."
rm -rf "$BUILD_DIR"

# 7. Final success message
echo "Build successful! Archive created at: $ZIP_FILE"