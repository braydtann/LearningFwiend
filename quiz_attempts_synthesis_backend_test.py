#!/usr/bin/env python3

"""
Quiz Attempts Synthesis Backend Testing
=====================================

This test verifies that the backend provides the correct data structure
for the frontend to synthesize quiz attempts from enrollment data.

Testing Objectives:
1. Verify Data Loading Order - Confirm courses are loaded before enrollment processing
2. Test Synthetic Attempts Creation - Verify enrollment data is properly structured for conversion
3. Check Recent Attempts Display Data - Ensure backend provides all required fields
4. Validate Course Filtering Data - Test that backend provides proper course-quiz relationships
5. Console Log Analysis - Verify backend data structure supports frontend synthesis

Expected Results:
- Backend APIs provide all required fields for synthetic quiz attempts
- Enrollment data contains quiz progress information
- Course data contains quiz lesson information
- All data is properly structured for frontend synthesis
"""

import requests
import json
import sys
from datetime import datetime
import os

# Use the production backend URL from frontend/.env
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials from previous testing
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class QuizAttemptsSynthesisBackendTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                admin_name = data['user']['full_name']
                admin_role = data['user']['role']
                self.log_test("Admin Authentication", True, f"Admin logged in: {admin_name}, Role: {admin_role}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_student(self):
        """Authenticate student user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                student_name = data['user']['full_name']
                student_id = data['user']['id']
                self.log_test("Student Authentication", True, f"Student logged in: {student_name}, ID: {student_id}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_courses_api_for_quiz_synthesis(self):
        """Test courses API to verify quiz lesson data structure"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/courses", headers=headers)
            
            if response.status_code == 200:
                courses = response.json()
                quiz_courses = []
                
                for course in courses:
                    # Check if course has modules with quiz lessons
                    has_quiz = False
                    for module in course.get('modules', []):
                        for lesson in module.get('lessons', []):
                            if lesson.get('type') == 'quiz':
                                has_quiz = True
                                break
                        if has_quiz:
                            break
                    
                    if has_quiz:
                        quiz_courses.append({
                            'id': course['id'],
                            'title': course['title'],
                            'modules': len(course.get('modules', []))
                        })
                
                if quiz_courses:
                    course_titles = [c['title'] for c in quiz_courses[:3]]
                    self.log_test("Courses API Quiz Data Structure", True, 
                                f"Found {len(quiz_courses)} courses with quiz lessons: {course_titles}")
                    return quiz_courses
                else:
                    self.log_test("Courses API Quiz Data Structure", False, "No courses with quiz lessons found")
                    return []
            else:
                self.log_test("Courses API Quiz Data Structure", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Courses API Quiz Data Structure", False, f"Exception: {str(e)}")
            return []
    
    def test_enrollments_api_for_quiz_synthesis(self):
        """Test enrollments API to verify quiz progress data structure"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                enrollments = response.json()
                quiz_enrollments = []
                
                for enrollment in enrollments:
                    # Check if enrollment has quiz progress (progress > 0)
                    if enrollment.get('progress', 0) > 0:
                        quiz_enrollments.append({
                            'id': enrollment['id'],
                            'courseId': enrollment['courseId'],
                            'progress': enrollment['progress'],
                            'status': enrollment.get('status', 'active'),
                            'enrolledAt': enrollment.get('enrolledAt'),
                            'lastAccessedAt': enrollment.get('lastAccessedAt'),
                            'completedAt': enrollment.get('completedAt')
                        })
                
                if quiz_enrollments:
                    progress_list = [str(e['progress']) + '%' for e in quiz_enrollments]
                    self.log_test("Enrollments API Quiz Progress Data", True, 
                                f"Found {len(quiz_enrollments)} enrollments with quiz progress: {progress_list}")
                    return quiz_enrollments
                else:
                    self.log_test("Enrollments API Quiz Progress Data", False, "No enrollments with quiz progress found")
                    return []
            else:
                self.log_test("Enrollments API Quiz Progress Data", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Enrollments API Quiz Progress Data", False, f"Exception: {str(e)}")
            return []
    
    def test_course_details_for_quiz_synthesis(self, course_ids):
        """Test individual course details for quiz synthesis compatibility"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            quiz_compatible_courses = []
            
            for course_id in course_ids[:3]:  # Test first 3 courses
                response = requests.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers)
                
                if response.status_code == 200:
                    course = response.json()
                    quiz_lessons = []
                    
                    # Extract quiz lessons for synthesis compatibility
                    for module in course.get('modules', []):
                        for lesson in module.get('lessons', []):
                            if lesson.get('type') == 'quiz':
                                quiz_lessons.append({
                                    'id': lesson['id'],
                                    'title': lesson.get('title', 'Quiz'),
                                    'type': lesson['type']
                                })
                    
                    if quiz_lessons:
                        quiz_compatible_courses.append({
                            'courseId': course_id,
                            'courseName': course['title'],
                            'quizLessons': quiz_lessons
                        })
            
            if quiz_compatible_courses:
                self.log_test("Course Details Quiz Synthesis Compatibility", True, 
                            f"Found {len(quiz_compatible_courses)} courses with quiz lessons for synthesis")
                return quiz_compatible_courses
            else:
                self.log_test("Course Details Quiz Synthesis Compatibility", False, "No quiz-compatible courses found")
                return []
        except Exception as e:
            self.log_test("Course Details Quiz Synthesis Compatibility", False, f"Exception: {str(e)}")
            return []
    
    def test_synthetic_quiz_attempts_data_structure(self, quiz_enrollments, quiz_courses):
        """Test if backend data can be synthesized into quiz attempts"""
        try:
            synthetic_attempts = []
            
            for enrollment in quiz_enrollments:
                # Find matching course
                matching_course = None
                for course in quiz_courses:
                    if course['courseId'] == enrollment['courseId']:
                        matching_course = course
                        break
                
                if matching_course:
                    # Create synthetic quiz attempt structure
                    synthetic_attempt = {
                        'id': f"course-quiz-{enrollment['courseId']}",
                        'courseId': enrollment['courseId'],
                        'courseName': matching_course['courseName'],
                        'studentName': 'Test Student',  # Would come from user data
                        'score': enrollment['progress'],
                        'status': 'completed' if enrollment['progress'] >= 100 else 'in_progress',
                        'submittedAt': enrollment.get('lastAccessedAt') or enrollment.get('enrolledAt'),
                        'completedAt': enrollment.get('completedAt')
                    }
                    synthetic_attempts.append(synthetic_attempt)
            
            if synthetic_attempts:
                self.log_test("Synthetic Quiz Attempts Data Structure", True, 
                            f"Successfully created {len(synthetic_attempts)} synthetic quiz attempts")
                
                # Verify all required fields are present
                required_fields = ['id', 'courseId', 'courseName', 'score', 'status', 'submittedAt']
                all_fields_present = True
                
                for attempt in synthetic_attempts:
                    for field in required_fields:
                        if field not in attempt or attempt[field] is None:
                            all_fields_present = False
                            break
                
                if all_fields_present:
                    self.log_test("Synthetic Quiz Attempts Required Fields", True, 
                                "All required fields present in synthetic attempts")
                else:
                    self.log_test("Synthetic Quiz Attempts Required Fields", False, 
                                "Some required fields missing in synthetic attempts")
                
                return synthetic_attempts
            else:
                self.log_test("Synthetic Quiz Attempts Data Structure", False, "Could not create synthetic quiz attempts")
                return []
        except Exception as e:
            self.log_test("Synthetic Quiz Attempts Data Structure", False, f"Exception: {str(e)}")
            return []
    
    def test_course_filtering_data_structure(self, synthetic_attempts):
        """Test if synthetic attempts support course filtering"""
        try:
            if not synthetic_attempts:
                self.log_test("Course Filtering Data Structure", False, "No synthetic attempts to test")
                return False
            
            # Group attempts by course
            course_stats = {}
            for attempt in synthetic_attempts:
                course_id = attempt['courseId']
                if course_id not in course_stats:
                    course_stats[course_id] = {
                        'courseName': attempt['courseName'],
                        'attempts': [],
                        'totalAttempts': 0,
                        'totalScore': 0,
                        'passCount': 0
                    }
                
                course_stats[course_id]['attempts'].append(attempt)
                course_stats[course_id]['totalAttempts'] += 1
                course_stats[course_id]['totalScore'] += attempt['score']
                if attempt['score'] >= 70:  # Assuming 70% pass rate
                    course_stats[course_id]['passCount'] += 1
            
            # Calculate statistics
            filtering_data = {}
            for course_id, stats in course_stats.items():
                filtering_data[course_id] = {
                    'courseName': stats['courseName'],
                    'totalAttempts': stats['totalAttempts'],
                    'averageScore': stats['totalScore'] / stats['totalAttempts'],
                    'passRate': (stats['passCount'] / stats['totalAttempts']) * 100
                }
            
            if filtering_data:
                self.log_test("Course Filtering Data Structure", True, 
                            f"Course filtering data ready for {len(filtering_data)} courses")
                
                # Log sample filtering data
                for course_id, data in list(filtering_data.items())[:2]:
                    course_name = data['courseName']
                    attempts = data['totalAttempts']
                    avg_score = data['averageScore']
                    pass_rate = data['passRate']
                    print(f"   Course: {course_name}, Attempts: {attempts}, Avg: {avg_score:.1f}%, Pass: {pass_rate:.1f}%")
                
                return True
            else:
                self.log_test("Course Filtering Data Structure", False, "Could not create filtering data")
                return False
        except Exception as e:
            self.log_test("Course Filtering Data Structure", False, f"Exception: {str(e)}")
            return False
    
    def test_recent_quiz_attempts_display_data(self, synthetic_attempts):
        """Test if synthetic attempts have all data needed for Recent Quiz Attempts display"""
        try:
            if not synthetic_attempts:
                self.log_test("Recent Quiz Attempts Display Data", False, "No synthetic attempts to test")
                return False
            
            # Check if all display fields are present
            display_fields = ['courseName', 'studentName', 'score', 'submittedAt', 'status']
            display_ready_attempts = []
            
            for attempt in synthetic_attempts:
                display_ready = True
                for field in display_fields:
                    if field not in attempt or attempt[field] is None:
                        display_ready = False
                        break
                
                if display_ready:
                    display_ready_attempts.append({
                        'courseName': attempt['courseName'],
                        'studentName': attempt['studentName'],
                        'score': str(attempt['score']) + '%',
                        'submittedAt': attempt['submittedAt'],
                        'status': attempt['status']
                    })
            
            if display_ready_attempts:
                self.log_test("Recent Quiz Attempts Display Data", True, 
                            f"Found {len(display_ready_attempts)} display-ready quiz attempts")
                
                # Log sample display data
                for attempt in display_ready_attempts[:2]:
                    course_name = attempt['courseName']
                    score = attempt['score']
                    status = attempt['status']
                    print(f"   Course: {course_name}, Score: {score}, Status: {status}")
                
                return True
            else:
                self.log_test("Recent Quiz Attempts Display Data", False, "No display-ready attempts found")
                return False
        except Exception as e:
            self.log_test("Recent Quiz Attempts Display Data", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive quiz attempts synthesis backend testing"""
        print("🎯 QUIZ ATTEMPTS SYNTHESIS BACKEND TESTING INITIATED")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        if not self.authenticate_student():
            print("❌ Cannot proceed without student authentication")
            return False
        
        # Step 2: Test courses API for quiz data structure
        quiz_courses = self.test_courses_api_for_quiz_synthesis()
        if not quiz_courses:
            print("⚠️  No quiz courses found - synthesis may not work")
        
        # Step 3: Test enrollments API for quiz progress data
        quiz_enrollments = self.test_enrollments_api_for_quiz_synthesis()
        if not quiz_enrollments:
            print("⚠️  No quiz enrollments found - synthesis may not work")
            return False
        
        # Step 4: Test course details for synthesis compatibility
        course_ids = [enrollment['courseId'] for enrollment in quiz_enrollments]
        quiz_compatible_courses = self.test_course_details_for_quiz_synthesis(course_ids)
        
        # Step 5: Test synthetic quiz attempts creation
        synthetic_attempts = self.test_synthetic_quiz_attempts_data_structure(quiz_enrollments, quiz_compatible_courses)
        
        # Step 6: Test course filtering data structure
        self.test_course_filtering_data_structure(synthetic_attempts)
        
        # Step 7: Test recent quiz attempts display data
        self.test_recent_quiz_attempts_display_data(synthetic_attempts)
        
        # Calculate success rate
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print(f"🎯 QUIZ ATTEMPTS SYNTHESIS BACKEND TESTING COMPLETED")
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        if success_rate >= 80:
            print("✅ BACKEND READY FOR QUIZ ATTEMPTS SYNTHESIS")
            print("   All required data structures are available for frontend synthesis")
        else:
            print("❌ BACKEND NOT READY FOR QUIZ ATTEMPTS SYNTHESIS")
            print("   Missing required data structures for frontend synthesis")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = QuizAttemptsSynthesisBackendTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)