# ./script/kaomojis_json_old_data_expander.py
import json
import pathlib

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

SOURCE_DIR = PROJECT_ROOT / "source"
BASE_JSON_FILE = PROJECT_ROOT / "kaomojis_original.json"
OUTPUT_JSON_FILE = PROJECT_ROOT / "kaomojis_simple_expanded.json"

MAPPING = [
    {
        'sources': ['[Microsoft] Happy.txt', '[Google] Smiling.txt'],
        'main_category': 'Positive',
        'sub_category': 'Joy'
    },
    {
        'sources': ['[Google] Love.txt'],
        'main_category': 'Positive',
        'sub_category': 'Love'
    },
    {
        'sources': ['[Microsoft] Acting Cute.txt'],
        'main_category': 'Positive',
        'sub_category': 'Cute'
    },
    {
        'sources': ['[Microsoft] Sad.txt', '[Google] Crying.txt'],
        'main_category': 'Negative',
        'sub_category': 'Sadness'
    },
    {
        'sources': ['[Microsoft] Angry.txt'],
        'main_category': 'Negative',
        'sub_category': 'Anger'
    },
    {
        'sources': ['[Google] Look of Disapproval.txt'],
        'main_category': 'Negative',
        'sub_category': 'Dissatisfaction'
    },
    {
        'sources': ['[Google] Nervous.txt'],
        'main_category': 'Negative',
        'sub_category': 'Fear'
    },
    {
        'sources': ['[Google] Shruggie.txt'],
        'main_category': 'Neutral',
        'sub_category': 'Indifference'
    },
    {
        'sources': ['[Microsoft] Surprised_Speechless.txt', '[Google] Surprise.txt'],
        'main_category': 'Neutral',
        'sub_category': 'Surprise'
    },
    {
        'sources': ['[Microsoft] Greeting.txt'],
        'main_category': 'Various',
        'sub_category': 'Greeting'
    },
    {
        'sources': ['[Google] Hugging.txt'],
        'main_category': 'Various',
        'sub_category': 'Hugging'
    },
    {
        'sources': ['[Google] Table Flip.txt'],
        'main_category': 'Various',
        'sub_category': 'Table Flipping'
    },
    {
        'sources': ['[Google] Dancing.txt'],
        'main_category': 'Various',
        'sub_category': 'Dancing'
    },
    {
        'sources': ['[Google] Flexing.txt'],
        'main_category': 'Various',
        'sub_category': 'Flexing'
    },
    {
        'sources': ['[Google] Pointers.txt'],
        'main_category': 'Various',
        'sub_category': 'Pointing'
    },
    {
        'sources': ['[Google] Animals.txt'],
        'main_category': 'Animals',
        'sub_category': 'General'
    },
    {
        'sources': ['[Microsoft] Classic ASCII Emoticons.txt', '[Google] Classic.txt'],
        'main_category': 'Other',
        'sub_category': 'Classic'
    }
]

def load_json_data(filepath):
    """Loads the initial JSON data from the base file."""
    if not filepath.exists():
        print(f"❌ ERROR: The base file '{filepath.name}' was not found in the root directory.")
        exit()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ ERROR: The file '{filepath.name}' is not a valid JSON file.")
        exit()

def read_kaomojis_from_file(filepath):
    """Reads all lines from a text file and returns them as a list."""
    if not filepath.exists():
        print(f"  - Warning: Source file '{filepath.name}' not found. Skipping.")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_json_data(data, filepath):
    """Saves the final data structure to a new JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"\n✅ SUCCESS: Created the expanded file: '{filepath}'")

def main():
    """Main function to run the merging process."""
    kaomoji_data = load_json_data(BASE_JSON_FILE)
    print("Starting the merge process...")

    master_set = set()
    for main_cat in kaomoji_data:
        for sub_cat in main_cat.get('categories', []):
            master_set.update(sub_cat.get('emoticons', []))

    for rule in MAPPING:
        main_cat_name = rule['main_category']
        sub_cat_name = rule['sub_category']

        print(f"Processing rule for '{main_cat_name} -> {sub_cat_name}'...")

        new_kaomojis_from_files = []
        for source_filename in rule['sources']:
            filepath = SOURCE_DIR / source_filename
            new_kaomojis_from_files.extend(read_kaomojis_from_file(filepath))

        if not new_kaomojis_from_files:
            continue

        main_cat_obj = next((cat for cat in kaomoji_data if cat['name'] == main_cat_name), None)
        if not main_cat_obj:
            print(f"  - Error: Main category '{main_cat_name}' not found. Check MAPPING.")
            continue

        sub_cat_obj = next((scat for scat in main_cat_obj['categories'] if scat['name'] == sub_cat_name), None)

        if sub_cat_obj is None:
            print(f"  - Creating new sub-category: '{sub_cat_name}'")
            sub_cat_obj = {'name': sub_cat_name, 'emoticons': []}
            main_cat_obj['categories'].append(sub_cat_obj)

        existing_emoticons = set(sub_cat_obj['emoticons'])
        unique_new_kaomojis = {k for k in new_kaomojis_from_files if k not in master_set}

        added_count = len(unique_new_kaomojis)
        if added_count > 0:
            print(f"  - Adding {added_count} new unique kaomojis.")

        combined_set = existing_emoticons.union(unique_new_kaomojis)
        sub_cat_obj['emoticons'] = sorted(list(combined_set))
        master_set.update(unique_new_kaomojis)

    save_json_data(kaomoji_data, OUTPUT_JSON_FILE)

if __name__ == '__main__':
    main()