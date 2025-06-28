#!/usr/bin/env python3

import sys
import os
from learning_german.config.settings import OUTPUT_DIR


def extract_examples(input_file):
    """
    Extract:
    1. The first line after each line containing both 'Beispiel' and 'satz' (case-insensitive)
    2. The content of lines beginning with '> [!tldr]- '
    from the input file and write them to a .txt file with the same base name.
    """
    if not os.path.isfile(input_file):
        raise ValueError(f"Input file '{input_file}' does not exist or is not a file.")
    if not input_file.endswith(".md"):
        raise ValueError(f"Input file '{input_file}' must be a Markdown file (.md).")
    # List to hold extracted examples
    examples = []

    # Create output filename with same name as input but .txt extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = f"{base_name}.txt"
    output_path = os.path.join(OUTPUT_DIR, output_file)

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i in range(len(lines) - 1):
            # Extract line after "Beispiel" and "satz"
            if "beispiel" in lines[i].lower() and "satz" in lines[i].lower():
                next_line = lines[i + 1].rstrip()
                if next_line:  # Only add non-empty lines
                    examples.append(next_line)

            # Extract content from tldr lines
            if lines[i].startswith("> [!tldr]- "):
                tldr_content = lines[i][len("> [!tldr]- ") :].strip()
                if tldr_content:  # Only add non-empty content
                    examples.append(tldr_content)

    # Write examples to output file
    with open(output_path, "w", encoding="utf-8") as out:
        for i, example in enumerate(examples):
            out.write(example + "\n")
            # Add empty line between examples, but not after the last one
            if i < len(examples) - 1:
                out.write("\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_examples.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    extract_examples(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    print(f"Examples extracted to {base_name}.txt")
    sys.exit(0)


if __name__ == "__main__":
    main()
