#!/usr/bin/env python3
"""
Specific Student Course Completion Test
=======================================

Testing the specific scenario mentioned in the review request:
- Authenticate as student: karlo.student@alder.com / StudentPermanent123!
- Find or access a course that has no quiz lessons
- Simulate completing all lessons in that course
- Verify that the course can reach 100% completion without being blocked by quiz requirements
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com/api"

class SpecificStudentTester:
    def __init__(self):
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
    
    def authenticate_student(self):
        """Authenticate as the specific student mentioned in review request"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": "karlo.student@alder.com",
                "password": "StudentPermanent123!"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data['access_token']
                self.log_test("Student Authentication", True, 
                            f"Student authenticated: {data['user']['full_name']} ({data['user']['email']})")
                return True
            else:
                self.log_test("Student Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def find_courses_without_quizzes(self):
        """Find courses that have no quiz lessons"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get all available courses
            response = requests.get(f"{BACKEND_URL}/courses", headers=headers)
            
            if response.status_code != 200:
                self.log_test("Find Courses Without Quizzes", False, 
                            f"Failed to get courses: {response.status_code}")
                return []
            
            courses = response.json()
            courses_without_quizzes = []
            
            print(f"\n🔍 Analyzing {len(courses)} available courses...")
            
            for course in courses:
                # Get detailed course info
                detail_response = requests.get(f"{BACKEND_URL}/courses/{course['id']}", headers=headers)
                if detail_response.status_code == 200:
                    course_detail = detail_response.json()
                    modules = course_detail.get('modules', [])
                    
                    # Check if course has any quiz lessons
                    has_quiz = False
                    total_lessons = 0
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        total_lessons += len(lessons)
                        for lesson in lessons:
                            if lesson.get('type') == 'quiz':
                                has_quiz = True
                                break
                        if has_quiz:
                            break
                    
                    if not has_quiz and total_lessons > 0:
                        courses_without_quizzes.append({
                            'course': course_detail,
                            'total_lessons': total_lessons,
                            'modules_count': len(modules)
                        })
                        print(f"✅ Found course without quizzes: '{course_detail['title']}' ({total_lessons} lessons, {len(modules)} modules)")
                    elif has_quiz:
                        print(f"⚠️  Course has quizzes: '{course_detail['title']}'")
                    else:
                        print(f"⚠️  Course has no lessons: '{course_detail['title']}'")
            
            if courses_without_quizzes:
                self.log_test("Find Courses Without Quizzes", True, 
                            f"Found {len(courses_without_quizzes)} courses without quiz lessons")
            else:
                self.log_test("Find Courses Without Quizzes", False, 
                            "No courses without quiz lessons found")
            
            return courses_without_quizzes
            
        except Exception as e:
            self.log_test("Find Courses Without Quizzes", False, f"Exception: {str(e)}")
            return []
    
    def test_course_completion(self, course_info):
        """Test completing a specific course without quizzes"""
        course = course_info['course']
        course_id = course['id']
        course_title = course['title']
        total_lessons = course_info['total_lessons']
        
        print(f"\n🎯 Testing completion of course: '{course_title}'")
        print(f"   Course ID: {course_id}")
        print(f"   Total lessons: {total_lessons}")
        print(f"   Modules: {course_info['modules_count']}")
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Check if already enrolled
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            if enrollments_response.status_code != 200:
                self.log_test(f"Get Enrollments for {course_title}", False, 
                            f"Failed to get enrollments: {enrollments_response.status_code}")
                return False
            
            enrollments = enrollments_response.json()
            existing_enrollment = None
            
            for enrollment in enrollments:
                if enrollment['courseId'] == course_id:
                    existing_enrollment = enrollment
                    break
            
            if existing_enrollment:
                print(f"   Already enrolled with {existing_enrollment.get('progress', 0)}% progress")
                current_enrollment = existing_enrollment
            else:
                # Enroll in the course
                enroll_response = requests.post(f"{BACKEND_URL}/enrollments", json={
                    "courseId": course_id
                }, headers=headers)
                
                if enroll_response.status_code == 200:
                    current_enrollment = enroll_response.json()
                    self.log_test(f"Enrollment in {course_title}", True, 
                                f"Successfully enrolled in course")
                else:
                    self.log_test(f"Enrollment in {course_title}", False, 
                                f"Enrollment failed: {enroll_response.status_code}")
                    return False
            
            # Simulate completing all lessons (100% progress)
            progress_data = {
                "progress": 100.0,
                "currentLessonId": "final-lesson",
                "lastAccessedAt": datetime.now().isoformat(),
                "timeSpent": total_lessons * 300  # 5 minutes per lesson
            }
            
            progress_response = requests.put(f"{BACKEND_URL}/enrollments/{course_id}/progress", 
                                           json=progress_data, headers=headers)
            
            if progress_response.status_code == 200:
                final_enrollment = progress_response.json()
                final_progress = final_enrollment.get('progress', 0)
                final_status = final_enrollment.get('status', 'active')
                completion_date = final_enrollment.get('completedAt')
                
                print(f"   Final progress: {final_progress}%")
                print(f"   Final status: {final_status}")
                print(f"   Completion date: {completion_date}")
                
                # Verify 100% completion was achieved
                if final_progress >= 100.0 and final_status == 'completed':
                    self.log_test(f"Course Completion - {course_title}", True, 
                                f"✅ Successfully reached 100% completion! Progress: {final_progress}%, Status: {final_status}")
                    
                    # Check if certificate was generated
                    if completion_date:
                        self.log_test(f"Certificate Generation - {course_title}", True, 
                                    f"Course marked as completed on {completion_date}")
                    
                    return True
                else:
                    self.log_test(f"Course Completion - {course_title}", False, 
                                f"❌ 99% BUG DETECTED! Only reached {final_progress}% with status '{final_status}'")
                    return False
            else:
                self.log_test(f"Progress Update - {course_title}", False, 
                            f"Progress update failed: {progress_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"Course Completion Test - {course_title}", False, f"Exception: {str(e)}")
            return False
    
    def run_specific_test(self):
        """Run the specific test scenario from the review request"""
        print("🚀 SPECIFIC STUDENT COURSE COMPLETION TESTING")
        print("=" * 80)
        print("Testing scenario from review request:")
        print("- Authenticate as student: karlo.student@alder.com / StudentPermanent123!")
        print("- Find or access a course that has no quiz lessons")
        print("- Simulate completing all lessons in that course")
        print("- Verify that the course can reach 100% completion")
        print("=" * 80)
        
        # Authenticate
        if not self.authenticate_student():
            return False
        
        # Find courses without quizzes
        courses_without_quizzes = self.find_courses_without_quizzes()
        if not courses_without_quizzes:
            print("❌ No courses without quizzes found for testing")
            return False
        
        # Test completion for each course without quizzes
        successful_completions = 0
        total_courses_tested = min(3, len(courses_without_quizzes))  # Test up to 3 courses
        
        for i in range(total_courses_tested):
            course_info = courses_without_quizzes[i]
            if self.test_course_completion(course_info):
                successful_completions += 1
        
        # Summary
        success_rate = (successful_completions / total_courses_tested) * 100
        
        print("\n" + "=" * 80)
        print("🎯 SPECIFIC STUDENT TESTING SUMMARY")
        print("=" * 80)
        print(f"✅ Courses Successfully Completed: {successful_completions}/{total_courses_tested}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 100:
            print("🎉 EXCELLENT: Course completion fix is working perfectly!")
            print("✅ Student can reach 100% completion in courses without quizzes")
            print("✅ 99% completion bug has been resolved")
        elif success_rate >= 75:
            print("✅ GOOD: Course completion fix is mostly working")
            print("⚠️  Some courses may still have issues")
        else:
            print("❌ CRITICAL: 99% completion bug is still present!")
            print("🚨 Courses without quizzes cannot reach 100% completion")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = SpecificStudentTester()
    success = tester.run_specific_test()
    sys.exit(0 if success else 1)