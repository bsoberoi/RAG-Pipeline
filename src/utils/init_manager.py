import os
import logging
import yaml
from src.utils.log_manager import LogManager
from dotenv import load_dotenv

def init_logging_and_config():
    # Load environment variables from .env file if present
    load_dotenv()
    # Suppress sentence_transformers logging
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
        
    # Suppress chromadb logging
    logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.WARNING)
    
    # Suppress httpx logging
    logging.getLogger("httpx").setLevel(logging.WARNING)    
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        log_level_str = config.get('logging', {}).get('level', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        log_format = config.get('logging', {}).get('format', LogManager.get_default_format())
        log_path = config.get('logging', {}).get('path', './logs')
        
        # Ensure log directory exists before creating log file
        LogManager.ensure_log_directory(log_path)
        
        # Use LogManager for consistent timestamped log filename
        log_file = LogManager.get_log_filepath(log_dir=log_path)
    else:
        config = {}
        log_level = logging.INFO
        log_format = LogManager.get_default_format()
        
        # Ensure default log directory exists before creating log file
        LogManager.ensure_log_directory('./logs')
        
        # Use LogManager for consistent timestamped log filename with default path
        log_file = LogManager.get_log_filepath()

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),  # Changed from 'a' to 'w' for new file
            logging.StreamHandler()
        ]
    )
    
    # Log initialization message only to file (not console)
    file_logger = logging.getLogger('file_only')
    file_logger.setLevel(log_level)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    file_logger.addHandler(file_handler)
    file_logger.propagate = False  # Prevent propagation to root logger (which has console handler)
    file_logger.info(f"Logging initialized. Log file: {os.path.abspath(log_file)}")
    
    return config, log_level 