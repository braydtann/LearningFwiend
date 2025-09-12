#!/usr/bin/env python3
"""
PROGRESS TRACKING BUG INVESTIGATION - BACKEND ENROLLMENT DATA ISSUE
LearningFwiend LMS Application Backend API Testing

CRITICAL BUG IDENTIFIED: Frontend console logs show that lessons are being marked complete correctly locally, 
but when backend returns updated enrollment data, the progress calculation is wrong.

INVESTIGATION NEEDED:
1. TEST lesson completion API calls and verify backend is storing moduleProgress correctly
2. CHECK if GET /api/enrollments returns complete moduleProgress data for all modules
3. VERIFY that PUT /api/enrollments/{id}/progress is properly updating and returning full enrollment data
4. ANALYZE if there's a data synchronization issue between local frontend state and backend database

SPECIFIC BUG SYMPTOMS:
- Frontend locally calculates: "Total lessons: 3, Completed: 2, Progress: 66.67%"
- Backend returns enrollment with progress still at 33.33%
- Console shows both modules have completed lessons but progress doesn't advance

TEST SCENARIO:
1. Login as progress.test@learningfwiend.com / ProgressTest123!
2. Complete first lesson (text) - should be 33%
3. Complete second lesson (video) - should be 66% 
4. Check what actual enrollment data is stored and returned by backend
5. Verify moduleProgress array contains all completed lessons across all modules
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

# Test credentials from review request
PROGRESS_TEST_CREDENTIALS = {
    "username_or_email": "progress.test@learningfwiend.com",
    "password": "ProgressTest123!"
}

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class ProgressTrackingTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.test_course_id = None
        self.test_enrollment_id = None
        
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
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Admin login failed - invalid token or role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
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
                "Admin login request failed",
                str(e)
            )
        return False
    
    def test_progress_student_login(self):
        """Test progress test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=PROGRESS_TEST_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token:
                    self.auth_tokens['progress_student'] = token
                    self.log_result(
                        "Progress Test Student Authentication", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Progress Test Student Authentication", 
                        "FAIL", 
                        "Student login failed - no token received",
                        f"Response data: {data}"
                    )
            else:
                self.log_result(
                    "Progress Test Student Authentication", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
                # If student doesn't exist, try to create it
                if response.status_code == 401:
                    print("🔧 Student doesn't exist or wrong password, attempting to create/reset...")
                    return self.create_or_reset_progress_student()
                    
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Progress Test Student Authentication", 
                "FAIL", 
                "Student login request failed",
                str(e)
            )
        return False
    
    def create_or_reset_progress_student(self):
        """Create or reset the progress test student"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Progress Test Student", 
                "FAIL", 
                "Cannot create student - no admin token",
                "Admin authentication required"
            )
            return False
        
        try:
            # First try to find existing user
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            existing_user = None
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    if user.get('email') == 'progress.test@learningfwiend.com':
                        existing_user = user
                        break
            
            if existing_user:
                # Reset password for existing user
                reset_data = {
                    "user_id": existing_user['id'],
                    "new_temporary_password": "ProgressTest123!"
                }
                
                reset_response = requests.post(
                    f"{BACKEND_URL}/auth/admin/reset-password",
                    json=reset_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if reset_response.status_code == 200:
                    print("✅ Password reset successful, retrying login...")
                    return self.test_progress_student_login()
                else:
                    self.log_result(
                        "Reset Progress Test Student Password", 
                        "FAIL", 
                        f"Password reset failed with status {reset_response.status_code}",
                        f"Response: {reset_response.text}"
                    )
            else:
                # Create new user
                user_data = {
                    "email": "progress.test@learningfwiend.com",
                    "username": "progress.test",
                    "full_name": "Progress Test Student",
                    "role": "learner",
                    "department": "Testing",
                    "temporary_password": "ProgressTest123!"
                }
                
                create_response = requests.post(
                    f"{BACKEND_URL}/auth/admin/create-user",
                    json=user_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if create_response.status_code == 200:
                    print("✅ Student created successfully, retrying login...")
                    return self.test_progress_student_login()
                else:
                    self.log_result(
                        "Create Progress Test Student", 
                        "FAIL", 
                        f"Student creation failed with status {create_response.status_code}",
                        f"Response: {create_response.text}"
                    )
                    
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Progress Test Student", 
                "FAIL", 
                "Failed to create/reset student",
                str(e)
            )
        return False
    
    def create_test_course_with_modules(self):
        """Create a test course with multiple modules and lessons for progress tracking"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Test Course", 
                "FAIL", 
                "Cannot create course - no admin token",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a course with 3 modules and 3 lessons total (33.33% per lesson)
            course_data = {
                "title": "Progress Tracking Test Course",
                "description": "Test course for investigating progress tracking bug",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 1 - Text Lesson",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Text Lesson 1",
                                "type": "text",
                                "content": "This is the first text lesson for progress tracking test."
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 2 - Video Lesson", 
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Video Lesson 1",
                                "type": "video",
                                "content": "This is the video lesson for progress tracking test.",
                                "videoUrl": "https://example.com/video.mp4"
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 3 - Quiz Lesson",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Quiz Lesson 1",
                                "type": "quiz",
                                "content": "This is the quiz lesson for progress tracking test.",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "question": "What is 2 + 2?",
                                        "type": "multiple_choice",
                                        "options": ["3", "4", "5", "6"],
                                        "correct_answer": "4"
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
                self.test_course_id = created_course.get('id')
                
                self.log_result(
                    "Create Test Course", 
                    "PASS", 
                    f"Test course created successfully: {created_course.get('title')}",
                    f"Course ID: {self.test_course_id}, Modules: {len(created_course.get('modules', []))}"
                )
                return True
            else:
                self.log_result(
                    "Create Test Course", 
                    "FAIL", 
                    f"Course creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Test Course", 
                "FAIL", 
                "Course creation request failed",
                str(e)
            )
        return False
    
    def enroll_student_in_test_course(self):
        """Enroll the progress test student in the test course"""
        if "progress_student" not in self.auth_tokens or not self.test_course_id:
            self.log_result(
                "Enroll Student in Test Course", 
                "FAIL", 
                "Cannot enroll - missing student token or course ID",
                f"Student token: {bool('progress_student' in self.auth_tokens)}, Course ID: {bool(self.test_course_id)}"
            )
            return False
        
        try:
            enrollment_data = {
                "courseId": self.test_course_id
            }
            
            response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["progress_student"]}'
                }
            )
            
            if response.status_code == 200:
                enrollment = response.json()
                self.test_enrollment_id = enrollment.get('id')
                
                self.log_result(
                    "Enroll Student in Test Course", 
                    "PASS", 
                    f"Student enrolled successfully in test course",
                    f"Enrollment ID: {self.test_enrollment_id}, Initial Progress: {enrollment.get('progress', 0)}%"
                )
                return True
            elif response.status_code == 400 and "already enrolled" in response.text:
                # Student already enrolled, get enrollment ID
                enrollments = self.get_student_enrollments()
                if enrollments:
                    for enrollment in enrollments:
                        if enrollment.get('courseId') == self.test_course_id:
                            self.test_enrollment_id = enrollment.get('id')
                            self.log_result(
                                "Enroll Student in Test Course", 
                                "PASS", 
                                f"Student already enrolled in test course",
                                f"Enrollment ID: {self.test_enrollment_id}, Current Progress: {enrollment.get('progress', 0)}%"
                            )
                            return True
                
                self.log_result(
                    "Enroll Student in Test Course", 
                    "FAIL", 
                    "Student already enrolled but couldn't find enrollment",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Enroll Student in Test Course", 
                    "FAIL", 
                    f"Enrollment failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enroll Student in Test Course", 
                "FAIL", 
                "Enrollment request failed",
                str(e)
            )
        return False
    
    def get_student_enrollments(self):
        """Get current student enrollments"""
        if "progress_student" not in self.auth_tokens:
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["progress_student"]}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get enrollments: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting enrollments: {str(e)}")
            return None
    
    def test_lesson_completion_progress_tracking(self):
        """Test the core progress tracking bug - lesson completion and backend data sync"""
        if not self.test_course_id or not self.test_enrollment_id:
            self.log_result(
                "Progress Tracking Bug Investigation", 
                "FAIL", 
                "Cannot test progress tracking - missing course or enrollment ID",
                f"Course ID: {bool(self.test_course_id)}, Enrollment ID: {bool(self.test_enrollment_id)}"
            )
            return False
        
        print(f"\n🔍 INVESTIGATING PROGRESS TRACKING BUG")
        print("=" * 60)
        print(f"Course ID: {self.test_course_id}")
        print(f"Enrollment ID: {self.test_enrollment_id}")
        print("=" * 60)
        
        # Step 1: Get initial enrollment state
        print(f"\n📊 STEP 1: Getting Initial Enrollment State")
        print("-" * 50)
        initial_enrollments = self.get_student_enrollments()
        initial_enrollment = None
        
        if initial_enrollments:
            for enrollment in initial_enrollments:
                if enrollment.get('courseId') == self.test_course_id:
                    initial_enrollment = enrollment
                    break
        
        if not initial_enrollment:
            self.log_result(
                "Progress Tracking Bug Investigation", 
                "FAIL", 
                "Cannot find test enrollment in student's enrollments",
                f"Found {len(initial_enrollments) if initial_enrollments else 0} enrollments"
            )
            return False
        
        print(f"✅ Initial enrollment found:")
        print(f"   Progress: {initial_enrollment.get('progress', 0)}%")
        print(f"   Status: {initial_enrollment.get('status', 'unknown')}")
        print(f"   Module Progress: {initial_enrollment.get('moduleProgress', 'Not set')}")
        
        # Step 2: Get course structure to understand lessons
        print(f"\n📚 STEP 2: Getting Course Structure")
        print("-" * 50)
        course_structure = self.get_course_structure()
        
        if not course_structure:
            self.log_result(
                "Progress Tracking Bug Investigation", 
                "FAIL", 
                "Cannot get course structure",
                "Need course structure to test lesson completion"
            )
            return False
        
        modules = course_structure.get('modules', [])
        total_lessons = sum(len(module.get('lessons', [])) for module in modules)
        print(f"✅ Course structure retrieved:")
        print(f"   Total Modules: {len(modules)}")
        print(f"   Total Lessons: {total_lessons}")
        print(f"   Expected progress per lesson: {100/total_lessons:.2f}%")
        
        # Step 3: Test lesson completion sequence
        print(f"\n🎯 STEP 3: Testing Lesson Completion Sequence")
        print("-" * 50)
        
        completed_lessons = 0
        progress_issues = []
        
        for module_idx, module in enumerate(modules):
            module_id = module.get('id')
            lessons = module.get('lessons', [])
            
            print(f"\n📖 Module {module_idx + 1}: {module.get('title')}")
            
            for lesson_idx, lesson in enumerate(lessons):
                lesson_id = lesson.get('id')
                completed_lessons += 1
                expected_progress = (completed_lessons / total_lessons) * 100
                
                print(f"   Lesson {lesson_idx + 1}: {lesson.get('title')} ({lesson.get('type')})")
                print(f"   Expected progress after completion: {expected_progress:.2f}%")
                
                # Complete this lesson
                completion_result = self.complete_lesson(module_id, lesson_id, completed_lessons, total_lessons)
                
                if completion_result:
                    backend_progress = completion_result.get('progress', 0)
                    print(f"   ✅ Lesson completed - Backend returned: {backend_progress}%")
                    
                    # Check if backend progress matches expected
                    if abs(backend_progress - expected_progress) > 1.0:  # Allow 1% tolerance
                        issue = f"Lesson {completed_lessons}: Expected {expected_progress:.2f}%, Got {backend_progress}%"
                        progress_issues.append(issue)
                        print(f"   ❌ PROGRESS MISMATCH: {issue}")
                    else:
                        print(f"   ✅ Progress calculation correct")
                        
                    # Check moduleProgress data
                    module_progress = completion_result.get('moduleProgress', [])
                    if module_progress:
                        print(f"   ✅ ModuleProgress data present: {len(module_progress)} modules")
                        
                        # Verify this lesson is marked complete in moduleProgress
                        lesson_found_complete = False
                        for mp in module_progress:
                            if mp.get('moduleId') == module_id:
                                for lp in mp.get('lessons', []):
                                    if lp.get('lessonId') == lesson_id and lp.get('completed'):
                                        lesson_found_complete = True
                                        break
                                break
                        
                        if lesson_found_complete:
                            print(f"   ✅ Lesson marked complete in moduleProgress")
                        else:
                            issue = f"Lesson {completed_lessons}: Not marked complete in moduleProgress"
                            progress_issues.append(issue)
                            print(f"   ❌ MODULEPROGRESS ISSUE: {issue}")
                    else:
                        issue = f"Lesson {completed_lessons}: No moduleProgress data returned"
                        progress_issues.append(issue)
                        print(f"   ❌ MODULEPROGRESS MISSING: {issue}")
                else:
                    issue = f"Lesson {completed_lessons}: Failed to complete lesson"
                    progress_issues.append(issue)
                    print(f"   ❌ COMPLETION FAILED: {issue}")
                
                # Small delay between completions
                time.sleep(0.5)
        
        # Step 4: Final verification - get enrollment data again
        print(f"\n🔍 STEP 4: Final Enrollment Data Verification")
        print("-" * 50)
        
        final_enrollments = self.get_student_enrollments()
        final_enrollment = None
        
        if final_enrollments:
            for enrollment in final_enrollments:
                if enrollment.get('courseId') == self.test_course_id:
                    final_enrollment = enrollment
                    break
        
        if final_enrollment:
            final_progress = final_enrollment.get('progress', 0)
            final_module_progress = final_enrollment.get('moduleProgress', [])
            
            print(f"✅ Final enrollment data:")
            print(f"   Final Progress: {final_progress}%")
            print(f"   Expected Progress: 100%")
            print(f"   ModuleProgress entries: {len(final_module_progress)}")
            
            # Count completed lessons in moduleProgress
            completed_in_module_progress = 0
            for mp in final_module_progress:
                for lp in mp.get('lessons', []):
                    if lp.get('completed'):
                        completed_in_module_progress += 1
            
            print(f"   Lessons marked complete in moduleProgress: {completed_in_module_progress}/{total_lessons}")
            
            if abs(final_progress - 100.0) > 1.0:
                progress_issues.append(f"Final progress {final_progress}% != 100%")
            
            if completed_in_module_progress != total_lessons:
                progress_issues.append(f"ModuleProgress shows {completed_in_module_progress}/{total_lessons} lessons complete")
        
        # Step 5: Summary and diagnosis
        print(f"\n📋 STEP 5: Progress Tracking Bug Analysis Summary")
        print("-" * 50)
        
        if len(progress_issues) == 0:
            self.log_result(
                "Progress Tracking Bug Investigation", 
                "PASS", 
                "✅ NO PROGRESS TRACKING ISSUES FOUND - Backend working correctly",
                f"All {total_lessons} lessons completed successfully, progress calculated correctly, moduleProgress data intact"
            )
            return True
        else:
            print(f"❌ FOUND {len(progress_issues)} PROGRESS TRACKING ISSUES:")
            for issue in progress_issues:
                print(f"   • {issue}")
            
            self.log_result(
                "Progress Tracking Bug Investigation", 
                "FAIL", 
                f"❌ PROGRESS TRACKING BUG CONFIRMED - Found {len(progress_issues)} issues",
                f"Issues: {'; '.join(progress_issues)}"
            )
            return False
    
    def get_course_structure(self):
        """Get the test course structure"""
        if "progress_student" not in self.auth_tokens or not self.test_course_id:
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["progress_student"]}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get course structure: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting course structure: {str(e)}")
            return None
    
    def complete_lesson(self, module_id, lesson_id, completed_count, total_lessons):
        """Complete a specific lesson and return updated enrollment data"""
        if "progress_student" not in self.auth_tokens or not self.test_course_id:
            return None
        
        try:
            # Calculate expected progress
            expected_progress = (completed_count / total_lessons) * 100
            
            # Create moduleProgress data structure
            # First get current enrollment to preserve existing moduleProgress
            current_enrollments = self.get_student_enrollments()
            current_enrollment = None
            
            for enrollment in current_enrollments:
                if enrollment.get('courseId') == self.test_course_id:
                    current_enrollment = enrollment
                    break
            
            if not current_enrollment:
                print(f"❌ Cannot find current enrollment for progress update")
                return None
            
            # Get current moduleProgress or initialize
            module_progress = current_enrollment.get('moduleProgress', [])
            
            # If no moduleProgress exists, initialize it based on course structure
            if not module_progress:
                course_structure = self.get_course_structure()
                if course_structure:
                    module_progress = []
                    for module in course_structure.get('modules', []):
                        lessons_progress = []
                        for lesson in module.get('lessons', []):
                            lessons_progress.append({
                                "lessonId": lesson.get('id'),
                                "completed": False,
                                "completedAt": None,
                                "timeSpent": 0
                            })
                        
                        module_progress.append({
                            "moduleId": module.get('id'),
                            "lessons": lessons_progress,
                            "completed": False,
                            "completedAt": None
                        })
            
            # Update the specific lesson as completed
            lesson_updated = False
            for mp in module_progress:
                if mp.get('moduleId') == module_id:
                    for lp in mp.get('lessons', []):
                        if lp.get('lessonId') == lesson_id:
                            lp['completed'] = True
                            lp['completedAt'] = datetime.utcnow().isoformat()
                            lp['timeSpent'] = 300  # 5 minutes
                            lesson_updated = True
                            break
                    
                    # Check if all lessons in this module are complete
                    all_lessons_complete = all(lp.get('completed', False) for lp in mp.get('lessons', []))
                    if all_lessons_complete:
                        mp['completed'] = True
                        mp['completedAt'] = datetime.utcnow().isoformat()
                    
                    break
            
            if not lesson_updated:
                print(f"❌ Could not find lesson {lesson_id} in module {module_id} to update")
                return None
            
            # Prepare progress update data
            progress_data = {
                "progress": expected_progress,
                "currentModuleId": module_id,
                "currentLessonId": lesson_id,
                "moduleProgress": module_progress,
                "lastAccessedAt": datetime.utcnow().isoformat(),
                "timeSpent": 300
            }
            
            # Send progress update to backend
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["progress_student"]}'
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Progress update failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error completing lesson: {str(e)}")
            return None
    
    def cleanup_test_data(self):
        """Clean up test course and enrollment data"""
        if "admin" in self.auth_tokens and self.test_course_id:
            try:
                # Delete test course
                response = requests.delete(
                    f"{BACKEND_URL}/courses/{self.test_course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code == 200:
                    print(f"✅ Test course cleaned up successfully")
                else:
                    print(f"⚠️ Failed to cleanup test course: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error during cleanup: {str(e)}")
    
    def run_progress_tracking_investigation(self):
        """Run the complete progress tracking bug investigation"""
        print("🚀 STARTING PROGRESS TRACKING BUG INVESTIGATION")
        print("=" * 80)
        print("CRITICAL BUG: Frontend calculates progress correctly locally,")
        print("but backend returns enrollment data with wrong progress calculation")
        print("=" * 80)
        
        try:
            # Step 1: Admin authentication
            print(f"\n🔑 STEP 1: Admin Authentication")
            if not self.test_admin_login():
                print("❌ Cannot proceed without admin access")
                return False
            
            # Step 2: Student authentication (create if needed)
            print(f"\n👤 STEP 2: Progress Test Student Authentication")
            if not self.test_progress_student_login():
                print("❌ Cannot proceed without student access")
                return False
            
            # Step 3: Create test course with modules
            print(f"\n📚 STEP 3: Creating Test Course with Multiple Modules")
            if not self.create_test_course_with_modules():
                print("❌ Cannot proceed without test course")
                return False
            
            # Step 4: Enroll student in test course
            print(f"\n📝 STEP 4: Enrolling Student in Test Course")
            if not self.enroll_student_in_test_course():
                print("❌ Cannot proceed without enrollment")
                return False
            
            # Step 5: Test progress tracking bug
            print(f"\n🔍 STEP 5: Progress Tracking Bug Investigation")
            bug_investigation_result = self.test_lesson_completion_progress_tracking()
            
            # Step 6: Cleanup
            print(f"\n🧹 STEP 6: Cleanup Test Data")
            self.cleanup_test_data()
            
            return bug_investigation_result
            
        except Exception as e:
            print(f"❌ Investigation failed with error: {str(e)}")
            self.log_result(
                "Progress Tracking Investigation", 
                "FAIL", 
                "Investigation failed with exception",
                str(e)
            )
            return False
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n" + "=" * 80)
        print(f"PROGRESS TRACKING BUG INVESTIGATION SUMMARY")
        print(f"=" * 80)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if (self.passed + self.failed) > 0 else "0%")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n" + "=" * 80)

