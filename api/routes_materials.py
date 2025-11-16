from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import Response
from services.material_manger import upload_material, download_material, get_materials_by_section, get_material_info
from auth_utils import require_authenticated
import urllib.parse

router = APIRouter(prefix="/materials", tags=["Materials"])

@router.post("/upload")
async def upload_material_route(
    section: str = Form(...),
    subject: str = Form(...),
    file: UploadFile = File(...),
    user_data: dict = Depends(require_authenticated)
):
    """
    Uploads a material file to MongoDB cloud storage and stores metadata.
    AUTHENTICATED ACCESS REQUIRED
    """
    try:
        file_content = await file.read()
        
        # Check file size (limit to 16MB - MongoDB document limit)
        if len(file_content) > 16 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 16MB.")
            
        teacher_id = user_data["user_id"]

        material_id = upload_material(
            file_data=file_content,
            filename=file.filename,
            teacher_id=teacher_id,
            section=section,
            subject=subject
        )

        return {
            "message": "Material uploaded successfully to cloud storage",
            "material_id": material_id,
            "filename": file.filename,
            "uploaded_by": user_data["email"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/download/{material_id}")
async def download_material_route(material_id: str, user_data: dict = Depends(require_authenticated)):
    """
    Download a material file from MongoDB cloud storage.
    AUTHENTICATED ACCESS REQUIRED
    """
    try:
        file_data, filename = download_material(material_id)
        
        encoded_filename = urllib.parse.quote(filename)
        
        return Response(
            content=file_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Content-Type": "application/octet-stream"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/list/{section}")
async def list_materials(section: str, user_data: dict = Depends(require_authenticated)):
    """
    List all materials available for a specific section.
    AUTHENTICATED ACCESS REQUIRED
    """
    try:
        materials = get_materials_by_section(section)
        
        # Convert ObjectId to string for JSON serialization
        for material in materials:
            material["_id"] = str(material["_id"])
            
        return {
            "section": section,
            "requested_by": user_data["email"],
            "materials": materials
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list materials: {str(e)}")

@router.get("/info/{material_id}")
async def get_material_info_route(material_id: str, user_data: dict = Depends(require_authenticated)):
    """
    Get information about a specific material.
    AUTHENTICATED ACCESS REQUIRED
    """
    try:
        material_info = get_material_info(material_id)
        if not material_info:
            raise HTTPException(status_code=404, detail="Material not found")
            
        return material_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))