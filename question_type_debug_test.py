#!/usr/bin/env python3
"""
Question Type Mismatch Debug Test
=================================

This test investigates the question type mismatch between backend and frontend
by logging in as a student and examining the actual question data structure
returned by the API.

Frontend expects: 'multiple-choice', 'select-all-that-apply', 'chronological-order', 
                 'true-false', 'short-answer', 'long-form'

We need to check what the backend is actually returning.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-debugfix.preview.emergentagent.com/api"

# Test credentials
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class QuestionTypeDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.student_id = None
        
    def login_student(self):
        """Login with student credentials"""
        print("🔐 Logging in as student...")
        
        login_data = {
            "username_or_email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.student_id = data["user"]["id"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Student login successful")
                print(f"   Student ID: {self.student_id}")
                print(f"   Student Name: {data['user']['full_name']}")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_student_enrollments(self):
        """Get student's enrollments to find courses with final tests"""
        print("\n📚 Getting student enrollments...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/enrollments")
            print(f"Enrollments response status: {response.status_code}")
            
            if response.status_code == 200:
                enrollments = response.json()
                print(f"✅ Found {len(enrollments)} enrollments")
                
                for i, enrollment in enumerate(enrollments):
                    print(f"   {i+1}. Course ID: {enrollment['courseId']}")
                    print(f"      Progress: {enrollment.get('progress', 0)}%")
                    print(f"      Status: {enrollment.get('status', 'unknown')}")
                
                return enrollments
            else:
                print(f"❌ Failed to get enrollments: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Enrollments error: {str(e)}")
            return []
    
    def get_final_tests_by_program(self):
        """Get final tests by program ID"""
        print("\n🎯 Checking for final tests by program...")
        
        try:
            # First, let's check if there are any programs
            response = self.session.get(f"{BACKEND_URL}/programs")
            print(f"Programs response status: {response.status_code}")
            
            if response.status_code == 200:
                programs = response.json()
                print(f"✅ Found {len(programs)} programs")
                
                for program in programs:
                    print(f"   Program: {program['title']} (ID: {program['id']})")
                    
                    # Try to get final test for this program
                    try:
                        final_test_response = self.session.get(f"{BACKEND_URL}/final-tests?program_id={program['id']}")
                        if final_test_response.status_code == 200:
                            final_tests = final_test_response.json()
                            if final_tests:
                                print(f"      ✅ Found {len(final_tests)} final test(s)")
                                return final_tests
                            else:
                                print(f"      ⚠️ No final tests found for this program")
                        else:
                            print(f"      ⚠️ Final test check failed: {final_test_response.status_code}")
                    except Exception as e:
                        print(f"      ⚠️ Error checking final tests: {str(e)}")
                
                return []
            else:
                print(f"❌ Failed to get programs: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Programs error: {str(e)}")
            return []
    
    def analyze_course_questions(self, course_id):
        """Analyze questions in a specific course"""
        print(f"\n🔍 Analyzing questions in course {course_id}...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/courses/{course_id}")
            print(f"Course response status: {response.status_code}")
            
            if response.status_code == 200:
                course = response.json()
                print(f"✅ Course: {course.get('title', 'Unknown')}")
                
                questions_found = []
                
                # Check modules and lessons for questions
                modules = course.get('modules', [])
                print(f"   Found {len(modules)} modules")
                
                for module_idx, module in enumerate(modules):
                    print(f"\n   Module {module_idx + 1}: {module.get('title', 'Untitled')}")
                    lessons = module.get('lessons', [])
                    print(f"   Found {len(lessons)} lessons")
                    
                    for lesson_idx, lesson in enumerate(lessons):
                        print(f"\n      Lesson {lesson_idx + 1}: {lesson.get('title', 'Untitled')}")
                        print(f"      Lesson Type: {lesson.get('type', 'unknown')}")
                        
                        # Check for questions in different possible locations
                        questions = []
                        
                        # Check lesson.questions (new format)
                        if 'questions' in lesson:
                            questions.extend(lesson['questions'])
                            print(f"      Found {len(lesson['questions'])} questions in lesson.questions")
                        
                        # Check lesson.quiz.questions (old format)
                        if 'quiz' in lesson and 'questions' in lesson['quiz']:
                            questions.extend(lesson['quiz']['questions'])
                            print(f"      Found {len(lesson['quiz']['questions'])} questions in lesson.quiz.questions")
                        
                        # Check lesson.content for embedded questions
                        if 'content' in lesson and isinstance(lesson['content'], dict):
                            if 'questions' in lesson['content']:
                                questions.extend(lesson['content']['questions'])
                                print(f"      Found {len(lesson['content']['questions'])} questions in lesson.content.questions")
                        
                        # Analyze each question
                        for q_idx, question in enumerate(questions):
                            print(f"\n         Question {q_idx + 1}:")
                            print(f"         ID: {question.get('id', 'No ID')}")
                            print(f"         Type: '{question.get('type', 'NO TYPE FIELD')}'")
                            print(f"         Question: {question.get('question', 'No question text')[:100]}...")
                            
                            # Check for required fields based on type
                            q_type = question.get('type', '')
                            
                            if q_type == 'multiple-choice' or q_type == 'multiple_choice':
                                print(f"         Options: {len(question.get('options', []))} options")
                                print(f"         Correct Answer: {question.get('correctAnswer', 'Not set')}")
                            
                            elif q_type == 'select-all-that-apply' or q_type == 'select_all_that_apply':
                                print(f"         Options: {len(question.get('options', []))} options")
                                print(f"         Correct Answers: {question.get('correctAnswers', 'Not set')}")
                            
                            elif q_type == 'chronological-order' or q_type == 'chronological_order':
                                print(f"         Items: {len(question.get('items', []))} items")
                                print(f"         Correct Order: {question.get('correctOrder', 'Not set')}")
                            
                            elif q_type == 'true-false' or q_type == 'true_false':
                                print(f"         Correct Answer: {question.get('correctAnswer', 'Not set')}")
                            
                            elif q_type in ['short-answer', 'short_answer', 'long-form', 'long_form']:
                                print(f"         Sample Answer: {question.get('sampleAnswer', 'Not set')}")
                            
                            # Store question for analysis
                            questions_found.append({
                                'course_id': course_id,
                                'module_idx': module_idx,
                                'lesson_idx': lesson_idx,
                                'question_idx': q_idx,
                                'question': question
                            })
                
                return questions_found
            else:
                print(f"❌ Failed to get course: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Course analysis error: {str(e)}")
            return []
    
    def analyze_question_types(self, all_questions):
        """Analyze all found question types and identify mismatches"""
        print(f"\n📊 QUESTION TYPE ANALYSIS")
        print("=" * 50)
        
        # Frontend expected types
        frontend_expected = [
            'multiple-choice', 'select-all-that-apply', 'chronological-order', 
            'true-false', 'short-answer', 'long-form'
        ]
        
        # Collect all unique types found
        backend_types = set()
        type_counts = {}
        
        for q_data in all_questions:
            question = q_data['question']
            q_type = question.get('type', 'NO_TYPE')
            backend_types.add(q_type)
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        print(f"Frontend expects: {frontend_expected}")
        print(f"Backend returns: {list(backend_types)}")
        print(f"\nType counts:")
        for q_type, count in type_counts.items():
            print(f"   '{q_type}': {count} questions")
        
        # Identify mismatches
        print(f"\n🔍 MISMATCH ANALYSIS:")
        
        mismatches = []
        for backend_type in backend_types:
            if backend_type not in frontend_expected:
                # Check for common naming pattern mismatches
                potential_matches = []
                
                if backend_type == 'multiple_choice':
                    potential_matches.append('multiple-choice')
                elif backend_type == 'select_all_that_apply':
                    potential_matches.append('select-all-that-apply')
                elif backend_type == 'chronological_order':
                    potential_matches.append('chronological-order')
                elif backend_type == 'true_false':
                    potential_matches.append('true-false')
                elif backend_type == 'short_answer':
                    potential_matches.append('short-answer')
                elif backend_type == 'long_form':
                    potential_matches.append('long-form')
                
                if potential_matches:
                    print(f"   ❌ MISMATCH: Backend '{backend_type}' should be '{potential_matches[0]}'")
                    mismatches.append((backend_type, potential_matches[0]))
                else:
                    print(f"   ❌ UNKNOWN: Backend '{backend_type}' has no frontend equivalent")
        
        # Check for missing required fields
        print(f"\n🔍 FIELD VALIDATION:")
        for q_data in all_questions:
            question = q_data['question']
            q_type = question.get('type', 'NO_TYPE')
            
            missing_fields = []
            
            if q_type in ['multiple-choice', 'multiple_choice']:
                if not question.get('options'):
                    missing_fields.append('options')
                if 'correctAnswer' not in question:
                    missing_fields.append('correctAnswer')
            
            elif q_type in ['select-all-that-apply', 'select_all_that_apply']:
                if not question.get('options'):
                    missing_fields.append('options')
                if 'correctAnswers' not in question:
                    missing_fields.append('correctAnswers')
            
            elif q_type in ['chronological-order', 'chronological_order']:
                if not question.get('items'):
                    missing_fields.append('items')
                if 'correctOrder' not in question:
                    missing_fields.append('correctOrder')
            
            if missing_fields:
                print(f"   ❌ Question {question.get('id', 'Unknown')} missing: {missing_fields}")
        
        return mismatches
    
    def run_debug_analysis(self):
        """Run the complete debug analysis"""
        print("🚀 QUESTION TYPE MISMATCH DEBUG ANALYSIS")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        
        # Step 1: Login
        if not self.login_student():
            return False
        
        # Step 2: Get enrollments to find courses
        enrollments = self.get_student_enrollments()
        
        # Step 3: Check for final tests
        final_tests = self.get_final_tests_by_program()
        
        # Step 4: Analyze questions in enrolled courses
        all_questions = []
        
        for enrollment in enrollments:
            course_id = enrollment['courseId']
            questions = self.analyze_course_questions(course_id)
            all_questions.extend(questions)
        
        # Step 5: Analyze question types and identify mismatches
        if all_questions:
            mismatches = self.analyze_question_types(all_questions)
            
            print(f"\n🎯 SUMMARY:")
            print(f"   Total questions analyzed: {len(all_questions)}")
            print(f"   Type mismatches found: {len(mismatches)}")
            
            if mismatches:
                print(f"\n🔧 RECOMMENDED FIXES:")
                for backend_type, frontend_type in mismatches:
                    print(f"   Change '{backend_type}' to '{frontend_type}' in backend")
            else:
                print(f"   ✅ No obvious type mismatches found")
        else:
            print(f"\n⚠️ No questions found in any enrolled courses")
        
        print(f"\nCompleted at: {datetime.now()}")
        return True

def main():
    """Main function"""
    debugger = QuestionTypeDebugger()
    success = debugger.run_debug_analysis()
    
    if success:
        print(f"\n✅ Debug analysis completed successfully")
        return 0
    else:
        print(f"\n❌ Debug analysis failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())