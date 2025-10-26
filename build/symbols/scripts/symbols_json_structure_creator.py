# ./scripts/symbols_json_structure_creator.py
import json
import re
import pathlib

# --- Configuration ---
# Get the directory of this script (e.g., /path/to/project/scripts)
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
# Get the root project directory (e.g., /path/to/project/)
PROJECT_ROOT = SCRIPT_DIR.parent

# Define source and output paths relative to the project root
SOURCE_DIR = PROJECT_ROOT / "source"
OUTPUT_FILE = PROJECT_ROOT / "symbols.json"

# The order of this list determines the final order in the JSON file.
SOURCE_FILENAMES = [
    '[Microsoft] General Punctuation.txt',
    '[Microsoft] Currency Symbols.txt',
    '[Microsoft] Latin Symbols.txt',
    '[Microsoft] Geometric Symbols.txt',
    '[Microsoft] Math Symbols.txt',
    '[Microsoft] Supplemental Symbols.txt',
    '[Microsoft] Language Symbols.txt',
]

def clean_category_name(filename):
    """Creates a clean category name from a filename."""
    name = re.sub(r'\[Microsoft\]\s*', '', filename)
    name = name.replace('.txt', '')
    return name.strip()

def read_symbols_from_file(filepath):
    """Reads all characters from a file, treating each as a potential symbol."""
    if not filepath.exists():
        print(f"Warning: Source file '{filepath.name}' not found. Skipping.")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Return a list of all non-whitespace characters
        return [char for char in content if not char.isspace()]

def save_json_data(data, filepath):
    """Saves the final data structure to the JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\nSuccessfully created symbol library: '{filepath}'")

def main():
    """Main function to build the symbols JSON."""
    final_data = []
    print("Starting to build Unicode symbol library...")

    for filename in SOURCE_FILENAMES:
        filepath = SOURCE_DIR / filename
        category_name = clean_category_name(filename)
        symbols = read_symbols_from_file(filepath)

        if not symbols:
            continue

        print(f"Processing '{category_name}'...")
        # Deduplicate and sort symbols by Unicode value
        unique_sorted_symbols = sorted(list(set(symbols)), key=ord)

        category_object = {
            "name": category_name,
            "symbols": unique_sorted_symbols
        }
        final_data.append(category_object)

    save_json_data(final_data, OUTPUT_FILE)

if __name__ == '__main__':
    main()