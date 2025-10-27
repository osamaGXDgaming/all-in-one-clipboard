# ./script/kaomojis_json_new_data_deduplicator.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# The detailed file that may contain duplicates.
# This is typically the last file you generated, like the sorted one.
INPUT_FILE = PROJECT_ROOT / "kaomojis_complex_enriched.json"

# The new, clean, and final file that will be created.
OUTPUT_FILE = PROJECT_ROOT / "kaomojis_complex_deduplicated.json"

def deduplicate_detailed_kaomojis():
    """
    Reads a detailed kaomoji JSON file, removes duplicate objects based on
    the 'kaomoji' key, and saves a clean version.
    """
    print("--- Detailed Kaomoji De-duplication Script ---")

    # --- Step 1: Load the input file ---
    if not INPUT_FILE.exists():
        print(f"❌ ERROR: Input file not found at '{INPUT_FILE}'")
        return

    try:
        print(f"Loading file: '{INPUT_FILE.name}'...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: The file is not valid JSON. Details: {e}")
        return

    # --- Step 2: Process the data and remove duplicates ---
    print("Scanning for duplicates in the detailed structure...")

    # This map will store the location of the first instance of each kaomoji string.
    seen_kaomojis_map = {}

    # This list will store the log of duplicates for the final report.
    duplicates_log = []

    # This will be our new, clean data structure.
    clean_data = []

    for main_category in original_data:
        main_name = main_category.get("name")
        new_main_cat = {"name": main_name, "categories": []}

        for sub_category in main_category.get("categories", []):
            sub_name = sub_category.get("name")
            location = f"{main_name} > {sub_name}"

            # We need to preserve all keys from the sub-category object.
            new_sub_cat = sub_category.copy()
            new_sub_cat["emoticons"] = [] # Start with an empty list to fill.

            for emoticon_obj in sub_category.get("emoticons", []):
                kaomoji_str = emoticon_obj.get("kaomoji")
                if not kaomoji_str: # Skip if the object is malformed
                    continue

                if kaomoji_str in seen_kaomojis_map:
                    # This is a duplicate. Log it and skip this object.
                    first_seen_location = seen_kaomojis_map[kaomoji_str]
                    log_entry = f"'{kaomoji_str}' in '{location}' is a duplicate. First seen in '{first_seen_location}'."
                    duplicates_log.append(log_entry)
                else:
                    # This is the first time we've seen this kaomoji.
                    # Keep the entire object and record its location.
                    seen_kaomojis_map[kaomoji_str] = location
                    new_sub_cat["emoticons"].append(emoticon_obj)

            # Only add the sub-category if it still has emoticons after cleaning.
            if new_sub_cat["emoticons"]:
                new_main_cat["categories"].append(new_sub_cat)

        # Only add the main category if it still has sub-categories.
        if new_main_cat["categories"]:
            clean_data.append(new_main_cat)

    # --- Step 3: Print the final report ---
    print("\n--- De-duplication Report ---")
    if not duplicates_log:
        print("✅ SUCCESS: No duplicates were found in the file.")
    else:
        print(f"⚠️ Found and removed {len(duplicates_log)} duplicate kaomojis:")
        for log in duplicates_log:
            print(f"  - {log}")

    # --- Step 4: Save the new, clean file ---
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ SUCCESS: Saved the clean, de-duplicated data to '{OUTPUT_FILE.name}'")
    except Exception as e:
        print(f"❌ FAILED: Could not save the final file. Reason: {e}")

if __name__ == '__main__':
    deduplicate_detailed_kaomojis()