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
    separator_line_content_regex = re.compile(r'^\|[\s:-]+\|$')

    def process_single_table_block(match):
        table_block = match.group(1)
        # print(f"\n--- DEBUG: Processing Table Block ---\n{table_block}\n---") # DEBUG

        lines = table_block.strip().split('\n')
        cleaned_lines = []
        num_cols = 0
        header_line = None
        standard_separator = None
        found_separator = False

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            # print(f"  DEBUG: Line {i}: '{stripped_line}'") # DEBUG
            if table_line_regex.match(stripped_line):
                # Split by unescaped pipes
                cells = [cell.strip() for cell in re.split(r'(?<!\\)\|', stripped_line)]
                # Ensure each cell starts and ends with a pipe for consistent formatting
                cleaned_line = '|' + '|'.join(cells) + '|'
                # Remove empty first/last cells created by leading/trailing pipes
                if cleaned_line.startswith('||'):
                    cleaned_line = cleaned_line[1:]
                if cleaned_line.endswith('||'):
                    cleaned_line = cleaned_line[:-1]


                if i == 0:
                    header_line = cleaned_line
                    # Calculate number of columns based on cells (excluding leading/trailing empty string from split)
                    num_cols = len([c for c in cells if c])
                    standard_separator = '|' + '---|' * num_cols
                    cleaned_lines.append(header_line)
                    # print(f"    DEBUG: Header found: '{header_line}', num_cols: {num_cols}, standard_separator: '{standard_separator}'") # DEBUG
                elif i == 1 and header_line and separator_line_content_regex.match(stripped_line):
                    cleaned_lines.append(standard_separator)
                    found_separator = True
                    # print(f"    DEBUG: Standard separator added/replaced at index 1.") # DEBUG
                elif i > 1 and header_line and (found_separator or separator_line_content_regex.match(stripped_line)):
                    # If it's a data row and a separator was found or current line is a separator
                    cleaned_lines.append(cleaned_line)
                    # print(f"    DEBUG: Data row or original separator kept: '{cleaned_line}'") # DEBUG
                elif i > 1 and header_line and not found_separator and table_line_regex.match(stripped_line):
                    # If it's a data row and no separator has been explicitly found yet
                    cleaned_lines.append(cleaned_line)
                    # print(f"    DEBUG: Data row kept (no explicit separator yet): '{cleaned_line}'") # DEBUG
            else:
                # If it's not a table line, keep it as is
                cleaned_lines.append(line)

        # Ensure a separator exists after the header if it was parsed correctly
        if header_line and num_cols > 0:
            if len(cleaned_lines) == 1: # Only header, no separator or data
                cleaned_lines.insert(1, standard_separator)
                # print(f"    DEBUG: Standard separator inserted (only header found).") # DEBUG
            elif not separator_line_content_regex.match(cleaned_lines[1]):
                # If the second line isn't a separator, replace or insert one
                if table_line_regex.match(cleaned_lines[1]): # It's a data row, insert separator above it
                    cleaned_lines.insert(1, standard_separator)
                    # print(f"    DEBUG: Standard separator inserted (second line was data row).") # DEBUG
                else: # It's some other non-separator, non-data line, just insert
                    cleaned_lines.insert(1, standard_separator)
                    # print(f"    DEBUG: Standard separator inserted (second line wasn't a separator/data).") # DEBUG


        # Remove extra separator lines (more than one immediately after the header)
        # This logic ensures only ONE standard separator line is present after the header.
        final_cleaned_lines_filtered = []
        if cleaned_lines:
            final_cleaned_lines_filtered.append(cleaned_lines[0]) # Always keep the header
            if len(cleaned_lines) > 1 and separator_line_content_regex.match(cleaned_lines[1]):
                final_cleaned_lines_filtered.append(standard_separator) # Always include the standard separator if present
                for i in range(2, len(cleaned_lines)):
                    if not separator_line_content_regex.match(cleaned_lines[i]):
                        final_cleaned_lines_filtered.append(cleaned_lines[i])
            else: # No separator found at index 1, just append all other lines
                for i in range(1, len(cleaned_lines)):
                     final_cleaned_lines_filtered.append(cleaned_lines[i])


        result = "\n".join(final_cleaned_lines_filtered)
        # print(f"--- DEBUG: Final processed table block ---\n{result}\n--- End DEBUG ---\n") # DEBUG
        return result

    return table_block_detection_regex.sub(process_single_table_block, content)


