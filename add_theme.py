#!/usr/bin/env python3
import os
import re
import sys # Import the sys module for exiting the script

# Define the path to the themes index file for the counter
THEMES_INDEX_FILE = "docs/themes/index.md"
# Define the path to the categories index file
CATEGORIES_FILE = "docs/themes/categories.md"
# Define the default base directory for saving markdown files
# This now defaults to 'docs/themes' to simplify relative paths in categories.md
DEFAULT_BASE_SAVE_DIR = "docs/themes"

# Mapping for tags to category headings
CATEGORY_MAPPING = {
    "underrated_gems": "## Underrated Gems",
    "old_but_gold": "## Old but Gold",
    "new_and_upcoming": "## New and Upcoming",
}

def get_user_input(prompt_text):
    """
    Prompts the user for input and checks if they typed 'exit'.
    If 'exit' is typed, the script terminates.
    """
    user_input = input(prompt_text).strip()
    if user_input.lower() == 'exit':
        print("Exiting Markdown Theme Generator. Goodbye!")
        sys.exit() # Terminate the script
    return user_input

def get_next_counter_value(counter_file_path=THEMES_INDEX_FILE):
    """
    Reads the counter from a specific Markdown file (docs/themes/index.md),
    increments it, and updates the file's content.
    Returns the *new* incremented count.
    Handles file existence and specific content format issues.
    """
    if not os.path.exists(counter_file_path):
        print(f"WARNING: Themes index file '{counter_file_path}' not found. "
              "Please ensure it exists and has the expected counter format. Initializing count to 0.")
        # Create a dummy file with initial content for first run convenience
        os.makedirs(os.path.dirname(counter_file_path), exist_ok=True)
        with open(counter_file_path, 'w', encoding='utf-8') as f:
            f.write("""<p>
    Themes added: 0 / 344
    <progress value="0" max="344"/>
</p>""")
        print(f"Created a dummy '{counter_file_path}' with initial counter.")
        return 0 # Return 0, as it will be incremented to 1 by the user's action
                 # and then the next read will see this updated value.

    try:
        with open(counter_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to find the 'Themes added: count / total' line
        text_line_regex = re.compile(r'(Themes added:\s*)(\d+)(\s*\/\s*)(\d+)', re.IGNORECASE)
        # Regex to find the <progress> tag
        progress_tag_regex = re.compile(r'(<progress\s+value=")(\d+)("\s+max=")(\d+)("\s*\/?>)', re.IGNORECASE)

        text_match = text_line_regex.search(content)
        progress_match = progress_tag_regex.search(content)

        current_count = 0
        total_themes = 0

        if text_match:
            current_count = int(text_match.group(2))
            total_themes = int(text_match.group(4))
        else:
            print(f"WARNING: Could not find 'Themes added: count / total' line in '{counter_file_path}'. "
                  "Please ensure the format is correct. Counter will not be updated.")
            return current_count # Return current_count so it doesn't try to update on a bad parse

        new_count = current_count + 1

        # Replace in text line: use re.sub with a callback to preserve groups
        content = text_line_regex.sub(lambda m: f"{m.group(1)}{new_count}{m.group(3)}{m.group(4)}", content, 1)
        
        # Replace in progress tag: also use re.sub with a callback
        if progress_match:
            content = progress_tag_regex.sub(lambda m: f"{m.group(1)}{new_count}{m.group(3)}{total_themes}{m.group(5)}", content, 1)
        else:
            print(f"WARNING: Could not find '<progress value=\"...\" max=\"...\"/>' tag in '{counter_file_path}'. "
                  "The progress bar will not be updated. This is likely a formatting issue in the file.")

        # Save the updated content back to the file
        with open(counter_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"SUCCESS: Counter in '{counter_file_path}' updated to {new_count}.")
        return new_count

    except ValueError:
        print(f"ERROR: Invalid number format in counter file '{counter_file_path}'. Counter will not be updated.")
        return current_count # Return current_count on parse error
    except Exception as e:
        print(f"ERROR: Failed to update counter in '{counter_file_path}': {e}. Counter will not be updated.")
        return current_count # Generic fallback for other errors

def get_multiline_input(prompt):
    """
    Prompts the user for multi-line input until an empty line is entered.
    Each line is checked for 'exit'.
    """
    print(prompt + " (Press Enter on an empty line to finish, or type 'done' or 'exit' to quit):")
    lines = []
    while True:
        line = get_user_input("") # Use the new get_user_input for each line
        if line.lower() == 'done': # Special keyword to finish multi-line input
            break
        if not line: # Empty line also finishes multi-line input
            break
        lines.append(line)
    return "\n".join(lines)

def extract_github_user_repo(repo_url):
    """
    Extracts 'username/repository' from a GitHub repository URL.
    Returns an empty string if not found.
    """
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url, re.IGNORECASE)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return ""

