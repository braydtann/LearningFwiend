#!/usr/bin/env python3
"""
Create test users directly in MongoDB for testing
"""

import pymongo
import uuid
from datetime import datetime
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def create_users():
    """Create admin and student users"""
    
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["learningfwiend_lms"]
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": "brayden.t@covesmart.com",
        "username": "brayden.admin",
        "full_name": "Brayden Admin",
        "role": "admin",
        "department": "Administration",
        "hashed_password": hash_password("Hawaii2020!"),
        "is_temporary_password": False,
        "first_login_required": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "password_updated_at": datetime.utcnow()
    }
    
    # Create student user
    student_user = {
        "id": str(uuid.uuid4()),
        "email": "karlo.student@alder.com",
        "username": "karlo.student",
        "full_name": "Karlo Student",
        "role": "learner",
        "department": "Testing",
        "hashed_password": hash_password("StudentPermanent123!"),
        "is_temporary_password": False,
        "first_login_required": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "password_updated_at": datetime.utcnow()
    }
    
    # Insert users
    try:
        # Check if users already exist
        existing_admin = db.users.find_one({"email": "brayden.t@covesmart.com"})
        existing_student = db.users.find_one({"email": "karlo.student@alder.com"})
        
        if not existing_admin:
            db.users.insert_one(admin_user)
            print("✅ Admin user created: brayden.t@covesmart.com / Hawaii2020!")
        else:
            print("✅ Admin user already exists")
        
        if not existing_student:
            db.users.insert_one(student_user)
            print("✅ Student user created: karlo.student@alder.com / StudentPermanent123!")
        else:
            print("✅ Student user already exists")
        
        # Create some sample data for testing
        create_sample_data(db, admin_user["id"], student_user["id"])
        
        print("🎉 Test users and sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
    
    finally:
        client.close()

def create_sample_data(db, admin_id, student_id):
    """Create sample courses, programs, and classrooms for testing"""
    
    # Create sample courses
    sample_courses = [
        {
            "id": str(uuid.uuid4()),
            "title": "Introduction to Programming",
            "description": "Learn the basics of programming",
            "category": "Technology",
            "duration": "4 weeks",
            "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
            "accessType": "open",
            "learningOutcomes": ["Understand basic programming concepts", "Write simple programs"],
            "modules": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Getting Started",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Introduction to Programming",
                            "type": "video",
                            "content": "Welcome to programming!",
                            "duration": 300
                        }
                    ]
                }
            ],
            "instructorId": admin_id,
            "instructor": "Brayden Admin",
            "status": "published",
            "enrolledStudents": 0,
            "rating": 4.5,
            "reviews": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Web Development Fundamentals",
            "description": "Learn HTML, CSS, and JavaScript",
            "category": "Technology",
            "duration": "6 weeks",
            "thumbnailUrl": "https://images.unsplash.com/photo-1547658719-da2b51169166?w=400",
            "accessType": "open",
            "learningOutcomes": ["Build web pages", "Understand web technologies"],
            "modules": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "HTML Basics",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "HTML Introduction",
                            "type": "text",
                            "content": "HTML is the foundation of web development",
                            "duration": 600
                        }
                    ]
                }
            ],
            "instructorId": admin_id,
            "instructor": "Brayden Admin",
            "status": "published",
            "enrolledStudents": 0,
            "rating": 4.7,
            "reviews": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert courses
    course_ids = []
    for course in sample_courses:
        existing_course = db.courses.find_one({"title": course["title"]})
        if not existing_course:
            db.courses.insert_one(course)
            course_ids.append(course["id"])
            print(f"✅ Created course: {course['title']}")
        else:
            course_ids.append(existing_course["id"])
            print(f"✅ Course already exists: {course['title']}")
    
    # Create sample program
    sample_program = {
        "id": str(uuid.uuid4()),
        "title": "Full Stack Development Program",
        "description": "Complete program for full stack development",
        "departmentId": None,
        "duration": "12 weeks",
        "courseIds": course_ids,
        "nestedProgramIds": [],
        "instructorId": admin_id,
        "instructor": "Brayden Admin",
        "isActive": True,
        "courseCount": len(course_ids),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert program
    existing_program = db.programs.find_one({"title": sample_program["title"]})
    if not existing_program:
        db.programs.insert_one(sample_program)
        program_id = sample_program["id"]
        print(f"✅ Created program: {sample_program['title']}")
    else:
        program_id = existing_program["id"]
        print(f"✅ Program already exists: {sample_program['title']}")
    
    # Create sample classroom
    sample_classroom = {
        "id": str(uuid.uuid4()),
        "title": "Development Bootcamp Class",
        "description": "Intensive development training",
        "instructorId": admin_id,
        "instructor": "Brayden Admin",
        "studentIds": [student_id],
        "courseIds": course_ids,
        "programIds": [program_id],
        "startDate": datetime.utcnow(),
        "endDate": None,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert classroom
    existing_classroom = db.classrooms.find_one({"title": sample_classroom["title"]})
    if not existing_classroom:
        db.classrooms.insert_one(sample_classroom)
        print(f"✅ Created classroom: {sample_classroom['title']}")
        
        # Create enrollments for the student
        for course_id in course_ids:
            enrollment = {
                "id": str(uuid.uuid4()),
                "userId": student_id,
                "courseId": course_id,
                "studentId": student_id,
                "courseName": next(c["title"] for c in sample_courses if c["id"] == course_id),
                "studentName": "Karlo Student",
                "enrollmentDate": datetime.utcnow(),
                "enrolledAt": datetime.utcnow(),
                "progress": 25.0,  # Some progress for testing
                "lastAccessedAt": None,
                "completedAt": None,
                "grade": None,
                "status": "active",
                "isActive": True,
                "enrolledBy": admin_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            existing_enrollment = db.enrollments.find_one({"userId": student_id, "courseId": course_id})
            if not existing_enrollment:
                db.enrollments.insert_one(enrollment)
                print(f"✅ Created enrollment for course: {enrollment['courseName']}")
            else:
                print(f"✅ Enrollment already exists for course: {enrollment['courseName']}")
    else:
        print(f"✅ Classroom already exists: {sample_classroom['title']}")

if __name__ == "__main__":
    create_users()