# ./script/kaomojis_json_old_data_deduplicator.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# The file to read from, which may contain duplicates
INPUT_FILE = PROJECT_ROOT / "kaomojis_cleaned.json"

# The new, clean file that will be created
OUTPUT_FILE = PROJECT_ROOT / "kaomojis_simple_deduplicated.json"

def deduplicate_kaomojis():
    """
    Reads the expanded kaomojis JSON file, removes any duplicate kaomojis
    found across all categories, and saves a clean version.
    """
    print("--- Kaomoji De-duplication Script ---")

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
    print("Scanning for duplicates...")
    
    # This map stores the location of the first instance of each kaomoji
    # Format: { "(＾▽＾)": "Positive > Joy" }
    seen_kaomojis_map = {}
    
    # This list will store the log of duplicates found for the final report
    duplicates_log = []

    # This will be our new, clean data structure
    clean_data = []

    for main_category in original_data:
        main_name = main_category.get("name")
        new_main_cat = {"name": main_name, "categories": []}

        for sub_category in main_category.get("categories", []):
            sub_name = sub_category.get("name")
            location = f"{main_name} > {sub_name}"
            
            new_sub_cat = {"name": sub_name, "emoticons": []}
            
            for kaomoji in sub_category.get("emoticons", []):
                if kaomoji in seen_kaomojis_map:
                    # This is a duplicate. Log it and skip it.
                    first_seen_location = seen_kaomojis_map[kaomoji]
                    log_entry = f"'{kaomoji}' in '{location}' is a duplicate. First seen in '{first_seen_location}'."
                    duplicates_log.append(log_entry)
                else:
                    # This is the first time we've seen this kaomoji.
                    # Keep it and record its location.
                    seen_kaomojis_map[kaomoji] = location
                    new_sub_cat["emoticons"].append(kaomoji)
            
            # Only add the sub-category if it still has emoticons after cleaning
            if new_sub_cat["emoticons"]:
                new_main_cat["categories"].append(new_sub_cat)

        # Only add the main category if it still has sub-categories
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
    deduplicate_kaomojis()