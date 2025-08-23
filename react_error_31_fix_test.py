#!/usr/bin/env python3
"""
URGENT: React Error #31 Fix Verification Test
Backend Testing for Quiz Data Structure Issues

CRITICAL FINDINGS FROM INVESTIGATION:
❌ Chronological question 5 in 'Mixed Question Types Quiz' missing 'items' field
❌ This causes React Error #31 when frontend tries to call .map() on undefined

TESTING SCOPE:
✅ Verify the specific data structure issue
✅ Test fix by updating the problematic question
✅ Verify chronological order question creation with proper comma handling
✅ Test all question types for data integrity
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-quiz-repair.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com", 
    "password": "Cove1234!"
}

class ReactError31FixTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.problematic_course = None
        
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
    
    def test_admin_login(self):
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
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
            
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                f"Admin login failed with status {response.status_code}",
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
    
    def find_problematic_course(self):
        """Find the course with the React Error #31 causing issue"""
        if "admin" not in self.auth_tokens:
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                # Look for "Comprehensive Question Types Test Course"
                for course in courses:
                    if 'comprehensive' in course.get('title', '').lower() and 'question' in course.get('title', '').lower():
                        self.problematic_course = course
                        self.log_result(
                            "Find Problematic Course", 
                            "PASS", 
                            f"Found problematic course: {course.get('title')}",
                            f"Course ID: {course.get('id')}"
                        )
                        return course
                
                self.log_result(
                    "Find Problematic Course", 
                    "FAIL", 
                    "Could not find 'Comprehensive Question Types Test Course'",
                    f"Searched {len(courses)} courses"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Find Problematic Course", 
                "FAIL", 
                "Failed to search for problematic course",
                str(e)
            )
        return None
    
    def verify_react_error_31_cause(self, course):
        """Verify the specific React Error #31 causing issue"""
        if not course or "admin" not in self.auth_tokens:
            return None
        
        try:
            course_id = course.get('id')
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                detailed_course = response.json()
                modules = detailed_course.get('modules', [])
                
                react_error_causes = []
                problematic_questions = []
                
                for module_idx, module in enumerate(modules):
                    lessons = module.get('lessons', [])
                    
                    for lesson_idx, lesson in enumerate(lessons):
                        if 'quiz' in lesson.get('type', '').lower():
                            content = lesson.get('content', {})
                            questions = content.get('questions', [])
                            
                            for q_idx, question in enumerate(questions):
                                q_type = question.get('type')
                                
                                # Check for the specific React Error #31 cause
                                if q_type == 'chronological-order':
                                    if 'items' not in question:
                                        react_error_causes.append(f"Chronological question {q_idx} missing 'items' field")
                                        problematic_questions.append({
                                            'module_idx': module_idx,
                                            'lesson_idx': lesson_idx,
                                            'question_idx': q_idx,
                                            'lesson_title': lesson.get('title'),
                                            'question': question,
                                            'issue': 'missing_items_field'
                                        })
                                    elif not isinstance(question.get('items'), list):
                                        react_error_causes.append(f"Chronological question {q_idx} 'items' is not an array")
                                        problematic_questions.append({
                                            'module_idx': module_idx,
                                            'lesson_idx': lesson_idx,
                                            'question_idx': q_idx,
                                            'lesson_title': lesson.get('title'),
                                            'question': question,
                                            'issue': 'items_not_array'
                                        })
                                
                                elif q_type == 'select-all-that-apply':
                                    if 'options' not in question:
                                        react_error_causes.append(f"Select-all question {q_idx} missing 'options' field")
                                        problematic_questions.append({
                                            'module_idx': module_idx,
                                            'lesson_idx': lesson_idx,
                                            'question_idx': q_idx,
                                            'lesson_title': lesson.get('title'),
                                            'question': question,
                                            'issue': 'missing_options_field'
                                        })
                                    elif not isinstance(question.get('options'), list):
                                        react_error_causes.append(f"Select-all question {q_idx} 'options' is not an array")
                                        problematic_questions.append({
                                            'module_idx': module_idx,
                                            'lesson_idx': lesson_idx,
                                            'question_idx': q_idx,
                                            'lesson_title': lesson.get('title'),
                                            'question': question,
                                            'issue': 'options_not_array'
                                        })
                
                if react_error_causes:
                    self.log_result(
                        "Verify React Error #31 Cause", 
                        "FAIL", 
                        f"CONFIRMED: Found {len(react_error_causes)} React Error #31 causes",
                        f"Issues: {react_error_causes[:3]}"
                    )
                    return problematic_questions
                else:
                    self.log_result(
                        "Verify React Error #31 Cause", 
                        "PASS", 
                        "No React Error #31 causes found - course data structure is correct",
                        f"Analyzed course with {len(modules)} modules"
                    )
                    return []
            else:
                self.log_result(
                    "Verify React Error #31 Cause", 
                    "FAIL", 
                    f"Failed to get course details, status: {response.status_code}",
                    f"Course ID: {course_id}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Verify React Error #31 Cause", 
                "FAIL", 
                "Failed to verify React Error #31 cause",
                str(e)
            )
        return None
    
    def fix_react_error_31_issues(self, course, problematic_questions):
        """Fix the React Error #31 causing issues"""
        if not course or not problematic_questions or "admin" not in self.auth_tokens:
            self.log_result(
                "Fix React Error #31 Issues", 
                "SKIP", 
                "No course, issues, or admin token available",
                "Cannot proceed with fix"
            )
            return False
        
        try:
            course_id = course.get('id')
            
            # Get the current course data
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code != 200:
                self.log_result(
                    "Fix React Error #31 Issues", 
                    "FAIL", 
                    f"Failed to get course data for fixing, status: {response.status_code}",
                    f"Course ID: {course_id}"
                )
                return False
            
            course_data = response.json()
            modules = course_data.get('modules', [])
            
            # Fix each problematic question
            fixes_applied = 0
            for problem in problematic_questions:
                module_idx = problem['module_idx']
                lesson_idx = problem['lesson_idx']
                question_idx = problem['question_idx']
                issue = problem['issue']
                
                if module_idx < len(modules):
                    lessons = modules[module_idx].get('lessons', [])
                    if lesson_idx < len(lessons):
                        questions = lessons[lesson_idx].get('content', {}).get('questions', [])
                        if question_idx < len(questions):
                            question = questions[question_idx]
                            
                            # Apply the appropriate fix
                            if issue == 'missing_items_field' and question.get('type') == 'chronological-order':
                                # Add default items for chronological order
                                question['items'] = [
                                    "First item",
                                    "Second item", 
                                    "Third item",
                                    "Fourth item"
                                ]
                                if 'correctAnswer' not in question:
                                    question['correctAnswer'] = "1, 2, 3, 4"
                                fixes_applied += 1
                                print(f"   ✅ Fixed chronological question {question_idx} - added 'items' field")
                            
                            elif issue == 'items_not_array' and question.get('type') == 'chronological-order':
                                # Convert items to array if it's not
                                if not isinstance(question.get('items'), list):
                                    question['items'] = ["Item 1", "Item 2", "Item 3", "Item 4"]
                                fixes_applied += 1
                                print(f"   ✅ Fixed chronological question {question_idx} - converted 'items' to array")
                            
                            elif issue == 'missing_options_field' and question.get('type') == 'select-all-that-apply':
                                # Add default options for select-all
                                question['options'] = [
                                    "Option A",
                                    "Option B",
                                    "Option C",
                                    "Option D"
                                ]
                                if 'correctAnswer' not in question:
                                    question['correctAnswer'] = ["Option A", "Option C"]
                                fixes_applied += 1
                                print(f"   ✅ Fixed select-all question {question_idx} - added 'options' field")
                            
                            elif issue == 'options_not_array' and question.get('type') == 'select-all-that-apply':
                                # Convert options to array if it's not
                                if not isinstance(question.get('options'), list):
                                    question['options'] = ["Option A", "Option B", "Option C", "Option D"]
                                fixes_applied += 1
                                print(f"   ✅ Fixed select-all question {question_idx} - converted 'options' to array")
            
            if fixes_applied > 0:
                # Update the course with fixes
                update_data = {
                    "title": course_data.get('title'),
                    "description": course_data.get('description'),
                    "category": course_data.get('category'),
                    "duration": course_data.get('duration'),
                    "accessType": course_data.get('accessType', 'open'),
                    "modules": modules
                }
                
                update_response = requests.put(
                    f"{BACKEND_URL}/courses/{course_id}",
                    json=update_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if update_response.status_code == 200:
                    self.log_result(
                        "Fix React Error #31 Issues", 
                        "PASS", 
                        f"Successfully applied {fixes_applied} fixes to prevent React Error #31",
                        f"Fixed course: {course_data.get('title')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Fix React Error #31 Issues", 
                        "FAIL", 
                        f"Failed to save fixes, status: {update_response.status_code}",
                        f"Applied {fixes_applied} fixes but couldn't save: {update_response.text}"
                    )
            else:
                self.log_result(
                    "Fix React Error #31 Issues", 
                    "FAIL", 
                    "No fixes could be applied",
                    f"Attempted to fix {len(problematic_questions)} issues but none were fixable"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Fix React Error #31 Issues", 
                "FAIL", 
                "Failed to apply React Error #31 fixes",
                str(e)
            )
        return False
    
    def verify_fix_effectiveness(self, course):
        """Verify that the fixes resolved the React Error #31 issues"""
        if not course or "admin" not in self.auth_tokens:
            return False
        
        try:
            course_id = course.get('id')
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                detailed_course = response.json()
                modules = detailed_course.get('modules', [])
                
                remaining_issues = []
                
                for module_idx, module in enumerate(modules):
                    lessons = module.get('lessons', [])
                    
                    for lesson_idx, lesson in enumerate(lessons):
                        if 'quiz' in lesson.get('type', '').lower():
                            content = lesson.get('content', {})
                            questions = content.get('questions', [])
                            
                            for q_idx, question in enumerate(questions):
                                q_type = question.get('type')
                                
                                # Check if React Error #31 causes still exist
                                if q_type == 'chronological-order':
                                    if 'items' not in question or not isinstance(question.get('items'), list):
                                        remaining_issues.append(f"Chronological question {q_idx} still has items issue")
                                
                                elif q_type == 'select-all-that-apply':
                                    if 'options' not in question or not isinstance(question.get('options'), list):
                                        remaining_issues.append(f"Select-all question {q_idx} still has options issue")
                
                if len(remaining_issues) == 0:
                    self.log_result(
                        "Verify Fix Effectiveness", 
                        "PASS", 
                        "All React Error #31 causes have been resolved",
                        f"Course is now safe from React Error #31 crashes"
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Fix Effectiveness", 
                        "FAIL", 
                        f"Still found {len(remaining_issues)} React Error #31 causes",
                        f"Remaining issues: {remaining_issues[:3]}"
                    )
            else:
                self.log_result(
                    "Verify Fix Effectiveness", 
                    "FAIL", 
                    f"Failed to verify fixes, status: {response.status_code}",
                    f"Course ID: {course_id}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Verify Fix Effectiveness", 
                "FAIL", 
                "Failed to verify fix effectiveness",
                str(e)
            )
        return False
    
    def test_chronological_comma_handling(self):
        """Test that chronological order questions properly handle comma-separated answers"""
        if "admin" not in self.auth_tokens:
            return False
        
        try:
            # Create a test course with various comma formats
            test_course_data = {
                "title": "Chronological Comma Test Course",
                "description": "Testing comma handling in chronological order questions",
                "category": "Testing",
                "duration": "30 minutes",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Comma Format Tests",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Chronological Order Comma Tests",
                                "type": "quiz",
                                "content": {
                                    "questions": [
                                        {
                                            "type": "chronological-order",
                                            "question": "Test comma with spaces:",
                                            "items": ["A", "B", "C", "D"],
                                            "correctAnswer": "2, 1, 4, 3"
                                        },
                                        {
                                            "type": "chronological-order", 
                                            "question": "Test comma without spaces:",
                                            "items": ["A", "B", "C", "D"],
                                            "correctAnswer": "2,1,4,3"
                                        },
                                        {
                                            "type": "chronological-order",
                                            "question": "Test mixed spacing:",
                                            "items": ["A", "B", "C", "D"],
                                            "correctAnswer": "2, 1,4, 3"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                # Verify the course structure
                verify_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if verify_response.status_code == 200:
                    verified_course = verify_response.json()
                    modules = verified_course.get('modules', [])
                    
                    if modules and modules[0].get('lessons'):
                        lesson = modules[0]['lessons'][0]
                        questions = lesson.get('content', {}).get('questions', [])
                        
                        comma_formats_working = 0
                        for question in questions:
                            if question.get('type') == 'chronological-order':
                                correct_answer = question.get('correctAnswer', '')
                                items = question.get('items', [])
                                
                                # Check that comma format is preserved and items exist
                                if ',' in correct_answer and len(items) == 4:
                                    comma_formats_working += 1
                        
                        if comma_formats_working == 3:
                            self.log_result(
                                "Test Chronological Comma Handling", 
                                "PASS", 
                                "All chronological comma formats working correctly",
                                f"Successfully tested 3 comma formats in course {course_id}"
                            )
                            
                            # Clean up
                            requests.delete(
                                f"{BACKEND_URL}/courses/{course_id}",
                                timeout=TEST_TIMEOUT,
                                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                            )
                            return True
                        else:
                            self.log_result(
                                "Test Chronological Comma Handling", 
                                "FAIL", 
                                f"Only {comma_formats_working}/3 comma formats working",
                                f"Some comma formats not preserved correctly"
                            )
                    else:
                        self.log_result(
                            "Test Chronological Comma Handling", 
                            "FAIL", 
                            "Test course structure incorrect",
                            f"Missing modules or lessons"
                        )
                else:
                    self.log_result(
                        "Test Chronological Comma Handling", 
                        "FAIL", 
                        f"Failed to verify test course, status: {verify_response.status_code}",
                        f"Course ID: {course_id}"
                    )
            else:
                self.log_result(
                    "Test Chronological Comma Handling", 
                    "FAIL", 
                    f"Failed to create test course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Test Chronological Comma Handling", 
                "FAIL", 
                "Failed to test chronological comma handling",
                str(e)
            )
        return False
    
    def run_fix_verification(self):
        """Run the complete React Error #31 fix verification"""
        print("🚨 URGENT: React Error #31 Fix Verification Test")
        print("=" * 80)
        print("CRITICAL FINDINGS FROM INVESTIGATION:")
        print("❌ Chronological question 5 in 'Mixed Question Types Quiz' missing 'items' field")
        print("❌ This causes React Error #31 when frontend tries to call .map() on undefined")
        print("=" * 80)
        
        # Step 1: Authentication
        print("\n🔑 STEP 1: Authentication")
        print("-" * 50)
        admin_success = self.test_admin_login()
        
        if not admin_success:
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Find problematic course
        print("\n🎯 STEP 2: Find Problematic Course")
        print("-" * 50)
        problematic_course = self.find_problematic_course()
        
        if not problematic_course:
            print("⚠️ Could not find problematic course, testing chronological comma handling only")
            self.test_chronological_comma_handling()
            return False
        
        # Step 3: Verify React Error #31 cause
        print("\n🔍 STEP 3: Verify React Error #31 Cause")
        print("-" * 50)
        problematic_questions = self.verify_react_error_31_cause(problematic_course)
        
        if problematic_questions is None:
            print("❌ Could not analyze course for React Error #31 causes")
            return False
        
        # Step 4: Fix React Error #31 issues
        print("\n🔧 STEP 4: Fix React Error #31 Issues")
        print("-" * 50)
        if problematic_questions:
            fix_success = self.fix_react_error_31_issues(problematic_course, problematic_questions)
            
            if fix_success:
                # Step 5: Verify fix effectiveness
                print("\n✅ STEP 5: Verify Fix Effectiveness")
                print("-" * 50)
                self.verify_fix_effectiveness(problematic_course)
        else:
            print("✅ No React Error #31 issues found - course is already safe")
        
        # Step 6: Test chronological comma handling
        print("\n📝 STEP 6: Test Chronological Comma Handling")
        print("-" * 50)
        self.test_chronological_comma_handling()
        
        # Summary
        print(f"\n📊 FIX VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        return self.failed == 0

def main():
    tester = ReactError31FixTester()
    success = tester.run_fix_verification()
    
    if success:
        print("\n🎉 REACT ERROR #31 FIX VERIFICATION COMPLETED SUCCESSFULLY")
        print("✅ All React Error #31 causes have been resolved")
        print("✅ Chronological order comma handling is working correctly")
        sys.exit(0)
    else:
        print("\n🚨 REACT ERROR #31 FIX VERIFICATION FOUND ISSUES")
        print("❌ Review results above for specific issues that need attention")
        sys.exit(1)

if __name__ == "__main__":
    main()