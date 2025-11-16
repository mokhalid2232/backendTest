from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
class GradeEntry(BaseModel):
	student_id: str = Field(..., example="student_123")
	quiz_id: str = Field(..., example="quiz_456")
	score: float = Field(..., ge=0.0, le=100.0, example=87.5)
	submitted_at: datetime

class AttendanceEntry(BaseModel):
	student_id: str = Field(..., example="student_123")
	date: datetime
	status: str = Field(..., example="present") # or "absent", "late"

class Recommendation(BaseModel):
	student_id: str = Field(..., example="student_123")
	message: str = Field(..., example="Focus more on algebra topics.")
	created_at: datetime

class GradeReport(BaseModel):
	section: str
	subject: str
	grades: List[GradeEntry]

class AttendanceReport(BaseModel):
	section: str
	attendance_records: List[AttendanceEntry]

class RecommendationList(BaseModel):
	recommendations: List[Recommendation]