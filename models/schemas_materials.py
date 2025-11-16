from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UploadMaterialRequest(BaseModel):
	section: str = Field(..., example="Section A")
	subject: str = Field(..., example="Mathematics")
	lecture_number: int = Field(..., example=5)
	description: Optional[str] = Field(None, example="Lecture on calculus basics")

class MaterialMetadata(BaseModel):
	section: str
	subject: str
	lecture_number: int
	file_url: str
	uploaded_at: datetime
	description: Optional[str] = None