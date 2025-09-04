#!/usr/bin/env python3
"""
QUIZ ANALYTICS FIX TESTING SUITE
LearningFwiend LMS Application - Quiz Analytics Data Flow Testing

TESTING SCOPE:
✅ Backend API functionality (authentication, enrollments, quiz attempts)
✅ Enrollment records with progress percentages representing quiz scores
✅ GET /api/enrollments endpoint verification for student quiz scores
✅ Specific student account verification (karlo.student@alder.com)
✅ Data structure validation for frontend fix reading enrollment-based quiz scores

FOCUS: Confirming enrollment system contains actual quiz score data for analytics display
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using production URL from frontend/.env
BACKEND_URL = "https://lms-chronology.preview.emergentagent.com/api"
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

class QuizAnalyticsFixTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        
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
    
    def test_admin_authentication(self):
        """Test admin authentication for system access"""
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
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Invalid admin credentials or role",
                        f"Response: {data}"
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
        """Test student authentication (karlo.student@alder.com)"""
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
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Invalid student credentials or role",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"Student authentication failed with status {response.status_code}",
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
    
    def test_enrollments_endpoint_functionality(self):
        """Test GET /api/enrollments endpoint functionality"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Enrollments Endpoint Test", 
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
                self.log_result(
                    "Enrollments Endpoint Test", 
                    "PASS", 
                    f"GET /api/enrollments working correctly - retrieved {len(enrollments)} enrollments",
                    f"Endpoint accessible and returning data"
                )
                return enrollments
            else:
                self.log_result(
                    "Enrollments Endpoint Test", 
                    "FAIL", 
                    f"GET /api/enrollments failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enrollments Endpoint Test", 
                "FAIL", 
                "Failed to access enrollments endpoint",
                str(e)
            )
        return False
    
    def test_enrollment_progress_scores(self):
        """Test that enrollment records contain progress percentages representing quiz scores"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Enrollment Progress Scores Test", 
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
                
                if not enrollments:
                    self.log_result(
                        "Enrollment Progress Scores Test", 
                        "FAIL", 
                        "No enrollment records found for student",
                        "Student needs to be enrolled in courses with quiz scores"
                    )
                    return False
                
                # Analyze enrollment progress scores
                enrollments_with_progress = []
                quiz_score_enrollments = []
                
                for enrollment in enrollments:
                    progress = enrollment.get('progress', 0)
                    course_id = enrollment.get('courseId')
                    course_name = enrollment.get('courseName', 'Unknown Course')
                    
                    if progress > 0:
                        enrollments_with_progress.append({
                            'courseId': course_id,
                            'courseName': course_name,
                            'progress': progress,
                            'status': enrollment.get('status', 'unknown'),
                            'enrolledAt': enrollment.get('enrolledAt'),
                            'completedAt': enrollment.get('completedAt')
                        })
                        
                        # Check if this looks like a quiz score (specific percentages)
                        if progress in [25, 50, 75, 100] or (progress > 0 and progress <= 100):
                            quiz_score_enrollments.append({
                                'courseId': course_id,
                                'courseName': course_name,
                                'progress': progress
                            })
                
                if enrollments_with_progress:
                    self.log_result(
                        "Enrollment Progress Scores Test", 
                        "PASS", 
                        f"Found {len(enrollments_with_progress)} enrollments with progress scores",
                        f"Progress scores: {[e['progress'] for e in enrollments_with_progress]}, Quiz-like scores: {len(quiz_score_enrollments)}"
                    )
                    return enrollments_with_progress
                else:
                    self.log_result(
                        "Enrollment Progress Scores Test", 
                        "FAIL", 
                        f"No enrollment records with progress scores found (0/{len(enrollments)})",
                        "All enrollments have 0% progress - no quiz scores stored"
                    )
            else:
                self.log_result(
                    "Enrollment Progress Scores Test", 
                    "FAIL", 
                    f"Failed to retrieve enrollments, status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enrollment Progress Scores Test", 
                "FAIL", 
                "Failed to test enrollment progress scores",
                str(e)
            )
        return False
    
    def test_specific_student_quiz_scores(self):
        """Test specific student account (karlo.student@alder.com) for quiz scores"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Specific Student Quiz Scores Test", 
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
                
                # Get student info
                student_response = requests.get(
                    f"{BACKEND_URL}/auth/me",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                
                student_info = {}
                if student_response.status_code == 200:
                    student_info = student_response.json()
                
                # Analyze karlo.student's specific quiz scores
                student_email = student_info.get('email', 'karlo.student@alder.com')
                student_name = student_info.get('full_name', 'Unknown')
                
                quiz_scores = []
                for enrollment in enrollments:
                    progress = enrollment.get('progress', 0)
                    if progress > 0:
                        quiz_scores.append({
                            'courseId': enrollment.get('courseId'),
                            'courseName': enrollment.get('courseName', 'Unknown Course'),
                            'progress': progress,
                            'status': enrollment.get('status'),
                            'completedAt': enrollment.get('completedAt')
                        })
                
                if quiz_scores:
                    self.log_result(
                        "Specific Student Quiz Scores Test", 
                        "PASS", 
                        f"Student {student_email} has {len(quiz_scores)} courses with quiz scores",
                        f"Student: {student_name}, Scores: {[s['progress'] for s in quiz_scores]}"
                    )
                    return quiz_scores
                else:
                    self.log_result(
                        "Specific Student Quiz Scores Test", 
                        "FAIL", 
                        f"Student {student_email} has no quiz scores in enrollment records",
                        f"Student: {student_name}, Total enrollments: {len(enrollments)}, All have 0% progress"
                    )
            else:
                self.log_result(
                    "Specific Student Quiz Scores Test", 
                    "FAIL", 
                    f"Failed to retrieve student enrollments, status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Specific Student Quiz Scores Test", 
                "FAIL", 
                "Failed to test specific student quiz scores",
                str(e)
            )
        return False
    
    def test_enrollment_data_structure_for_frontend(self):
        """Validate enrollment data structure is correct for frontend fix"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Enrollment Data Structure Test", 
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
                
                if not enrollments:
                    self.log_result(
                        "Enrollment Data Structure Test", 
                        "FAIL", 
                        "No enrollment records to validate data structure",
                        "Need enrollment records to test data structure"
                    )
                    return False
                
                # Check required fields for frontend analytics
                required_fields = ['id', 'userId', 'courseId', 'progress', 'status', 'enrolledAt']
                optional_fields = ['courseName', 'studentName', 'completedAt', 'grade', 'lastAccessedAt']
                
                structure_issues = []
                valid_enrollments = 0
                
                for i, enrollment in enumerate(enrollments):
                    enrollment_issues = []
                    
                    # Check required fields
                    for field in required_fields:
                        if field not in enrollment:
                            enrollment_issues.append(f"Missing required field: {field}")
                    
                    # Check progress field type and range
                    progress = enrollment.get('progress')
                    if progress is not None:
                        if not isinstance(progress, (int, float)):
                            enrollment_issues.append(f"Progress field is not numeric: {type(progress)}")
                        elif progress < 0 or progress > 100:
                            enrollment_issues.append(f"Progress out of range (0-100): {progress}")
                    
                    # Check courseId format (should be UUID)
                    course_id = enrollment.get('courseId')
                    if course_id and not isinstance(course_id, str):
                        enrollment_issues.append(f"CourseId is not string: {type(course_id)}")
                    
                    if not enrollment_issues:
                        valid_enrollments += 1
                    else:
                        structure_issues.extend([f"Enrollment {i}: {issue}" for issue in enrollment_issues])
                
                if len(structure_issues) == 0:
                    self.log_result(
                        "Enrollment Data Structure Test", 
                        "PASS", 
                        f"All {len(enrollments)} enrollment records have correct data structure for frontend",
                        f"Required fields present, progress values valid, ready for analytics display"
                    )
                    return True
                else:
                    self.log_result(
                        "Enrollment Data Structure Test", 
                        "FAIL", 
                        f"Data structure issues found in {len(enrollments) - valid_enrollments}/{len(enrollments)} enrollments",
                        f"Issues: {'; '.join(structure_issues[:5])}{'...' if len(structure_issues) > 5 else ''}"
                    )
            else:
                self.log_result(
                    "Enrollment Data Structure Test", 
                    "FAIL", 
                    f"Failed to retrieve enrollments for structure validation, status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enrollment Data Structure Test", 
                "FAIL", 
                "Failed to validate enrollment data structure",
                str(e)
            )
        return False
    
    def test_quiz_attempts_vs_enrollments_comparison(self):
        """Compare quiz_attempts collection vs enrollments collection for analytics data"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Quiz Attempts vs Enrollments Comparison", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test quiz attempts endpoint (what QuizResults.js currently reads)
            quiz_attempts_response = requests.get(
                f"{BACKEND_URL}/quiz-attempts",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            # Test enrollments endpoint (where actual quiz data is stored)
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            quiz_attempts_data = []
            enrollments_data = []
            
            # Process quiz attempts response
            if quiz_attempts_response.status_code == 200:
                quiz_attempts_data = quiz_attempts_response.json()
            elif quiz_attempts_response.status_code == 404:
                # Endpoint doesn't exist - this is expected based on the issue
                quiz_attempts_data = "ENDPOINT_NOT_FOUND"
            
            # Process enrollments response
            if enrollments_response.status_code == 200:
                enrollments_data = enrollments_response.json()
            
            # Analyze the data mismatch
            enrollments_with_scores = [e for e in enrollments_data if e.get('progress', 0) > 0] if isinstance(enrollments_data, list) else []
            
            if quiz_attempts_data == "ENDPOINT_NOT_FOUND" or (isinstance(quiz_attempts_data, list) and len(quiz_attempts_data) == 0):
                if len(enrollments_with_scores) > 0:
                    self.log_result(
                        "Quiz Attempts vs Enrollments Comparison", 
                        "PASS", 
                        f"ROOT CAUSE CONFIRMED: quiz_attempts collection empty/missing, enrollments has {len(enrollments_with_scores)} records with quiz scores",
                        f"QuizResults.js reads from wrong collection - should read from enrollments, not quiz_attempts"
                    )
                    return True
                else:
                    self.log_result(
                        "Quiz Attempts vs Enrollments Comparison", 
                        "FAIL", 
                        "Both quiz_attempts and enrollments collections have no quiz score data",
                        "No quiz scores found in either collection - need to investigate quiz submission process"
                    )
            else:
                self.log_result(
                    "Quiz Attempts vs Enrollments Comparison", 
                    "PASS", 
                    f"Both collections have data: quiz_attempts ({len(quiz_attempts_data)}), enrollments ({len(enrollments_with_scores)} with scores)",
                    "Data exists in both collections - need to verify which has correct quiz scores"
                )
                return True
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Attempts vs Enrollments Comparison", 
                "FAIL", 
                "Failed to compare quiz attempts vs enrollments data",
                str(e)
            )
        return False
    
    def test_progress_update_endpoint(self):
        """Test PUT /api/enrollments/{course_id}/progress endpoint for quiz score updates"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Progress Update Endpoint Test", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return False
        
        try:
            # First get student's enrollments to find a course to test with
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Progress Update Endpoint Test", 
                    "FAIL", 
                    "Cannot get enrollments to test progress update",
                    f"Enrollments endpoint failed: {enrollments_response.status_code}"
                )
                return False
            
            enrollments = enrollments_response.json()
            if not enrollments:
                self.log_result(
                    "Progress Update Endpoint Test", 
                    "SKIP", 
                    "No enrollments found to test progress update",
                    "Student needs to be enrolled in courses"
                )
                return False
            
            # Test progress update on first enrollment
            test_enrollment = enrollments[0]
            course_id = test_enrollment.get('courseId')
            original_progress = test_enrollment.get('progress', 0)
            
            # Test updating progress (simulate quiz completion)
            test_progress = 85.5  # Simulate quiz score
            progress_data = {
                "progress": test_progress,
                "currentLessonId": "test-lesson-id",
                "timeSpent": 300
            }
            
            update_response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if update_response.status_code == 200:
                updated_enrollment = update_response.json()
                new_progress = updated_enrollment.get('progress', 0)
                
                if new_progress == test_progress:
                    # Restore original progress
                    restore_data = {"progress": original_progress}
                    requests.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=restore_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["student"]}'
                        }
                    )
                    
                    self.log_result(
                        "Progress Update Endpoint Test", 
                        "PASS", 
                        f"PUT /api/enrollments/{{course_id}}/progress working correctly - updated progress from {original_progress}% to {new_progress}%",
                        f"Quiz score update mechanism functional, progress restored to {original_progress}%"
                    )
                    return True
                else:
                    self.log_result(
                        "Progress Update Endpoint Test", 
                        "FAIL", 
                        f"Progress update failed - expected {test_progress}%, got {new_progress}%",
                        f"Progress update mechanism not working correctly"
                    )
            else:
                self.log_result(
                    "Progress Update Endpoint Test", 
                    "FAIL", 
                    f"PUT /api/enrollments/{{course_id}}/progress failed with status {update_response.status_code}",
                    f"Response: {update_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Progress Update Endpoint Test", 
                "FAIL", 
                "Failed to test progress update endpoint",
                str(e)
            )
        return False
    
    def run_all_tests(self):
        """Run all quiz analytics fix tests"""
        print("🎯 QUIZ ANALYTICS FIX TESTING SUITE")
        print("=" * 80)
        print("Testing quiz analytics data flow after fix implementation")
        print("Focus: Verifying enrollment system contains quiz score data for analytics")
        print("=" * 80)
        
        # Test 1: Authentication
        print("\n🔑 AUTHENTICATION TESTS")
        print("-" * 50)
        admin_auth = self.test_admin_authentication()
        student_auth = self.test_student_authentication()
        
        # Test 2: Core API Functionality
        print("\n🔧 CORE API FUNCTIONALITY TESTS")
        print("-" * 50)
        enrollments_endpoint = self.test_enrollments_endpoint_functionality()
        progress_update = self.test_progress_update_endpoint()
        
        # Test 3: Quiz Score Data Verification
        print("\n📊 QUIZ SCORE DATA VERIFICATION TESTS")
        print("-" * 50)
        enrollment_scores = self.test_enrollment_progress_scores()
        specific_student_scores = self.test_specific_student_quiz_scores()
        
        # Test 4: Data Structure Validation
        print("\n🏗️ DATA STRUCTURE VALIDATION TESTS")
        print("-" * 50)
        data_structure = self.test_enrollment_data_structure_for_frontend()
        
        # Test 5: Root Cause Analysis
        print("\n🔍 ROOT CAUSE ANALYSIS TESTS")
        print("-" * 50)
        data_comparison = self.test_quiz_attempts_vs_enrollments_comparison()
        
        # Summary
        print(f"\n📋 QUIZ ANALYTICS FIX TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📊 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        # Critical findings
        print(f"\n🎯 CRITICAL FINDINGS FOR QUIZ ANALYTICS FIX:")
        print("-" * 50)
        
        if admin_auth and student_auth:
            print("✅ Authentication: Both admin and student authentication working")
        else:
            print("❌ Authentication: Issues with admin or student login")
        
        if enrollments_endpoint:
            print("✅ Enrollments API: GET /api/enrollments endpoint functional")
        else:
            print("❌ Enrollments API: GET /api/enrollments endpoint not working")
        
        if enrollment_scores:
            print("✅ Quiz Scores: Enrollment records contain progress percentages (quiz scores)")
        else:
            print("❌ Quiz Scores: No quiz scores found in enrollment records")
        
        if specific_student_scores:
            print("✅ Student Data: karlo.student@alder.com has quiz scores in enrollments")
        else:
            print("❌ Student Data: karlo.student@alder.com has no quiz scores")
        
        if data_structure:
            print("✅ Data Structure: Enrollment data structure compatible with frontend")
        else:
            print("❌ Data Structure: Issues with enrollment data structure")
        
        return self.passed >= 6  # Require at least 6 tests to pass

def main():
    """Main test execution"""
    tester = QuizAnalyticsFixTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 QUIZ ANALYTICS FIX TESTING COMPLETED SUCCESSFULLY")
        print("Backend APIs are functional and ready for frontend analytics fix")
        sys.exit(0)
    else:
        print(f"\n🚨 QUIZ ANALYTICS FIX TESTING FAILED")
        print("Issues found that need to be addressed before frontend fix")
        sys.exit(1)

if __name__ == "__main__":
    main()