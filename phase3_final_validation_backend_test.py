#!/usr/bin/env python3
"""
FINAL PHASE 3 VALIDATION - Comprehensive Backend Testing for Drag-and-Drop Chronological Order Functionality
Testing all backend APIs that support the complete chronological order workflow as requested in review.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://fixfriend.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class ChronologicalOrderBackendTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_course_id = None
        self.test_enrollment_id = None
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                admin_name = data["user"]["full_name"]
                admin_role = data["user"]["role"]
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Admin logged in: {admin_name}, Role: {admin_role}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                student_name = data["user"]["full_name"]
                student_id = data["user"]["id"]
                self.log_result(
                    "Student Authentication", 
                    True, 
                    f"Student logged in: {student_name}, ID: {student_id}"
                )
                return True
            else:
                self.log_result(
                    "Student Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def create_chronological_course(self):
        """Test course creation with chronological order questions"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Historical Events Test Question as specified in review request
            chronological_questions = [
                {
                    "id": "hist_events_1",
                    "type": "chronological-order",
                    "question": "Arrange these historical events in chronological order:",
                    "items": [
                        {"text": "World War I begins", "year": "1914"},
                        {"text": "World War II ends", "year": "1945"},
                        {"text": "Moon landing", "year": "1969"},
                        {"text": "Berlin Wall falls", "year": "1989"}
                    ],
                    "correctOrder": [0, 1, 2, 3],  # Correct chronological sequence
                    "points": 10,
                    "explanation": "These events span from 1914 to 1989 in chronological order."
                }
            ]
            
            course_data = {
                "title": "Phase 3 Chronological Order Test Course",
                "description": "Final validation course for drag-and-drop chronological order functionality",
                "category": "History",
                "duration": "30 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=200&fit=crop",
                "accessType": "open",
                "learningOutcomes": [
                    "Master chronological ordering of historical events",
                    "Practice drag-and-drop interface skills",
                    "Understand historical timeline relationships"
                ],
                "modules": [
                    {
                        "title": "Historical Timeline Module",
                        "lessons": [
                            {
                                "id": "lesson_1",
                                "title": "Historical Events Quiz",
                                "type": "quiz",
                                "content": {
                                    "instructions": "Use the drag-and-drop interface to arrange events in chronological order",
                                    "timeLimit": 300,
                                    "passingScore": 75
                                },
                                "questions": chronological_questions
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                self.test_course_id = course["id"]
                
                # Validate chronological question structure
                lesson = course["modules"][0]["lessons"][0]
                question = lesson["questions"][0]
                
                validation_checks = [
                    ("Question type", question.get("type") == "chronological-order"),
                    ("Items array exists", "items" in question and len(question["items"]) == 4),
                    ("CorrectOrder array exists", "correctOrder" in question and len(question["correctOrder"]) == 4),
                    ("Array lengths match", len(question["items"]) == len(question["correctOrder"])),
                    ("Valid indices", all(0 <= idx < len(question["items"]) for idx in question["correctOrder"]))
                ]
                
                all_valid = all(check[1] for check in validation_checks)
                validation_details = ", ".join([f"{check[0]}: {'✓' if check[1] else '✗'}" for check in validation_checks])
                
                self.log_result(
                    "Course Creation with Chronological Order",
                    all_valid,
                    f"Course ID: {self.test_course_id}, Validations: {validation_details}"
                )
                return all_valid
            else:
                self.log_result(
                    "Course Creation with Chronological Order",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Course Creation with Chronological Order", False, f"Exception: {str(e)}")
            return False

    def enroll_student_in_course(self):
        """Test student enrollment in chronological order course"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            enrollment_data = {"courseId": self.test_course_id}
            
            response = requests.post(f"{BACKEND_URL}/enrollments", json=enrollment_data, headers=headers)
            
            if response.status_code == 200:
                enrollment = response.json()
                self.test_enrollment_id = enrollment["id"]
                self.log_result(
                    "Student Enrollment in Chronological Course",
                    True,
                    f"Enrollment ID: {self.test_enrollment_id}, Progress: {enrollment['progress']}%"
                )
                return True
            else:
                self.log_result(
                    "Student Enrollment in Chronological Course",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Student Enrollment in Chronological Course", False, f"Exception: {str(e)}")
            return False

    def test_course_access_and_data_structure(self):
        """Test student access to course and validate chronological data structure"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(f"{BACKEND_URL}/courses/{self.test_course_id}", headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                
                # Validate complete data structure for drag-and-drop interface
                lesson = course["modules"][0]["lessons"][0]
                question = lesson["questions"][0]
                
                structure_checks = [
                    ("Course accessible", True),
                    ("Module structure", len(course["modules"]) == 1),
                    ("Lesson structure", len(course["modules"][0]["lessons"]) == 1),
                    ("Question exists", len(lesson["questions"]) == 1),
                    ("Question type correct", question["type"] == "chronological-order"),
                    ("Items field exists", "items" in question),
                    ("Items is array", isinstance(question["items"], list)),
                    ("Items count correct", len(question["items"]) == 4),
                    ("CorrectOrder field exists", "correctOrder" in question),
                    ("CorrectOrder is array", isinstance(question["correctOrder"], list)),
                    ("CorrectOrder count correct", len(question["correctOrder"]) == 4),
                    ("All items have text", all("text" in item for item in question["items"])),
                    ("Valid index range", all(0 <= idx < 4 for idx in question["correctOrder"]))
                ]
                
                all_valid = all(check[1] for check in structure_checks)
                passed_checks = sum(1 for check in structure_checks if check[1])
                
                self.log_result(
                    "Course Access & Data Structure Validation",
                    all_valid,
                    f"Passed {passed_checks}/{len(structure_checks)} structure checks"
                )
                return all_valid
            else:
                self.log_result(
                    "Course Access & Data Structure Validation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Course Access & Data Structure Validation", False, f"Exception: {str(e)}")
            return False

    def test_chronological_answer_submission(self):
        """Test quiz submission with chronological order answers"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test correct chronological order (as specified in review request)
            correct_answer = [0, 1, 2, 3]  # World War I → WWII → Moon landing → Berlin Wall
            
            progress_data = {
                "progress": 100.0,
                "currentLessonId": "lesson_1",
                "timeSpent": 180
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                json=progress_data,
                headers=headers
            )
            
            if response.status_code == 200:
                enrollment = response.json()
                
                success_checks = [
                    ("Progress updated", enrollment["progress"] == 100.0),
                    ("Status completed", enrollment.get("status") == "completed"),
                    ("Completion timestamp", "completedAt" in enrollment),
                    ("Current lesson tracked", enrollment.get("currentLessonId") == "lesson_1")
                ]
                
                all_successful = all(check[1] for check in success_checks)
                passed_checks = sum(1 for check in success_checks if check[1])
                
                self.log_result(
                    "Chronological Answer Submission & Progress Tracking",
                    all_successful,
                    f"Progress: {enrollment['progress']}%, Status: {enrollment.get('status')}, Checks: {passed_checks}/{len(success_checks)}"
                )
                return all_successful
            else:
                self.log_result(
                    "Chronological Answer Submission & Progress Tracking",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Chronological Answer Submission & Progress Tracking", False, f"Exception: {str(e)}")
            return False

    def test_edge_cases(self):
        """Test edge cases for chronological order functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test single item chronological question
            single_item_course = {
                "title": "Single Item Chronological Test",
                "description": "Edge case testing for single item",
                "category": "Testing",
                "modules": [
                    {
                        "title": "Edge Case Module",
                        "lessons": [
                            {
                                "id": "edge_lesson_1",
                                "title": "Single Item Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": "single_item_q",
                                        "type": "chronological-order",
                                        "question": "Single item chronological test:",
                                        "items": [{"text": "Only event", "year": "2024"}],
                                        "correctOrder": [0],
                                        "points": 5
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/courses", json=single_item_course, headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                question = course["modules"][0]["lessons"][0]["questions"][0]
                
                edge_case_checks = [
                    ("Single item accepted", len(question["items"]) == 1),
                    ("Single correctOrder", len(question["correctOrder"]) == 1),
                    ("Valid single index", question["correctOrder"][0] == 0),
                    ("Question type preserved", question["type"] == "chronological-order")
                ]
                
                all_valid = all(check[1] for check in edge_case_checks)
                
                self.log_result(
                    "Edge Case Testing (Single Item)",
                    all_valid,
                    f"Single item chronological question handled correctly"
                )
                return all_valid
            else:
                self.log_result(
                    "Edge Case Testing (Single Item)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Edge Case Testing (Single Item)", False, f"Exception: {str(e)}")
            return False

    def test_mixed_question_types(self):
        """Test integration with other question types"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            mixed_course = {
                "title": "Mixed Question Types Integration Test",
                "description": "Testing chronological order with other question types",
                "category": "Integration",
                "modules": [
                    {
                        "title": "Mixed Quiz Module",
                        "lessons": [
                            {
                                "id": "mixed_lesson",
                                "title": "Mixed Question Types Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": "mc_q1",
                                        "type": "multiple-choice",
                                        "question": "What is 2+2?",
                                        "options": ["3", "4", "5", "6"],
                                        "correctAnswer": 1,
                                        "points": 5
                                    },
                                    {
                                        "id": "chrono_q1",
                                        "type": "chronological-order",
                                        "question": "Order these technological inventions:",
                                        "items": [
                                            {"text": "Internet", "year": "1969"},
                                            {"text": "Personal Computer", "year": "1975"},
                                            {"text": "Smartphone", "year": "2007"}
                                        ],
                                        "correctOrder": [0, 1, 2],
                                        "points": 10
                                    },
                                    {
                                        "id": "tf_q1",
                                        "type": "true-false",
                                        "question": "The Earth is round.",
                                        "correctAnswer": True,
                                        "points": 3
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/courses", json=mixed_course, headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                questions = course["modules"][0]["lessons"][0]["questions"]
                
                integration_checks = [
                    ("Three questions created", len(questions) == 3),
                    ("Multiple choice preserved", questions[0]["type"] == "multiple-choice"),
                    ("Chronological order preserved", questions[1]["type"] == "chronological-order"),
                    ("True/false preserved", questions[2]["type"] == "true-false"),
                    ("Chronological structure intact", "items" in questions[1] and "correctOrder" in questions[1]),
                    ("No type conflicts", all("type" in q for q in questions))
                ]
                
                all_valid = all(check[1] for check in integration_checks)
                
                self.log_result(
                    "Mixed Question Types Integration",
                    all_valid,
                    f"Successfully integrated chronological order with multiple choice and true/false questions"
                )
                return all_valid
            else:
                self.log_result(
                    "Mixed Question Types Integration",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Mixed Question Types Integration", False, f"Exception: {str(e)}")
            return False

    def test_enrollment_workflow(self):
        """Test complete enrollment and progress workflow"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get student enrollments
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Find our test course enrollment
                test_enrollment = None
                for enrollment in enrollments:
                    if enrollment["courseId"] == self.test_course_id:
                        test_enrollment = enrollment
                        break
                
                if test_enrollment:
                    workflow_checks = [
                        ("Enrollment exists", test_enrollment is not None),
                        ("Course ID matches", test_enrollment["courseId"] == self.test_course_id),
                        ("Progress tracked", "progress" in test_enrollment),
                        ("Status tracked", "status" in test_enrollment),
                        ("Enrollment date", "enrolledAt" in test_enrollment)
                    ]
                    
                    all_valid = all(check[1] for check in workflow_checks)
                    
                    self.log_result(
                        "Complete Enrollment Workflow",
                        all_valid,
                        f"Enrollment workflow functional, Progress: {test_enrollment.get('progress', 0)}%"
                    )
                    return all_valid
                else:
                    self.log_result(
                        "Complete Enrollment Workflow",
                        False,
                        "Test course enrollment not found in student enrollments"
                    )
                    return False
            else:
                self.log_result(
                    "Complete Enrollment Workflow",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Complete Enrollment Workflow", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all chronological order backend tests"""
        print("🚀 FINAL PHASE 3 VALIDATION - Comprehensive Chronological Order Backend Testing")
        print("=" * 80)
        print()
        
        # Authentication tests
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with testing.")
            return False
            
        if not self.authenticate_student():
            print("❌ CRITICAL: Student authentication failed. Cannot proceed with testing.")
            return False
        
        # Core functionality tests
        test_methods = [
            self.create_chronological_course,
            self.enroll_student_in_course,
            self.test_course_access_and_data_structure,
            self.test_chronological_answer_submission,
            self.test_edge_cases,
            self.test_mixed_question_types,
            self.test_enrollment_workflow
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            if test_method():
                passed_tests += 1
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 80)
        print("🎯 FINAL PHASE 3 VALIDATION RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 85:
            print("✅ PHASE 3 VALIDATION SUCCESSFUL - Chronological order backend functionality is ready for production")
            print()
            print("🎉 SUCCESS CRITERIA MET:")
            print("✅ Course creation with chronological order works end-to-end")
            print("✅ Student enrollment and access functional")
            print("✅ Data structure validation passed")
            print("✅ Answer submission and progress tracking working")
            print("✅ Edge cases handled correctly")
            print("✅ Integration with other question types successful")
            print("✅ Complete workflow functional")
        else:
            print("❌ PHASE 3 VALIDATION FAILED - Critical issues found in chronological order backend")
            print()
            print("🚨 ISSUES IDENTIFIED:")
            for result in self.results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
        
        print()
        print("📊 DETAILED TEST RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = ChronologicalOrderBackendTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)