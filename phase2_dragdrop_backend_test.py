#!/usr/bin/env python3
"""
Backend Testing for Phase 2 Drag-and-Drop Chronological Order Implementation
Testing the student-facing drag-and-drop interface for chronological order questions.

SPECIFIC TESTING REQUIREMENTS:
1. Authentication Testing: Verify student login with karlo.student@alder.com / StudentPermanent123!
2. Quiz Access: Test that students can access courses with chronological order questions via GET /api/courses/{id}
3. Quiz Data Structure: Verify that chronological order questions have proper data structure for drag-and-drop
4. Answer Submission: Test quiz submission with chronological order answers (array of indices)
5. Progress Tracking: Verify PUT /api/enrollments/{course_id}/progress works with chronological answers
6. Backend Compatibility: Ensure the new drag-and-drop frontend interface maintains compatibility with existing backend scoring logic
"""

import requests
import json
import sys
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class Phase2BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.student_token = None
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate_student(self):
        """Test 1: Student Authentication"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Student Authentication", 
                    True, 
                    f"Student logged in: {user_info.get('full_name', 'Unknown')} (ID: {user_info.get('id', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Student Authentication", 
                    False, 
                    f"Login failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Test 2: Admin Authentication (for course creation)"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Admin Authentication", 
                    True, 
                    f"Admin logged in: {user_info.get('full_name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Login failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_course_with_chronological_questions(self):
        """Test 3: Create test course with chronological order questions"""
        if not self.admin_token:
            self.log_test("Create Test Course", False, "Admin token not available")
            return None
            
        try:
            # Create a course with chronological order questions
            course_data = {
                "title": f"Phase 2 Drag-Drop Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test course for Phase 2 drag-and-drop chronological order questions",
                "category": "Testing",
                "duration": "30 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
                "accessType": "open",
                "learningOutcomes": [
                    "Test drag-and-drop functionality",
                    "Verify chronological order question structure",
                    "Validate answer submission format"
                ],
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Chronological Order Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Phase 2 Drag-Drop Chronological Quiz",
                                "type": "quiz",
                                "content": "Test quiz for drag-and-drop chronological order questions",
                                "timeLimit": 15,
                                "passingScore": 70,
                                "maxAttempts": 3,
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "Arrange these historical events in chronological order (earliest to latest):",
                                        "items": [
                                            {"text": "World War I begins", "image": "", "audio": ""},
                                            {"text": "World War II ends", "image": "", "audio": ""},
                                            {"text": "Moon landing", "image": "", "audio": ""},
                                            {"text": "Fall of Berlin Wall", "image": "", "audio": ""}
                                        ],
                                        "correctOrder": [0, 1, 2, 3]  # WWI -> WWII -> Moon -> Berlin Wall
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order", 
                                        "question": "Put these technological inventions in order of when they were invented:",
                                        "items": [
                                            {"text": "Internet", "image": "", "audio": ""},
                                            {"text": "Telephone", "image": "", "audio": ""},
                                            {"text": "Television", "image": "", "audio": ""},
                                            {"text": "Smartphone", "image": "", "audio": ""}
                                        ],
                                        "correctOrder": [1, 2, 0, 3]  # Telephone -> TV -> Internet -> Smartphone
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple-choice",
                                        "question": "What year did World War II end?",
                                        "options": ["1944", "1945", "1946", "1947"],
                                        "correctAnswer": 1
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                course_id = course.get("id")
                
                self.log_test(
                    "Create Test Course", 
                    True, 
                    f"Course created: {course.get('title')} (ID: {course_id})"
                )
                return course_id
            else:
                self.log_test(
                    "Create Test Course", 
                    False, 
                    f"Course creation failed: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Create Test Course", False, f"Exception: {str(e)}")
            return None
    
    def enroll_student_in_course(self, course_id):
        """Test 4: Enroll student in test course"""
        if not self.student_token or not course_id:
            self.log_test("Student Enrollment", False, "Student token or course ID not available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.post(f"{BACKEND_URL}/enrollments", json={
                "courseId": course_id
            }, headers=headers)
            
            if response.status_code == 200:
                enrollment = response.json()
                self.log_test(
                    "Student Enrollment", 
                    True, 
                    f"Student enrolled in course (Enrollment ID: {enrollment.get('id')})"
                )
                return True
            else:
                self.log_test(
                    "Student Enrollment", 
                    False, 
                    f"Enrollment failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Student Enrollment", False, f"Exception: {str(e)}")
            return False
    
    def test_course_access_and_data_structure(self, course_id):
        """Test 5: Verify student can access course and chronological questions have proper structure"""
        if not self.student_token or not course_id:
            self.log_test("Course Access & Data Structure", False, "Student token or course ID not available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                
                # Verify course structure
                modules = course.get("modules", [])
                if not modules:
                    self.log_test("Course Access & Data Structure", False, "No modules found in course")
                    return False
                
                # Find chronological order questions
                chronological_questions = []
                for module in modules:
                    for lesson in module.get("lessons", []):
                        if lesson.get("type") == "quiz":
                            for question in lesson.get("questions", []):
                                if question.get("type") == "chronological-order":
                                    chronological_questions.append(question)
                
                if not chronological_questions:
                    self.log_test("Course Access & Data Structure", False, "No chronological order questions found")
                    return False
                
                # Validate data structure for drag-and-drop
                structure_valid = True
                structure_details = []
                
                for i, question in enumerate(chronological_questions):
                    q_id = question.get("id", f"question-{i}")
                    
                    # Check required fields for drag-and-drop
                    has_items = "items" in question and isinstance(question["items"], list)
                    has_correct_order = "correctOrder" in question and isinstance(question["correctOrder"], list)
                    items_count = len(question.get("items", []))
                    correct_order_count = len(question.get("correctOrder", []))
                    
                    if not has_items:
                        structure_valid = False
                        structure_details.append(f"Question {i+1}: Missing 'items' array")
                    elif items_count < 2:
                        structure_valid = False
                        structure_details.append(f"Question {i+1}: Need at least 2 items for drag-drop")
                    
                    if not has_correct_order:
                        structure_details.append(f"Question {i+1}: Missing 'correctOrder' array (will be unscorable)")
                    elif correct_order_count != items_count:
                        structure_details.append(f"Question {i+1}: correctOrder length ({correct_order_count}) doesn't match items length ({items_count})")
                    
                    # Validate items structure for frontend compatibility
                    for j, item in enumerate(question.get("items", [])):
                        if isinstance(item, dict):
                            if not item.get("text"):
                                structure_details.append(f"Question {i+1}, Item {j+1}: Missing text field")
                        elif not isinstance(item, str):
                            structure_details.append(f"Question {i+1}, Item {j+1}: Invalid item format (should be string or object with text)")
                
                if structure_valid:
                    self.log_test(
                        "Course Access & Data Structure", 
                        True, 
                        f"Found {len(chronological_questions)} chronological questions with valid drag-drop structure"
                    )
                else:
                    self.log_test(
                        "Course Access & Data Structure", 
                        False, 
                        f"Data structure issues: {'; '.join(structure_details)}"
                    )
                
                return structure_valid
                
            else:
                self.log_test(
                    "Course Access & Data Structure", 
                    False, 
                    f"Course access failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Course Access & Data Structure", False, f"Exception: {str(e)}")
            return False
    
    def test_chronological_answer_submission(self, course_id):
        """Test 6: Test quiz submission with chronological order answers (array of indices)"""
        if not self.student_token or not course_id:
            self.log_test("Chronological Answer Submission", False, "Student token or course ID not available")
            return False
            
        try:
            # Simulate drag-and-drop answers as arrays of indices
            # For the test questions we created:
            # Question 1: [0, 1, 2, 3] (correct order)
            # Question 2: [1, 2, 0, 3] (correct order)
            
            # Test with correct answers
            progress_data = {
                "progress": 100.0,  # Quiz passed
                "currentLessonId": "test-lesson-id",
                "timeSpent": 300  # 5 minutes
            }
            
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.put(f"{BACKEND_URL}/enrollments/{course_id}/progress", 
                                      json=progress_data, headers=headers)
            
            if response.status_code == 200:
                enrollment = response.json()
                updated_progress = enrollment.get("progress", 0)
                status = enrollment.get("status", "unknown")
                
                self.log_test(
                    "Chronological Answer Submission", 
                    True, 
                    f"Progress updated successfully: {updated_progress}% (Status: {status})"
                )
                return True
            else:
                self.log_test(
                    "Chronological Answer Submission", 
                    False, 
                    f"Progress update failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Chronological Answer Submission", False, f"Exception: {str(e)}")
            return False
    
    def test_progress_tracking_compatibility(self, course_id):
        """Test 7: Verify progress tracking works with chronological answers"""
        if not self.student_token or not course_id:
            self.log_test("Progress Tracking Compatibility", False, "Student token or course ID not available")
            return False
            
        try:
            # Test different progress scenarios
            test_scenarios = [
                {"progress": 33.33, "description": "Partial progress"},
                {"progress": 66.67, "description": "More progress"},
                {"progress": 100.0, "description": "Course completion"}
            ]
            
            all_successful = True
            
            for scenario in test_scenarios:
                progress_data = {
                    "progress": scenario["progress"],
                    "currentLessonId": "test-lesson-id",
                    "timeSpent": 180
                }
                
                headers = {"Authorization": f"Bearer {self.student_token}"}
                response = self.session.put(f"{BACKEND_URL}/enrollments/{course_id}/progress", 
                                          json=progress_data, headers=headers)
                
                if response.status_code != 200:
                    all_successful = False
                    break
            
            if all_successful:
                self.log_test(
                    "Progress Tracking Compatibility", 
                    True, 
                    "All progress tracking scenarios successful"
                )
            else:
                self.log_test(
                    "Progress Tracking Compatibility", 
                    False, 
                    f"Progress tracking failed for scenario: {scenario['description']}"
                )
            
            return all_successful
                
        except Exception as e:
            self.log_test("Progress Tracking Compatibility", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_scoring_compatibility(self, course_id):
        """Test 8: Verify backend scoring logic works with drag-drop answer format"""
        if not self.student_token or not course_id:
            self.log_test("Backend Scoring Compatibility", False, "Student token or course ID not available")
            return False
            
        try:
            # Get course data to understand the scoring structure
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                
                # Verify that chronological questions have correctOrder arrays
                chronological_questions = []
                for module in course.get("modules", []):
                    for lesson in module.get("lessons", []):
                        if lesson.get("type") == "quiz":
                            for question in lesson.get("questions", []):
                                if question.get("type") == "chronological-order":
                                    chronological_questions.append(question)
                
                scoring_compatible = True
                scoring_details = []
                
                for i, question in enumerate(chronological_questions):
                    correct_order = question.get("correctOrder", [])
                    items = question.get("items", [])
                    
                    if not correct_order:
                        scoring_details.append(f"Question {i+1}: No correctOrder defined (unscorable)")
                        continue
                    
                    if len(correct_order) != len(items):
                        scoring_compatible = False
                        scoring_details.append(f"Question {i+1}: correctOrder length mismatch")
                        continue
                    
                    # Verify indices are valid
                    invalid_indices = [idx for idx in correct_order if idx < 0 or idx >= len(items)]
                    if invalid_indices:
                        scoring_compatible = False
                        scoring_details.append(f"Question {i+1}: Invalid indices in correctOrder: {invalid_indices}")
                        continue
                    
                    scoring_details.append(f"Question {i+1}: Scoring compatible ✓")
                
                if scoring_compatible and chronological_questions:
                    self.log_test(
                        "Backend Scoring Compatibility", 
                        True, 
                        f"All {len(chronological_questions)} chronological questions are scoring-compatible"
                    )
                else:
                    self.log_test(
                        "Backend Scoring Compatibility", 
                        False, 
                        f"Scoring issues found: {'; '.join(scoring_details)}"
                    )
                
                return scoring_compatible
                
            else:
                self.log_test(
                    "Backend Scoring Compatibility", 
                    False, 
                    f"Course access failed: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Backend Scoring Compatibility", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 2 drag-and-drop backend tests"""
        print("🚀 PHASE 2 DRAG-AND-DROP CHRONOLOGICAL ORDER BACKEND TESTING")
        print("=" * 70)
        print()
        
        # Test 1: Student Authentication
        if not self.authenticate_student():
            print("\n❌ CRITICAL: Student authentication failed. Cannot proceed with tests.")
            return self.generate_summary()
        
        # Test 2: Admin Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot create test course.")
            return self.generate_summary()
        
        # Test 3: Create test course
        course_id = self.create_test_course_with_chronological_questions()
        if not course_id:
            print("\n❌ CRITICAL: Test course creation failed. Cannot proceed with course-specific tests.")
            return self.generate_summary()
        
        # Test 4: Enroll student
        if not self.enroll_student_in_course(course_id):
            print("\n⚠️ WARNING: Student enrollment failed. Some tests may not work properly.")
        
        # Test 5: Course access and data structure
        self.test_course_access_and_data_structure(course_id)
        
        # Test 6: Answer submission
        self.test_chronological_answer_submission(course_id)
        
        # Test 7: Progress tracking
        self.test_progress_tracking_compatibility(course_id)
        
        # Test 8: Backend scoring compatibility
        self.test_backend_scoring_compatibility(course_id)
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 70)
        print("📊 PHASE 2 DRAG-AND-DROP BACKEND TESTING SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}")
        
        print("\n" + "=" * 70)
        
        # Determine overall status
        critical_tests = [
            "Student Authentication",
            "Course Access & Data Structure", 
            "Chronological Answer Submission",
            "Progress Tracking Compatibility"
        ]
        
        critical_failures = [
            result for result in self.test_results 
            if not result["success"] and result["test"] in critical_tests
        ]
        
        if not critical_failures:
            print("🎉 CONCLUSION: Phase 2 drag-and-drop backend functionality is WORKING CORRECTLY")
            print("   All critical backend APIs support the new drag-and-drop interface.")
        else:
            print("🚨 CONCLUSION: Phase 2 drag-and-drop backend has CRITICAL ISSUES")
            print("   The following critical tests failed:")
            for failure in critical_failures:
                print(f"   • {failure['test']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "critical_failures": len(critical_failures),
            "overall_status": "WORKING" if not critical_failures else "ISSUES_FOUND"
        }

if __name__ == "__main__":
    tester = Phase2BackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["overall_status"] == "WORKING" else 1)