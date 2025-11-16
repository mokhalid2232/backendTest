def generate_quiz_prompt(subject: str, level: str, material_text: str, num_questions: int = 5) -> str:
    """
    Generate a prompt for quiz creation optimized for Gemini.
    """
    prompt = f"""
    You are an expert teacher creating educational quizzes. Create a {num_questions}-question quiz for {subject} at {level} level.

    STUDY MATERIAL:
    {material_text}

    REQUIREMENTS:
    1. Create {num_questions} multiple-choice questions with 4 options each
    2. Clearly mark the correct answer with "Correct Answer:"
    3. Make questions relevant to the provided study material
    4. Include a mix of difficulty levels
    5. Format each question clearly with numbering
    6. Return only the quiz content without additional explanations

    QUIZ FORMAT EXAMPLE:
    1. What is the main topic covered in this material?
    A) Option 1
    B) Option 2  
    C) Option 3
    D) Option 4
    Correct Answer: A

    2. [Next question...]
    """
    return prompt

def generate_summary_prompt(subject: str, lecture_number: int, content: str) -> str:
    """
    Generate a prompt for lecture summarization optimized for Gemini.
    """
    prompt = f"""
    Summarize the following lecture content for {subject}, Lecture {lecture_number}:

    LECTURE CONTENT:
    {content}

    Please provide a concise educational summary that:
    1. Captures the main concepts and key points
    2. Is easy to understand for students
    3. Highlights important definitions and examples  
    4. Is approximately 15-20% of the original text length
    5. Maintains the core educational value
    6. Uses clear, academic language

    Return only the summary content without introductory text.
    """
    return prompt