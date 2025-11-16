import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print("✅ Gemini AI configured successfully")
else:
    print("❌ GEMINI_API_KEY not found in environment variables")

def call_llm(prompt: str, model_type: str = "gemini-2.0-flash") -> str:
    """
    Make a call to Google Gemini with the given prompt.
    """
    if not gemini_api_key:
        return "Error: Gemini API key not configured. Please set GEMINI_API_KEY in your .env file"
    
    try:
        # Use the latest model naming
        model = genai.GenerativeModel(model_type)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1500,
            )
        )
        return response.text.strip()
    
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"

def generate_quiz_with_llm(subject: str, level: str, material_text: str, num_questions: int = 5) -> str:
    """
    Direct function to generate quiz using Gemini.
    """
    from .llm_templates import generate_quiz_prompt
    prompt = generate_quiz_prompt(subject, level, material_text, num_questions)
    return call_llm(prompt)

def generate_summary_with_llm(subject: str, lecture_number: int, content: str) -> str:
    """
    Direct function to generate summary using Gemini.
    """
    from .llm_templates import generate_summary_prompt
    prompt = generate_summary_prompt(subject, lecture_number, content)
    return call_llm(prompt)

# Backward compatibility functions
def generate_quiz_from_material(material_text: str) -> str:
    """
    Generate quiz using Gemini (compatible with existing code).
    """
    return generate_quiz_with_llm("General", "Intermediate", material_text)