import re
import os

def replace_img_tags_recursive(folder_path="docs"):
    """
    Recursively replaces all <img alt="..." src="..."> tags with Markdown ![]() syntax
    within all text files (.md, .txt, etc.) in the specified folder (defaults to 'docs')
    and its subdirectories.
    """
    img_regex = re.compile(r'<img\s+alt="([^"]*)"\s+src="([^"]*)"[^>]*>', re.IGNORECASE)

    if not os.path.isdir(folder_path):
        print(f"Error: The directory '{folder_path}' does not exist.")
        return

    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(('.md', '.txt')):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    def replace(match):
                        alt_text = match.group(1)
                        src_url = match.group(2)
                        return f'![{alt_text}]({src_url})'

                    modified_content = img_regex.sub(replace, content)

                    if modified_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        print(f"Replaced img tags in: {filepath}")
                    else:
                        print(f"No img tags found in: {filepath}")

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    folder_to_process = input("Enter the path to the folder containing the files (defaults to 'docs'): ")
    if not folder_to_process:
        folder_to_process = "docs"

    if os.path.isdir(folder_to_process):
        replace_img_tags_recursive(folder_to_process)
    else:
        print("Invalid folder path.")
