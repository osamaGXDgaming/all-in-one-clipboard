#!/usr/bin/env python3

import json
import sys
from pathlib import Path

# --- Configuration ---
POT_HEADER = r'''# Translation template for All-in-One Clipboard data content.
# Copyright (C) 2025 YOUR NAME
# This file is distributed under the same license as the All-in-One Clipboard package.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: all-in-one-clipboard\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2025-10-26 10:00+0000\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

'''

# --- Main Logic ---
def escape_string(s):
    """Escapes quotes and backslashes for POT format."""
    return s.replace('\\', '\\\\').replace('"', '\\"')

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract-data-strings.py <output_file.pot> <input_dir>")
        sys.exit(1)

    output_file = Path(sys.argv[1])
    input_dir = Path(sys.argv[2])

    translatable_strings = set()

    # --- EMOJIS ---
    for json_file in input_dir.glob('emojis.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for category in data:
                translatable_strings.add(category['name'])
                for emoji in category.get('emojis', []):
                    translatable_strings.add(emoji['name'])
                    if 'keywords' in emoji:
                        for keyword in emoji['keywords']:
                            translatable_strings.add(keyword)

    # --- SYMBOLS ---
    for json_file in input_dir.glob('symbols.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for category in data:
                translatable_strings.add(category['name'])

    # --- KAOMOJIS ---
    for json_file in input_dir.glob('kaomojis.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for greater_category in data:
                translatable_strings.add(greater_category['name'])
                for inner_category in greater_category.get('categories', []):
                    translatable_strings.add(inner_category['name'])

    # --- Write to the .pot file ---
    sorted_strings = sorted(list(translatable_strings))
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(POT_HEADER)
        for s in sorted_strings:
            if not s: continue # Skip empty strings
            f.write('#: extension/data/*.json\n')
            f.write(f'msgid "{escape_string(s)}"\n')
            f.write('msgstr ""\n\n')

    print(f"Generated {output_file} with {len(sorted_strings)} unique strings.")

if __name__ == '__main__':
    main()