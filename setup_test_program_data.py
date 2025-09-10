#!/usr/bin/env python3
"""
Script to create test program and classroom data for the investigation
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def create_test_data():
    """Create test program, courses, and classroom data."""
    
    # Get admin and student users
    admin_user = await db.users.find_one({"email": "brayden.t@covesmart.com"})
    student_user = await db.users.find_one({"email": "brayden.student@learningfwiend.com"})
    
    if not admin_user or not student_user:
        print("❌ Required users not found!")
        return
    
    print(f"✅ Found admin: {admin_user['full_name']} (ID: {admin_user['id']})")
    print(f"✅ Found student: {student_user['full_name']} (ID: {student_user['id']})")
    
    # Create test courses first
    test_courses = []
    for i in range(1, 4):
        course_data = {
            "id": str(uuid.uuid4()),
            "title": f"Test Course {i}",
            "description": f"This is test course {i} for program testing",
            "category": "Programming",
            "duration": "4 weeks",
            "thumbnailUrl": f"https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=300&fit=crop&crop=center",
            "accessType": "open",
            "learningOutcomes": [f"Learn test skill {i}", f"Master test concept {i}"],
            "modules": [
                {
                    "id": str(uuid.uuid4()),
                    "title": f"Module 1 - Introduction to Test {i}",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": f"Lesson 1.1 - Basics of Test {i}",
                            "type": "video",
                            "content": f"Introduction to test course {i}",
                            "duration": 15
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "title": f"Lesson 1.2 - Quiz for Test {i}",
                            "type": "quiz",
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": f"What is the main topic of test course {i}?",
                                    "options": [f"Test {i}", "Other topic", "Random topic", "None"],
                                    "correctAnswer": 0
                                }
                            ]
                        }
                    ]
                }
            ],
            "instructorId": admin_user['id'],
            "instructor": admin_user['full_name'],
            "status": "published",
            "enrolledStudents": 0,
            "rating": 4.5,
            "reviews": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Check if course already exists
        existing_course = await db.courses.find_one({"title": course_data["title"]})
        if not existing_course:
            await db.courses.insert_one(course_data)
            print(f"✅ Created course: {course_data['title']} (ID: {course_data['id']})")
        else:
            course_data = existing_course
            print(f"✅ Found existing course: {course_data['title']} (ID: {course_data['id']})")
        
        test_courses.append(course_data)
    
    # Create 'test program 2'
    program_data = {
        "id": str(uuid.uuid4()),
        "title": "Test Program 2",
        "description": "This is the test program 2 for investigating enrollment issues",
        "departmentId": None,
        "duration": "12 weeks",
        "courseIds": [course['id'] for course in test_courses],  # Include all test courses
        "nestedProgramIds": [],
        "instructorId": admin_user['id'],
        "instructor": admin_user['full_name'],
        "isActive": True,
        "courseCount": len(test_courses),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if program already exists
    existing_program = await db.programs.find_one({"title": "Test Program 2"})
    if not existing_program:
        await db.programs.insert_one(program_data)
        print(f"✅ Created program: {program_data['title']} (ID: {program_data['id']})")
    else:
        program_data = existing_program
        print(f"✅ Found existing program: {program_data['title']} (ID: {program_data['id']})")
    
    # Create classroom that includes the program and assigns the student
    classroom_data = {
        "id": str(uuid.uuid4()),
        "title": "Test Classroom for Program 2",
        "description": "Classroom that includes test program 2 and assigns brayden.student",
        "instructorId": admin_user['id'],
        "instructor": admin_user['full_name'],
        "studentIds": [student_user['id']],  # Assign brayden.student
        "courseIds": [],  # Direct courses (empty for this test)
        "programIds": [program_data['id']],  # Include test program 2
        "startDate": datetime.utcnow(),
        "endDate": None,  # No end date
        "isActive": True,
        "studentCount": 1,
        "courseCount": len(test_courses),  # Courses from program
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if classroom already exists
    existing_classroom = await db.classrooms.find_one({"title": classroom_data["title"]})
    if not existing_classroom:
        await db.classrooms.insert_one(classroom_data)
        print(f"✅ Created classroom: {classroom_data['title']} (ID: {classroom_data['id']})")
        
        # Auto-enroll student in program courses (simulate the auto-enrollment logic)
        for course in test_courses:
            enrollment_data = {
                "id": str(uuid.uuid4()),
                "userId": student_user['id'],
                "courseId": course['id'],
                "studentId": student_user['id'],
                "courseName": course['title'],
                "studentName": student_user['full_name'],
                "enrollmentDate": datetime.utcnow(),
                "enrolledAt": datetime.utcnow(),
                "progress": 0.0,
                "lastAccessedAt": None,
                "completedAt": None,
                "grade": None,
                "status": "active",
                "isActive": True,
                "enrolledBy": admin_user['id'],  # Enrolled by admin via classroom
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Check if enrollment already exists
            existing_enrollment = await db.enrollments.find_one({
                "userId": student_user['id'],
                "courseId": course['id']
            })
            
            if not existing_enrollment:
                await db.enrollments.insert_one(enrollment_data)
                print(f"✅ Auto-enrolled student in: {course['title']}")
                
                # Update course enrollment count
                await db.courses.update_one(
                    {"id": course['id']},
                    {"$inc": {"enrolledStudents": 1}}
                )
            else:
                print(f"✅ Student already enrolled in: {course['title']}")
    else:
        classroom_data = existing_classroom
        print(f"✅ Found existing classroom: {classroom_data['title']} (ID: {classroom_data['id']})")
    
    print("\n🎯 TEST DATA SUMMARY:")
    print(f"   Program: {program_data['title']} (ID: {program_data['id']})")
    print(f"   Courses: {len(test_courses)} courses in program")
    print(f"   Classroom: {classroom_data['title']} (ID: {classroom_data['id']})")
    print(f"   Student: {student_user['full_name']} assigned to classroom")
    print(f"   Expected: Student should be auto-enrolled in all {len(test_courses)} program courses")

async def main():
    try:
        await create_test_data()
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())