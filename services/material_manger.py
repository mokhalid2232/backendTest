import uuid
from datetime import datetime
from config import materials_collection, db
import gridfs
from bson import ObjectId

# Initialize GridFS
fs = gridfs.GridFS(db)

ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "txt"}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_material(file_data: bytes, filename: str, teacher_id: str, section: str, subject: str = None) -> str:
    """
    Upload material to MongoDB GridFS (cloud storage) and save metadata.
    """
    if not is_allowed_file(filename):
        raise ValueError("Unsupported file format.")

    # Store file in GridFS (cloud storage)
    file_id = fs.put(file_data, filename=filename, content_type="application/octet-stream")
    
    # Save metadata to materials collection
    material_id = str(uuid.uuid4())
    material_data = {
        "material_id": material_id,
        "file_id": file_id,  # GridFS file ID
        "teacher_id": teacher_id,
        "section": section,
        "subject": subject,
        "filename": filename,
        "file_size": len(file_data),
        "uploaded_at": datetime.utcnow()
    }
    
    result = materials_collection.insert_one(material_data)
    return material_id

def download_material(material_id: str) -> tuple[bytes, str]:
    """
    Download material from MongoDB GridFS.
    Returns (file_data, filename)
    """
    material = materials_collection.find_one({"material_id": material_id})
    if not material:
        raise ValueError("Material not found")
    
    file_id = material["file_id"]
    file_data = fs.get(file_id).read()
    filename = material["filename"]
    
    return file_data, filename

def get_materials_by_section(section: str) -> list:
    """
    Get all materials for a section (metadata only, not file content).
    """
    materials = materials_collection.find({"section": section})
    return list(materials)

def get_material_info(material_id: str) -> dict:
    """
    Get material metadata without downloading the file.
    """
    material = materials_collection.find_one({"material_id": material_id})
    if material:
        # Remove the file_id from response for security
        material.pop('file_id', None)
        return material
    return None