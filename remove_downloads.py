#!/usr/bin/env python3
import os
import re

def remove_downloads_from_md_files(start_directory):
    """
    Recursively finds all .md files in the start_directory and its subdirectories,
    and removes lines containing "Downloads" (case-insensitive).
    """
    print(f"Starting to scan directory: {start_directory}")
    print("WARNING: This script will modify files directly. Consider backing up your data.")

    # Regex to match lines containing "Downloads" (case-insensitive)
    # It accounts for potential Markdown table formatting and leading/trailing whitespace.
    downloads_regex = re.compile(r'^\s*\|?.*downloads.*\|\s*$', re.IGNORECASE)

    modified_files_count = 0
    skipped_files_count = 0

    for root, _, files in os.walk(start_directory):
        for filename in files:
            if filename.lower().endswith(".md"):
                filepath = os.path.join(root, filename)
                print(f"Processing: {filepath}")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    new_lines = []
                    found_downloads = False
                    for line in lines:
                        if downloads_regex.search(line):
                            print(f"  - Removed line: {line.strip()}")
                            found_downloads = True
                        else:
                            new_lines.append(line)

                    if found_downloads:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(new_lines)
                        print(f"  Successfully updated '{filename}'.")
                        modified_files_count += 1
                    else:
                        print(f"  No 'Downloads' lines found in '{filename}'.")
                        skipped_files_count += 1

                except Exception as e:
                    print(f"ERROR: Could not process '{filepath}': {e}")
                    skipped_files_count += 1
    
    print("\n--- Summary ---")
    print(f"Files modified: {modified_files_count}")
    print(f"Files skipped (no 'Downloads' lines or error): {skipped_files_count}")
    print("Process complete.")


if __name__ == "__main__":
    # Define the directory to start scanning from.
    # Set this to your 'docs' folder or a specific subfolder like 'docs/themes'
    target_directory = "docs/themes" # <--- IMPORTANT: Adjust this path as needed!

    if not os.path.isdir(target_directory):
        print(f"Error: Directory '{target_directory}' not found.")
        print("Please set 'target_directory' in the script to the correct path.")
    else:
        remove_downloads_from_md_files(target_directory)
