#!/usr/bin/env python3
import os
import re
import sys
import yaml
from datetime import datetime

# Configuration
MKDOCS_CONFIG = "mkdocs.yml"
THEMES_INDEX_FILE = "docs/themes/index.md"
CATEGORIES_FILE = "docs/themes/categories.md"
DEFAULT_BASE_SAVE_DIR = "docs/themes"

CATEGORY_MAPPING = {
    "underrated_gems": "## Underrated Gems",
    "old_but_gold": "## Old but Gold",
    "new_and_upcoming": "## New and Upcoming",
}

def load_allowed_tags():
    try:
        with open(MKDOCS_CONFIG, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            tags_dict = config.get('theme', {}).get('extra', {}).get('tags', {})
            return list(tags_dict.values())
    except Exception:
        return []

def get_base_input(prompt, required=True):
    """The core input handler for navigation, exiting, and Ctrl+C."""
    try:
        val = input(f"{prompt} (type 'back' to go up, 'exit' to quit): ").strip()
    except KeyboardInterrupt:
        print("\n\n[Interrupted] Keyboard interrupt detected. Exiting...")
        sys.exit(0)
        
    if val.lower() == 'exit':
        print("Exiting...")
        sys.exit(0)
    if val.lower() == 'back':
        return "BACK_SIGNAL"
    if required and not val:
        print(">> This field is required.")
        return get_base_input(prompt, required)
    return val

def get_tag_input(prompt, allowed_list):
    """Special handler for multiple tags with validation against the allow-list."""
    print(f"\n--- Available Tags ---")
    print(", ".join(allowed_list))
    
    val = get_base_input(prompt)
    if val == "BACK_SIGNAL": return val
    
    # Split by comma and clean
    user_tags = [t.strip() for t in val.split(',') if t.strip()]
    valid_tags = [t for t in user_tags if t in allowed_list]
    invalid_tags = [t for t in user_tags if t not in allowed_list]
    
    if invalid_tags:
        print(f">> Warning: Ignored invalid tags: {', '.join(invalid_tags)}")
    
    if not valid_tags:
        print(">> Error: You must provide at least one valid tag from the list.")
        return get_tag_input(prompt, allowed_list)
    
    print(f">> Accepted Tags: {', '.join(valid_tags)}")
    return ",".join(valid_tags) # Store as comma-sep string for the data dict

def get_choice(prompt, options, allow_custom=False):
    print(f"\n--- Select {prompt} ---")
    for idx, opt in enumerate(options, 1):
        print(f"  [{idx}] {opt}")
    if allow_custom:
        print(f"  [+] Or type your own arbitrary text")
    
    val = get_base_input("Selection")
    if val == "BACK_SIGNAL": return val
    
    if val.isdigit():
        choice_idx = int(val) - 1
        if 0 <= choice_idx < len(options):
            return options[choice_idx]
    
    if val in options:
        return val

    if allow_custom and val:
        return val
    
    print(f">> Invalid choice. Please enter a number 1-{len(options)} or the exact text.")
    return get_choice(prompt, options, allow_custom)

def get_multiline(prompt):
    print(f"\n{prompt} (Press Enter on empty line to finish, type 'back' on a new line to go up):")
    lines = []
    while True:
        line = input("> ").strip()
        if line.lower() == 'back': return "BACK_SIGNAL"
        if not line: break
        lines.append(line)
    return "\n".join(lines)

def get_validated_date(prompt):
    while True:
        val = get_base_input(prompt)
        if val == "BACK_SIGNAL": return val
        try:
            datetime.strptime(val, "%d %B %Y")
            return val
        except ValueError:
            print(">> Error: Invalid format. Use 'DD MMMM YYYY' (e.g., 01 January 2024).")

def get_first_letter_info(title):
    char = title.strip()[0].lower()
    if not char.isalpha(): return {'link_char': '$<a$', 'dir_name': '_a'}
    return {'link_char': f'${char}$', 'dir_name': char}

def update_categories(title, filename, tags):
    if not os.path.exists(CATEGORIES_FILE): return
    info = get_first_letter_info(title)
    rel_path = f"./{info['dir_name']}/{filename}"
    new_row = f"|{info['link_char']}|[{title}]({rel_path})|"
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated_content, current_cat, section_buffer = [], None, []
    def flush(b): return sorted(b, key=lambda x: x.split('|')[2].lower())
    
    for line in lines:
        clean = line.strip()
        header = next((h for h in CATEGORY_MAPPING.values() if clean == h), None)
        if header:
            if current_cat and section_buffer: updated_content.extend(flush(section_buffer))
            section_buffer = []; updated_content.append(line)
            current_cat = next(k for k, v in CATEGORY_MAPPING.items() if v == header)
        elif current_cat and clean.startswith('|') and 'Letter' not in clean and '---' not in clean:
            section_buffer.append(line)
        else:
            if section_buffer:
                if current_cat in tags: section_buffer.append(new_row + "\n")
                updated_content.extend(flush(section_buffer)); section_buffer = []
            updated_content.append(line)
            if header is None: current_cat = None
    
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        f.writelines(updated_content)

def update_counter():
    if not os.path.exists(THEMES_INDEX_FILE): return
    with open(THEMES_INDEX_FILE, 'r+', encoding='utf-8') as f:
        content = f.read()
        repl = lambda m: f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}"
        content = re.sub(r'(Themes added:\s*)(\d+)(\s*\/)', repl, content)
        content = re.sub(r'(value=")(\d+)(")', repl, content)
        f.seek(0); f.write(content); f.truncate()

