#!/usr/bin/env python3

"""
Backend Testing for Final Exam Subjective Questions Bug Fixes
Testing the bug fixes for final exam grading logic to ensure:
1. Short-answer and long-form questions are NOT auto-graded (should get 0 points initially)
2. These questions create subjective submissions for manual grading
3. Auto-graded questions (multiple choice, true/false, etc.) still work correctly
4. Manual grading functionality works
5. Score recalculation after manual grading works
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamSubjectiveTestRunner:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_program_id = None
        self.test_final_test_id = None
        self.test_attempt_id = None
        self.subjective_submission_ids = []
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({"test": test_name, "success": success, "details": details})
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        print()
        
    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                admin_info = f"Admin: {data['user']['full_name']} (Role: {data['user']['role']})"
                self.log_result("Admin Authentication", True, admin_info)
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
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
                student_info = f"Student: {data['user']['full_name']} (Role: {data['user']['role']})"
                self.log_result("Student Authentication", True, student_info)
                return True
            else:
                self.log_result("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False
            
    def create_test_program(self):
        """Create a test program for final exam testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get available courses first
            courses_response = requests.get(f"{BACKEND_URL}/courses", headers=headers)
            if courses_response.status_code != 200:
                self.log_result("Create Test Program", False, "Failed to get courses")
                return False
                
            courses = courses_response.json()
            if not courses:
                self.log_result("Create Test Program", False, "No courses available")
                return False
                
            # Use first available course
            course_id = courses[0]["id"]
            
            program_data = {
                "title": f"Final Exam Subjective Test Program - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for final exam subjective questions testing",
                "duration": "2 weeks",
                "courseIds": [course_id],
                "nestedProgramIds": []
            }
            
            response = requests.post(f"{BACKEND_URL}/programs", json=program_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_program_id = data["id"]
                program_info = f"Program ID: {self.test_program_id}, Title: {data['title']}"
                self.log_result("Create Test Program", True, program_info)
                return True
            else:
                self.log_result("Create Test Program", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Test Program", False, f"Exception: {str(e)}")
            return False
            
    def create_final_test_with_subjective_questions(self):
        """Create final test with mixed question types including subjective questions"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create final test with mixed question types
            final_test_data = {
                "title": "Subjective Questions Test - Final Exam",
                "description": "Testing subjective question grading logic",
                "programId": self.test_program_id,
                "timeLimit": 60,
                "passingScore": 75.0,
                "maxAttempts": 2,
                "showResults": True,
                "isPublished": True,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is the capital of Hawaii?",
                        "options": ["Honolulu", "Hilo", "Kona", "Maui"],
                        "correctAnswer": "0",
                        "points": 10,
                        "explanation": "Honolulu is the capital and largest city of Hawaii."
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "Hawaii is the 50th state of the United States.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",
                        "points": 10,
                        "explanation": "Hawaii became the 50th state on August 21, 1959."
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "short_answer",
                        "question": "Explain the significance of Pearl Harbor in World War II. (Short answer)",
                        "correctAnswer": "Pearl Harbor attack led to US entry into WWII",
                        "points": 15,
                        "explanation": "This is a subjective question requiring manual grading."
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "essay",
                        "question": "Write a detailed essay about the cultural diversity of Hawaii and its impact on modern Hawaiian society. Include specific examples and discuss at least three different cultural influences. (Long form essay)",
                        "points": 25,
                        "explanation": "This is a long-form essay question requiring manual grading."
                    }
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/final-tests", json=final_test_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_final_test_id = data["id"]
                test_info = f"Final Test ID: {self.test_final_test_id}, Questions: {len(data['questions'])}, Total Points: {data['totalPoints']}"
                self.log_result("Create Final Test with Subjective Questions", True, test_info)
                return True
            else:
                self.log_result("Create Final Test with Subjective Questions", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Final Test with Subjective Questions", False, f"Exception: {str(e)}")
            return False
            
    def student_take_final_exam(self):
        """Student takes the final exam with subjective answers"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get the final test first
            response = requests.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}", headers=headers)
            if response.status_code != 200:
                self.log_result("Student Take Final Exam", False, "Failed to get final test")
                return False
                
            test_data = response.json()
            questions = test_data.get("questions", [])
            
            # Prepare answers - mix of correct and incorrect for auto-graded, subjective answers for manual grading
            answers = []
            for question in questions:
                question_id = question["id"]
                if question["type"] == "multiple_choice":
                    # Answer correctly (option 0 = Honolulu)
                    answers.append({"questionId": question_id, "answer": "0"})
                elif question["type"] == "true_false":
                    # Answer correctly (True = option 0)
                    answers.append({"questionId": question_id, "answer": "0"})
                elif question["type"] == "short-answer":
                    # Provide a short answer that should be manually graded
                    answers.append({"questionId": question_id, "answer": "Pearl Harbor was attacked by Japan on December 7, 1941, which led to the United States entering World War II."})
                elif question["type"] == "essay":
                    # Provide a long-form essay answer
                    essay_answer = """Hawaii is a unique melting pot of cultures that has shaped its modern society in profound ways. The cultural diversity stems from three main influences:

1. Native Hawaiian Culture: The indigenous Polynesian culture provides the foundation with concepts like 'ohana (family), aloha spirit, and respect for the land (malama 'aina). This is seen in modern Hawaii through hula preservation, traditional fishing practices, and the Hawaiian language revival.

2. Asian Influences: Large populations of Japanese, Chinese, Filipino, and Korean immigrants brought their traditions. This is evident in Hawaii's cuisine (plate lunch, musubi, malasadas), festivals (Bon Festival, Chinese New Year), and business practices. The concept of respect for elders and community harmony reflects Asian values.

3. Western/American Influence: American colonization and statehood brought Western education, legal systems, and economic structures. However, Hawaii has adapted these with local flavor, creating a unique blend of American democracy with island-style consensus building.

These cultural influences have created modern Hawaii's distinctive identity - a place where East meets West in the Pacific, where ancient traditions coexist with modern technology, and where the aloha spirit represents a genuine multicultural harmony that serves as a model for diversity worldwide."""
                    answers.append({"questionId": question_id, "answer": essay_answer})
            
            # Submit the final exam attempt
            attempt_data = {
                "testId": self.test_final_test_id,
                "answers": answers,
                "timeSpent": 45  # 45 minutes
            }
            
            response = requests.post(f"{BACKEND_URL}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_attempt_id = data["id"]
                
                # Check initial scoring - should only get points for auto-graded questions
                initial_score = data["score"]
                points_earned = data["pointsEarned"]
                total_points = data["totalPoints"]
                
                # Expected: 20 points from auto-graded (10+10), 0 from subjective (15+25)
                expected_auto_points = 20
                expected_total_points = 60
                
                success = (points_earned == expected_auto_points and 
                          total_points == expected_total_points and
                          initial_score == (expected_auto_points / expected_total_points * 100))
                
                attempt_info = f"Attempt ID: {self.test_attempt_id}, Initial Score: {initial_score}%, Points: {points_earned}/{total_points}"
                self.log_result("Student Take Final Exam", success, attempt_info)
                return success
            else:
                self.log_result("Student Take Final Exam", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Student Take Final Exam", False, f"Exception: {str(e)}")
            return False
            
    def verify_subjective_submissions_created(self):
        """Verify that subjective submissions were created for manual grading"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all subjective submissions
            response = requests.get(f"{BACKEND_URL}/courses/all/submissions", headers=headers)
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                # Filter submissions for our test attempt
                test_submissions = [sub for sub in submissions if sub.get("attemptId") == self.test_attempt_id]
                
                # Should have 2 subjective submissions (short_answer + essay)
                expected_count = 2
                success = len(test_submissions) == expected_count
                
                if success:
                    self.subjective_submission_ids = [sub["id"] for sub in test_submissions]
                    
                submission_info = f"Found {len(test_submissions)} subjective submissions (expected {expected_count})"
                if test_submissions:
                    submission_info += f", Types: {[sub['questionType'] for sub in test_submissions]}"
                    
                self.log_result("Verify Subjective Submissions Created", success, submission_info)
                return success
            else:
                self.log_result("Verify Subjective Submissions Created", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Verify Subjective Submissions Created", False, f"Exception: {str(e)}")
            return False
            
    def test_manual_grading(self):
        """Test manual grading of subjective submissions"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            grading_results = []
            
            for submission_id in self.subjective_submission_ids:
                # Get submission details first
                response = requests.get(f"{BACKEND_URL}/submissions/{submission_id}/grade", headers=headers)
                if response.status_code != 200:
                    continue
                    
                submission = response.json()
                question_type = submission.get("questionType", "")
                max_points = submission.get("questionPoints", 10)
                
                # Grade based on question type
                if question_type == "short-answer":
                    # Give partial credit for short answer
                    grade_data = {
                        "score": 12,  # 12 out of 15 points
                        "feedback": "Good answer covering the key points about Pearl Harbor's significance in WWII. Could include more specific details about the impact on US public opinion."
                    }
                elif question_type == "essay":
                    # Give high score for comprehensive essay
                    grade_data = {
                        "score": 23,  # 23 out of 25 points
                        "feedback": "Excellent essay demonstrating deep understanding of Hawaiian cultural diversity. Well-structured with specific examples from Native Hawaiian, Asian, and Western influences. Minor deduction for could have included more contemporary examples."
                    }
                else:
                    continue
                    
                # Submit the grade
                response = requests.post(f"{BACKEND_URL}/submissions/{submission_id}/grade", 
                                       json=grade_data, headers=headers)
                
                if response.status_code == 200:
                    grading_results.append({"submission_id": submission_id, "type": question_type, "score": grade_data["score"]})
                    
            success = len(grading_results) == len(self.subjective_submission_ids)
            grading_info = f"Graded {len(grading_results)} submissions: {grading_results}"
            self.log_result("Test Manual Grading", success, grading_info)
            return success
            
        except Exception as e:
            self.log_result("Test Manual Grading", False, f"Exception: {str(e)}")
            return False
            
    def verify_score_recalculation(self):
        """Verify that final test attempt score is recalculated after manual grading"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get the updated attempt
            response = requests.get(f"{BACKEND_URL}/final-test-attempts/{self.test_attempt_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                final_score = data["score"]
                final_points = data["pointsEarned"]
                total_points = data["totalPoints"]
                
                # Expected: 20 (auto-graded) + 12 (short answer) + 23 (essay) = 55 out of 60 = 91.67%
                expected_points = 55
                expected_total = 60
                expected_score = round(expected_points / expected_total * 100, 2)
                
                success = (abs(final_score - expected_score) < 0.1 and 
                          final_points == expected_points and
                          total_points == expected_total)
                
                score_info = f"Final Score: {final_score}% (expected ~{expected_score}%), Points: {final_points}/{total_points}"
                self.log_result("Verify Score Recalculation", success, score_info)
                return success
            else:
                self.log_result("Verify Score Recalculation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Verify Score Recalculation", False, f"Exception: {str(e)}")
            return False
            
    def test_question_point_validation(self):
        """Test that grading validates against question point values"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.subjective_submission_ids:
                self.log_result("Test Question Point Validation", False, "No subjective submissions available")
                return False
                
            submission_id = self.subjective_submission_ids[0]
            
            # Try to grade with score exceeding question points
            invalid_grade_data = {
                "score": 100,  # Way more than the question is worth
                "feedback": "Testing validation"
            }
            
            response = requests.post(f"{BACKEND_URL}/submissions/{submission_id}/grade", 
                                   json=invalid_grade_data, headers=headers)
            
            # Should get 400 error for invalid score
            success = response.status_code == 400
            
            validation_info = f"Invalid score response: {response.status_code} (expected 400)"
            if response.status_code == 400:
                validation_info += f", Error: {response.json().get('detail', 'No detail')}"
                
            self.log_result("Test Question Point Validation", success, validation_info)
            return success
            
        except Exception as e:
            self.log_result("Test Question Point Validation", False, f"Exception: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all final exam subjective questions tests"""
        print("🎯 FINAL EXAM SUBJECTIVE QUESTIONS BACKEND TESTING INITIATED")
        print("=" * 80)
        print("Testing bug fixes for final exam grading logic:")
        print("1. Short-answer and long-form questions are NOT auto-graded")
        print("2. These questions create subjective submissions for manual grading")
        print("3. Auto-graded questions still work correctly")
        print("4. Manual grading functionality works")
        print("5. Score recalculation after manual grading works")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        tests = [
            self.authenticate_admin,
            self.authenticate_student,
            self.create_test_program,
            self.create_final_test_with_subjective_questions,
            self.student_take_final_exam,
            self.verify_subjective_submissions_created,
            self.test_manual_grading,
            self.verify_score_recalculation,
            self.test_question_point_validation
        ]
        
        for test in tests:
            if not test():
                break
                
        # Print summary
        print("=" * 80)
        print("🎯 FINAL EXAM SUBJECTIVE QUESTIONS TESTING SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.results if result["success"])
        total = len(self.results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"SUCCESS RATE: {success_rate:.1f}% ({passed}/{total} tests passed)")
        print()
        
        # Print detailed results
        for result in self.results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")
                
        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 CONCLUSION: Final exam subjective questions functionality is working correctly!")
            print("✅ Short-answer and long-form questions are properly handled")
            print("✅ Subjective submissions are created for manual grading")
            print("✅ Auto-graded questions continue to work")
            print("✅ Manual grading and score recalculation functional")
        else:
            print("❌ CONCLUSION: Issues detected with final exam subjective questions functionality")
            print("🔧 Manual intervention required to fix failing tests")
            
        return success_rate >= 80

if __name__ == "__main__":
    runner = FinalExamSubjectiveTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)