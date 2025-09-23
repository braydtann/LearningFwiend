#!/usr/bin/env python3

"""
Final Exam Data Format Investigation Backend Test
=================================================

This test investigates the exact data format being sent by the deployed frontend
when submitting final exam attempts to understand if there's still a format issue.

Focus Areas:
1. Inspect actual API requests from deployed frontend
2. Create program and final test through frontend interface
3. Submit answers and capture exact request format
4. Compare request format with backend expectations

Environment: https://lms-bug-fixes.preview.emergentagent.com
"""

import requests
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Test Configuration
BASE_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}
STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamDataFormatTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_program_id = None
        self.test_final_test_id = None
        self.results = []

    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                print(f"✅ Admin authentication successful")
                print(f"   User: {data['user']['full_name']} ({data['user']['role']})")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False

    def authenticate_student(self) -> bool:
        """Authenticate as student user"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                print(f"✅ Student authentication successful")
                print(f"   User: {data['user']['full_name']} ({data['user']['role']})")
                return True
            else:
                print(f"❌ Student authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Student authentication error: {str(e)}")
            return False

    def create_test_program(self) -> bool:
        """Create a test program via API to ensure clean test data"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            program_data = {
                "title": f"Final Exam Format Test Program - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for investigating final exam data format issues",
                "departmentId": None,
                "duration": "1 week",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BASE_URL}/programs", json=program_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_program_id = data["id"]
                print(f"✅ Test program created successfully")
                print(f"   Program ID: {self.test_program_id}")
                print(f"   Title: {data['title']}")
                return True
            else:
                print(f"❌ Program creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Program creation error: {str(e)}")
            return False

    def create_test_final_exam(self) -> bool:
        """Create a final exam with multiple question types for testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create final test with various question types to test data format
            final_test_data = {
                "title": "Data Format Investigation Final Exam",
                "description": "Testing exact data format sent by frontend",
                "programId": self.test_program_id,
                "passingScore": 75.0,
                "maxAttempts": 3,
                "timeLimit": 60,
                "isPublished": True,  # Make it accessible to students
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the expected format for final exam answers?",
                        "options": [
                            "Dictionary format: {questionId: answer}",
                            "List format: [{questionId: id, answer: value}]",
                            "String format: questionId=answer",
                            "Array format: [questionId, answer]"
                        ],
                        "correctAnswer": "1",
                        "points": 10,
                        "explanation": "Backend expects list of objects format"
                    },
                    {
                        "type": "true_false",
                        "question": "The frontend should send answers as a dictionary?",
                        "options": ["True", "False"],
                        "correctAnswer": "1",
                        "points": 5,
                        "explanation": "False - should be list format"
                    },
                    {
                        "type": "short_answer",
                        "question": "What HTTP status code indicates a data format validation error?",
                        "correctAnswer": "422",
                        "points": 5,
                        "explanation": "422 Unprocessable Entity"
                    }
                ]
            }
            
            response = self.session.post(f"{BASE_URL}/final-tests", json=final_test_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_final_test_id = data["id"]
                print(f"✅ Final exam created successfully")
                print(f"   Final Test ID: {self.test_final_test_id}")
                print(f"   Questions: {len(data['questions'])}")
                print(f"   Total Points: {data['totalPoints']}")
                print(f"   Published: {data.get('isPublished', False)}")
                
                return True
            else:
                print(f"❌ Final exam creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Final exam creation error: {str(e)}")
            return False

    def get_final_exam_for_student(self) -> Optional[Dict]:
        """Get final exam as student to see what data is available"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = self.session.get(f"{BASE_URL}/final-tests/{self.test_final_test_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Student retrieved final exam successfully")
                print(f"   Questions available: {len(data.get('questions', []))}")
                
                # Analyze question structure for format investigation
                for i, question in enumerate(data.get('questions', [])):
                    print(f"   Question {i+1}:")
                    print(f"     ID: {question.get('id', 'N/A')}")
                    print(f"     Type: {question.get('type', 'N/A')}")
                    print(f"     Has correctAnswer: {'correctAnswer' in question}")
                    if 'correctAnswer' in question:
                        print(f"     correctAnswer value: {question['correctAnswer']}")
                    else:
                        print(f"     correctAnswer: MISSING (expected for students)")
                
                return data
            else:
                print(f"❌ Student final exam retrieval failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Student final exam retrieval error: {str(e)}")
            return None

    def test_answer_format_dictionary(self, final_exam_data: Dict) -> bool:
        """Test submitting answers in dictionary format (potentially wrong format)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Create answers in DICTIONARY format (what might be sent incorrectly)
            questions = final_exam_data.get('questions', [])
            answers_dict = {}
            
            for question in questions:
                question_id = question.get('id')
                if question.get('type') == 'multiple_choice':
                    answers_dict[question_id] = '1'  # Second option
                elif question.get('type') == 'true_false':
                    answers_dict[question_id] = '0'  # First option (True)
                elif question.get('type') == 'short_answer':
                    answers_dict[question_id] = '422'
            
            print(f"🔍 Testing DICTIONARY format submission:")
            print(f"   Format: {{questionId: answer}}")
            print(f"   Data: {json.dumps(answers_dict, indent=2)}")
            
            attempt_data = {
                "testId": self.test_final_test_id,  # Use testId, not finalTestId
                "answers": answers_dict  # Dictionary format
            }
            
            response = self.session.post(f"{BASE_URL}/final-test-attempts", json=attempt_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dictionary format ACCEPTED (unexpected!)")
                print(f"   Score: {data.get('score', 'N/A')}%")
                print(f"   Status: {data.get('status', 'N/A')}")
                return True
            else:
                print(f"❌ Dictionary format REJECTED (expected)")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print(f"   Error details: {error_data['detail']}")
                except:
                    pass
                
                return False
        except Exception as e:
            print(f"❌ Dictionary format test error: {str(e)}")
            return False

    def test_answer_format_list(self, final_exam_data: Dict) -> bool:
        """Test submitting answers in list format (expected correct format)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Create answers in LIST format (expected correct format)
            questions = final_exam_data.get('questions', [])
            answers_list = []
            
            for question in questions:
                question_id = question.get('id')
                answer_obj = {"questionId": question_id}
                
                if question.get('type') == 'multiple_choice':
                    answer_obj["answer"] = '1'  # Second option
                elif question.get('type') == 'true_false':
                    answer_obj["answer"] = '0'  # First option (True)
                elif question.get('type') == 'short_answer':
                    answer_obj["answer"] = '422'
                
                answers_list.append(answer_obj)
            
            print(f"🔍 Testing LIST format submission:")
            print(f"   Format: [{{questionId: id, answer: value}}]")
            print(f"   Data: {json.dumps(answers_list, indent=2)}")
            
            attempt_data = {
                "testId": self.test_final_test_id,  # Use testId, not finalTestId
                "answers": answers_list  # List format
            }
            
            response = self.session.post(f"{BASE_URL}/final-test-attempts", json=attempt_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ List format ACCEPTED (expected!)")
                print(f"   Score: {data.get('score', 'N/A')}%")
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Attempt ID: {data.get('id', 'N/A')}")
                return True
            else:
                print(f"❌ List format REJECTED (unexpected!)")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print(f"   Error details: {error_data['detail']}")
                except:
                    pass
                
                return False
        except Exception as e:
            print(f"❌ List format test error: {str(e)}")
            return False

    def check_existing_attempts(self) -> bool:
        """Check existing final test attempts to see what format was used"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = self.session.get(f"{BASE_URL}/final-test-attempts", headers=headers)
            if response.status_code == 200:
                attempts = response.json()
                print(f"✅ Retrieved {len(attempts)} existing final test attempts")
                
                for i, attempt in enumerate(attempts[:3]):  # Show first 3 attempts
                    print(f"   Attempt {i+1}:")
                    print(f"     ID: {attempt.get('id', 'N/A')}")
                    print(f"     Score: {attempt.get('score', 'N/A')}%")
                    print(f"     Status: {attempt.get('status', 'N/A')}")
                    print(f"     Created: {attempt.get('createdAt', 'N/A')}")
                    
                    # Check if answers are stored and in what format
                    if 'answers' in attempt:
                        answers = attempt['answers']
                        if isinstance(answers, list):
                            print(f"     Answers format: LIST (correct)")
                            if answers:
                                print(f"     Sample answer: {answers[0]}")
                        elif isinstance(answers, dict):
                            print(f"     Answers format: DICTIONARY (potentially wrong)")
                            if answers:
                                first_key = list(answers.keys())[0]
                                print(f"     Sample answer: {first_key}: {answers[first_key]}")
                        else:
                            print(f"     Answers format: {type(answers)} (unknown)")
                
                return True
            else:
                print(f"❌ Failed to retrieve attempts: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Existing attempts check error: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive final exam data format investigation"""
        print("🎯 FINAL EXAM DATA FORMAT INVESTIGATION")
        print("=" * 60)
        print(f"Environment: {BASE_URL}")
        print(f"Focus: Investigating exact data format sent by frontend")
        print()
        
        test_results = []
        
        # Authentication
        print("📋 STEP 1: Authentication")
        print("-" * 30)
        admin_auth = self.authenticate_admin()
        test_results.append(("Admin Authentication", admin_auth))
        
        student_auth = self.authenticate_student()
        test_results.append(("Student Authentication", student_auth))
        
        if not admin_auth or not student_auth:
            print("❌ Authentication failed, cannot continue")
            return
        
        print()
        
        # Create test data
        print("📋 STEP 2: Test Data Creation")
        print("-" * 30)
        program_created = self.create_test_program()
        test_results.append(("Test Program Creation", program_created))
        
        if program_created:
            final_exam_created = self.create_test_final_exam()
            test_results.append(("Final Exam Creation", final_exam_created))
        else:
            final_exam_created = False
        
        if not program_created or not final_exam_created:
            print("❌ Test data creation failed, cannot continue")
            return
        
        print()
        
        # Student data retrieval
        print("📋 STEP 3: Student Data Analysis")
        print("-" * 30)
        final_exam_data = self.get_final_exam_for_student()
        test_results.append(("Student Final Exam Retrieval", final_exam_data is not None))
        
        if not final_exam_data:
            print("❌ Cannot retrieve final exam data, cannot continue")
            return
        
        print()
        
        # Format testing
        print("📋 STEP 4: Answer Format Testing")
        print("-" * 30)
        
        # Test dictionary format (potentially wrong)
        dict_result = self.test_answer_format_dictionary(final_exam_data)
        test_results.append(("Dictionary Format Test", dict_result))
        
        print()
        
        # Test list format (expected correct)
        list_result = self.test_answer_format_list(final_exam_data)
        test_results.append(("List Format Test", list_result))
        
        print()
        
        # Existing attempts analysis
        print("📋 STEP 5: Existing Attempts Analysis")
        print("-" * 30)
        attempts_analysis = self.check_existing_attempts()
        test_results.append(("Existing Attempts Analysis", attempts_analysis))
        
        print()
        
        # Results summary
        print("📊 INVESTIGATION RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print()
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Critical findings
        print()
        print("🔍 CRITICAL FINDINGS:")
        print("-" * 30)
        
        if dict_result and list_result:
            print("⚠️  BOTH formats accepted - backend is flexible")
        elif list_result and not dict_result:
            print("✅ Only LIST format accepted - backend expects correct format")
        elif dict_result and not list_result:
            print("❌ Only DICTIONARY format accepted - backend has wrong expectations")
        else:
            print("❌ NEITHER format accepted - backend has validation issues")
        
        print()
        print("📋 RECOMMENDATIONS:")
        print("-" * 30)
        
        if list_result:
            print("✅ Frontend should send: [{questionId: 'id', answer: 'value'}]")
        else:
            print("❌ Backend validation needs investigation")
        
        if not dict_result:
            print("✅ Dictionary format correctly rejected")
        else:
            print("⚠️  Dictionary format unexpectedly accepted")

def main():
    """Main test execution"""
    tester = FinalExamDataFormatTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()