# ./scripts/symbols_json_order_enforcer.py
import json
import pathlib
import shutil

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TARGET_FILE = PROJECT_ROOT / "symbols.json"

def sort_symbols_in_place(filepath):
    """
    Sorts the 'symbols' list in each category of the JSON file by Unicode value.
    Creates a backup of the original file before modifying.
    """
    print(f"--- Applying sorting changes to '{filepath.name}' ---")
    if not filepath.exists():
        print(f"❌ ERROR: File not found at '{filepath}'")
        return

    # Create a backup
    backup_path = filepath.with_suffix(".json.bak")
    try:
        shutil.copy(filepath, backup_path)
        print(f"Created backup: '{backup_path.name}'")
    except Exception as e:
        print(f"❌ ERROR: Could not create backup file. Aborting. Reason: {e}")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Could not parse JSON file. Aborting. Reason: {e}")
        return
        
    changes_made = False
    for category in data:
        if "symbols" in category and isinstance(category["symbols"], list):
            original_list = category["symbols"].copy()
            # Sort the list in-place using the Unicode value (ord)
            category["symbols"].sort(key=ord)
            if original_list != category["symbols"]:
                print(f"Sorted symbols in category: '{category.get('name')}'")
                changes_made = True

    if not changes_made:
        print("No changes needed. All categories were already sorted.")
        backup_path.unlink() # Remove the unnecessary backup
        print("Removed backup file.")
        return

    # Save the modified data back to the original file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ SUCCESS: Successfully sorted and saved changes to '{filepath.name}'")
    except Exception as e:
        print(f"\n❌ FAILED: Could not save changes. Reason: {e}")

if __name__ == '__main__':
    sort_symbols_in_place(TARGET_FILE)