# ./scripts/emoji_json_metadata_enricher.py
import json
import pathlib

def enrich_emoji_file_with_codepoints(input_path, output_path):
    """
    Loads the emojis.json file, adds a "codepoints" list to each emoji
    object, and saves the result to a new file.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Successfully loaded '{input_path}'.")
    except FileNotFoundError:
        print(f"Error: The input file '{input_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred loading the file: {e}")
        return

    print("Enriching emoji objects with codepoints...")

    # Iterate through each top-level category (e.g., "Smileys & Emotion")
    for category in data:
        if 'emojis' in category and isinstance(category['emojis'], list):
            # Iterate through each emoji object in the category
            for emoji_object in category['emojis']:
                if 'emoji' in emoji_object and isinstance(emoji_object['emoji'], str):

                    # Get the emoji character string (which could be multi-char)
                    emoji_string = emoji_object['emoji']

                    # Create a list of codepoint strings from the character(s)
                    # This list comprehension handles both single and multi-char emojis perfectly.
                    codepoints = [f"U+{ord(char):04X}" for char in emoji_string]

                    # Add the new 'codepoints' field to the object
                    emoji_object['codepoints'] = codepoints

    # Write the newly enriched data to the output file
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"\nProcessing complete!")
            print(f"Successfully saved enriched emoji data to '{output_path}'.")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

# --- SCRIPT EXECUTION ---

# Get the directory where this script is located
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

# Define the input and output filenames
input_filename = "emojis.json"  # Your existing file
output_filename = "emojis_detailed.json" # A new file for the improved data

# Construct the full paths for the files
input_file_path = SCRIPT_DIR / input_filename
output_file_path = SCRIPT_DIR / output_filename

# Run the enrichment process
enrich_emoji_file_with_codepoints(input_file_path, output_file_path)