import json
import argparse
import os

def format_json_file(file_path, indent_level, output_path=None):
    """
    Reads a JSON file, formats it with the specified indentation,
    and writes it back to a file.

    Args:
        file_path (str): The path to the input JSON file.
        indent_level (int): The number of spaces to use for indentation.
        output_path (str, optional): The path for the output file.
                                     If None, overwrites the input file.
    """
    try:
        # Step 1: Read and Parse the JSON file
        # The 'encoding="utf-8"' is crucial for handling special characters like kaomojis.
        with open(file_path, 'r', encoding='utf-8') as f:
            # This is the "structure agnostic" part. json.load() builds the Python
            # object regardless of the JSON's internal structure.
            data = json.load(f)

        # Determine the destination for the formatted file
        destination_path = output_path if output_path else file_path
        
        # Step 2: Write and Serialize the data back to a file with formatting
        with open(destination_path, 'w', encoding='utf-8') as f:
            # json.dump() writes the Python object back to a JSON formatted string.
            # - indent=indent_level: Adds newlines and whitespace for readability.
            # - ensure_ascii=False: Preserves non-ASCII characters (like kaomojis)
            #   instead of converting them to escape sequences (\uXXXX).
            json.dump(data, f, indent=indent_level, ensure_ascii=False)
        
        if destination_path == file_path:
            print(f"✅ Successfully formatted '{file_path}' in-place.")
        else:
            print(f"✅ Successfully formatted '{file_path}' and saved to '{destination_path}'.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{file_path}'. Could not parse.")
        print(f"   Details: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred while processing '{file_path}': {e}")


def main():
    """
    Main function to parse command-line arguments and process files.
    """
    parser = argparse.ArgumentParser(
        description="A structure-agnostic tool to format JSON files with proper indentation.",
        epilog="Example: python format_json.py my_file.json --indent 2"
    )

    parser.add_argument(
        "input_paths",
        nargs='+',  # Allows one or more input files/directories
        help="One or more paths to JSON files or directories containing JSON files."
    )
    
    parser.add_argument(
        "-i", "--indent",
        type=int,
        default=2,
        help="The number of spaces to use for indentation. Default is 2."
    )

    parser.add_argument(
        "-o", "--output",
        help="Optional: Path to the output file. If not provided, files are formatted in-place. "
             "Only works when providing a single input file."
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true", # Makes it a flag, e.g., just add '-r'
        help="If an input path is a directory, search for .json files recursively."
    )

    args = parser.parse_args()

    # Validate that --output is only used with a single input file
    if args.output and len(args.input_paths) > 1:
        print("❌ Error: The --output option can only be used with a single input file.")
        return

    for path in args.input_paths:
        if os.path.isfile(path):
            format_json_file(path, args.indent, args.output)
        elif os.path.isdir(path):
            if args.recursive:
                for root, _, files in os.walk(path):
                    for name in files:
                        if name.lower().endswith('.json'):
                            file_path = os.path.join(root, name)
                            format_json_file(file_path, args.indent) # Always in-place for recursive
            else:
                print(f"ℹ️ '{path}' is a directory. Use the -r/--recursive flag to process .json files within it.")
        else:
            print(f"⚠️ Warning: The path '{path}' does not exist or is not a file/directory.")


if __name__ == "__main__":
    main()