def get_first_letter_info(theme_title):
    """
    Determines the 'Letter' column content and the corresponding directory name
    based on the first character of the theme title.
    Handles alphanumeric and special cases like '80s Neon'.
    Returns a dictionary {'link_char': '$a$', 'dir_name': 'a'}
    """
    first_char = theme_title.strip()[0].lower() if theme_title.strip() else ''
    
    if not first_char or not first_char.isalnum():
        # If title is empty, or starts with a non-alphanumeric character (e.g., '!', '#')
        # Based on example '80s Neon' -> $<a$, _a
        return {'link_char': '$<a$', 'dir_name': '_a'}
    elif first_char.isdigit():
        # If it starts with a digit (e.g., '80s Neon')
        return {'link_char': '$<a$', 'dir_name': '_a'}
    else: # If it starts with an alphabet
        return {'link_char': f'${first_char}$', 'dir_name': first_char}

def custom_table_row_sort_key(row_data):
    """
    Custom sort key for table rows. Sorts by 'Letter' (with _a before a), then by Theme Title.
    row_data is a tuple: (link_char, theme_title, theme_link_path)
    """
    link_char, theme_title, _ = row_data
    
    # Custom order for link_char: '$<a$' should come before '$a$', '$b$' etc.
    # We can use a numerical prefix for sorting
    if link_char == '$<a$':
        letter_sort_value = '00' # Comes first
    else:
        letter_sort_value = link_char.replace('$', '').lower() # e.g., 'a', 'b', etc.
        # Ensure 'a' (01) comes after '00'
        if letter_sort_value.isalpha():
            letter_sort_value = '01' + letter_sort_value

    return (letter_sort_value, theme_title.lower()) # Sort by custom letter value, then by title