def replace_pipe_o_in_markdown_links(content):
    """
    Replaces all occurrences of '|O' with '| O' only within the TEXT part of Markdown links.
    Example: `[text\|Ovalue](url)` becomes `[text\| Ovalue](url)`
    """
    # Regex to capture a Markdown link: [text](url)
    # Group 1: The opening bracket '['
    # Group 2: The text content inside the brackets (the part we want to modify)
    # Group 3: The closing '](url)' part of the link
    markdown_link_regex = re.compile(r'(\[)([^\]]+)(\]\([^)]*\))')

    def replace_text_content(match):
        prefix = match.group(1) # '['
        text_content = match.group(2) # The text inside the brackets
        suffix = match.group(3) # '](url)'

        print(f"DEBUG: Original Link Text part: '{text_content}'") # Debug print

        # Perform the specific replacement within the captured text
        # We are looking for the literal string '\' followed by '|O'
        modified_text_content = text_content.replace('\\|O', '\\| O')

        print(f"DEBUG: Modified Link Text part: '{modified_text_content}'") # Debug print

        # Reconstruct the full Markdown link
        return f"{prefix}{modified_text_content}{suffix}"

    # Use re.sub with the callback function to apply the replacement globally
    return markdown_link_regex.sub(replace_text_content, content)


def process_markdown_files(folder_path="docs"):
    """
    Recursively processes Markdown files to replace image tags, clean up Markdown tables,
    and replace '|O' in markdown link TEXT.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: The directory '{folder_path}' does not exist.")
        return

    print(f"Starting file processing in '{folder_path}' and its subdirectories...")
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(('.md', '.txt')): # Process .md and .txt files
                filepath = os.path.join(root, filename)
                try:
                    print(f"\n--- Processing file: {filepath} ---")
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    original_content = content

                    # Step 1: Replace HTML <img> tags with Markdown syntax
                    modified_content = replace_img_tags_in_content(content)

                    # Step 2: Replace '|O' with '| O' only within Markdown link TEXT
                    modified_content = replace_pipe_o_in_markdown_links(modified_content)

                    # Step 3: Clean up and standardize Markdown tables
                    final_content = clean_markdown_tables_in_content(modified_content)


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
    # --- Test case for replace_pipe_o_in_markdown_links ---
    test_string_1 = "This is a [link with \\|O in text](https://example.com/path?query=\\|Ovalue)."
    test_string_2 = "No change here [link without backslash |O in text](https://example.com/path?query=|Ovalue)."
    test_string_3 = "Another [link with \\|O in file path](file:///path/to/doc\|Owith\|Ofile)."
    test_string_4 = "Multiple [links with \\|O in text](http://test.com/\!O) and [another \\|O here](http://test.com/\!O?q=\!O)."
    test_string_5 = "[Just \\|O at start](url)"
    test_string_6 = "[\\|O at end](url)"


    print("\n--- Testing replace_pipe_o_in_markdown_links function directly ---")
    print(f"Input 1: {test_string_1}")
    print(f"Output 1: {replace_pipe_o_in_markdown_links(test_string_1)}\n")

    print(f"Input 2: {test_string_2}")
    print(f"Output 2: {replace_pipe_o_in_markdown_links(test_string_2)}\n")

    print(f"Input 3: {test_string_3}")
    print(f"Output 3: {replace_pipe_o_in_markdown_links(test_string_3)}\n")

    print(f"Input 4: {test_string_4}")
    print(f"Output 4: {replace_pipe_o_in_markdown_links(test_string_4)}\n")

    print(f"Input 5: {test_string_5}")
    print(f"Output 5: {replace_pipe_o_in_markdown_links(test_string_5)}\n")

    print(f"Input 6: {test_string_6}")
    print(f"Output 6: {replace_pipe_o_in_markdown_links(test_string_6)}\n")

    print("--- End direct function testing ---\n")

    process_markdown_files()
