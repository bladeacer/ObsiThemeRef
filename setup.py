#!/usr/bin/env python3
# This shebang line ensures the script is executable directly on Linux/macOS systems.

import os
import subprocess
import sys
import shutil
import platform # To detect the operating system

def rel2abspath(path):
    """Converts a relative path to an absolute path based on the script's directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

def create_and_install_venv(venv_name=".venv", requirements_file="requirements.txt"):
    """
    Creates a Python virtual environment named .venv and installs dependencies
    from requirements.txt into it.
    This function is designed to be cross-platform (Windows, Linux, macOS).
    """
    print("--- Starting Python Virtual Environment Setup ---")

    # Define the path for the virtual environment
    venv_path = rel2abspath(venv_name)

    # Step 1: Remove existing virtual environment if it exists for a clean setup
    if os.path.exists(venv_path):
        print(f"Removing existing virtual environment at: {venv_path}")
        try:
            shutil.rmtree(venv_path)
            print("Existing virtual environment removed successfully.")
        except OSError as e:
            print(f"Error removing virtual environment '{venv_path}': {e}")
            sys.exit(1)

    # Step 2: Create a new Python virtual environment
    print(f"Creating new virtual environment at: {venv_path}")
    try:
        # Use sys.executable to ensure the venv is created with the same Python interpreter
        # that is running this setup.py script.
        subprocess.run(
            [sys.executable, "-m", "venv", venv_path],
            check=True,
            stdout=sys.stdout, # Direct output of venv creation to console
            stderr=sys.stderr, # Direct errors of venv creation to console
        )
        print("Virtual environment created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create virtual environment: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during venv creation: {e}")
        sys.exit(1)

    # Step 3: Determine pip executable path within the new venv
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
    else: # Linux, macOS, and other Unix-like systems
        pip_path = os.path.join(venv_path, "bin", "pip")

    # Step 4: Install Python dependencies from requirements.txt into the new venv
    requirements_file_abs_path = rel2abspath(requirements_file)
    if os.path.exists(requirements_file_abs_path):
        print(f"Installing Python dependencies from '{requirements_file_abs_path}' into '{venv_path}'...")
        try:
            # Add --default-timeout for potentially unstable internet connections
            subprocess.run(
                [pip_path, "install", "--default-timeout=600", "-r", requirements_file_abs_path],
                check=True,
                stdout=sys.stdout, # Direct output of pip install to console
                stderr=sys.stderr, # Direct errors of pip install to console
            )
            print("Dependencies from requirements.txt installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies from requirements.txt: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Pip executable not found at '{pip_path}'. "
                         "This indicates an issue with virtual environment creation or Python setup.")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during pip install: {e}")
            sys.exit(1)
    else:
        print(
            f"Warning: '{requirements_file_abs_path}' not found. "
            "Skipping standard Python dependency installation."
        )

    print("\n--- Python Virtual Environment Setup Complete ---")
    # Provide activation instructions for the user
    if platform.system() == "Windows":
        activate_command = f"call {os.path.join(venv_path, 'Scripts', 'activate.bat')}"
    else:
        activate_command = f"source {os.path.join(venv_path, 'bin', 'activate')}"
    print(f"\nTo activate the virtual environment for your session, run:")
    print(f"  {activate_command}")
    print(f"Then you can run your Python scripts using 'python your_script.py'.")


if __name__ == "__main__":
    # For demonstration, create a dummy requirements.txt if it doesn't exist
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("requests\n")
            f.write("beautifulsoup4\n")
        print("Created a dummy requirements.txt for demonstration purposes (requests, beautifulsoup4).")

    create_and_install_venv()

