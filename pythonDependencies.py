#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################################
# PYTHON DEPENDENCIES MANAGER
####################################################################################################################
# This tool allows:
# 1. Automatically generate a requirements.txt file based on source code imports
# 2. Verify and install necessary dependencies from a requirements.txt file
# 3. Update dependencies to their latest versions
#
# Usage:
#    python pythonDependencies.py --generate  # Generate requirements.txt
#    python pythonDependencies.py --check      # Check and install dependencies
#    python pythonDependencies.py --update     # Update dependencies
####################################################################################################################

import os
import sys
import re
import ast
import argparse
import subprocess
import importlib.util
from datetime import datetime

# Mapping of module names to package names
# This dictionary facilitates translation between the name used for importing
# and the actual package name in PyPI if they differ
MODULE_TO_PACKAGE = {
    'bs4': 'beautifulsoup4',
    'requests_oauthlib': 'requests-oauthlib',
    'flask_cors': 'Flask-Cors',
    'flask_sqlalchemy': 'Flask-SQLAlchemy',
    'flask_login': 'Flask-Login',
    'flask_wtf': 'Flask-WTF',
    'flask_migrate': 'Flask-Migrate',
    'flask_restful': 'Flask-RESTful',
    'matplotlib.pyplot': 'matplotlib',
    'sklearn': 'scikit-learn',
    'joblib': 'scikit-learn',
    'tensorflow.keras': 'tensorflow',
    'dotenv': 'python-dotenv',
    'yaml': 'pyyaml',
    'crypto': 'pycryptodome',
    'dateutil': 'python-dateutil',
    'sqlalchemy': 'SQLAlchemy',
    'psycopg2': 'psycopg2-binary',
    'telegram': 'python-telegram-bot',
    'discord': 'discord.py',
    'firebase_admin': 'firebase-admin',
    'tkinter': 'tk',
    'PIL': 'pillow',
    'cv2': 'opencv-python',
    'skimage': 'scikit-image',
    'unittest': 'unittest2',
    'docx': 'python-docx',
    'pptx': 'python-pptx',
}


