#!/usr/bin/env python3

"""
Learning Outcomes Backend Testing Script
========================================

This script tests the "What You'll Learn" (learning outcomes) functionality 
in the course creation system as requested in the review.

Test Coverage:
1. Course Creation with Learning Outcomes - Test POST /api/courses endpoint with learningOutcomes array
2. Course Retrieval - Test GET /api/courses/{id} to verify learning outcomes are returned
3. Course Update - Test PUT /api/courses/{id} to update learning outcomes
4. Learning Outcomes Data Structure - Verify the learningOutcomes field is properly handled and stored

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

# Test data for learning outcomes
SAMPLE_LEARNING_OUTCOMES = [
    "Master the fundamentals and advanced concepts",
    "Build real-world projects from scratch", 
    "Best practices and industry standards",
    "Prepare for professional opportunities"
]

UPDATED_LEARNING_OUTCOMES = [
    "Understand core principles and methodologies",
    "Apply knowledge to practical scenarios",
    "Develop critical thinking and problem-solving skills",
    "Gain industry-relevant expertise",
    "Build a portfolio of completed projects"
]

class LearningOutcomesBackendTester:
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
        print()
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 AUTHENTICATING AS ADMIN...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                
                user_info = data.get('user', {})
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
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_course_creation_with_learning_outcomes(self):
        """Test POST /api/courses endpoint with learningOutcomes array"""
        print("📚 TESTING COURSE CREATION WITH LEARNING OUTCOMES...")
        
        course_data = {
            "title": "Learning Outcomes Test Course",
            "description": "A comprehensive course to test learning outcomes functionality",
            "category": "Technology",
            "duration": "8 weeks",
            "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
            "accessType": "open",
            "learningOutcomes": SAMPLE_LEARNING_OUTCOMES,
            "modules": [
                {
                    "title": "Introduction Module",
                    "lessons": [
                        {
                            "id": "lesson-1",
                            "title": "Getting Started",
                            "type": "text",
                            "content": "Welcome to the course!"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                self.test_course_id = course.get('id')
                
                # Verify learning outcomes are in response
                returned_outcomes = course.get('learningOutcomes', [])
                
                if returned_outcomes == SAMPLE_LEARNING_OUTCOMES:
                    self.log_test(
                        "Course Creation with Learning Outcomes", 
                        True, 
                        f"Course created successfully with {len(returned_outcomes)} learning outcomes. Course ID: {self.test_course_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Course Creation with Learning Outcomes", 
                        False, 
                        f"Learning outcomes mismatch. Expected: {SAMPLE_LEARNING_OUTCOMES}, Got: {returned_outcomes}"
                    )
                    return False
            else:
                self.log_test(
                    "Course Creation with Learning Outcomes", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Course Creation with Learning Outcomes", False, f"Exception: {str(e)}")
            return False
    
    def test_course_retrieval_with_learning_outcomes(self):
        """Test GET /api/courses/{id} to verify learning outcomes are returned"""
        print("🔍 TESTING COURSE RETRIEVAL WITH LEARNING OUTCOMES...")
        
        if not self.test_course_id:
            self.log_test("Course Retrieval with Learning Outcomes", False, "No test course ID available")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/courses/{self.test_course_id}")
            
            if response.status_code == 200:
                course = response.json()
                returned_outcomes = course.get('learningOutcomes', [])
                
                if returned_outcomes == SAMPLE_LEARNING_OUTCOMES:
                    self.log_test(
                        "Course Retrieval with Learning Outcomes", 
                        True, 
                        f"Successfully retrieved course with {len(returned_outcomes)} learning outcomes intact"
                    )
                    
                    # Verify each learning outcome
                    print("   Learning Outcomes Retrieved:")
                    for i, outcome in enumerate(returned_outcomes, 1):
                        print(f"   {i}. {outcome}")
                    
                    return True
                else:
                    self.log_test(
                        "Course Retrieval with Learning Outcomes", 
                        False, 
                        f"Learning outcomes mismatch. Expected: {SAMPLE_LEARNING_OUTCOMES}, Got: {returned_outcomes}"
                    )
                    return False
            else:
                self.log_test(
                    "Course Retrieval with Learning Outcomes", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Course Retrieval with Learning Outcomes", False, f"Exception: {str(e)}")
            return False
    
    def test_course_update_with_learning_outcomes(self):
        """Test PUT /api/courses/{id} to update learning outcomes"""
        print("✏️ TESTING COURSE UPDATE WITH LEARNING OUTCOMES...")
        
        if not self.test_course_id:
            self.log_test("Course Update with Learning Outcomes", False, "No test course ID available")
            return False
        
        update_data = {
            "title": "Updated Learning Outcomes Test Course",
            "description": "An updated course to test learning outcomes modification",
            "category": "Technology",
            "duration": "10 weeks",
            "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
            "accessType": "open",
            "learningOutcomes": UPDATED_LEARNING_OUTCOMES,
            "modules": [
                {
                    "title": "Updated Introduction Module",
                    "lessons": [
                        {
                            "id": "lesson-1",
                            "title": "Getting Started - Updated",
                            "type": "text",
                            "content": "Welcome to the updated course!"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = self.session.put(f"{BACKEND_URL}/courses/{self.test_course_id}", json=update_data)
            
            if response.status_code == 200:
                course = response.json()
                returned_outcomes = course.get('learningOutcomes', [])
                
                if returned_outcomes == UPDATED_LEARNING_OUTCOMES:
                    self.log_test(
                        "Course Update with Learning Outcomes", 
                        True, 
                        f"Successfully updated course with {len(returned_outcomes)} new learning outcomes"
                    )
                    
                    # Verify each updated learning outcome
                    print("   Updated Learning Outcomes:")
                    for i, outcome in enumerate(returned_outcomes, 1):
                        print(f"   {i}. {outcome}")
                    
                    return True
                else:
                    self.log_test(
                        "Course Update with Learning Outcomes", 
                        False, 
                        f"Learning outcomes mismatch after update. Expected: {UPDATED_LEARNING_OUTCOMES}, Got: {returned_outcomes}"
                    )
                    return False
            else:
                self.log_test(
                    "Course Update with Learning Outcomes", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Course Update with Learning Outcomes", False, f"Exception: {str(e)}")
            return False
    
    def test_learning_outcomes_data_structure(self):
        """Verify the learningOutcomes field is properly handled and stored"""
        print("🔬 TESTING LEARNING OUTCOMES DATA STRUCTURE...")
        
        if not self.test_course_id:
            self.log_test("Learning Outcomes Data Structure", False, "No test course ID available")
            return False
        
        try:
            # Get the course again to verify data structure
            response = self.session.get(f"{BACKEND_URL}/courses/{self.test_course_id}")
            
            if response.status_code == 200:
                course = response.json()
                
                # Check if learningOutcomes field exists
                if 'learningOutcomes' not in course:
                    self.log_test(
                        "Learning Outcomes Data Structure", 
                        False, 
                        "learningOutcomes field missing from course response"
                    )
                    return False
                
                learning_outcomes = course.get('learningOutcomes')
                
                # Verify it's a list
                if not isinstance(learning_outcomes, list):
                    self.log_test(
                        "Learning Outcomes Data Structure", 
                        False, 
                        f"learningOutcomes should be a list, got {type(learning_outcomes)}"
                    )
                    return False
                
                # Verify all items are strings
                for i, outcome in enumerate(learning_outcomes):
                    if not isinstance(outcome, str):
                        self.log_test(
                            "Learning Outcomes Data Structure", 
                            False, 
                            f"Learning outcome {i+1} should be a string, got {type(outcome)}"
                        )
                        return False
                
                # Verify the content matches what we expect
                if learning_outcomes == UPDATED_LEARNING_OUTCOMES:
                    self.log_test(
                        "Learning Outcomes Data Structure", 
                        True, 
                        f"Data structure is correct: List of {len(learning_outcomes)} strings, properly stored and retrieved"
                    )
                    return True
                else:
                    self.log_test(
                        "Learning Outcomes Data Structure", 
                        False, 
                        f"Content mismatch. Expected: {UPDATED_LEARNING_OUTCOMES}, Got: {learning_outcomes}"
                    )
                    return False
            else:
                self.log_test(
                    "Learning Outcomes Data Structure", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Learning Outcomes Data Structure", False, f"Exception: {str(e)}")
            return False
    
    def test_empty_learning_outcomes(self):
        """Test course creation with empty learning outcomes array"""
        print("📝 TESTING EMPTY LEARNING OUTCOMES ARRAY...")
        
        course_data = {
            "title": "Empty Learning Outcomes Test Course",
            "description": "A course to test empty learning outcomes handling",
            "category": "Technology",
            "duration": "4 weeks",
            "accessType": "open",
            "learningOutcomes": [],  # Empty array
            "modules": []
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                returned_outcomes = course.get('learningOutcomes', [])
                
                if returned_outcomes == []:
                    self.log_test(
                        "Empty Learning Outcomes Array", 
                        True, 
                        "Successfully handled empty learning outcomes array"
                    )
                    
                    # Clean up this test course
                    test_course_id = course.get('id')
                    if test_course_id:
                        self.session.delete(f"{BACKEND_URL}/courses/{test_course_id}")
                    
                    return True
                else:
                    self.log_test(
                        "Empty Learning Outcomes Array", 
                        False, 
                        f"Expected empty array, got: {returned_outcomes}"
                    )
                    return False
            else:
                self.log_test(
                    "Empty Learning Outcomes Array", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Empty Learning Outcomes Array", False, f"Exception: {str(e)}")
            return False
    
    def test_course_listing_with_learning_outcomes(self):
        """Test GET /api/courses to verify learning outcomes are included in course listings"""
        print("📋 TESTING COURSE LISTING WITH LEARNING OUTCOMES...")
        
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
                    returned_outcomes = test_course.get('learningOutcomes', [])
                    
                    if returned_outcomes == UPDATED_LEARNING_OUTCOMES:
                        self.log_test(
                            "Course Listing with Learning Outcomes", 
                            True, 
                            f"Learning outcomes properly included in course listings ({len(returned_outcomes)} outcomes)"
                        )
                        return True
                    else:
                        self.log_test(
                            "Course Listing with Learning Outcomes", 
                            False, 
                            f"Learning outcomes mismatch in listing. Expected: {UPDATED_LEARNING_OUTCOMES}, Got: {returned_outcomes}"
                        )
                        return False
                else:
                    self.log_test(
                        "Course Listing with Learning Outcomes", 
                        False, 
                        f"Test course {self.test_course_id} not found in course listing"
                    )
                    return False
            else:
                self.log_test(
                    "Course Listing with Learning Outcomes", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Course Listing with Learning Outcomes", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_course(self):
        """Clean up the test course"""
        print("🧹 CLEANING UP TEST COURSE...")
        
        if not self.test_course_id:
            print("   No test course to clean up")
            return
        
        try:
            response = self.session.delete(f"{BACKEND_URL}/courses/{self.test_course_id}")
            
            if response.status_code == 200:
                print(f"   ✅ Successfully deleted test course {self.test_course_id}")
            else:
                print(f"   ⚠️ Failed to delete test course: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Exception during cleanup: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 LEARNING OUTCOMES BACKEND TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}")
        
        print("\n" + "="*80)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Learning outcomes functionality is working correctly!")
        elif success_rate >= 75:
            print("✅ GOOD: Most learning outcomes functionality is working with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Learning outcomes functionality has significant issues")
        else:
            print("❌ CRITICAL: Learning outcomes functionality is not working properly")
        
        print("="*80)
    
    def run_all_tests(self):
        """Run all learning outcomes tests"""
        print("🚀 STARTING LEARNING OUTCOMES BACKEND TESTING")
        print("="*80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL} / {'*' * len(ADMIN_PASSWORD)}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test course creation with learning outcomes
        self.test_course_creation_with_learning_outcomes()
        
        # Step 3: Test course retrieval with learning outcomes
        self.test_course_retrieval_with_learning_outcomes()
        
        # Step 4: Test course update with learning outcomes
        self.test_course_update_with_learning_outcomes()
        
        # Step 5: Test learning outcomes data structure
        self.test_learning_outcomes_data_structure()
        
        # Step 6: Test empty learning outcomes
        self.test_empty_learning_outcomes()
        
        # Step 7: Test course listing with learning outcomes
        self.test_course_listing_with_learning_outcomes()
        
        # Step 8: Cleanup
        self.cleanup_test_course()
        
        # Step 9: Print summary
        self.print_summary()
        
        return True

def main():
    """Main function"""
    tester = LearningOutcomesBackendTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        tester.cleanup_test_course()
        return 1
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        tester.cleanup_test_course()
        return 1

if __name__ == "__main__":
    sys.exit(main())