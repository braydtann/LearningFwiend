#!/usr/bin/env python3
"""
URGENT: Quiz Scoring Investigation Backend Test
Testing the specific issue where users created tests YESTERDAY but get 0% scores despite correct answers.

Critical Investigation Areas:
1. Real User Test Replication - Find tests created in last 24-48 hours
2. Frontend vs Backend Data Flow - Check question ID generation and format
3. Actual Submission Debug - Test exact workflow user followed
4. Question ID Mismatch Investigation - Most likely root cause

Environment: https://lms-progression.preview.emergentagent.com
Admin: brayden.t@covesmart.com / Hawaii2020!
Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import uuid

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class QuizScoringInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.recent_programs = []
        self.recent_courses = []
        
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
    
    def authenticate_student(self):
        """Authenticate as student user"""
        try:
            # Create new session for student
            student_session = requests.Session()
            response = student_session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_session = student_session
                self.student_session.headers.update({
                    "Authorization": f"Bearer {self.student_token}"
                })
                self.log_test("Student Authentication", True, f"Logged in as {data['user']['full_name']}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def find_recent_programs_with_tests(self):
        """Find programs created in the last 48 hours that have final tests"""
        try:
            # Get all programs
            response = self.session.get(f"{BACKEND_URL}/programs")
            
            if response.status_code != 200:
                self.log_test("Find Recent Programs", False, f"Failed to get programs: {response.status_code}")
                return []
            
            programs = response.json()
            
            # Filter programs created in last 48 hours
            cutoff_time = datetime.now() - timedelta(hours=48)
            recent_programs = []
            
            for program in programs:
                created_at = datetime.fromisoformat(program['created_at'].replace('Z', '+00:00'))
                if created_at.replace(tzinfo=None) > cutoff_time:
                    recent_programs.append(program)
            
            self.log_test("Find Recent Programs", True, f"Found {len(recent_programs)} programs created in last 48 hours")
            
            # Now check which ones have final tests
            programs_with_tests = []
            for program in recent_programs:
                try:
                    test_response = self.session.get(f"{BACKEND_URL}/final-tests", params={
                        "program_id": program["id"]
                    })
                    
                    if test_response.status_code == 200:
                        tests = test_response.json()
                        if tests:
                            program['final_tests'] = tests
                            programs_with_tests.append(program)
                            print(f"    Program '{program['title']}' has {len(tests)} final test(s)")
                except:
                    continue
            
            self.recent_programs = programs_with_tests
            self.log_test("Find Programs with Tests", True, f"Found {len(programs_with_tests)} recent programs with final tests")
            return programs_with_tests
            
        except Exception as e:
            self.log_test("Find Recent Programs", False, f"Exception: {str(e)}")
            return []
    
    def find_recent_courses_with_quizzes(self):
        """Find courses created in the last 48 hours that have quiz lessons"""
        try:
            # Get all courses
            response = self.session.get(f"{BACKEND_URL}/courses")
            
            if response.status_code != 200:
                self.log_test("Find Recent Courses", False, f"Failed to get courses: {response.status_code}")
                return []
            
            courses = response.json()
            
            # Filter courses created in last 48 hours
            cutoff_time = datetime.now() - timedelta(hours=48)
            recent_courses = []
            
            for course in courses:
                created_at = datetime.fromisoformat(course['created_at'].replace('Z', '+00:00'))
                if created_at.replace(tzinfo=None) > cutoff_time:
                    recent_courses.append(course)
            
            self.log_test("Find Recent Courses", True, f"Found {len(recent_courses)} courses created in last 48 hours")
            
            # Check which ones have quiz lessons
            courses_with_quizzes = []
            for course in recent_courses:
                has_quiz = False
                for module in course.get('modules', []):
                    for lesson in module.get('lessons', []):
                        if lesson.get('type') == 'quiz':
                            has_quiz = True
                            break
                    if has_quiz:
                        break
                
                if has_quiz:
                    courses_with_quizzes.append(course)
                    print(f"    Course '{course['title']}' has quiz lessons")
            
            self.recent_courses = courses_with_quizzes
            self.log_test("Find Courses with Quizzes", True, f"Found {len(courses_with_quizzes)} recent courses with quizzes")
            return courses_with_quizzes
            
        except Exception as e:
            self.log_test("Find Recent Courses", False, f"Exception: {str(e)}")
            return []
    
    def analyze_question_data_structure(self, test_data):
        """Analyze the data structure of questions in a test"""
        try:
            questions = test_data.get('questions', [])
            analysis = {
                'total_questions': len(questions),
                'question_types': {},
                'id_formats': [],
                'missing_fields': [],
                'data_issues': []
            }
            
            for i, question in enumerate(questions):
                # Track question types
                q_type = question.get('type', 'unknown')
                analysis['question_types'][q_type] = analysis['question_types'].get(q_type, 0) + 1
                
                # Check question ID format
                q_id = question.get('id')
                if q_id:
                    analysis['id_formats'].append(type(q_id).__name__)
                else:
                    analysis['missing_fields'].append(f"Question {i+1} missing 'id' field")
                
                # Check for required fields based on question type
                if q_type == 'multiple_choice':
                    if 'options' not in question:
                        analysis['data_issues'].append(f"Multiple choice question {i+1} missing 'options'")
                    if 'correctAnswer' not in question:
                        analysis['data_issues'].append(f"Multiple choice question {i+1} missing 'correctAnswer'")
                    else:
                        # Check correctAnswer format
                        correct_answer = question['correctAnswer']
                        analysis['data_issues'].append(f"Q{i+1} correctAnswer type: {type(correct_answer).__name__}, value: {correct_answer}")
                
                elif q_type == 'select_all_that_apply':
                    if 'correctAnswers' not in question:
                        analysis['data_issues'].append(f"Select all question {i+1} missing 'correctAnswers'")
                
                elif q_type == 'chronological_order':
                    if 'items' not in question:
                        analysis['data_issues'].append(f"Chronological question {i+1} missing 'items'")
                    if 'correctOrder' not in question:
                        analysis['data_issues'].append(f"Chronological question {i+1} missing 'correctOrder'")
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def test_question_id_generation_mismatch(self):
        """Test if there's a mismatch between frontend question ID generation and backend expectations"""
        try:
            # Create a test program with questions using different ID formats
            program_data = {
                "title": f"ID Mismatch Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing question ID format compatibility",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            if program_response.status_code != 200:
                self.log_test("Question ID Mismatch Test - Program Creation", False, f"Failed: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Test 1: String-based question IDs (like frontend might generate)
            test_data_string_ids = {
                "title": "String ID Test",
                "description": "Testing with string-based question IDs",
                "programId": program_id,
                "questions": [
                    {
                        "id": "q1",  # String ID
                        "type": "multiple_choice",
                        "question": "What is 2 + 2?",
                        "options": ["2", "3", "4", "5"],
                        "correctAnswer": "2",  # String format
                        "points": 10
                    },
                    {
                        "id": "q2",  # String ID
                        "type": "true_false",
                        "question": "The sky is blue.",
                        "correctAnswer": "true",  # String format
                        "points": 5
                    }
                ],
                "timeLimit": 60,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data_string_ids)
            
            if test_response.status_code == 200:
                test_created = test_response.json()
                test_id = test_created["id"]
                
                # Analyze the created test structure
                analysis = self.analyze_question_data_structure(test_created)
                
                self.log_test("Question ID Mismatch Test - String IDs", True, 
                            f"Created test with string IDs. Analysis: {json.dumps(analysis, indent=2)}")
                
                # Now test submission with the same ID format
                return self.test_quiz_submission_with_different_id_formats(test_id, test_created)
            else:
                self.log_test("Question ID Mismatch Test - String IDs", False, 
                            f"Failed to create test: {test_response.status_code}, {test_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Question ID Mismatch Test", False, f"Exception: {str(e)}")
            return False
    
    def test_quiz_submission_with_different_id_formats(self, test_id, test_data):
        """Test quiz submission using different question ID formats"""
        try:
            if not hasattr(self, 'student_session'):
                self.log_test("Quiz Submission Test", False, "Student not authenticated")
                return False
            
            questions = test_data.get('questions', [])
            
            # Test 1: Submit answers using string question IDs (matching creation format)
            answers_string_format = {}
            for question in questions:
                q_id = question.get('id')
                if question.get('type') == 'multiple_choice':
                    answers_string_format[str(q_id)] = "2"  # Correct answer
                elif question.get('type') == 'true_false':
                    answers_string_format[str(q_id)] = "true"  # Correct answer
            
            submission_data = {
                "testId": test_id,
                "answers": answers_string_format,
                "timeSpent": 120
            }
            
            print(f"    Submitting answers with string format: {answers_string_format}")
            
            submission_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
            
            if submission_response.status_code == 200:
                result = submission_response.json()
                score = result.get('score', 0)
                passed = result.get('passed', False)
                
                self.log_test("Quiz Submission - String ID Format", True, 
                            f"Score: {score}%, Passed: {passed}, Expected: 100%")
                
                if score == 0:
                    self.log_test("CRITICAL ISSUE DETECTED", False, 
                                f"0% score despite correct answers! This matches user's reported issue.")
                    
                    # Detailed analysis of the scoring issue
                    print("    🔍 DETAILED SCORING ANALYSIS:")
                    print(f"    - Questions in test: {len(questions)}")
                    print(f"    - Answers submitted: {len(answers_string_format)}")
                    print(f"    - Answer format: {answers_string_format}")
                    print(f"    - Result details: {json.dumps(result, indent=6)}")
                    
                    return False
                else:
                    return True
            else:
                self.log_test("Quiz Submission - String ID Format", False, 
                            f"Submission failed: {submission_response.status_code}, {submission_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Quiz Submission Test", False, f"Exception: {str(e)}")
            return False
    
    def create_realistic_test_scenario(self):
        """Create a realistic test scenario mimicking user's workflow"""
        try:
            # Step 1: Create a program (like user did)
            program_data = {
                "title": f"Math Fundamentals Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "A comprehensive program covering basic mathematics concepts with final exam",
                "departmentId": None,
                "duration": "4 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            if program_response.status_code != 200:
                self.log_test("Realistic Scenario - Program Creation", False, f"Failed: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Step 2: Create final exam with 4 questions (like user did)
            final_exam_data = {
                "title": "Math Fundamentals Final Exam",
                "description": "Final examination covering all topics in the Math Fundamentals program",
                "programId": program_id,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is the result of 15 + 27?",
                        "options": ["40", "41", "42", "43"],
                        "correctAnswer": "2",  # Index 2 = "42"
                        "points": 25,
                        "explanation": "15 + 27 = 42"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice", 
                        "question": "Which of the following is a prime number?",
                        "options": ["15", "21", "17", "25"],
                        "correctAnswer": "2",  # Index 2 = "17"
                        "points": 25,
                        "explanation": "17 is a prime number as it's only divisible by 1 and itself"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "The square root of 64 is 8.",
                        "correctAnswer": "true",
                        "points": 25,
                        "explanation": "8 × 8 = 64, so √64 = 8"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",
                        "question": "What is 12 × 8?",
                        "options": ["84", "92", "96", "104"],
                        "correctAnswer": "2",  # Index 2 = "96"
                        "points": 25,
                        "explanation": "12 × 8 = 96"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 3,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=final_exam_data)
            
            if test_response.status_code != 200:
                self.log_test("Realistic Scenario - Final Exam Creation", False, 
                            f"Failed: {test_response.status_code}, {test_response.text}")
                return False
            
            created_test = test_response.json()
            test_id = created_test["id"]
            
            self.log_test("Realistic Scenario - Final Exam Creation", True, 
                        f"Created exam with 4 questions, total points: {created_test.get('totalPoints', 0)}")
            
            # Step 3: Student takes the exam with correct answers
            if not hasattr(self, 'student_session'):
                self.log_test("Realistic Scenario", False, "Student not authenticated")
                return False
            
            # Prepare correct answers
            correct_answers = {}
            questions = created_test.get('questions', [])
            
            for question in questions:
                q_id = question.get('id')
                if question.get('type') == 'multiple_choice':
                    correct_answers[str(q_id)] = question.get('correctAnswer')
                elif question.get('type') == 'true_false':
                    correct_answers[str(q_id)] = question.get('correctAnswer')
            
            submission_data = {
                "testId": test_id,
                "answers": correct_answers,
                "timeSpent": 1800  # 30 minutes
            }
            
            print(f"    📝 Student submitting exam with correct answers:")
            for q_id, answer in correct_answers.items():
                print(f"      Question {q_id[:8]}...: {answer}")
            
            submission_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
            
            if submission_response.status_code == 200:
                result = submission_response.json()
                score = result.get('score', 0)
                passed = result.get('passed', False)
                
                print(f"    📊 EXAM RESULT:")
                print(f"      Score: {score}%")
                print(f"      Passed: {passed}")
                print(f"      Expected: 100% (all answers correct)")
                
                if score == 0:
                    self.log_test("🚨 CRITICAL BUG REPRODUCED", False, 
                                f"Student got 0% despite all correct answers! This is the exact issue user reported.")
                    
                    # Deep dive analysis
                    print(f"    🔍 DEEP DIVE ANALYSIS:")
                    print(f"      - Test ID: {test_id}")
                    print(f"      - Questions created: {len(questions)}")
                    print(f"      - Answers submitted: {len(correct_answers)}")
                    print(f"      - Full result: {json.dumps(result, indent=8)}")
                    
                    # Check if it's a question ID mismatch
                    stored_questions = created_test.get('questions', [])
                    print(f"      - Question IDs in database:")
                    for i, q in enumerate(stored_questions):
                        print(f"        Q{i+1}: {q.get('id')} (type: {type(q.get('id')).__name__})")
                    
                    print(f"      - Answer keys submitted:")
                    for key in correct_answers.keys():
                        print(f"        {key} (type: {type(key).__name__})")
                    
                    return False
                else:
                    self.log_test("Realistic Scenario - Exam Scoring", True, 
                                f"Exam scored correctly: {score}%")
                    return True
            else:
                self.log_test("Realistic Scenario - Exam Submission", False, 
                            f"Submission failed: {submission_response.status_code}, {submission_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Realistic Scenario", False, f"Exception: {str(e)}")
            return False
    
    def investigate_existing_recent_tests(self):
        """Investigate existing tests created recently to find the scoring issue"""
        try:
            if not self.recent_programs:
                self.log_test("Investigate Recent Tests", False, "No recent programs found to investigate")
                return False
            
            issues_found = []
            
            for program in self.recent_programs:
                print(f"    🔍 Investigating program: {program['title']}")
                
                for test in program.get('final_tests', []):
                    print(f"      📝 Analyzing test: {test['title']}")
                    
                    # Analyze question structure
                    analysis = self.analyze_question_data_structure(test)
                    
                    if analysis.get('data_issues'):
                        issues_found.extend(analysis['data_issues'])
                        print(f"        ⚠️  Data issues found: {len(analysis['data_issues'])}")
                        for issue in analysis['data_issues']:
                            print(f"          - {issue}")
                    
                    # Check if test has attempts
                    try:
                        attempts_response = self.session.get(f"{BACKEND_URL}/final-test-attempts", params={
                            "test_id": test["id"]
                        })
                        
                        if attempts_response.status_code == 200:
                            attempts = attempts_response.json()
                            print(f"        📊 Found {len(attempts)} attempt(s)")
                            
                            for attempt in attempts:
                                score = attempt.get('score', 0)
                                if score == 0:
                                    issues_found.append(f"Test '{test['title']}' has 0% score attempt")
                                    print(f"          🚨 0% score attempt found! Attempt ID: {attempt.get('id')}")
                    except:
                        pass
            
            if issues_found:
                self.log_test("Investigate Recent Tests", False, 
                            f"Found {len(issues_found)} issues in recent tests")
                return False
            else:
                self.log_test("Investigate Recent Tests", True, 
                            f"Analyzed {len(self.recent_programs)} recent programs, no critical issues found")
                return True
                
        except Exception as e:
            self.log_test("Investigate Recent Tests", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_investigation(self):
        """Run comprehensive investigation of the quiz scoring issue"""
        print("🚨 URGENT: Quiz Scoring Investigation - 0% Score Bug")
        print("=" * 80)
        print("User reports: Created 4 programs with final exams YESTERDAY")
        print("Issue: All tests return 0% scores despite correct answers")
        print("=" * 80)
        
        # Step 1: Authenticate both admin and student
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed.")
            return False
        
        if not self.authenticate_student():
            print("❌ Student authentication failed. Cannot proceed.")
            return False
        
        # Step 2: Find recent programs and courses with tests
        print("\n🔍 PHASE 1: Finding Recent Test Data")
        print("-" * 50)
        self.find_recent_programs_with_tests()
        self.find_recent_courses_with_quizzes()
        
        # Step 3: Investigate existing recent tests
        print("\n🔍 PHASE 2: Investigating Existing Recent Tests")
        print("-" * 50)
        self.investigate_existing_recent_tests()
        
        # Step 4: Test question ID generation mismatch
        print("\n🔍 PHASE 3: Testing Question ID Mismatch Theory")
        print("-" * 50)
        self.test_question_id_generation_mismatch()
        
        # Step 5: Create realistic test scenario
        print("\n🔍 PHASE 4: Reproducing User's Exact Workflow")
        print("-" * 50)
        self.create_realistic_test_scenario()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        critical_issues = []
        for result in self.test_results:
            if not result["success"] and ("0%" in result["details"] or "CRITICAL" in result["test"]):
                critical_issues.append(result)
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND: {len(critical_issues)}")
            for issue in critical_issues:
                print(f"  - {issue['test']}: {issue['details']}")
        
        if success_rate < 50:
            print(f"\n🚨 QUIZ SCORING BUG CONFIRMED: Multiple tests failing with 0% scores")
        else:
            print(f"\n✅ Quiz scoring appears to be working correctly")
        
        return success_rate >= 50

if __name__ == "__main__":
    investigator = QuizScoringInvestigator()
    success = investigator.run_comprehensive_investigation()
    sys.exit(0 if success else 1)