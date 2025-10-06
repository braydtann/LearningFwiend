#!/usr/bin/env python3
"""
Course Image Handling Test Suite for LearningFwiend LMS
Focus: Testing thumbnailUrl field handling in course management APIs
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class CourseImageTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        
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
        elif status == 'SKIP':
            print(f"⏭️  {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def authenticate_users(self):
        """Authenticate admin and instructor users"""
        # Admin login
        try:
            admin_login = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=admin_login,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['admin'] = data.get('access_token')
                print(f"✅ Admin authenticated: {data.get('user', {}).get('email')}")
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Admin authentication error: {e}")
        
        # Instructor login
        try:
            instructor_login = {
                "username_or_email": "instructor",
                "password": "Instructor123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=instructor_login,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['instructor'] = data.get('access_token')
                print(f"✅ Instructor authenticated: {data.get('user', {}).get('username')}")
            else:
                print(f"❌ Instructor authentication failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Instructor authentication error: {e}")
    
    def test_course_creation_with_thumbnailurl(self):
        """Test course creation API with thumbnailUrl field"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course Creation with ThumbnailUrl", 
                "SKIP", 
                "No instructor token available for course creation test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test course creation with thumbnailUrl field
            course_data = {
                "title": "Course Image Test - Creation",
                "description": "Testing course creation with thumbnailUrl field handling",
                "category": "Testing",
                "duration": "3 weeks",
                "thumbnailUrl": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Module 1: Image Testing",
                        "lessons": [
                            {
                                "title": "Lesson 1: Basic Image Handling",
                                "type": "text",
                                "content": "Testing image handling in courses"
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
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                returned_thumbnail = created_course.get('thumbnailUrl')
                
                # Verify thumbnailUrl field is properly stored and returned
                if returned_thumbnail == course_data['thumbnailUrl']:
                    self.log_result(
                        "Course Creation with ThumbnailUrl", 
                        "PASS", 
                        f"Successfully created course with thumbnailUrl field properly stored and returned",
                        f"Course ID: {course_id}, thumbnailUrl length: {len(returned_thumbnail)} chars"
                    )
                    return created_course
                else:
                    self.log_result(
                        "Course Creation with ThumbnailUrl", 
                        "FAIL", 
                        "ThumbnailUrl field not properly stored or returned",
                        f"Expected: {course_data['thumbnailUrl'][:50]}..., Got: {returned_thumbnail[:50] if returned_thumbnail else 'None'}..."
                    )
            else:
                self.log_result(
                    "Course Creation with ThumbnailUrl", 
                    "FAIL", 
                    f"Failed to create course with thumbnailUrl, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Creation with ThumbnailUrl", 
                "FAIL", 
                "Failed to test course creation with thumbnailUrl",
                str(e)
            )
        return False
    
    def test_course_retrieval_with_thumbnailurl(self):
        """Test course retrieval APIs return thumbnailUrl field correctly"""
        # First create a course with thumbnailUrl
        created_course = self.test_course_creation_with_thumbnailurl()
        if not created_course:
            self.log_result(
                "Course Retrieval with ThumbnailUrl", 
                "SKIP", 
                "Could not create test course for retrieval test",
                "Course creation required first"
            )
            return False
        
        course_id = created_course.get('id')
        expected_thumbnail = created_course.get('thumbnailUrl')
        
        try:
            # Test GET /api/courses/{course_id} - individual course retrieval
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                retrieved_course = response.json()
                returned_thumbnail = retrieved_course.get('thumbnailUrl')
                
                if returned_thumbnail == expected_thumbnail:
                    self.log_result(
                        "Course Retrieval with ThumbnailUrl", 
                        "PASS", 
                        f"Individual course retrieval correctly returns thumbnailUrl field",
                        f"Course ID: {course_id}, thumbnailUrl properly returned"
                    )
                    return True
                else:
                    self.log_result(
                        "Course Retrieval with ThumbnailUrl", 
                        "FAIL", 
                        "Individual course retrieval does not return correct thumbnailUrl",
                        f"Expected: {expected_thumbnail[:50] if expected_thumbnail else 'None'}..., Got: {returned_thumbnail[:50] if returned_thumbnail else 'None'}..."
                    )
            else:
                self.log_result(
                    "Course Retrieval with ThumbnailUrl", 
                    "FAIL", 
                    f"Failed to retrieve individual course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Retrieval with ThumbnailUrl", 
                "FAIL", 
                "Failed to test individual course retrieval with thumbnailUrl",
                str(e)
            )
        return False
    
    def test_course_listing_with_thumbnailurl(self):
        """Test course listing shows courses with proper thumbnail data"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course Listing with ThumbnailUrl", 
                "SKIP", 
                "No instructor token available for course listing test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test GET /api/courses - all courses listing
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                # Look for courses with thumbnailUrl field
                courses_with_thumbnails = []
                courses_without_thumbnails = []
                
                for course in courses:
                    if course.get('thumbnailUrl'):
                        courses_with_thumbnails.append(course)
                    else:
                        courses_without_thumbnails.append(course)
                
                self.log_result(
                    "Course Listing with ThumbnailUrl", 
                    "PASS", 
                    f"Course listing successfully returns thumbnailUrl field data",
                    f"Total courses: {len(courses)}, With thumbnails: {len(courses_with_thumbnails)}, Without thumbnails: {len(courses_without_thumbnails)}"
                )
                return True
            else:
                self.log_result(
                    "Course Listing with ThumbnailUrl", 
                    "FAIL", 
                    f"Failed to retrieve course listing, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Listing with ThumbnailUrl", 
                "FAIL", 
                "Failed to test course listing with thumbnailUrl",
                str(e)
            )
        return False
    
    def test_course_update_with_thumbnailurl(self):
        """Test course updating works with thumbnailUrl field"""
        # First create a course with thumbnailUrl
        created_course = self.test_course_creation_with_thumbnailurl()
        if not created_course:
            self.log_result(
                "Course Update with ThumbnailUrl", 
                "SKIP", 
                "Could not create test course for update test",
                "Course creation required first"
            )
            return False
        
        course_id = created_course.get('id')
        
        try:
            # Test updating course with new thumbnailUrl
            updated_course_data = {
                "title": "Course Image Test - Updated",
                "description": "Testing course update with thumbnailUrl field handling",
                "category": "Testing",
                "duration": "4 weeks",
                "thumbnailUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Module 1: Updated Image Testing",
                        "lessons": [
                            {
                                "title": "Lesson 1: Updated Image Handling",
                                "type": "text",
                                "content": "Testing updated image handling in courses"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.put(
                f"{BACKEND_URL}/courses/{course_id}",
                json=updated_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                updated_course = response.json()
                returned_thumbnail = updated_course.get('thumbnailUrl')
                
                # Verify thumbnailUrl field is properly updated
                if returned_thumbnail == updated_course_data['thumbnailUrl']:
                    self.log_result(
                        "Course Update with ThumbnailUrl", 
                        "PASS", 
                        f"Successfully updated course with new thumbnailUrl field",
                        f"Course ID: {course_id}, new thumbnailUrl properly stored and returned"
                    )
                    return True
                else:
                    self.log_result(
                        "Course Update with ThumbnailUrl", 
                        "FAIL", 
                        "ThumbnailUrl field not properly updated",
                        f"Expected: {updated_course_data['thumbnailUrl'][:50]}..., Got: {returned_thumbnail[:50] if returned_thumbnail else 'None'}..."
                    )
            else:
                self.log_result(
                    "Course Update with ThumbnailUrl", 
                    "FAIL", 
                    f"Failed to update course with thumbnailUrl, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Update with ThumbnailUrl", 
                "FAIL", 
                "Failed to test course update with thumbnailUrl",
                str(e)
            )
        return False
    
    def test_course_image_handling_comprehensive(self):
        """Comprehensive test of course image handling functionality"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course Image Handling Comprehensive", 
                "SKIP", 
                "No instructor token available for comprehensive image test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test 1: Create course with base64 image
            base64_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            
            course_data = {
                "title": "Comprehensive Image Test Course",
                "description": "Testing comprehensive course image handling",
                "category": "Testing",
                "duration": "1 week",
                "thumbnailUrl": base64_image,
                "accessType": "open"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result(
                    "Course Image Handling Comprehensive", 
                    "FAIL", 
                    f"Failed to create course with image, status: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
                return False
            
            created_course = create_response.json()
            course_id = created_course.get('id')
            
            # Test 2: Verify image in course listing
            listing_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if listing_response.status_code != 200:
                self.log_result(
                    "Course Image Handling Comprehensive", 
                    "FAIL", 
                    f"Failed to get course listing, status: {listing_response.status_code}",
                    f"Response: {listing_response.text}"
                )
                return False
            
            courses = listing_response.json()
            test_course_in_listing = None
            for course in courses:
                if course.get('id') == course_id:
                    test_course_in_listing = course
                    break
            
            if not test_course_in_listing or test_course_in_listing.get('thumbnailUrl') != base64_image:
                self.log_result(
                    "Course Image Handling Comprehensive", 
                    "FAIL", 
                    "Course image not properly displayed in course listing",
                    f"Course found in listing: {bool(test_course_in_listing)}, Image matches: {test_course_in_listing.get('thumbnailUrl') == base64_image if test_course_in_listing else False}"
                )
                return False
            
            # Test 3: Verify image in individual course retrieval
            detail_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if detail_response.status_code != 200:
                self.log_result(
                    "Course Image Handling Comprehensive", 
                    "FAIL", 
                    f"Failed to get course details, status: {detail_response.status_code}",
                    f"Response: {detail_response.text}"
                )
                return False
            
            course_details = detail_response.json()
            if course_details.get('thumbnailUrl') != base64_image:
                self.log_result(
                    "Course Image Handling Comprehensive", 
                    "FAIL", 
                    "Course image not properly returned in course details",
                    f"Expected image matches: {course_details.get('thumbnailUrl') == base64_image}"
                )
                return False
            
            # Test 4: Update course image
            new_image = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
            update_data = {
                "title": "Updated Comprehensive Image Test Course",
                "description": "Testing updated course image handling",
                "category": "Testing",
                "duration": "1 week",
                "thumbnailUrl": new_image,
                "accessType": "open"
            }
            
            update_response = requests.put(
                f"{BACKEND_URL}/courses/{course_id}",
                json=update_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if update_response.status_code != 200:
                self.log_result(
                    "Course Image Handling Comprehensive", 
                    "FAIL", 
                    f"Failed to update course image, status: {update_response.status_code}",
                    f"Response: {update_response.text}"
                )
                return False
            
            updated_course = update_response.json()
            if updated_course.get('thumbnailUrl') != new_image:
                self.log_result(
                    "Course Image Handling Comprehensive", 
                    "FAIL", 
                    "Course image not properly updated",
                    f"Updated image matches: {updated_course.get('thumbnailUrl') == new_image}"
                )
                return False
            
            self.log_result(
                "Course Image Handling Comprehensive", 
                "PASS", 
                "All course image handling functionality working correctly",
                f"✅ Create with image, ✅ List with image, ✅ Retrieve with image, ✅ Update image - Course ID: {course_id}"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Image Handling Comprehensive", 
                "FAIL", 
                "Failed to complete comprehensive course image test",
                str(e)
            )
        return False
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 COURSE IMAGE HANDLING TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"📈 TEST RESULTS:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        print()
        
        if self.results:
            print("🔍 DETAILED RESULTS:")
            for result in self.results:
                status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⏭️"
                print(f"   {status_icon} {result['test']}: {result['message']}")
        
        print()
        if self.failed == 0:
            print("🏆 OVERALL ASSESSMENT:")
            print("   🎉 EXCELLENT: All course image handling tests passed!")
            print("   ✅ ThumbnailUrl field handling is working correctly")
        else:
            print("🚨 CRITICAL ISSUES FOUND:")
            failed_tests = [r for r in self.results if r['status'] == 'FAIL']
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        print("=" * 80)
        return {
            'passed': self.passed,
            'failed': self.failed,
            'success_rate': success_rate,
            'results': self.results
        }
    
    def run_tests(self):
        """Run all course image handling tests"""
        print("🚀 Starting Course Image Handling Test Suite")
        print(f"🎯 Target: {BACKEND_URL}")
        print("📸 Focus: ThumbnailUrl field handling in course management APIs")
        print("=" * 80)
        
        # Authenticate users
        print("🔐 Authenticating users...")
        self.authenticate_users()
        
        if not self.auth_tokens:
            print("❌ No authentication tokens available - cannot run tests")
            return self.generate_summary()
        
        print("\n📸 COURSE IMAGE HANDLING TESTS")
        print("=" * 50)
        
        # Run course image tests
        self.test_course_creation_with_thumbnailurl()
        self.test_course_retrieval_with_thumbnailurl()
        self.test_course_listing_with_thumbnailurl()
        self.test_course_update_with_thumbnailurl()
        self.test_course_image_handling_comprehensive()
        
        return self.generate_summary()

if __name__ == "__main__":
    tester = CourseImageTester()
    results = tester.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)