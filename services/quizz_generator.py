from utils.llm_templates import generate_quiz_prompt
from utils.llm_client import call_llm, generate_quiz_with_llm
from config import quizzes_collection, materials_collection
from datetime import datetime
import uuid
from .pdf_extractor import extract_text_from_pdf
import os
from bson import ObjectId

def generate_quiz_from_text(subject: str, level: str, material_text: str, num_questions: int = 5) -> str:
    """
    Generate a quiz from lecture/material text using Gemini.
    """
    prompt = generate_quiz_prompt(subject, level, material_text, num_questions)
    quiz_text = call_llm(prompt)
    return quiz_text

def generate_quiz_from_material_id(material_id: str, subject: str, level: str) -> str:
    """
    Generate a quiz based on a specific material ID.
    """
    try:
        # Get material from MongoDB
        material = materials_collection.find_one({"material_id": material_id})
        if not material:
            raise Exception(f"No material found with ID: {material_id}")

        # Get file data
        file_data, filename = download_material(material_id)
        
        # Extract text from file
        material_text = extract_text_from_pdf(file_data)
        if not material_text:
            raise Exception("No text could be extracted from the file.")

        # Generate quiz using Gemini
        quiz_text = generate_quiz_with_llm(subject, level, material_text)
        return quiz_text

    except Exception as e:
        raise Exception(f"Quiz generation failed: {str(e)}")

def save_quiz_to_mongodb(teacher_id: str, section: str, subject: str, quiz_content: str) -> str:
    """
    Save the generated quiz to MongoDB and return the quiz ID.
    """
    quiz_id = str(uuid.uuid4())
    quiz_data = {
        "quiz_id": quiz_id,
        "teacher_id": teacher_id,
        "section": section,
        "subject": subject,
        "quiz": quiz_content,
        "created_at": datetime.utcnow()
    }
    
    result = quizzes_collection.insert_one(quiz_data)
    return quiz_id

def get_quiz_by_id(quiz_id: str) -> dict:
    """
    Fetch a quiz by ID from MongoDB.
    """
    try:
        # Try by MongoDB _id first
        quiz = quizzes_collection.find_one({"_id": ObjectId(quiz_id)})
        if quiz:
            return quiz
        
        # Try by quiz_id field
        quiz = quizzes_collection.find_one({"quiz_id": quiz_id})
        return quiz if quiz else {}
    except:
        return {}

# Helper function to download material (using your material_manager)
def download_material(material_id: str):
    """
    Download material using the material_manager.
    """
    from .material_manger import download_material as dm
    return dm(material_id)