from pydantic import BaseModel, Field
class SummaryRequest(BaseModel):
	subject: str = Field(..., example="History")
	lecture_number: int = Field(..., example=3)
	lecture_text: str = Field(..., description="Full lecture text to be summarized")

class SummaryResponse(BaseModel):
	subject: str = Field(..., example="History")
	lecture_number: int = Field(..., example=3)
	summary: str = Field(..., description="Summarized content of the lecture")