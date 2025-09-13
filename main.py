#!/usr/bin/env python3
"""
Enhanced CLI interface for the RAG Pipeline.
Provides a comprehensive command-line interface for document ingestion, querying, and management.
"""

import os
import sys
import argparse
import time
from pathlib import Path
from typing import Optional, List
from src.utils.init_manager import init_logging_and_config
from src.utils.version_manager import VersionManager

# Initialize logging and config before any other imports
config, log_level = init_logging_and_config()

# Get version information
try:
    vm = VersionManager()
    version_info = vm.get_version_info()
except Exception:
    version_info = {'version': 'unknown'}

from src.rag_pipeline import RAGPipeline


class RAGCLIApp:
    """Command-line interface for the RAG Pipeline application."""
    
    def __init__(self):
        """Initialize the CLI application."""
        self.rag: Optional[RAGPipeline] = None
        self.vector_db = None  # For lightweight vector DB access
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands and options."""
        parser = argparse.ArgumentParser(
            description=f"🧠 RAG Pipeline - Retrieval-Augmented Generation System (v{version_info['version']})",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  main.py init                           # Initialize and test the pipeline
  main.py ingest -d ./docs               # Ingest documents from directory
  main.py ingest -f document.pdf         # Ingest single file
  main.py query \"What is machine learning?\"  # Query the system
  main.py interactive                    # Start interactive mode
  main.py stats                          # Show database statistics
  main.py clear                          # Clear all documents from database
  main.py list                           # List supported file formats and current configuration
  main.py logs                           # Manage log files (see 'main.py logs --help' for more)

🚪 Stuck in PowerShell continuation mode (>> prompt)?
  This happens with mismatched quotes like: main.py query 'Hello"
  
  Exit methods:
  • Complete the quote: >>  '
  • Force exit: Press Ctrl+C
  • Stop parsing: >>  --

Interactive Mode Exit:
  • Type: /quit
  • Press: Ctrl+C
            """
        )
        
        # Global options
        parser.add_argument(
            '--config', '-c',
            type=str,
            help='Path to configuration file (default: config/config.yaml)'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Init command
        init_parser = subparsers.add_parser('init', help='Initialize and test the RAG pipeline',
            epilog="""
Examples:
  python main.py init
  python main.py init --no-test
  python main.py init --config custom_config.yaml
"""
        )
        init_parser.add_argument(
            '--no-test', 
            action='store_true',
            help='Skip running test query'
        )
        
        # Ingest command
        ingest_parser = subparsers.add_parser('ingest', help='Ingest documents into the system',
            epilog="""
Examples:
  python main.py ingest --directory ./docs
  python main.py ingest --file document.pdf
  python main.py ingest --directory ./docs --recursive
  python main.py ingest --directory ./docs --config custom_config.yaml
"""
        )
        ingest_group = ingest_parser.add_mutually_exclusive_group(required=True)
        ingest_group.add_argument(
            '--directory', '-d',
            type=str,
            help='Directory containing documents to ingest'
        )
        ingest_group.add_argument(
            '--file', '-f',
            type=str,
            help='Single file to ingest'
        )
        ingest_parser.add_argument(
            '--recursive', '-r',
            action='store_true',
            help='Recursively search subdirectories'
        )
        
        # Query command
        query_parser = subparsers.add_parser('query', help='Query the RAG system',
            epilog="""
Examples:
  python main.py query "What is machine learning?"
  python main.py query "Explain deep learning" --max-results 10
  python main.py query "What is AI?" --config custom_config.yaml
"""
        )
        query_parser.add_argument(
            'question',
            type=str,
            help='Question to ask the system'
        )
        query_parser.add_argument(
            '--max-results', '-n',
            type=int,
            default=5,
            help='Maximum number of source documents to retrieve (default: 5)'
        )
        
        # Interactive command
        subparsers.add_parser('interactive', help='Start interactive query mode',
            epilog="""
Examples:
  python main.py interactive
  python main.py interactive --config custom_config.yaml
"""
        )
        
        # Stats command
        subparsers.add_parser('stats', help='Show database statistics',
            epilog="""
Examples:
  python main.py stats
  python main.py stats --config custom_config.yaml
"""
        )
        
        # Clear command
        clear_parser = subparsers.add_parser('clear', help='Clear all documents from database',
            epilog="""
Examples:
  python main.py clear
  python main.py clear --confirm
  python main.py clear --config custom_config.yaml
"""
        )
        clear_parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt'
        )
        
        # List command
        subparsers.add_parser('list', help='List supported file formats and current configuration',
            epilog="""
Examples:
  python main.py list
"""
        )
        
        # Logs command
        logs_parser = subparsers.add_parser('logs', help='Manage log files',
            epilog="""
Examples:
  python main.py logs --list
  python main.py logs --cleanup
  python main.py logs --cleanup --keep 3
  python main.py logs --cleanup --keep 1
  python main.py logs --view log_YYYYMMDD_HHMM.log
  python main.py logs --view log_YYYYMMDD_HHMM.log --tail --lines 100
"""
        )
        logs_group = logs_parser.add_mutually_exclusive_group()
        logs_group.add_argument(
            '--list', '-l',
            action='store_true',
            help='List all log files'
        )
        logs_group.add_argument(
            '--view', '-v',
            type=str,
            metavar='FILENAME',
            help='View contents of a specific log file'
        )
        logs_group.add_argument(
            '--cleanup', '-c',
            action='store_true',
            help='Clean up old log files, keeping only the latest 5'
        )
        logs_parser.add_argument(
            '--keep',
            type=int,
            default=5,
            help='Number of files to keep during cleanup (default: 5)'
        )
        logs_parser.add_argument(
            '--lines',
            type=int,
            default=50,
            help='Number of lines to show when viewing (default: 50)'
        )
        logs_parser.add_argument(
            '--tail',
            action='store_true',
            help='Show lines from the end of the file (like tail command)'
        )
        
        return parser
    
    def _initialize_rag(self, config_path: Optional[str] = None) -> bool:
        """Initialize the RAG pipeline."""
        try:
            print("🚀 Initializing RAG Pipeline...")
            if config_path:
                self.rag = RAGPipeline(config_path)
            else:
                self.rag = RAGPipeline()
            print("✅ RAG Pipeline initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize RAG Pipeline: {e}")
            print("💡 Make sure all dependencies are installed and GROQ_API_KEY is set")
            return False
    
    def _initialize_vector_db_only(self, config_path: Optional[str] = None) -> bool:
        """Initialize only the vector database for lightweight operations."""
        try:
            print("🔍 Connecting to vector database...")
            
            # Import required modules for vector DB only
            from src.utils.config_loader import ConfigLoader
            from src.vector_db import create_vector_db
            
            # Load config
            if not config_path:
                # Get the current working directory where main.py is located
                config_path = os.path.join(os.getcwd(), "config", "config.yaml")
            
            config = ConfigLoader(config_path)
            vector_db_config = config.get_vector_db_config()
            
            # Initialize vector database using factory
            self.vector_db = create_vector_db(vector_db_config)
            
            print("✅ Vector database connected!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to vector database: {e}")
            return False
    
    def _suppress_console_logging(self) -> None:
        """Temporarily suppress console logging to reduce clutter during interactive queries."""
        import logging
        
        # Store the original handlers from the root logger
        root_logger = logging.getLogger()
        self._original_handlers = root_logger.handlers.copy()
        
        # Remove only StreamHandlers (console output), keep FileHandlers
        for handler in root_logger.handlers.copy():
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
    
    def _restore_console_logging(self) -> None:
        """Restore console logging after interactive query."""
        import logging
        
        if hasattr(self, '_original_handlers'):
            root_logger = logging.getLogger()
            # Clear current handlers and restore original ones
            root_logger.handlers.clear()
            root_logger.handlers.extend(self._original_handlers)
            
            # Clean up the stored handlers
            delattr(self, '_original_handlers')
    
    def _print_stats(self) -> None:
        """Print current database statistics."""
        # Check if we have full RAG pipeline or just vector DB
        if hasattr(self, 'rag') and self.rag:
            stats = self.rag.get_collection_stats()
        elif hasattr(self, 'vector_db') and self.vector_db:
            # Use lightweight vector DB directly
            stats = {
                'total_documents': self.vector_db.count(),
                'collection_name': self.vector_db.name
            }
        else:
            print("❌ Database not initialized")
            return
        
        print("\n📊 Database Statistics:")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Collection name: {stats['collection_name']}")
        
        if stats['total_documents'] == 0:
            print("   💡 No documents found. Use 'ingest' command to add documents.")
    
    def cmd_init(self, args) -> None:
        """Handle the init command."""
        if not self._initialize_rag(args.config):
            return
        
        self._print_stats()
        
        # Check for documents in default location
        raw_data_path = Path("data/raw")
        if raw_data_path.exists() and any(raw_data_path.iterdir()):
            print(f"\n📁 Found documents in {raw_data_path}")
            if not args.no_test:
                response = input("Would you like to ingest them? (y/N): ")
                if response.lower() in ['y', 'yes']:
                    self.rag.ingest_directory(str(raw_data_path))
                    self._print_stats()
        
        if not args.no_test and self.rag.get_collection_stats()['total_documents'] > 0:
            print("\n🔍 Running test query...")
            result = self.rag.query("What is the main topic discussed in the documents?")
            print(f"Question: {result['question']}")
            print(f"Response: {result['response']}")
            print(f"Sources used: {result['num_sources']}")
    
    def cmd_ingest(self, args) -> None:
        """Handle the ingest command."""
        if not self._initialize_rag(args.config):
            return
        
        start_time = time.time()
        
        try:
            if args.directory:
                path = Path(args.directory)
                if not path.exists():
                    print(f"❌ Directory not found: {args.directory}")
                    return
                
                print(f"📚 Ingesting documents from: {path}")
                self.rag.ingest_directory(str(path))
                
            elif args.file:
                path = Path(args.file)
                if not path.exists():
                    print(f"❌ File not found: {args.file}")
                    return
                
                print(f"📄 Ingesting file: {path}")
                self.rag.ingest_document(str(path))
            
            elapsed = time.time() - start_time
            print(f"✅ Ingestion completed in {elapsed:.2f} seconds")
            self._print_stats()
            
        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
    
    def cmd_query(self, args) -> None:
        """Handle the query command."""
        if not self._initialize_rag(args.config):
            return
        
        stats = self.rag.get_collection_stats()
        if stats['total_documents'] == 0:
            print("❌ No documents in database. Use 'ingest' command first.")
            return
        
        print(f"❓ Querying: {args.question}")
        print("🔍 Searching...")
        
        try:
            # Temporarily suppress console logging during query for cleaner output
            self._suppress_console_logging()
            try:
                result = self.rag.query(args.question)
            finally:
                self._restore_console_logging()
            
            print(f"\n💬 Response:")
            print(f"   {result['response']}")
            print(f"\n📚 Sources used: {result['num_sources']}")
            
            if args.verbose and result['retrieved_documents']:
                print("\n📄 Source details:")
                for i, doc in enumerate(result['retrieved_documents'][:3], 1):
                    print(f"   {i}. {doc['metadata'].get('filename', 'Unknown')}")
                    if 'distance' in doc and doc['distance'] is not None:
                        print(f"      Relevance: {1 - doc['distance']:.3f}")
                        
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    def cmd_interactive(self, args) -> None:
        """Handle the interactive command."""
        if not self._initialize_rag(args.config):
            return
        
        stats = self.rag.get_collection_stats()
        if stats['total_documents'] == 0:
            print("❌ No documents in database. Use 'ingest' command first.")
            return
        
        print("🎯 Interactive Query Mode")
        print("Type your questions below. Commands:")
        print("   /stats  - Show database statistics")
        print("   /quit   - Exit interactive mode")
        print("   /help   - Show this help")
        print()
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if not question:
                    continue
                
                if question == "/quit":
                    print("👋 Goodbye!")
                    break
                elif question == "/stats":
                    self._print_stats()
                    continue
                elif question == "/help":
                    print("Commands: /stats, /quit, /help")
                    continue
                elif question.startswith("/"):
                    print("❌ Unknown command. Type /help for available commands.")
                    continue
                
                print("🔍 Searching...")
                
                # Temporarily suppress console logging during query
                self._suppress_console_logging()
                try:
                    result = self.rag.query(question)
                finally:
                    self._restore_console_logging()
                
                print(f"\n💬 {result['response']}")
                print(f"📚 ({result['num_sources']} sources)\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def cmd_stats(self, args) -> None:
        """Handle the stats command."""
        if not self._initialize_vector_db_only(args.config):
            return
        
        self._print_stats()
    
    def cmd_clear(self, args) -> None:
        """Handle the clear command."""
        if not self._initialize_vector_db_only(args.config):
            return
        
        # Get stats using lightweight approach
        stats = {
            'total_documents': self.vector_db.count(),
            'collection_name': self.vector_db.name
        }
        
        if stats['total_documents'] == 0:
            print("📭 Database is already empty.")
            return
        
        if not args.confirm:
            response = input(f"⚠️  This will delete {stats['total_documents']} documents. Continue? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Operation cancelled.")
                return
        
        try:
            print("🗑️  Clearing database...")
            initial_count = stats['total_documents']
            
            # Clear database using lightweight vector DB access
            if initial_count > 0:
                # Get all document IDs
                results = self.vector_db.get(include=[])  # Get only metadata and IDs
                
                if results and results.get('ids') and len(results['ids']) > 0:
                    # Delete all documents by their IDs
                    self.vector_db.delete(ids=results['ids'])
                    print(f"✅ Database cleared successfully! Removed {initial_count} documents.")
                else:
                    print("✅ Database cleared successfully! No documents found to remove.")
            else:
                print("✅ Database is already empty.")
                
        except Exception as e:
            print(f"❌ Failed to clear database: {e}")
    
    def get_log_files(self):
        """Get all log files sorted by modification time (newest first)."""
        try:
            logs_path = Path("./logs")
            if not logs_path.exists():
                return []
            
            log_files = []
            for log_file in logs_path.glob("*.log"):
                try:
                    stat = log_file.stat()
                    log_files.append({
                        'name': log_file.name,
                        'path': str(log_file),
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'modified_str': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                    })
                except Exception:
                    continue
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x['modified'], reverse=True)
            return log_files
            
        except Exception as e:
            print(f"❌ Error getting log files: {e}")
            return []
    
    def cleanup_old_logs(self, keep_count=5):
        """Delete old log files, keeping only the latest 'keep_count' files."""
        try:
            log_files = self.get_log_files()
            
            if len(log_files) <= keep_count:
                return 0, []
            
            # Files to delete (all except the first 'keep_count')
            files_to_delete = log_files[keep_count:]
            deleted_files = []
            
            for file_info in files_to_delete:
                try:
                    Path(file_info['path']).unlink()
                    deleted_files.append(file_info['name'])
                except Exception as e:
                    print(f"❌ Failed to delete {file_info['name']}: {e}")
            
            return len(deleted_files), deleted_files
            
        except Exception as e:
            print(f"❌ Error during log cleanup: {e}")
            return 0, []
    
    def cmd_logs(self, args) -> None:
        """Handle the logs command."""
        if args.list:
            # List all log files
            log_files = self.get_log_files()
            
            if not log_files:
                print("📭 No log files found.")
                return
            
            print("📝 Log Files:")
            print(f"{'File Name':<30} {'Size (KB)':<10} {'Modified':<20}")
            print("-" * 65)
            
            total_size = 0
            for file_info in log_files:
                size_kb = file_info['size'] / 1024
                total_size += file_info['size']
                print(f"{file_info['name']:<30} {size_kb:<10.1f} {file_info['modified_str']:<20}")
            
            print("-" * 65)
            print(f"Total: {len(log_files)} files, {total_size / 1024 / 1024:.2f} MB")
        
        elif args.view:
            # View contents of a specific log file
            log_files = self.get_log_files()
            log_file_names = [f['name'] for f in log_files]
            
            if args.view not in log_file_names:
                print(f"❌ Log file '{args.view}' not found.")
                print("Available files:")
                for name in log_file_names:
                    print(f"   • {name}")
                return
            
            # Find the file info
            file_info = next(f for f in log_files if f['name'] == args.view)
            
            try:
                with open(file_info['path'], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                print(f"📄 Log file: {args.view}")
                print(f"📊 Size: {file_info['size']} bytes ({file_info['size'] / 1024:.1f} KB)")
                print(f"🕒 Modified: {file_info['modified_str']}")
                print(f"📏 Total lines: {len(lines)}")
                print("-" * 60)
                
                if args.tail:
                    display_lines = lines[-args.lines:] if len(lines) > args.lines else lines
                    print(f"📄 Showing last {len(display_lines)} lines:")
                else:
                    display_lines = lines[:args.lines] if len(lines) > args.lines else lines
                    print(f"📄 Showing first {len(display_lines)} lines:")
                
                print("-" * 60)
                for line in display_lines:
                    print(line.rstrip())
                
                if len(lines) > args.lines:
                    remaining = len(lines) - args.lines
                    print("-" * 60)
                    print(f"... ({remaining} more lines)")
                    print(f"💡 Use --lines {len(lines)} to see all lines")
                
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
        
        elif args.cleanup:
            # Clean up old log files
            log_files = self.get_log_files()
            
            if len(log_files) <= args.keep:
                print(f"✅ Only {len(log_files)} log files found. No cleanup needed.")
                return
            
            files_to_delete = len(log_files) - args.keep
            print(f"⚠️  This will delete {files_to_delete} old log files, keeping the latest {args.keep}.")
            
            response = input("Continue? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ Operation cancelled.")
                return
            
            deleted_count, deleted_files = self.cleanup_old_logs(args.keep)
            
            if deleted_count > 0:
                print(f"✅ Deleted {deleted_count} old log files!")
                print("Deleted files:")
                for file_name in deleted_files:
                    print(f"   • {file_name}")
            else:
                print("ℹ️ No files were deleted.")
        
        else:
            # Default: show log statistics
            log_files = self.get_log_files()
            
            if not log_files:
                print("📭 No log files found.")
                return
            
            total_size = sum(f['size'] for f in log_files)
            
            print("📊 Log Statistics:")
            print(f"   • Total files: {len(log_files)}")
            print(f"   • Total size: {total_size / 1024 / 1024:.2f} MB")
            print(f"   • Oldest: {log_files[-1]['modified_str']}")
            print(f"   • Newest: {log_files[0]['modified_str']}")
            print()
            print("💡 Use 'python main.py logs --help' for more options")
    
    def cmd_list(self, args) -> None:
        """Handle the list command."""
        print("📋 RAG Pipeline Information")
        print(f"   • Version: {version_info['version']}")
        print("\n🔧 Supported file formats:")
        print("   • PDF files (.pdf)")
        print("   • Word documents (.docx)")
        print("   • Text files (.txt)")
        print("   • JSON files (.json)")
        
        print("\n⚙️  Configuration:")
        print(f"   • Config file: config/config.yaml")
        print(f"   • Log directory: ./logs")
        print(f"   • Vector database: ./data/vectors")
        print(f"   • Raw documents: ./data/raw")
    
    def run(self) -> None:
        """Run the CLI application."""
        args = self.parser.parse_args()
        
        # Handle case where no command is provided
        if not args.command:
            self.parser.print_help()
            return
        
        # Set verbose mode
        if args.verbose:
            print("🔍 Verbose mode enabled")
        
        # Route to appropriate command handler
        command_handlers = {
            'init': self.cmd_init,
            'ingest': self.cmd_ingest,
            'query': self.cmd_query,
            'interactive': self.cmd_interactive,
            'stats': self.cmd_stats,
            'clear': self.cmd_clear,
            'logs': self.cmd_logs,
            'list': self.cmd_list,
        }
        
        handler = command_handlers.get(args.command)
        if handler:
            handler(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            self.parser.print_help()


def main():
    """Entry point for the CLI application."""
    try:
        app = RAGCLIApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 