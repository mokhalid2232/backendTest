import uvicorn # ASGI server to run FastAPI apps
from fastapi import FastAPI
from api.routes_teacher import router as teacher_router
from api.routes_student import router as student_router
from fastapi.middleware.cors import CORSMiddleware
from api.routes_materials import router as materials_router
from api.routes_student_materials import router as student_materials_router
from api.routes_monitoring import router as monitoring_router
from api.routes_auth import router as auth_router

app = FastAPI(
title="AI Learning Assistant",
description="AI-powered app for generating quizzes and summarizing lectures",
version="1.0.0"
)
# Debug: Print all routes on startup
@app.on_event("startup")
async def print_routes():
    print("🚀 REGISTERED ROUTES:")
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            print(f"  {list(route.methods)} {route.path}")
            
#Enable CORS for frontend-backend communication
app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # In production, specify allowed origins
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)
#Register routers
app.include_router(teacher_router, prefix="/api/teacher", tags=["Teacher"])
app.include_router(student_router, prefix="/api/student", tags=["Student"])
app.include_router(materials_router, prefix="/materials", tags=["Materials"])
app.include_router(student_materials_router, prefix="/api", tags=["Student Materials"])
app.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
#Health check
@app.get("/")
def root():
	return {"message": "AI Learning Assistant is running"}
#Run the app using uvicorn
if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)