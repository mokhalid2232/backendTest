from fastapi import APIRouter, HTTPException, Depends,status
from config import grades_collection, attendance_collection
from auth_utils import require_authenticated, require_teacher, require_student
from typing import List, Dict

router = APIRouter()

@router.get("/grades/{student_id}")
def get_student_grades(student_id: str, user_data: dict = Depends(require_authenticated)) -> List[Dict]:
    """
    Fetch all grades for a student.
    AUTHENTICATED ACCESS REQUIRED
    - Students can only see their own grades
    - Teachers can see any student's grades
    """
    try:
        # Students can only access their own grades
        if user_data["role"] == "student" and user_data["user_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only view their own grades"
            )
        
        print(f"📊 {user_data['role']} {user_data['email']} fetching grades for student: {student_id}")
        grades = grades_collection.find({"student_id": student_id})
        grades_list = list(grades)
        
        # Convert ObjectId to string for JSON serialization
        for grade in grades_list:
            grade["_id"] = str(grade["_id"])
            
        print(f"✅ Found {len(grades_list)} grades for student {student_id}")
        return grades_list
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching grades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attendance/{student_id}")
def get_student_attendance(student_id: str, user_data: dict = Depends(require_authenticated)) -> Dict:
    """
    Fetch attendance data for a student.
    AUTHENTICATED ACCESS REQUIRED
    - Students can only see their own attendance
    - Teachers can see any student's attendance
    """
    try:
        # Students can only access their own attendance
        if user_data["role"] == "student" and user_data["user_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only view their own attendance"
            )
            
        print(f"📅 {user_data['role']} {user_data['email']} fetching attendance for student: {student_id}")
        attendance = attendance_collection.find({"student_id": student_id})
        attendance_list = list(attendance)
        
        # Convert ObjectId to string for JSON serialization
        for record in attendance_list:
            record["_id"] = str(record["_id"])
            
        print(f"✅ Found {len(attendance_list)} attendance records for student {student_id}")
        return {"attendance": attendance_list}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{student_id}")
def get_recommendations(student_id: str, user_data: dict = Depends(require_authenticated)) -> Dict:
    """
    Generate study recommendations based on grades.
    AUTHENTICATED ACCESS REQUIRED
    - Students can only get their own recommendations
    - Teachers can get any student's recommendations
    """
    try:
        # Students can only access their own recommendations
        if user_data["role"] == "student" and user_data["user_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only view their own recommendations"
            )
            
        print(f"💡 {user_data['role']} {user_data['email']} generating recommendations for student: {student_id}")
        grades = list(grades_collection.find({"student_id": student_id}))
        weak_subjects = []
        
        for grade in grades:
            if grade.get("score", 100) < 60:
                weak_subjects.append(grade["subject"])
        
        recommendations = {
            "student_id": student_id,
            "focus_on": weak_subjects,
            "advice": "Focus on these subjects for improvement" if weak_subjects else "Keep up the good work!",
            "weak_subjects_count": len(weak_subjects),
            "generated_by": user_data["email"]
        }
        
        print(f"✅ Generated recommendations for student {student_id}")
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grades/{student_id}")
def add_student_grade(
    student_id: str, 
    subject: str, 
    score: float, 
    quiz_id: str = "demo_quiz",
    user_data: dict = Depends(require_teacher)
):
    """
    Add a grade for a student.
    TEACHER ACCESS REQUIRED
    """
    try:
        from datetime import datetime
        
        grade_data = {
            "student_id": student_id,
            "subject": subject,
            "score": score,
            "quiz_id": quiz_id,
            "added_by": user_data["user_id"],
            "timestamp": datetime.utcnow()
        }
        
        result = grades_collection.insert_one(grade_data)
        print(f"✅ Teacher {user_data['email']} added grade for student {student_id}: {subject} - {score}%")
        
        return {
            "message": "Grade added successfully",
            "grade_id": str(result.inserted_id),
            "added_by": user_data["email"]
        }
        
    except Exception as e:
        print(f"❌ Error adding grade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attendance/{student_id}")
def mark_attendance(
    student_id: str, 
    date: str, 
    status: str = "present", 
    subject: str = "General",
    user_data: dict = Depends(require_teacher)
):
    """
    Mark attendance for a student.
    TEACHER ACCESS REQUIRED
    """
    try:
        from datetime import datetime
        
        attendance_data = {
            "student_id": student_id,
            "date": date,
            "status": status,
            "subject": subject,
            "marked_by": user_data["user_id"],
            "marked_at": datetime.utcnow()
        }
        
        result = attendance_collection.insert_one(attendance_data)
        print(f"✅ Teacher {user_data['email']} marked attendance for student {student_id}: {date} - {status}")
        
        return {
            "message": "Attendance marked successfully",
            "attendance_id": str(result.inserted_id),
            "marked_by": user_data["email"]
        }
        
    except Exception as e:
        print(f"❌ Error marking attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-grades")
def get_my_grades(user_data: dict = Depends(require_student)) -> List[Dict]:
    """
    Students can get their own grades.
    STUDENT ACCESS REQUIRED
    """
    try:
        student_id = user_data["user_id"]
        print(f"📊 Student {user_data['email']} fetching their own grades")
        
        grades = grades_collection.find({"student_id": student_id})
        grades_list = list(grades)
        
        # Convert ObjectId to string for JSON serialization
        for grade in grades_list:
            grade["_id"] = str(grade["_id"])
            
        return grades_list
        
    except Exception as e:
        print(f"❌ Error fetching grades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-attendance")
def get_my_attendance(user_data: dict = Depends(require_student)) -> Dict:
    """
    Students can get their own attendance.
    STUDENT ACCESS REQUIRED
    """
    try:
        student_id = user_data["user_id"]
        print(f"📅 Student {user_data['email']} fetching their own attendance")
        
        attendance = attendance_collection.find({"student_id": student_id})
        attendance_list = list(attendance)
        
        # Convert ObjectId to string for JSON serialization
        for record in attendance_list:
            record["_id"] = str(record["_id"])
            
        return {"attendance": attendance_list}
        
    except Exception as e:
        print(f"❌ Error fetching attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))