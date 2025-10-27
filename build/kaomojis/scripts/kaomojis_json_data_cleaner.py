# ./script/kaomojis_json_data_cleaner.py
import json
import pathlib
import unicodedata

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# The file you want to clean.
INPUT_FILE = PROJECT_ROOT / "kaomojis_simple_expanded.json"

# The new, clean file that will be created.
OUTPUT_FILE = PROJECT_ROOT / "kaomojis_cleaned.json"

# --- Cleaning Configuration ---
# This script will ONLY remove characters belonging to these specific
# Unicode categories. These are the categories for invisible, zero-width
# control and formatting characters.
# Cc = Control, Cf = Format
CATEGORIES_TO_REMOVE = ('Cc', 'Cf')

def clean_kaomoji_string(s):
    """
    Removes only invisible, zero-width characters and strips leading/trailing whitespace.
    """
    # Rebuild the string, keeping every character whose category is NOT in our removal list.
    # This protects all visible characters (letters, symbols, punctuation, dashes, etc.).
    cleaned_chars = [
        char for char in s
        if unicodedata.category(char) not in CATEGORIES_TO_REMOVE
    ]

    # Join the visible characters back into a string and strip leading/trailing whitespace.
    return "".join(cleaned_chars).strip()

def clean_kaomoji_file():
    """
    Reads a kaomoji JSON file, removes only invisible characters, and saves a new version.
    """
    print("--- Precise Invisible Character Cleaner ---")

    if not INPUT_FILE.exists():
        print(f"❌ ERROR: Input file not found at '{INPUT_FILE}'")
        return

    try:
        print(f"\nLoading file: '{INPUT_FILE.name}'...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Could not parse file. Details: {e}")
        return

    print("Scanning for invisible characters to remove...")
    changes_log = []

    for main_category in data:
        for sub_category in main_category.get("categories", []):
            location = f"{main_category.get('name')} > {sub_category.get('name')}"

            emoticons = sub_category.get("emoticons", [])
            if not emoticons: continue

            if isinstance(emoticons[0], str): # Old structure
                cleaned_emoticons = []
                for kaomoji in emoticons:
                    cleaned = clean_kaomoji_string(kaomoji)
                    if cleaned != kaomoji:
                        changes_log.append(f"Cleaned '{kaomoji}' -> '{cleaned}' in '{location}'.")
                    cleaned_emoticons.append(cleaned)
                sub_category["emoticons"] = cleaned_emoticons

            elif isinstance(emoticons[0], dict): # New structure
                for obj in emoticons:
                    original = obj.get("kaomoji")
                    if original:
                        cleaned = clean_kaomoji_string(original)
                        if cleaned != original:
                            changes_log.append(f"Cleaned '{original}' -> '{cleaned}' in '{location}'.")
                            obj["kaomoji"] = cleaned

    print("\n--- Cleaning Report ---")
    if not changes_log:
        print("✅ SUCCESS: No invisible control or format characters were found.")
    else:
        print(f"⚠️ Found and cleaned {len(changes_log)} kaomojis:")
        for log in changes_log:
            print(f"  - {log}")
        print("\nNote: The 'before' and 'after' in the log may look identical because the removed characters are invisible.")

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ SUCCESS: Saved the sanitized data to '{OUTPUT_FILE.name}'")
    except Exception as e:
        print(f"❌ FAILED: Could not save the final file. Reason: {e}")

if __name__ == '__main__':
    clean_kaomoji_file()