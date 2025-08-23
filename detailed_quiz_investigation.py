#!/usr/bin/env python3
"""
DETAILED QUIZ INVESTIGATION - LOOKING FOR ACTUAL QUIZ QUESTIONS
This script will look deeper into the quiz data structure to find courses with actual questions
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://lms-evolution.emergent.host/api"
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class DetailedQuizInvestigator:
    def __init__(self):
        self.session = None
        self.auth_token = None
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate as admin
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS) as response:
            if response.status == 200:
                auth_data = await response.json()
                self.auth_token = auth_data["access_token"]
                print(f"✅ Admin authentication successful: {auth_data['user']['full_name']}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Admin authentication failed: {response.status} - {error_text}")
                return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def get_course_details(self, course_id: str):
        """Get detailed course information"""
        try:
            async with self.session.get(f"{BACKEND_URL}/courses/{course_id}", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ Failed to get course {course_id}: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Error getting course {course_id}: {str(e)}")
            return None
    
    async def investigate_specific_courses(self):
        """Investigate specific courses mentioned in the review request"""
        print("🔍 INVESTIGATING SPECIFIC COURSES FROM REVIEW REQUEST")
        print("=" * 60)
        
        # Look for courses that might have quiz questions
        target_courses = [
            "7590f85b-cb33-4df7-931c-756cb8f390f4",  # "all quizzes as options"
            "477b339d-9c3a-44db-aef4-6ec971280bc1",  # "Multiple Choice"
            "e677fcf9-89b3-4e55-8332-1b3fba224a11",  # "Select all that apply test"
        ]
        
        for course_id in target_courses:
            print(f"\n📖 DETAILED ANALYSIS: Course {course_id}")
            course = await self.get_course_details(course_id)
            if course:
                await self.analyze_course_structure(course)
    
    async def analyze_course_structure(self, course: Dict):
        """Analyze the complete course structure"""
        print(f"   Title: {course['title']}")
        print(f"   Created: {course.get('created_at', 'Unknown')}")
        print(f"   Modules: {len(course.get('modules', []))}")
        
        modules = course.get('modules', [])
        for module_idx, module in enumerate(modules):
            print(f"\n   📁 Module {module_idx}: '{module.get('title', 'Untitled')}'")
            lessons = module.get('lessons', [])
            print(f"      Lessons: {len(lessons)}")
            
            for lesson_idx, lesson in enumerate(lessons):
                lesson_type = lesson.get('type', 'unknown')
                lesson_title = lesson.get('title', 'Untitled')
                print(f"      📄 Lesson {lesson_idx}: '{lesson_title}' (Type: {lesson_type})")
                
                if lesson_type == 'quiz':
                    await self.analyze_quiz_lesson_detailed(lesson, module_idx, lesson_idx)
    
    async def analyze_quiz_lesson_detailed(self, lesson: Dict, module_idx: int, lesson_idx: int):
        """Analyze quiz lesson in detail"""
        print(f"         🎯 QUIZ LESSON DETAILED ANALYSIS:")
        
        # Print the entire lesson structure
        print(f"         📋 Complete Lesson Structure:")
        lesson_json = json.dumps(lesson, indent=12, default=str)
        print(lesson_json)
        
        # Check for questions
        questions = lesson.get('questions', [])
        if not questions:
            print(f"         ❌ NO QUESTIONS FOUND")
            
            # Check if questions might be stored elsewhere
            for key, value in lesson.items():
                if 'question' in key.lower():
                    print(f"         🔍 Found question-related field '{key}': {type(value)} = {value}")
        else:
            print(f"         ✅ FOUND {len(questions)} QUESTIONS")
            for q_idx, question in enumerate(questions):
                await self.analyze_question_detailed(question, q_idx)
    
    async def analyze_question_detailed(self, question: Dict, q_idx: int):
        """Analyze individual question in detail"""
        question_type = question.get('type', 'unknown')
        question_text = question.get('question', 'No question text')[:50]
        
        print(f"            📝 Question {q_idx + 1}: {question_type}")
        print(f"               Text: '{question_text}...'")
        
        # Print complete question structure
        question_json = json.dumps(question, indent=16, default=str)
        print(f"               Complete Structure:")
        print(question_json)
        
        # Check for React Error #31 causes
        if question_type == 'multiple-choice':
            options = question.get('options')
            print(f"               Options field: {type(options)} = {options}")
            if options is None:
                print(f"               ❌ CRITICAL: Missing 'options' field - REACT ERROR #31 CAUSE")
            elif not isinstance(options, list):
                print(f"               ❌ CRITICAL: 'options' is not array - REACT ERROR #31 CAUSE")
        
        elif question_type == 'chronological-order':
            items = question.get('items')
            print(f"               Items field: {type(items)} = {items}")
            if items is None:
                print(f"               ❌ CRITICAL: Missing 'items' field - REACT ERROR #31 CAUSE")
            elif not isinstance(items, list):
                print(f"               ❌ CRITICAL: 'items' is not array - REACT ERROR #31 CAUSE")
        
        elif question_type == 'select-all-that-apply':
            options = question.get('options')
            correct_answers = question.get('correctAnswers')
            print(f"               Options field: {type(options)} = {options}")
            print(f"               CorrectAnswers field: {type(correct_answers)} = {correct_answers}")
            
            if options is None:
                print(f"               ❌ CRITICAL: Missing 'options' field")
            if correct_answers is None:
                print(f"               ❌ CRITICAL: Missing 'correctAnswers' field")
    
    async def search_for_courses_with_questions(self):
        """Search through all courses to find any with actual quiz questions"""
        print("\n🔍 SEARCHING ALL COURSES FOR QUIZ QUESTIONS")
        print("=" * 50)
        
        try:
            async with self.session.get(f"{BACKEND_URL}/courses", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    courses = await response.json()
                    print(f"📚 Searching through {len(courses)} courses...")
                    
                    courses_with_questions = []
                    
                    for course in courses:
                        course_details = await self.get_course_details(course['id'])
                        if course_details:
                            has_questions = await self.check_course_has_questions(course_details)
                            if has_questions:
                                courses_with_questions.append(course_details)
                    
                    print(f"\n🎯 FOUND {len(courses_with_questions)} COURSES WITH ACTUAL QUIZ QUESTIONS")
                    
                    if courses_with_questions:
                        for course in courses_with_questions:
                            print(f"\n📖 COURSE WITH QUESTIONS: {course['title']}")
                            await self.analyze_course_structure(course)
                    else:
                        print("❌ NO COURSES FOUND WITH ACTUAL QUIZ QUESTIONS")
                        print("   This suggests that:")
                        print("   1. Quiz questions are not being saved properly during course creation")
                        print("   2. Quiz questions might be stored in a different location")
                        print("   3. The quiz creation process is not working correctly")
                        
                else:
                    print(f"❌ Failed to get courses: {response.status}")
        except Exception as e:
            print(f"❌ Error searching courses: {str(e)}")
    
    async def check_course_has_questions(self, course: Dict) -> bool:
        """Check if course has any quiz questions"""
        modules = course.get('modules', [])
        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                if lesson.get('type') == 'quiz':
                    questions = lesson.get('questions', [])
                    if questions and len(questions) > 0:
                        return True
        return False
    
    async def test_quiz_creation_api(self):
        """Test if we can create a simple quiz to see the expected structure"""
        print("\n🧪 TESTING QUIZ CREATION TO UNDERSTAND EXPECTED STRUCTURE")
        print("=" * 60)
        
        # Create a test course with a quiz
        test_course_data = {
            "title": "TEST QUIZ STRUCTURE INVESTIGATION",
            "description": "Test course to investigate quiz data structure",
            "category": "Testing",
            "modules": [
                {
                    "title": "Test Module",
                    "lessons": [
                        {
                            "id": "test-lesson-1",
                            "title": "Test Quiz Lesson",
                            "type": "quiz",
                            "questions": [
                                {
                                    "id": "test-q1",
                                    "type": "multiple-choice",
                                    "question": "What is 2+2?",
                                    "options": ["3", "4", "5", "6"],
                                    "correctAnswer": 1
                                },
                                {
                                    "id": "test-q2", 
                                    "type": "chronological-order",
                                    "question": "Put these in order: A, B, C, D",
                                    "items": ["D", "C", "B", "A"],
                                    "correctOrder": [3, 2, 1, 0]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        try:
            async with self.session.post(f"{BACKEND_URL}/courses", 
                                       json=test_course_data, 
                                       headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    created_course = await response.json()
                    print(f"✅ Test course created: {created_course['id']}")
                    
                    # Get the course back to see how it was stored
                    stored_course = await self.get_course_details(created_course['id'])
                    if stored_course:
                        print(f"\n📋 STORED COURSE STRUCTURE:")
                        await self.analyze_course_structure(stored_course)
                        
                        # Clean up - delete the test course
                        async with self.session.delete(f"{BACKEND_URL}/courses/{created_course['id']}", 
                                                     headers=self.get_auth_headers()) as delete_response:
                            if delete_response.status == 200:
                                print(f"✅ Test course cleaned up")
                            else:
                                print(f"⚠️  Could not clean up test course")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create test course: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Error testing quiz creation: {str(e)}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def run_investigation(self):
        """Run the detailed investigation"""
        print("🔬 DETAILED QUIZ DATA STRUCTURE INVESTIGATION")
        print("=" * 60)
        print("Looking for actual quiz questions and data structure issues")
        print("=" * 60)
        
        try:
            # Setup
            if not await self.setup_session():
                return False
            
            # Investigate specific courses
            await self.investigate_specific_courses()
            
            # Search for any courses with questions
            await self.search_for_courses_with_questions()
            
            # Test quiz creation
            await self.test_quiz_creation_api()
            
            print(f"\n🎉 DETAILED INVESTIGATION COMPLETE")
            return True
            
        except Exception as e:
            print(f"❌ Investigation failed: {str(e)}")
            return False
        finally:
            await self.cleanup()

async def main():
    """Main function"""
    investigator = DetailedQuizInvestigator()
    success = await investigator.run_investigation()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)