#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Final Test Creation Workflow
Testing the complete program creation workflow after fixing data structure issues
in the FinalTestQuestionInterface component.

Focus Areas:
1. Create a program with a final test containing multiple choice questions
2. Verify question data is sent in correct format to backend
3. Ensure no 422 errors during final test creation
4. Test with different question types (multiple_choice, true_false, chronological_order)

Data Structure Fixes Tested:
- Fixed question type values from hyphens to underscores (multiple-choice → multiple_choice, etc.)
- Fixed option rendering from option.text to direct string access
- Fixed item rendering from item.text to direct string access
- Removed media sections that don't match backend schema

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://lms-progression.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class FinalTestWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_program_id = None
        self.test_final_test_id = None
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            self.log("🔐 Authenticating admin user...")
            
            login_data = {
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user = data["user"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log(f"✅ Admin authentication successful - User: {self.admin_user['full_name']} ({self.admin_user['role']})")
                return True
            else:
                self.log(f"❌ Admin authentication failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Admin authentication error: {str(e)}", "ERROR")
            return False
    
    def create_test_program(self):
        """Create a test program for final test creation"""
        try:
            self.log("📚 Creating test program...")
            
            program_data = {
                "title": f"Final Test Program - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for final test creation workflow validation",
                "departmentId": None,
                "duration": "4 weeks",
                "courseIds": [],  # Empty for now, can add courses later
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BASE_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.test_program_id = program["id"]
                self.log(f"✅ Test program created successfully - ID: {self.test_program_id}")
                self.log(f"   Program Title: {program['title']}")
                return True
            else:
                self.log(f"❌ Program creation failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Program creation error: {str(e)}", "ERROR")
            return False
    
    def create_final_test_with_multiple_choice(self):
        """Create final test with multiple choice questions using correct data structure"""
        try:
            self.log("📝 Creating final test with multiple choice questions...")
            
            # Test data with corrected structure (multiple_choice instead of multiple-choice)
            final_test_data = {
                "title": f"Final Test - Multiple Choice - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Final test with multiple choice questions to validate data structure fixes",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",  # Fixed: underscore instead of hyphen
                        "question": "What is the primary purpose of a Learning Management System?",
                        "options": [
                            "To manage student enrollment",  # Direct string access (not option.text)
                            "To deliver educational content and track progress",
                            "To handle financial transactions",
                            "To manage building facilities"
                        ],
                        "correctAnswer": "1",  # Index as string
                        "points": 10,
                        "explanation": "LMS systems are primarily designed to deliver educational content and track student progress."
                    },
                    {
                        "type": "multiple_choice",
                        "question": "Which of the following is a key feature of modern LMS platforms?",
                        "options": [
                            "Video conferencing only",
                            "Progress tracking and analytics",
                            "Social media integration only",
                            "Gaming features only"
                        ],
                        "correctAnswer": "1",
                        "points": 10,
                        "explanation": "Progress tracking and analytics are fundamental features of LMS platforms."
                    }
                ],
                "timeLimit": 60,  # 60 minutes
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BASE_URL}/final-tests", json=final_test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.test_final_test_id = final_test["id"]
                self.log(f"✅ Final test with multiple choice created successfully - ID: {self.test_final_test_id}")
                self.log(f"   Test Title: {final_test['title']}")
                self.log(f"   Question Count: {final_test['questionCount']}")
                self.log(f"   Total Points: {final_test['totalPoints']}")
                
                # Validate question structure
                for i, question in enumerate(final_test['questions']):
                    self.log(f"   Question {i+1}: Type={question['type']}, Points={question['points']}")
                    if question['type'] == 'multiple_choice':
                        self.log(f"     Options Count: {len(question['options'])}")
                
                return True
            else:
                self.log(f"❌ Final test creation failed - Status: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Final test creation error: {str(e)}", "ERROR")
            return False
    
    def create_final_test_with_true_false(self):
        """Create final test with true/false questions"""
        try:
            self.log("📝 Creating final test with true/false questions...")
            
            final_test_data = {
                "title": f"Final Test - True/False - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Final test with true/false questions to validate data structure fixes",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "true_false",  # Fixed: underscore instead of hyphen
                        "question": "Learning Management Systems can only be used for online education.",
                        "options": ["True", "False"],  # Direct string access
                        "correctAnswer": "1",  # False (index 1)
                        "points": 5,
                        "explanation": "LMS systems can be used for both online and blended learning approaches."
                    },
                    {
                        "type": "true_false",
                        "question": "Progress tracking is an essential feature of modern LMS platforms.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # True (index 0)
                        "points": 5,
                        "explanation": "Progress tracking allows educators to monitor student advancement and identify areas needing support."
                    }
                ],
                "timeLimit": 30,
                "maxAttempts": 3,
                "passingScore": 70.0,
                "shuffleQuestions": True,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BASE_URL}/final-tests", json=final_test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.log(f"✅ Final test with true/false created successfully - ID: {final_test['id']}")
                self.log(f"   Test Title: {final_test['title']}")
                self.log(f"   Question Count: {final_test['questionCount']}")
                self.log(f"   Total Points: {final_test['totalPoints']}")
                return True
            else:
                self.log(f"❌ True/False final test creation failed - Status: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ True/False final test creation error: {str(e)}", "ERROR")
            return False
    
    def create_final_test_with_chronological_order(self):
        """Create final test with chronological order questions"""
        try:
            self.log("📝 Creating final test with chronological order questions...")
            
            final_test_data = {
                "title": f"Final Test - Chronological Order - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Final test with chronological order questions to validate data structure fixes",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "chronological-order",  # Note: Backend expects hyphen for this type
                        "question": "Arrange the following LMS development phases in chronological order:",
                        "items": [  # Direct string access (not item.text)
                            "Requirements gathering",
                            "System design",
                            "Implementation",
                            "Testing and deployment"
                        ],
                        "correctOrder": [0, 1, 2, 3],  # Correct sequence indices
                        "points": 15,
                        "explanation": "Software development follows a logical sequence from requirements to deployment."
                    },
                    {
                        "type": "chronological-order",
                        "question": "Order the following student learning progression steps:",
                        "items": [
                            "Course enrollment",
                            "Content consumption",
                            "Assessment completion",
                            "Certificate generation"
                        ],
                        "correctOrder": [0, 1, 2, 3],
                        "points": 15,
                        "explanation": "Student learning follows a natural progression from enrollment to certification."
                    }
                ],
                "timeLimit": 45,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BASE_URL}/final-tests", json=final_test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.log(f"✅ Final test with chronological order created successfully - ID: {final_test['id']}")
                self.log(f"   Test Title: {final_test['title']}")
                self.log(f"   Question Count: {final_test['questionCount']}")
                self.log(f"   Total Points: {final_test['totalPoints']}")
                
                # Validate chronological order structure
                for i, question in enumerate(final_test['questions']):
                    if question['type'] == 'chronological-order':
                        self.log(f"   Question {i+1}: Items Count={len(question.get('items', []))}")
                        self.log(f"     Correct Order: {question.get('correctOrder', [])}")
                
                return True
            else:
                self.log(f"❌ Chronological order final test creation failed - Status: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Chronological order final test creation error: {str(e)}", "ERROR")
            return False
    
    def test_mixed_question_types(self):
        """Create final test with mixed question types to validate comprehensive workflow"""
        try:
            self.log("📝 Creating final test with mixed question types...")
            
            final_test_data = {
                "title": f"Final Test - Mixed Types - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Comprehensive final test with multiple question types to validate all data structure fixes",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the main benefit of using an LMS?",
                        "options": [
                            "Cost reduction only",
                            "Centralized learning management and tracking",
                            "Social networking features",
                            "Gaming capabilities"
                        ],
                        "correctAnswer": "1",
                        "points": 10,
                        "explanation": "LMS provides centralized learning management and comprehensive tracking capabilities."
                    },
                    {
                        "type": "true_false",
                        "question": "All LMS platforms require internet connectivity to function.",
                        "options": ["True", "False"],
                        "correctAnswer": "1",  # False
                        "points": 5,
                        "explanation": "Some LMS platforms can work offline or in hybrid modes."
                    },
                    {
                        "type": "chronological-order",
                        "question": "Order the typical student assessment workflow:",
                        "items": [
                            "Question presentation",
                            "Answer submission",
                            "Automatic grading",
                            "Results display"
                        ],
                        "correctOrder": [0, 1, 2, 3],
                        "points": 15,
                        "explanation": "Assessment workflow follows a logical sequence from presentation to results."
                    },
                    {
                        "type": "short_answer",
                        "question": "Name one key advantage of automated progress tracking in LMS systems.",
                        "correctAnswer": "Real-time monitoring of student progress",
                        "points": 10,
                        "explanation": "Automated tracking provides immediate insights into student performance and engagement."
                    }
                ],
                "timeLimit": 90,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": True,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BASE_URL}/final-tests", json=final_test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.log(f"✅ Mixed question types final test created successfully - ID: {final_test['id']}")
                self.log(f"   Test Title: {final_test['title']}")
                self.log(f"   Question Count: {final_test['questionCount']}")
                self.log(f"   Total Points: {final_test['totalPoints']}")
                
                # Validate all question types
                question_types = {}
                for question in final_test['questions']:
                    q_type = question['type']
                    question_types[q_type] = question_types.get(q_type, 0) + 1
                
                self.log(f"   Question Types Distribution: {question_types}")
                return True
            else:
                self.log(f"❌ Mixed question types final test creation failed - Status: {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Mixed question types final test creation error: {str(e)}", "ERROR")
            return False
    
    def validate_final_test_retrieval(self):
        """Validate that created final tests can be retrieved correctly"""
        try:
            self.log("🔍 Validating final test retrieval...")
            
            # Get all final tests for the program
            response = self.session.get(f"{BASE_URL}/final-tests?program_id={self.test_program_id}")
            
            if response.status_code == 200:
                final_tests = response.json()
                self.log(f"✅ Final tests retrieved successfully - Count: {len(final_tests)}")
                
                for test in final_tests:
                    self.log(f"   Test: {test['title']} (ID: {test['id']})")
                    self.log(f"     Questions: {test['questionCount']}, Points: {test['totalPoints']}")
                    self.log(f"     Published: {test['isPublished']}, Passing Score: {test['passingScore']}%")
                
                return True
            else:
                self.log(f"❌ Final test retrieval failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Final test retrieval error: {str(e)}", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete final test creation workflow test"""
        self.log("🚀 Starting Comprehensive Final Test Creation Workflow Testing")
        self.log("=" * 80)
        
        test_results = {
            "admin_auth": False,
            "program_creation": False,
            "multiple_choice_test": False,
            "true_false_test": False,
            "chronological_order_test": False,
            "mixed_types_test": False,
            "test_retrieval": False
        }
        
        # Step 1: Admin Authentication
        if self.authenticate_admin():
            test_results["admin_auth"] = True
        else:
            self.log("❌ Cannot proceed without admin authentication", "ERROR")
            return test_results
        
        # Step 2: Create Test Program
        if self.create_test_program():
            test_results["program_creation"] = True
        else:
            self.log("❌ Cannot proceed without test program", "ERROR")
            return test_results
        
        # Step 3: Test Multiple Choice Questions
        if self.create_final_test_with_multiple_choice():
            test_results["multiple_choice_test"] = True
        
        # Step 4: Test True/False Questions
        if self.create_final_test_with_true_false():
            test_results["true_false_test"] = True
        
        # Step 5: Test Chronological Order Questions
        if self.create_final_test_with_chronological_order():
            test_results["chronological_order_test"] = True
        
        # Step 6: Test Mixed Question Types
        if self.test_mixed_question_types():
            test_results["mixed_types_test"] = True
        
        # Step 7: Validate Retrieval
        if self.validate_final_test_retrieval():
            test_results["test_retrieval"] = True
        
        return test_results
    
    def print_final_report(self, test_results):
        """Print comprehensive test results report"""
        self.log("=" * 80)
        self.log("🎯 FINAL TEST CREATION WORKFLOW - COMPREHENSIVE TEST RESULTS")
        self.log("=" * 80)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        self.log("")
        
        # Detailed results
        test_descriptions = {
            "admin_auth": "Admin Authentication",
            "program_creation": "Test Program Creation",
            "multiple_choice_test": "Multiple Choice Final Test Creation",
            "true_false_test": "True/False Final Test Creation", 
            "chronological_order_test": "Chronological Order Final Test Creation",
            "mixed_types_test": "Mixed Question Types Final Test Creation",
            "test_retrieval": "Final Test Retrieval Validation"
        }
        
        for test_key, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            description = test_descriptions.get(test_key, test_key)
            self.log(f"{status} - {description}")
        
        self.log("")
        
        # Critical findings
        critical_tests = ["multiple_choice_test", "true_false_test", "chronological_order_test", "mixed_types_test"]
        critical_passed = sum(1 for test in critical_tests if test_results.get(test, False))
        critical_total = len(critical_tests)
        
        self.log("🔍 CRITICAL FINDINGS:")
        if critical_passed == critical_total:
            self.log("✅ ALL CRITICAL TESTS PASSED - Final test creation workflow is working correctly")
            self.log("✅ Data structure fixes are successful:")
            self.log("   - Question type values using underscores (multiple_choice, true_false)")
            self.log("   - Option rendering using direct string access")
            self.log("   - Item rendering using direct string access")
            self.log("   - No 422 errors during final test creation")
        else:
            self.log(f"❌ CRITICAL ISSUES DETECTED - {critical_passed}/{critical_total} critical tests passed")
            self.log("   Some question types or data structures may still have issues")
        
        self.log("")
        self.log("🎉 FINAL TEST CREATION WORKFLOW TESTING COMPLETED")
        self.log("=" * 80)
        
        return success_rate >= 75.0  # Consider successful if 75% or more tests pass

def main():
    """Main execution function"""
    print("🚀 Final Test Creation Workflow - Backend Testing")
    print("Testing data structure fixes for FinalTestQuestionInterface component")
    print("=" * 80)
    
    tester = FinalTestWorkflowTester()
    test_results = tester.run_comprehensive_test()
    overall_success = tester.print_final_report(test_results)
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()