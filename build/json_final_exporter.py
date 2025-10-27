import argparse
import json
import hashlib
import sys
from pathlib import Path

# --- Configuration Section ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE_PATH = SCRIPT_DIR / 'json_final_config.json'

# An explicit map from data type to its directory name.
TYPE_TO_DIRECTORY_MAP = {
    "emoji": "emojis",
    "kaomoji": "kaomojis",
    "symbol": "symbols"
}

# Hardcoded defaults. These are used if json_final_config.json is missing or incomplete.
INTERNAL_DEFAULTS = {
    "emoji": "emojis_detailed.json",
    "kaomoji": "kaomojis_cleaned.json",
    "symbol": "symbols_detailed.json"
}

# Central place to define attributions.
ATTRIBUTIONS = {
    "emoji": {
        "provider": "Unicode Consortium",
        "url": "https://unicode.org/emoji/charts/full-emoji-list.html",
        "notes": "Data is derived from Unicode emoji charts and enriched with additional metadata."
    },
    "kaomoji": {
        "provider": "Various (Google, Microsoft, etc.)",
        "url": "https://github.com/NiffirgkcaJ/all-in-one-clipboard",
        "notes": "Kaomojis are aggregated from various public sources."
    },
    "symbol": {
        "provider": "Various (Microsoft, Unicode, etc.)",
        "url": "https://github.com/NiffirgkcaJ/all-in-one-clipboard",
        "notes": "Symbols are aggregated from various public sources and Unicode standards."
    }
}

# --- Helper Functions ---
def load_and_merge_config():
    """Loads default source files with a clear priority."""
    effective_defaults = INTERNAL_DEFAULTS.copy()
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            user_sources = user_config.get("default_sources", {})
            if user_sources:
                effective_defaults.update(user_sources)
                print(f"INFO: Loaded custom defaults from '{CONFIG_FILE_PATH}'")
        except json.JSONDecodeError:
            print(f"Warning: Could not parse '{CONFIG_FILE_PATH}'. Using internal defaults.", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Error reading '{CONFIG_FILE_PATH}'. Using internal defaults. Error: {e}", file=sys.stderr)
    else:
        print(f"INFO: No '{CONFIG_FILE_PATH}' found. Using internal defaults.")
    return effective_defaults

def load_extension_metadata():
    """Loads static metadata from the extension's metadata.json file."""
    metadata_path = PROJECT_ROOT / 'extension' / 'metadata.json'
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        return {
            "name": metadata.get("name"),
            "uuid": metadata.get("uuid")
        }
    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: Could not load extension/metadata.json. Will skip embedding this info.", file=sys.stderr)
        return None

def get_emoji_version(data_list):
    """Parses emoji data to find the highest Unicode version number."""
    max_version = 0.0
    try:
        for category in data_list:
            for emoji in category.get("emojis", []):
                version_str = emoji.get("unicode_version", "0.0")
                try:
                    version_float = float(version_str)
                    if version_float > max_version:
                        max_version = version_float
                except (ValueError, TypeError):
                    continue
    except Exception as e:
        print(f"Warning: Could not determine emoji version due to unexpected data structure. Error: {e}", file=sys.stderr)
        return "unknown"
    return str(max_version)

def get_content_hash(data_list):
    """Calculates the SHA256 hash of the JSON data to create a unique version string."""
    data_string = json.dumps(data_list, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    hash_object = hashlib.sha256(data_string.encode('utf-8'))
    return f"sha256:{hash_object.hexdigest()[:16]}"

def main():
    final_defaults = load_and_merge_config()

    parser = argparse.ArgumentParser(
        description="Finalizes a JSON data file by adding metadata and copying it to the extension directory."
    )
    parser.add_argument(
        "-i", "--input",
        dest="input_specifier",
        type=str,
        help="A filename to use from the default directory (e.g., 'file.json'), OR a full/relative path to override the default location."
    )
    parser.add_argument(
        "-o", "--output",
        dest="destination_file",
        type=Path,
        help="Override the default output file path.")
    parser.add_argument(
        "-t", "--type",
        required=True,
        choices=['emoji', 'kaomoji', 'symbol'],
        help="The type of data being processed.")
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="The number of spaces to use for indentation in the output JSON. Default is 2."
    )

    args = parser.parse_args()

    # --- 1. Determine Input and Output Paths ---
    input_spec = args.input_specifier
    source_file = None

    # Get the correct plural directory name from our map.
    directory_name = TYPE_TO_DIRECTORY_MAP[args.type]
    # Build the full, correct base path.
    default_base_dir = PROJECT_ROOT / 'build' / directory_name

    if input_spec:
        input_path = Path(input_spec)
        if str(input_path.parent) == '.':
            source_file = default_base_dir / input_path
            print(f"INFO: Interpreted '{input_spec}' as a filename in the default directory.")
        else:
            source_file = input_path
            print(f"INFO: Interpreted '{input_spec}' as an explicit path.")
    else:
        default_filename = final_defaults[args.type]
        source_file = default_base_dir / default_filename
        print(f"INFO: No input specified. Using configured default: '{default_filename}'")

    print(f"  > Final source path: '{source_file}'")

    destination_file = args.destination_file
    if not destination_file:
        destination_file = PROJECT_ROOT / 'extension' / 'data' / f'{args.type}s.json'
        print(f"INFO: No output specified. Using default destination.")

    print(f"  > Final destination path: '{destination_file}'")

    # --- 2. Load Source File and Extension Metadata ---
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Source file not found at '{source_file}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON from '{source_file}'.", file=sys.stderr)
        sys.exit(1)

    extension_info = load_extension_metadata()
    print(f"\nProcessing '{source_file}' as type '{args.type}'...")

    # --- 3. Determine Data Version ---
    if args.type == 'emoji':
        data_version = get_emoji_version(source_data)
    else:
        data_version = get_content_hash(source_data)
    print(f"  > Determined data version: {data_version}")

    # --- 4. Assemble the Final File Structure ---
    final_json_structure = {
        "_metadata": {
            "data_version": data_version,
            "attribution": ATTRIBUTIONS.get(args.type),
            "extension_info": extension_info
        },
        "data": source_data
    }

    # --- 5. Write the Finalized File ---
    try:
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_file, 'w', encoding='utf-8') as f:
            json.dump(final_json_structure, f, indent=args.indent, ensure_ascii=False)
    except Exception as e:
        print(f"\nError: Could not write to destination file '{destination_file}'. Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n✅ Success! Finalized data written to '{destination_file}'")

if __name__ == "__main__":
    main()