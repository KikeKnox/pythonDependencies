# Python Dependencies Manager

A lightweight, dependency-free tool to automatically generate, check, and update Python project dependencies.

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Automatic Detection**: Scans your code to identify all third-party dependencies
- **Smart Recognition**: Handles cases where import names differ from PyPI package names
- **Version Detection**: Includes installed package versions in requirements.txt
- **Dependency Verification**: Checks if all dependencies are installed
- **One-Click Installation**: Installs missing dependencies automatically
- **Update Management**: Updates all dependencies to their latest versions
- **Zero External Dependencies**: Uses only the Python standard library

## Installation

Just download the `pythonDependencies.py` file and place it in your project

## Usage

### Generate requirements.txt

Automatically scan your project and create a requirements.txt file with all third-party dependencies:

```bash
python pythonDependencies.py --generate
```

### Check and Install Dependencies

Verify all dependencies from requirements.txt are installed, and optionally install missing ones:

```bash
python pythonDependencies.py --check
```

### Update Dependencies

Update all your dependencies to their latest versions:

```bash
python pythonDependencies.py --update
```

## Advanced Options

```
usage: pythonDependencies.py [-h] [--generate] [--check] [--update] [--dir DIR] [--file FILE]

Dependencies manager for Python projects

options:
  -h, --help            show this help message and exit
  --generate, -g        Generate a requirements.txt file based on code imports
  --check, -c           Check and install dependencies from requirements.txt
  --file FILE, -f FILE  Requirements file name (default: requirements.txt)
  --dir DIR, -d DIR     Project directory (default: current directory)
  --update, -u          Update dependencies to the latest version

Usage examples:
  python pythonDependencies.py --generate            # Generate requirements.txt
  python pythonDependencies.py --check               # Check and install dependencies
  python pythonDependencies.py --update              # Update dependencies
  python pythonDependencies.py --dir /path/project   # Specify directory
  python pythonDependencies.py --file req-dev.txt    # Use alternative file
```

## How It Works

1. **Import Detection**: The script scans all Python files in your project and extracts import statements
2. **Filtering**: Standard library imports are automatically filtered out
3. **Mapping**: Special handling for modules where the import name differs from the PyPI package name
4. **Version Detection**: For installed packages, the current version is detected and included
5. **Requirements Generation**: Creates a properly formatted requirements.txt file

## Special Module Mapping

The script includes a comprehensive mapping between import names and their corresponding PyPI package names. For example:

- `bs4` → `beautifulsoup4`
- `PIL` → `pillow`
- `cv2` → `opencv-python`
- `dotenv` → `python-dotenv`

This ensures accurate requirements.txt generation regardless of how modules are imported in your code.

## Compatibility

- Python 3.6 and above
- Works on Windows, macOS and Linux
- No external dependencies required

## Use Cases

- **New Project Setup**: Quickly set up dependency management for new projects
- **Legacy Project Maintenance**: Identify and document dependencies in older projects
- **Environment Replication**: Easily replicate your development environment on other systems
- **CI/CD Integration**: Ensure all dependencies are properly documented and versioned

## License

This project is licensed under the MIT License.