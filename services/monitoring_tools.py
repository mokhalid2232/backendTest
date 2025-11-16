from config import grades_collection, attendance_collection, recommendations_collection
from datetime import datetime
from bson import ObjectId

def record_grade(student_id: str, quiz_id: str, grade: float, subject: str = None, feedback: str = None):
    """
    Store or update a student's grade for a specific quiz.
    """
    grade_data = {
        "student_id": student_id,
        "quiz_id": quiz_id,
        "grade": grade,
        "subject": subject,
        "feedback": feedback,
        "timestamp": datetime.utcnow()
    }
    
    # Use composite key to avoid duplicates
    grades_collection.update_one(
        {"student_id": student_id, "quiz_id": quiz_id},
        {"$set": grade_data},
        upsert=True
    )

def get_student_grades(student_id: str):
    """
    Retrieve all grades for a specific student.
    """
    grades = grades_collection.find({"student_id": student_id})
    return list(grades)

def get_grades_by_subject(subject: str):
    """
    Retrieve all grades for a specific subject.
    """
    grades = grades_collection.find({"subject": subject})
    return list(grades)

def get_class_grades(section: str, subject: str = None):
    """
    Retrieve all grades for a specific class section.
    """
    query = {"section": section}
    if subject:
        query["subject"] = subject
    
    grades = grades_collection.find(query)
    return list(grades)

def mark_attendance(student_id: str, date: str, status: str = "present", section: str = None, subject: str = None):
    """
    Mark student attendance for a specific date.
    """
    attendance_data = {
        "student_id": student_id,
        "date": date,
        "status": status,
        "section": section,
        "subject": subject,
        "marked_at": datetime.utcnow()
    }
    
    # Use composite key to avoid duplicates for same date
    attendance_collection.update_one(
        {"student_id": student_id, "date": date},
        {"$set": attendance_data},
        upsert=True
    )

def get_attendance_by_student(student_id: str):
    """
    Retrieve all attendance records for a student.
    """
    attendance = attendance_collection.find({"student_id": student_id})
    return list(attendance)

def get_attendance_by_date(date: str, section: str = None):
    """
    Retrieve attendance records for a specific date.
    """
    query = {"date": date}
    if section:
        query["section"] = section
    
    attendance = attendance_collection.find(query)
    return list(attendance)

def get_attendance_by_section(section: str, start_date: str = None, end_date: str = None):
    """
    Retrieve attendance records for a specific section.
    """
    query = {"section": section}
    
    if start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        query["date"] = {"$gte": start_date}
    elif end_date:
        query["date"] = {"$lte": end_date}
    
    attendance = attendance_collection.find(query)
    return list(attendance)

def generate_recommendations(student_id: str):
    """
    Generate study recommendations based on grades.
    This can be replaced by more advanced ML-based insights later.
    """
    grades = get_student_grades(student_id)
    
    if not grades:
        return ["No data available to generate recommendations."]
    
    # Calculate average grade
    avg_grade = sum([g["grade"] for g in grades]) / len(grades)
    
    # Identify weak subjects (below 60%)
    weak_subjects = []
    subject_grades = {}
    
    for grade in grades:
        subject = grade.get("subject", "Unknown")
        if subject not in subject_grades:
            subject_grades[subject] = []
        subject_grades[subject].append(grade["grade"])
    
    for subject, grades_list in subject_grades.items():
        subject_avg = sum(grades_list) / len(grades_list)
        if subject_avg < 60:
            weak_subjects.append(subject)
    
    # Generate recommendations based on performance
    recommendations = []
    
    if avg_grade >= 85:
        recommendations = [
            "Keep up the great work!",
            "Consider mentoring your peers.",
            "Challenge yourself with advanced topics."
        ]
    elif avg_grade >= 70:
        recommendations = [
            "You're doing well, but there's room for improvement.",
            "Review quizzes regularly to maintain your performance.",
            "Focus on consistent study habits."
        ]
    elif avg_grade >= 60:
        recommendations = [
            "Focus more on weak areas.",
            "Consider forming study groups.",
            "Review materials before each class."
        ]
    else:
        recommendations = [
            "Seek help from the teacher during office hours.",
            "Focus on fundamental concepts.",
            "Create a structured study schedule.",
            "Practice with additional exercises."
        ]
    
    # Add subject-specific recommendations
    if weak_subjects:
        recommendations.append(f"Focus more on: {', '.join(weak_subjects)}")
    
    # Save recommendations to database
    recommendation_data = {
        "student_id": student_id,
        "recommendations": recommendations,
        "average_grade": avg_grade,
        "weak_subjects": weak_subjects,
        "generated_at": datetime.utcnow()
    }
    
    recommendations_collection.insert_one(recommendation_data)
    
    return recommendations

def get_student_recommendations(student_id: str):
    """
    Get the latest recommendations for a student.
    """
    recommendations = recommendations_collection.find(
        {"student_id": student_id}
    ).sort("generated_at", -1).limit(1)
    
    rec_list = list(recommendations)
    return rec_list[0] if rec_list else None

def get_attendance_stats(student_id: str, start_date: str = None, end_date: str = None):
    """
    Calculate attendance statistics for a student.
    """
    query = {"student_id": student_id}
    
    if start_date and end_date:
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    attendance_records = list(attendance_collection.find(query))
    
    if not attendance_records:
        return {
            "total_classes": 0,
            "present_count": 0,
            "attendance_rate": 0,
            "absent_count": 0
        }
    
    present_count = sum(1 for record in attendance_records if record.get("status") == "present")
    absent_count = sum(1 for record in attendance_records if record.get("status") == "absent")
    total_classes = len(attendance_records)
    
    attendance_rate = (present_count / total_classes) * 100 if total_classes > 0 else 0
    
    return {
        "total_classes": total_classes,
        "present_count": present_count,
        "absent_count": absent_count,
        "attendance_rate": round(attendance_rate, 2)
    }