import re
import os

def replace_img_tags_in_content(content):
    """Replaces <img alt="..." src="..."> tags with Markdown ![]() syntax in a string."""
    img_regex = re.compile(r'<img\s+alt="([^"]*)"\s+src="([^"]*)"[^>]*>', re.IGNORECASE)
    def replace_img(match):
        alt_text = match.group(1)
        src_url = match.group(2)
        return f'![{alt_text}]({src_url})'
    return img_regex.sub(replace_img, content)

def clean_markdown_tables_in_content(content):
    """Clears extra spacing and ensures exactly one standardized separator line in Markdown tables."""
    table_block_detection_regex = re.compile(r'(^\|.*\|\n(?:\|.*\|(?:\n\|.*\|)*)?)', re.MULTILINE)
    table_line_regex = re.compile(r'^\|.*?\|$')
    separator_line_content_regex = re.compile(r'^\|[\s:-]+\\|$')

    def process_single_table_block(match):
        table_block = match.group(1)
        print(f"\n--- DEBUG: Processing Table Block ---\n{table_block}\n---") # DEBUG

        lines = table_block.strip().split('\n')
        cleaned_lines = []
        num_cols = 0
        header_line = None
        standard_separator = None
        found_separator = False

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            print(f"  DEBUG: Line {i}: '{stripped_line}'") # DEBUG
            if table_line_regex.match(stripped_line):
                cells = [cell.strip() for cell in stripped_line.split('|')]
                cleaned_line = '|'.join(cells)
                if i == 0:
                    header_line = cleaned_line
                    num_cols = len(cells) - 2 if len(cells) > 1 else 0
                    standard_separator = '|' + '---|' * num_cols
                    cleaned_lines.append(header_line)
                    print(f"    DEBUG: Header found: '{header_line}', num_cols: {num_cols}, standard_separator: '{standard_separator}'") # DEBUG
                elif i == 1 and header_line and separator_line_content_regex.match(stripped_line):
                    cleaned_lines.append(standard_separator)
                    found_separator = True
                    print(f"    DEBUG: Standard separator added/replaced at index 1.") # DEBUG
                elif i > 1 and header_line and (found_separator or separator_line_content_regex.match(stripped_line)):
                    cleaned_lines.append(cleaned_line)
                    print(f"    DEBUG: Data row or original separator kept: '{cleaned_line}'") # DEBUG
                elif i > 1 and header_line and not found_separator and table_line_regex.match(stripped_line):
                    cleaned_lines.append(cleaned_line)
                    print(f"    DEBUG: Data row kept (no explicit separator yet): '{cleaned_line}'") # DEBUG
            else:
                cleaned_lines.append(line)

        # Ensure a separator exists after the header
        if header_line and not cleaned_lines[1:2] and num_cols > 0:
            cleaned_lines.insert(1, standard_separator)
            print(f"    DEBUG: Standard separator inserted (no original found).") # DEBUG
        elif header_line and cleaned_lines[1:2] and not separator_line_content_regex.match(cleaned_lines[1]):
            # If the second line isn't a separator, insert one
            cleaned_lines.insert(1, standard_separator)
            print(f"    DEBUG: Standard separator inserted (second line wasn't a separator).") # DEBUG

        # Remove extra separator lines (more than one immediately after the header)
        final_cleaned_lines = [cleaned_lines[0]] # Keep the header
        separator_added = False
        for i in range(1, len(cleaned_lines)):
            if separator_line_content_regex.match(cleaned_lines[i]) and not separator_added:
                final_cleaned_lines.append(cleaned_lines[i])
                separator_added = True
            elif not separator_line_content_regex.match(cleaned_lines[i]):
                final_cleaned_lines.append(cleaned_lines[i])

        result = "\n".join(final_cleaned_lines)
        print(f"--- DEBUG: Final processed table block ---\n{result}\n--- End DEBUG ---\n") # DEBUG
        return result

    return table_block_detection_regex.sub(process_single_table_block, content)

def process_markdown_files(folder_path="docs"):
    """
    Recursively processes Markdown files to replace image tags and clean up Markdown tables.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: The directory '{folder_path}' does not exist.")
        return

    print(f"Starting file processing in '{folder_path}' and its subdirectories...")
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(('.md', '.txt')):
                filepath = os.path.join(root, filename)
                try:
                    print(f"\n--- Processing file: {filepath} ---") # DEBUG
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    original_content = content

                    # Replace image tags
                    modified_content_img = replace_img_tags_in_content(content)

                    # Clean up Markdown tables
                    final_content = clean_markdown_tables_in_content(modified_content_img)

                    if final_content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(final_content)
                        print(f"  Modified: {filepath}")
                    else:
                        print(f"  No changes: {filepath}")

                except Exception as e:
                    print(f"  Error processing {filepath}: {e}")
    print(f"\n--- Finished file processing ---")

if __name__ == "__main__":
    process_markdown_files()
