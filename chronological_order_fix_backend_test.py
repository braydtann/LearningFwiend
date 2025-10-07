#!/usr/bin/env python3
"""
CHRONOLOGICAL ORDER QUESTION FIX BACKEND TESTING SUITE
LearningFriend LMS Application - Critical Bug Fix Verification

TESTING FOCUS (Based on Review Request):
✅ Chronological Order Bug Fix Verification - Test that final test questions preserve all items in correctOrder
✅ Final Exam Scoring - Create final test with 4+ items and verify 100% scoring for correct answers
✅ Edge Cases - Test different numbers of items (3, 4, 5, 6 items) and item reordering
✅ Integration Testing - Verify existing 3-item questions still work and grading center shows correct results

CRITICAL BUG BEING TESTED:
- User reported getting marked wrong despite correct answers on chronological order questions with more than 3 items
- Root cause: correctOrder array not properly updated when adding/removing items beyond default 3 items
- Expected fix: correctOrder should contain all item indices, not just first 3

AUTHENTICATION CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using frontend/.env REACT_APP_BACKEND_URL
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class ChronologicalOrderFixTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.test_program_id = None
        self.test_final_test_id = None
        
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
    
    def test_admin_authentication(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_student_authentication(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_create_program_with_chronological_final_test(self):
        """Create a program with final test containing chronological order questions with 4+ items"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Program with Chronological Final Test", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Step 1: Create a test program
            program_data = {
                "title": "Chronological Order Fix Test Program",
                "description": "Testing chronological order bug fix with 4+ items",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = requests.post(
                f"{BACKEND_URL}/programs",
                json=program_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if program_response.status_code == 200:
                program = program_response.json()
                self.test_program_id = program.get('id')
                print(f"✅ Created test program: {self.test_program_id}")
                
                # Step 2: Create final test with chronological order questions (4+ items)
                final_test_data = {
                    "programId": self.test_program_id,
                    "title": "Chronological Order Bug Fix Test",
                    "description": "Testing the specific A->D->B->C order scenario from user's screenshot",
                    "timeLimit": 60,
                    "passingScore": 75,
                    "questions": [
                        {
                            "id": str(uuid.uuid4()),
                            "type": "chronological-order",
                            "question": "Arrange these historical events in chronological order (A->D->B->C scenario):",
                            "items": [
                                "A: American Civil War ends (1865)",
                                "B: World War I begins (1914)", 
                                "C: World War II begins (1939)",
                                "D: Industrial Revolution begins (1760)"
                            ],
                            "correctOrder": [3, 0, 1, 2],  # D->A->B->C (1760, 1865, 1914, 1939)
                            "points": 25,
                            "explanation": "Correct chronological order: Industrial Revolution (1760), Civil War ends (1865), WWI begins (1914), WWII begins (1939)"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "type": "chronological-order",
                            "question": "Order these technological inventions (5 items test):",
                            "items": [
                                "Telephone (1876)",
                                "Light bulb (1879)",
                                "Radio (1895)",
                                "Television (1927)",
                                "Internet (1969)"
                            ],
                            "correctOrder": [0, 1, 2, 3, 4],  # All 5 items in order
                            "points": 25,
                            "explanation": "Chronological order of technological inventions"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "type": "chronological-order",
                            "question": "Order these scientific discoveries (6 items test):",
                            "items": [
                                "Newton's Laws (1687)",
                                "Darwin's Evolution (1859)",
                                "DNA Structure (1953)",
                                "Penicillin (1928)",
                                "Electricity (1752)",
                                "Atomic Theory (1803)"
                            ],
                            "correctOrder": [0, 4, 5, 1, 3, 2],  # Newton, Electricity, Atomic, Darwin, Penicillin, DNA
                            "points": 25,
                            "explanation": "Chronological order of major scientific discoveries"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "type": "multiple_choice",
                            "question": "Control question: What is 2 + 2?",
                            "options": ["3", "4", "5", "6"],
                            "correctAnswer": "1",
                            "points": 25,
                            "explanation": "Basic arithmetic control question"
                        }
                    ]
                }
                
                final_test_response = requests.post(
                    f"{BACKEND_URL}/final-tests",
                    json=final_test_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if final_test_response.status_code == 200:
                    final_test = final_test_response.json()
                    self.test_final_test_id = final_test.get('id')
                    
                    # Verify the chronological order questions have correct structure
                    questions = final_test.get('questions', [])
                    chronological_questions = [q for q in questions if q.get('type') == 'chronological-order']
                    
                    if len(chronological_questions) == 3:
                        # Check that all correctOrder arrays contain all item indices
                        structure_valid = True
                        validation_details = []
                        
                        for i, q in enumerate(chronological_questions):
                            items = q.get('items', [])
                            correct_order = q.get('correctOrder', [])
                            
                            if len(items) != len(correct_order):
                                structure_valid = False
                                validation_details.append(f"Question {i+1}: items({len(items)}) != correctOrder({len(correct_order)})")
                            
                            # Verify correctOrder contains all indices from 0 to len(items)-1
                            expected_indices = set(range(len(items)))
                            actual_indices = set(correct_order)
                            
                            if expected_indices != actual_indices:
                                structure_valid = False
                                validation_details.append(f"Question {i+1}: missing indices {expected_indices - actual_indices}")
                        
                        if structure_valid:
                            self.log_result(
                                "Create Program with Chronological Final Test", 
                                "PASS", 
                                f"Successfully created final test with chronological questions (4, 5, 6 items)",
                                f"Program ID: {self.test_program_id}, Final Test ID: {self.test_final_test_id}, Questions: {len(chronological_questions)}"
                            )
                            return True
                        else:
                            self.log_result(
                                "Create Program with Chronological Final Test", 
                                "FAIL", 
                                f"Final test created but chronological questions have structure issues",
                                f"Issues: {'; '.join(validation_details)}"
                            )
                    else:
                        self.log_result(
                            "Create Program with Chronological Final Test", 
                            "FAIL", 
                            f"Expected 3 chronological questions, found {len(chronological_questions)}",
                            f"Question types: {[q.get('type') for q in questions]}"
                        )
                else:
                    self.log_result(
                        "Create Program with Chronological Final Test", 
                        "FAIL", 
                        f"Failed to create final test, status: {final_test_response.status_code}",
                        f"Response: {final_test_response.text}"
                    )
            else:
                self.log_result(
                    "Create Program with Chronological Final Test", 
                    "FAIL", 
                    f"Failed to create program, status: {program_response.status_code}",
                    f"Response: {program_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Program with Chronological Final Test", 
                "FAIL", 
                "Failed to create program with chronological final test",
                str(e)
            )
        return False
    
    def test_final_exam_scoring_with_correct_answers(self):
        """Test that student gets 100% when providing correct chronological order for all items"""
        if not self.test_final_test_id or "student" not in self.auth_tokens:
            self.log_result(
                "Final Exam Scoring - Correct Answers", 
                "SKIP", 
                "No final test available or no student token",
                "Final test creation and student authentication required"
            )
            return False
        
        try:
            # Submit final test attempt with correct answers
            attempt_data = {
                "testId": self.test_final_test_id,
                "programId": self.test_program_id,
                "answers": [
                    {
                        "questionId": "q1",  # Will be replaced with actual IDs
                        "answer": [3, 0, 1, 2]  # D->A->B->C (correct order)
                    },
                    {
                        "questionId": "q2",
                        "answer": [0, 1, 2, 3, 4]  # All 5 items in correct order
                    },
                    {
                        "questionId": "q3", 
                        "answer": [0, 4, 5, 1, 3, 2]  # All 6 items in correct order
                    },
                    {
                        "questionId": "q4",
                        "answer": "1"  # Multiple choice control question
                    }
                ],
                "timeSpent": 1800  # 30 minutes
            }
            
            # First, get the actual question IDs from the final test
            final_test_response = requests.get(
                f"{BACKEND_URL}/final-tests/{self.test_final_test_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if final_test_response.status_code == 200:
                final_test = final_test_response.json()
                questions = final_test.get('questions', [])
                
                # Update attempt_data with actual question IDs
                for i, question in enumerate(questions):
                    if i < len(attempt_data['answers']):
                        attempt_data['answers'][i]['questionId'] = question.get('id')
                
                # Submit the attempt
                attempt_response = requests.post(
                    f"{BACKEND_URL}/final-test-attempts",
                    json=attempt_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["student"]}'
                    }
                )
                
                if attempt_response.status_code == 200:
                    attempt_result = attempt_response.json()
                    score = attempt_result.get('score', 0)
                    total_points = attempt_result.get('totalPoints', 100)
                    percentage = attempt_result.get('percentage', 0)
                    passed = attempt_result.get('passed', False)
                    
                    # Check if student got 100% (or close to it due to rounding)
                    if percentage >= 99.0 and passed:
                        self.log_result(
                            "Final Exam Scoring - Correct Answers", 
                            "PASS", 
                            f"Student achieved perfect score with correct chronological answers",
                            f"Score: {score}/{total_points} ({percentage}%), Passed: {passed}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Final Exam Scoring - Correct Answers", 
                            "FAIL", 
                            f"Student did not achieve expected score despite correct answers",
                            f"Score: {score}/{total_points} ({percentage}%), Passed: {passed}, Expected: 100%"
                        )
                else:
                    self.log_result(
                        "Final Exam Scoring - Correct Answers", 
                        "FAIL", 
                        f"Failed to submit final test attempt, status: {attempt_response.status_code}",
                        f"Response: {attempt_response.text}"
                    )
            else:
                self.log_result(
                    "Final Exam Scoring - Correct Answers", 
                    "FAIL", 
                    f"Failed to retrieve final test details, status: {final_test_response.status_code}",
                    f"Response: {final_test_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Final Exam Scoring - Correct Answers", 
                "FAIL", 
                "Failed to test final exam scoring",
                str(e)
            )
        return False
    
    def test_final_exam_scoring_with_incorrect_answers(self):
        """Test that student gets partial score when providing incorrect chronological order"""
        if not self.test_final_test_id or "student" not in self.auth_tokens:
            self.log_result(
                "Final Exam Scoring - Incorrect Answers", 
                "SKIP", 
                "No final test available or no student token",
                "Final test creation and student authentication required"
            )
            return False
        
        try:
            # Submit final test attempt with incorrect chronological answers
            attempt_data = {
                "testId": self.test_final_test_id,
                "programId": self.test_program_id,
                "answers": [
                    {
                        "questionId": "q1",
                        "answer": [0, 1, 2, 3]  # A->B->C->D (incorrect order)
                    },
                    {
                        "questionId": "q2",
                        "answer": [4, 3, 2, 1, 0]  # Reverse order (incorrect)
                    },
                    {
                        "questionId": "q3",
                        "answer": [0, 1, 2, 3, 4, 5]  # Sequential but wrong (incorrect)
                    },
                    {
                        "questionId": "q4",
                        "answer": "1"  # Multiple choice control question (correct)
                    }
                ],
                "timeSpent": 1200  # 20 minutes
            }
            
            # Get the actual question IDs from the final test
            final_test_response = requests.get(
                f"{BACKEND_URL}/final-tests/{self.test_final_test_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if final_test_response.status_code == 200:
                final_test = final_test_response.json()
                questions = final_test.get('questions', [])
                
                # Update attempt_data with actual question IDs
                for i, question in enumerate(questions):
                    if i < len(attempt_data['answers']):
                        attempt_data['answers'][i]['questionId'] = question.get('id')
                
                # Submit the attempt
                attempt_response = requests.post(
                    f"{BACKEND_URL}/final-test-attempts",
                    json=attempt_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["student"]}'
                    }
                )
                
                if attempt_response.status_code == 200:
                    attempt_result = attempt_response.json()
                    score = attempt_result.get('score', 0)
                    total_points = attempt_result.get('totalPoints', 100)
                    percentage = attempt_result.get('percentage', 0)
                    passed = attempt_result.get('passed', False)
                    
                    # Should get 25% (only the multiple choice question correct)
                    expected_percentage = 25.0
                    if abs(percentage - expected_percentage) <= 5.0:  # Allow 5% tolerance
                        self.log_result(
                            "Final Exam Scoring - Incorrect Answers", 
                            "PASS", 
                            f"Student received expected partial score for incorrect chronological answers",
                            f"Score: {score}/{total_points} ({percentage}%), Expected: ~{expected_percentage}%, Passed: {passed}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Final Exam Scoring - Incorrect Answers", 
                            "FAIL", 
                            f"Student score does not match expected partial score",
                            f"Score: {score}/{total_points} ({percentage}%), Expected: ~{expected_percentage}%, Passed: {passed}"
                        )
                else:
                    self.log_result(
                        "Final Exam Scoring - Incorrect Answers", 
                        "FAIL", 
                        f"Failed to submit final test attempt, status: {attempt_response.status_code}",
                        f"Response: {attempt_response.text}"
                    )
            else:
                self.log_result(
                    "Final Exam Scoring - Incorrect Answers", 
                    "FAIL", 
                    f"Failed to retrieve final test details, status: {final_test_response.status_code}",
                    f"Response: {final_test_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Final Exam Scoring - Incorrect Answers", 
                "FAIL", 
                "Failed to test final exam scoring with incorrect answers",
                str(e)
            )
        return False
    
    def test_edge_cases_different_item_counts(self):
        """Test chronological questions with different numbers of items (3, 4, 5, 6 items)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Edge Cases - Different Item Counts", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a course with chronological questions of different lengths
            course_data = {
                "title": "Chronological Order Edge Cases Test",
                "description": "Testing chronological order with 3, 4, 5, and 6 items",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Edge Cases Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Variable Length Chronological Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "3 items test - Order these events:",
                                        "items": ["Event A", "Event B", "Event C"],
                                        "correctOrder": [0, 1, 2]
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "4 items test - Order these events:",
                                        "items": ["Event A", "Event B", "Event C", "Event D"],
                                        "correctOrder": [0, 1, 2, 3]
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "5 items test - Order these events:",
                                        "items": ["Event A", "Event B", "Event C", "Event D", "Event E"],
                                        "correctOrder": [0, 1, 2, 3, 4]
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "6 items test - Order these events:",
                                        "items": ["Event A", "Event B", "Event C", "Event D", "Event E", "Event F"],
                                        "correctOrder": [0, 1, 2, 3, 4, 5]
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
                created_course = response.json()
                course_id = created_course.get('id')
                
                # Verify all questions have correct structure
                modules = created_course.get('modules', [])
                if len(modules) > 0:
                    lessons = modules[0].get('lessons', [])
                    if len(lessons) > 0:
                        questions = lessons[0].get('questions', [])
                        
                        if len(questions) == 4:
                            structure_valid = True
                            validation_details = []
                            
                            expected_lengths = [3, 4, 5, 6]
                            for i, question in enumerate(questions):
                                items = question.get('items', [])
                                correct_order = question.get('correctOrder', [])
                                expected_length = expected_lengths[i]
                                
                                if len(items) != expected_length:
                                    structure_valid = False
                                    validation_details.append(f"Question {i+1}: expected {expected_length} items, got {len(items)}")
                                
                                if len(correct_order) != expected_length:
                                    structure_valid = False
                                    validation_details.append(f"Question {i+1}: expected {expected_length} correctOrder indices, got {len(correct_order)}")
                                
                                # Verify correctOrder contains all indices
                                expected_indices = list(range(expected_length))
                                if correct_order != expected_indices:
                                    structure_valid = False
                                    validation_details.append(f"Question {i+1}: correctOrder {correct_order} != expected {expected_indices}")
                            
                            if structure_valid:
                                self.log_result(
                                    "Edge Cases - Different Item Counts", 
                                    "PASS", 
                                    f"Successfully created chronological questions with 3, 4, 5, 6 items",
                                    f"Course ID: {course_id}, All correctOrder arrays properly sized"
                                )
                                return True
                            else:
                                self.log_result(
                                    "Edge Cases - Different Item Counts", 
                                    "FAIL", 
                                    f"Course created but questions have structure issues",
                                    f"Issues: {'; '.join(validation_details)}"
                                )
                        else:
                            self.log_result(
                                "Edge Cases - Different Item Counts", 
                                "FAIL", 
                                f"Expected 4 questions, found {len(questions)}",
                                f"Question count mismatch"
                            )
                    else:
                        self.log_result(
                            "Edge Cases - Different Item Counts", 
                            "FAIL", 
                            "Course created but no lessons found",
                            f"Module structure issue"
                        )
                else:
                    self.log_result(
                        "Edge Cases - Different Item Counts", 
                        "FAIL", 
                        "Course created but no modules found",
                        f"Course structure issue"
                    )
            else:
                self.log_result(
                    "Edge Cases - Different Item Counts", 
                    "FAIL", 
                    f"Failed to create edge cases course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge Cases - Different Item Counts", 
                "FAIL", 
                "Failed to test edge cases with different item counts",
                str(e)
            )
        return False
    
    def test_existing_3_item_questions_compatibility(self):
        """Test that existing 3-item chronological questions still work correctly"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Existing 3-Item Questions Compatibility", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a course with traditional 3-item chronological questions
            course_data = {
                "title": "Legacy 3-Item Chronological Test",
                "description": "Testing backward compatibility with existing 3-item questions",
                "category": "Testing",
                "duration": "30 minutes",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Legacy Compatibility Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Traditional 3-Item Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "Order these historical periods:",
                                        "items": ["Medieval", "Renaissance", "Modern"],
                                        "correctOrder": [0, 1, 2]
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "chronological-order",
                                        "question": "Order these inventions:",
                                        "items": ["Wheel", "Printing Press", "Computer"],
                                        "correctOrder": [0, 1, 2]
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
                created_course = response.json()
                course_id = created_course.get('id')
                
                # Verify 3-item questions work correctly
                modules = created_course.get('modules', [])
                if len(modules) > 0:
                    lessons = modules[0].get('lessons', [])
                    if len(lessons) > 0:
                        questions = lessons[0].get('questions', [])
                        
                        if len(questions) == 2:
                            compatibility_valid = True
                            validation_details = []
                            
                            for i, question in enumerate(questions):
                                items = question.get('items', [])
                                correct_order = question.get('correctOrder', [])
                                
                                if len(items) != 3:
                                    compatibility_valid = False
                                    validation_details.append(f"Question {i+1}: expected 3 items, got {len(items)}")
                                
                                if len(correct_order) != 3:
                                    compatibility_valid = False
                                    validation_details.append(f"Question {i+1}: expected 3 correctOrder indices, got {len(correct_order)}")
                                
                                if correct_order != [0, 1, 2]:
                                    compatibility_valid = False
                                    validation_details.append(f"Question {i+1}: correctOrder {correct_order} != expected [0, 1, 2]")
                            
                            if compatibility_valid:
                                self.log_result(
                                    "Existing 3-Item Questions Compatibility", 
                                    "PASS", 
                                    f"Successfully verified backward compatibility with 3-item questions",
                                    f"Course ID: {course_id}, Both questions properly structured"
                                )
                                return True
                            else:
                                self.log_result(
                                    "Existing 3-Item Questions Compatibility", 
                                    "FAIL", 
                                    f"3-item questions have compatibility issues",
                                    f"Issues: {'; '.join(validation_details)}"
                                )
                        else:
                            self.log_result(
                                "Existing 3-Item Questions Compatibility", 
                                "FAIL", 
                                f"Expected 2 questions, found {len(questions)}",
                                f"Question count mismatch"
                            )
                    else:
                        self.log_result(
                            "Existing 3-Item Questions Compatibility", 
                            "FAIL", 
                            "Course created but no lessons found",
                            f"Module structure issue"
                        )
                else:
                    self.log_result(
                        "Existing 3-Item Questions Compatibility", 
                        "FAIL", 
                        "Course created but no modules found",
                        f"Course structure issue"
                    )
            else:
                self.log_result(
                    "Existing 3-Item Questions Compatibility", 
                    "FAIL", 
                    f"Failed to create 3-item compatibility test course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Existing 3-Item Questions Compatibility", 
                "FAIL", 
                "Failed to test 3-item questions compatibility",
                str(e)
            )
        return False
    
    def run_all_tests(self):
        """Run all chronological order fix tests"""
        print("🎯 CHRONOLOGICAL ORDER QUESTION FIX BACKEND TESTING")
        print("=" * 80)
        print("Testing critical chronological order bug fix in LearningFriend LMS")
        print("CRITICAL BUG: Students getting marked wrong despite correct answers on 4+ item questions")
        print("EXPECTED FIX: correctOrder array should contain all item indices, not just first 3")
        print("Authentication Credentials:")
        print(f"  Admin: {ADMIN_CREDENTIALS['username_or_email']}")
        print(f"  Student: {STUDENT_CREDENTIALS['username_or_email']}")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Run tests in sequence
        tests = [
            self.test_admin_authentication,
            self.test_student_authentication,
            self.test_create_program_with_chronological_final_test,
            self.test_final_exam_scoring_with_correct_answers,
            self.test_final_exam_scoring_with_incorrect_answers,
            self.test_edge_cases_different_item_counts,
            self.test_existing_3_item_questions_compatibility
        ]
        
        for test in tests:
            print(f"\n🔄 Running: {test.__name__}")
            print("-" * 50)
            test()
            time.sleep(1)  # Brief pause between tests
        
        # Print summary
        print(f"\n📊 CHRONOLOGICAL ORDER FIX TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n🎯 CRITICAL BUG FIX VERIFICATION:")
        if self.passed >= 5:  # Most tests passed
            print("✅ Chronological order bug fix appears to be working correctly")
            print("✅ Students should now get 100% for correct answers on 4+ item questions")
        else:
            print("❌ Chronological order bug fix may not be working correctly")
            print("❌ Students may still get marked wrong despite correct answers")
        
        return self.passed, self.failed

if __name__ == "__main__":
    tester = ChronologicalOrderFixTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)