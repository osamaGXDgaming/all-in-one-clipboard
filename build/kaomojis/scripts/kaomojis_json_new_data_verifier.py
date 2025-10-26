# ./script/kaomojis_json_new_data_verifier.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# The "source of truth" file with the old, simple structure.
# This should be the clean, de-duplicated version.
OLD_STRUCTURE_FILE = PROJECT_ROOT / "kaomojis_simple_deduplicated.json"

# The final, enriched file with the new, detailed object structure.
NEW_STRUCTURE_FILE = PROJECT_ROOT / "kaomojis_complex_expanded.json"

def create_map_from_old_structure(data):
    """
    Creates a dictionary mapping each kaomoji string to its location
    from the old data structure (list of strings).
    Example: { "(* ^ ω ^)": "Positive > Joy" }
    """
    location_map = {}
    for main_category in data:
        main_name = main_category.get("name", "N/A")
        for sub_category in main_category.get("categories", []):
            sub_name = sub_category.get("name", "N/A")
            location = f"{main_name} > {sub_name}"
            for kaomoji_str in sub_category.get("emoticons", []):
                location_map[kaomoji_str] = location
    return location_map

def create_map_from_new_structure(data):
    """
    Creates a location map from the new data structure (list of objects).
    """
    location_map = {}
    for main_category in data:
        main_name = main_category.get("name", "N/A")
        for sub_category in main_category.get("categories", []):
            sub_name = sub_category.get("name", "N/A")
            location = f"{main_name} > {sub_name}"
            for emoticon_obj in sub_category.get("emoticons", []):
                if "kaomoji" in emoticon_obj:
                    location_map[emoticon_obj["kaomoji"]] = location
    return location_map

def verify_structures():
    """
    Performs a full, two-way comparison between the old and new data structures.
    """
    print("--- Final Kaomoji Data Structure Verifier ---")

    # --- Step 1: Load both files ---
    try:
        print(f"Loading old structure file: '{OLD_STRUCTURE_FILE.name}'...")
        with open(OLD_STRUCTURE_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        print(f"Loading new structure file: '{NEW_STRUCTURE_FILE.name}'...")
        with open(NEW_STRUCTURE_FILE, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ ERROR: File not found. Missing: {e.filename}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: A file is not valid JSON. Details: {e}")
        return

    # --- Step 2: Create location maps for each file ---
    print("\nBuilding location maps for comparison...")
    old_map = create_map_from_old_structure(old_data)
    new_map = create_map_from_new_structure(new_data)
    
    print(f"Found {len(old_map)} unique kaomojis in the old structure file.")
    print(f"Found {len(new_map)} unique kaomojis in the new structure file.")

    # --- Step 3: Compare the sets of kaomojis ---
    old_kaomojis_set = set(old_map.keys())
    new_kaomojis_set = set(new_map.keys())

    missing_from_new = old_kaomojis_set - new_kaomojis_set
    added_to_new = new_kaomojis_set - old_kaomojis_set

    # --- Step 4: Generate a detailed report ---
    print("\n--- Verification Report ---")
    
    if not missing_from_new and not added_to_new:
        print("✅ SUCCESS: Perfect match! The two files are in sync.")
    else:
        print("❌ FAILED: Found discrepancies between the files.")
        
        if missing_from_new:
            print(f"\n🚨 The following {len(missing_from_new)} kaomojis are MISSING from the new structure file:")
            for item in sorted(list(missing_from_new)):
                location = old_map.get(item, "Unknown Location")
                print(f"  - {item.ljust(25)} (Expected in: {location})")
        
        if added_to_new:
            print(f"\n⚠️ The following {len(added_to_new)} kaomojis were UNEXPECTEDLY ADDED to the new structure file:")
            for item in sorted(list(added_to_new)):
                location = new_map.get(item, "Unknown Location")
                print(f"  - {item.ljust(25)} (Found in: {location})")

if __name__ == '__main__':
    verify_structures()