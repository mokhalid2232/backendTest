from utils.llm_templates import generate_summary_prompt
from utils.llm_client import call_llm, generate_summary_with_llm
from config import summaries_collection
from datetime import datetime
import uuid
from .pdf_extractor import extract_text_from_pdf

def summarize_lecture(subject: str, lecture_number: int, content: str) -> str:
    """
    Generate a summary of the lecture content using Gemini.
    """
    prompt = generate_summary_prompt(subject, lecture_number, content)
    summary = call_llm(prompt)
    return summary

def summarize_lecture_and_store(student_id: str, subject: str, lecture_number: int, lecture_text: str = None, file_data: bytes = None) -> str:
    """
    Summarize lecture from text or PDF file and store in MongoDB.
    """
    try:
        content_to_summarize = ""
        
        # If file provided, extract text from PDF
        if file_data:
            print(f"📄 Processing uploaded file, size: {len(file_data)} bytes")
            content_to_summarize = extract_text_from_pdf(file_data)
            if not content_to_summarize:
                raise Exception("Could not extract text from PDF file")
            print(f"📝 Extracted {len(content_to_summarize)} characters from PDF")
        
        # If text provided, use it directly
        elif lecture_text:
            content_to_summarize = lecture_text
            print(f"📝 Using provided text, length: {len(content_to_summarize)} characters")
        
        else:
            raise Exception("No lecture text or file provided for summarization")

        # Generate summary using Gemini
        print(f"🤖 Generating summary for {subject}, Lecture {lecture_number}...")
        summary = summarize_lecture(subject, lecture_number, content_to_summarize)

        # Save to MongoDB
        save_summary_to_mongodb(student_id, subject, lecture_number, summary)

        return summary

    except Exception as e:
        print(f"❌ Summarization failed: {str(e)}")
        raise Exception(f"Summarization failed: {str(e)}")

def save_summary_to_mongodb(student_id: str, subject: str, lecture_number: int, summary: str) -> str:
    """
    Save the summarized lecture to MongoDB.
    """
    summary_id = str(uuid.uuid4())
    summary_data = {
        "summary_id": summary_id,
        "student_id": student_id,
        "subject": subject,
        "lecture_number": lecture_number,
        "summary": summary,
        "created_at": datetime.utcnow()
    }
    
    result = summaries_collection.insert_one(summary_data)
    print(f"💾 Summary saved to database with ID: {summary_id}")
    return summary_id

def get_summary_by_id(summary_id: str) -> dict:
    """
    Retrieve a summary document from MongoDB.
    """
    from bson import ObjectId
    try:
        summary = summaries_collection.find_one({"_id": ObjectId(summary_id)})
        return summary if summary else {}
    except:
        # Also try searching by summary_id field for backward compatibility
        summary = summaries_collection.find_one({"summary_id": summary_id})
        return summary if summary else {}