def main():
    """Main function to run progress tracking investigation"""
    tester = ProgressTrackingTester()
    
    try:
        success = tester.run_progress_tracking_investigation()
        tester.print_summary()
        
        if success:
            print(f"\n✅ INVESTIGATION COMPLETE: Progress tracking working correctly")
            return 0
        else:
            print(f"\n❌ INVESTIGATION COMPLETE: Progress tracking bug confirmed")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Investigation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Investigation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
"""
Focused Progress Tracking Tests for Critical Bug Fixes
Tests the specific issues mentioned in the review request:
- Progress stuck at 33% despite completing additional lessons
- Progress calculations not reflecting in UI immediately  
- State synchronization problems between backend and frontend
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://fixfriend.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ProgressTrackingTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_token = None
        self.student_info = None
        
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

    def authenticate_student(self):
        """Authenticate with the specified test credentials"""
        try:
            login_data = {
                "username_or_email": "test.student@learningfwiend.com",
                "password": "StudentPermanent123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.student_info = data.get('user', {})
                
                self.log_result(
                    "Authentication", 
                    "PASS", 
                    f"Successfully authenticated as {self.student_info.get('email')}",
                    f"User ID: {self.student_info.get('id')}, Role: {self.student_info.get('role')}"
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    "FAIL", 
                    f"Authentication failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Authentication", 
                "FAIL", 
                "Authentication request failed",
                str(e)
            )
        return False

    def get_available_courses(self):
        """Get available courses for testing"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                if courses:
                    # Find a course with modules and lessons
                    for course in courses:
                        modules = course.get('modules', [])
                        if modules and any(module.get('lessons') for module in modules):
                            total_lessons = sum(len(module.get('lessons', [])) for module in modules)
                            self.log_result(
                                "Course Selection", 
                                "PASS", 
                                f"Found suitable test course: {course.get('title')}",
                                f"Course ID: {course.get('id')}, Modules: {len(modules)}, Total Lessons: {total_lessons}"
                            )
                            return course
                    
                    # If no course with modules found, use the first available course
                    course = courses[0]
                    self.log_result(
                        "Course Selection", 
                        "PASS", 
                        f"Using available course: {course.get('title')} (may not have modules)",
                        f"Course ID: {course.get('id')}"
                    )
                    return course
                else:
                    self.log_result(
                        "Course Selection", 
                        "FAIL", 
                        "No courses available for testing",
                        "Need at least one course to test progress tracking"
                    )
            else:
                self.log_result(
                    "Course Selection", 
                    "FAIL", 
                    f"Failed to retrieve courses (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Course Selection", 
                "FAIL", 
                "Failed to get available courses",
                str(e)
            )
        return None

    def enroll_in_course(self, course_id):
        """Enroll in the test course"""
        try:
            enrollment_data = {"courseId": course_id}
            
            response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_token}'
                }
            )
            
            if response.status_code == 200:
                enrollment = response.json()
                self.log_result(
                    "Course Enrollment", 
                    "PASS", 
                    f"Successfully enrolled in course",
                    f"Enrollment ID: {enrollment.get('id')}, Initial Progress: {enrollment.get('progress', 0)}%"
                )
                return enrollment
            elif response.status_code == 400 and "already enrolled" in response.text:
                # Already enrolled, get current enrollment
                enrollments_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_token}'}
                )
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    for enrollment in enrollments:
                        if enrollment.get('courseId') == course_id:
                            self.log_result(
                                "Course Enrollment", 
                                "PASS", 
                                f"Already enrolled in course (using existing enrollment)",
                                f"Enrollment ID: {enrollment.get('id')}, Current Progress: {enrollment.get('progress', 0)}%"
                            )
                            return enrollment
                
                self.log_result(
                    "Course Enrollment", 
                    "FAIL", 
                    "Already enrolled but could not retrieve enrollment details",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Course Enrollment", 
                    "FAIL", 
                    f"Enrollment failed (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Course Enrollment", 
                "FAIL", 
                "Enrollment request failed",
                str(e)
            )
        return None

    def test_progress_state_synchronization(self, course_id):
        """Test progress tracking state synchronization - immediate UI updates"""
        print(f"\n🔄 TESTING PROGRESS TRACKING STATE SYNCHRONIZATION")
        print("-" * 60)
        
        try:
            # Test sequence: 33% -> 66% -> 100% with immediate verification
            progress_sequence = [
                {"progress": 33.33, "description": "First module completion"},
                {"progress": 66.67, "description": "Second module completion"},
                {"progress": 100.0, "description": "Course completion"}
            ]
            
            successful_updates = 0
            
            for i, step in enumerate(progress_sequence):
                print(f"\nStep {i+1}: {step['description']} ({step['progress']}%)")
                
                # Update progress
                progress_data = {
                    "progress": step["progress"],
                    "lastAccessedAt": datetime.now().isoformat(),
                    "currentModuleId": f"module-{i+1}",
                    "moduleProgress": [
                        {
                            "moduleId": f"module-{j+1}",
                            "completed": j <= i,
                            "completedAt": datetime.now().isoformat() if j <= i else None
                        } for j in range(3)
                    ]
                }
                
                # Send update request
                update_response = requests.put(
                    f"{BACKEND_URL}/enrollments/{course_id}/progress",
                    json=progress_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_token}'
                    }
                )
                
                if update_response.status_code == 200:
                    updated_enrollment = update_response.json()
                    returned_progress = updated_enrollment.get('progress', 0)
                    
                    # Immediately verify the update by fetching enrollment
                    verify_response = requests.get(
                        f"{BACKEND_URL}/enrollments",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_token}'}
                    )
                    
                    if verify_response.status_code == 200:
                        enrollments = verify_response.json()
                        current_enrollment = None
                        for enrollment in enrollments:
                            if enrollment.get('courseId') == course_id:
                                current_enrollment = enrollment
                                break
                        
                        if current_enrollment:
                            verified_progress = current_enrollment.get('progress', 0)
                            
                            # Check if progress matches immediately
                            if abs(verified_progress - step["progress"]) < 0.1:
                                successful_updates += 1
                                print(f"   ✅ Progress updated immediately: {verified_progress}%")
                                
                                # Check for console logging data
                                if current_enrollment.get('lastAccessedAt'):
                                    print(f"   ✅ Last accessed timestamp updated: {current_enrollment.get('lastAccessedAt')}")
                                
                                if step["progress"] >= 100.0:
                                    if current_enrollment.get('status') == 'completed':
                                        print(f"   ✅ Course marked as completed at 100%")
                                    if current_enrollment.get('completedAt'):
                                        print(f"   ✅ Completion timestamp set: {current_enrollment.get('completedAt')}")
                            else:
                                print(f"   ❌ Progress mismatch: Expected {step['progress']}%, Got {verified_progress}%")
                        else:
                            print(f"   ❌ Could not find enrollment for verification")
                    else:
                        print(f"   ❌ Failed to verify progress update (status: {verify_response.status_code})")
                else:
                    print(f"   ❌ Progress update failed (status: {update_response.status_code})")
                
                # Small delay between updates to simulate real usage
                time.sleep(0.5)
            
            if successful_updates == len(progress_sequence):
                self.log_result(
                    "Progress State Synchronization", 
                    "PASS", 
                    f"All progress updates synchronized immediately ({successful_updates}/{len(progress_sequence)})",
                    "Progress calculations reflect in backend immediately without delays"
                )
                return True
            else:
                self.log_result(
                    "Progress State Synchronization", 
                    "FAIL", 
                    f"Some progress updates not synchronized ({successful_updates}/{len(progress_sequence)})",
                    "Progress calculations not reflecting immediately - state synchronization issues"
                )
        except Exception as e:
            self.log_result(
                "Progress State Synchronization", 
                "FAIL", 
                "Failed to test progress state synchronization",
                str(e)
            )
        return False

    def test_lesson_completion_workflow(self, course_id):
        """Test individual lesson completion updates progress immediately"""
        print(f"\n📚 TESTING LESSON COMPLETION WORKFLOW")
        print("-" * 60)
        
        try:
            # Simulate completing individual lessons in a 3-lesson course
            # Expected progress: 33.33%, 66.67%, 100%
            lesson_completions = [
                {
                    "progress": 33.33,
                    "description": "Lesson 1 completed",
                    "moduleProgress": [
                        {
                            "moduleId": "module-1",
                            "lessons": [
                                {"lessonId": "lesson-1", "completed": True, "completedAt": datetime.now().isoformat()}
                            ],
                            "completed": False
                        }
                    ]
                },
                {
                    "progress": 66.67,
                    "description": "Lesson 2 completed",
                    "moduleProgress": [
                        {
                            "moduleId": "module-1",
                            "lessons": [
                                {"lessonId": "lesson-1", "completed": True, "completedAt": datetime.now().isoformat()},
                                {"lessonId": "lesson-2", "completed": True, "completedAt": datetime.now().isoformat()}
                            ],
                            "completed": False
                        }
                    ]
                },
                {
                    "progress": 100.0,
                    "description": "Lesson 3 completed (course complete)",
                    "moduleProgress": [
                        {
                            "moduleId": "module-1",
                            "lessons": [
                                {"lessonId": "lesson-1", "completed": True, "completedAt": datetime.now().isoformat()},
                                {"lessonId": "lesson-2", "completed": True, "completedAt": datetime.now().isoformat()},
                                {"lessonId": "lesson-3", "completed": True, "completedAt": datetime.now().isoformat()}
                            ],
                            "completed": True,
                            "completedAt": datetime.now().isoformat()
                        }
                    ]
                }
            ]
            
            successful_completions = 0
            
            for i, completion in enumerate(lesson_completions):
                print(f"\nLesson Completion {i+1}: {completion['description']}")
                
                # Mark lesson as complete
                response = requests.put(
                    f"{BACKEND_URL}/enrollments/{course_id}/progress",
                    json=completion,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_token}'
                    }
                )
                
                if response.status_code == 200:
                    updated_enrollment = response.json()
                    returned_progress = updated_enrollment.get('progress', 0)
                    
                    # Verify progress matches expected value
                    if abs(returned_progress - completion["progress"]) < 0.1:
                        successful_completions += 1
                        print(f"   ✅ Progress updated correctly: {returned_progress}%")
                        
                        # Check module progress data
                        module_progress = updated_enrollment.get('moduleProgress', [])
                        if module_progress:
                            print(f"   ✅ Module progress data stored: {len(module_progress)} modules")
                        
                        # Check completion status at 100%
                        if completion["progress"] >= 100.0:
                            if updated_enrollment.get('status') == 'completed':
                                print(f"   ✅ Course status changed to 'completed'")
                    else:
                        print(f"   ❌ Progress incorrect: Expected {completion['progress']}%, Got {returned_progress}%")
                else:
                    print(f"   ❌ Lesson completion failed (status: {response.status_code})")
                    print(f"       Response: {response.text}")
                
                time.sleep(0.3)  # Brief delay between completions
            
            if successful_completions == len(lesson_completions):
                self.log_result(
                    "Lesson Completion Workflow", 
                    "PASS", 
                    f"All lesson completions processed correctly ({successful_completions}/{len(lesson_completions)})",
                    "Individual lesson completion updates progress immediately as expected"
                )
                return True
            else:
                self.log_result(
                    "Lesson Completion Workflow", 
                    "FAIL", 
                    f"Some lesson completions failed ({successful_completions}/{len(lesson_completions)})",
                    "Lesson completion workflow not working correctly - progress stuck issue may persist"
                )
        except Exception as e:
            self.log_result(
                "Lesson Completion Workflow", 
                "FAIL", 
                "Failed to test lesson completion workflow",
                str(e)
            )
        return False

    def test_api_communication_performance(self, course_id):
        """Test PUT /api/enrollments/{course_id}/progress endpoint response times"""
        print(f"\n⚡ TESTING API COMMUNICATION PERFORMANCE")
        print("-" * 60)
        
        try:
            response_times = []
            successful_requests = 0
            
            # Test multiple progress updates to measure response times
            test_updates = [
                {"progress": 10.0, "description": "10% progress"},
                {"progress": 25.0, "description": "25% progress"},
                {"progress": 50.0, "description": "50% progress"},
                {"progress": 75.0, "description": "75% progress"},
                {"progress": 90.0, "description": "90% progress"}
            ]
            
            for update in test_updates:
                start_time = time.time()
                
                progress_data = {
                    "progress": update["progress"],
                    "lastAccessedAt": datetime.now().isoformat()
                }
                
                response = requests.put(
                    f"{BACKEND_URL}/enrollments/{course_id}/progress",
                    json=progress_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_token}'
                    }
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                response_times.append(response_time)
                
                if response.status_code == 200:
                    successful_requests += 1
                    print(f"   ✅ {update['description']}: {response_time:.0f}ms")
                else:
                    print(f"   ❌ {update['description']}: Failed ({response.status_code}) - {response_time:.0f}ms")
                
                time.sleep(0.2)  # Small delay between requests
            
            # Calculate performance metrics
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                # Consider good performance if average response time < 2000ms and all requests successful
                if avg_response_time < 2000 and successful_requests == len(test_updates):
                    self.log_result(
                        "API Communication Performance", 
                        "PASS", 
                        f"API response times acceptable (avg: {avg_response_time:.0f}ms)",
                        f"Min: {min_response_time:.0f}ms, Max: {max_response_time:.0f}ms, Success: {successful_requests}/{len(test_updates)}"
                    )
                    return True
                else:
                    self.log_result(
                        "API Communication Performance", 
                        "FAIL", 
                        f"API performance issues detected (avg: {avg_response_time:.0f}ms)",
                        f"Min: {min_response_time:.0f}ms, Max: {max_response_time:.0f}ms, Success: {successful_requests}/{len(test_updates)}"
                    )
            else:
                self.log_result(
                    "API Communication Performance", 
                    "FAIL", 
                    "No response times recorded",
                    "Could not measure API performance"
                )
        except Exception as e:
            self.log_result(
                "API Communication Performance", 
                "FAIL", 
                "Failed to test API communication performance",
                str(e)
            )
        return False

    def test_data_persistence(self, course_id):
        """Test that progress updates persist correctly in database"""
        print(f"\n💾 TESTING DATA PERSISTENCE")
        print("-" * 60)
        
        try:
            # Set a specific progress value
            test_progress = 87.5
            progress_data = {
                "progress": test_progress,
                "currentModuleId": "module-3",
                "currentLessonId": "lesson-3-2",
                "lastAccessedAt": datetime.now().isoformat(),
                "timeSpent": 3600  # 1 hour
            }
            
            # Update progress
            update_response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_token}'
                }
            )
            
            if update_response.status_code == 200:
                print(f"   ✅ Progress update sent: {test_progress}%")
                
                # Wait a moment for database write
                time.sleep(1)
                
                # Retrieve enrollment to verify persistence
                get_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_token}'}
                )
                
                if get_response.status_code == 200:
                    enrollments = get_response.json()
                    test_enrollment = None
                    
                    for enrollment in enrollments:
                        if enrollment.get('courseId') == course_id:
                            test_enrollment = enrollment
                            break
                    
                    if test_enrollment:
                        persisted_progress = test_enrollment.get('progress', 0)
                        persisted_module = test_enrollment.get('currentModuleId')
                        persisted_lesson = test_enrollment.get('currentLessonId')
                        persisted_time = test_enrollment.get('timeSpent')
                        
                        # Verify all data persisted correctly
                        checks = []
                        checks.append(abs(persisted_progress - test_progress) < 0.1)
                        checks.append(persisted_module == "module-3")
                        checks.append(persisted_lesson == "lesson-3-2")
                        checks.append(persisted_time == 3600)
                        
                        if all(checks):
                            self.log_result(
                                "Data Persistence", 
                                "PASS", 
                                f"All progress data persisted correctly in database",
                                f"Progress: {persisted_progress}%, Module: {persisted_module}, Lesson: {persisted_lesson}, Time: {persisted_time}s"
                            )
                            return True
                        else:
                            self.log_result(
                                "Data Persistence", 
                                "FAIL", 
                                f"Some progress data not persisted correctly",
                                f"Progress: {persisted_progress}% (exp: {test_progress}%), Module: {persisted_module}, Lesson: {persisted_lesson}, Time: {persisted_time}s"
                            )
                    else:
                        self.log_result(
                            "Data Persistence", 
                            "FAIL", 
                            "Could not find enrollment after update",
                            "Enrollment may not have been persisted"
                        )
                else:
                    self.log_result(
                        "Data Persistence", 
                        "FAIL", 
                        f"Failed to retrieve enrollments for verification (status: {get_response.status_code})",
                        f"Response: {get_response.text}"
                    )
            else:
                self.log_result(
                    "Data Persistence", 
                    "FAIL", 
                    f"Progress update failed (status: {update_response.status_code})",
                    f"Response: {update_response.text}"
                )
        except Exception as e:
            self.log_result(
                "Data Persistence", 
                "FAIL", 
                "Failed to test data persistence",
                str(e)
            )
        return False

    def run_comprehensive_tests(self):
        """Run all comprehensive progress tracking tests"""
        print(f"\n🎯 COMPREHENSIVE COURSE PROGRESS TRACKING BUG FIX TESTS")
        print("=" * 80)
        print("Testing critical bug fixes for course progress tracking issues:")
        print("• Progress stuck at 33% despite completing additional lessons")
        print("• Progress calculations not reflecting in UI immediately")
        print("• State synchronization problems between backend and frontend")
        print("• API communication and response times")
        print("• Data persistence and integrity")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_student():
            print("\n❌ Authentication failed - cannot proceed with tests")
            return self.print_summary()
        
        # Step 2: Get available course
        test_course = self.get_available_courses()
        if not test_course:
            print("\n❌ No suitable course found - cannot proceed with tests")
            return self.print_summary()
        
        course_id = test_course.get('id')
        
        # Step 3: Enroll in course
        enrollment = self.enroll_in_course(course_id)
        if not enrollment:
            print("\n❌ Enrollment failed - cannot proceed with tests")
            return self.print_summary()
        
        print(f"\n🧪 Running progress tracking tests on course: {test_course.get('title')}")
        print(f"Course ID: {course_id}")
        print(f"Student: {self.student_info.get('email')}")
        
        # Step 4: Run all tests
        test_results = []
        
        test_results.append(self.test_progress_state_synchronization(course_id))
        test_results.append(self.test_lesson_completion_workflow(course_id))
        test_results.append(self.test_api_communication_performance(course_id))
        test_results.append(self.test_data_persistence(course_id))
        
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print(f"\n" + "=" * 80)
        print(f"📊 PROGRESS TRACKING TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        # Provide specific recommendations based on results
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ Progress tracking functionality is working correctly")
            print("   ✅ Critical bug fixes appear to be successful")
        elif success_rate >= 70:
            print("   ⚠️  Most progress tracking functionality working, some issues remain")
            print("   ⚠️  Review failed tests for remaining issues")
        else:
            print("   ❌ Significant progress tracking issues detected")
            print("   ❌ Critical bug fixes may not be fully implemented")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ProgressTrackingTester()
    success = tester.run_comprehensive_tests()
    exit(0 if success else 1)