def update_categories_file(theme_title, kebab_case_filename, original_tags_list):
    """
    Updates docs/themes/categories.md with the new theme entry if it belongs to
    underrated_gems, old_but_gold, or new_and_upcoming categories.
    Inserts entry alphabetically within its section.
    """
    print(f"\nAttempting to update {CATEGORIES_FILE}...")
    
    # Read existing content
    categories_lines = []
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            categories_lines = f.read().splitlines() 
    else:
        print(f"WARNING: '{CATEGORIES_FILE}' not found. Creating a default structure.")
        # Create a basic file structure with all headings and empty tables
        for heading_text in CATEGORY_MAPPING.values():
            categories_lines.append(heading_text)
            categories_lines.append("") # One blank line after heading
            categories_lines.append("|Letter|Theme|")
            categories_lines.append("|---|---|")
            categories_lines.append("") # One blank line after table separator
        os.makedirs(os.path.dirname(CATEGORIES_FILE), exist_ok=True)

    parsed_sections = {}
    current_section_heading = None
    
    for heading_text in CATEGORY_MAPPING.values():
        parsed_sections[heading_text] = []

    # Parse existing content into structured data
    i = 0
    while i < len(categories_lines):
        line = categories_lines[i].strip()
        
        is_category_heading = False
        for heading_text in CATEGORY_MAPPING.values():
            if line == heading_text:
                current_section_heading = heading_text
                is_category_heading = True
                break
        
        if is_category_heading:
            i += 1 # Move past the heading line
            # Consume blank lines after heading (if any)
            while i < len(categories_lines) and not categories_lines[i].strip():
                i += 1
            
            # Consume table header and separator (checking current line and next)
            if i < len(categories_lines) and categories_lines[i].strip() == "|Letter|Theme|":
                i += 1 
                if i < len(categories_lines) and categories_lines[i].strip() == "|---|---|":
                    i += 1 
            
            # Now, read table rows until next heading or blank line or EOF
            while i < len(categories_lines) and categories_lines[i].strip().startswith('|'):
                # Skip the table header and separator lines themselves if they somehow recur within rows
                if categories_lines[i].strip() == "|Letter|Theme|" or categories_lines[i].strip() == "|---|---|":
                    i += 1
                    continue 
                
                full_row_markdown = categories_lines[i].rstrip() # Store original line without trailing newline
                
                # Extract content for sorting from the row.
                cells = [cell.strip() for cell in re.split(r'(?<!\\)\|', full_row_markdown)][1:-1]
                if len(cells) >= 2:
                    letter_col_content = cells[0].strip()
                    theme_col_content = cells[1].strip()
                    
                    theme_title_in_row_match = re.search(r'\[([^\]]+)\]', theme_col_content)
                    row_theme_title = theme_title_in_row_match.group(1) if theme_title_in_row_match else theme_col_content
                    
                    if current_section_heading: # Only add if we have a valid heading context
                        parsed_sections[current_section_heading].append((letter_col_content, row_theme_title, full_row_markdown))
                i += 1
            # Consume blank lines after table (if any) until next content or EOF
            while i < len(categories_lines) and not categories_lines[i].strip():
                i += 1
            continue 

        i += 1 

    # Construct the new theme entry tuple
    letter_info = get_first_letter_info(theme_title)
    link_char = letter_info['link_char']
    dir_name = letter_info['dir_name']
    
    # Relative path from categories.md to the theme file
    theme_file_relative_path = os.path.join("./", dir_name, kebab_case_filename)
    new_entry_markdown_row = f"|{link_char}|[{theme_title}]({theme_file_relative_path})|"
    new_entry_tuple = (link_char, theme_title, new_entry_markdown_row)

    # Add the new entry to the appropriate category lists in parsed_sections
    added_to_any_category = False
    for tag_key, heading_text in CATEGORY_MAPPING.items():
        if tag_key in original_tags_list:
            parsed_sections[heading_text].append(new_entry_tuple)
            added_to_any_category = True
            print(f"Prepared to add '{theme_title}' to '{heading_text}' section.")

    if not added_to_any_category:
        print(f"No relevant category tags found for '{theme_title}'. Not updating '{CATEGORIES_FILE}'.")
        return 

    # Reconstruct the full content of categories.md with sorted rows
    final_categories_content_lines = []
    
    for heading_text in CATEGORY_MAPPING.values():
        final_categories_content_lines.append(heading_text)
        final_categories_content_lines.append("") # One blank line after heading
        final_categories_content_lines.append("|Letter|Theme|")
        final_categories_content_lines.append("|---|---|")

        # Sort and add rows for this section
        sorted_rows_for_section = sorted(parsed_sections[heading_text], key=custom_table_row_sort_key)
        for row_tuple in sorted_rows_for_section:
            final_categories_content_lines.append(row_tuple[2]) 

        final_categories_content_lines.append("") # One blank line after table
        
    # Join all parts to form the final content.
    # The `filter(None, ...)` and `strip()` is used at the very end to
    # clean up any unintended leading/trailing/multiple blank lines,
    # ensuring only necessary newlines are present.
    final_categories_content = "\n".join(line for line in final_categories_content_lines if line is not None).strip()
    
    # Ensure a single trailing newline at the very end of the file for good measure
    if final_categories_content and not final_categories_content.endswith('\n'):
        final_categories_content += '\n'

    try:
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            f.write(final_categories_content)
        print(f"SUCCESS: '{CATEGORIES_FILE}' updated for '{theme_title}'.")
    except IOError as e:
        print(f"ERROR: Could not save '{CATEGORIES_FILE}': {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while writing to '{CATEGORIES_FILE}': {e}")


