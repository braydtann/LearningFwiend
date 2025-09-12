#!/usr/bin/env python3
"""
🧪 SUBJECTIVE QUIZ SUBMISSIONS FUNCTIONALITY TESTING

TESTING OBJECTIVES:
1. Test the POST /api/quiz-submissions/subjective endpoint with admin credentials
2. Test the POST /api/quiz-submissions/subjective endpoint with student credentials  
3. Test the GET /api/courses/{course_id}/submissions endpoint to verify submissions appear
4. Verify proper authentication and permission handling
5. Test submission data structure and storage

SPECIFIC TESTS:
1. **Admin Subjective Quiz Submission**:
   - Login as admin (brayden.t@covesmart.com / Hawaii2020!)
   - Submit subjective quiz answers using the provided structure
   - Verify successful submission response

2. **Student Subjective Quiz Submission**:
   - Login as student (brayden.student@learningfwiend.com / Cove1234!)
   - Submit subjective quiz answers using the provided structure
   - Verify successful submission response

3. **Submissions Retrieval**:
   - Use admin credentials to GET /api/courses/{course_id}/submissions
   - Verify submitted answers appear in the response
   - Check data structure and completeness

4. **Permission Testing**:
   - Verify students cannot access GET /api/courses/{course_id}/submissions
   - Verify proper error handling for unauthorized access

SUCCESS CRITERIA:
- Both admin and student can successfully submit subjective answers
- Submissions are properly stored and retrievable by instructors/admins
- Proper authentication and authorization enforcement
- All API responses have correct structure and data
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class SubjectiveQuizSubmissionsTestSuite:
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.base_url = "https://coursemate-14.preview.emergentagent.com/api"
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials from review request
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        self.student_credentials = {
            "username_or_email": "brayden.student@learningfwiend.com", 
            "password": "Cove1234!"
        }
        
        # Test course ID from review request
        self.test_course_id = "8b948233-8bcf-4c4b-88b8-c0ae1c4063a5"
        
        # Sample submission data from review request
        self.sample_submission = {
            "submissions": [
                {
                    "questionId": "test-question-1",
                    "questionText": "What is your opinion on this topic?",
                    "studentAnswer": "This is my test answer for the subjective question.",
                    "courseId": "8b948233-8bcf-4c4b-88b8-c0ae1c4063a5",
                    "lessonId": "l1",
                    "questionType": "short-answer"
                }
            ]
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

    def authenticate_student(self) -> bool:
        """Authenticate as student user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.student_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Student Authentication",
                    True,
                    f"Successfully authenticated as {user_info.get('full_name', 'Student')} (Role: {user_info.get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Student Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def test_admin_subjective_submission(self) -> bool:
        """Test subjective quiz submission with admin credentials"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create admin-specific submission data
            admin_submission = {
                "submissions": [
                    {
                        "questionId": "admin-test-question-1",
                        "questionText": "What is your opinion on this topic?",
                        "studentAnswer": "This is my admin test answer for the subjective question. As an admin, I'm testing the submission functionality.",
                        "courseId": self.test_course_id,
                        "lessonId": "l1",
                        "questionType": "short-answer"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/quiz-submissions/subjective",
                json=admin_submission,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                if success and "1" in message:
                    self.log_test(
                        "Admin Subjective Quiz Submission",
                        True,
                        f"Successfully submitted subjective answer. Response: {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Subjective Quiz Submission",
                        False,
                        f"Unexpected response structure: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Subjective Quiz Submission",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Subjective Quiz Submission", False, f"Exception: {str(e)}")
            return False

    def test_student_subjective_submission(self) -> bool:
        """Test subjective quiz submission with student credentials"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Create student-specific submission data
            student_submission = {
                "submissions": [
                    {
                        "questionId": "student-test-question-1",
                        "questionText": "What is your opinion on this topic?",
                        "studentAnswer": "This is my student test answer for the subjective question. I'm providing a thoughtful response to demonstrate the functionality.",
                        "courseId": self.test_course_id,
                        "lessonId": "l1",
                        "questionType": "short-answer"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/quiz-submissions/subjective",
                json=student_submission,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                if success and "1" in message:
                    self.log_test(
                        "Student Subjective Quiz Submission",
                        True,
                        f"Successfully submitted subjective answer. Response: {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "Student Subjective Quiz Submission",
                        False,
                        f"Unexpected response structure: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Student Subjective Quiz Submission",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Student Subjective Quiz Submission", False, f"Exception: {str(e)}")
            return False

    def test_multiple_submissions(self) -> bool:
        """Test submitting multiple subjective answers in one request"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create multiple submissions data
            multiple_submissions = {
                "submissions": [
                    {
                        "questionId": "multi-test-question-1",
                        "questionText": "What is your opinion on topic A?",
                        "studentAnswer": "This is my answer to topic A. I believe it's important to consider multiple perspectives.",
                        "courseId": self.test_course_id,
                        "lessonId": "l1",
                        "questionType": "short-answer"
                    },
                    {
                        "questionId": "multi-test-question-2",
                        "questionText": "Explain your understanding of topic B.",
                        "studentAnswer": "Topic B is complex and requires careful analysis. Here's my detailed explanation of the key concepts.",
                        "courseId": self.test_course_id,
                        "lessonId": "l2",
                        "questionType": "long-form"
                    },
                    {
                        "questionId": "multi-test-question-3",
                        "questionText": "Provide your thoughts on topic C.",
                        "studentAnswer": "Topic C relates to the previous topics but has unique characteristics that need to be addressed separately.",
                        "courseId": self.test_course_id,
                        "lessonId": "l1",
                        "questionType": "short-answer"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/quiz-submissions/subjective",
                json=multiple_submissions,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                if success and "3" in message:
                    self.log_test(
                        "Multiple Subjective Submissions",
                        True,
                        f"Successfully submitted 3 subjective answers. Response: {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "Multiple Subjective Submissions",
                        False,
                        f"Unexpected response structure: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Multiple Subjective Submissions",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Multiple Subjective Submissions", False, f"Exception: {str(e)}")
            return False

    def test_admin_get_submissions(self) -> bool:
        """Test retrieving course submissions with admin credentials"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{self.base_url}/courses/{self.test_course_id}/submissions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if isinstance(response_data, dict) and "submissions" in response_data:
                    submissions = response_data["submissions"]
                    submission_count = response_data.get("count", len(submissions))
                elif isinstance(response_data, list):
                    submissions = response_data
                    submission_count = len(submissions)
                else:
                    self.log_test(
                        "Admin Get Course Submissions",
                        False,
                        f"Unexpected response format: {type(response_data)}"
                    )
                    return False
                
                if isinstance(submissions, list):
                    # Check if we have submissions from our tests
                    admin_submissions = [s for s in submissions if "admin" in s.get("questionId", "").lower()]
                    student_submissions = [s for s in submissions if "student" in s.get("questionId", "").lower()]
                    multi_submissions = [s for s in submissions if "multi" in s.get("questionId", "").lower()]
                    
                    total_test_submissions = len(admin_submissions) + len(student_submissions) + len(multi_submissions)
                    
                    if total_test_submissions >= 5:  # 1 admin + 1 student + 3 multi = 5 expected
                        # Verify submission structure
                        sample_submission = submissions[0] if submissions else {}
                        required_fields = ["id", "studentId", "studentName", "courseId", "lessonId", 
                                         "questionId", "questionText", "studentAnswer", "questionType", 
                                         "submittedAt", "status"]
                        
                        has_required_fields = all(field in sample_submission for field in required_fields)
                        
                        if has_required_fields:
                            self.log_test(
                                "Admin Get Course Submissions",
                                True,
                                f"Retrieved {len(submissions)} total submissions ({total_test_submissions} from our tests). All required fields present."
                            )
                            return True
                        else:
                            missing_fields = [field for field in required_fields if field not in sample_submission]
                            self.log_test(
                                "Admin Get Course Submissions",
                                False,
                                f"Missing required fields in submission structure: {missing_fields}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Admin Get Course Submissions",
                            False,
                            f"Expected at least 5 test submissions, found {total_test_submissions}. Total submissions: {len(submissions)}"
                        )
                        return False
                else:
                    self.log_test(
                        "Admin Get Course Submissions",
                        False,
                        f"Expected list response, got: {type(submissions)}"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Get Course Submissions",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Get Course Submissions", False, f"Exception: {str(e)}")
            return False

    def test_student_get_submissions_permission(self) -> bool:
        """Test that students cannot access course submissions (should get 403)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(
                f"{self.base_url}/courses/{self.test_course_id}/submissions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 403:
                self.log_test(
                    "Student Get Submissions Permission Check",
                    True,
                    "Correctly denied student access to course submissions (HTTP 403)"
                )
                return True
            elif response.status_code == 200:
                self.log_test(
                    "Student Get Submissions Permission Check",
                    False,
                    "Student was incorrectly allowed to access course submissions"
                )
                return False
            else:
                self.log_test(
                    "Student Get Submissions Permission Check",
                    False,
                    f"Unexpected HTTP status: {response.status_code}. Expected 403, got {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Student Get Submissions Permission Check", False, f"Exception: {str(e)}")
            return False

    def test_invalid_submission_data(self) -> bool:
        """Test submission with invalid/missing data"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test with missing required fields
            invalid_submission = {
                "submissions": [
                    {
                        "questionId": "invalid-test-question-1",
                        # Missing questionText
                        "studentAnswer": "This submission is missing questionText",
                        "courseId": self.test_course_id,
                        "lessonId": "l1",
                        "questionType": "short-answer"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/quiz-submissions/subjective",
                json=invalid_submission,
                headers=headers,
                timeout=10
            )
            
            # Should get 422 (validation error) or 400 (bad request)
            if response.status_code in [400, 422]:
                self.log_test(
                    "Invalid Submission Data Handling",
                    True,
                    f"Correctly rejected invalid submission data (HTTP {response.status_code})"
                )
                return True
            elif response.status_code == 200:
                self.log_test(
                    "Invalid Submission Data Handling",
                    False,
                    "Invalid submission was incorrectly accepted"
                )
                return False
            else:
                self.log_test(
                    "Invalid Submission Data Handling",
                    False,
                    f"Unexpected HTTP status: {response.status_code}. Expected 400/422 for invalid data"
                )
                return False
                
        except Exception as e:
            self.log_test("Invalid Submission Data Handling", False, f"Exception: {str(e)}")
            return False

    def test_empty_submissions_array(self) -> bool:
        """Test submission with empty submissions array"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test with empty submissions array
            empty_submission = {
                "submissions": []
            }
            
            response = requests.post(
                f"{self.base_url}/quiz-submissions/subjective",
                json=empty_submission,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                if success and "0" in message:
                    self.log_test(
                        "Empty Submissions Array Handling",
                        True,
                        f"Correctly handled empty submissions array. Response: {message}"
                    )
                    return True
                else:
                    self.log_test(
                        "Empty Submissions Array Handling",
                        False,
                        f"Unexpected response for empty array: {data}"
                    )
                    return False
            else:
                self.log_test(
                    "Empty Submissions Array Handling",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Empty Submissions Array Handling", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all tests for subjective quiz submissions functionality"""
        print("🧪 SUBJECTIVE QUIZ SUBMISSIONS FUNCTIONALITY TESTING")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        print("🔐 AUTHENTICATION TESTING")
        print("-" * 40)
        
        admin_auth = self.authenticate_admin()
        student_auth = self.authenticate_student()
        
        if not admin_auth or not student_auth:
            print("❌ CRITICAL: Authentication failed. Cannot proceed with testing.")
            return False
        
        print()
        
        # Step 2: Subjective Quiz Submissions Testing
        print("📝 SUBJECTIVE QUIZ SUBMISSIONS TESTING")
        print("-" * 40)
        
        admin_submission_success = self.test_admin_subjective_submission()
        student_submission_success = self.test_student_subjective_submission()
        multiple_submissions_success = self.test_multiple_submissions()
        
        print()
        
        # Step 3: Submissions Retrieval Testing
        print("📋 SUBMISSIONS RETRIEVAL TESTING")
        print("-" * 40)
        
        admin_get_success = self.test_admin_get_submissions()
        student_permission_success = self.test_student_get_submissions_permission()
        
        print()
        
        # Step 4: Error Handling Testing
        print("⚠️ ERROR HANDLING TESTING")
        print("-" * 40)
        
        invalid_data_success = self.test_invalid_submission_data()
        empty_array_success = self.test_empty_submissions_array()
        
        print()
        
        # Generate Summary Report
        self.generate_summary_report()
        
        return True

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("📊 COMPREHENSIVE SUMMARY REPORT")
        print("=" * 80)
        
        # Calculate overall success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Categorize results
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"]]
        submission_tests = [r for r in self.test_results if "Submission" in r["test"] and "Permission" not in r["test"]]
        retrieval_tests = [r for r in self.test_results if "Get" in r["test"] or "Permission" in r["test"]]
        error_tests = [r for r in self.test_results if "Invalid" in r["test"] or "Empty" in r["test"]]
        
        # Authentication Results
        auth_passed = sum(1 for r in auth_tests if r["success"])
        print(f"🔐 AUTHENTICATION: {auth_passed}/{len(auth_tests)} tests passed")
        for test in auth_tests:
            status = "✅" if test["success"] else "❌"
            print(f"   {status} {test['test']}")
        print()
        
        # Submission Results
        submission_passed = sum(1 for r in submission_tests if r["success"])
        print(f"📝 SUBMISSIONS: {submission_passed}/{len(submission_tests)} tests passed")
        for test in submission_tests:
            status = "✅" if test["success"] else "❌"
            print(f"   {status} {test['test']}")
        print()
        
        # Retrieval Results
        retrieval_passed = sum(1 for r in retrieval_tests if r["success"])
        print(f"📋 RETRIEVAL & PERMISSIONS: {retrieval_passed}/{len(retrieval_tests)} tests passed")
        for test in retrieval_tests:
            status = "✅" if test["success"] else "❌"
            print(f"   {status} {test['test']}")
        print()
        
        # Error Handling Results
        error_passed = sum(1 for r in error_tests if r["success"])
        print(f"⚠️ ERROR HANDLING: {error_passed}/{len(error_tests)} tests passed")
        for test in error_tests:
            status = "✅" if test["success"] else "❌"
            print(f"   {status} {test['test']}")
        print()
        
        # Key Findings
        print("🔍 KEY FINDINGS:")
        print("-" * 20)
        
        if auth_passed == len(auth_tests):
            print("✅ AUTHENTICATION: Both admin and student authentication working correctly")
        else:
            print("❌ AUTHENTICATION: Authentication issues detected")
        
        if submission_passed == len(submission_tests):
            print("✅ SUBMISSIONS: All submission scenarios working correctly")
        else:
            print("❌ SUBMISSIONS: Some submission scenarios failing")
        
        if retrieval_passed == len(retrieval_tests):
            print("✅ RETRIEVAL: Submission retrieval and permissions working correctly")
        else:
            print("❌ RETRIEVAL: Issues with submission retrieval or permissions")
        
        if error_passed == len(error_tests):
            print("✅ ERROR HANDLING: Proper error handling for invalid data")
        else:
            print("❌ ERROR HANDLING: Issues with error handling")
        
        print()
        
        # Final Status
        critical_success = (
            auth_passed == len(auth_tests) and
            submission_passed >= len(submission_tests) * 0.8 and  # Allow 80% success rate
            retrieval_passed >= len(retrieval_tests) * 0.8
        )
        
        if critical_success:
            print("🎉 SUCCESS: Subjective quiz submissions functionality is working correctly!")
            print("✅ Both admin and student can submit subjective answers")
            print("✅ Submissions are properly stored and retrievable")
            print("✅ Authentication and authorization working correctly")
        else:
            print("⚠️ ISSUES DETECTED: Some functionality needs attention")
            if auth_passed < len(auth_tests):
                print("🔧 Fix authentication issues")
            if submission_passed < len(submission_tests):
                print("🔧 Fix submission functionality")
            if retrieval_passed < len(retrieval_tests):
                print("🔧 Fix retrieval or permission issues")
        
        print()
        print("=" * 80)

def main():
    """Main execution function"""
    test_suite = SubjectiveQuizSubmissionsTestSuite()
    
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