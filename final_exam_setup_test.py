#!/usr/bin/env python3

"""
Final Exam Setup and Debug Test
===============================

This test creates the necessary test data (programs, courses, final exams) and then
debugs the final exam access issue.

Test Flow:
1. Create test courses
2. Create test programs with courses
3. Create final exams for programs
4. Create classrooms and enroll student
5. Test final exam access flow
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://quiz-analytics-lms.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamSetupTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        self.created_data = {
            'courses': [],
            'programs': [],
            'final_tests': [],
            'classrooms': []
        }
        
    def log_result(self, test_name: str, success: bool, details: str, data: Optional[Dict] = None):
        """Log test result with timestamp."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}: {details}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate admin user."""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user = data["user"]
                self.log_result("Admin Authentication", True, f"Successfully authenticated as {self.admin_user['full_name']}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed with status {response.status_code}", response.json())
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_student(self) -> bool:
        """Authenticate student user."""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_user = data["user"]
                self.log_result("Student Authentication", True, f"Successfully authenticated as {self.student_user['full_name']}")
                return True
            else:
                self.log_result("Student Authentication", False, f"Failed with status {response.status_code}", response.json())
                return False
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_courses(self) -> bool:
        """Create test courses for the program."""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            courses_data = [
                {
                    "title": "Final Exam Test Course 1",
                    "description": "First course for final exam testing",
                    "category": "Programming",
                    "duration": "4 weeks",
                    "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
                    "accessType": "open",
                    "learningOutcomes": ["Learn basics", "Practice skills"],
                    "modules": [
                        {
                            "title": "Module 1",
                            "lessons": [
                                {
                                    "id": "lesson1",
                                    "title": "Introduction",
                                    "type": "video",
                                    "content": "Introduction to the course",
                                    "duration": 10
                                }
                            ]
                        }
                    ]
                },
                {
                    "title": "Final Exam Test Course 2", 
                    "description": "Second course for final exam testing",
                    "category": "Programming",
                    "duration": "3 weeks",
                    "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
                    "accessType": "open",
                    "learningOutcomes": ["Advanced concepts", "Real-world application"],
                    "modules": [
                        {
                            "title": "Module 1",
                            "lessons": [
                                {
                                    "id": "lesson1",
                                    "title": "Advanced Topics",
                                    "type": "text",
                                    "content": "Advanced course content",
                                    "duration": 15
                                }
                            ]
                        }
                    ]
                }
            ]
            
            created_courses = []
            for course_data in courses_data:
                response = requests.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
                
                if response.status_code == 200:
                    course = response.json()
                    created_courses.append(course)
                    self.created_data['courses'].append(course)
                    print(f"  ✅ Created course: {course['title']} (ID: {course['id']})")
                else:
                    self.log_result("Create Test Courses", False, f"Failed to create course: {response.status_code}", response.json())
                    return False
            
            self.log_result("Create Test Courses", True, f"Successfully created {len(created_courses)} test courses")
            return True
            
        except Exception as e:
            self.log_result("Create Test Courses", False, f"Exception: {str(e)}")
            return False
    
    def create_test_program(self) -> bool:
        """Create a test program with the created courses."""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.created_data['courses']:
                self.log_result("Create Test Program", False, "No courses available for program creation")
                return False
            
            course_ids = [course['id'] for course in self.created_data['courses']]
            
            program_data = {
                "title": "Final Exam Test Program",
                "description": "Test program for debugging final exam access",
                "departmentId": None,
                "duration": "8 weeks",
                "courseIds": course_ids,
                "nestedProgramIds": []
            }
            
            response = requests.post(f"{BACKEND_URL}/programs", json=program_data, headers=headers)
            
            if response.status_code == 200:
                program = response.json()
                self.created_data['programs'].append(program)
                
                print(f"  ✅ Created program: {program['title']}")
                print(f"     Program ID: {program['id']}")
                print(f"     Course Count: {program['courseCount']}")
                print(f"     Course IDs: {program['courseIds']}")
                
                self.log_result("Create Test Program", True, f"Successfully created test program with {len(course_ids)} courses")
                return True
            else:
                self.log_result("Create Test Program", False, f"Failed to create program: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Test Program", False, f"Exception: {str(e)}")
            return False
    
    def create_final_exam(self) -> bool:
        """Create a final exam for the test program."""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.created_data['programs']:
                self.log_result("Create Final Exam", False, "No programs available for final exam creation")
                return False
            
            program = self.created_data['programs'][0]
            
            final_exam_data = {
                "title": "Final Exam Test",
                "description": "Test final exam for debugging access issues",
                "programId": program['id'],
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the main purpose of this test?",
                        "options": ["To debug final exam access", "To test functionality", "To verify program completion", "All of the above"],
                        "correctAnswer": "All of the above",
                        "points": 25,
                        "explanation": "This test covers all aspects of final exam functionality"
                    },
                    {
                        "type": "true_false",
                        "question": "Final exams should be accessible to students who complete all program courses.",
                        "correctAnswer": "true",
                        "points": 25,
                        "explanation": "Students should have access to final exams upon program completion"
                    },
                    {
                        "type": "short_answer",
                        "question": "Describe the expected flow for final exam access.",
                        "correctAnswer": "Student completes all courses in program, then gains access to final exam",
                        "points": 25,
                        "explanation": "The flow should be: course completion → program completion → final exam access"
                    },
                    {
                        "type": "multiple_choice",
                        "question": "What should happen if a student hasn't completed all program courses?",
                        "options": ["Show final exam anyway", "Show 'no final exam' message", "Show 'complete courses first' message", "Redirect to courses"],
                        "correctAnswer": "Show 'complete courses first' message",
                        "points": 25,
                        "explanation": "Students should be guided to complete remaining courses first"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            response = requests.post(f"{BACKEND_URL}/final-tests", json=final_exam_data, headers=headers)
            
            if response.status_code == 200:
                final_exam = response.json()
                self.created_data['final_tests'].append(final_exam)
                
                print(f"  ✅ Created final exam: {final_exam['title']}")
                print(f"     Final Exam ID: {final_exam['id']}")
                print(f"     Program ID: {final_exam['programId']}")
                print(f"     Program Name: {final_exam.get('programName', 'Unknown')}")
                print(f"     Published: {final_exam.get('isPublished', False)}")
                print(f"     Question Count: {final_exam.get('questionCount', 0)}")
                print(f"     Total Points: {final_exam.get('totalPoints', 0)}")
                
                self.log_result("Create Final Exam", True, f"Successfully created final exam with {final_exam.get('questionCount', 0)} questions")
                return True
            else:
                self.log_result("Create Final Exam", False, f"Failed to create final exam: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Final Exam", False, f"Exception: {str(e)}")
            return False
    
    def create_classroom_and_enroll_student(self) -> bool:
        """Create a classroom with the program and enroll the student."""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.created_data['programs']:
                self.log_result("Create Classroom", False, "No programs available for classroom creation")
                return False
            
            program = self.created_data['programs'][0]
            
            # First, get all users to find an instructor
            users_response = requests.get(f"{BACKEND_URL}/auth/admin/users", headers=headers)
            if users_response.status_code != 200:
                self.log_result("Create Classroom", False, "Could not retrieve users list")
                return False
            
            users = users_response.json()
            instructor_user = None
            
            # Look for an instructor user
            for user in users:
                if user.get('role') == 'instructor':
                    instructor_user = user
                    break
            
            # If no instructor found, create one
            if not instructor_user:
                instructor_data = {
                    "email": "test.instructor@example.com",
                    "username": "test_instructor",
                    "full_name": "Test Instructor",
                    "role": "instructor",
                    "department": "Testing",
                    "temporary_password": "TestInstructor123!"
                }
                
                create_instructor_response = requests.post(
                    f"{BACKEND_URL}/auth/admin/create-user", 
                    json=instructor_data, 
                    headers=headers
                )
                
                if create_instructor_response.status_code == 200:
                    instructor_user = create_instructor_response.json()
                    print(f"  ✅ Created instructor user: {instructor_user['full_name']}")
                else:
                    print(f"  ❌ Failed to create instructor: {create_instructor_response.status_code}")
                    print(f"     Error: {create_instructor_response.json()}")
                    self.log_result("Create Classroom", False, f"Failed to create instructor: {create_instructor_response.status_code}", create_instructor_response.json())
                    return False
            
            classroom_data = {
                "name": "Final Exam Test Classroom",
                "description": "Test classroom for debugging final exam access",
                "courseIds": program['courseIds'],
                "programIds": [program['id']],
                "studentIds": [self.student_user['id']],
                "instructorId": self.admin_user['id'],
                "trainerId": instructor_user['id'],  # Use instructor user
                "startDate": datetime.now().isoformat(),
                "endDate": None,
                "isActive": True
            }
            
            response = requests.post(f"{BACKEND_URL}/classrooms", json=classroom_data, headers=headers)
            
            if response.status_code == 200:
                classroom = response.json()
                self.created_data['classrooms'].append(classroom)
                
                print(f"  ✅ Created classroom: {classroom['name']}")
                print(f"     Classroom ID: {classroom['id']}")
                print(f"     Program IDs: {classroom.get('programIds', [])}")
                print(f"     Course IDs: {classroom.get('courseIds', [])}")
                print(f"     Student Count: {len(classroom.get('studentIds', []))}")
                print(f"     Trainer: {instructor_user['full_name']}")
                
                self.log_result("Create Classroom", True, f"Successfully created classroom with student enrolled")
                return True
            else:
                self.log_result("Create Classroom", False, f"Failed to create classroom: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Classroom", False, f"Exception: {str(e)}")
            return False
    
    def test_final_exam_access_flow(self) -> bool:
        """Test the complete final exam access flow."""
        try:
            print(f"\n=== FINAL EXAM ACCESS FLOW TEST ===")
            
            # Step 1: Check student enrollments
            headers = {"Authorization": f"Bearer {self.student_token}"}
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if enrollments_response.status_code != 200:
                self.log_result("Final Exam Access Flow", False, "Could not retrieve student enrollments")
                return False
            
            enrollments = enrollments_response.json()
            print(f"Student Enrollments: {len(enrollments)}")
            
            # Step 2: Check program access
            if not self.created_data['programs']:
                self.log_result("Final Exam Access Flow", False, "No test programs available")
                return False
            
            program = self.created_data['programs'][0]
            program_id = program['id']
            
            # Step 3: Test final exam retrieval with program filter
            final_tests_response = requests.get(
                f"{BACKEND_URL}/final-tests?program_id={program_id}&published_only=true",
                headers=headers
            )
            
            print(f"\nTesting final exam access for program: {program['title']}")
            print(f"Program ID: {program_id}")
            
            if final_tests_response.status_code == 200:
                final_tests = final_tests_response.json()
                print(f"Final Tests Found: {len(final_tests)}")
                
                if len(final_tests) > 0:
                    for test in final_tests:
                        print(f"  - {test['title']} (ID: {test['id']})")
                        print(f"    Program ID: {test['programId']}")
                        print(f"    Published: {test.get('isPublished', False)}")
                        
                        # Verify program ID matches
                        if test['programId'] == program_id:
                            print(f"    ✅ Program ID matches")
                        else:
                            print(f"    ❌ Program ID mismatch: expected {program_id}, got {test['programId']}")
                    
                    self.log_result("Final Exam Access Flow", True, f"Successfully retrieved {len(final_tests)} final exams for program")
                    return True
                else:
                    print(f"  ❌ No final exams found for program {program_id}")
                    
                    # Debug: Check all final tests
                    all_tests_response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers)
                    if all_tests_response.status_code == 200:
                        all_tests = all_tests_response.json()
                        print(f"\nDEBUG: All final tests in system: {len(all_tests)}")
                        for test in all_tests:
                            print(f"  - {test['title']} (Program ID: {test['programId']})")
                    
                    self.log_result("Final Exam Access Flow", False, f"No final exams found for program {program_id}")
                    return False
            else:
                self.log_result("Final Exam Access Flow", False, f"Failed to retrieve final tests: {final_tests_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Final Exam Access Flow", False, f"Exception: {str(e)}")
            return False
    
    def simulate_course_completion(self) -> bool:
        """Simulate completing all courses in the program."""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            if not self.created_data['programs']:
                self.log_result("Simulate Course Completion", False, "No programs available")
                return False
            
            program = self.created_data['programs'][0]
            course_ids = program['courseIds']
            
            print(f"\n=== SIMULATING COURSE COMPLETION ===")
            print(f"Program: {program['title']}")
            print(f"Courses to complete: {len(course_ids)}")
            
            completed_count = 0
            
            for course_id in course_ids:
                # First enroll in the course if not already enrolled
                enrollment_data = {"courseId": course_id}
                enroll_response = requests.post(f"{BACKEND_URL}/enrollments", json=enrollment_data, headers=headers)
                
                if enroll_response.status_code == 200:
                    print(f"  ✅ Enrolled in course {course_id}")
                elif enroll_response.status_code == 400:
                    # Already enrolled
                    print(f"  ℹ️  Already enrolled in course {course_id}")
                else:
                    print(f"  ❌ Failed to enroll in course {course_id}: {enroll_response.status_code}")
                    continue
                
                # Update progress to 100% (completed)
                progress_data = {
                    "progress": 100.0,
                    "currentModuleId": None,
                    "currentLessonId": None,
                    "lastAccessedAt": datetime.now().isoformat(),
                    "timeSpent": 3600  # 1 hour
                }
                
                progress_response = requests.put(
                    f"{BACKEND_URL}/enrollments/{course_id}/progress",
                    json=progress_data,
                    headers=headers
                )
                
                if progress_response.status_code == 200:
                    print(f"  ✅ Completed course {course_id} (100% progress)")
                    completed_count += 1
                else:
                    print(f"  ❌ Failed to update progress for course {course_id}: {progress_response.status_code}")
            
            success = completed_count == len(course_ids)
            self.log_result("Simulate Course Completion", success, f"Completed {completed_count}/{len(course_ids)} courses")
            
            return success
            
        except Exception as e:
            self.log_result("Simulate Course Completion", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete final exam setup and debug test."""
        print("🔧 FINAL EXAM SETUP AND DEBUG TEST")
        print("=" * 50)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        if not self.authenticate_student():
            print("❌ Cannot proceed without student authentication")
            return False
        
        # Setup test data
        print("\n📝 SETTING UP TEST DATA...")
        if not self.create_test_courses():
            return False
        
        if not self.create_test_program():
            return False
        
        if not self.create_final_exam():
            return False
        
        if not self.create_classroom_and_enroll_student():
            return False
        
        # Test the flow
        print("\n🧪 TESTING FINAL EXAM ACCESS FLOW...")
        if not self.simulate_course_completion():
            return False
        
        if not self.test_final_exam_access_flow():
            return False
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 FINAL EXAM SETUP AND DEBUG SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n📊 CREATED TEST DATA:")
        print(f"  Courses: {len(self.created_data['courses'])}")
        print(f"  Programs: {len(self.created_data['programs'])}")
        print(f"  Final Tests: {len(self.created_data['final_tests'])}")
        print(f"  Classrooms: {len(self.created_data['classrooms'])}")
        
        if self.created_data['programs']:
            program = self.created_data['programs'][0]
            print(f"\n🎯 KEY TEST DATA:")
            print(f"  Program ID: {program['id']}")
            print(f"  Program Title: {program['title']}")
            if self.created_data['final_tests']:
                final_test = self.created_data['final_tests'][0]
                print(f"  Final Test ID: {final_test['id']}")
                print(f"  Final Test Program ID: {final_test['programId']}")
                print(f"  Program ID Match: {'✅ YES' if final_test['programId'] == program['id'] else '❌ NO'}")
        
        return passed == total

if __name__ == "__main__":
    tester = FinalExamSetupTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)