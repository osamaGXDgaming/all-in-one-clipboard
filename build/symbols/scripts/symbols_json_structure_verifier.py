# ./scripts/symbols_json_structure_verifier.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "symbols.json"

def verify_json_structure(filepath):
    """Verifies the basic structure of the symbols.json file."""
    print(f"--- Verifying structure of '{filepath.name}' ---")
    if not filepath.exists():
        print(f"❌ ERROR: File not found at '{filepath}'")
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Could not read or parse JSON file. Reason: {e}")
        return False

    errors = []
    if not isinstance(data, list):
        errors.append("Top-level structure is not a list.")
    else:
        for i, category in enumerate(data):
            if not isinstance(category, dict):
                errors.append(f"Item at index {i} is not a dictionary/object.")
                continue
            if "name" not in category or not isinstance(category["name"], str):
                errors.append(f"Item {i} ('{category.get('name', 'N/A')}') is missing a valid 'name' key.")
            if "symbols" not in category or not isinstance(category["symbols"], list):
                errors.append(f"Item {i} ('{category.get('name', 'N/A')}') is missing a valid 'symbols' key.")

    if not errors:
        print("✅ SUCCESS: JSON structure is valid.")
        return True
    else:
        print("\n❌ FAILED: Found structural issues:")
        for error in errors:
            print(f"  - {error}")
        return False

if __name__ == '__main__':
    verify_json_structure(INPUT_FILE)