def create_markdown_theme_entry():
    """
    Continuously creates new Markdown theme entries based on user input and a predefined template
    until the user types 'exit' for the title.
    Includes prompts for all fields in the provided theme template.
    Automatically extracts GitHub username from repository link.
    Updates a counter in a separate file (docs/themes/index.md) *after* successful file generation.
    """
    print("--- Markdown Theme Generator ---")
    print("You can type 'exit' at any prompt to quit the application.")

    # --- Define the full Markdown template ---
    markdown_template = """---
title: {title}
tags:
{tags_list_yaml}
---

{images_block_markdown}

## Info

|Info|Status|
|---|---|
|Repository Link|[{github_user_repo}]({repository_link})|
|Author|[{author_github_username}](https://github.com/{author_github_username})|
|Last Updated|![GitHub last commit](https://img.shields.io/github/last-commit/{github_user_repo}?color=573E7A&amp;label=last%20update&amp;logo=github&amp;style=for-the-badge)|
|“Help wanted” issues|![GitHub issues by-label](https://img.shields.io/github/issues/{github_user_repo}/help%20wanted?color=573E7A&amp;logo=github&amp;style=for-the-badge)|
|Stars|![GitHub Repo stars](https://img.shields.io/github/stars/{github_user_repo}?color=573E7A&amp;logo=github&amp;style=for-the-badge)|
|Version|![GitHub Repo version](https://img.shields.io/github/v/release/{github_user_repo}?color=573E7A&amp;logo=github&amp;style=for-the-badge&sort=semver)|
|License|![GitHub License](https://img.shields.io/github/license/{github_user_repo}?style=for-the-badge)|
|View in Obsidian Hub|{obsidian_hub_link_or_text}|
|View in Moritz Jung’s Obsidian Stats|{moritz_jung_link_or_text}|

## Excerpt from README

{excerpt_from_readme}

## Features

{features_content}

## Criteria

|Criteria|Status|
|---|---|
|Dark/Light mode support|{dark_light_mode_support}|
|One or multiple colour schemes|{one_or_multiple_color_schemes}|
|Value Propositions|{value_propositions}|
|Accessibility|{accessibility_status}|
|Style Settings support|{style_settings_support}|
|Age of Theme|Released {age_of_theme}|
|Last Updated|![GitHub last commit](https://img.shields.io/github/last-commit/{github_user_repo}?color=573E7A&amp;label=last%20update&amp;logo=github&amp;style=for-the-badge)|
"""
    
    # Ensure the default base directory exists once at the start
    os.makedirs(DEFAULT_BASE_SAVE_DIR, exist_ok=True)
    print(f"All theme files will be saved within the base directory: '{DEFAULT_BASE_SAVE_DIR}'")

    while True:
        print("\n--- New Theme Entry ---")
        
        # --- 1. Get the title first to check for exit condition ---
        title = get_user_input("Enter the Theme Title: ")
        # No need for manual 'exit' check here, get_user_input handles sys.exit()

        # --- 2. Prompts for YAML Front Matter and Main Screenshot ---
        # Tags input for YAML list format
        raw_tags_input = get_user_input("Enter Tags (comma-separated, e.g., dark_theme, custom_fonts): ")
        tags_list = [tag.strip() for tag in raw_tags_input.split(',') if tag.strip()]
        # Format tags for YAML: each tag on a new line with '- ' prefix and 2-space indent
        tags_list_yaml = "\n".join([f"  - {tag}" for tag in tags_list]) if tags_list else ""

        main_screenshot_url = get_user_input("Enter URL for Main Theme Screenshot: ")

        # --- 3. Prompts for Additional Image Lines and construct combined image block ---
        main_screenshot_markdown = f"![{title} Theme Screenshot]({main_screenshot_url})"
        
        additional_image_md_lines = []
        add_more_images = get_user_input("Add more image links (e.g., ![]()) after the main screenshot? (yes/no): ").lower()
        if add_more_images == 'yes':
            print("Enter details for additional images (type 'done' for alt text when finished):")
            while True:
                alt_text = get_user_input("  Enter alt text (or 'done' to finish images): ")
                if alt_text.lower() == 'done':
                    break
                src_url = get_user_input("  Enter image URL: ")
                if src_url: # Only add if URL is provided
                    additional_image_md_lines.append(f"![{alt_text}]({src_url})")
                else:
                    print("  Image URL cannot be empty. Skipping this image.")
        
        # Combine main screenshot and additional images, ensuring proper spacing
        if additional_image_md_lines:
            # Add a single newline between main screenshot and additional images
            images_block_markdown = main_screenshot_markdown + "\n" + "\n".join(additional_image_md_lines)
        else:
            images_block_markdown = main_screenshot_markdown # Only the main screenshot


        # --- 4. Prompts for 'Info' Table ---
        repository_link = get_user_input("Enter GitHub Repository Link (e.g., https://github.com/user/repo): ")
        github_user_repo = extract_github_user_repo(repository_link) if repository_link else ""
        
        # Extract author_github_username from github_user_repo
        author_github_username = github_user_repo.split('/')[0] if github_user_repo else "N/A"

        # REMOVED: Downloads Count prompt and formatting
        # downloads_count_raw = get_user_input("Enter Downloads Count (e.g., 5587): ")
        # downloads_count_formatted = ""
        # try:
        #     downloads_count_formatted = f"{int(downloads_count_raw):_}".replace('_', ' ')
        # except ValueError:
        #     print("WARNING: Invalid number entered for Downloads Count. It will be saved as entered.")
        #     downloads_count_formatted = downloads_count_raw

        obsidian_hub_slug_input = get_user_input("Enter Obsidian Hub Slug (e.g., Charcoal - last part of URL, or type 'DNE' if page does not exist): ")
        if obsidian_hub_slug_input.lower() == 'dne':
            obsidian_hub_link_or_text = "Page does not exist"
        else:
            obsidian_hub_link_or_text = f"[{title} \\- Obsidian Hub \\- Obsidian Publish](https://publish.obsidian.md/hub/02+-+Community+Expansions/02.05+All+Community+Expansions/Themes/{obsidian_hub_slug_input})"

        moritz_jung_stats_slug_input = get_user_input("Enter Moritz Jung's Obsidian Stats Slug (e.g., charcoal - last part of URL, or type 'DNE' if page does not exist): ")
        if moritz_jung_stats_slug_input.lower() == 'dne':
            moritz_jung_link_or_text = "Page does not exist"
        else:
            moritz_jung_link_or_text = f"[{title} \\| Obsidian Stats](https://www.moritzjung.dev/obsidian-stats/themes/{moritz_jung_stats_slug_input}/)"


        # --- 5. Prompts for sections (multi-line) ---
        excerpt_from_readme = get_multiline_input("Enter Excerpt from README")
        features_content = get_multiline_input("Enter Features")

        # --- 6. Prompts for 'Criteria' Table ---
        dark_light_mode_support = get_user_input("Enter Dark/Light mode support status (e.g., Dark mode only): ")
        one_or_multiple_color_schemes = get_user_input("Enter One or multiple colour schemes (e.g., One colour scheme for dark mode): ")
        value_propositions = get_user_input("Enter Value Propositions: ")
        accessibility_status = get_user_input("Enter Accessibility status (e.g., NIL): ")
        style_settings_support = get_user_input("Enter Style Settings support (e.g., No): ")
        age_of_theme = get_user_input("Enter Age of Theme (e.g. 24 November 2020): ")

        # --- 7. Determine default save directory based on first letter of title ---
        first_letter_info = get_first_letter_info(title)
        first_letter_dir = first_letter_info['dir_name'] # e.g., 'a' or '_a'
        
        default_letter_subdir_path = os.path.join(DEFAULT_BASE_SAVE_DIR, first_letter_dir)

        sub_directory_input = get_user_input(
            f"Enter sub-directory (default: '{os.path.basename(default_letter_subdir_path)}' based on title's first letter, "
            f"or specify a full relative path like 'my-custom-folder'): " # Adjusted prompt for clarity
        ).strip()
        
        if sub_directory_input:
            # If user provides input, assume it's relative to DEFAULT_BASE_SAVE_DIR
            current_full_save_dir = os.path.join(DEFAULT_BASE_SAVE_DIR, sub_directory_input)
        else:
            # If user leaves blank, use the first-letter default
            current_full_save_dir = default_letter_subdir_path
        
        # Ensure the entire directory path exists before saving
        os.makedirs(current_full_save_dir, exist_ok=True)
        print(f"Saving to: '{current_full_save_dir}'")

        # --- 8. Generate filename in kebab-case based solely on title ---
        sanitized_title_kebab_case = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        suggested_filename = f"{sanitized_title_kebab_case}.md" 
        
        output_filename_base = get_user_input(f"Enter the filename (default: '{suggested_filename}'): ")

        if not output_filename_base:
            output_filename_base = suggested_filename
        
        if not output_filename_base.lower().endswith(".md"):
            output_filename_base += ".md"
            
        full_output_filepath = os.path.join(current_full_save_dir, output_filename_base)


        # --- 9. Fill the template with all collected and derived data ---
        try:
            final_markdown_content = markdown_template.format(
                title=title,
                tags_list_yaml=tags_list_yaml, # Use the YAML formatted tags
                images_block_markdown=images_block_markdown, # Use the combined images block
                github_user_repo=github_user_repo,
                repository_link=repository_link,
                author_github_username=author_github_username,
                # REMOVED: downloads_count_formatted=downloads_count_formatted,
                obsidian_hub_link_or_text=obsidian_hub_link_or_text,
                moritz_jung_link_or_text=moritz_jung_link_or_text,
                excerpt_from_readme=excerpt_from_readme,
                features_content=features_content,
                dark_light_mode_support=dark_light_mode_support,
                one_or_multiple_color_schemes=one_or_multiple_color_schemes,
                value_propositions=value_propositions,
                accessibility_status=accessibility_status,
                style_settings_support=style_settings_support,
                age_of_theme=age_of_theme
            )
        except KeyError as e:
            print(f"ERROR: Missing data for template placeholder: {e}. Please ensure all prompts are answered.")
            continue # Go to next iteration of the loop
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while formatting the template: {e}")
            continue

        # --- 10. Save the combined content to the specified Markdown file ---
        try:
            with open(full_output_filepath, 'w', encoding='utf-8') as f:
                f.write(final_markdown_content)
            print(f"\nSuccessfully created '{full_output_filepath}'!")
            print("--- Content Preview (first 20 lines) ---")
            print("\n".join(final_markdown_content.split('\n')[:20]))
            print("...")
            print("-----------------------")
            
            # --- IMPORTANT: Update the categories file ONLY if theme file generation was successful ---
            # Pass the original tags list to check which categories it belongs to
            update_categories_file(title, suggested_filename, tags_list) 
            
            # --- Update the global themes counter ONLY if all operations (theme file + categories) were successful ---
            get_next_counter_value() 

        except IOError as e:
            print(f"ERROR: Could not save file to '{full_output_filepath}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred during file save or counter update: {e}")

if __name__ == "__main__":
    # Ensure the directories for the counter file and categories file exist.
    os.makedirs(os.path.dirname(THEMES_INDEX_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(CATEGORIES_FILE), exist_ok=True) # Ensure docs/themes exists for categories.md
    
    create_markdown_theme_entry()
