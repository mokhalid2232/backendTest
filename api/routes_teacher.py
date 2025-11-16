from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from models.schemas_teacher import QuizRequest, QuizResponse, UploadMaterialResponse
from services.quizz_generator import generate_quiz_from_material_id, save_quiz_to_mongodb
from services.material_manger import upload_material
from auth_utils import require_teacher
from utils.llm_client import generate_quiz_with_llm

router = APIRouter(prefix="", tags=["Teacher"])

@router.post("/upload-material", response_model=UploadMaterialResponse)
async def upload_material_route(
    class_name: str = Form(...),
    section: str = Form(...),
    file: UploadFile = File(...),
    user_data: dict = Depends(require_teacher)
):
    """
    Upload teaching material (PDF or text file) to MongoDB, categorized by class and section.
    TEACHER ACCESS REQUIRED
    """
    try:
        file_content = await file.read()
        filename = file.filename
        teacher_id = user_data["user_id"]  # Use actual teacher ID from auth
        teacher_email = user_data["email"]
        

        print(f"👨‍🏫 Teacher {teacher_id} uploading material: {filename}")

        material_id = upload_material(
            file_data=file_content,
            filename=filename,
            teacher_id=teacher_id,
            section=section
        )

        return UploadMaterialResponse(
            status="success",
            file_name=filename,
            doc_id=material_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    data: QuizRequest,
    user_data: dict = Depends(require_teacher)
):
    """
    Generate a quiz based on previously uploaded materials for a specific class and section.
    TEACHER ACCESS REQUIRED
    """
    try:
        print(f"👨‍🏫 Teacher {user_data['email']} generating quiz...")
        
        # If material_ids are provided, use the first one
        if data.material_ids and len(data.material_ids) > 0:
            material_id = data.material_ids[0]
            print(f"📚 Using material ID: {material_id}")
            quiz = generate_quiz_from_material_id(
                material_id=material_id,
                subject=data.subject,
                level=data.level,
                num_questions=data.num_questions
            )
        else:
            # Fallback: generate quiz without specific material
            print("🔧 Using general knowledge fallback")
            quiz = generate_quiz_with_llm(
                subject=data.subject,
                level=data.level,
                material_text=f"General knowledge about {data.subject} for {data.level} level",
                num_questions=data.num_questions
            )

        # Save quiz to MongoDB
        teacher_id = user_data["user_id"]
        quiz_id = save_quiz_to_mongodb(
            teacher_id=teacher_id,
            section="default",
            subject=data.subject,
            quiz_content=quiz
        )

        return QuizResponse(quiz=quiz)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-materials")
async def get_teacher_materials(user_data: dict = Depends(require_teacher)):
    """
    Get all materials uploaded by the current teacher.
    TEACHER ACCESS REQUIRED
    """
    try:
        from services.material_manger import get_materials_by_teacher
        
        teacher_id = user_data["user_id"]
        materials = get_materials_by_teacher(teacher_id)
        
        return {
            "teacher_id": teacher_id,
            "materials": materials
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))