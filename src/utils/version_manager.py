#!/usr/bin/env python3
"""
Version Manager for RAG Pipeline.
Handles version information, changelog management, and release operations.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VersionManager:
    """Manages version information and changelog for the RAG Pipeline."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the version manager.
        
        Args:
            project_root: Path to project root directory. If None, uses current directory.
        """
        if project_root is None:
            project_root = os.getcwd()
        
        self.project_root = Path(project_root)
        self.version_file = self.project_root / "VERSION"
        self.changelog_file = self.project_root / "CHANGELOG.md"
        
    def get_current_version(self) -> str:
        """Get the current version from VERSION file.
        
        Returns:
            Current version string (e.g., "1.0.0")
            
        Raises:
            FileNotFoundError: If VERSION file doesn't exist
            ValueError: If version format is invalid
        """
        if not self.version_file.exists():
            raise FileNotFoundError(f"VERSION file not found at {self.version_file}")
        
        version = self.version_file.read_text().strip()
        
        # Validate version format (semantic versioning)
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$', version):
            raise ValueError(f"Invalid version format: {version}")
        
        return version
    
    def set_version(self, version: str) -> None:
        """Set the version in VERSION file.
        
        Args:
            version: Version string (e.g., "1.0.0")
            
        Raises:
            ValueError: If version format is invalid
        """
        # Validate version format
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$', version):
            raise ValueError(f"Invalid version format: {version}")
        
        self.version_file.write_text(f"{version}\n")
        logger.info(f"Version set to {version}")
    
    def get_version_parts(self, version: Optional[str] = None) -> Tuple[int, int, int, str, str]:
        """Parse version into its components.
        
        Args:
            version: Version string. If None, uses current version.
            
        Returns:
            Tuple of (major, minor, patch, prerelease, build)
        """
        if version is None:
            version = self.get_current_version()
        
        # Remove build metadata for parsing
        build = ""
        if "+" in version:
            version, build = version.split("+", 1)
        
        # Remove prerelease for parsing
        prerelease = ""
        if "-" in version:
            version, prerelease = version.split("-", 1)
        
        # Parse major.minor.patch
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version}")
        
        try:
            major, minor, patch = map(int, parts)
        except ValueError:
            raise ValueError(f"Invalid version format: {version}")
        
        return major, minor, patch, prerelease, build
    
    def increment_version(self, increment_type: str, prerelease: Optional[str] = None) -> str:
        """Increment the current version.
        
        Args:
            increment_type: Type of increment ("major", "minor", "patch")
            prerelease: Optional prerelease identifier (e.g., "alpha", "beta", "rc1")
            
        Returns:
            New version string
        """
        current_version = self.get_current_version()
        major, minor, patch, _, build = self.get_version_parts(current_version)
        
        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        elif increment_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid increment type: {increment_type}")
        
        new_version = f"{major}.{minor}.{patch}"
        
        if prerelease:
            new_version += f"-{prerelease}"
        
        if build:
            new_version += f"+{build}"
        
        return new_version
    
    def get_changelog_entries(self) -> List[Dict[str, str]]:
        """Parse changelog entries.
        
        Returns:
            List of changelog entries with version, date, and content
        """
        if not self.changelog_file.exists():
            return []
        
        content = self.changelog_file.read_text()
        entries = []
        
        # Parse changelog entries
        version_pattern = r'^## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})$'
        current_entry = None
        
        for line in content.split('\n'):
            version_match = re.match(version_pattern, line)
            if version_match:
                if current_entry:
                    entries.append(current_entry)
                
                version, date = version_match.groups()
                current_entry = {
                    'version': version,
                    'date': date,
                    'content': []
                }
            elif current_entry and line.strip():
                current_entry['content'].append(line)
        
        if current_entry:
            entries.append(current_entry)
        
        return entries
    
    def add_changelog_entry(self, version: str, changes: Dict[str, List[str]], 
                           date: Optional[str] = None) -> None:
        """Add a new changelog entry.
        
        Args:
            version: Version string
            changes: Dictionary with change types as keys and lists of changes as values
            date: Date string (YYYY-MM-DD). If None, uses current date.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Create changelog entry
        entry_lines = [f"## [{version}] - {date}", ""]
        
        for change_type, change_list in changes.items():
            if change_list:
                entry_lines.append(f"### {change_type}")
                for change in change_list:
                    entry_lines.append(f"- {change}")
                entry_lines.append("")
        
        entry_text = "\n".join(entry_lines)
        
        # Read existing changelog
        if self.changelog_file.exists():
            existing_content = self.changelog_file.read_text()
            
            # Find the position to insert new entry (after the header)
            lines = existing_content.split('\n')
            insert_pos = 0
            
            for i, line in enumerate(lines):
                if line.startswith('## ['):
                    insert_pos = i
                    break
            
            # Insert new entry
            lines.insert(insert_pos, entry_text)
            new_content = '\n'.join(lines)
        else:
            # Create new changelog
            header = """# Changelog

All notable changes to the RAG Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""
            new_content = header + entry_text
        
        self.changelog_file.write_text(new_content)
        logger.info(f"Added changelog entry for version {version}")
    
    def update_pyproject_version(self, version: str) -> None:
        """Update version in pyproject.toml.
        
        Args:
            version: Version string
        """
        pyproject_file = self.project_root / "pyproject.toml"
        if not pyproject_file.exists():
            logger.warning("pyproject.toml not found, skipping version update")
            return
        
        content = pyproject_file.read_text()
        
        # Update version in [tool.poetry] or [project] section
        version_pattern = r'(version\s*=\s*["\'])([^"\']+)(["\'])'
        new_content = re.sub(version_pattern, rf'\g<1>{version}\g<3>', content)
        
        if new_content != content:
            pyproject_file.write_text(new_content)
            logger.info(f"Updated pyproject.toml version to {version}")
        else:
            logger.warning("Could not find version field in pyproject.toml")
    
    def update_setup_version(self, version: str) -> None:
        """Update version in setup.py.
        
        Args:
            version: Version string
        """
        setup_file = self.project_root / "setup.py"
        if not setup_file.exists():
            logger.warning("setup.py not found, skipping version update")
            return
        
        content = setup_file.read_text()
        
        # Update version in setup() call
        version_pattern = r'(version\s*=\s*["\'])([^"\']+)(["\'])'
        new_content = re.sub(version_pattern, rf'\g<1>{version}\g<3>', content)
        
        if new_content != content:
            setup_file.write_text(new_content)
            logger.info(f"Updated setup.py version to {version}")
        else:
            logger.warning("Could not find version field in setup.py")
    
    def create_release(self, version: str, changes: Dict[str, List[str]], 
                      update_files: bool = True) -> None:
        """Create a new release by updating version and changelog.
        
        Args:
            version: Version string
            changes: Dictionary with change types as keys and lists of changes as values
            update_files: Whether to update pyproject.toml and setup.py
        """
        # Set version
        self.set_version(version)
        
        # Add changelog entry
        self.add_changelog_entry(version, changes)
        
        # Update other files if requested
        if update_files:
            self.update_pyproject_version(version)
            self.update_setup_version(version)
        
        logger.info(f"Created release {version}")
    
    def get_version_info(self) -> Dict[str, str]:
        """Get comprehensive version information.
        
        Returns:
            Dictionary with version information
        """
        try:
            current_version = self.get_current_version()
            major, minor, patch, prerelease, build = self.get_version_parts(current_version)
            
            return {
                'version': current_version,
                'major': str(major),
                'minor': str(minor),
                'patch': str(patch),
                'prerelease': prerelease,
                'build': build,
                'is_prerelease': bool(prerelease),
                'is_build': bool(build)
            }
        except Exception as e:
            logger.error(f"Error getting version info: {e}")
            return {
                'version': 'unknown',
                'major': '0',
                'minor': '0',
                'patch': '0',
                'prerelease': '',
                'build': '',
                'is_prerelease': False,
                'is_build': False
            }


def main():
    """Command-line interface for version management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG Pipeline Version Manager")
    parser.add_argument("--project-root", help="Project root directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Get version command
    subparsers.add_parser("get", help="Get current version")
    
    # Set version command
    set_parser = subparsers.add_parser("set", help="Set version")
    set_parser.add_argument("version", help="Version to set")
    
    # Increment version command
    inc_parser = subparsers.add_parser("increment", help="Increment version")
    inc_parser.add_argument("type", choices=["major", "minor", "patch"], help="Increment type")
    inc_parser.add_argument("--prerelease", help="Prerelease identifier")
    
    # Info command
    subparsers.add_parser("info", help="Get detailed version information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    vm = VersionManager(args.project_root)
    
    try:
        if args.command == "get":
            print(vm.get_current_version())
        elif args.command == "set":
            vm.set_version(args.version)
            print(f"Version set to {args.version}")
        elif args.command == "increment":
            new_version = vm.increment_version(args.type, args.prerelease)
            vm.set_version(new_version)
            print(f"Version incremented to {new_version}")
        elif args.command == "info":
            info = vm.get_version_info()
            for key, value in info.items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
