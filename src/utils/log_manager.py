"""Log management utilities for the RAG system."""

import os
from datetime import datetime
from typing import Optional

# Default log format - centralized to avoid hardcoding
DEFAULT_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s.%(funcName)s:%(lineno)d - %(message)s"


class LogManager:
    """Utility class for consistent logging configuration across the application."""
    
    _timestamp: Optional[str] = None
    
    @classmethod
    def get_timestamped_filename(cls, base_name: str = "log", extension: str = ".log") -> str:
        """
        Generate a timestamped filename for logging.
        
        Args:
            base_name: Base name for the log file (default: "log")
            extension: File extension (default: .log)
            
        Returns:
            Timestamped filename string in format: log_YYMMDD_HHMM.log
        """
        if cls._timestamp is None:
            cls._timestamp = datetime.now().strftime("%y%m%d_%H%M")
        
        return f"{base_name}_{cls._timestamp}{extension}"
    
    @classmethod
    def ensure_log_directory(cls, log_dir: str = "./logs") -> str:
        """
        Check if log directory exists and create it if it doesn't.
        
        Args:
            log_dir: Directory path for log files (default: "./logs")
            
        Returns:
            Absolute path of the created/existing directory
        """
        # Convert to absolute path for clarity
        abs_log_dir = os.path.abspath(log_dir)
        
        if not os.path.exists(abs_log_dir):
            try:
                os.makedirs(abs_log_dir, exist_ok=True)
                # Directory creation is now silent - no console output
            except OSError as e:
                # Only raise the exception, don't print to console
                raise OSError(f"Failed to create log directory {abs_log_dir}: {e}")
        
        return abs_log_dir
    
    @classmethod
    def get_log_filepath(cls, base_name: str = "log", log_dir: str = "./logs") -> str:
        """
        Generate a full path for a timestamped log file.
        
        Args:
            base_name: Base name for the log file (default: "log")
            log_dir: Directory to store log files
            
        Returns:
            Full path to the timestamped log file
        """
        # Ensure logs directory exists with explicit checking
        cls.ensure_log_directory(log_dir)
        
        filename = cls.get_timestamped_filename(base_name)
        return os.path.join(log_dir, filename)
    
    @classmethod
    def reset_timestamp(cls) -> None:
        """Reset the timestamp to generate a new one on next call."""
        cls._timestamp = None
    
    @classmethod
    def get_default_format(cls) -> str:
        """Get the default log format."""
        return DEFAULT_LOG_FORMAT 