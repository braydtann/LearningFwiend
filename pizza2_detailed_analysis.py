#!/usr/bin/env python3
"""
PIZZA2 COURSE DETAILED ANALYSIS
Detailed examination of the pizza2 course structure and Select All That Apply questions
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration
BACKEND_URL = "https://coursemate-14.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Admin credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class Pizza2DetailedAnalyzer:
    def __init__(self):
        self.auth_token = None
        self.pizza2_course_id = "040b7021-eaf6-4f33-b813-a7a286f19e11"
        
    def authenticate(self):
        """Authenticate as admin"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                print("✅ Admin authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_detailed_course_info(self):
        """Get detailed information about pizza2 course"""
        if not self.auth_token:
            print("❌ No authentication token available")
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.pizza2_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                
                print("\n🍕 PIZZA2 COURSE DETAILED INFORMATION")
                print("=" * 60)
                print(f"Course ID: {course.get('id')}")
                print(f"Title: {course.get('title')}")
                print(f"Description: {course.get('description')}")
                print(f"Category: {course.get('category')}")
                print(f"Status: {course.get('status')}")
                print(f"Instructor: {course.get('instructor')} (ID: {course.get('instructorId')})")
                print(f"Created: {course.get('created_at')}")
                print(f"Updated: {course.get('updated_at')}")
                print(f"Enrolled Students: {course.get('enrolledStudents', 0)}")
                print(f"Access Type: {course.get('accessType')}")
                
                # Analyze modules and lessons
                modules = course.get('modules', [])
                print(f"\n📚 COURSE STRUCTURE:")
                print(f"Modules: {len(modules)}")
                
                total_lessons = 0
                total_questions = 0
                question_breakdown = {}
                
                for i, module in enumerate(modules):
                    module_id = module.get('id')
                    module_title = module.get('title')
                    lessons = module.get('lessons', [])
                    total_lessons += len(lessons)
                    
                    print(f"\n  📖 Module {i+1}: {module_title}")
                    print(f"     ID: {module_id}")
                    print(f"     Lessons: {len(lessons)}")
                    
                    for j, lesson in enumerate(lessons):
                        lesson_id = lesson.get('id')
                        lesson_title = lesson.get('title')
                        lesson_type = lesson.get('type')
                        lesson_content = lesson.get('content', '')
                        
                        print(f"\n    📝 Lesson {j+1}: {lesson_title}")
                        print(f"       ID: {lesson_id}")
                        print(f"       Type: {lesson_type}")
                        print(f"       Content: {lesson_content[:100]}{'...' if len(lesson_content) > 100 else ''}")
                        
                        # Check for questions in lesson
                        questions = lesson.get('questions', [])
                        if questions:
                            total_questions += len(questions)
                            print(f"       Questions: {len(questions)}")
                            
                            for k, question in enumerate(questions):
                                q_type = question.get('type')
                                q_text = question.get('question', '')
                                q_id = question.get('id')
                                
                                question_breakdown[q_type] = question_breakdown.get(q_type, 0) + 1
                                
                                print(f"\n         🎯 Question {k+1}: {q_type}")
                                print(f"            ID: {q_id}")
                                print(f"            Text: {q_text}")
                                
                                if q_type == 'select-all-that-apply':
                                    options = question.get('options', [])
                                    correct_answers = question.get('correctAnswers', [])
                                    points = question.get('points', 0)
                                    
                                    print(f"            Options ({len(options)}):")
                                    for idx, option in enumerate(options):
                                        is_correct = idx in correct_answers
                                        print(f"              {idx}: {option} {'✅' if is_correct else '❌'}")
                                    
                                    print(f"            Correct Answers: {correct_answers}")
                                    print(f"            Points: {points}")
                                    
                                    # Check for data integrity issues
                                    issues = []
                                    if not options:
                                        issues.append("Missing options array")
                                    if not correct_answers:
                                        issues.append("Missing correctAnswers array")
                                    if any(idx >= len(options) for idx in correct_answers):
                                        issues.append("correctAnswers contains invalid indices")
                                    
                                    if issues:
                                        print(f"            ⚠️ ISSUES: {', '.join(issues)}")
                                    else:
                                        print(f"            ✅ Data structure valid")
                                
                                elif q_type == 'multiple-choice':
                                    options = question.get('options', [])
                                    correct_answer = question.get('correctAnswer')
                                    points = question.get('points', 0)
                                    
                                    print(f"            Options ({len(options)}):")
                                    for idx, option in enumerate(options):
                                        is_correct = idx == correct_answer
                                        print(f"              {idx}: {option} {'✅' if is_correct else '❌'}")
                                    
                                    print(f"            Correct Answer: {correct_answer}")
                                    print(f"            Points: {points}")
                        
                        # Check for quiz structure (old format)
                        quiz = lesson.get('quiz')
                        if quiz:
                            quiz_questions = quiz.get('questions', [])
                            if quiz_questions:
                                print(f"       ⚠️ OLD QUIZ FORMAT DETECTED: {len(quiz_questions)} questions in lesson.quiz.questions")
                                total_questions += len(quiz_questions)
                                
                                for k, question in enumerate(quiz_questions):
                                    q_type = question.get('type')
                                    question_breakdown[q_type] = question_breakdown.get(q_type, 0) + 1
                                    print(f"         🎯 Quiz Question {k+1}: {q_type}")
                
                print(f"\n📊 COURSE SUMMARY:")
                print(f"Total Modules: {len(modules)}")
                print(f"Total Lessons: {total_lessons}")
                print(f"Total Questions: {total_questions}")
                print(f"Question Types: {question_breakdown}")
                
                return course
            else:
                print(f"❌ Failed to get course details: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting course details: {str(e)}")
            return None
    
    def test_course_accessibility(self):
        """Test if the course is accessible via different endpoints"""
        if not self.auth_token:
            print("❌ No authentication token available")
            return False
        
        print(f"\n🔍 TESTING COURSE ACCESSIBILITY")
        print("=" * 50)
        
        # Test 1: Direct course access
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.pizza2_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            if response.status_code == 200:
                print("✅ Direct course access: SUCCESS")
            else:
                print(f"❌ Direct course access: FAILED ({response.status_code})")
        except Exception as e:
            print(f"❌ Direct course access: ERROR ({str(e)})")
        
        # Test 2: Course in courses list
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                pizza2_in_list = any(c.get('id') == self.pizza2_course_id for c in courses)
                if pizza2_in_list:
                    print("✅ Course in courses list: SUCCESS")
                else:
                    print("❌ Course in courses list: NOT FOUND")
            else:
                print(f"❌ Course in courses list: FAILED ({response.status_code})")
        except Exception as e:
            print(f"❌ Course in courses list: ERROR ({str(e)})")
        
        # Test 3: Search for pizza courses
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                pizza_courses = [c for c in courses if 'pizza' in c.get('title', '').lower()]
                print(f"✅ Pizza courses search: Found {len(pizza_courses)} pizza courses")
                for course in pizza_courses:
                    print(f"   - {course.get('title')} (ID: {course.get('id')})")
            else:
                print(f"❌ Pizza courses search: FAILED ({response.status_code})")
        except Exception as e:
            print(f"❌ Pizza courses search: ERROR ({str(e)})")
        
        return True
    
    def run_analysis(self):
        """Run the complete detailed analysis"""
        print("🔬 PIZZA2 COURSE DETAILED ANALYSIS")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            return False
        
        # Step 2: Get detailed course information
        course = self.get_detailed_course_info()
        
        if not course:
            return False
        
        # Step 3: Test course accessibility
        self.test_course_accessibility()
        
        print(f"\n🎯 ANALYSIS CONCLUSIONS:")
        print("=" * 50)
        
        modules = course.get('modules', [])
        total_questions = sum(
            len(lesson.get('questions', [])) + len(lesson.get('quiz', {}).get('questions', []))
            for module in modules
            for lesson in module.get('lessons', [])
        )
        
        if total_questions == 0:
            print("⚠️ ISSUE IDENTIFIED: pizza2 course has NO QUESTIONS")
            print("   This could cause issues when students try to access quiz content")
            print("   The course exists but may appear empty or cause white screen")
        else:
            print("✅ Course has questions and should be functional")
        
        print(f"\n📋 RECOMMENDATIONS:")
        if total_questions == 0:
            print("1. Add questions to the pizza2 course to make it functional")
            print("2. Check if this is intentional (empty course for testing)")
            print("3. Consider adding Select All That Apply questions as requested")
        else:
            print("1. Course structure appears valid")
            print("2. Check frontend routing and access permissions")
            print("3. Verify student enrollment in the course")
        
        return True

def main():
    """Main function"""
    analyzer = Pizza2DetailedAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print(f"\n🎉 DETAILED ANALYSIS COMPLETED")
    else:
        print(f"\n⚠️ ANALYSIS FAILED")
    
    return success

if __name__ == "__main__":
    main()