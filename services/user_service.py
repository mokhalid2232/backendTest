from config import users_collection
from models.schemas_auth import UserCreate, UserResponse
from auth_utils import get_password_hash, verify_password
from datetime import datetime
import uuid
from bson import ObjectId

def create_user(user_data: UserCreate) -> dict:
    """Create a new user in MongoDB."""
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Create user document
    user_id = str(uuid.uuid4())
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "hashed_password": get_password_hash(user_data.password),
        "is_active": True,
        "created_at": datetime.utcnow()  # Make sure this is included
    }
    
    # Insert into MongoDB
    result = users_collection.insert_one(user_doc)
    
    # Return user data (without password)
    return {
        "user_id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "created_at": user_doc["created_at"],  # Include created_at
        "is_active": True
    }

def authenticate_user(email: str, password: str) -> dict:
    """Authenticate a user and return user data if valid."""
    user = users_collection.find_one({"email": email})
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    if not user.get("is_active", True):
        return None
    
    # Return user data without password
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "created_at": user["created_at"]  # Include created_at
    }

def get_user_by_id(user_id: str) -> dict:
    """Get user by ID."""
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return None
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "created_at": user["created_at"],  # Include created_at
        "is_active": user.get("is_active", True)
    }

def get_user_by_email(email: str) -> dict:
    """Get user by email."""
    user = users_collection.find_one({"email": email})
    if not user:
        return None
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "created_at": user["created_at"],  # Include created_at
        "is_active": user.get("is_active", True)
    }