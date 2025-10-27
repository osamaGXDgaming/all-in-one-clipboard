# ./scripts/symbols_json_order_verifier.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "symbols.json"

def verify_symbol_order(filepath):
    """Verifies that symbols in each category are sorted by Unicode codepoint."""
    print(f"--- Verifying symbol sort order in '{filepath.name}' ---")
    if not filepath.exists():
        print(f"❌ ERROR: File not found at '{filepath}'")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Could not parse JSON file. Reason: {e}")
        return

    is_fully_sorted = True
    for category in data:
        name = category.get("name", "Unknown")
        symbols = category.get("symbols", [])

        if not symbols:
            print(f"⚪ Category '{name}': No symbols to check.")
            continue

        sorted_symbols = sorted(symbols, key=ord)
        if symbols != sorted_symbols:
            print(f"❌ Category '{name}': NOT sorted correctly.")
            is_fully_sorted = False

    print("\n--- Verification Complete ---")
    if is_fully_sorted:
        print("✅ SUCCESS: All categories are perfectly sorted by Unicode codepoint!")
    else:
        print("❌ FAILED: One or more categories are not sorted correctly.")

if __name__ == '__main__':
    verify_symbol_order(INPUT_FILE)