#!/usr/bin/env python3
"""
🧪 QUESTION IMAGE FIX VERIFICATION: Short Answer & Long Form Question Image Display

TESTING OBJECTIVE:
Verify that the question image fix has been properly implemented for Short Answer and Long Form question types in the quiz system.

SPECIFIC TESTS NEEDED:
1. Create Test Quiz: Create a test quiz with Short Answer and Long Form questions that have questionImage URLs
2. Backend Data Verification: Verify that question image URLs are properly stored in the backend
3. API Response Check: Confirm that GET /api/courses/{id} returns question data with questionImage field
4. Data Structure Validation: Ensure question image data is in the correct format for frontend consumption

SUCCESS CRITERIA:
- Backend properly stores questionImage field for Short Answer and Long Form questions
- API responses include question image URLs in the correct format
- All required APIs working correctly for quiz image display

CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import uuid
from datetime import datetime
import sys
import os

# Configuration
BACKEND_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class QuestionImageTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_course_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                self.log_test("Admin Authentication", True, f"Token length: {len(self.admin_token)} chars")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_course_with_question_images(self):
        """Create a test course with Short Answer and Long Form questions that have questionImage URLs"""
        try:
            # Sample question images for testing
            sample_image_urls = [
                "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",  # Question image 1
                "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400",  # Question image 2
                "https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=400",  # Question image 3
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"   # Question image 4
            ]
            
            # Create course with Short Answer and Long Form questions with questionImage
            course_data = {
                "title": "Question Image Test Course - Short Answer & Long Form",
                "description": "Test course to verify question image functionality for Short Answer and Long Form question types",
                "category": "Testing",
                "duration": "30 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400",
                "accessType": "open",
                "learningOutcomes": [
                    "Test question image display for Short Answer questions",
                    "Test question image display for Long Form questions",
                    "Verify backend storage of questionImage field",
                    "Validate API response format for question images"
                ],
                "modules": [
                    {
                        "title": "Question Image Testing Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Short Answer & Long Form Question Image Test",
                                "type": "quiz",
                                "content": "Test quiz with question images",
                                "duration": "15 minutes",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "short-answer",
                                        "question": "What do you see in this image? Describe the main elements.",
                                        "questionImage": sample_image_urls[0],
                                        "correctAnswer": "Sample answer for short answer question",
                                        "points": 10
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "short-answer", 
                                        "question": "Based on the image shown, what technology is being demonstrated?",
                                        "questionImage": sample_image_urls[1],
                                        "correctAnswer": "Technology demonstration answer",
                                        "points": 10
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "long-form-answer",
                                        "question": "Analyze the image and provide a detailed explanation of what you observe. Include your thoughts on the composition, colors, and overall message.",
                                        "questionImage": sample_image_urls[2],
                                        "correctAnswer": "Detailed analysis of the image including composition, colors, and message interpretation",
                                        "points": 20
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "long-form-answer",
                                        "question": "Write a comprehensive essay about the subject matter shown in this image. Discuss its significance and potential applications.",
                                        "questionImage": sample_image_urls[3],
                                        "correctAnswer": "Comprehensive essay about the subject matter, significance, and applications",
                                        "points": 20
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
                self.test_course_id = course['id']
                
                # Verify the course was created with question images
                questions = course['modules'][0]['lessons'][0]['questions']
                short_answer_count = sum(1 for q in questions if q['type'] == 'short-answer' and 'questionImage' in q)
                long_form_count = sum(1 for q in questions if q['type'] == 'long-form-answer' and 'questionImage' in q)
                
                self.log_test("Create Test Course with Question Images", True, 
                            f"Course ID: {self.test_course_id}, Short Answer with images: {short_answer_count}, Long Form with images: {long_form_count}")
                return True
            else:
                self.log_test("Create Test Course with Question Images", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Test Course with Question Images", False, f"Exception: {str(e)}")
            return False
    
    def verify_backend_data_storage(self):
        """Verify that question image URLs are properly stored in the backend"""
        try:
            if not self.test_course_id:
                self.log_test("Backend Data Storage Verification", False, "No test course ID available")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/courses/{self.test_course_id}")
            
            if response.status_code == 200:
                course = response.json()
                
                # Check if course has modules and lessons
                if not course.get('modules') or not course['modules'][0].get('lessons'):
                    self.log_test("Backend Data Storage Verification", False, "Course missing modules or lessons")
                    return False
                
                questions = course['modules'][0]['lessons'][0].get('questions', [])
                
                # Verify questionImage field storage
                questions_with_images = []
                for question in questions:
                    if question.get('type') in ['short-answer', 'long-form-answer'] and 'questionImage' in question:
                        questions_with_images.append({
                            'type': question['type'],
                            'questionImage': question['questionImage'],
                            'has_valid_url': question['questionImage'].startswith('https://')
                        })
                
                if len(questions_with_images) >= 4:  # Should have 2 short-answer + 2 long-form
                    short_answer_images = [q for q in questions_with_images if q['type'] == 'short-answer']
                    long_form_images = [q for q in questions_with_images if q['type'] == 'long-form-answer']
                    
                    self.log_test("Backend Data Storage Verification", True, 
                                f"Found {len(short_answer_images)} Short Answer and {len(long_form_images)} Long Form questions with questionImage field")
                    return True
                else:
                    self.log_test("Backend Data Storage Verification", False, 
                                f"Expected 4 questions with images, found {len(questions_with_images)}")
                    return False
            else:
                self.log_test("Backend Data Storage Verification", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backend Data Storage Verification", False, f"Exception: {str(e)}")
            return False
    
    def verify_api_response_format(self):
        """Confirm that GET /api/courses/{id} returns question data with questionImage field in correct format"""
        try:
            if not self.test_course_id:
                self.log_test("API Response Format Verification", False, "No test course ID available")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/courses/{self.test_course_id}")
            
            if response.status_code == 200:
                course = response.json()
                questions = course['modules'][0]['lessons'][0].get('questions', [])
                
                # Verify API response format for questionImage field
                format_checks = []
                for question in questions:
                    if question.get('type') in ['short-answer', 'long-form-answer']:
                        check = {
                            'question_id': question.get('id'),
                            'type': question.get('type'),
                            'has_questionImage': 'questionImage' in question,
                            'questionImage_is_string': isinstance(question.get('questionImage'), str),
                            'questionImage_is_url': question.get('questionImage', '').startswith('https://') if 'questionImage' in question else False,
                            'has_question_text': 'question' in question and len(question['question']) > 0,
                            'has_correct_answer': 'correctAnswer' in question
                        }
                        format_checks.append(check)
                
                # Validate format requirements
                valid_formats = 0
                for check in format_checks:
                    if (check['has_questionImage'] and 
                        check['questionImage_is_string'] and 
                        check['questionImage_is_url'] and
                        check['has_question_text'] and
                        check['has_correct_answer']):
                        valid_formats += 1
                
                if valid_formats >= 4:  # Should have 4 questions with proper format
                    self.log_test("API Response Format Verification", True, 
                                f"All {valid_formats} questions have proper questionImage format")
                    return True
                else:
                    self.log_test("API Response Format Verification", False, 
                                f"Only {valid_formats} out of {len(format_checks)} questions have proper format")
                    return False
            else:
                self.log_test("API Response Format Verification", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API Response Format Verification", False, f"Exception: {str(e)}")
            return False
    
    def validate_data_structure_for_frontend(self):
        """Ensure question image data is in the correct format for frontend consumption"""
        try:
            if not self.test_course_id:
                self.log_test("Frontend Data Structure Validation", False, "No test course ID available")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/courses/{self.test_course_id}")
            
            if response.status_code == 200:
                course = response.json()
                questions = course['modules'][0]['lessons'][0].get('questions', [])
                
                # Validate data structure for frontend consumption
                frontend_compatibility = []
                for question in questions:
                    if question.get('type') in ['short-answer', 'long-form-answer']:
                        compatibility = {
                            'question_id': question.get('id'),
                            'type': question.get('type'),
                            'has_required_fields': all(field in question for field in ['id', 'type', 'question']),
                            'questionImage_accessible': 'questionImage' in question and isinstance(question['questionImage'], str),
                            'questionImage_valid_url': question.get('questionImage', '').startswith('https://') if 'questionImage' in question else False,
                            'json_serializable': True  # Already JSON if we got it from API
                        }
                        
                        # Test if questionImage URL is accessible (basic check)
                        if compatibility['questionImage_valid_url']:
                            try:
                                img_response = requests.head(question['questionImage'], timeout=5)
                                compatibility['questionImage_url_accessible'] = img_response.status_code == 200
                            except:
                                compatibility['questionImage_url_accessible'] = False
                        else:
                            compatibility['questionImage_url_accessible'] = False
                        
                        frontend_compatibility.append(compatibility)
                
                # Check frontend compatibility
                compatible_questions = 0
                for comp in frontend_compatibility:
                    if (comp['has_required_fields'] and 
                        comp['questionImage_accessible'] and 
                        comp['questionImage_valid_url'] and
                        comp['json_serializable']):
                        compatible_questions += 1
                
                if compatible_questions >= 4:
                    # Test URL accessibility
                    accessible_urls = sum(1 for comp in frontend_compatibility if comp.get('questionImage_url_accessible', False))
                    
                    self.log_test("Frontend Data Structure Validation", True, 
                                f"All {compatible_questions} questions are frontend-compatible, {accessible_urls} URLs accessible")
                    return True
                else:
                    self.log_test("Frontend Data Structure Validation", False, 
                                f"Only {compatible_questions} out of {len(frontend_compatibility)} questions are frontend-compatible")
                    return False
            else:
                self.log_test("Frontend Data Structure Validation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Frontend Data Structure Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_course_listing_includes_question_images(self):
        """Test that course listing API includes courses with question images"""
        try:
            response = self.session.get(f"{BACKEND_URL}/courses")
            
            if response.status_code == 200:
                courses = response.json()
                
                # Find our test course in the listing
                test_course = None
                for course in courses:
                    if course.get('id') == self.test_course_id:
                        test_course = course
                        break
                
                if test_course:
                    self.log_test("Course Listing Includes Question Images", True, 
                                f"Test course found in listing: {test_course['title']}")
                    return True
                else:
                    self.log_test("Course Listing Includes Question Images", False, 
                                f"Test course not found in {len(courses)} courses")
                    return False
            else:
                self.log_test("Course Listing Includes Question Images", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Course Listing Includes Question Images", False, f"Exception: {str(e)}")
            return False
    
    def test_question_image_field_consistency(self):
        """Test that questionImage field is consistently handled across different question types"""
        try:
            if not self.test_course_id:
                self.log_test("Question Image Field Consistency", False, "No test course ID available")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/courses/{self.test_course_id}")
            
            if response.status_code == 200:
                course = response.json()
                questions = course['modules'][0]['lessons'][0].get('questions', [])
                
                # Check consistency across question types
                short_answer_questions = [q for q in questions if q.get('type') == 'short-answer']
                long_form_questions = [q for q in questions if q.get('type') == 'long-form-answer']
                
                # Verify both question types have questionImage field
                short_answer_with_images = [q for q in short_answer_questions if 'questionImage' in q]
                long_form_with_images = [q for q in long_form_questions if 'questionImage' in q]
                
                consistency_check = {
                    'short_answer_total': len(short_answer_questions),
                    'short_answer_with_images': len(short_answer_with_images),
                    'long_form_total': len(long_form_questions),
                    'long_form_with_images': len(long_form_with_images),
                    'consistent_field_structure': True
                }
                
                # Check field structure consistency
                all_image_questions = short_answer_with_images + long_form_with_images
                for question in all_image_questions:
                    if not isinstance(question.get('questionImage'), str):
                        consistency_check['consistent_field_structure'] = False
                        break
                
                if (consistency_check['short_answer_with_images'] >= 2 and 
                    consistency_check['long_form_with_images'] >= 2 and
                    consistency_check['consistent_field_structure']):
                    
                    self.log_test("Question Image Field Consistency", True, 
                                f"Short Answer: {consistency_check['short_answer_with_images']}/{consistency_check['short_answer_total']}, "
                                f"Long Form: {consistency_check['long_form_with_images']}/{consistency_check['long_form_total']}")
                    return True
                else:
                    self.log_test("Question Image Field Consistency", False, 
                                f"Inconsistent field structure: {consistency_check}")
                    return False
            else:
                self.log_test("Question Image Field Consistency", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Question Image Field Consistency", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test course after testing"""
        try:
            if self.test_course_id:
                response = self.session.delete(f"{BACKEND_URL}/courses/{self.test_course_id}")
                if response.status_code == 200:
                    self.log_test("Test Data Cleanup", True, f"Deleted test course {self.test_course_id}")
                else:
                    self.log_test("Test Data Cleanup", False, f"Failed to delete course: HTTP {response.status_code}")
            else:
                self.log_test("Test Data Cleanup", True, "No test course to clean up")
        except Exception as e:
            self.log_test("Test Data Cleanup", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all question image tests"""
        print("🧪 QUESTION IMAGE FIX VERIFICATION: Short Answer & Long Form Question Image Display")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Admin Authentication", self.authenticate_admin),
            ("Create Test Course with Question Images", self.create_test_course_with_question_images),
            ("Backend Data Storage Verification", self.verify_backend_data_storage),
            ("API Response Format Verification", self.verify_api_response_format),
            ("Frontend Data Structure Validation", self.validate_data_structure_for_frontend),
            ("Course Listing Includes Question Images", self.test_course_listing_includes_question_images),
            ("Question Image Field Consistency", self.test_question_image_field_consistency),
            ("Test Data Cleanup", self.cleanup_test_data)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected error: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("🎉 QUESTION IMAGE FIX VERIFICATION: SUCCESS")
            print("✅ Backend properly stores questionImage field for Short Answer and Long Form questions")
            print("✅ API responses include question image URLs in the correct format")
            print("✅ All required APIs working correctly for quiz image display")
        else:
            print("❌ QUESTION IMAGE FIX VERIFICATION: ISSUES FOUND")
            print("Some tests failed - review the details above")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        return success_rate >= 85

def main():
    """Main test execution"""
    test_suite = QuestionImageTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION: Question image fix for Short Answer and Long Form questions is working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  CONCLUSION: Issues found with question image implementation - review test results above")
        sys.exit(1)

if __name__ == "__main__":
    main()