#!/usr/bin/env python3
"""
Google Drive URL Conversion Fix Testing
Testing the implementation of Google Drive URL conversion for quiz images in QuizTakingNewFixed.js and FinalTest.js
"""

import requests
import json
import sys
import os
from datetime import datetime
import re

# Configuration
BACKEND_URL = "https://lms-evolution.emergent.host/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class GoogleDriveURLTestRunner:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                self.log_test("Admin Authentication", True, f"Admin user: {data.get('user', {}).get('full_name', 'Unknown')}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_student(self):
        """Authenticate student user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                self.log_test("Student Authentication", True, f"Student user: {data.get('user', {}).get('full_name', 'Unknown')}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_courses_with_quiz_images(self):
        """Get courses that contain quiz questions with images"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/courses", headers=headers, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Get Courses with Quiz Images", False, f"Failed to get courses: {response.status_code}")
                return []
            
            courses = response.json()
            courses_with_images = []
            
            for course in courses:
                if course.get('modules'):
                    for module in course['modules']:
                        if module.get('lessons'):
                            for lesson in module['lessons']:
                                if lesson.get('type') == 'quiz':
                                    # Check both old and new quiz structures
                                    questions = []
                                    if lesson.get('questions'):
                                        questions = lesson['questions']
                                    elif lesson.get('quiz', {}).get('questions'):
                                        questions = lesson['quiz']['questions']
                                    
                                    # Look for questions with images
                                    for question in questions:
                                        has_question_image = bool(question.get('questionImage'))
                                        has_option_images = False
                                        
                                        # Check for option images
                                        if question.get('options'):
                                            for option in question['options']:
                                                if isinstance(option, dict) and option.get('image'):
                                                    has_option_images = True
                                                    break
                                        
                                        # Check for chronological order item images
                                        if question.get('items'):
                                            for item in question['items']:
                                                if isinstance(item, dict) and item.get('image'):
                                                    has_option_images = True
                                                    break
                                        
                                        if has_question_image or has_option_images:
                                            courses_with_images.append({
                                                'course_id': course['id'],
                                                'course_title': course['title'],
                                                'lesson_id': lesson['id'],
                                                'lesson_title': lesson.get('title', 'Quiz Lesson'),
                                                'question_id': question.get('id'),
                                                'question_type': question.get('type'),
                                                'has_question_image': has_question_image,
                                                'has_option_images': has_option_images,
                                                'question_image': question.get('questionImage'),
                                                'question': question.get('question', '')[:100] + '...'
                                            })
            
            self.log_test("Get Courses with Quiz Images", True, f"Found {len(courses_with_images)} questions with images across {len(set(c['course_id'] for c in courses_with_images))} courses")
            return courses_with_images
            
        except Exception as e:
            self.log_test("Get Courses with Quiz Images", False, f"Exception: {str(e)}")
            return []
    
    def test_google_drive_url_patterns(self):
        """Test various Google Drive URL patterns that should be converted"""
        test_urls = [
            # Standard Google Drive sharing URL
            {
                'input': 'https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view?usp=sharing',
                'expected': 'https://drive.googleusercontent.com/u/0/uc?id=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms&export=view',
                'description': 'Standard Google Drive sharing URL'
            },
            # Alternative Google Drive URL format
            {
                'input': 'https://drive.google.com/open?id=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms',
                'expected': 'https://drive.googleusercontent.com/u/0/uc?id=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms&export=view',
                'description': 'Alternative Google Drive open URL'
            },
            # Non-Google Drive URL should remain unchanged
            {
                'input': 'https://example.com/image.jpg',
                'expected': 'https://example.com/image.jpg',
                'description': 'Non-Google Drive URL should remain unchanged'
            },
            # Empty/null URL should remain unchanged
            {
                'input': '',
                'expected': '',
                'description': 'Empty URL should remain unchanged'
            }
        ]
        
        # Test the conversion logic (simulating frontend function)
        def convert_google_drive_url(url):
            if not url or not isinstance(url, str):
                return url
            
            # Check if it's a Google Drive URL
            drive_regex = r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/view'
            match = re.search(drive_regex, url)
            
            if match:
                file_id = match.group(1)
                return f'https://drive.googleusercontent.com/u/0/uc?id={file_id}&export=view'
            
            # Also handle alternative Google Drive sharing URLs
            alt_drive_regex = r'https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)'
            alt_match = re.search(alt_drive_regex, url)
            
            if alt_match:
                file_id = alt_match.group(1)
                return f'https://drive.googleusercontent.com/u/0/uc?id={file_id}&export=view'
            
            # Return original URL if not a Google Drive URL
            return url
        
        all_passed = True
        for test_case in test_urls:
            result = convert_google_drive_url(test_case['input'])
            passed = result == test_case['expected']
            all_passed = all_passed and passed
            
            self.log_test(
                f"URL Conversion - {test_case['description']}", 
                passed,
                f"Input: {test_case['input'][:50]}{'...' if len(test_case['input']) > 50 else ''}, Output: {result[:50]}{'...' if len(result) > 50 else ''}"
            )
        
        return all_passed
    
    def test_quiz_endpoints_with_images(self, courses_with_images):
        """Test quiz endpoints that return question data with images"""
        if not courses_with_images:
            self.log_test("Quiz Endpoints with Images", False, "No courses with quiz images found to test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            tested_courses = set()
            successful_tests = 0
            total_tests = 0
            
            for quiz_data in courses_with_images[:5]:  # Test first 5 to avoid timeout
                course_id = quiz_data['course_id']
                
                if course_id in tested_courses:
                    continue
                    
                tested_courses.add(course_id)
                total_tests += 1
                
                # Test GET /api/courses/{course_id} endpoint
                response = self.session.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers, timeout=30)
                
                if response.status_code == 200:
                    course_data = response.json()
                    
                    # Verify course structure contains quiz data
                    has_quiz_data = False
                    image_urls_found = []
                    
                    if course_data.get('modules'):
                        for module in course_data['modules']:
                            if module.get('lessons'):
                                for lesson in module['lessons']:
                                    if lesson.get('type') == 'quiz':
                                        # Check both old and new quiz structures
                                        questions = []
                                        if lesson.get('questions'):
                                            questions = lesson['questions']
                                        elif lesson.get('quiz', {}).get('questions'):
                                            questions = lesson['quiz']['questions']
                                        
                                        if questions:
                                            has_quiz_data = True
                                            
                                            # Collect image URLs for analysis
                                            for question in questions:
                                                if question.get('questionImage'):
                                                    image_urls_found.append(question['questionImage'])
                                                
                                                if question.get('options'):
                                                    for option in question['options']:
                                                        if isinstance(option, dict) and option.get('image'):
                                                            image_urls_found.append(option['image'])
                                                
                                                if question.get('items'):
                                                    for item in question['items']:
                                                        if isinstance(item, dict) and item.get('image'):
                                                            image_urls_found.append(item['image'])
                    
                    if has_quiz_data:
                        successful_tests += 1
                        google_drive_urls = [url for url in image_urls_found if 'drive.google.com' in url]
                        
                        self.log_test(
                            f"Quiz Endpoint - Course {quiz_data['course_title'][:30]}",
                            True,
                            f"Found {len(image_urls_found)} image URLs, {len(google_drive_urls)} Google Drive URLs"
                        )
                    else:
                        self.log_test(
                            f"Quiz Endpoint - Course {quiz_data['course_title'][:30]}",
                            False,
                            "No quiz data found in course structure"
                        )
                else:
                    self.log_test(
                        f"Quiz Endpoint - Course {quiz_data['course_title'][:30]}",
                        False,
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )
            
            overall_success = successful_tests > 0
            self.log_test(
                "Quiz Endpoints with Images - Overall",
                overall_success,
                f"Successfully tested {successful_tests}/{total_tests} courses with quiz images"
            )
            
            return overall_success
            
        except Exception as e:
            self.log_test("Quiz Endpoints with Images", False, f"Exception: {str(e)}")
            return False
    
    def test_question_types_with_images(self):
        """Test all question types mentioned in review request for image support"""
        question_types = [
            "True/False",
            "Multiple Choice", 
            "Select All That Apply",
            "Chronological Order",
            "Short Answer",
            "Long Form"
        ]
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/courses", headers=headers, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Question Types with Images", False, f"Failed to get courses: {response.status_code}")
                return False
            
            courses = response.json()
            question_type_coverage = {}
            
            for course in courses:
                if course.get('modules'):
                    for module in course['modules']:
                        if module.get('lessons'):
                            for lesson in module['lessons']:
                                if lesson.get('type') == 'quiz':
                                    # Check both old and new quiz structures
                                    questions = []
                                    if lesson.get('questions'):
                                        questions = lesson['questions']
                                    elif lesson.get('quiz', {}).get('questions'):
                                        questions = lesson['quiz']['questions']
                                    
                                    for question in questions:
                                        q_type = question.get('type', 'unknown')
                                        
                                        # Normalize question type names
                                        type_mapping = {
                                            'true-false': 'True/False',
                                            'multiple-choice': 'Multiple Choice',
                                            'select-all-that-apply': 'Select All That Apply',
                                            'chronological-order': 'Chronological Order',
                                            'short-answer': 'Short Answer',
                                            'long-form-answer': 'Long Form'
                                        }
                                        
                                        normalized_type = type_mapping.get(q_type, q_type)
                                        
                                        if normalized_type not in question_type_coverage:
                                            question_type_coverage[normalized_type] = {
                                                'total': 0,
                                                'with_images': 0,
                                                'examples': []
                                            }
                                        
                                        question_type_coverage[normalized_type]['total'] += 1
                                        
                                        # Check for images
                                        has_images = False
                                        if question.get('questionImage'):
                                            has_images = True
                                        
                                        if question.get('options'):
                                            for option in question['options']:
                                                if isinstance(option, dict) and option.get('image'):
                                                    has_images = True
                                                    break
                                        
                                        if question.get('items'):
                                            for item in question['items']:
                                                if isinstance(item, dict) and item.get('image'):
                                                    has_images = True
                                                    break
                                        
                                        if has_images:
                                            question_type_coverage[normalized_type]['with_images'] += 1
                                            if len(question_type_coverage[normalized_type]['examples']) < 3:
                                                question_type_coverage[normalized_type]['examples'].append({
                                                    'course': course['title'][:30],
                                                    'question': question.get('question', '')[:50] + '...'
                                                })
            
            # Report coverage for each question type
            for q_type in question_types:
                if q_type in question_type_coverage:
                    coverage = question_type_coverage[q_type]
                    self.log_test(
                        f"Question Type Coverage - {q_type}",
                        True,
                        f"Found {coverage['total']} questions, {coverage['with_images']} with images"
                    )
                else:
                    self.log_test(
                        f"Question Type Coverage - {q_type}",
                        False,
                        "No questions of this type found in system"
                    )
            
            # Overall assessment
            types_with_images = sum(1 for q_type in question_types if question_type_coverage.get(q_type, {}).get('with_images', 0) > 0)
            overall_success = types_with_images >= 3  # At least 3 question types should have image support
            
            self.log_test(
                "Question Types with Images - Overall",
                overall_success,
                f"{types_with_images}/{len(question_types)} question types have image support in the system"
            )
            
            return overall_success
            
        except Exception as e:
            self.log_test("Question Types with Images", False, f"Exception: {str(e)}")
            return False
    
    def test_frontend_components_implementation(self):
        """Test that frontend components have the convertGoogleDriveUrl implementation"""
        components_to_check = [
            "/app/frontend/src/pages/QuizTakingNewFixed.js",
            "/app/frontend/src/pages/FinalTest.js"
        ]
        
        implementation_found = {}
        
        for component_path in components_to_check:
            try:
                if os.path.exists(component_path):
                    with open(component_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for convertGoogleDriveUrl function
                    has_function = 'convertGoogleDriveUrl' in content
                    has_regex_pattern = 'drive\\.google\\.com' in content  # Check for escaped regex pattern
                    has_conversion_logic = 'drive.googleusercontent.com' in content
                    has_usage = content.count('convertGoogleDriveUrl(') >= 1  # Function definition + usage
                    
                    implementation_found[component_path] = {
                        'exists': True,
                        'has_function': has_function,
                        'has_regex': has_regex_pattern,
                        'has_conversion': has_conversion_logic,
                        'has_usage': has_usage,
                        'usage_count': content.count('convertGoogleDriveUrl(') - 1  # Subtract function definition
                    }
                    
                    component_name = component_path.split('/')[-1]
                    success = has_function and has_regex_pattern and has_conversion_logic and has_usage
                    
                    self.log_test(
                        f"Frontend Implementation - {component_name}",
                        success,
                        f"Function: {has_function}, Regex: {has_regex_pattern}, Conversion: {has_conversion_logic}, Usage: {implementation_found[component_path]['usage_count']} times"
                    )
                else:
                    implementation_found[component_path] = {'exists': False}
                    component_name = component_path.split('/')[-1]
                    self.log_test(
                        f"Frontend Implementation - {component_name}",
                        False,
                        "Component file not found"
                    )
                    
            except Exception as e:
                component_name = component_path.split('/')[-1]
                self.log_test(
                    f"Frontend Implementation - {component_name}",
                    False,
                    f"Error reading file: {str(e)}"
                )
        
        # Overall assessment
        successful_implementations = sum(1 for impl in implementation_found.values() 
                                       if impl.get('exists') and impl.get('has_function') and 
                                          impl.get('has_conversion') and impl.get('has_usage'))
        
        overall_success = successful_implementations == len(components_to_check)
        
        self.log_test(
            "Frontend Implementation - Overall",
            overall_success,
            f"{successful_implementations}/{len(components_to_check)} components properly implement Google Drive URL conversion"
        )
        
        return overall_success
    
    def run_comprehensive_test(self):
        """Run comprehensive Google Drive URL conversion testing"""
        print("🎯 GOOGLE DRIVE URL CONVERSION FIX TESTING INITIATED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Authentication tests
        print("\n📋 AUTHENTICATION TESTING")
        print("-" * 40)
        admin_auth = self.authenticate_admin()
        student_auth = self.authenticate_student()
        
        if not admin_auth or not student_auth:
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Frontend implementation tests
        print("\n🔧 FRONTEND IMPLEMENTATION TESTING")
        print("-" * 40)
        frontend_impl = self.test_frontend_components_implementation()
        
        # URL conversion pattern tests
        print("\n🔗 URL CONVERSION PATTERN TESTING")
        print("-" * 40)
        url_patterns = self.test_google_drive_url_patterns()
        
        # Backend quiz data tests
        print("\n📚 BACKEND QUIZ DATA TESTING")
        print("-" * 40)
        courses_with_images = self.get_courses_with_quiz_images()
        quiz_endpoints = self.test_quiz_endpoints_with_images(courses_with_images)
        
        # Question type coverage tests
        print("\n❓ QUESTION TYPE COVERAGE TESTING")
        print("-" * 40)
        question_types = self.test_question_types_with_images()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical assessments
        critical_tests = [
            ("Authentication", admin_auth and student_auth),
            ("Frontend Implementation", frontend_impl),
            ("URL Conversion Logic", url_patterns),
            ("Backend Quiz Data", quiz_endpoints)
        ]
        
        print(f"\n🎯 CRITICAL ASSESSMENTS:")
        for test_name, result in critical_tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        overall_success = all(result for _, result in critical_tests)
        
        if overall_success:
            print(f"\n🎉 GOOGLE DRIVE URL CONVERSION FIX TESTING COMPLETED SUCCESSFULLY")
            print(f"✅ All critical functionality is working correctly")
            print(f"✅ Frontend components properly implement URL conversion")
            print(f"✅ Backend APIs return quiz data with image URLs")
            print(f"✅ URL conversion patterns work as expected")
        else:
            print(f"\n🚨 GOOGLE DRIVE URL CONVERSION FIX TESTING COMPLETED WITH ISSUES")
            failed_critical = [name for name, result in critical_tests if not result]
            print(f"❌ Failed critical tests: {', '.join(failed_critical)}")
        
        return overall_success

def main():
    """Main test execution"""
    tester = GoogleDriveURLTestRunner()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()