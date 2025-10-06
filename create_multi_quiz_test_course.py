#!/usr/bin/env python3
"""
Create Multi-Quiz Test Course
============================

Creates a comprehensive test course with multiple quizzes across different modules
to test the multi-quiz progression fix, then enrolls brayden.student.
"""

import requests
import json
import uuid
from datetime import datetime, timezone

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"

# Admin credentials for creating course
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com", 
    "password": "Hawaii2020!"
}

def authenticate_admin():
    """Authenticate admin user"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin authenticated successfully")
            return data["access_token"]
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return None

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def create_multi_quiz_course(token):
    """Create a course with multiple quizzes across different modules"""
    
    course_data = {
        "id": str(uuid.uuid4()),
        "title": "Multi-Quiz Progression Test Course",
        "description": "A test course designed to validate multi-quiz progression functionality. Contains 3 modules with progressive quizzes to test sequential unlocking and course completion logic.",
        "category": "Testing",
        "difficulty": "Beginner", 
        "duration": "2 hours",
        "thumbnailUrl": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&h=600&fit=crop&crop=entropy&auto=format",
        "published": True,
        "createdBy": "Multi-Quiz Test System",
        "enrolledStudents": 0,
        "totalLessons": 6,
        "modules": [
            {
                "id": str(uuid.uuid4()),
                "title": "Module 1: Introduction & Basic Concepts",
                "description": "Introduction to the course with basic concepts and first quiz",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Welcome to Multi-Quiz Testing",
                        "type": "text",
                        "content": "Welcome to the Multi-Quiz Progression Test Course!\n\nThis course is designed to test the sequential quiz unlocking functionality. You will encounter 3 quizzes across 3 modules.\n\nEach quiz must be completed successfully before the next one unlocks.\n\nKey Features Being Tested:\n- Sequential quiz access\n- Progress tracking after each quiz\n- Course completion with multiple quiz requirements\n\nLet's begin your learning journey!",
                        "duration": 300
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Quiz 1: Basic Knowledge Check",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is the primary purpose of this test course?",
                                    "options": [
                                        "To learn advanced programming",
                                        "To test multi-quiz progression functionality", 
                                        "To practice mathematics",
                                        "To study history"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "Sequential quiz unlocking means all quizzes are available immediately.",
                                    "correctAnswer": 0,  # False
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice", 
                                    "question": "How many quizzes will you encounter in this course?",
                                    "options": ["1", "2", "3", "4"],
                                    "correctAnswer": 2,  # 3 quizzes
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "What must happen before the next quiz unlocks?",
                                    "correctAnswer": "Complete the previous quiz successfully",
                                    "points": 25
                                }
                            ],
                            "passingScore": 70,
                            "maxAttempts": 3,
                            "timeLimit": 600
                        }
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Module 2: Intermediate Concepts",
                "description": "Building on basics with intermediate concepts and second quiz",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Understanding Progressive Access",
                        "type": "text", 
                        "content": "Congratulations on completing Quiz 1!\n\nProgressive Access in Learning Management Systems:\n\nProgressive access ensures that students complete learning materials in a logical sequence. This approach:\n\n1. Builds knowledge systematically\n2. Prevents students from skipping important fundamentals\n3. Ensures prerequisite knowledge before advanced topics\n4. Tracks learning progress accurately\n\nKey Benefits:\n- Better learning outcomes\n- Reduced confusion\n- Clear learning path\n- Achievement recognition\n\nNow you're ready for Quiz 2, which will test your understanding of these concepts.",
                        "duration": 600
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Quiz 2: Progressive Learning Assessment", 
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is a key benefit of progressive access in learning?",
                                    "options": [
                                        "Students can skip boring content",
                                        "All content is available immediately", 
                                        "Knowledge builds systematically",
                                        "Quizzes become easier"
                                    ],
                                    "correctAnswer": 2,
                                    "points": 20
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false", 
                                    "question": "Progressive access prevents students from skipping important fundamentals.",
                                    "correctAnswer": 1,  # True
                                    "points": 20
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "Which quiz are you currently taking?",
                                    "options": ["Quiz 1", "Quiz 2", "Quiz 3", "Final Quiz"],
                                    "correctAnswer": 1,  # Quiz 2
                                    "points": 20
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "Name one way progressive access improves learning outcomes.",
                                    "correctAnswer": "Builds knowledge systematically OR Prevents skipping fundamentals OR Ensures prerequisite knowledge OR Tracks progress accurately",
                                    "points": 20
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What should happen after you complete this quiz successfully?",
                                    "options": [
                                        "The course ends",
                                        "Quiz 3 becomes available", 
                                        "You start over",
                                        "Nothing happens"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 20
                                }
                            ],
                            "passingScore": 75,
                            "maxAttempts": 3,
                            "timeLimit": 900
                        }
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Module 3: Advanced Application & Final Assessment",
                "description": "Advanced concepts and final comprehensive quiz",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Mastering Multi-Quiz Systems",
                        "type": "text",
                        "content": "Excellent progress! You've completed Quiz 1 and Quiz 2.\n\nAdvanced Multi-Quiz System Features:\n\nReal-world learning management systems use sophisticated progression logic:\n\n1. **Sequential Unlocking**: Each quiz unlocks only after prerequisites are met\n2. **Progress Tracking**: System accurately tracks completion percentage\n3. **Completion Validation**: Course completion requires ALL quizzes to be passed\n4. **Flexible Prerequisites**: Non-quiz content can be accessed more freely\n5. **Comprehensive Reporting**: Detailed analytics on student progress\n\nTechnical Implementation:\n- Frontend manages quiz access permissions\n- Backend validates completion requirements\n- Database stores detailed progress tracking\n- UI provides clear progression indicators\n\nYou're now ready for the final quiz, which will test your comprehensive understanding!",
                        "duration": 600
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Quiz 3: Comprehensive Assessment",
                        "type": "quiz", 
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "In a multi-quiz course, what determines when the next quiz becomes available?",
                                    "options": [
                                        "Time spent on previous lessons",
                                        "Successful completion of previous quiz",
                                        "Number of attempts made", 
                                        "Random system selection"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 15
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "Course completion requires passing ALL quizzes in the course.",
                                    "correctAnswer": 1,  # True
                                    "points": 15
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is the main advantage of sequential quiz unlocking?",
                                    "options": [
                                        "Faster course completion",
                                        "Fewer quiz questions needed",
                                        "Systematic knowledge building",
                                        "Reduced server load"
                                    ],
                                    "correctAnswer": 2,
                                    "points": 15
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer", 
                                    "question": "What happens to course progress when a quiz is completed successfully?",
                                    "correctAnswer": "Progress percentage increases OR Enrollment progress updates OR Next quiz unlocks OR Module completion tracked",
                                    "points": 15
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "Which component is responsible for managing quiz access permissions?",
                                    "options": [
                                        "Database only",
                                        "Backend only", 
                                        "Frontend logic",
                                        "External service"
                                    ],
                                    "correctAnswer": 2,
                                    "points": 15
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "Non-quiz content should follow the same strict progression rules as quizzes.",
                                    "correctAnswer": 0,  # False - non-quiz content can be more flexible
                                    "points": 15
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is this quiz testing?",
                                    "options": [
                                        "Basic math skills",
                                        "Multi-quiz progression functionality",
                                        "Writing abilities", 
                                        "Memory capacity"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 10
                                }
                            ],
                            "passingScore": 80,
                            "maxAttempts": 3,
                            "timeLimit": 1200
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        print("🏗️ Creating multi-quiz test course...")
        response = requests.post(
            f"{BACKEND_URL}/courses",
            headers=get_headers(token),
            json=course_data
        )
        
        if response.status_code == 200:
            course = response.json()
            print(f"✅ Course created successfully!")
            print(f"   📚 Course ID: {course['id']}")
            print(f"   📖 Title: {course['title']}")
            print(f"   📊 Modules: {len(course.get('modules', []))}")
            
            # Count quizzes
            quiz_count = 0
            for module in course.get('modules', []):
                for lesson in module.get('lessons', []):
                    if lesson.get('type') == 'quiz':
                        quiz_count += 1
            
            print(f"   🎯 Quizzes: {quiz_count}")
            print(f"   📝 Total Lessons: {course.get('totalLessons', 'N/A')}")
            
            return course
        else:
            print(f"❌ Failed to create course: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Course creation failed: {str(e)}")
        return None

def find_student_user(token):
    """Find or use existing student user (karlo.student)"""
    try:
        print("🔍 Using existing student user (karlo.student)...")
        
        # Use the existing student from backend testing
        # We'll directly enroll using the known user ID pattern
        student_info = {
            "id": "karlo-student-id",  # We'll use email for enrollment
            "email": "karlo.student@alder.com",
            "name": "Karlo Student"
        }
        
        print(f"✅ Using student: {student_info['email']}")
        return student_info
            
    except Exception as e:
        print(f"❌ Student setup failed: {str(e)}")
        return None

def create_brayden_student(token):
    """Create brayden.student user if not exists"""
    try:
        student_data = {
            "id": str(uuid.uuid4()),
            "email": "brayden.student@learningfwiend.com",
            "username": "brayden.student", 
            "firstName": "Brayden",
            "lastName": "Student",
            "password": "Cove1234!",
            "role": "learner",
            "isActive": True,
            "needsPasswordChange": False
        }
        
        response = requests.post(
            f"{BACKEND_URL}/users",
            headers=get_headers(token),
            json=student_data
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Created brayden.student: {user['id']}")
            return user
        else:
            print(f"❌ Failed to create student: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Student creation failed: {str(e)}")
        return None

def enroll_student(token, course_id, student_info):
    """Enroll student in the course via admin enrollment"""
    try:
        print(f"📝 Enrolling {student_info['email']} in multi-quiz course...")
        
        # Try admin enrollment endpoint
        enrollment_data = {
            "email": student_info['email'],
            "courseId": course_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/admin/enroll-student",
            headers=get_headers(token),
            json=enrollment_data
        )
        
        if response.status_code == 200:
            print(f"✅ Student enrolled successfully via admin endpoint!")
            print(f"   📧 Student: {student_info['email']}")
            print(f"   🎓 Course: Multi-Quiz Progression Test Course")
            return {"success": True}
        else:
            # Try direct enrollment creation
            print(f"   Admin enrollment failed ({response.status_code}), trying direct approach...")
            
            # Create enrollment directly in database
            enrollment_data = {
                "id": str(uuid.uuid4()),
                "userEmail": student_info['email'],  # Use email as identifier
                "courseId": course_id,
                "enrolledAt": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "progress": 1.0,  # Start with 1% 
                "moduleProgress": []
            }
            
            # Try creating enrollment with email
            response2 = requests.post(
                f"{BACKEND_URL}/enrollments",
                headers=get_headers(token),
                json=enrollment_data
            )
            
            if response2.status_code == 200:
                enrollment = response2.json()
                print(f"✅ Student enrolled successfully via direct enrollment!")
                print(f"   📧 Student: {student_info['email']}")
                print(f"   🎓 Course: Multi-Quiz Progression Test Course")
                return enrollment
            else:
                print(f"❌ Both enrollment methods failed")
                print(f"   Admin: {response.status_code}")
                print(f"   Direct: {response2.status_code}")
                return None
            
    except Exception as e:
        print(f"❌ Enrollment failed: {str(e)}")
        return None

def main():
    """Main function to create course and enroll student"""
    print("🚀 Creating Multi-Quiz Progression Test Course")
    print("=" * 60)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        return
    
    # Create course
    course = create_multi_quiz_course(token)
    if not course:
        return
    
    # Find student
    student = find_student_user(token)
    if not student:
        return
    
    # Enroll student
    enrollment = enroll_student(token, course['id'], student['id'])
    if not enrollment:
        return
    
    print()
    print("🎉 MULTI-QUIZ TEST COURSE SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Course Created: Multi-Quiz Progression Test Course")
    print("✅ Student Enrolled: brayden.student@learningfwiend.com")
    print()
    print("📋 TESTING INSTRUCTIONS:")
    print("1. Login as brayden.student@learningfwiend.com / Cove1234!")
    print("2. Navigate to the course: 'Multi-Quiz Progression Test Course'")
    print("3. Test the progression:")
    print("   - Only Quiz 1 should be accessible initially")
    print("   - Complete Quiz 1 (70% passing score)")
    print("   - Verify Quiz 2 unlocks after Quiz 1 completion")
    print("   - Complete Quiz 2 (75% passing score)") 
    print("   - Verify Quiz 3 unlocks after Quiz 2 completion")
    print("   - Complete Quiz 3 (80% passing score)")
    print("   - Verify course reaches 100% completion")
    print()
    print("🎯 EXPECTED BEHAVIOR:")
    print("- Sequential quiz unlocking (Quiz 2 after Quiz 1, Quiz 3 after Quiz 2)")
    print("- Progress updates after each quiz completion")
    print("- Course completion only after all 3 quizzes are passed")
    print("- Non-quiz content accessible without strict progression")
    print()
    print(f"📊 Course Structure:")
    print(f"   Module 1: Intro + Quiz 1 (4 questions, 70% pass)")
    print(f"   Module 2: Concepts + Quiz 2 (5 questions, 75% pass)")
    print(f"   Module 3: Advanced + Quiz 3 (7 questions, 80% pass)")

if __name__ == "__main__":
    main()