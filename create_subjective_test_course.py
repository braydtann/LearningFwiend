#!/usr/bin/env python3
"""
Create a test course with subjective questions for testing subjective scoring functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"

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
            return data["access_token"]
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return None

def create_subjective_test_course(admin_token):
    """Create a course with subjective questions for testing"""
    
    course_data = {
        "title": "Subjective Question Scoring Test Course",
        "description": "A test course designed to validate subjective question scoring functionality. Contains mixed question types including short answer, essay, and long form questions.",
        "category": "Testing",
        "duration": "30 minutes",
        "thumbnailUrl": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=300&fit=crop",
        "accessType": "open",
        "learningOutcomes": [
            "Test subjective question scoring",
            "Validate full points for non-empty answers",
            "Confirm zero points for empty answers",
            "Test manual grading override capability"
        ],
        "modules": [
            {
                "title": "Module 1: Mixed Question Types Quiz",
                "lessons": [
                    {
                        "id": "lesson-intro",
                        "title": "Introduction to Subjective Scoring",
                        "type": "text",
                        "content": "This course tests the subjective question scoring functionality. You will encounter various question types including subjective questions that should receive full points for any non-empty answer.",
                        "duration": 5
                    },
                    {
                        "id": "lesson-quiz-mixed",
                        "title": "Mixed Question Types Quiz",
                        "type": "quiz",
                        "duration": 20,
                        "quiz": {
                            "id": "quiz-mixed-types",
                            "title": "Mixed Question Types Quiz",
                            "description": "A quiz with multiple question types including subjective questions",
                            "timeLimit": 1200,  # 20 minutes
                            "passingScore": 70,
                            "maxAttempts": 3,
                            "questions": [
                                {
                                    "id": "q1-multiple-choice",
                                    "type": "multiple_choice",
                                    "question": "What is the primary purpose of subjective questions in assessments?",
                                    "options": [
                                        "To test memorization",
                                        "To evaluate critical thinking and understanding",
                                        "To make grading easier",
                                        "To reduce test time"
                                    ],
                                    "correctAnswer": 1,
                                    "points": 2,
                                    "explanation": "Subjective questions are designed to evaluate critical thinking and deeper understanding."
                                },
                                {
                                    "id": "q2-short-answer",
                                    "type": "short_answer",
                                    "question": "Explain in 2-3 sentences why subjective questions are important in education.",
                                    "sampleAnswer": "Subjective questions allow students to demonstrate their understanding in their own words. They encourage critical thinking and help assess comprehension beyond memorization.",
                                    "points": 3,
                                    "gradingCriteria": "Look for understanding of the educational value of subjective assessment"
                                },
                                {
                                    "id": "q3-true-false",
                                    "type": "true_false",
                                    "question": "Subjective questions should always receive full points regardless of the answer quality.",
                                    "correctAnswer": False,
                                    "points": 2,
                                    "explanation": "While our system gives full points initially to allow progression, manual grading can adjust scores based on answer quality."
                                },
                                {
                                    "id": "q4-essay",
                                    "type": "essay",
                                    "question": "Write a short essay (150-200 words) discussing the benefits and challenges of implementing automated scoring for subjective questions in online learning platforms.",
                                    "sampleAnswer": "Automated scoring for subjective questions presents both opportunities and challenges. Benefits include immediate feedback, consistent initial scoring, and reduced instructor workload. However, challenges include the difficulty of assessing creativity, nuanced understanding, and context-specific responses. A hybrid approach combining automated initial scoring with manual review offers the best balance.",
                                    "points": 5,
                                    "gradingCriteria": "Evaluate depth of analysis, understanding of the topic, and quality of argumentation"
                                },
                                {
                                    "id": "q5-long-form",
                                    "type": "long_form",
                                    "question": "Describe a comprehensive strategy for implementing subjective question scoring in an LMS. Include considerations for student progression, instructor workload, and assessment quality. Provide specific examples and justify your recommendations.",
                                    "sampleAnswer": "A comprehensive strategy should include: 1) Initial automated scoring giving full points for non-empty answers to allow immediate progression, 2) Flagging system for instructor review, 3) Rubric-based manual grading interface, 4) Student notification system for grade updates, 5) Analytics to track scoring patterns and identify areas needing attention.",
                                    "points": 8,
                                    "gradingCriteria": "Assess comprehensiveness of strategy, practical considerations, specific examples, and justification of recommendations"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
        
        if response.status_code in [200, 201]:
            course = response.json()
            print(f"✅ Successfully created course: {course['title']}")
            print(f"   Course ID: {course['id']}")
            print(f"   Modules: {len(course['modules'])}")
            
            # Count question types
            quiz_lesson = course['modules'][0]['lessons'][1]
            questions = quiz_lesson['quiz']['questions']
            
            question_types = {}
            total_points = 0
            
            for question in questions:
                q_type = question['type']
                question_types[q_type] = question_types.get(q_type, 0) + 1
                total_points += question.get('points', 1)
            
            print(f"   Question types: {question_types}")
            print(f"   Total points: {total_points}")
            print(f"   Subjective questions: {question_types.get('short_answer', 0) + question_types.get('essay', 0) + question_types.get('long_form', 0)}")
            
            return course
        else:
            print(f"❌ Failed to create course: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating course: {str(e)}")
        return None

def enroll_student_in_course(admin_token, course_id, student_email="karlo.student@alder.com"):
    """Enroll student in the test course"""
    
    # First, get the student user
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Get all users to find the student
        response = requests.get(f"{BACKEND_URL}/auth/admin/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            student_user = None
            
            for user in users:
                if user.get('email') == student_email:
                    student_user = user
                    break
            
            if not student_user:
                print(f"❌ Student {student_email} not found")
                return False
            
            # Now authenticate as student to enroll
            student_credentials = {
                "username_or_email": student_email,
                "password": "StudentPermanent123!"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=student_credentials)
            
            if response.status_code == 200:
                student_data = response.json()
                student_token = student_data["access_token"]
                student_headers = {"Authorization": f"Bearer {student_token}"}
                
                # Enroll in course
                enrollment_data = {"courseId": course_id}
                response = requests.post(f"{BACKEND_URL}/enrollments", json=enrollment_data, headers=student_headers)
                
                if response.status_code in [200, 201]:
                    print(f"✅ Successfully enrolled {student_email} in the test course")
                    return True
                else:
                    print(f"❌ Failed to enroll student: {response.status_code}")
                    print(f"   Error: {response.text}")
                    return False
            else:
                print(f"❌ Failed to authenticate student: {response.status_code}")
                return False
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error enrolling student: {str(e)}")
        return False

def main():
    """Main execution"""
    print("🚀 Creating Subjective Question Scoring Test Course")
    print("=" * 60)
    
    # Authenticate admin
    admin_token = authenticate_admin()
    if not admin_token:
        return 1
    
    print("✅ Admin authenticated successfully")
    
    # Create test course
    course = create_subjective_test_course(admin_token)
    if not course:
        return 1
    
    # Enroll student
    enrollment_success = enroll_student_in_course(admin_token, course['id'])
    
    print("\n" + "=" * 60)
    print("📋 COURSE CREATION SUMMARY")
    print("=" * 60)
    
    if course:
        print(f"✅ Course Created: {course['title']}")
        print(f"   Course ID: {course['id']}")
        print(f"   Student Enrolled: {'✅ Yes' if enrollment_success else '❌ No'}")
        print("\n📝 Next Steps:")
        print("1. Run the subjective scoring backend test")
        print("2. Student can take the quiz to test subjective scoring")
        print("3. Admin can review and manually grade subjective questions")
        
        return 0
    else:
        print("❌ Course creation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())