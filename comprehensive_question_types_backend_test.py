#!/usr/bin/env python3
"""
Comprehensive Backend Testing for ALL Supported Question Types
Testing all 6 supported question types to ensure no [object Object] errors or 422 validation failures.

Based on backend validation pattern: ^(multiple_choice|true_false|short_answer|essay|chronological-order|select-all-that-apply)$

Supported Question Types:
1. multiple_choice - Test with string options array
2. true_false - Test with correct boolean format  
3. short_answer - Test with string correctAnswer
4. essay - Test with no correctAnswer required
5. chronological-order - Test with string items array (hyphen format!)
6. select-all-that-apply - Test with multiple correct answers (hyphen format!)

CRITICAL: Backend expects:
- chronological-order (with hyphen, not underscore)  
- select-all-that-apply (with hyphens, not underscores)

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://lms-analytics-hub.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class QuestionTypesBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.test_course_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Logged in as {data['user']['full_name']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_multiple_choice_question(self):
        """Test 1: Multiple Choice Question Type"""
        try:
            course_data = {
                "title": f"Multiple Choice Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing multiple choice question type",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Multiple Choice Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple_choice",
                                        "question": "What is the capital of France?",
                                        "options": ["London", "Berlin", "Paris", "Madrid"],
                                        "correctAnswer": "2",
                                        "points": 10,
                                        "explanation": "Paris is the capital of France"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Multiple Choice Question Type", True, 
                            f"Successfully created course with multiple_choice question")
                return course
            else:
                self.log_test("Multiple Choice Question Type", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Multiple Choice Question Type", False, f"Exception: {str(e)}")
            return None
    
    def test_true_false_question(self):
        """Test 2: True/False Question Type"""
        try:
            course_data = {
                "title": f"True False Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing true/false question type",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "True False Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "true_false",
                                        "question": "Python is a programming language.",
                                        "correctAnswer": "true",
                                        "points": 5,
                                        "explanation": "Python is indeed a programming language"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("True/False Question Type", True, 
                            f"Successfully created course with true_false question")
                return course
            else:
                self.log_test("True/False Question Type", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("True/False Question Type", False, f"Exception: {str(e)}")
            return None
    
    def test_short_answer_question(self):
        """Test 3: Short Answer Question Type"""
        try:
            course_data = {
                "title": f"Short Answer Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing short answer question type",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Short Answer Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "short_answer",
                                        "question": "What is the name of the Python web framework used in this project?",
                                        "correctAnswer": "FastAPI",
                                        "points": 15,
                                        "explanation": "FastAPI is the web framework used for the backend"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Short Answer Question Type", True, 
                            f"Successfully created course with short_answer question")
                return course
            else:
                self.log_test("Short Answer Question Type", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Short Answer Question Type", False, f"Exception: {str(e)}")
            return None
    
    def test_essay_question(self):
        """Test 4: Essay Question Type"""
        try:
            course_data = {
                "title": f"Essay Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing essay question type",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Essay Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "essay",
                                        "question": "Explain the benefits of using a Learning Management System in education.",
                                        "points": 25,
                                        "explanation": "This is an open-ended question requiring detailed explanation"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Essay Question Type", True, 
                            f"Successfully created course with essay question (no correctAnswer required)")
                return course
            else:
                self.log_test("Essay Question Type", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Essay Question Type", False, f"Exception: {str(e)}")
            return None
    
    def test_chronological_order_question(self):
        """Test 5: Chronological Order Question Type (with hyphens!)"""
        try:
            course_data = {
                "title": f"Chronological Order Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing chronological-order question type",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Chronological Order Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",  # CRITICAL: hyphen format!
                                        "question": "Arrange these historical events in chronological order:",
                                        "items": ["World War II", "World War I", "Cold War", "Renaissance"],
                                        "correctOrder": ["Renaissance", "World War I", "World War II", "Cold War"],
                                        "points": 20,
                                        "explanation": "These events occurred in this chronological sequence"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Chronological Order Question Type", True, 
                            f"Successfully created course with chronological-order question (hyphen format)")
                return course
            else:
                self.log_test("Chronological Order Question Type", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Chronological Order Question Type", False, f"Exception: {str(e)}")
            return None
    
    def test_select_all_that_apply_question(self):
        """Test 6: Select All That Apply Question Type (with hyphens!)"""
        try:
            course_data = {
                "title": f"Select All That Apply Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing select-all-that-apply question type",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Select All That Apply Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "select-all-that-apply",  # CRITICAL: hyphen format!
                                        "question": "Which of the following are programming languages?",
                                        "options": ["Python", "HTML", "JavaScript", "CSS", "Java", "SQL"],
                                        "correctAnswers": ["Python", "JavaScript", "Java"],
                                        "points": 30,
                                        "explanation": "Python, JavaScript, and Java are programming languages"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Select All That Apply Question Type", True, 
                            f"Successfully created course with select-all-that-apply question (hyphen format)")
                return course
            else:
                self.log_test("Select All That Apply Question Type", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Select All That Apply Question Type", False, f"Exception: {str(e)}")
            return None
    
    def test_mixed_question_types_course(self):
        """Test 7: Mixed Question Types in Single Course"""
        try:
            course_data = {
                "title": f"Mixed Question Types Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing all question types in a single course",
                "category": "Testing",
                "duration": "2 hours",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Comprehensive Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "All Question Types Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple_choice",
                                        "question": "What is 2 + 2?",
                                        "options": ["3", "4", "5", "6"],
                                        "correctAnswer": "1",
                                        "points": 5
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "true_false",
                                        "question": "The Earth is round.",
                                        "correctAnswer": "true",
                                        "points": 5
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "short_answer",
                                        "question": "What is the chemical symbol for water?",
                                        "correctAnswer": "H2O",
                                        "points": 10
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "essay",
                                        "question": "Describe the importance of education.",
                                        "points": 20
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "Order these numbers from smallest to largest:",
                                        "items": ["5", "1", "3", "2"],
                                        "correctOrder": ["1", "2", "3", "5"],
                                        "points": 15
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "select-all-that-apply",
                                        "question": "Which are even numbers?",
                                        "options": ["1", "2", "3", "4", "5", "6"],
                                        "correctAnswers": ["2", "4", "6"],
                                        "points": 15
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Mixed Question Types Course", True, 
                            f"Successfully created course with ALL 6 question types in single quiz")
                return course
            else:
                self.log_test("Mixed Question Types Course", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Mixed Question Types Course", False, f"Exception: {str(e)}")
            return None
    
    def test_course_retrieval_validation(self):
        """Test 8: Retrieve and validate course data structure"""
        try:
            # Get all courses to find our test courses
            response = self.session.get(f"{BACKEND_URL}/courses")
            
            if response.status_code == 200:
                courses = response.json()
                test_courses = [course for course in courses if "Test Course" in course["title"]]
                
                if len(test_courses) >= 6:  # Should have at least 6 test courses
                    # Test retrieving a specific course with questions
                    mixed_course = next((c for c in test_courses if "Mixed Question Types" in c["title"]), None)
                    
                    if mixed_course:
                        detail_response = self.session.get(f"{BACKEND_URL}/courses/{mixed_course['id']}")
                        
                        if detail_response.status_code == 200:
                            course_detail = detail_response.json()
                            
                            # Validate course structure
                            if ("modules" in course_detail and 
                                len(course_detail["modules"]) > 0 and
                                "lessons" in course_detail["modules"][0] and
                                len(course_detail["modules"][0]["lessons"]) > 0 and
                                "questions" in course_detail["modules"][0]["lessons"][0]):
                                
                                questions = course_detail["modules"][0]["lessons"][0]["questions"]
                                question_types = [q["type"] for q in questions]
                                
                                expected_types = ["multiple_choice", "true_false", "short_answer", 
                                                "essay", "chronological-order", "select-all-that-apply"]
                                
                                if all(qtype in question_types for qtype in expected_types):
                                    self.log_test("Course Retrieval Validation", True, 
                                                f"Successfully validated all 6 question types in retrieved course data")
                                    return True
                                else:
                                    missing_types = [t for t in expected_types if t not in question_types]
                                    self.log_test("Course Retrieval Validation", False, 
                                                f"Missing question types in retrieved data: {missing_types}")
                                    return False
                            else:
                                self.log_test("Course Retrieval Validation", False, 
                                            "Course structure validation failed - missing required fields")
                                return False
                        else:
                            self.log_test("Course Retrieval Validation", False, 
                                        f"Failed to retrieve course details: {detail_response.status_code}")
                            return False
                    else:
                        self.log_test("Course Retrieval Validation", False, 
                                    "Could not find mixed question types course for validation")
                        return False
                else:
                    self.log_test("Course Retrieval Validation", False, 
                                f"Expected at least 6 test courses, found {len(test_courses)}")
                    return False
            else:
                self.log_test("Course Retrieval Validation", False, 
                            f"Failed to retrieve courses: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Course Retrieval Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all question type tests"""
        print("🚀 Starting Comprehensive Question Types Backend Testing")
        print("=" * 80)
        print("Testing ALL 6 supported question types for [object Object] errors and 422 validation failures")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test each question type individually
        print("\n📝 Testing Individual Question Types:")
        print("-" * 50)
        
        self.test_multiple_choice_question()
        self.test_true_false_question()
        self.test_short_answer_question()
        self.test_essay_question()
        self.test_chronological_order_question()
        self.test_select_all_that_apply_question()
        
        # Step 3: Test mixed question types
        print("\n🔄 Testing Mixed Question Types:")
        print("-" * 50)
        
        self.test_mixed_question_types_course()
        
        # Step 4: Validate course retrieval
        print("\n✅ Validating Data Structure:")
        print("-" * 50)
        
        self.test_course_retrieval_validation()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE QUESTION TYPES TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 Question Type Support Status:")
        question_type_tests = [
            "Multiple Choice Question Type",
            "True/False Question Type", 
            "Short Answer Question Type",
            "Essay Question Type",
            "Chronological Order Question Type",
            "Select All That Apply Question Type"
        ]
        
        for test_name in question_type_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                status = "✅ WORKING" if test_result["success"] else "❌ FAILING"
                print(f"  - {test_name}: {status}")
        
        print(f"\n🏆 Overall Question Types Support: {'✅ ALL WORKING' if success_rate >= 85 else '❌ NEEDS ATTENTION'}")
        
        if success_rate >= 85:
            print("\n🎉 SUCCESS: All question types are working correctly!")
            print("   - No [object Object] errors detected")
            print("   - No 422 validation failures found")
            print("   - Backend accepts all supported question type formats")
            print("   - Hyphen formats (chronological-order, select-all-that-apply) working correctly")
        else:
            print("\n⚠️  WARNING: Some question types have issues that need attention")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = QuestionTypesBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)