class DependenciesManager:
    ####################################################################################################################
    # DEPENDENCIES MANAGER FOR PYTHON PROJECTS
    ####################################################################################################################
    
    def __init__(self, project_dir='.', requirements_file='requirements.txt'):
        self.project_dir = os.path.abspath(project_dir)
        self.requirements_file = os.path.join(self.project_dir, requirements_file)
        self.module_to_package = MODULE_TO_PACKAGE

    def extract_imports_from_file(self, file_path):
        ####################################################################################################################
        # EXTRACTS ALL IMPORTS FROM A PYTHON FILE
        ####################################################################################################################
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    tree = ast.parse(file.read(), filename=file_path)
                except SyntaxError as e:
                    print(f"Syntax error in {file_path}: {e}")
                    return set()
            
            imports = set()
            
            for node in ast.walk(tree):
                # Capture 'import x' and 'import x as y'
                if isinstance(node, ast.Import):
                    for name in node.names:
                        # Get the main module (before the first dot)
                        module_name = name.name.split('.')[0]
                        imports.add(module_name)
                
                # Capture 'from x import y' and 'from x import y as z'
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0 and node.module:  # Not a relative import
                        # Get the main module
                        module_name = node.module.split('.')[0]
                        imports.add(module_name)
            
            # Filter out any empty strings
            imports = {imp for imp in imports if imp}
            return imports
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return set()

    def is_standard_library(self, module_name):
        ####################################################################################################################
        # CHECKS IF A MODULE BELONGS TO THE PYTHON STANDARD LIBRARY
        ####################################################################################################################
        
        # First check built-in modules
        if module_name in sys.builtin_module_names:
            return True
        
        # Then check if it's a local module of the project
        if os.path.exists(os.path.join(self.project_dir, f"{module_name}.py")):
            return True
            
        if os.path.exists(os.path.join(self.project_dir, module_name)) and os.path.isdir(os.path.join(self.project_dir, module_name)):
            if os.path.exists(os.path.join(self.project_dir, module_name, "__init__.py")):
                return True
        
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return False
                
            # If it has a location
            if spec.origin:
                # If it's in the standard library
                if 'site-packages' not in spec.origin and ('lib' in spec.origin or 'lib-dynload' in spec.origin):
                    return True
                
        except (ImportError, AttributeError, ValueError):
            pass
            
        # List of modules commonly included in the standard library
        stdlib_modules = {
            'abc', 'argparse', 'array', 'ast', 'asyncio', 'base64', 'builtins', 'calendar',
            'collections', 'concurrent', 'contextlib', 'copy', 'csv', 'ctypes', 'datetime',
            'decimal', 'difflib', 'email', 'enum', 'fileinput', 'fnmatch', 'fractions',
            'functools', 'gc', 'getopt', 'getpass', 'glob', 'hashlib', 'heapq', 'hmac',
            'html', 'http', 'importlib', 'inspect', 'io', 'itertools', 'json', 'logging',
            'math', 'mimetypes', 'multiprocessing', 'netrc', 'numbers', 'operator', 'os',
            'pathlib', 'pickle', 'platform', 'pprint', 'queue', 'random', 're', 'readline',
            'reprlib', 'select', 'shlex', 'shutil', 'signal', 'socket', 'sqlite3',
            'statistics', 'string', 'struct', 'subprocess', 'sys', 'tempfile', 'threading',
            'time', 'timeit', 'tkinter', 'token', 'tokenize', 'traceback', 'typing',
            'unittest', 'urllib', 'uuid', 'venv', 'warnings', 'wave', 'weakref',
            'webbrowser', 'xml', 'xmlrpc', 'zipfile', 'zipimport', 'zlib'
        }
        
        return module_name in stdlib_modules

    def get_package_version(self, package_name):
        ####################################################################################################################
        # GETS THE VERSION OF AN INSTALLED PACKAGE USING PIP (STANDARD LIBRARY ONLY)
        ####################################################################################################################
        
        try:
            # Use pip to get package info
            result = subprocess.run(
                ['pip', 'show', package_name],
                capture_output=True, 
                text=True,
                check=False  # Don't raise exception if command fails
            )
            
            if result.returncode != 0:
                return None
                
            # Extract version from pip output
            for line in result.stdout.splitlines():
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
                    
            return None
        except Exception:
            return None
            
    def get_package_info(self, module_name):
        ####################################################################################################################
        # GETS INFORMATION ABOUT AN INSTALLED PACKAGE
        ####################################################################################################################
        
        # Adjust the module name to the package name if necessary
        package_name = self.module_to_package.get(module_name, module_name)
        
        # Try to get version using pip
        version = self.get_package_version(package_name)
        
        # If version is found, format with >=
        if version:
            return f"{package_name}>={version}"
        
        # Otherwise just return the package name
        return package_name

    def generate_requirements(self, output_file=None):
        ####################################################################################################################
        # GENERATES A REQUIREMENTS.TXT FILE BASED ON CODE IMPORTS
        ####################################################################################################################

        if output_file is None:
            output_file = self.requirements_file

        all_imports = set()

        print("Analyzing Python files to detect imports...")

        # Counter for statistics
        file_count = 0

        # Go through all .py files in the directory and subdirectories
        for root, dirs, files in os.walk(self.project_dir):
            # Ignore common directories that should not be analyzed
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', '.idea', '.vscode'}]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.project_dir)

                    # Don't analyze the dependencies script itself
                    if os.path.basename(file_path) == os.path.basename(__file__):
                        continue
                    
                    print(f"  Analyzing: {relative_path}")
                    file_imports = self.extract_imports_from_file(file_path)
                    all_imports.update(file_imports)
                    file_count += 1

        if file_count == 0:
            print(f"No Python files found to analyze in {self.project_dir}")
            return False

        # Filter standard libraries and sort
        third_party = {imp for imp in all_imports if not self.is_standard_library(imp)}

        if not third_party:
            print("No third-party libraries detected in the code.")
            return False

        print(f"\nDetected {len(third_party)} external dependencies:")

        # Get version information
        requirements = []
        not_installed_packages = []

        for module in sorted(third_party):
            # Adjust the module name to the package name if necessary
            package_name = self.module_to_package.get(module, module)

            # Try to get the version if the package is installed
            version = self.get_package_version(package_name)

            if version:
                req = f"{package_name}>={version}"
                requirements.append(req)
                print(f"  ✓ {req} (installed)")
            else:
                requirements.append(package_name)
                not_installed_packages.append(package_name)
                print(f"  ! {package_name} (not installed)")

        # Write the requirements.txt file
        with open(output_file, 'w') as f:
            f.write("# Automatically generated by pythonDependencies.py\n")
            f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Project: {os.path.basename(self.project_dir)}\n\n")

            if not_installed_packages:
                f.write("# WARNING: The following packages were detected in your code but are not installed.\n")
                f.write("# Install them and regenerate this file to include version numbers.\n")
                f.write("# You can install all dependencies with: pip install -r requirements.txt\n\n")

            for req in requirements:
                f.write(req + "\n")

        print(f"\nFile {os.path.relpath(output_file)} successfully generated.")
        print(f"It contains {len(requirements)} dependencies detected in {file_count} Python files.")

        if not_installed_packages:
            print("\nWARNING: Some packages used in your code are not installed in your environment.")
            print("These packages are included in requirements.txt but without version numbers.")
            print("After installing all dependencies, you should regenerate this file to include versions.")
            print("\nTo install all dependencies: pip install -r " + os.path.basename(output_file))

        return True

    def check_and_install_dependencies(self, auto_install=True):
        ####################################################################################################################
        # CHECKS AND INSTALLS THE DEPENDENCIES FROM THE REQUIREMENTS.TXT FILE
        ####################################################################################################################
        
        print("\n==========================================")
        print("   PYTHON DEPENDENCIES CHECKER")
        print("==========================================\n")
    
        if not os.path.exists(self.requirements_file):
            print(f"Error: File {self.requirements_file} not found.")
            print("You can generate it with the --generate option.\n")
            return False
        
        # Read requirements file
        try:
            with open(self.requirements_file, 'r') as f:
                requirements = f.readlines()
            
            # Process each line, removing comments and empty lines
            packages = []
            for req in requirements:
                # Remove comments
                req = re.sub(r'#.*$', '', req).strip()
                if req:  # Skip empty lines
                    packages.append(req)
                    
            if not packages:
                print("No dependencies found in the file.\n")
                return True
                
            print(f"Found {len(packages)} dependencies to check...")
            
            # Check each package
            missing_packages = []
            for package in packages:
                # Extract base package name (without version)
                base_package = re.split(r'[=<>~!]', package)[0].strip()
                
                # Check using pip (consistent with the rest of the script)
                version = self.get_package_version(base_package)
                
                if version:
                    print(f"✓ {base_package} is already installed (version {version})")
                else:
                    missing_packages.append(package)
            
            # If no packages are missing, end
            if not missing_packages:
                print("\n✅ All dependencies are correctly installed.")
                return True
            
            # Install missing packages if requested
            print(f"\nMissing {len(missing_packages)} dependencies: {', '.join(missing_packages)}")
            
            if not auto_install:
                print("\nYou can install them manually with:")
                print(f"pip install {' '.join(missing_packages)}")
                return False
            
            print("\nInstalling missing dependencies...")
            success = True
            for package in missing_packages:
                try:
                    print(f"Installing {package}...")
                    subprocess.check_call(["pip", "install", package])
                    print(f"✓ {package} successfully installed.")
                except subprocess.CalledProcessError:
                    print(f"✗ Error installing {package}. Try installing it manually.")
                    success = False
            
            if success:
                print("\n✅ All missing dependencies have been installed.")
                print("You should restart your application to load the new libraries.")
                return True
            else:
                print("\n⚠️ Some dependencies could not be installed.")
                return False
                
        except Exception as e:
            print(f"Error checking dependencies: {e}")
            return False
            
    def update_dependencies(self):
        ####################################################################################################################
        # UPDATES ALL DEPENDENCIES TO THEIR LATEST VERSIONS
        ####################################################################################################################
        
        print("\n==========================================")
        print("   PYTHON DEPENDENCIES UPDATER")
        print("==========================================\n")
        
        if not os.path.exists(self.requirements_file):
            print(f"Error: File {self.requirements_file} not found.")
            print("You can generate it with the --generate option.\n")
            return False
            
        try:
            # Read the requirements file
            with open(self.requirements_file, 'r') as f:
                requirements = f.readlines()
                
            # Process each line, removing comments and empty lines
            packages = []
            for req in requirements:
                req = re.sub(r'#.*$', '', req).strip()
                if req:
                    # Extract only the package name (without version)
                    package_name = re.split(r'[=<>~!]', req)[0].strip()
                    packages.append(package_name)
                    
            if not packages:
                print("No dependencies found to update.\n")
                return True
                
            print(f"Updating {len(packages)} packages to their latest versions...")
            
            # Update each package
            for package in packages:
                try:
                    print(f"Updating {package}...")
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "--upgrade", package
                    ])
                    print(f"✓ {package} successfully updated.")
                except subprocess.CalledProcessError:
                    print(f"✗ Error updating {package}.")
                    
            print("\nUpdate completed.")
            
            # Regenerate the requirements.txt file with the new versions
            regenerate = input("Do you want to update the requirements.txt file with the new versions? (y/n): ")
            if regenerate.lower() in ['y', 'yes']:
                return self.generate_requirements()
                
            return True
            
        except Exception as e:
            print(f"Error updating dependencies: {e}")
            return False


