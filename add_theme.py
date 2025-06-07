import os
import re
from datetime import datetime

# Define the path to the themes index file for the counter
THEMES_INDEX_FILE = "docs/themes/index.md"
# Define the default base directory for saving markdown files
DEFAULT_BASE_SAVE_DIR = "docs/themes"

def get_next_counter_value(counter_file_path=THEMES_INDEX_FILE):
    """
    Reads the counter from a specific Markdown file (docs/themes/index.md),
    increments it, and updates the file's content.
    Returns the *new* incremented count to be used as the article_id.
    Handles file existence and specific content format issues.
    """
    if not os.path.exists(counter_file_path):
        print(f"WARNING: Themes index file '{counter_file_path}' not found. "
              "Please ensure it exists and has the expected counter format. Assigning article_id 1.")
        # Create a dummy file with initial content for first run convenience
        os.makedirs(os.path.dirname(counter_file_path), exist_ok=True)
        with open(counter_file_path, 'w', encoding='utf-8') as f:
            f.write("""<p>
    Themes added: 0 / 344
    <progress value="0" max="344"/>
</p>""")
        print(f"Created a dummy '{counter_file_path}' with initial counter.")
        return 1 # Fallback: return 1 if file didn't exist initially

    try:
        with open(counter_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to find the 'Themes added: count / total' line
        # Groups: 1: "Themes added: ", 2: count, 3: " / ", 4: total
        text_line_regex = re.compile(r'(Themes added:\s*)(\d+)(\s*\/\s*)(\d+)', re.IGNORECASE)
        
        # Regex to find the <progress> tag
        # Groups: 1: "<progress value=\"", 2: current_value, 3: "\" max=\"", 4: max_value, 5: "\"/>"
        progress_tag_regex = re.compile(r'(<progress\s+value=")(\d+)("\s+max=")(\d+)("\s*\/?>)', re.IGNORECASE)

        text_match = text_line_regex.search(content)
        progress_match = progress_tag_regex.search(content)

        current_count = 0
        total_themes = 0

        if text_match:
            current_count = int(text_match.group(2))
            total_themes = int(text_match.group(4))
            # print(f"DEBUG: Found text counter: {current_count} / {total_themes}")
        else:
            print(f"WARNING: Could not find 'Themes added: count / total' line in '{counter_file_path}'. "
                  "Please ensure the format is correct. Assigning article_id 1.")
            return 1 # Fallback if specific text line not found

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
        print(f"ERROR: Invalid number format in counter file '{counter_file_path}'. Assigning article_id 1.")
        return 1 # Fallback if count/total are not valid integers
    except Exception as e:
        print(f"ERROR: Failed to update counter in '{counter_file_path}': {e}. Assigning article_id 1.")
        return 1 # Generic fallback for other errors

def get_multiline_input(prompt):
    """
    Prompts the user for multi-line input until an empty line is entered.
    """
    print(prompt + " (Press Enter on an empty line to finish):")
    lines = []
    while True:
        line = input()
        if not line:
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

def create_markdown_theme_entry():
    """
    Continuously creates new Markdown theme entries based on user input and a predefined template
    until the user types 'exit' for the title.
    Includes prompts for all fields in the provided theme template.
    Automatically extracts GitHub username from repository link.
    """
    print("--- Markdown Theme Generator ---")
    print("Type 'exit' for the title to quit the application.")

    # --- Define the full Markdown template ---
    # Note the change for 'tags' formatting to a YAML list
    markdown_template = """---
title: {title}
tags:
{tags_list_yaml}
---

![{title} Theme Screenshot]({main_screenshot_url})

{additional_image_lines}

## Info

|Info|Status|
|---|---|
|Repository Link|[{github_user_repo}]({repository_link})|
|Author|[{author_github_username}](https://github.com/{author_github_username})|
|Downloads|{downloads_count}|
|Last Updated|![GitHub last commit](https://img.shields.io/github/last-commit/{github_user_repo}?color=573E7A&amp;label=last%20update&amp;logo=github&amp;style=for-the-badge)|
|“Help wanted” issues|![GitHub issues by-label](https://img.shields.io/github/issues/{github_user_repo}/help%20wanted?color=573E7A&amp;logo=github&amp;style=for-the-badge)|
|Stars|![GitHub Repo stars](https://img.shields.io/github/stars/{github_user_repo}?color=573E7A&amp;logo=github&amp;style=for-the-badge)|
|Version|![GitHub Repo version](https://img.shields.io/github/v/release/{github_user_repo}?color=573E7A&amp;logo=github&amp;style=for-the-badge&sort=semver)|
|License|![GitHub License](https://img.shields.io/github/license/{github_user_repo}?style=for-the-badge)|
|View in Obsidian Hub|[View in Obsidian Hub](https://publish.obsidian.md/hub/02+-+Community+Expansions/02.05+All+Community+Expansions/Themes/{obsidian_hub_slug})|
|View in Moritz Jung’s Obsidian Stats|[View in Moritz Jung’s Obsidian Stats](https://www.moritzjung.dev/obsidian-stats/themes/{moritz_jung_stats_slug}/)|

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
|Age of Theme|{age_of_theme}|
|Last Updated|![GitHub last commit](https://img.shields.io/github/last-commit/{github_user_repo}?color=573E7A&amp;label=last%20update&amp;logo=github&amp;style=for-the-badge)|
"""
    
    # Ensure the default base directory exists once at the start
    os.makedirs(DEFAULT_BASE_SAVE_DIR, exist_ok=True)
    print(f"All theme files will be saved within the base directory: '{DEFAULT_BASE_SAVE_DIR}'")

    while True:
        print("\n--- New Theme Entry ---")
        
        # --- 1. Get the title first to check for exit condition ---
        title = input("Enter the Theme Title (or 'exit' to quit): ").strip()
        if title.lower() == 'exit':
            print("Exiting Markdown Theme Generator. Goodbye!")
            break # Exit the while loop

        # --- 2. Update and get the next article ID from the themes index counter ---
        article_id = get_next_counter_value() 
        print(f"This theme entry will be assigned ID: {article_id}")

        # --- 3. Prompts for YAML Front Matter and Main Screenshot ---
        # Tags input for YAML list format
        raw_tags_input = input("Enter Tags (comma-separated, e.g., dark_theme, custom_fonts): ").strip()
        tags_list = [tag.strip() for tag in raw_tags_input.split(',') if tag.strip()]
        # Format tags for YAML: each tag on a new line with '- ' prefix and 2-space indent
        tags_list_yaml = "\n".join([f"  - {tag}" for tag in tags_list]) if tags_list else ""

        main_screenshot_url = input("Enter URL for Main Theme Screenshot: ").strip()

        # --- 4. Prompts for Additional Image Lines ---
        additional_image_md_lines = []
        add_more_images = input("Add more image links (e.g., ![]()) after the main screenshot? (yes/no): ").strip().lower()
        if add_more_images == 'yes':
            print("Enter details for additional images (type 'done' for alt text when finished):")
            while True:
                alt_text = input("  Enter alt text (or 'done' to finish images): ").strip()
                if alt_text.lower() == 'done':
                    break
                src_url = input("  Enter image URL: ").strip()
                if src_url: # Only add if URL is provided
                    additional_image_md_lines.append(f"![{alt_text}]({src_url})")
                else:
                    print("  Image URL cannot be empty. Skipping this image.")
        
        # Join additional image lines with double newline for better markdown rendering
        additional_image_lines = "\n\n" + "\n".join(additional_image_md_lines) + "\n" if additional_image_md_lines else ""


        # --- 5. Prompts for 'Info' Table ---
        repository_link = input("Enter GitHub Repository Link (e.g., https://github.com/user/repo): ").strip()
        github_user_repo = extract_github_user_repo(repository_link) if repository_link else ""
        
        # Extract author_github_username from github_user_repo
        author_github_username = github_user_repo.split('/')[0] if github_user_repo else "N/A"

        downloads_count = input("Enter Downloads Count: ").strip()
        
        obsidian_hub_slug = input("Enter Obsidian Hub Slug (e.g., Charcoal - last part of URL): ").strip()
        moritz_jung_stats_slug = input("Enter Moritz Jung's Obsidian Stats Slug (e.g., charcoal - last part of URL): ").strip()

        # --- 6. Prompts for sections (multi-line) ---
        excerpt_from_readme = get_multiline_input("Enter Excerpt from README")
        features_content = get_multiline_input("Enter Features")

        # --- 7. Prompts for 'Criteria' Table ---
        dark_light_mode_support = input("Enter Dark/Light mode support status (e.g., Dark mode only): ").strip()
        one_or_multiple_color_schemes = input("Enter One or multiple colour schemes (e.g., One colour scheme for dark mode): ").strip()
        value_propositions = input("Enter Value Propositions: ").strip()
        accessibility_status = input("Enter Accessibility status (e.g., NIL): ").strip()
        style_settings_support = input("Enter Style Settings support (e.g., No): ").strip()
        age_of_theme = input("Enter Age of Theme (e.g., Released 24 November 2020): ").strip()

        # --- 8. Construct full save path ---
        sub_directory_input = input(f"Enter sub-directory (e.g., 'themes/my-category', leave blank for '{DEFAULT_BASE_SAVE_DIR}'): ").strip()
        
        if sub_directory_input:
            current_full_save_dir = os.path.join(DEFAULT_BASE_SAVE_DIR, sub_directory_input)
        else:
            current_full_save_dir = DEFAULT_BASE_SAVE_DIR
        
        os.makedirs(current_full_save_dir, exist_ok=True)
        print(f"Saving to: '{current_full_save_dir}'")

        # --- 9. Generate filename in kebab-case based solely on title ---
        sanitized_title_kebab_case = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        # Prepend article_id to the filename
        suggested_filename = f"{article_id:04d}-{sanitized_title_kebab_case}.md" 
        
        output_filename_base = input(f"Enter the filename (default: '{suggested_filename}'): ").strip()

        if not output_filename_base:
            output_filename_base = suggested_filename
        
        if not output_filename_base.lower().endswith(".md"):
            output_filename_base += ".md"
            
        full_output_filepath = os.path.join(current_full_save_dir, output_filename_base)


        # --- 10. Fill the template with all collected and derived data ---
        try:
            final_markdown_content = markdown_template.format(
                title=title,
                tags_list_yaml=tags_list_yaml, # Use the YAML formatted tags
                main_screenshot_url=main_screenshot_url,
                additional_image_lines=additional_image_lines,
                github_user_repo=github_user_repo,
                repository_link=repository_link,
                author_github_username=author_github_username,
                downloads_count=downloads_count,
                obsidian_hub_slug=obsidian_hub_slug,
                moritz_jung_stats_slug=moritz_jung_stats_slug,
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

        # --- 11. Save the combined content to the specified Markdown file ---
        try:
            with open(full_output_filepath, 'w', encoding='utf-8') as f:
                f.write(final_markdown_content)
            print(f"\nSuccessfully created '{full_output_filepath}'!")
            print("--- Content Preview (first 20 lines) ---")
            print("\n".join(final_markdown_content.split('\n')[:20]))
            print("...")
            print("-----------------------")
        except IOError as e:
            print(f"ERROR: Could not save file to '{full_output_filepath}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure the directory for the counter file exists.
    # get_next_counter_value will create the index.md if missing.
    os.makedirs(os.path.dirname(THEMES_INDEX_FILE), exist_ok=True)
    
    create_markdown_theme_entry()
