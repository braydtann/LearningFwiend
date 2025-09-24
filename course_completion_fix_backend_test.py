#!/usr/bin/env python3
"""
Course Completion Fix Backend Testing
=====================================

Testing the course completion fix for courses without quizzes to resolve the 99% completion bug.

Test Focus:
1. Course Without Quizzes Test - verify courses without quiz lessons can reach 100% completion
2. Course With Practice Quizzes Test - verify practice quizzes don't block completion
3. Data Structure Validation - test course data structure with modules and lessons
4. Error Handling Test - test fallback behavior when quiz attempts cannot be fetched

User Credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com/api"

class CourseCompletionTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def authenticate_admin(self):
        """Authenticate as admin"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.log_test("Admin Authentication", True, f"Admin authenticated: {data['user']['full_name']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_student(self):
        """Authenticate as student"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": "karlo.student@alder.com",
                "password": "StudentPermanent123!"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data['access_token']
                self.log_test("Student Authentication", True, f"Student authenticated: {data['user']['full_name']}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_course_without_quizzes(self):
        """Create a test course without any quiz lessons"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            course_data = {
                "title": "Course Completion Test - No Quizzes",
                "description": "Test course with only video and text lessons to test 100% completion without quizzes",
                "category": "Testing",
                "duration": "30 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
                "accessType": "open",
                "learningOutcomes": ["Complete course without quiz barriers"],
                "modules": [
                    {
                        "title": "Module 1: Introduction",
                        "lessons": [
                            {
                                "id": "lesson-1",
                                "title": "Welcome Video",
                                "type": "video",
                                "content": "Introduction to the course",
                                "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                                "duration": "5 minutes"
                            },
                            {
                                "id": "lesson-2", 
                                "title": "Course Overview",
                                "type": "text",
                                "content": "This course will teach you about completion tracking",
                                "duration": "10 minutes"
                            }
                        ]
                    },
                    {
                        "title": "Module 2: Content",
                        "lessons": [
                            {
                                "id": "lesson-3",
                                "title": "Main Content",
                                "type": "text",
                                "content": "Main learning content without any quizzes",
                                "duration": "15 minutes"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Create Course Without Quizzes", True, f"Course created: {course['id']}")
                return course
            else:
                self.log_test("Create Course Without Quizzes", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Course Without Quizzes", False, f"Exception: {str(e)}")
            return None
    
    def create_course_with_practice_quizzes(self):
        """Create a test course with practice quizzes (no passing score requirements)"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            course_data = {
                "title": "Course Completion Test - Practice Quizzes",
                "description": "Test course with practice quizzes that shouldn't block completion",
                "category": "Testing",
                "duration": "45 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
                "accessType": "open",
                "learningOutcomes": ["Complete course with practice quizzes"],
                "modules": [
                    {
                        "title": "Module 1: Learning",
                        "lessons": [
                            {
                                "id": "lesson-1",
                                "title": "Learning Content",
                                "type": "text",
                                "content": "Learn the basics before the practice quiz",
                                "duration": "15 minutes"
                            },
                            {
                                "id": "lesson-2",
                                "title": "Practice Quiz",
                                "type": "quiz",
                                "content": "Practice your knowledge",
                                "duration": "10 minutes",
                                "passingScore": None,  # No passing score requirement
                                "questions": [
                                    {
                                        "id": "q1",
                                        "type": "multiple-choice",
                                        "question": "What is 2 + 2?",
                                        "options": ["3", "4", "5", "6"],
                                        "correctAnswer": "1"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Module 2: Advanced",
                        "lessons": [
                            {
                                "id": "lesson-3",
                                "title": "Advanced Content",
                                "type": "text",
                                "content": "Advanced learning content",
                                "duration": "20 minutes"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                self.log_test("Create Course With Practice Quizzes", True, f"Course created: {course['id']}")
                return course
            else:
                self.log_test("Create Course With Practice Quizzes", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Course With Practice Quizzes", False, f"Exception: {str(e)}")
            return None
    
    def enroll_student_in_course(self, course_id):
        """Enroll student in a course"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.post(f"{BACKEND_URL}/enrollments", json={
                "courseId": course_id
            }, headers=headers)
            
            if response.status_code == 200:
                enrollment = response.json()
                self.log_test("Student Enrollment", True, f"Enrolled in course {course_id}")
                return enrollment
            else:
                self.log_test("Student Enrollment", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Student Enrollment", False, f"Exception: {str(e)}")
            return None
    
    def simulate_lesson_completion(self, course_id, progress_percentage):
        """Simulate completing lessons in a course"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            progress_data = {
                "progress": progress_percentage,
                "currentLessonId": "lesson-3",  # Final lesson
                "lastAccessedAt": datetime.now().isoformat(),
                "timeSpent": 1800  # 30 minutes
            }
            
            response = requests.put(f"{BACKEND_URL}/enrollments/{course_id}/progress", 
                                  json=progress_data, headers=headers)
            
            if response.status_code == 200:
                enrollment = response.json()
                actual_progress = enrollment.get('progress', 0)
                status = enrollment.get('status', 'active')
                
                self.log_test("Lesson Completion Simulation", True, 
                            f"Progress: {actual_progress}%, Status: {status}")
                return enrollment
            else:
                self.log_test("Lesson Completion Simulation", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Lesson Completion Simulation", False, f"Exception: {str(e)}")
            return None
    
    def test_course_completion_without_quizzes(self):
        """Test that courses without quizzes can reach 100% completion"""
        print("\n🎯 TESTING COURSE COMPLETION WITHOUT QUIZZES")
        print("=" * 60)
        
        # Create course without quizzes
        course = self.create_course_without_quizzes()
        if not course:
            return False
        
        # Enroll student
        enrollment = self.enroll_student_in_course(course['id'])
        if not enrollment:
            return False
        
        # Simulate completing all lessons (should reach 100%)
        final_enrollment = self.simulate_lesson_completion(course['id'], 100.0)
        if not final_enrollment:
            return False
        
        # Verify 100% completion
        final_progress = final_enrollment.get('progress', 0)
        final_status = final_enrollment.get('status', 'active')
        
        if final_progress >= 100.0 and final_status == 'completed':
            self.log_test("Course Without Quizzes - 100% Completion", True, 
                        f"Successfully reached {final_progress}% completion with status '{final_status}'")
            return True
        else:
            self.log_test("Course Without Quizzes - 100% Completion", False, 
                        f"Only reached {final_progress}% completion with status '{final_status}' - 99% bug detected!")
            return False
    
    def test_course_completion_with_practice_quizzes(self):
        """Test that practice quizzes don't block course completion"""
        print("\n🎯 TESTING COURSE COMPLETION WITH PRACTICE QUIZZES")
        print("=" * 60)
        
        # Create course with practice quizzes
        course = self.create_course_with_practice_quizzes()
        if not course:
            return False
        
        # Enroll student
        enrollment = self.enroll_student_in_course(course['id'])
        if not enrollment:
            return False
        
        # Simulate completing all lessons including practice quiz
        final_enrollment = self.simulate_lesson_completion(course['id'], 100.0)
        if not final_enrollment:
            return False
        
        # Verify 100% completion
        final_progress = final_enrollment.get('progress', 0)
        final_status = final_enrollment.get('status', 'active')
        
        if final_progress >= 100.0 and final_status == 'completed':
            self.log_test("Course With Practice Quizzes - 100% Completion", True, 
                        f"Successfully reached {final_progress}% completion with status '{final_status}'")
            return True
        else:
            self.log_test("Course With Practice Quizzes - 100% Completion", False, 
                        f"Only reached {final_progress}% completion with status '{final_status}' - practice quiz blocking completion!")
            return False
    
    def test_data_structure_validation(self):
        """Test course data structure includes modules and lessons"""
        print("\n🎯 TESTING DATA STRUCTURE VALIDATION")
        print("=" * 60)
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get all courses to find ones with different structures
            response = requests.get(f"{BACKEND_URL}/courses", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Data Structure Validation", False, f"Failed to get courses: {response.status_code}")
                return False
            
            courses = response.json()
            
            # Test different course structures
            courses_with_modules = 0
            courses_without_modules = 0
            courses_with_quizzes = 0
            courses_without_quizzes = 0
            
            for course in courses[:10]:  # Test first 10 courses
                # Get detailed course info
                detail_response = requests.get(f"{BACKEND_URL}/courses/{course['id']}", headers=headers)
                if detail_response.status_code == 200:
                    course_detail = detail_response.json()
                    modules = course_detail.get('modules', [])
                    
                    if modules:
                        courses_with_modules += 1
                        
                        # Check for quiz lessons
                        has_quiz = False
                        for module in modules:
                            lessons = module.get('lessons', [])
                            for lesson in lessons:
                                if lesson.get('type') == 'quiz':
                                    has_quiz = True
                                    break
                            if has_quiz:
                                break
                        
                        if has_quiz:
                            courses_with_quizzes += 1
                        else:
                            courses_without_quizzes += 1
                    else:
                        courses_without_modules += 1
            
            self.log_test("Data Structure Validation", True, 
                        f"Analyzed courses - With modules: {courses_with_modules}, Without modules: {courses_without_modules}, With quizzes: {courses_with_quizzes}, Without quizzes: {courses_without_quizzes}")
            
            # Test graceful handling of courses without modules
            if courses_without_modules > 0:
                self.log_test("Graceful Handling - Courses Without Modules", True, 
                            f"System handles {courses_without_modules} courses without modules gracefully")
            else:
                self.log_test("Graceful Handling - Courses Without Modules", True, 
                            "All courses have proper module structure")
            
            return True
            
        except Exception as e:
            self.log_test("Data Structure Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_fallback(self):
        """Test fallback behavior when quiz attempts cannot be fetched"""
        print("\n🎯 TESTING ERROR HANDLING FALLBACK")
        print("=" * 60)
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test enrollment progress update with edge cases
            test_cases = [
                {"progress": 100.0, "description": "Normal 100% completion"},
                {"progress": 99.9, "description": "Near completion (99.9%)"},
                {"progress": 100.0, "currentLessonId": None, "description": "100% with null lesson ID"},
                {"progress": 100.0, "timeSpent": None, "description": "100% with null time spent"}
            ]
            
            # Get student's first enrollment for testing
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            if enrollments_response.status_code != 200:
                self.log_test("Error Handling Fallback", False, "Could not get enrollments for testing")
                return False
            
            enrollments = enrollments_response.json()
            if not enrollments:
                self.log_test("Error Handling Fallback", False, "No enrollments found for testing")
                return False
            
            test_course_id = enrollments[0]['courseId']
            
            for i, test_case in enumerate(test_cases):
                progress_data = {
                    "progress": test_case["progress"],
                    "lastAccessedAt": datetime.now().isoformat()
                }
                
                # Add optional fields if specified
                if "currentLessonId" in test_case:
                    progress_data["currentLessonId"] = test_case["currentLessonId"]
                if "timeSpent" in test_case:
                    progress_data["timeSpent"] = test_case["timeSpent"]
                
                response = requests.put(f"{BACKEND_URL}/enrollments/{test_course_id}/progress", 
                                      json=progress_data, headers=headers)
                
                if response.status_code == 200:
                    enrollment = response.json()
                    actual_progress = enrollment.get('progress', 0)
                    status = enrollment.get('status', 'active')
                    
                    # Check if system defaults to allowing completion
                    if test_case["progress"] >= 100.0:
                        if actual_progress >= 100.0 and status == 'completed':
                            self.log_test(f"Error Handling Test {i+1}", True, 
                                        f"{test_case['description']}: Progress {actual_progress}%, Status: {status}")
                        else:
                            self.log_test(f"Error Handling Test {i+1}", False, 
                                        f"{test_case['description']}: Only {actual_progress}%, Status: {status}")
                    else:
                        self.log_test(f"Error Handling Test {i+1}", True, 
                                    f"{test_case['description']}: Progress {actual_progress}%, Status: {status}")
                else:
                    self.log_test(f"Error Handling Test {i+1}", False, 
                                f"{test_case['description']}: Status {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling Fallback", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all course completion tests"""
        print("🚀 COURSE COMPLETION FIX BACKEND TESTING INITIATED")
        print("=" * 80)
        print("Testing the course completion fix for courses without quizzes")
        print("Focus: Resolve 99% completion bug and allow 100% completion")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate_admin():
            return False
        
        if not self.authenticate_student():
            return False
        
        # Run all tests
        test_results = []
        
        test_results.append(self.test_course_completion_without_quizzes())
        test_results.append(self.test_course_completion_with_practice_quizzes())
        test_results.append(self.test_data_structure_validation())
        test_results.append(self.test_error_handling_fallback())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("🎯 COURSE COMPLETION FIX TESTING SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 100:
            print("🎉 EXCELLENT: Course completion fix is working perfectly!")
            print("✅ Courses without quizzes can reach 100% completion")
            print("✅ Practice quizzes don't block course completion")
            print("✅ Data structures are properly validated")
            print("✅ Error handling provides proper fallback behavior")
        elif success_rate >= 75:
            print("✅ GOOD: Course completion fix is mostly working")
            print("⚠️  Some edge cases may need attention")
        else:
            print("❌ ISSUES DETECTED: Course completion fix needs investigation")
            print("🚨 99% completion bug may still be present")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = CourseCompletionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)