def main():
    ####################################################################################################################
    # MAIN ENTRY POINT OF THE SCRIPT
    ####################################################################################################################
    
    parser = argparse.ArgumentParser(
        description="Dependencies manager for Python projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python pythonDependencies.py --generate            # Generate requirements.txt
  python pythonDependencies.py --check               # Check and install dependencies
  python pythonDependencies.py --update              # Update dependencies
  python pythonDependencies.py --dir /path/project   # Specify directory
  python pythonDependencies.py --file req-dev.txt    # Use alternative file
        """
    )
    
    # Define arguments
    parser.add_argument('--generate', '-g', action='store_true', 
                        help='Generate a requirements.txt file based on code imports')
                        
    parser.add_argument('--check', '-c', action='store_true',
                        help='Check and install dependencies from requirements.txt')
                        
    parser.add_argument('--update', '-u', action='store_true',
                        help='Update dependencies to the latest version')
                        
    parser.add_argument('--dir', '-d', type=str, default='.',
                        help='Project directory (default: current directory)')
                        
    parser.add_argument('--file', '-f', type=str, default='requirements.txt',
                        help='Requirements file name (default: requirements.txt)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create manager instance
    manager = DependenciesManager(project_dir=args.dir, requirements_file=args.file)
    
    # No arguments, show help
    if not any([args.generate, args.check, args.update]):
        parser.print_help()
        return
    
    # Execute the corresponding function
    if args.generate:
        manager.generate_requirements()
        
    if args.check:
        manager.check_and_install_dependencies()
            
    if args.update:
        manager.update_dependencies()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(1)