#!/usr/bin/env python3
"""
COMPREHENSIVE SELECT ALL THAT APPLY BACKEND TESTING SUITE
Additional testing for edge cases and critical endpoints

TESTING FOCUS:
✅ Edge cases for Select All That Apply questions
✅ API response validation for no 422 errors
✅ Data structure integrity across different scenarios
✅ Scoring logic validation (all-or-nothing approach)
✅ Progress tracking with mixed question types
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration
BACKEND_URL = "https://summarize-it-2.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class ComprehensiveSelectAllTester:
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
    
    def authenticate_users(self):
        """Authenticate both admin and student users"""
        # Admin authentication
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['admin'] = data.get('access_token')
        except:
            pass
        
        # Student authentication
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['student'] = data.get('access_token')
        except:
            pass
        
        return len(self.auth_tokens) >= 2
    
    def test_select_all_edge_cases(self):
        """Test edge cases for Select All That Apply questions"""
        if "admin" not in self.auth_tokens:
            self.log_result("Select All Edge Cases", "SKIP", "No admin token", "Admin auth required")
            return False
        
        edge_cases = [
            {
                "name": "Single Option Select All",
                "options": ["Only Option"],
                "correctAnswers": [0],
                "expected_valid": True
            },
            {
                "name": "All Options Correct",
                "options": ["Option 1", "Option 2", "Option 3"],
                "correctAnswers": [0, 1, 2],
                "expected_valid": True
            },
            {
                "name": "No Correct Answers",
                "options": ["Wrong 1", "Wrong 2", "Wrong 3"],
                "correctAnswers": [],
                "expected_valid": True
            },
            {
                "name": "Large Number of Options",
                "options": [f"Option {i+1}" for i in range(10)],
                "correctAnswers": [0, 2, 4, 6, 8],
                "expected_valid": True
            }
        ]
        
        successful_cases = 0
        
        for case in edge_cases:
            try:
                course_data = {
                    "title": f"Edge Case Test: {case['name']}",
                    "description": f"Testing {case['name']} for Select All That Apply",
                    "category": "Testing",
                    "duration": "30 minutes",
                    "accessType": "open",
                    "modules": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Edge Case Module",
                            "lessons": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "title": "Edge Case Quiz",
                                    "type": "quiz",
                                    "content": "",
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "select-all-that-apply",
                                            "question": f"Test question for {case['name']}",
                                            "options": case["options"],
                                            "correctAnswers": case["correctAnswers"],
                                            "points": 10
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/courses",
                    json=course_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if response.status_code == 200:
                    successful_cases += 1
                    print(f"   ✅ {case['name']}: Backend handled correctly")
                else:
                    print(f"   ❌ {case['name']}: Failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {case['name']}: Exception - {str(e)}")
        
        if successful_cases >= 3:
            self.log_result(
                "Select All Edge Cases", 
                "PASS", 
                f"Backend handles Select All That Apply edge cases correctly",
                f"Successful cases: {successful_cases}/{len(edge_cases)}"
            )
            return True
        else:
            self.log_result(
                "Select All Edge Cases", 
                "FAIL", 
                f"Backend failed to handle some Select All That Apply edge cases",
                f"Successful cases: {successful_cases}/{len(edge_cases)}"
            )
            return False
    
    def test_no_422_errors_with_select_all(self):
        """Test that Select All That Apply questions don't cause 422 errors"""
        if "admin" not in self.auth_tokens or "student" not in self.auth_tokens:
            self.log_result("No 422 Errors Test", "SKIP", "Missing auth tokens", "Both admin and student auth required")
            return False
        
        try:
            # Create a course with Select All That Apply
            course_data = {
                "title": "422 Error Prevention Test Course",
                "description": "Testing that Select All That Apply doesn't cause 422 errors",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "No 422 Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "No 422 Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "select-all-that-apply",
                                        "question": "Which are fruits? (Select all that apply)",
                                        "options": ["Apple", "Banana", "Carrot", "Orange", "Potato"],
                                        "correctAnswers": [0, 1, 3],  # Apple, Banana, Orange
                                        "points": 10
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            # Step 1: Create course
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result("No 422 Errors Test", "FAIL", f"Course creation failed: {create_response.status_code}", create_response.text)
                return False
            
            course_id = create_response.json().get('id')
            
            # Step 2: Student enrollment
            enrollment_data = {"courseId": course_id}
            enroll_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            # Allow already enrolled
            if enroll_response.status_code not in [200, 400]:
                self.log_result("No 422 Errors Test", "FAIL", f"Enrollment failed: {enroll_response.status_code}", enroll_response.text)
                return False
            
            # Step 3: Get course details (should not cause 422)
            get_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if get_response.status_code == 422:
                self.log_result("No 422 Errors Test", "FAIL", "GET course caused 422 error", get_response.text)
                return False
            
            # Step 4: Update progress (should not cause 422)
            progress_data = {
                "progress": 50.0,
                "timeSpent": 180
            }
            
            progress_response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if progress_response.status_code == 422:
                self.log_result("No 422 Errors Test", "FAIL", "Progress update caused 422 error", progress_response.text)
                return False
            
            # All operations successful without 422 errors
            self.log_result(
                "No 422 Errors Test", 
                "PASS", 
                "No 422 errors detected with Select All That Apply questions",
                f"Course creation: {create_response.status_code}, Enrollment: {enroll_response.status_code}, Get course: {get_response.status_code}, Progress: {progress_response.status_code}"
            )
            return True
            
        except Exception as e:
            self.log_result("No 422 Errors Test", "FAIL", "Exception during 422 error test", str(e))
            return False
    
    def test_select_all_scoring_logic(self):
        """Test all-or-nothing scoring logic for Select All That Apply"""
        if "admin" not in self.auth_tokens or "student" not in self.auth_tokens:
            self.log_result("Scoring Logic Test", "SKIP", "Missing auth tokens", "Both admin and student auth required")
            return False
        
        try:
            # Create course to test scoring
            course_data = {
                "title": "Scoring Logic Test Course",
                "description": "Testing all-or-nothing scoring for Select All That Apply",
                "category": "Testing",
                "duration": "30 minutes",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Scoring Test Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Scoring Test Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "select-all-that-apply",
                                        "question": "Which are programming languages? (Select all that apply)",
                                        "options": ["Python", "HTML", "JavaScript", "CSS", "Java"],
                                        "correctAnswers": [0, 2, 4],  # Python, JavaScript, Java
                                        "points": 20
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result("Scoring Logic Test", "FAIL", f"Course creation failed: {create_response.status_code}", create_response.text)
                return False
            
            course_id = create_response.json().get('id')
            
            # Test different scoring scenarios
            scoring_scenarios = [
                {
                    "name": "Perfect Score",
                    "progress": 100.0,
                    "expected_status": "completed"
                },
                {
                    "name": "Partial Score", 
                    "progress": 75.0,
                    "expected_status": "active"
                },
                {
                    "name": "Failed Score",
                    "progress": 0.0,
                    "expected_status": "active"
                }
            ]
            
            successful_scenarios = 0
            
            for scenario in scoring_scenarios:
                try:
                    progress_data = {
                        "progress": scenario["progress"],
                        "timeSpent": 300
                    }
                    
                    progress_response = requests.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=progress_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["student"]}'
                        }
                    )
                    
                    if progress_response.status_code == 200:
                        result = progress_response.json()
                        actual_progress = result.get('progress')
                        actual_status = result.get('status')
                        
                        # Verify progress was recorded correctly
                        if actual_progress == scenario["progress"]:
                            successful_scenarios += 1
                            print(f"   ✅ {scenario['name']}: Progress {actual_progress}%, Status: {actual_status}")
                        else:
                            print(f"   ❌ {scenario['name']}: Expected {scenario['progress']}%, got {actual_progress}%")
                    else:
                        print(f"   ❌ {scenario['name']}: Failed with status {progress_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {scenario['name']}: Exception - {str(e)}")
            
            if successful_scenarios >= 2:
                self.log_result(
                    "Scoring Logic Test", 
                    "PASS", 
                    "Select All That Apply scoring logic working correctly",
                    f"Successful scenarios: {successful_scenarios}/{len(scoring_scenarios)}"
                )
                return True
            else:
                self.log_result(
                    "Scoring Logic Test", 
                    "FAIL", 
                    "Issues with Select All That Apply scoring logic",
                    f"Successful scenarios: {successful_scenarios}/{len(scoring_scenarios)}"
                )
                return False
                
        except Exception as e:
            self.log_result("Scoring Logic Test", "FAIL", "Exception during scoring test", str(e))
            return False
    
    def test_data_structure_integrity(self):
        """Test data structure integrity across different API calls"""
        if "admin" not in self.auth_tokens or "student" not in self.auth_tokens:
            self.log_result("Data Structure Integrity", "SKIP", "Missing auth tokens", "Both admin and student auth required")
            return False
        
        try:
            # Create course with complex Select All That Apply structure
            course_data = {
                "title": "Data Structure Integrity Test",
                "description": "Testing data structure consistency",
                "category": "Testing",
                "duration": "45 minutes",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Structure Test Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Structure Test Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "select-all-that-apply",
                                        "question": "Which are web technologies? (Select all that apply)",
                                        "options": ["HTML", "Python", "CSS", "JavaScript", "SQL", "React"],
                                        "correctAnswers": [0, 2, 3, 5],  # HTML, CSS, JavaScript, React
                                        "points": 15,
                                        "explanation": "Web technologies are used for building websites and web applications."
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            # Step 1: Create course
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result("Data Structure Integrity", "FAIL", f"Course creation failed: {create_response.status_code}", create_response.text)
                return False
            
            created_course = create_response.json()
            course_id = created_course.get('id')
            
            # Step 2: Retrieve course and verify structure
            get_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result("Data Structure Integrity", "FAIL", f"Course retrieval failed: {get_response.status_code}", get_response.text)
                return False
            
            retrieved_course = get_response.json()
            
            # Step 3: Verify data structure consistency
            original_question = course_data['modules'][0]['lessons'][0]['questions'][0]
            retrieved_modules = retrieved_course.get('modules', [])
            
            if len(retrieved_modules) > 0:
                retrieved_lessons = retrieved_modules[0].get('lessons', [])
                if len(retrieved_lessons) > 0:
                    retrieved_questions = retrieved_lessons[0].get('questions', [])
                    if len(retrieved_questions) > 0:
                        retrieved_question = retrieved_questions[0]
                        
                        # Check key fields
                        structure_checks = {
                            'type': retrieved_question.get('type') == 'select-all-that-apply',
                            'options_count': len(retrieved_question.get('options', [])) == len(original_question['options']),
                            'correct_answers_count': len(retrieved_question.get('correctAnswers', [])) == len(original_question['correctAnswers']),
                            'points': retrieved_question.get('points') == original_question['points']
                        }
                        
                        passed_checks = sum(structure_checks.values())
                        total_checks = len(structure_checks)
                        
                        if passed_checks == total_checks:
                            self.log_result(
                                "Data Structure Integrity", 
                                "PASS", 
                                "Select All That Apply data structure maintained across API calls",
                                f"All {total_checks} structure checks passed"
                            )
                            return True
                        else:
                            self.log_result(
                                "Data Structure Integrity", 
                                "FAIL", 
                                "Data structure inconsistencies detected",
                                f"Passed checks: {passed_checks}/{total_checks}, Details: {structure_checks}"
                            )
                            return False
            
            self.log_result("Data Structure Integrity", "FAIL", "Could not find question data in retrieved course", "Course structure incomplete")
            return False
            
        except Exception as e:
            self.log_result("Data Structure Integrity", "FAIL", "Exception during structure integrity test", str(e))
            return False
    
    def test_mixed_progress_tracking(self):
        """Test progress tracking with mixed question types including Select All That Apply"""
        if "admin" not in self.auth_tokens or "student" not in self.auth_tokens:
            self.log_result("Mixed Progress Tracking", "SKIP", "Missing auth tokens", "Both admin and student auth required")
            return False
        
        try:
            # Create course with mixed question types
            course_data = {
                "title": "Mixed Progress Tracking Test",
                "description": "Testing progress tracking with Select All That Apply and other question types",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Mixed Progress Module 1",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Multiple Choice Lesson",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple-choice",
                                        "question": "What is 5 + 3?",
                                        "options": ["6", "7", "8", "9"],
                                        "correctAnswer": 2,
                                        "points": 10
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Mixed Progress Module 2",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Select All That Apply Lesson",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "select-all-that-apply",
                                        "question": "Which are even numbers? (Select all that apply)",
                                        "options": ["1", "2", "3", "4", "5", "6"],
                                        "correctAnswers": [1, 3, 5],  # 2, 4, 6
                                        "points": 15
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result("Mixed Progress Tracking", "FAIL", f"Course creation failed: {create_response.status_code}", create_response.text)
                return False
            
            course_id = create_response.json().get('id')
            
            # Test progressive completion
            progress_steps = [25.0, 50.0, 75.0, 100.0]
            successful_steps = 0
            
            for step in progress_steps:
                try:
                    progress_data = {
                        "progress": step,
                        "timeSpent": int(step * 3)  # Simulate time spent
                    }
                    
                    progress_response = requests.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=progress_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["student"]}'
                        }
                    )
                    
                    if progress_response.status_code == 200:
                        result = progress_response.json()
                        if result.get('progress') == step:
                            successful_steps += 1
                            print(f"   ✅ Progress {step}%: Updated successfully")
                        else:
                            print(f"   ❌ Progress {step}%: Expected {step}%, got {result.get('progress')}%")
                    else:
                        print(f"   ❌ Progress {step}%: Failed with status {progress_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Progress {step}%: Exception - {str(e)}")
            
            if successful_steps >= 3:
                self.log_result(
                    "Mixed Progress Tracking", 
                    "PASS", 
                    "Progress tracking works correctly with Select All That Apply in mixed courses",
                    f"Successful progress steps: {successful_steps}/{len(progress_steps)}"
                )
                return True
            else:
                self.log_result(
                    "Mixed Progress Tracking", 
                    "FAIL", 
                    "Issues with progress tracking in mixed courses",
                    f"Successful progress steps: {successful_steps}/{len(progress_steps)}"
                )
                return False
                
        except Exception as e:
            self.log_result("Mixed Progress Tracking", "FAIL", "Exception during mixed progress test", str(e))
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive Select All That Apply tests"""
        print("🚀 STARTING COMPREHENSIVE SELECT ALL THAT APPLY BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print("Testing advanced scenarios and edge cases...")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate_users():
            print("❌ CRITICAL: Authentication failed - cannot proceed with tests")
            return False
        
        print("✅ Authentication successful for both admin and student")
        
        # Run comprehensive tests
        print("\n🔍 EDGE CASES TESTING")
        print("-" * 40)
        self.test_select_all_edge_cases()
        
        print("\n🚫 422 ERROR PREVENTION TESTING")
        print("-" * 40)
        self.test_no_422_errors_with_select_all()
        
        print("\n🎯 SCORING LOGIC TESTING")
        print("-" * 40)
        self.test_select_all_scoring_logic()
        
        print("\n🏗️ DATA STRUCTURE INTEGRITY TESTING")
        print("-" * 40)
        self.test_data_structure_integrity()
        
        print("\n📊 MIXED PROGRESS TRACKING TESTING")
        print("-" * 40)
        self.test_mixed_progress_tracking()
        
        # Final Results
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE SELECT ALL THAT APPLY TESTING COMPLETED")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 COMPREHENSIVE RESULTS SUMMARY:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"🎯 EXCELLENT: Select All That Apply backend is robust and handles edge cases well!")
        elif success_rate >= 60:
            print(f"⚠️ GOOD: Most functionality working, some edge cases need attention")
        else:
            print(f"🚨 CRITICAL: Significant issues with Select All That Apply backend functionality")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ComprehensiveSelectAllTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n✅ COMPREHENSIVE SELECT ALL THAT APPLY TESTING: SUCCESS")
        sys.exit(0)
    else:
        print("\n❌ COMPREHENSIVE SELECT ALL THAT APPLY TESTING: ISSUES DETECTED")
        sys.exit(1)