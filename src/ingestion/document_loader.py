"""Document loader for various file formats."""

import os
from typing import List, Dict, Any, Union
from pathlib import Path
import logging
import json

# Document processing imports
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

# Add this at the top of the file, after imports, to set the logger format for this module
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s.%(funcName)s:%(lineno)d - %(message)s',
    level=logging.INFO
)


class DocumentLoader:
    """Load and extract text from various document formats."""
    
    def __init__(self):
        """Initialize the document loader."""
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.txt', '.pdf', '.docx', '.json']
    
    def load_document(self, file_path: Union[str, Path]) -> Union[Dict[str, Any], list]:
        """
        Load a document and extract its text content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing document metadata and content
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Extract text based on file type
        text_content = ""
        
        if file_path.suffix.lower() == '.txt':
            text_content = self._load_txt(file_path)
        elif file_path.suffix.lower() == '.pdf':
            text_content = self._load_pdf(file_path)
        elif file_path.suffix.lower() == '.docx':
            text_content = self._load_docx(file_path)
        elif file_path.suffix.lower() == '.json':
            return self._load_json(file_path)
        # Create document metadata (for non-JSON)
        document_data = {
            'content': text_content,
            'metadata': {
                'filename': file_path.name,
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'file_type': file_path.suffix.lower(),
                'character_count': len(text_content)
            }
        }
        self.logger.info(f"Loaded document: {file_path.name} ({len(text_content)} characters)")
        return document_data
    
    def _load_txt(self, file_path: Path) -> str:
        """Load text from a TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _load_pdf(self, file_path: Path) -> str:
        """Load text from a PDF file."""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF support. Install with: pip install PyPDF2")
        
        text_content = ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                    
        except Exception as e:
            raise Exception(f"Error reading PDF file: {e}")
        
        return text_content.strip()
    
    def _load_docx(self, file_path: Path) -> str:
        """Load text from a DOCX file."""
        if Document is None:
            raise ImportError("python-docx is required for DOCX support. Install with: pip install python-docx")
        
        try:
            doc = Document(file_path)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
                
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {e}")

    def _load_json(self, file_path: Union[str, Path]) -> list:
        """Load documents from a JSON file. Each document should have a 'content' field."""
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        docs = []
        # Debug: log type and length of data
        self.logger.debug(f"Loading JSON file: {file_path}")
        self.logger.debug(f"Top-level JSON type: {type(data)}")
        if isinstance(data, list):
            self.logger.debug(f"JSON list length: {len(data)}")
            if len(data) > 0 and isinstance(data[0], dict):
                self.logger.debug(f"First document keys: {list(data[0].keys())}")
        elif isinstance(data, dict):
            self.logger.debug(f"JSON dict length: {len(data)}")
            first_key = next(iter(data), None)
            if first_key and isinstance(data[first_key], dict):
                self.logger.debug(f"First document keys: {list(data[first_key].keys())}")
        # If the JSON is a list of documents
        if isinstance(data, list):
            for i, doc in enumerate(data):
                if isinstance(doc, dict):
                    content = doc.get('content') or doc.get('publication_description') or str(doc)
                else:
                    content = str(doc)
                if content is None:
                    content = ""
                docs.append({
                    'content': content,
                    'metadata': {
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_size': file_path.stat().st_size,
                        'file_type': file_path.suffix.lower(),
                        'character_count': len(content),
                        'json_index': i
                    }
                })
        # If the JSON is a dict of documents
        elif isinstance(data, dict):
            for key, doc in data.items():
                if isinstance(doc, dict):
                    content = doc.get('content') or doc.get('publication_description') or str(doc)
                else:
                    content = str(doc)
                if content is None:
                    content = ""
                docs.append({
                    'content': content,
                    'metadata': {
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_size': file_path.stat().st_size,
                        'file_type': file_path.suffix.lower(),
                        'character_count': len(content),
                        'json_key': key
                    }
                })
        else:
            # Fallback: treat the whole JSON as one document
            content = str(data) if data is not None else ""
            docs.append({
                'content': content,
                'metadata': {
                    'filename': file_path.name,
                    'file_path': str(file_path),
                    'file_size': file_path.stat().st_size,
                    'file_type': file_path.suffix.lower(),
                    'character_count': len(content)
                }
            })
        self.logger.info(f"Loaded {len(docs)} documents from JSON file: {file_path.name}")
        self.logger.debug(f"Loaded {len(docs)} documents from JSON file: {file_path.name}")
        return docs
    
    def load_directory(self, directory_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory_path: Path to the directory containing documents
            
        Returns:
            List of document data dictionaries
        """
        if not isinstance(directory_path, Path):
            directory_path = Path(directory_path)
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        documents = []
        
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    doc_data = self.load_document(file_path)
                    if isinstance(doc_data, list):
                        documents.extend(doc_data)
                    else:
                        documents.append(doc_data)
                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {e}")
                    continue
        
        self.logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents 