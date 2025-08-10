"""
Document Processing Module
Handles text extraction from various document formats
"""

import os
import PyPDF2
from docx import Document
from typing import Optional, Tuple

class DocumentProcessor:
    """Handles document processing and text extraction"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    }
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ['pdf', 'docx', 'txt']
    
    @staticmethod
    def allowed_mime_type(mime_type: str) -> bool:
        """Check if MIME type is allowed"""
        return mime_type in DocumentProcessor.ALLOWED_MIME_TYPES
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")
    
    @staticmethod
    def process_document(file_path: str, file_type: str) -> Tuple[str, str]:
        """
        Process document and extract text
        
        Args:
            file_path: Path to the uploaded file
            file_type: MIME type of the file
            
        Returns:
            Tuple of (extracted_text, file_extension)
        """
        try:
            # Determine file extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Extract text based on file type
            if file_type == 'application/pdf' or file_extension == '.pdf':
                text = DocumentProcessor.extract_text_from_pdf(file_path)
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_extension == '.docx':
                text = DocumentProcessor.extract_text_from_docx(file_path)
            elif file_type == 'text/plain' or file_extension == '.txt':
                text = DocumentProcessor.extract_text_from_txt(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
            
            # Validate extracted text
            if not text or len(text.strip()) == 0:
                raise Exception("No text could be extracted from the document")
            
            return text, file_extension
            
        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes 