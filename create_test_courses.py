#!/usr/bin/env python3
"""
Create Multiple Test Courses
============================

Creates several different test courses for ongoing testing of multi-quiz progression
and subjective question features without needing to recreate courses each time.
"""

import requests
import json
import uuid
from datetime import datetime, timezone

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"

# Admin credentials
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

def create_simple_quiz_course(token):
    """Course 1: Simple Single-Quiz Course (for basic testing)"""
    course_data = {
        "id": str(uuid.uuid4()),
        "title": "Simple Quiz Test Course",
        "description": "A simple course with one lesson and one quiz for basic functionality testing.",
        "category": "Testing",
        "difficulty": "Beginner", 
        "duration": "30 minutes",
        "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=600&fit=crop",
        "published": True,
        "createdBy": "Test System",
        "enrolledStudents": 0,
        "totalLessons": 2,
        "modules": [
            {
                "id": str(uuid.uuid4()),
                "title": "Module 1: Basic Knowledge",
                "description": "Simple module with content and a quiz",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Introduction to Testing",
                        "type": "text",
                        "content": "Welcome! This is a simple course to test basic quiz functionality.\n\nKey concepts:\n- Course enrollment\n- Lesson completion\n- Quiz taking\n- Progress tracking\n\nThis lesson should be quick to complete so you can focus on testing the quiz.",
                        "duration": 300
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Basic Knowledge Quiz",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is the primary purpose of this course?",
                                    "options": [
                                        "Learning advanced mathematics",
                                        "Testing quiz functionality", 
                                        "Studying history",
                                        "Programming basics"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 50
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "Name one benefit of automated testing.",
                                    "correctAnswer": "Saves time OR Reduces errors OR Improves quality OR Increases reliability",
                                    "points": 50
                                }
                            ],
                            "passingScore": 60,
                            "maxAttempts": 3,
                            "timeLimit": 300
                        }
                    }
                ]
            }
        ]
    }
    return create_course(token, course_data, "Simple Quiz Test Course")

def create_two_quiz_course(token):
    """Course 2: Two-Quiz Sequential Course (for progression testing)"""
    course_data = {
        "id": str(uuid.uuid4()),
        "title": "Two-Quiz Progression Course",
        "description": "A course with two quizzes to test sequential unlocking functionality.",
        "category": "Testing",
        "difficulty": "Intermediate", 
        "duration": "1 hour",
        "thumbnailUrl": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=600&fit=crop",
        "published": True,
        "createdBy": "Test System",
        "enrolledStudents": 0,
        "totalLessons": 4,
        "modules": [
            {
                "id": str(uuid.uuid4()),
                "title": "Module 1: Foundation",
                "description": "First module with introduction and first quiz",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Course Overview",
                        "type": "text",
                        "content": "Welcome to the Two-Quiz Progression Course!\n\nThis course tests:\n- Sequential quiz unlocking\n- Progress tracking\n- Multi-quiz completion\n\nYou'll complete Quiz 1, which will unlock Quiz 2.\nBoth quizzes must be passed to complete the course.",
                        "duration": 200
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Quiz 1: Basic Concepts",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "This is the first quiz in the course.",
                                    "correctAnswer": 1,  # True
                                    "points": 30
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "How many quizzes are in this course?",
                                    "options": ["1", "2", "3", "4"],
                                    "correctAnswer": 1,  # 2 quizzes
                                    "points": 40
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "What should happen after you pass this quiz?",
                                    "correctAnswer": "Quiz 2 unlocks OR Next quiz becomes available OR Can access second quiz",
                                    "points": 30
                                }
                            ],
                            "passingScore": 70,
                            "maxAttempts": 3,
                            "timeLimit": 400
                        }
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Module 2: Advanced Concepts", 
                "description": "Second module with advanced content and final quiz",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Advanced Learning Concepts",
                        "type": "text",
                        "content": "Great job completing Quiz 1!\n\nAdvanced Concepts:\n- Sequential learning builds knowledge systematically\n- Each quiz validates understanding before proceeding\n- Progress tracking ensures completion requirements are met\n\nNow you're ready for Quiz 2, which will complete the course.",
                        "duration": 300
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Quiz 2: Final Assessment",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice", 
                                    "question": "What quiz are you taking now?",
                                    "options": ["Quiz 1", "Quiz 2", "Quiz 3", "Final Quiz"],
                                    "correctAnswer": 1,  # Quiz 2
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "Sequential quiz unlocking improves learning outcomes.",
                                    "correctAnswer": 1,  # True
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "What happens when you complete this quiz successfully?",
                                    "correctAnswer": "Course completion OR Course reaches 100% OR Get certificate OR Finish course",
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is a key benefit of progressive learning?",
                                    "options": [
                                        "Skip difficult content",
                                        "Builds knowledge systematically", 
                                        "Faster completion",
                                        "Fewer requirements"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 25
                                }
                            ],
                            "passingScore": 75,
                            "maxAttempts": 3,
                            "timeLimit": 500
                        }
                    }
                ]
            }
        ]
    }
    return create_course(token, course_data, "Two-Quiz Progression Course")

def create_subjective_heavy_course(token):
    """Course 3: Subjective Question Focus Course (for testing subjective scoring)"""
    course_data = {
        "id": str(uuid.uuid4()),
        "title": "Subjective Assessment Course",
        "description": "A course focused on testing subjective question handling and manual grading workflow.",
        "category": "Testing",
        "difficulty": "Intermediate", 
        "duration": "45 minutes",
        "thumbnailUrl": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800&h=600&fit=crop",
        "published": True,
        "createdBy": "Test System",
        "enrolledStudents": 0,
        "totalLessons": 3,
        "modules": [
            {
                "id": str(uuid.uuid4()),
                "title": "Module 1: Subjective Learning",
                "description": "Module focused on subjective assessment",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Understanding Subjective Assessment",
                        "type": "text",
                        "content": "Welcome to Subjective Assessment Testing!\n\nThis course focuses on:\n- Subjective question handling\n- Manual grading workflow\n- Default scoring for progression\n- Instructor review process\n\nSubjective questions (short-answer, essay) receive full points initially to allow progression, then instructors can review and adjust scores.",
                        "duration": 400
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Mixed Question Types Quiz",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is the main purpose of subjective questions?",
                                    "options": [
                                        "Quick grading",
                                        "Assess deeper understanding", 
                                        "Save time",
                                        "Avoid manual work"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 20
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "Explain one benefit of giving subjective questions full points initially.",
                                    "correctAnswer": "Allows progression OR Prevents blocking OR Maintains learning flow OR Enables continuity",
                                    "points": 30
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "essay",
                                    "question": "Describe how the manual grading workflow benefits both students and instructors. Write 2-3 sentences.",
                                    "correctAnswer": "Students can continue learning without delays while instructors can provide detailed feedback and adjust scores based on quality and understanding demonstrated in responses.",
                                    "points": 30
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "Subjective questions should completely block course progression until manually graded.",
                                    "correctAnswer": 0,  # False
                                    "points": 20
                                }
                            ],
                            "passingScore": 65,
                            "maxAttempts": 3,
                            "timeLimit": 600
                        }
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Subjective-Heavy Quiz",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "What is the most important principle in education technology?",
                                    "correctAnswer": "Accessibility OR User experience OR Learning effectiveness OR Continuous improvement",
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "essay",
                                    "question": "Describe your ideal learning management system. What features would it have and why?",
                                    "correctAnswer": "Student-focused design with progressive learning, clear feedback mechanisms, mobile accessibility, and instructor tools for personalized support and assessment.",
                                    "points": 35
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer", 
                                    "question": "How do you measure learning success?",
                                    "correctAnswer": "Practical application OR Skill demonstration OR Knowledge retention OR Real-world problem solving",
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "What makes online learning effective?",
                                    "correctAnswer": "Engagement OR Interaction OR Clear structure OR Regular feedback OR Practical examples",
                                    "points": 15
                                }
                            ],
                            "passingScore": 70,
                            "maxAttempts": 3,
                            "timeLimit": 900
                        }
                    }
                ]
            }
        ]
    }
    return create_course(token, course_data, "Subjective Assessment Course")

def create_mixed_content_course(token):
    """Course 4: Mixed Content Course (for comprehensive testing)"""
    course_data = {
        "id": str(uuid.uuid4()),
        "title": "Comprehensive Testing Course",
        "description": "A comprehensive course with mixed content types, multiple modules, and various assessment methods.",
        "category": "Testing",
        "difficulty": "Advanced", 
        "duration": "2 hours",
        "thumbnailUrl": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop",
        "published": True,
        "createdBy": "Test System", 
        "enrolledStudents": 0,
        "totalLessons": 8,
        "modules": [
            {
                "id": str(uuid.uuid4()),
                "title": "Module 1: Fundamentals",
                "description": "Basic concepts and initial assessment",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Course Introduction",
                        "type": "text",
                        "content": "Welcome to the Comprehensive Testing Course!\n\nThis course includes:\n- Multiple content types\n- Sequential progression\n- Various question formats\n- Comprehensive assessment\n\nComplete all modules and quizzes to finish the course.",
                        "duration": 300
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Fundamentals Assessment",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "This course is designed for what type of testing?",
                                    "options": ["Basic functionality", "Comprehensive system testing", "Quick validation", "Single features"],
                                    "correctAnswer": 1,
                                    "points": 50
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "Comprehensive testing covers multiple aspects of a system.",
                                    "correctAnswer": 1,  # True
                                    "points": 50
                                }
                            ],
                            "passingScore": 70,
                            "maxAttempts": 3,
                            "timeLimit": 300
                        }
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Module 2: Intermediate Concepts",
                "description": "Building on fundamentals",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Advanced Learning Strategies",
                        "type": "text", 
                        "content": "Building on the fundamentals...\n\nAdvanced strategies include:\n- Systematic progression\n- Multi-modal assessment\n- Continuous feedback\n- Adaptive learning paths\n\nThese concepts prepare you for the intermediate assessment.",
                        "duration": 400
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Strategy Application Quiz",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "What is a key component of adaptive learning?",
                                    "options": ["Fixed curriculum", "Personalized progression", "Uniform assessment", "Standard timing"],
                                    "correctAnswer": 1,
                                    "points": 30
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "Define 'multi-modal assessment' in your own words.",
                                    "correctAnswer": "Using multiple formats OR Different question types OR Various assessment methods OR Comprehensive evaluation approaches",
                                    "points": 40
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "true-false",
                                    "question": "Continuous feedback improves learning outcomes.",
                                    "correctAnswer": 1,  # True
                                    "points": 30
                                }
                            ],
                            "passingScore": 70,
                            "maxAttempts": 3,
                            "timeLimit": 500
                        }
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Module 3: Advanced Application",
                "description": "Practical application and final assessment",
                "lessons": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Practical Applications",
                        "type": "text",
                        "content": "Applying your knowledge in real scenarios...\n\nPractical applications:\n- System integration testing\n- User experience validation\n- Performance assessment\n- Comprehensive evaluation\n\nThe final quiz will test your complete understanding.",
                        "duration": 500
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Real-World Scenarios",
                        "type": "text",
                        "content": "Consider these real-world scenarios:\n\n1. A student struggles with quiz progression\n2. An instructor needs to review subjective answers\n3. A system needs to handle multiple course types\n4. Progress tracking across different learning paths\n\nHow would you address each scenario?",
                        "duration": 400
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Comprehensive Final Assessment",
                        "type": "quiz",
                        "quiz": {
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "In a comprehensive learning system, what is most critical?",
                                    "options": ["Speed", "User experience and learning outcomes", "Cost efficiency", "Technical complexity"],
                                    "correctAnswer": 1,
                                    "points": 20
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "essay",
                                    "question": "Describe how you would design a learning system that balances automated efficiency with personalized instruction.",
                                    "correctAnswer": "Combine automated progression tracking with instructor oversight, provide immediate feedback for objective questions while allowing manual review of subjective responses, and create flexible pathways that adapt to individual learning needs while maintaining quality standards.",
                                    "points": 30
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "short-answer",
                                    "question": "What is the most important factor in student engagement?",
                                    "correctAnswer": "Relevance OR Clear feedback OR Progress visibility OR Interactive content OR Personal connection",
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "type": "multiple-choice",
                                    "question": "How should a system handle quiz progression issues?",
                                    "options": [
                                        "Block all progress until resolved",
                                        "Allow continuation with instructor review",
                                        "Ignore the issues", 
                                        "Reset all progress"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 25
                                }
                            ],
                            "passingScore": 75,
                            "maxAttempts": 3,
                            "timeLimit": 1200
                        }
                    }
                ]
            }
        ]
    }
    return create_course(token, course_data, "Comprehensive Testing Course")

def create_course(token, course_data, course_name):
    """Helper function to create a course"""
    try:
        print(f"🏗️ Creating {course_name}...")
        response = requests.post(
            f"{BACKEND_URL}/courses",
            headers=get_headers(token),
            json=course_data
        )
        
        if response.status_code == 200:
            course = response.json()
            print(f"✅ {course_name} created successfully!")
            print(f"   📚 Course ID: {course['id']}")
            
            # Count quizzes
            quiz_count = 0
            lesson_count = 0
            for module in course.get('modules', []):
                for lesson in module.get('lessons', []):
                    lesson_count += 1
                    if lesson.get('type') == 'quiz':
                        quiz_count += 1
            
            print(f"   🎯 Quizzes: {quiz_count}")
            print(f"   📝 Total Lessons: {lesson_count}")
            print(f"   📊 Modules: {len(course.get('modules', []))}")
            
            return course
        else:
            print(f"❌ Failed to create {course_name}: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ {course_name} creation failed: {str(e)}")
        return None

def main():
    """Main function to create all test courses"""
    print("🚀 Creating Multiple Test Courses for Ongoing Testing")
    print("=" * 70)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        return
    
    courses = []
    
    # Create each course
    course1 = create_simple_quiz_course(token)
    if course1:
        courses.append(course1)
    
    print()
    course2 = create_two_quiz_course(token)
    if course2:
        courses.append(course2)
    
    print()
    course3 = create_subjective_heavy_course(token)
    if course3:
        courses.append(course3)
    
    print()
    course4 = create_mixed_content_course(token)
    if course4:
        courses.append(course4)
    
    print()
    print("🎉 TEST COURSE CREATION COMPLETE!")
    print("=" * 70)
    print(f"✅ Created {len(courses)} test courses:")
    
    for i, course in enumerate(courses, 1):
        print(f"{i}. {course['title']}")
        print(f"   ID: {course['id']}")
    
    print()
    print("📋 USAGE INSTRUCTIONS:")
    print("• Enroll test students in these courses via admin interface")
    print("• Use different courses to test different scenarios:")
    print("  - Simple Quiz Test Course: Basic functionality")
    print("  - Two-Quiz Progression Course: Sequential unlocking")
    print("  - Subjective Assessment Course: Manual grading workflow") 
    print("  - Comprehensive Testing Course: Complete system testing")
    print()
    print("🔧 FOR FUTURE TESTING:")
    print("• These courses are now available permanently")
    print("• No need to recreate courses for each test cycle")
    print("• Enroll different students as needed")
    print("• Modify content through admin interface if needed")

if __name__ == "__main__":
    main()