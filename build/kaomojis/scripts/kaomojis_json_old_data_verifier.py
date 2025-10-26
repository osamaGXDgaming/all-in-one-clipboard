# ./script/kaomojis_json_old_data_verifier.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# The original, base file. This is the "source of truth".
ORIGINAL_FILE = PROJECT_ROOT / "kaomojis_original.json"

# The new, expanded file that should contain everything from the original, plus more.
EXPANDED_FILE = PROJECT_ROOT / "kaomojis_simple_deduplicated.json"

def extract_kaomoji_map(data):
    """
    Extracts all kaomojis from a data structure and maps them to their location.
    Returns a dictionary: { "(* ^ ω ^)": "Positive > Joy" }
    """
    location_map = {}
    for main_category in data:
        main_name = main_category.get("name", "N/A")
        for sub_category in main_category.get("categories", []):
            sub_name = sub_category.get("name", "N/A")
            location = f"{main_name} > {sub_name}"
            for kaomoji in sub_category.get("emoticons", []):
                location_map[kaomoji] = location
    return location_map

def extract_kaomoji_set(data):
    """Extracts all kaomojis from a data structure into a simple set for fast lookups."""
    kaomoji_set = set()
    for main_category in data:
        for sub_category in main_category.get("categories", []):
            kaomoji_set.update(sub_category.get("emoticons", []))
    return kaomoji_set

def verify_old_data_is_present():
    """
    Checks if all kaomojis from the original file are present in the expanded file.
    """
    print("--- Original Kaomoji Data Preservation Verifier ---")

    # --- Step 1: Load both files ---
    try:
        print(f"Loading original file: '{ORIGINAL_FILE.name}'...")
        with open(ORIGINAL_FILE, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        print(f"Loading expanded file: '{EXPANDED_FILE.name}'...")
        with open(EXPANDED_FILE, 'r', encoding='utf-8') as f:
            expanded_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ ERROR: File not found. Missing: {e.filename}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: A file is not valid JSON. Details: {e}")
        return

    # --- Step 2: Extract kaomojis from both files ---
    original_kaomoji_map = extract_kaomoji_map(original_data)
    expanded_kaomoji_set = extract_kaomoji_set(expanded_data)
    
    print(f"\nFound {len(original_kaomoji_map)} unique kaomojis in the original file.")
    print(f"Found {len(expanded_kaomoji_set)} unique kaomojis in the expanded file.")

    # --- Step 3: Check for missing items and generate report ---
    missing_items = []
    # For every kaomoji in the original file...
    for kaomoji, location in original_kaomoji_map.items():
        # ...check if it exists in the expanded file's set.
        if kaomoji not in expanded_kaomoji_set:
            missing_items.append({"kaomoji": kaomoji, "location": location})

    print("\n--- Verification Report ---")
    if not missing_items:
        print("✅ SUCCESS: All data from the original file has been successfully preserved.")
    else:
        print(f"❌ FAILED: Found {len(missing_items)} kaomojis from the original file that are MISSING in the expanded file:")
        for item in missing_items:
            print(f"  - {item['kaomoji']} (was in category: {item['location']})")

if __name__ == '__main__':
    verify_old_data_is_present()