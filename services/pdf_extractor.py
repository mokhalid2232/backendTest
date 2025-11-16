from PyPDF2 import PdfReader
from typing import Optional
import io

def extract_text_from_pdf(pdf_data: bytes) -> Optional[str]:
    """
    Extract text from PDF bytes using PyPDF2
    Same function name as your existing code expects
    """
    try:
        # Create a file-like object from bytes
        pdf_file = io.BytesIO(pdf_data)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip() if text.strip() else None
        
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None

def get_pdf_info(pdf_data: bytes) -> dict:
    """
    Get PDF metadata like page count
    Same function name for consistency
    """
    try:
        pdf_file = io.BytesIO(pdf_data)
        reader = PdfReader(pdf_file)
        
        info = {
            "page_count": len(reader.pages),
            "is_valid": True,
            "author": reader.metadata.get('/Author', ''),
            "title": reader.metadata.get('/Title', ''),
            "subject": reader.metadata.get('/Subject', '')
        }
        return info
        
    except Exception as e:
        return {"is_valid": False, "error": str(e)}