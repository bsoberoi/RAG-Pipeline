#!/usr/bin/env python3
"""
Simple version management script for RAG Pipeline.
Provides command-line interface for version operations.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.version_manager import VersionManager


def main():
    """Main entry point for version management."""
    if len(sys.argv) < 2:
        print("RAG Pipeline Version Manager")
        print("Usage: python version.py <command> [options]")
        print("\nCommands:")
        print("  get                    - Get current version")
        print("  set <version>          - Set version")
        print("  increment <type>       - Increment version (major|minor|patch)")
        print("  info                   - Get detailed version information")
        print("  changelog              - Show recent changelog entries")
        print("\nExamples:")
        print("  python version.py get")
        print("  python version.py set 1.2.0")
        print("  python version.py increment minor")
        print("  python version.py info")
        return 0
    
    command = sys.argv[1].lower()
    vm = VersionManager()
    
    try:
        if command == "get":
            version = vm.get_current_version()
            print(f"Current version: {version}")
            
        elif command == "set":
            if len(sys.argv) < 3:
                print("Error: Version required for 'set' command")
                print("Usage: python version.py set <version>")
                return 1
            
            version = sys.argv[2]
            vm.set_version(version)
            print(f"Version set to: {version}")
            
        elif command == "increment":
            if len(sys.argv) < 3:
                print("Error: Increment type required")
                print("Usage: python version.py increment <major|minor|patch>")
                return 1
            
            increment_type = sys.argv[2].lower()
            if increment_type not in ["major", "minor", "patch"]:
                print("Error: Invalid increment type. Use 'major', 'minor', or 'patch'")
                return 1
            
            new_version = vm.increment_version(increment_type)
            vm.set_version(new_version)
            print(f"Version incremented to: {new_version}")
            
        elif command == "info":
            info = vm.get_version_info()
            print("Version Information:")
            print(f"  Version: {info['version']}")
            print(f"  Major: {info['major']}")
            print(f"  Minor: {info['minor']}")
            print(f"  Patch: {info['patch']}")
            if info['prerelease']:
                print(f"  Prerelease: {info['prerelease']}")
            if info['build']:
                print(f"  Build: {info['build']}")
            print(f"  Is Prerelease: {info['is_prerelease']}")
            print(f"  Is Build: {info['is_build']}")
            
        elif command == "changelog":
            entries = vm.get_changelog_entries()
            if not entries:
                print("No changelog entries found.")
                return 0
            
            print("Recent Changelog Entries:")
            print("=" * 50)
            
            for entry in entries[:5]:  # Show last 5 entries
                print(f"\nVersion: {entry['version']}")
                print(f"Date: {entry['date']}")
                print("-" * 30)
                
                # Show first few lines of content
                content_lines = [line for line in entry['content'] if line.strip()]
                for line in content_lines[:10]:  # Show first 10 lines
                    if line.startswith('###'):
                        print(f"\n{line}")
                    elif line.startswith('-'):
                        print(f"  {line}")
                    else:
                        print(line)
                
                if len(content_lines) > 10:
                    print("  ... (truncated)")
                print()
                
        else:
            print(f"Error: Unknown command '{command}'")
            print("Run 'python version.py' for usage information.")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
