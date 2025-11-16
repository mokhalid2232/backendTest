from pydantic import BaseModel, Field
from typing import List, Optional

class QuizRequest(BaseModel):
    subject: str = Field(..., example="Mathematics")
    level: str = Field(..., example="Intermediate")
    num_questions: int = Field(..., example=5)
    material_ids: Optional[List[str]] = Field(None, description="IDs of uploaded materials to use in quiz generation")

class QuizResponse(BaseModel):
    quiz: str = Field(..., description="Generated quiz text")

class UploadMaterialResponse(BaseModel):
    status: str = Field(..., example="success")
    file_name: str = Field(..., example="lecture.pdf")
    doc_id: str = Field(..., example="material_123")

class Grade(BaseModel):
    student_id: str = Field(..., example="student_123")
    quiz_id: str = Field(..., example="quiz_456")
    score: float = Field(..., ge=0, le=100, example=85.0)
    subject: str = Field(..., example="Science")
    feedback: Optional[str] = Field(None, example="Needs improvement in physics concepts")