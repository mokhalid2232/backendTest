from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from models.schemas_student import SummaryResponse
from services.lecture_summerizer import summarize_lecture_and_store
from auth_utils import require_student

router = APIRouter(prefix="", tags=["Student"])

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_lecture(
    subject: str = Form(...),
    lecture_number: int = Form(...),
    lecture_text: str = Form(None),
    file: UploadFile = File(None),
    user_data: dict = Depends(require_student)
):
    """
    Accepts either lecture text or file, summarizes the content, and stores it in MongoDB.
    STUDENT ACCESS REQUIRED
    """
    try:
        print(f"👨‍🎓 Student {user_data['email']} requesting summary...")
        
        file_data = None
        content = None
        
        if file:
            # Read file as bytes (don't decode - PDF is binary)
            file_data = await file.read()
            print(f"📄 File uploaded: {file.filename}, Size: {len(file_data)} bytes")
        
        if lecture_text:
            # Text is already string, no decoding needed
            content = lecture_text
            print(f"📝 Text length: {len(lecture_text)} characters")

        student_id = user_data["user_id"]  # Use actual student ID from auth

        summary = summarize_lecture_and_store(
            student_id=student_id,
            subject=subject,
            lecture_number=lecture_number,
            lecture_text=content,
            file_data=file_data
        )

        return SummaryResponse(
            subject=subject,
            lecture_number=lecture_number,
            summary=summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-summaries")
async def get_student_summaries(user_data: dict = Depends(require_student)):
    """
    Get all summaries created by the current student.
    STUDENT ACCESS REQUIRED
    """
    try:
        from config import summaries_collection
        
        student_id = user_data["user_id"]
        summaries = summaries_collection.find({"student_id": student_id})
        
        # Convert ObjectId to string for JSON serialization
        summaries_list = []
        for summary in summaries:
            summary["_id"] = str(summary["_id"])
            summaries_list.append(summary)
            
        return {
            "student_id": student_id,
            "summaries": summaries_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))