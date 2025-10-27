import json
import argparse
import os
from collections import OrderedDict

def get_data_type(value):
    """
    Returns the appropriate type name for a value.
    Handles special cases for lists and objects.
    """
    if isinstance(value, list):
        return "Array"
    elif isinstance(value, dict):
        return "Object"
    elif isinstance(value, str):
        return "String"
    elif isinstance(value, bool):
        return "Boolean"
    elif isinstance(value, int):
        return "Integer"
    elif isinstance(value, float):
        return "Float"
    elif value is None:
        return "Null"
    else:
        return str(type(value))

def analyze_json_structure(data, structure=None):
    """
    Recursively analyzes the JSON data to determine its structure and data types.
    """
    if structure is None:
        structure = OrderedDict()

    # Handle the case where the top level is a list (JSON array)
    if isinstance(data, list):
        if not data:
            structure["<Array Contents>"] = "Empty Array"
            return structure

        # Analyze only the first element as a representative sample
        sample_element = data[0]
        array_structure = OrderedDict()

        analyze_json_structure(sample_element, array_structure)

        structure["<Array: Items structure>"] = array_structure

    # Handle the case where the top level is an object (JSON object)
    elif isinstance(data, dict):
        for key, value in data.items():
            data_type = get_data_type(value)

            if data_type == "Object":
                # Recurse for nested objects
                structure[key] = analyze_json_structure(value, OrderedDict())
            elif data_type == "Array":
                # Handle lists within the object
                list_structure = OrderedDict()
                analyze_json_structure(value, list_structure)
                structure[key] = list_structure
            else:
                # Simple value
                structure[key] = data_type

    return structure

def print_structure(structure, indent=0):
    """
    Prints the analyzed structure in a readable, hierarchical format.
    """
    for key, value in structure.items():
        # Indentation for hierarchy
        print("    " * indent, end="")

        if isinstance(value, dict):
            # Nested object or array structure
            print(f"🔹 {key} (Object/Array):")
            print_structure(value, indent + 1)
        else:
            # Key with a simple type
            print(f"🔸 {key}: {value}")

def process_file(file_path):
    """
    Loads, analyzes, and prints the structure of a single JSON file.
    """
    try:
        # Step 1. Load the JSON data from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("\n" + "="*80)
        print(f"🔎 Analyzing JSON structure for: **{file_path}**")
        print("="*80)

        # Step 2. Analyze the structure
        json_structure = analyze_json_structure(data)

        # Step 3. Print the results
        print_structure(json_structure)
        print("="*80)

    except FileNotFoundError:
        print(f"❌ Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in '{file_path}'. Could not parse.")
        print(f"   Details: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred while processing '{file_path}': {e}")


def main():
    """
    Main function to parse command-line arguments and process files/directories.
    """
    parser = argparse.ArgumentParser(
        description="Analyzes and outputs the general key/type structure of one or more JSON files.",
        epilog="Example: python json_structure_analyzer_cli.py config.json data/ --recursive"
    )

    parser.add_argument(
        "input_paths",
        nargs='+',  # Allows one or more input files/directories
        help="One or more paths to JSON files or directories containing JSON files."
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true", # Makes it a boolean flag
        help="If an input path is a directory, search for .json files recursively."
    )

    # Note: Unlike the formatter, structure analysis doesn't need an --output flag
    # because it just prints to the console (stdout).

    args = parser.parse_args()

    for path in args.input_paths:
        if os.path.isfile(path):
            process_file(path)
        elif os.path.isdir(path):
            if args.recursive:
                print(f"\n📂 Scanning directory recursively: '{path}'")
                processed_count = 0
                for root, _, files in os.walk(path):
                    for name in files:
                        if name.lower().endswith('.json'):
                            file_path = os.path.join(root, name)
                            process_file(file_path)
                            processed_count += 1
                if processed_count == 0:
                    print(f"ℹ️ No .json files found in '{path}' or its subdirectories.")
            else:
                print(f"ℹ️ '{path}' is a directory. Use the -r/--recursive flag to process .json files within it.")
        else:
            print(f"⚠️ Warning: The path '{path}' does not exist or is not a file/directory.")


if __name__ == "__main__":
    main()