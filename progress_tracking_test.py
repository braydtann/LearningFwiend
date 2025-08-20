#!/usr/bin/env python3
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
BACKEND_URL = "https://learning-journey-3.preview.emergentagent.com/api"
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