import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

# Initialize Firebase Admin
firebase_credentials_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if firebase_credentials_path and os.path.exists(firebase_credentials_path):
    cred = credentials.Certificate(firebase_credentials_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin initialized successfully")
else:
    print("⚠️  Firebase credentials not found - authentication will be disabled")

# MongoDB Connection
mongodb_uri = os.getenv("MONGODB_URI")
database_name = os.getenv("DATABASE_NAME", "educational_assistant")
print(f"🔗 Connecting to MongoDB: {database_name}")
client = MongoClient(mongodb_uri)
db = client[database_name]

# Collections
materials_collection = db["materials"]
quizzes_collection = db["quizzes"]
summaries_collection = db["summaries"]
grades_collection = db["grades"]
attendance_collection = db["attendance"]
users_collection = db["users"]

# Gemini API key (for reference - actual config is in gemini_client.py)
gemini_api_key = os.getenv("GEMINI_API_KEY") # ← Set the API key

ENV = os.getenv("ENV", "development")