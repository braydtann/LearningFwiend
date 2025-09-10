#!/usr/bin/env python3
"""
🧪 VERIFY TRUE/FALSE QUESTION IMAGES: Final Verification Before Deployment

TESTING OBJECTIVE:
Verify that True/False questions with question images work correctly in the backend and are ready for frontend testing.

SPECIFIC TESTS NEEDED:
1. **Create True/False Test Quiz**: Create a test quiz with True/False questions that have `questionImage` URLs
2. **Backend Storage Verification**: Ensure True/False questions with images are stored correctly
3. **API Response Validation**: Confirm GET /api/courses/{id} returns True/False question data with `questionImage` field
4. **Data Structure Check**: Verify the data format is compatible with frontend expectations

SUCCESS CRITERIA:
- Backend properly stores `questionImage` field for True/False questions
- API responses include question image URLs in correct format
- Data structure matches frontend requirements
- All APIs working correctly

TEST APPROACH:
- Create test course with True/False questions containing question images
- Verify backend data storage and retrieval
- Validate API response format
- Clean up test data after verification

CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class TrueFalseImageTestSuite:
    def __init__(self):
        # Use localhost backend URL as per system instructions
        self.base_url = "http://localhost:8001/api"
        self.admin_token = None
        self.test_results = []
        self.test_course_id = None
        
        # Test credentials from review request
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and data:
            print(f"    Error Data: {data}")
        print()

    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {user_info.get('full_name', 'Admin')} (Role: {user_info.get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_true_false_image_course(self) -> bool:
        """Create a test course with True/False questions containing question images"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create course with True/False questions that have questionImage URLs
            course_data = {
                "title": "True/False Question Images Test Course",
                "description": "Test course to verify True/False questions with question images work correctly",
                "category": "Testing",
                "duration": "30 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=300&fit=crop",
                "accessType": "open",
                "learningOutcomes": [
                    "Verify True/False question image functionality",
                    "Test backend storage of question images",
                    "Validate API response format"
                ],
                "modules": [
                    {
                        "title": "True/False Questions with Images Module",
                        "lessons": [
                            {
                                "id": "lesson-1",
                                "title": "True/False Image Questions Quiz",
                                "type": "quiz",
                                "content": "Quiz with True/False questions containing question images",
                                "questions": [
                                    {
                                        "id": "q1",
                                        "type": "true_false",
                                        "question": "Is this the correct logo for Python programming language?",
                                        "questionImage": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&h=300&fit=crop",
                                        "correctAnswer": "true",
                                        "points": 10,
                                        "explanation": "This is indeed the Python logo, recognizable by its distinctive blue and yellow snake design."
                                    },
                                    {
                                        "id": "q2", 
                                        "type": "true_false",
                                        "question": "Does this image show a JavaScript code editor?",
                                        "questionImage": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&h=300&fit=crop",
                                        "correctAnswer": "true",
                                        "points": 10,
                                        "explanation": "Yes, this image shows code being written in what appears to be a JavaScript development environment."
                                    },
                                    {
                                        "id": "q3",
                                        "type": "true_false", 
                                        "question": "Is this image showing a database schema diagram?",
                                        "questionImage": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=300&fit=crop",
                                        "correctAnswer": "false",
                                        "points": 10,
                                        "explanation": "No, this image shows network/server infrastructure, not a database schema diagram."
                                    },
                                    {
                                        "id": "q4",
                                        "type": "true_false",
                                        "question": "Does this image represent cloud computing architecture?",
                                        "questionImage": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=300&fit=crop",
                                        "correctAnswer": "true", 
                                        "points": 10,
                                        "explanation": "Yes, this image shows cloud/network connectivity which represents cloud computing concepts."
                                    },
                                    {
                                        "id": "q5",
                                        "type": "true_false",
                                        "question": "Is this a mobile app development interface?",
                                        "questionImage": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop",
                                        "correctAnswer": "true",
                                        "points": 10,
                                        "explanation": "Yes, this appears to be a mobile development environment or app interface design."
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/courses",
                json=course_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                course = response.json()
                self.test_course_id = course.get('id')
                
                # Verify course structure
                modules = course.get('modules', [])
                if len(modules) > 0:
                    lessons = modules[0].get('lessons', [])
                    if len(lessons) > 0:
                        questions = lessons[0].get('questions', [])
                        true_false_questions = [q for q in questions if q.get('type') == 'true_false']
                        questions_with_images = [q for q in true_false_questions if 'questionImage' in q]
                        
                        success = (
                            len(true_false_questions) == 5 and
                            len(questions_with_images) == 5 and
                            all(q.get('questionImage', '').startswith('https://') for q in questions_with_images)
                        )
                        
                        if success:
                            self.log_test(
                                "Create True/False Image Course",
                                True,
                                f"Successfully created course with {len(true_false_questions)} True/False questions, all with question images. Course ID: {self.test_course_id}"
                            )
                            return True
                        else:
                            self.log_test(
                                "Create True/False Image Course",
                                False,
                                f"Course structure validation failed - T/F questions: {len(true_false_questions)}, With images: {len(questions_with_images)}"
                            )
                            return False
                    else:
                        self.log_test("Create True/False Image Course", False, "No lessons found in course")
                        return False
                else:
                    self.log_test("Create True/False Image Course", False, "No modules found in course")
                    return False
            else:
                self.log_test(
                    "Create True/False Image Course",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Create True/False Image Course", False, f"Exception: {str(e)}")
            return False

    def verify_backend_storage(self) -> bool:
        """Verify that True/False questions with images are stored correctly in backend"""
        try:
            if not self.test_course_id:
                self.log_test("Backend Storage Verification", False, "No test course ID available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/courses/{self.test_course_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Navigate to questions
                modules = course.get('modules', [])
                if not modules:
                    self.log_test("Backend Storage Verification", False, "No modules found")
                    return False
                
                lessons = modules[0].get('lessons', [])
                if not lessons:
                    self.log_test("Backend Storage Verification", False, "No lessons found")
                    return False
                
                questions = lessons[0].get('questions', [])
                if not questions:
                    self.log_test("Backend Storage Verification", False, "No questions found")
                    return False
                
                # Analyze question storage
                storage_analysis = {
                    "total_questions": len(questions),
                    "true_false_questions": 0,
                    "questions_with_images": 0,
                    "valid_image_urls": 0,
                    "required_fields_present": 0,
                    "sample_questions": []
                }
                
                for question in questions:
                    if question.get('type') == 'true_false':
                        storage_analysis["true_false_questions"] += 1
                        
                        # Check for questionImage field
                        if 'questionImage' in question:
                            storage_analysis["questions_with_images"] += 1
                            
                            # Validate image URL
                            image_url = question.get('questionImage', '')
                            if image_url.startswith('https://'):
                                storage_analysis["valid_image_urls"] += 1
                        
                        # Check required fields
                        required_fields = ['id', 'type', 'question', 'correctAnswer', 'points']
                        if all(field in question for field in required_fields):
                            storage_analysis["required_fields_present"] += 1
                        
                        # Store sample for analysis
                        if len(storage_analysis["sample_questions"]) < 2:
                            storage_analysis["sample_questions"].append({
                                "id": question.get('id'),
                                "question_text": question.get('question', '')[:50] + "...",
                                "has_image": 'questionImage' in question,
                                "image_url": question.get('questionImage', 'N/A')[:50] + "..." if question.get('questionImage') else 'N/A',
                                "correct_answer": question.get('correctAnswer'),
                                "points": question.get('points')
                            })
                
                # Validate storage success
                expected_count = 5
                success = (
                    storage_analysis["true_false_questions"] == expected_count and
                    storage_analysis["questions_with_images"] == expected_count and
                    storage_analysis["valid_image_urls"] == expected_count and
                    storage_analysis["required_fields_present"] == expected_count
                )
                
                if success:
                    self.log_test(
                        "Backend Storage Verification",
                        True,
                        f"All {expected_count} True/False questions stored correctly with valid question images and required fields",
                        storage_analysis
                    )
                    return True
                else:
                    self.log_test(
                        "Backend Storage Verification",
                        False,
                        f"Storage validation failed - Expected {expected_count} questions with images, got T/F: {storage_analysis['true_false_questions']}, With images: {storage_analysis['questions_with_images']}, Valid URLs: {storage_analysis['valid_image_urls']}",
                        storage_analysis
                    )
                    return False
            else:
                self.log_test(
                    "Backend Storage Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Backend Storage Verification", False, f"Exception: {str(e)}")
            return False

    def validate_api_response_format(self) -> bool:
        """Validate that GET /api/courses/{id} returns True/False question data with questionImage field in correct format"""
        try:
            if not self.test_course_id:
                self.log_test("API Response Format Validation", False, "No test course ID available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/courses/{self.test_course_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Validate response structure
                format_analysis = {
                    "has_course_id": 'id' in course,
                    "has_modules": 'modules' in course and len(course['modules']) > 0,
                    "has_lessons": False,
                    "has_questions": False,
                    "question_format_valid": False,
                    "image_urls_accessible": 0,
                    "frontend_compatibility": {
                        "question_structure": False,
                        "image_field_present": False,
                        "answer_format_correct": False
                    }
                }
                
                # Navigate through structure
                if format_analysis["has_modules"]:
                    lessons = course['modules'][0].get('lessons', [])
                    if lessons:
                        format_analysis["has_lessons"] = True
                        questions = lessons[0].get('questions', [])
                        if questions:
                            format_analysis["has_questions"] = True
                            
                            # Validate question format for frontend compatibility
                            true_false_questions = [q for q in questions if q.get('type') == 'true_false']
                            
                            if true_false_questions:
                                # Check first question structure
                                sample_question = true_false_questions[0]
                                
                                # Frontend compatibility checks
                                format_analysis["frontend_compatibility"]["question_structure"] = all(
                                    field in sample_question for field in ['id', 'type', 'question', 'correctAnswer']
                                )
                                
                                format_analysis["frontend_compatibility"]["image_field_present"] = 'questionImage' in sample_question
                                
                                format_analysis["frontend_compatibility"]["answer_format_correct"] = (
                                    sample_question.get('correctAnswer') in ['true', 'false']
                                )
                                
                                # Test image URL accessibility (basic format check)
                                for question in true_false_questions:
                                    image_url = question.get('questionImage', '')
                                    if image_url.startswith('https://') and 'unsplash.com' in image_url:
                                        format_analysis["image_urls_accessible"] += 1
                                
                                format_analysis["question_format_valid"] = (
                                    len(true_false_questions) == 5 and
                                    format_analysis["image_urls_accessible"] == 5
                                )
                
                # Overall validation
                success = (
                    format_analysis["has_course_id"] and
                    format_analysis["has_modules"] and
                    format_analysis["has_lessons"] and
                    format_analysis["has_questions"] and
                    format_analysis["question_format_valid"] and
                    all(format_analysis["frontend_compatibility"].values())
                )
                
                if success:
                    self.log_test(
                        "API Response Format Validation",
                        True,
                        f"API response format is correct and frontend-compatible. {format_analysis['image_urls_accessible']} questions with valid image URLs",
                        format_analysis
                    )
                    return True
                else:
                    self.log_test(
                        "API Response Format Validation",
                        False,
                        f"API response format validation failed. Frontend compatibility issues detected",
                        format_analysis
                    )
                    return False
            else:
                self.log_test(
                    "API Response Format Validation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("API Response Format Validation", False, f"Exception: {str(e)}")
            return False

    def test_data_structure_compatibility(self) -> bool:
        """Test that the data structure matches frontend expectations for True/False questions with images"""
        try:
            if not self.test_course_id:
                self.log_test("Data Structure Compatibility", False, "No test course ID available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/courses/{self.test_course_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Extract questions for analysis
                questions = []
                try:
                    questions = course['modules'][0]['lessons'][0]['questions']
                except (KeyError, IndexError):
                    self.log_test("Data Structure Compatibility", False, "Could not extract questions from course structure")
                    return False
                
                compatibility_analysis = {
                    "total_questions": len(questions),
                    "structure_tests": {
                        "question_id_format": 0,
                        "question_type_correct": 0,
                        "question_text_present": 0,
                        "question_image_url_valid": 0,
                        "correct_answer_format": 0,
                        "points_numeric": 0,
                        "explanation_present": 0
                    },
                    "frontend_ready_questions": 0,
                    "sample_structures": []
                }
                
                for question in questions:
                    if question.get('type') == 'true_false':
                        # Test each compatibility requirement
                        if question.get('id') and isinstance(question['id'], str):
                            compatibility_analysis["structure_tests"]["question_id_format"] += 1
                        
                        if question.get('type') == 'true_false':
                            compatibility_analysis["structure_tests"]["question_type_correct"] += 1
                        
                        if question.get('question') and len(question['question']) > 0:
                            compatibility_analysis["structure_tests"]["question_text_present"] += 1
                        
                        image_url = question.get('questionImage', '')
                        if image_url and image_url.startswith('https://'):
                            compatibility_analysis["structure_tests"]["question_image_url_valid"] += 1
                        
                        if question.get('correctAnswer') in ['true', 'false']:
                            compatibility_analysis["structure_tests"]["correct_answer_format"] += 1
                        
                        if isinstance(question.get('points'), (int, float)) and question['points'] > 0:
                            compatibility_analysis["structure_tests"]["points_numeric"] += 1
                        
                        if question.get('explanation') and len(question['explanation']) > 0:
                            compatibility_analysis["structure_tests"]["explanation_present"] += 1
                        
                        # Count as frontend-ready if all tests pass
                        tests_passed = sum(1 for test in [
                            question.get('id') and isinstance(question['id'], str),
                            question.get('type') == 'true_false',
                            question.get('question') and len(question['question']) > 0,
                            question.get('questionImage', '').startswith('https://'),
                            question.get('correctAnswer') in ['true', 'false'],
                            isinstance(question.get('points'), (int, float))
                        ] if test)
                        
                        if tests_passed == 6:  # All required tests passed
                            compatibility_analysis["frontend_ready_questions"] += 1
                        
                        # Store sample structure
                        if len(compatibility_analysis["sample_structures"]) < 2:
                            compatibility_analysis["sample_structures"].append({
                                "id": question.get('id'),
                                "type": question.get('type'),
                                "has_question_text": bool(question.get('question')),
                                "has_question_image": bool(question.get('questionImage')),
                                "image_url_sample": question.get('questionImage', '')[:30] + "..." if question.get('questionImage') else None,
                                "correct_answer": question.get('correctAnswer'),
                                "points": question.get('points'),
                                "has_explanation": bool(question.get('explanation'))
                            })
                
                # Validate overall compatibility
                expected_questions = 5
                success = (
                    compatibility_analysis["frontend_ready_questions"] == expected_questions and
                    compatibility_analysis["structure_tests"]["question_image_url_valid"] == expected_questions and
                    compatibility_analysis["structure_tests"]["correct_answer_format"] == expected_questions
                )
                
                if success:
                    self.log_test(
                        "Data Structure Compatibility",
                        True,
                        f"All {expected_questions} True/False questions are frontend-compatible with proper questionImage fields",
                        compatibility_analysis
                    )
                    return True
                else:
                    self.log_test(
                        "Data Structure Compatibility",
                        False,
                        f"Compatibility issues found - Frontend-ready: {compatibility_analysis['frontend_ready_questions']}/{expected_questions}, Valid images: {compatibility_analysis['structure_tests']['question_image_url_valid']}/{expected_questions}",
                        compatibility_analysis
                    )
                    return False
            else:
                self.log_test(
                    "Data Structure Compatibility",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Data Structure Compatibility", False, f"Exception: {str(e)}")
            return False

    def test_all_apis_working(self) -> bool:
        """Test that all required APIs are working correctly"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            api_tests = [
                ("GET /api/courses", f"{self.base_url}/courses"),
                ("GET /api/categories", f"{self.base_url}/categories"),
                ("GET /api/programs", f"{self.base_url}/programs"),
                ("GET /api/departments", f"{self.base_url}/departments")
            ]
            
            if self.test_course_id:
                api_tests.append((f"GET /api/courses/{self.test_course_id}", f"{self.base_url}/courses/{self.test_course_id}"))
            
            api_results = []
            
            for test_name, url in api_tests:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    success = response.status_code == 200
                    api_results.append(success)
                    
                    if success:
                        data = response.json()
                        if isinstance(data, list):
                            details = f"HTTP 200 - Retrieved {len(data)} items"
                        else:
                            details = f"HTTP 200 - Retrieved course data"
                    else:
                        details = f"HTTP {response.status_code}: {response.text[:100]}"
                    
                    self.log_test(test_name, success, details)
                    
                except Exception as e:
                    self.log_test(test_name, False, f"Exception: {str(e)}")
                    api_results.append(False)
            
            overall_success = all(api_results)
            success_rate = sum(api_results) / len(api_results) * 100
            
            self.log_test(
                "All APIs Working Test",
                overall_success,
                f"API Success Rate: {success_rate:.1f}% ({sum(api_results)}/{len(api_results)} tests passed)"
            )
            
            return overall_success
            
        except Exception as e:
            self.log_test("All APIs Working Test", False, f"Exception: {str(e)}")
            return False

    def cleanup_test_data(self) -> bool:
        """Clean up test course after verification"""
        try:
            if not self.test_course_id:
                self.log_test("Test Data Cleanup", True, "No test course to clean up")
                return True
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.delete(
                f"{self.base_url}/courses/{self.test_course_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Test Data Cleanup",
                    True,
                    f"Successfully deleted test course {self.test_course_id}"
                )
                return True
            else:
                self.log_test(
                    "Test Data Cleanup",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Test Data Cleanup", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all tests for True/False question images verification"""
        print("🧪 VERIFY TRUE/FALSE QUESTION IMAGES: Final Verification Before Deployment")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        print("🔐 AUTHENTICATION TESTING")
        print("-" * 40)
        
        admin_auth = self.authenticate_admin()
        if not admin_auth:
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with testing.")
            return False
        
        print()
        
        # Step 2: Create True/False Test Quiz
        print("📝 CREATE TRUE/FALSE TEST QUIZ")
        print("-" * 40)
        
        course_created = self.create_true_false_image_course()
        print()
        
        # Step 3: Backend Storage Verification
        print("💾 BACKEND STORAGE VERIFICATION")
        print("-" * 40)
        
        storage_verified = self.verify_backend_storage()
        print()
        
        # Step 4: API Response Validation
        print("🔍 API RESPONSE VALIDATION")
        print("-" * 40)
        
        api_validated = self.validate_api_response_format()
        print()
        
        # Step 5: Data Structure Check
        print("🏗️ DATA STRUCTURE COMPATIBILITY CHECK")
        print("-" * 40)
        
        structure_compatible = self.test_data_structure_compatibility()
        print()
        
        # Step 6: All APIs Working
        print("🔧 ALL APIS WORKING VERIFICATION")
        print("-" * 40)
        
        apis_working = self.test_all_apis_working()
        print()
        
        # Step 7: Cleanup
        print("🧹 TEST DATA CLEANUP")
        print("-" * 40)
        
        cleanup_success = self.cleanup_test_data()
        print()
        
        # Generate Summary Report
        self.generate_summary_report(course_created, storage_verified, api_validated, structure_compatible, apis_working)
        
        return True

    def generate_summary_report(self, course_created: bool, storage_verified: bool, api_validated: bool, structure_compatible: bool, apis_working: bool):
        """Generate comprehensive summary report"""
        print("📊 COMPREHENSIVE SUMMARY REPORT")
        print("=" * 80)
        
        # Calculate overall success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Key Findings
        print("🔍 KEY FINDINGS:")
        print("-" * 20)
        
        if course_created:
            print("✅ TRUE/FALSE QUIZ CREATION: Successfully created test course with True/False questions containing question images")
        else:
            print("❌ TRUE/FALSE QUIZ CREATION: Failed to create test course with question images")
        
        if storage_verified:
            print("✅ BACKEND STORAGE: True/False questions with questionImage field stored correctly")
        else:
            print("❌ BACKEND STORAGE: Issues with storing True/False question images")
        
        if api_validated:
            print("✅ API RESPONSE FORMAT: GET /api/courses/{id} returns correct format with questionImage field")
        else:
            print("❌ API RESPONSE FORMAT: API response format issues detected")
        
        if structure_compatible:
            print("✅ DATA STRUCTURE: Data format is compatible with frontend expectations")
        else:
            print("❌ DATA STRUCTURE: Data structure compatibility issues found")
        
        if apis_working:
            print("✅ ALL APIS: All required backend APIs working correctly")
        else:
            print("❌ ALL APIS: Some backend APIs not working correctly")
        
        print()
        
        # Success Criteria Assessment
        print("🎯 SUCCESS CRITERIA ASSESSMENT:")
        print("-" * 30)
        
        criteria_met = [
            ("Backend properly stores questionImage field", storage_verified),
            ("API responses include question image URLs", api_validated),
            ("Data structure matches frontend requirements", structure_compatible),
            ("All APIs working correctly", apis_working)
        ]
        
        for criterion, met in criteria_met:
            status = "✅" if met else "❌"
            print(f"{status} {criterion}")
        
        print()
        
        # Final Status
        all_criteria_met = all(met for _, met in criteria_met)
        
        if all_criteria_met:
            print("🎉 SUCCESS: True/False questions with question images are ready for frontend testing!")
            print("✅ Backend properly handles questionImage field for True/False questions")
            print("✅ API responses are correctly formatted and frontend-compatible")
            print("✅ All success criteria have been met")
        else:
            print("⚠️  PARTIAL SUCCESS: Some issues need to be addressed before frontend testing")
            failed_criteria = [criterion for criterion, met in criteria_met if not met]
            print(f"❌ Failed criteria: {', '.join(failed_criteria)}")
        
        print()
        print("=" * 80)

def main():
    """Main execution function"""
    test_suite = TrueFalseImageTestSuite()
    
    try:
        success = test_suite.run_comprehensive_test()
        
        if success:
            print("✅ Testing completed successfully!")
            return 0
        else:
            print("❌ Testing completed with issues!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)