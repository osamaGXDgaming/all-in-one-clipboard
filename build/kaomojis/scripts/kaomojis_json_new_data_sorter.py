# ./script/kaomojis_json_new_data_sorter.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# The file with the CORRECT ORDER of kaomoji strings.
# This should be your clean, de-duplicated "old structure" file.
ORDER_SOURCE_FILE = PROJECT_ROOT / "kaomojis_simple_deduplicated.json"

# The detailed file with the rich objects that needs to be re-ordered.
# This might be your AI draft or a de-duplicated detailed file.
DETAILED_FILE_TO_SORT = PROJECT_ROOT / "kaomojis_complex_expanded.json"

# The final, correctly ordered output file.
FINAL_OUTPUT_FILE = PROJECT_ROOT / "kaomojis_complex_sorted.json"

def create_ai_object_map(detailed_data):
    """
    Creates a dictionary mapping each kaomoji string to its full, detailed object
    for fast lookups.
    """
    kaomoji_map = {}
    for main_cat in detailed_data:
        for sub_cat in main_cat.get("categories", []):
            for emoticon_obj in sub_cat.get("emoticons", []):
                if "kaomoji" in emoticon_obj:
                    kaomoji_map[emoticon_obj["kaomoji"]] = emoticon_obj
    return kaomoji_map

def find_subcategory(data_structure, main_cat_name, sub_cat_name):
    """Helper function to find a specific sub-category object by name."""
    main_cat = next((mc for mc in data_structure if mc.get("name") == main_cat_name), None)
    if main_cat:
        return next((sc for sc in main_cat.get("categories", []) if sc.get("name") == sub_cat_name), None)
    return None

def reorder_detailed_data():
    """
    Re-sorts the emoticons in the detailed file based on the order
    in the old-structure source file, preserving all data.
    """
    print("--- Kaomoji Re-ordering Script ---")

    # --- Step 1: Load both files ---
    try:
        print(f"Loading order source: '{ORDER_SOURCE_FILE.name}'")
        with open(ORDER_SOURCE_FILE, 'r', encoding='utf-8') as f:
            order_data = json.load(f)

        print(f"Loading detailed file to sort: '{DETAILED_FILE_TO_SORT.name}'")
        with open(DETAILED_FILE_TO_SORT, 'r', encoding='utf-8') as f:
            detailed_data = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ ERROR: File not found. Missing: {e.filename}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: A file is not valid JSON. Details: {e}")
        return

    # --- Step 2: Create the fast lookup map from the detailed data ---
    print("\nBuilding a map of detailed kaomoji objects...")
    detailed_object_map = create_ai_object_map(detailed_data)
    print(f"Mapped {len(detailed_object_map)} unique objects.")

    # --- Step 3: Iterate through the original order and rebuild ---
    print("Re-ordering emoticons based on the source file...")

    orphans_log = []

    # We will modify the 'detailed_data' structure in place.
    for main_cat_orig in order_data:
        main_name = main_cat_orig.get("name")
        for sub_cat_orig in main_cat_orig.get("categories", []):
            sub_name = sub_cat_orig.get("name")

            # Find the corresponding sub-category in the detailed data to modify it
            sub_cat_detailed = find_subcategory(detailed_data, main_name, sub_name)
            if not sub_cat_detailed:
                print(f"  - Warning: Category '{main_name} > {sub_name}' not found in the detailed file. Skipping.")
                continue

            correctly_ordered_emoticons = []
            original_order_set = set()

            # Place all known kaomojis in the correct order
            for kaomoji_str in sub_cat_orig.get("emoticons", []):
                original_order_set.add(kaomoji_str)
                detailed_obj = detailed_object_map.get(kaomoji_str)
                if detailed_obj:
                    correctly_ordered_emoticons.append(detailed_obj)

            # Find and append any "orphan" kaomojis from the detailed file
            detailed_category_set = {obj["kaomoji"] for obj in sub_cat_detailed.get("emoticons", [])}
            orphans = detailed_category_set - original_order_set

            if orphans:
                for orphan_str in sorted(list(orphans)): # Sort orphans for predictable order
                    detailed_obj = detailed_object_map.get(orphan_str)
                    if detailed_obj:
                        correctly_ordered_emoticons.append(detailed_obj)
                        log_entry = f"Preserved new kaomoji '{orphan_str}' in category '{main_name} > {sub_name}'."
                        orphans_log.append(log_entry)

            # Replace the scrambled list with our new, complete list
            sub_cat_detailed["emoticons"] = correctly_ordered_emoticons

    print("\n--- Re-ordering Report ---")
    if not orphans_log:
        print("✅ All kaomojis were successfully re-ordered according to the source file.")
    else:
        print(f"⚠️ Found and preserved {len(orphans_log)} new kaomojis not present in the source order file:")
        for log in orphans_log:
            print(f"  - {log}")

    # --- Step 4: Save the final, corrected file ---
    try:
        with open(FINAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ SUCCESS: Saved the correctly ordered data to '{FINAL_OUTPUT_FILE.name}'")
    except Exception as e:
        print(f"❌ FAILED: Could not save the final file. Reason: {e}")

if __name__ == '__main__':
    reorder_detailed_data()