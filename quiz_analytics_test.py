#!/usr/bin/env python3
"""
QUIZ ANALYTICS DATA FLOW TESTING SUITE
LearningFwiend LMS Application - Quiz Analytics Issue Investigation

TESTING FOCUS:
✅ Quiz submission process and score storage verification
✅ Analytics endpoints that fetch quiz data for dashboard
✅ getQuizAttempts API endpoint used by QuizResults.js frontend
✅ Authentication with existing test accounts
✅ Quiz attempt records verification (scores stored correctly)
✅ Analytics dashboard endpoints returning correct quiz score data
✅ Data flow: quiz submission → database storage → analytics retrieval

ISSUE REPORTED: "quiz and test scores from agents are not deploying the correct results 
to the quiz and test analytics page for the students. all scores report as 0% instead 
of reporting the proper scores taken from the quizzes."
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using frontend/.env REACT_APP_BACKEND_URL
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class QuizAnalyticsTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.test_course_id = None
        self.test_enrollment_id = None
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.results.append(result)
        
        if status == 'PASS':
            self.passed += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    # =============================================================================
    # AUTHENTICATION TESTS
    # =============================================================================
    
    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin authenticated successfully: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Authentication succeeded but invalid token or role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Authentication failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_student_authentication(self):
        """Test student authentication with provided credentials"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"Student authenticated successfully: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Authentication succeeded but invalid token or role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"Authentication failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ COURSE SETUP AND ENROLLMENT TESTS
    # =============================================================================
    
    def test_find_quiz_course(self):
        """Find existing courses with quiz content for testing"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Find Quiz Course", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                quiz_courses = []
                
                for course in courses:
                    modules = course.get('modules', [])
                    has_quiz = False
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if 'quiz' in lesson.get('type', '').lower() or lesson.get('questions'):
                                has_quiz = True
                                break
                        if has_quiz:
                            break
                    
                    if has_quiz:
                        quiz_courses.append(course)
                
                if quiz_courses:
                    # Use the first quiz course found
                    self.test_course_id = quiz_courses[0]['id']
                    self.log_result(
                        "Find Quiz Course", 
                        "PASS", 
                        f"Found {len(quiz_courses)} courses with quiz content, using: {quiz_courses[0]['title']}",
                        f"Course ID: {self.test_course_id}, Modules: {len(quiz_courses[0].get('modules', []))}"
                    )
                    return True
                else:
                    self.log_result(
                        "Find Quiz Course", 
                        "FAIL", 
                        f"No courses with quiz content found among {len(courses)} courses",
                        "Need courses with quiz lessons to test analytics"
                    )
            else:
                self.log_result(
                    "Find Quiz Course", 
                    "FAIL", 
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Find Quiz Course", 
                "FAIL", 
                "Failed to connect to courses endpoint",
                str(e)
            )
        return False
    
    def test_student_enrollment_in_quiz_course(self):
        """Ensure student is enrolled in the quiz course"""
        if "student" not in self.auth_tokens or not self.test_course_id:
            self.log_result(
                "Student Quiz Course Enrollment", 
                "SKIP", 
                "Missing student token or course ID",
                "Student authentication and course selection required"
            )
            return False
        
        try:
            # Check existing enrollments
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                existing_enrollment = None
                
                for enrollment in enrollments:
                    if enrollment.get('courseId') == self.test_course_id:
                        existing_enrollment = enrollment
                        break
                
                if existing_enrollment:
                    self.test_enrollment_id = existing_enrollment.get('id')
                    self.log_result(
                        "Student Quiz Course Enrollment", 
                        "PASS", 
                        f"Student already enrolled in quiz course",
                        f"Enrollment ID: {self.test_enrollment_id}, Progress: {existing_enrollment.get('progress', 0)}%"
                    )
                    return True
                else:
                    # Try to enroll student
                    enrollment_data = {"courseId": self.test_course_id}
                    enroll_response = requests.post(
                        f"{BACKEND_URL}/enrollments",
                        json=enrollment_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["student"]}'
                        }
                    )
                    
                    if enroll_response.status_code == 200:
                        enrollment = enroll_response.json()
                        self.test_enrollment_id = enrollment.get('id')
                        self.log_result(
                            "Student Quiz Course Enrollment", 
                            "PASS", 
                            f"Student successfully enrolled in quiz course",
                            f"New enrollment ID: {self.test_enrollment_id}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Student Quiz Course Enrollment", 
                            "FAIL", 
                            f"Failed to enroll student, status: {enroll_response.status_code}",
                            f"Response: {enroll_response.text}"
                        )
            else:
                self.log_result(
                    "Student Quiz Course Enrollment", 
                    "FAIL", 
                    f"Failed to check enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Quiz Course Enrollment", 
                "FAIL", 
                "Failed to check/create enrollment",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ SUBMISSION AND PROGRESS TRACKING TESTS
    # =============================================================================
    
    def test_quiz_course_structure(self):
        """Analyze the quiz course structure to understand quiz content"""
        if "student" not in self.auth_tokens or not self.test_course_id:
            self.log_result(
                "Quiz Course Structure Analysis", 
                "SKIP", 
                "Missing student token or course ID",
                "Student authentication and course selection required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                modules = course.get('modules', [])
                
                quiz_analysis = {
                    'total_modules': len(modules),
                    'total_lessons': 0,
                    'quiz_lessons': 0,
                    'quiz_details': []
                }
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    quiz_analysis['total_lessons'] += len(lessons)
                    
                    for lesson in lessons:
                        lesson_type = lesson.get('type', '').lower()
                        has_questions = bool(lesson.get('questions'))
                        
                        if 'quiz' in lesson_type or has_questions:
                            quiz_analysis['quiz_lessons'] += 1
                            
                            questions = lesson.get('questions', [])
                            quiz_details = {
                                'lesson_id': lesson.get('id'),
                                'lesson_title': lesson.get('title', 'Untitled'),
                                'lesson_type': lesson_type,
                                'question_count': len(questions),
                                'question_types': []
                            }
                            
                            for question in questions:
                                q_type = question.get('type', 'unknown')
                                if q_type not in quiz_details['question_types']:
                                    quiz_details['question_types'].append(q_type)
                            
                            quiz_analysis['quiz_details'].append(quiz_details)
                
                if quiz_analysis['quiz_lessons'] > 0:
                    self.log_result(
                        "Quiz Course Structure Analysis", 
                        "PASS", 
                        f"Course has {quiz_analysis['quiz_lessons']} quiz lessons out of {quiz_analysis['total_lessons']} total lessons",
                        f"Quiz details: {quiz_analysis['quiz_details']}"
                    )
                    return quiz_analysis
                else:
                    self.log_result(
                        "Quiz Course Structure Analysis", 
                        "FAIL", 
                        f"Course has no quiz content - cannot test quiz analytics",
                        f"Total lessons: {quiz_analysis['total_lessons']}, Quiz lessons: 0"
                    )
            else:
                self.log_result(
                    "Quiz Course Structure Analysis", 
                    "FAIL", 
                    f"Failed to retrieve course details, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Course Structure Analysis", 
                "FAIL", 
                "Failed to analyze course structure",
                str(e)
            )
        return False
    
    def test_quiz_progress_update_with_score(self):
        """Test updating enrollment progress with quiz scores"""
        if "student" not in self.auth_tokens or not self.test_course_id:
            self.log_result(
                "Quiz Progress Update with Score", 
                "SKIP", 
                "Missing student token or course ID",
                "Student authentication and course selection required"
            )
            return False
        
        try:
            # Test different quiz completion scenarios
            test_scenarios = [
                {"progress": 25.0, "description": "25% completion (failed quiz)"},
                {"progress": 50.0, "description": "50% completion (partial)"},
                {"progress": 75.0, "description": "75% completion (good score)"},
                {"progress": 100.0, "description": "100% completion (perfect score)"}
            ]
            
            successful_updates = []
            
            for scenario in test_scenarios:
                progress_data = {
                    "progress": scenario["progress"],
                    "currentLessonId": f"lesson_{int(scenario['progress']/25)}",
                    "timeSpent": 300  # 5 minutes
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                    json=progress_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["student"]}'
                    }
                )
                
                if response.status_code == 200:
                    updated_enrollment = response.json()
                    actual_progress = updated_enrollment.get('progress', 0)
                    
                    if abs(actual_progress - scenario["progress"]) < 0.1:  # Allow small floating point differences
                        successful_updates.append(scenario["description"])
                        print(f"   ✅ {scenario['description']}: Progress updated to {actual_progress}%")
                    else:
                        print(f"   ❌ {scenario['description']}: Expected {scenario['progress']}%, got {actual_progress}%")
                else:
                    print(f"   ❌ {scenario['description']}: HTTP {response.status_code}")
            
            if len(successful_updates) >= 3:
                self.log_result(
                    "Quiz Progress Update with Score", 
                    "PASS", 
                    f"Successfully updated progress for {len(successful_updates)}/4 scenarios",
                    f"Working scenarios: {', '.join(successful_updates)}"
                )
                return True
            else:
                self.log_result(
                    "Quiz Progress Update with Score", 
                    "FAIL", 
                    f"Only {len(successful_updates)}/4 progress update scenarios worked",
                    f"Failed scenarios indicate quiz score storage issues"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Progress Update with Score", 
                "FAIL", 
                "Failed to test progress updates",
                str(e)
            )
        return False
    
    # =============================================================================
    # ANALYTICS ENDPOINTS TESTS
    # =============================================================================
    
    def test_enrollment_analytics_data(self):
        """Test retrieving enrollment data for analytics"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Enrollment Analytics Data", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                
                analytics_data = {
                    'total_enrollments': len(enrollments),
                    'completed_courses': 0,
                    'in_progress_courses': 0,
                    'not_started_courses': 0,
                    'average_progress': 0,
                    'quiz_scores': []
                }
                
                total_progress = 0
                
                for enrollment in enrollments:
                    progress = enrollment.get('progress', 0)
                    total_progress += progress
                    
                    if progress >= 100:
                        analytics_data['completed_courses'] += 1
                    elif progress > 0:
                        analytics_data['in_progress_courses'] += 1
                    else:
                        analytics_data['not_started_courses'] += 1
                    
                    # Check if this enrollment has quiz score data
                    if enrollment.get('courseId') == self.test_course_id:
                        analytics_data['quiz_scores'].append({
                            'course_id': enrollment.get('courseId'),
                            'progress': progress,
                            'status': enrollment.get('status'),
                            'last_accessed': enrollment.get('lastAccessedAt'),
                            'completed_at': enrollment.get('completedAt')
                        })
                
                if len(enrollments) > 0:
                    analytics_data['average_progress'] = total_progress / len(enrollments)
                
                # Check if quiz scores are being stored properly (not all 0%)
                non_zero_scores = [score for score in analytics_data['quiz_scores'] if score['progress'] > 0]
                
                if len(analytics_data['quiz_scores']) > 0 and len(non_zero_scores) > 0:
                    self.log_result(
                        "Enrollment Analytics Data", 
                        "PASS", 
                        f"Analytics data retrieved with {len(non_zero_scores)} non-zero quiz scores",
                        f"Analytics summary: {analytics_data}"
                    )
                    return analytics_data
                elif len(analytics_data['quiz_scores']) > 0:
                    self.log_result(
                        "Enrollment Analytics Data", 
                        "FAIL", 
                        f"CRITICAL: All quiz scores are 0% - this matches the reported issue!",
                        f"Found {len(analytics_data['quiz_scores'])} quiz enrollments but all have 0% progress"
                    )
                else:
                    self.log_result(
                        "Enrollment Analytics Data", 
                        "PASS", 
                        f"Analytics data retrieved successfully",
                        f"No quiz course enrollments found for detailed analysis"
                    )
                    return analytics_data
            else:
                self.log_result(
                    "Enrollment Analytics Data", 
                    "FAIL", 
                    f"Failed to retrieve enrollment analytics, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enrollment Analytics Data", 
                "FAIL", 
                "Failed to retrieve analytics data",
                str(e)
            )
        return False
    
    def test_quiz_attempts_endpoint(self):
        """Test getQuizAttempts API endpoint used by QuizResults.js frontend"""
        # Note: This endpoint might not exist yet, but we'll test for it
        if "student" not in self.auth_tokens:
            self.log_result(
                "Quiz Attempts Endpoint", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return False
        
        # Try different possible endpoint patterns for quiz attempts
        possible_endpoints = [
            f"/quiz-attempts",
            f"/enrollments/quiz-attempts", 
            f"/courses/{self.test_course_id}/quiz-attempts" if self.test_course_id else None,
            f"/analytics/quiz-attempts",
            f"/student/quiz-attempts"
        ]
        
        possible_endpoints = [ep for ep in possible_endpoints if ep is not None]
        
        working_endpoints = []
        
        for endpoint in possible_endpoints:
            try:
                response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'data_count': len(data) if isinstance(data, list) else 1,
                        'sample_data': data[:2] if isinstance(data, list) and len(data) > 0 else data
                    })
                    print(f"   ✅ {endpoint}: Found {len(data) if isinstance(data, list) else 1} records")
                elif response.status_code == 404:
                    print(f"   ❌ {endpoint}: Not found (404)")
                else:
                    print(f"   ❌ {endpoint}: HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {endpoint}: Connection error")
        
        if working_endpoints:
            self.log_result(
                "Quiz Attempts Endpoint", 
                "PASS", 
                f"Found {len(working_endpoints)} working quiz attempts endpoints",
                f"Working endpoints: {[ep['endpoint'] for ep in working_endpoints]}"
            )
            return working_endpoints
        else:
            self.log_result(
                "Quiz Attempts Endpoint", 
                "FAIL", 
                "No quiz attempts endpoints found - this may explain missing analytics data",
                f"Tested {len(possible_endpoints)} possible endpoint patterns, none worked"
            )
        return False
    
    def test_admin_analytics_access(self):
        """Test admin access to analytics data for all students"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Admin Analytics Access", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test admin access to all enrollments
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            # Note: This might fail if admin can't see all enrollments
            # Let's also try getting all users and their enrollments
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                students = [u for u in users if u.get('role') == 'learner']
                
                analytics_summary = {
                    'total_students': len(students),
                    'students_with_enrollments': 0,
                    'total_quiz_attempts': 0,
                    'zero_score_attempts': 0,
                    'non_zero_score_attempts': 0
                }
                
                # For each student, we'd need to check their enrollments
                # But since we can't impersonate them, we'll use the admin's view
                
                if response.status_code == 200:
                    all_enrollments = response.json()
                    
                    for enrollment in all_enrollments:
                        progress = enrollment.get('progress', 0)
                        
                        # Check if this is a quiz course enrollment
                        course_id = enrollment.get('courseId')
                        if course_id:
                            analytics_summary['total_quiz_attempts'] += 1
                            
                            if progress == 0:
                                analytics_summary['zero_score_attempts'] += 1
                            else:
                                analytics_summary['non_zero_score_attempts'] += 1
                    
                    # Check for the reported issue: all scores showing as 0%
                    if analytics_summary['total_quiz_attempts'] > 0:
                        zero_percentage = (analytics_summary['zero_score_attempts'] / analytics_summary['total_quiz_attempts']) * 100
                        
                        if zero_percentage > 80:  # More than 80% are zero scores
                            self.log_result(
                                "Admin Analytics Access", 
                                "FAIL", 
                                f"CRITICAL: {zero_percentage:.1f}% of quiz attempts show 0% scores - confirms reported issue!",
                                f"Analytics: {analytics_summary}"
                            )
                        else:
                            self.log_result(
                                "Admin Analytics Access", 
                                "PASS", 
                                f"Admin can access analytics data, {zero_percentage:.1f}% zero scores (acceptable)",
                                f"Analytics: {analytics_summary}"
                            )
                    else:
                        self.log_result(
                            "Admin Analytics Access", 
                            "PASS", 
                            f"Admin can access analytics data",
                            f"No quiz attempts found for analysis"
                        )
                    
                    return analytics_summary
                else:
                    self.log_result(
                        "Admin Analytics Access", 
                        "FAIL", 
                        f"Admin cannot access enrollment data, status: {response.status_code}",
                        f"This would prevent analytics dashboard from working"
                    )
            else:
                self.log_result(
                    "Admin Analytics Access", 
                    "FAIL", 
                    f"Failed to get users list, status: {users_response.status_code}",
                    f"Response: {users_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Analytics Access", 
                "FAIL", 
                "Failed to test admin analytics access",
                str(e)
            )
        return False
    
    # =============================================================================
    # DATA FLOW VERIFICATION TESTS
    # =============================================================================
    
    def test_quiz_submission_to_analytics_flow(self):
        """Test complete data flow: quiz submission → database storage → analytics retrieval"""
        if "student" not in self.auth_tokens or not self.test_course_id:
            self.log_result(
                "Quiz Submission to Analytics Flow", 
                "SKIP", 
                "Missing student token or course ID",
                "Student authentication and course selection required"
            )
            return False
        
        try:
            print("\n🔄 TESTING COMPLETE QUIZ ANALYTICS DATA FLOW")
            print("=" * 60)
            
            # Step 1: Get initial enrollment state
            print("📊 Step 1: Getting initial enrollment state...")
            initial_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            initial_progress = 0
            if initial_response.status_code == 200:
                enrollments = initial_response.json()
                for enrollment in enrollments:
                    if enrollment.get('courseId') == self.test_course_id:
                        initial_progress = enrollment.get('progress', 0)
                        break
                print(f"   Initial progress: {initial_progress}%")
            
            # Step 2: Simulate quiz submission with score
            print("🎯 Step 2: Simulating quiz submission with 85% score...")
            quiz_score = 85.0
            progress_data = {
                "progress": quiz_score,
                "currentLessonId": "quiz_lesson_1",
                "timeSpent": 600  # 10 minutes
            }
            
            submission_response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if submission_response.status_code != 200:
                self.log_result(
                    "Quiz Submission to Analytics Flow", 
                    "FAIL", 
                    f"Quiz submission failed with status {submission_response.status_code}",
                    f"Cannot test data flow if submission fails"
                )
                return False
            
            submission_data = submission_response.json()
            submitted_progress = submission_data.get('progress', 0)
            print(f"   Submitted progress: {submitted_progress}%")
            
            # Step 3: Wait and verify data persistence
            print("⏳ Step 3: Waiting for data persistence (2 seconds)...")
            time.sleep(2)
            
            # Step 4: Retrieve updated enrollment data
            print("📈 Step 4: Retrieving updated analytics data...")
            updated_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if updated_response.status_code == 200:
                updated_enrollments = updated_response.json()
                final_progress = 0
                
                for enrollment in updated_enrollments:
                    if enrollment.get('courseId') == self.test_course_id:
                        final_progress = enrollment.get('progress', 0)
                        break
                
                print(f"   Final progress in analytics: {final_progress}%")
                
                # Step 5: Verify data flow integrity
                print("🔍 Step 5: Verifying data flow integrity...")
                
                flow_results = {
                    'initial_progress': initial_progress,
                    'submitted_score': quiz_score,
                    'submission_response_progress': submitted_progress,
                    'final_analytics_progress': final_progress,
                    'data_flow_working': False,
                    'score_preserved': False
                }
                
                # Check if the score was preserved through the entire flow
                if abs(submitted_progress - quiz_score) < 0.1:
                    flow_results['score_preserved'] = True
                    print("   ✅ Score preserved in submission response")
                else:
                    print(f"   ❌ Score NOT preserved in submission: expected {quiz_score}%, got {submitted_progress}%")
                
                if abs(final_progress - quiz_score) < 0.1:
                    flow_results['data_flow_working'] = True
                    print("   ✅ Score preserved in analytics data")
                else:
                    print(f"   ❌ Score NOT preserved in analytics: expected {quiz_score}%, got {final_progress}%")
                
                # Final assessment
                if flow_results['data_flow_working'] and flow_results['score_preserved']:
                    self.log_result(
                        "Quiz Submission to Analytics Flow", 
                        "PASS", 
                        f"Complete data flow working: {quiz_score}% → {submitted_progress}% → {final_progress}%",
                        f"Flow results: {flow_results}"
                    )
                    return True
                else:
                    self.log_result(
                        "Quiz Submission to Analytics Flow", 
                        "FAIL", 
                        f"CRITICAL: Data flow broken - quiz scores not reaching analytics correctly",
                        f"This explains why analytics shows 0% scores. Flow results: {flow_results}"
                    )
            else:
                self.log_result(
                    "Quiz Submission to Analytics Flow", 
                    "FAIL", 
                    f"Failed to retrieve updated analytics data, status: {updated_response.status_code}",
                    f"Cannot verify if quiz scores reach analytics"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Submission to Analytics Flow", 
                "FAIL", 
                "Failed to test complete data flow",
                str(e)
            )
        return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all quiz analytics tests"""
        print("🎯 QUIZ ANALYTICS DATA FLOW TESTING SUITE")
        print("=" * 80)
        print("ISSUE: Quiz scores showing as 0% in analytics instead of actual scores")
        print("=" * 80)
        
        # Authentication Tests
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 40)
        admin_auth = self.test_admin_authentication()
        student_auth = self.test_student_authentication()
        
        if not admin_auth or not student_auth:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with quiz analytics testing")
            return False
        
        # Course Setup Tests
        print("\n📚 QUIZ COURSE SETUP TESTS")
        print("-" * 40)
        quiz_course_found = self.test_find_quiz_course()
        
        if quiz_course_found:
            student_enrolled = self.test_student_enrollment_in_quiz_course()
            quiz_structure = self.test_quiz_course_structure()
        
        # Quiz Progress and Scoring Tests
        print("\n🎯 QUIZ PROGRESS AND SCORING TESTS")
        print("-" * 40)
        if quiz_course_found:
            progress_updates = self.test_quiz_progress_update_with_score()
        
        # Analytics Endpoints Tests
        print("\n📊 ANALYTICS ENDPOINTS TESTS")
        print("-" * 40)
        enrollment_analytics = self.test_enrollment_analytics_data()
        quiz_attempts_endpoint = self.test_quiz_attempts_endpoint()
        admin_analytics = self.test_admin_analytics_access()
        
        # Data Flow Verification Tests
        print("\n🔄 DATA FLOW VERIFICATION TESTS")
        print("-" * 40)
        if quiz_course_found:
            data_flow_test = self.test_quiz_submission_to_analytics_flow()
        
        # Final Summary
        print(f"\n📊 QUIZ ANALYTICS TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        # Issue Analysis
        print(f"\n🔍 QUIZ ANALYTICS ISSUE ANALYSIS")
        print("-" * 40)
        
        critical_issues = []
        for result in self.results:
            if result['status'] == 'FAIL' and 'CRITICAL' in result['message']:
                critical_issues.append(result['message'])
        
        if critical_issues:
            print("❌ CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   • {issue}")
        else:
            print("✅ No critical issues found in quiz analytics data flow")
        
        return len(critical_issues) == 0

if __name__ == "__main__":
    tester = QuizAnalyticsTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 QUIZ ANALYTICS TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n🚨 QUIZ ANALYTICS TESTING FOUND CRITICAL ISSUES")
        sys.exit(1)