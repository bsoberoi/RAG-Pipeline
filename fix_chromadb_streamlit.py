#!/usr/bin/env python3
"""
Script to apply ChromaDB Streamlit Cloud compatibility fix.
This script modifies the existing app.py to work with ChromaDB on Streamlit Cloud.
"""

import os
import shutil
from pathlib import Path


def apply_chromadb_fix():
    """Apply ChromaDB compatibility fix to the existing app."""
    print("🔧 Applying ChromaDB Streamlit Cloud Fix")
    print("=" * 50)
    
    # Check if app.py exists
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ app.py not found!")
        return False
    
    # Backup original app.py
    backup_file = Path("app.py.backup")
    shutil.copy2(app_file, backup_file)
    print(f"✅ Backed up original app.py to {backup_file}")
    
    # Read the original app.py
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if fix is already applied
    if "__import__('pysqlite3')" in content:
        print("✅ ChromaDB fix already applied!")
        return True
    
    # Apply the fix by adding SQLite compatibility code at the top
    sqlite_fix = '''# Fix for ChromaDB SQLite compatibility on Streamlit Cloud
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

'''
    
    # Find the first import statement
    lines = content.split('\n')
    insert_index = 0
    
    # Find where to insert the fix (after shebang and docstring)
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_index = i
            break
    
    # Insert the fix
    lines.insert(insert_index, sqlite_fix.strip())
    
    # Write the modified content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✅ Applied ChromaDB SQLite compatibility fix")
    
    # Update requirements.txt
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            req_content = f.read()
        
        if 'pysqlite3-binary' not in req_content:
            # Add pysqlite3-binary to requirements
            with open(requirements_file, 'a') as f:
                f.write('\npysqlite3-binary\n')
            print("✅ Added pysqlite3-binary to requirements.txt")
        else:
            print("✅ pysqlite3-binary already in requirements.txt")
    
    print("\n📝 Next Steps:")
    print("1. Deploy to Streamlit Cloud using:")
    print("   - Main file: app.py")
    print("   - Requirements: requirements.txt")
    print("2. Set GROQ_API_KEY in Streamlit Cloud secrets")
    print("3. Your ChromaDB should now work on Streamlit Cloud!")
    
    return True


def revert_chromadb_fix():
    """Revert the ChromaDB fix."""
    print("🔄 Reverting ChromaDB Fix")
    print("=" * 30)
    
    # Check if backup exists
    backup_file = Path("app.py.backup")
    if not backup_file.exists():
        print("❌ No backup file found!")
        return False
    
    # Restore backup
    app_file = Path("app.py")
    shutil.copy2(backup_file, app_file)
    print("✅ Restored original app.py from backup")
    
    # Remove pysqlite3-binary from requirements if it was added
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
        
        # Remove pysqlite3-binary line
        lines = [line for line in lines if 'pysqlite3-binary' not in line]
        
        with open(requirements_file, 'w') as f:
            f.writelines(lines)
        
        print("✅ Removed pysqlite3-binary from requirements.txt")
    
    print("✅ ChromaDB fix reverted successfully")
    return True


def check_fix_status():
    """Check if the ChromaDB fix is applied."""
    print("📊 ChromaDB Fix Status")
    print("=" * 25)
    
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ app.py not found")
        return False
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for fix
    if "__import__('pysqlite3')" in content:
        print("✅ ChromaDB fix is applied")
    else:
        print("❌ ChromaDB fix is NOT applied")
    
    # Check requirements
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            req_content = f.read()
        
        if 'pysqlite3-binary' in req_content:
            print("✅ pysqlite3-binary in requirements.txt")
        else:
            print("❌ pysqlite3-binary NOT in requirements.txt")
    
    # Check backup
    backup_file = Path("app.py.backup")
    if backup_file.exists():
        print("✅ Backup file exists")
    else:
        print("❌ No backup file found")
    
    return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ChromaDB Streamlit Cloud Fix")
    parser.add_argument("--apply", action="store_true", help="Apply ChromaDB fix")
    parser.add_argument("--revert", action="store_true", help="Revert ChromaDB fix")
    parser.add_argument("--status", action="store_true", help="Check fix status")
    
    args = parser.parse_args()
    
    if args.apply:
        success = apply_chromadb_fix()
        return 0 if success else 1
    
    elif args.revert:
        success = revert_chromadb_fix()
        return 0 if success else 1
    
    elif args.status:
        success = check_fix_status()
        return 0 if success else 1
    
    else:
        print("ChromaDB Streamlit Cloud Fix Tool")
        print("=" * 35)
        print("Usage:")
        print("  python fix_chromadb_streamlit.py --apply    # Apply the fix")
        print("  python fix_chromadb_streamlit.py --revert   # Revert the fix")
        print("  python fix_chromadb_streamlit.py --status   # Check status")
        return 0


if __name__ == "__main__":
    exit(main())
