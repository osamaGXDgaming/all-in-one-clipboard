# ./scripts/symbols_json_metadata_enricher.py
import json
import pathlib
import unicodedata

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

INPUT_FILE = PROJECT_ROOT / "symbols.json"
OUTPUT_FILE = PROJECT_ROOT / "symbols_detailed.json"

def enrich_json_file(input_path, output_path):
    """Loads symbols.json and enriches it with Unicode metadata."""
    print(f"--- Enriching '{input_path.name}' ---")
    if not input_path.exists():
        print(f"❌ ERROR: Input file not found at '{input_path}'")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Could not parse JSON. Reason: {e}")
        return

    enriched_data = []
    for category in original_data:
        category_name = category.get("name", "Unknown")
        print(f"Processing category: '{category_name}'...")
        
        new_category = {
            "name": category_name,
            "slug": category_name.lower().replace(" ", "-"),
            "symbols": []
        }

        for symbol in category.get("symbols", []):
            try:
                enriched_symbol = {
                    "symbol": symbol,
                    "name": unicodedata.name(symbol),
                    "codepoint": f"U+{ord(symbol):04X}",
                    "category_code": unicodedata.category(symbol)
                }
                new_category["symbols"].append( enriched_symbol)
            except ValueError:
                print(f"  - Warning: Skipping '{symbol}' (no Unicode name found).")

        enriched_data.append(new_category)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ SUCCESS: Enriched data saved to '{output_path}'")
    except Exception as e:
        print(f"\n❌ FAILED: Could not save output file. Reason: {e}")

if __name__ == '__main__':
    enrich_json_file(INPUT_FILE, OUTPUT_FILE)