def main():
    print("--- Welcome to ObsiThemeRef's Theme Helper --- ")
    allowed_tags = load_allowed_tags()
    data = {}
    
    # Structure: (key, function, label, extra_arg)
    questions = [
        ('title', get_base_input, "Theme Title", None),
        ('tags_list', get_tag_input, "Enter Tags (comma-separated)", allowed_tags),
        ('main_screenshot', get_base_input, "Main Screenshot URL", None),
        ('repo_url', get_base_input, "GitHub Repository URL", None),
        ('hub_slug', get_base_input, "Obsidian Hub Slug (or DNE)", None),
        ('stats_slug', get_base_input, "Moritz Jung Stats Slug (or DNE)", None),
        ('readme_excerpt', get_multiline, "Excerpt from README", None),
        ('features', get_multiline, "Features", None),
        ('dm_support', get_choice, "Dark/Light Mode", ["Dark mode only", "Light mode only", "Both light and dark mode supported"]),
        ('color_schemes', get_choice, "Color Schemes", ["One colour scheme for dark mode", "One colour scheme for light mode", "One colour scheme for light and dark mode", "Multiple colour schemes for light and dark mode"]),
        ('value_props', get_base_input, "Value Propositions", None),
        ('acc', get_choice, "Accessibility", (["NIL", "Yes"], True)), # Tuple for multi-arg choice
        ('style_support', get_choice, "Style Settings support", (["No", "Yes"], True)),
        ('age', get_validated_date, "Age of Theme (Released date)", None),
    ]

    i = 0
    while i < len(questions):
        key, func, label, extra = questions[i]
        
        if func == get_choice:
            if isinstance(extra, tuple): # for Accessibility custom
                result = func(label, extra[0], extra[1])
            else:
                result = func(label, extra)
        elif func == get_tag_input:
            result = func(label, extra)
        else:
            result = func(label)
        
        if result == "BACK_SIGNAL":
            if i == 0:
                confirm = input("Already at start. Exit script? (y/n): ").lower()
                if confirm == 'y': sys.exit(0)
                continue
            print("\n" + "—" * 40 + f"\n  ↩ Returning to: {questions[i-1][2]}\n" + "—" * 40 + "\n")
            i -= 1
            continue
        
        data[key] = result
        i += 1

    # Post-processing
    final_tags = data['tags_list'].split(',')
    repo_slug = re.search(r'github\.com/([^/]+/[^/]+)', data['repo_url']).group(1)
    author = repo_slug.split('/')[0]
    
    hub_link = "Page does not exist" if data['hub_slug'].lower() == 'dne' else f"[{data['title']} \\- Obsidian Hub](https://publish.obsidian.md/hub/02+-+Community+Expansions/02.05+All+Community+Expansions/Themes/{data['hub_slug']})"
    stats_link = "Page does not exist" if data['stats_slug'].lower() == 'dne' else f"[{data['title']} \\| Obsidian Stats](https://www.moritzjung.dev/obsidian-stats/themes/{data['stats_slug']}/)"

    markdown_template = f"""---
title: {data['title']}
tags:
{chr(10).join(f"  - {t}" for t in final_tags)}
---

![{data['title']} Theme Screenshot]({data['main_screenshot']})

## Info

|Info|Status|
|---|---|
|Repository Link|[{repo_slug}]({data['repo_url']})|
|Author|[{author}](https://github.com/{author})|
|Last Updated|![GitHub last commit](https://img.shields.io/github/last-commit/{repo_slug}?color=573E7A&amp;label=last%20update&amp;logo=github&amp;style=for-the-badge)|
|“Help wanted” issues|![GitHub issues by-label](https://img.shields.io/github/issues/{repo_slug}/help%20wanted?color=573E7A&amp;logo=github&amp;style=for-the-badge)|
|Stars|![GitHub Repo stars](https://img.shields.io/github/stars/{repo_slug}?color=573E7A&amp;logo=github&amp;style=for-the-badge)|
|Version|![GitHub Repo version](https://img.shields.io/github/v/release/{repo_slug}?color=573E7A&amp;logo=github&amp;style=for-the-badge&sort=semver)|
|License|![GitHub License](https://img.shields.io/github/license/{repo_slug}?style=for-the-badge)|
|View in Obsidian Hub|{hub_link}|
|View in Moritz Jung’s Obsidian Stats|{stats_link}|

## Excerpt from README

{data['readme_excerpt']}

## Features

{data['features']}

## Criteria

|Criteria|Status|
|---|---|
|Dark/Light mode support|{data['dm_support']}|
|One or multiple colour schemes|{data['color_schemes']}|
|Value Propositions|{data['value_props']}|
|Accessibility|{data['acc']}|
|Style Settings support|{data['style_support']}|
|Age of Theme|Released {data['age']}|
|Last Updated|![GitHub last commit](https://img.shields.io/github/last-commit/{repo_slug}?color=573E7A&amp;label=last%20update&amp;logo=github&amp;style=for-the-badge)|
"""

    info = get_first_letter_info(data['title'])
    filename = f"{re.sub(r'[^a-z0-9]+', '-', data['title'].lower()).strip('-')}.md"
    save_path = os.path.join(DEFAULT_BASE_SAVE_DIR, info['dir_name'], filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(markdown_template)

    update_categories(data['title'], filename, final_tags)
    update_counter()
    print(f"\nSUCCESS: Created {save_path} and updated indices.")

if __name__ == "__main__":
    main()
