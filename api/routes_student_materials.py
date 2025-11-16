from fastapi import APIRouter, HTTPException
from services.material_manger import get_materials_by_section, get_material_info, download_material
from fastapi.responses import Response
import urllib.parse

router = APIRouter(prefix="/student", tags=["Student Materials"])

@router.get("/materials/{section}")
async def get_section_materials(section: str):
    """
    Students can see all materials for their section.
    """
    try:
        materials = get_materials_by_section(section)
        
        # Clean up response for students
        clean_materials = []
        for material in materials:
            clean_materials.append({
                "material_id": material["material_id"],
                "filename": material["filename"],
                "subject": material.get("subject", "Unknown"),
                "uploaded_at": material["uploaded_at"],
                "file_size": material.get("file_size", 0)
            })
            
        return {
            "section": section,
            "materials": clean_materials
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get materials: {str(e)}")

@router.get("/materials/download/{material_id}")
async def student_download_material(material_id: str):
    """
    Students can download materials.
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