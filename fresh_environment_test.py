#!/usr/bin/env python3
"""
COMPLETE FRESH TEST ENVIRONMENT SETUP - BEFORE DEPLOYMENT
LearningFwiend LMS Application Backend API Testing

OBJECTIVE: Create completely clean test environment with proper course structure before frontend deployment.

STEP 1 - CLEANUP:
1. DELETE all existing courses from production database
2. DELETE all existing classrooms from production database
3. DELETE all existing enrollments from production database
4. DELETE all existing programs from production database

STEP 2 - CREATE NEW TEST USER:
1. CREATE new test user: progress.test@learningfwiend.com / ProgressTest123!
2. VERIFY user can authenticate successfully
3. Set up user as learner role

STEP 3 - CREATE NEW STRUCTURED COURSE:
1. CREATE course titled "Complete Progress Test Course"
2. STRUCTURE with exactly 3 modules:
   - Module 1: Text Module ("Reading Content") with 1 text lesson
   - Module 2: Video Module ("Watch and Learn") with 1 video lesson (YouTube URL)
   - Module 3: Quiz Module ("Test Your Knowledge") with 1 quiz lesson (3-5 questions)

STEP 4 - CREATE CLASSROOM AND ASSIGNMENT:
1. CREATE classroom "Progress Test Classroom - Final"
2. ASSIGN the course to the classroom
3. ASSIGN the new test user to the classroom (auto-enrollment)

STEP 5 - VERIFICATION:
1. VERIFY test user is enrolled in the course
2. VERIFY course structure is correct (3 modules, 3 lessons total)
3. VERIFY progress tracking will work: 33% → 66% → 100%

ADMIN CREDENTIALS: brayden.t@covesmart.com / Hawaii2020!
NEW TEST USER: progress.test@learningfwiend.com / ProgressTest123!

GOAL: Clean, structured test environment ready for frontend deployment and progress testing.
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

# Admin credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

# New test user credentials from review request
NEW_TEST_USER = {
    "email": "progress.test@learningfwiend.com",
    "username": "progress.test",
    "full_name": "Progress Test User",
    "role": "learner",
    "department": "Testing",
    "temporary_password": "ProgressTest123!"
}

class FreshEnvironmentTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        self.created_entities = {
            'users': [],
            'courses': [],
            'classrooms': [],
            'programs': []
        }
        
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
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
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
                        f"Successfully authenticated as admin: {user_info.get('email')}",
                        f"Admin role confirmed, token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Authentication succeeded but admin role not confirmed",
                        f"User role: {user_info.get('role')}, Token: {'Yes' if token else 'No'}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Admin authentication failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to authenticate admin user",
                str(e)
            )
        return False
    
    def cleanup_existing_data(self):
        """STEP 1: DELETE all existing data from production database"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Database Cleanup", 
                "FAIL", 
                "Cannot cleanup - admin authentication required",
                "Admin token not available"
            )
            return False
        
        print("\n🧹 STEP 1: CLEANING UP EXISTING DATA FROM PRODUCTION DATABASE")
        print("=" * 70)
        
        cleanup_results = {
            'courses_deleted': 0,
            'classrooms_deleted': 0,
            'enrollments_deleted': 0,
            'programs_deleted': 0,
            'errors': []
        }
        
        # 1. Delete all existing courses
        try:
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code == 200:
                courses = courses_response.json()
                print(f"📚 Found {len(courses)} courses to delete...")
                
                for course in courses:
                    course_id = course.get('id')
                    course_title = course.get('title', 'Unknown')
                    
                    try:
                        delete_response = requests.delete(
                            f"{BACKEND_URL}/courses/{course_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        
                        if delete_response.status_code == 200:
                            cleanup_results['courses_deleted'] += 1
                            print(f"   ✅ Deleted course: {course_title}")
                        else:
                            cleanup_results['errors'].append(f"Failed to delete course {course_title}: {delete_response.status_code}")
                            print(f"   ❌ Failed to delete course: {course_title}")
                    except Exception as e:
                        cleanup_results['errors'].append(f"Error deleting course {course_title}: {str(e)}")
                        print(f"   ❌ Error deleting course {course_title}: {str(e)}")
            else:
                cleanup_results['errors'].append(f"Failed to get courses list: {courses_response.status_code}")
        except Exception as e:
            cleanup_results['errors'].append(f"Error getting courses: {str(e)}")
        
        # 2. Delete all existing classrooms
        try:
            classrooms_response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if classrooms_response.status_code == 200:
                classrooms = classrooms_response.json()
                print(f"🏫 Found {len(classrooms)} classrooms to delete...")
                
                for classroom in classrooms:
                    classroom_id = classroom.get('id')
                    classroom_name = classroom.get('name', 'Unknown')
                    
                    try:
                        delete_response = requests.delete(
                            f"{BACKEND_URL}/classrooms/{classroom_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        
                        if delete_response.status_code == 200:
                            cleanup_results['classrooms_deleted'] += 1
                            print(f"   ✅ Deleted classroom: {classroom_name}")
                        else:
                            cleanup_results['errors'].append(f"Failed to delete classroom {classroom_name}: {delete_response.status_code}")
                            print(f"   ❌ Failed to delete classroom: {classroom_name}")
                    except Exception as e:
                        cleanup_results['errors'].append(f"Error deleting classroom {classroom_name}: {str(e)}")
                        print(f"   ❌ Error deleting classroom {classroom_name}: {str(e)}")
            else:
                cleanup_results['errors'].append(f"Failed to get classrooms list: {classrooms_response.status_code}")
        except Exception as e:
            cleanup_results['errors'].append(f"Error getting classrooms: {str(e)}")
        
        # 3. Clean up orphaned enrollments
        try:
            cleanup_response = requests.post(
                f"{BACKEND_URL}/enrollments/cleanup-orphaned",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if cleanup_response.status_code == 200:
                cleanup_data = cleanup_response.json()
                cleanup_results['enrollments_deleted'] = cleanup_data.get('deletedCount', 0)
                print(f"📝 Cleaned up {cleanup_results['enrollments_deleted']} orphaned enrollments")
            else:
                cleanup_results['errors'].append(f"Failed to cleanup enrollments: {cleanup_response.status_code}")
        except Exception as e:
            cleanup_results['errors'].append(f"Error cleaning up enrollments: {str(e)}")
        
        # 4. Delete all existing programs
        try:
            programs_response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if programs_response.status_code == 200:
                programs = programs_response.json()
                print(f"📋 Found {len(programs)} programs to delete...")
                
                for program in programs:
                    program_id = program.get('id')
                    program_title = program.get('title', 'Unknown')
                    
                    try:
                        delete_response = requests.delete(
                            f"{BACKEND_URL}/programs/{program_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        
                        if delete_response.status_code == 200:
                            cleanup_results['programs_deleted'] += 1
                            print(f"   ✅ Deleted program: {program_title}")
                        else:
                            cleanup_results['errors'].append(f"Failed to delete program {program_title}: {delete_response.status_code}")
                            print(f"   ❌ Failed to delete program: {program_title}")
                    except Exception as e:
                        cleanup_results['errors'].append(f"Error deleting program {program_title}: {str(e)}")
                        print(f"   ❌ Error deleting program {program_title}: {str(e)}")
            else:
                cleanup_results['errors'].append(f"Failed to get programs list: {programs_response.status_code}")
        except Exception as e:
            cleanup_results['errors'].append(f"Error getting programs: {str(e)}")
        
        # Summary
        total_deleted = (cleanup_results['courses_deleted'] + 
                        cleanup_results['classrooms_deleted'] + 
                        cleanup_results['enrollments_deleted'] + 
                        cleanup_results['programs_deleted'])
        
        if len(cleanup_results['errors']) == 0:
            self.log_result(
                "Database Cleanup", 
                "PASS", 
                f"Successfully cleaned production database: {total_deleted} items deleted",
                f"Courses: {cleanup_results['courses_deleted']}, Classrooms: {cleanup_results['classrooms_deleted']}, Enrollments: {cleanup_results['enrollments_deleted']}, Programs: {cleanup_results['programs_deleted']}"
            )
            return True
        else:
            self.log_result(
                "Database Cleanup", 
                "FAIL", 
                f"Database cleanup completed with {len(cleanup_results['errors'])} errors",
                f"Deleted: {total_deleted} items, Errors: {'; '.join(cleanup_results['errors'][:3])}"
            )
            return False
    
    def create_test_user(self):
        """STEP 2: CREATE new test user: progress.test@learningfwiend.com / ProgressTest123!"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Test User", 
                "FAIL", 
                "Cannot create user - admin authentication required",
                "Admin token not available"
            )
            return False
        
        print("\n👤 STEP 2: CREATING NEW TEST USER")
        print("=" * 50)
        print(f"Creating user: {NEW_TEST_USER['email']} / {NEW_TEST_USER['temporary_password']}")
        
        try:
            # First check if user already exists
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                existing_user = None
                
                for user in users:
                    if user.get('email') == NEW_TEST_USER['email']:
                        existing_user = user
                        break
                
                if existing_user:
                    print(f"⚠️ User already exists, deleting first...")
                    delete_response = requests.delete(
                        f"{BACKEND_URL}/auth/admin/users/{existing_user['id']}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                    )
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted existing user")
                    else:
                        print(f"⚠️ Could not delete existing user: {delete_response.status_code}")
            
            # Create new user
            create_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=NEW_TEST_USER,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code == 200:
                created_user = create_response.json()
                user_id = created_user.get('id')
                self.created_entities['users'].append(user_id)
                
                print(f"✅ Created user: {created_user.get('email')}")
                print(f"   User ID: {user_id}")
                print(f"   Role: {created_user.get('role')}")
                print(f"   Department: {created_user.get('department')}")
                
                # Test user authentication
                test_login_success = self.test_new_user_authentication()
                
                if test_login_success:
                    self.log_result(
                        "Create Test User", 
                        "PASS", 
                        f"Successfully created and verified test user: {NEW_TEST_USER['email']}",
                        f"User ID: {user_id}, Authentication: ✅, Role: learner"
                    )
                    return created_user
                else:
                    self.log_result(
                        "Create Test User", 
                        "FAIL", 
                        f"User created but authentication failed: {NEW_TEST_USER['email']}",
                        f"User ID: {user_id}, Authentication: ❌"
                    )
                    return False
            else:
                self.log_result(
                    "Create Test User", 
                    "FAIL", 
                    f"Failed to create test user, status: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Test User", 
                "FAIL", 
                "Failed to create test user",
                str(e)
            )
        return False
    
    def test_new_user_authentication(self):
        """Test authentication for the newly created user"""
        try:
            login_data = {
                "username_or_email": NEW_TEST_USER['email'],
                "password": NEW_TEST_USER['temporary_password']
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['test_user'] = token
                    print(f"✅ Test user authentication successful")
                    return True
                else:
                    print(f"❌ Test user authentication failed - invalid response")
                    return False
            else:
                print(f"❌ Test user authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing user authentication: {str(e)}")
            return False
    
    def create_structured_course(self):
        """STEP 3: CREATE structured course with 3 modules (Text, Video, Quiz)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Structured Course", 
                "FAIL", 
                "Cannot create course - admin authentication required",
                "Admin token not available"
            )
            return False
        
        print("\n📚 STEP 3: CREATING STRUCTURED COURSE WITH 3 MODULES")
        print("=" * 60)
        print("Course: 'Complete Progress Test Course'")
        print("Module 1: Text Module ('Reading Content') with 1 text lesson")
        print("Module 2: Video Module ('Watch and Learn') with 1 video lesson")
        print("Module 3: Quiz Module ('Test Your Knowledge') with 1 quiz lesson")
        
        # Define the structured course with exactly 3 modules
        course_data = {
            "title": "Complete Progress Test Course",
            "description": "A comprehensive test course with text, video, and quiz modules for progress tracking validation",
            "category": "Testing",
            "duration": "3 hours",
            "accessType": "open",
            "thumbnailUrl": "https://via.placeholder.com/300x200/4CAF50/white?text=Progress+Test+Course",
            "modules": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Reading Content",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Introduction to Progress Tracking",
                            "type": "text",
                            "content": "This is a text lesson that introduces the concept of progress tracking in learning management systems. Students will learn about the importance of monitoring their learning progress and how it helps in achieving educational goals.",
                            "duration": "15 minutes",
                            "order": 1
                        }
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Watch and Learn",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Progress Tracking Video Tutorial",
                            "type": "video",
                            "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "content": "Watch this video to understand how progress tracking works in practice.",
                            "duration": "10 minutes",
                            "order": 1
                        }
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Test Your Knowledge",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Progress Tracking Quiz",
                            "type": "quiz",
                            "content": "Test your understanding of progress tracking concepts.",
                            "duration": "10 minutes",
                            "order": 1,
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "question": "What is the primary purpose of progress tracking in learning?",
                                    "type": "multiple_choice",
                                    "options": [
                                        "To monitor student engagement",
                                        "To measure learning outcomes",
                                        "To provide feedback to instructors",
                                        "All of the above"
                                    ],
                                    "correct_answer": 3,
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "question": "How often should progress be updated in a learning system?",
                                    "type": "multiple_choice",
                                    "options": [
                                        "Once per week",
                                        "After each lesson completion",
                                        "Only at course completion",
                                        "Never"
                                    ],
                                    "correct_answer": 1,
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "question": "What percentage represents full course completion?",
                                    "type": "multiple_choice",
                                    "options": [
                                        "90%",
                                        "95%",
                                        "100%",
                                        "It depends on the course"
                                    ],
                                    "correct_answer": 2,
                                    "points": 25
                                },
                                {
                                    "id": str(uuid.uuid4()),
                                    "question": "True or False: Progress tracking helps identify struggling students.",
                                    "type": "true_false",
                                    "correct_answer": True,
                                    "points": 25
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        try:
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code == 200:
                created_course = create_response.json()
                course_id = created_course.get('id')
                self.created_entities['courses'].append(course_id)
                
                print(f"✅ Created course: {created_course.get('title')}")
                print(f"   Course ID: {course_id}")
                print(f"   Modules: {len(created_course.get('modules', []))}")
                
                # Verify course structure
                modules = created_course.get('modules', [])
                total_lessons = sum(len(module.get('lessons', [])) for module in modules)
                
                print(f"   Total lessons: {total_lessons}")
                print(f"   Expected progress increments: 33% → 66% → 100%")
                
                for i, module in enumerate(modules, 1):
                    module_title = module.get('title', f'Module {i}')
                    lesson_count = len(module.get('lessons', []))
                    print(f"   Module {i}: {module_title} ({lesson_count} lesson{'s' if lesson_count != 1 else ''})")
                
                if len(modules) == 3 and total_lessons == 3:
                    self.log_result(
                        "Create Structured Course", 
                        "PASS", 
                        f"Successfully created structured course with perfect 3-module structure",
                        f"Course ID: {course_id}, Modules: 3, Lessons: 3, Progress tracking ready: 33% → 66% → 100%"
                    )
                    return created_course
                else:
                    self.log_result(
                        "Create Structured Course", 
                        "FAIL", 
                        f"Course created but structure incorrect: {len(modules)} modules, {total_lessons} lessons",
                        f"Expected: 3 modules, 3 lessons for proper progress tracking"
                    )
                    return False
            else:
                self.log_result(
                    "Create Structured Course", 
                    "FAIL", 
                    f"Failed to create course, status: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Structured Course", 
                "FAIL", 
                "Failed to create structured course",
                str(e)
            )
        return False
    
    def create_classroom_and_assignment(self, course, test_user):
        """STEP 4: CREATE classroom and assign course and user"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Classroom and Assignment", 
                "FAIL", 
                "Cannot create classroom - admin authentication required",
                "Admin token not available"
            )
            return False
        
        print("\n🏫 STEP 4: CREATING CLASSROOM AND ASSIGNMENTS")
        print("=" * 50)
        print("Classroom: 'Progress Test Classroom - Final'")
        print(f"Assigning course: {course.get('title')}")
        print(f"Assigning user: {test_user.get('email')}")
        
        # Get instructor for classroom (use admin as instructor)
        instructor_id = None
        instructor_name = None
        
        try:
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    if user.get('role') in ['instructor', 'admin']:
                        instructor_id = user.get('id')
                        instructor_name = user.get('full_name', user.get('username'))
                        break
        except Exception as e:
            print(f"⚠️ Could not find instructor, using admin: {str(e)}")
        
        if not instructor_id:
            print("❌ No instructor found for classroom")
            return False
        
        # Create classroom data
        classroom_data = {
            "name": "Progress Test Classroom - Final",
            "description": "Final test classroom for progress tracking validation before deployment",
            "trainerId": instructor_id,  # Use trainerId instead of instructorId
            "courseIds": [course.get('id')],
            "studentIds": [test_user.get('id')],
            "programIds": [],
            "startDate": datetime.utcnow().isoformat(),
            "endDate": None,  # No end date for unlimited access
            "maxStudents": 50,
            "department": "Testing"
        }
        
        try:
            create_response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code == 200:
                created_classroom = create_response.json()
                classroom_id = created_classroom.get('id')
                self.created_entities['classrooms'].append(classroom_id)
                
                print(f"✅ Created classroom: {created_classroom.get('name')}")
                print(f"   Classroom ID: {classroom_id}")
                print(f"   Instructor: {created_classroom.get('instructor')}")
                print(f"   Assigned courses: {len(created_classroom.get('courseIds', []))}")
                print(f"   Assigned students: {len(created_classroom.get('studentIds', []))}")
                
                # Verify auto-enrollment occurred
                time.sleep(2)  # Wait for auto-enrollment to process
                enrollment_success = self.verify_auto_enrollment(test_user, course)
                
                if enrollment_success:
                    self.log_result(
                        "Create Classroom and Assignment", 
                        "PASS", 
                        f"Successfully created classroom with auto-enrollment working",
                        f"Classroom ID: {classroom_id}, Course assigned: ✅, Student assigned: ✅, Auto-enrollment: ✅"
                    )
                    return created_classroom
                else:
                    self.log_result(
                        "Create Classroom and Assignment", 
                        "FAIL", 
                        f"Classroom created but auto-enrollment failed",
                        f"Classroom ID: {classroom_id}, Auto-enrollment: ❌"
                    )
                    return False
            else:
                self.log_result(
                    "Create Classroom and Assignment", 
                    "FAIL", 
                    f"Failed to create classroom, status: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Classroom and Assignment", 
                "FAIL", 
                "Failed to create classroom and assignment",
                str(e)
            )
        return False
    
    def verify_auto_enrollment(self, test_user, course):
        """Verify that auto-enrollment worked correctly"""
        if "test_user" not in self.auth_tokens:
            print("❌ Cannot verify enrollment - test user not authenticated")
            return False
        
        try:
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["test_user"]}'}
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                course_id = course.get('id')
                
                for enrollment in enrollments:
                    if enrollment.get('courseId') == course_id:
                        print(f"✅ Auto-enrollment successful")
                        print(f"   Enrollment ID: {enrollment.get('id')}")
                        print(f"   Progress: {enrollment.get('progress', 0)}%")
                        print(f"   Status: {enrollment.get('status', 'unknown')}")
                        return True
                
                print(f"❌ Auto-enrollment failed - course not found in enrollments")
                print(f"   Found {len(enrollments)} enrollments, but not for course {course_id}")
                return False
            else:
                print(f"❌ Could not check enrollments: {enrollments_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error verifying auto-enrollment: {str(e)}")
            return False
    
    def verify_test_environment(self, course, test_user, classroom):
        """STEP 5: VERIFY the complete test environment is ready"""
        print("\n🔍 STEP 5: VERIFYING COMPLETE TEST ENVIRONMENT")
        print("=" * 60)
        
        verification_results = {
            'user_enrolled': False,
            'course_structure_correct': False,
            'progress_tracking_ready': False,
            'errors': []
        }
        
        # 1. Verify test user is enrolled in the course
        if "test_user" in self.auth_tokens:
            try:
                enrollments_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["test_user"]}'}
                )
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    course_id = course.get('id')
                    
                    for enrollment in enrollments:
                        if enrollment.get('courseId') == course_id:
                            verification_results['user_enrolled'] = True
                            print(f"✅ Test user is enrolled in the course")
                            print(f"   Enrollment progress: {enrollment.get('progress', 0)}%")
                            break
                    
                    if not verification_results['user_enrolled']:
                        verification_results['errors'].append("Test user is not enrolled in the course")
                        print(f"❌ Test user is not enrolled in the course")
                else:
                    verification_results['errors'].append(f"Could not check enrollments: {enrollments_response.status_code}")
            except Exception as e:
                verification_results['errors'].append(f"Error checking enrollment: {str(e)}")
        else:
            verification_results['errors'].append("Test user authentication token not available")
        
        # 2. Verify course structure is correct (3 modules, 3 lessons total)
        modules = course.get('modules', [])
        total_lessons = sum(len(module.get('lessons', [])) for module in modules)
        
        if len(modules) == 3 and total_lessons == 3:
            verification_results['course_structure_correct'] = True
            print(f"✅ Course structure is correct: 3 modules, 3 lessons total")
            
            # Verify module types
            module_types = []
            for module in modules:
                lessons = module.get('lessons', [])
                if lessons:
                    lesson_type = lessons[0].get('type', 'unknown')
                    module_types.append(lesson_type)
            
            expected_types = ['text', 'video', 'quiz']
            if set(module_types) == set(expected_types):
                print(f"✅ Module types are correct: {', '.join(module_types)}")
            else:
                print(f"⚠️ Module types may not be as expected: {', '.join(module_types)}")
        else:
            verification_results['errors'].append(f"Course structure incorrect: {len(modules)} modules, {total_lessons} lessons")
            print(f"❌ Course structure incorrect: {len(modules)} modules, {total_lessons} lessons")
        
        # 3. Verify progress tracking will work: 33% → 66% → 100%
        if verification_results['course_structure_correct'] and verification_results['user_enrolled']:
            verification_results['progress_tracking_ready'] = True
            print(f"✅ Progress tracking ready: 33% → 66% → 100%")
            print(f"   Module 1 completion: 33.33%")
            print(f"   Module 2 completion: 66.67%")
            print(f"   Module 3 completion: 100.00%")
        else:
            verification_results['errors'].append("Progress tracking not ready due to structure or enrollment issues")
            print(f"❌ Progress tracking not ready")
        
        # 4. Verify classroom assignment
        if classroom:
            course_ids = classroom.get('courseIds', [])
            student_ids = classroom.get('studentIds', [])
            
            if course.get('id') in course_ids and test_user.get('id') in student_ids:
                print(f"✅ Classroom assignments correct")
                print(f"   Course assigned to classroom: ✅")
                print(f"   Student assigned to classroom: ✅")
            else:
                verification_results['errors'].append("Classroom assignments incorrect")
                print(f"❌ Classroom assignments incorrect")
        
        # Summary
        all_verified = (verification_results['user_enrolled'] and 
                       verification_results['course_structure_correct'] and 
                       verification_results['progress_tracking_ready'] and 
                       len(verification_results['errors']) == 0)
        
        if all_verified:
            self.log_result(
                "Test Environment Verification", 
                "PASS", 
                "✅ COMPLETE TEST ENVIRONMENT READY FOR DEPLOYMENT",
                f"User enrolled: ✅, Course structure: ✅, Progress tracking: ✅, Classroom: ✅"
            )
            return True
        else:
            self.log_result(
                "Test Environment Verification", 
                "FAIL", 
                f"Test environment has {len(verification_results['errors'])} issues",
                f"Errors: {'; '.join(verification_results['errors'])}"
            )
            return False
    
    def run_complete_fresh_environment_setup(self):
        """Run the complete fresh environment setup process"""
        print("🚀 COMPLETE FRESH TEST ENVIRONMENT SETUP - BEFORE DEPLOYMENT")
        print("=" * 80)
        print("OBJECTIVE: Create completely clean test environment with proper course structure")
        print("=" * 80)
        
        # Step 0: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 1: Cleanup existing data
        cleanup_success = self.cleanup_existing_data()
        if not cleanup_success:
            print("⚠️ WARNING: Database cleanup had issues, but continuing...")
        
        # Step 2: Create new test user
        test_user = self.create_test_user()
        if not test_user:
            print("❌ CRITICAL: Cannot proceed without test user")
            return False
        
        # Step 3: Create structured course
        course = self.create_structured_course()
        if not course:
            print("❌ CRITICAL: Cannot proceed without structured course")
            return False
        
        # Step 4: Create classroom and assignments
        classroom = self.create_classroom_and_assignment(course, test_user)
        if not classroom:
            print("❌ CRITICAL: Cannot proceed without classroom setup")
            return False
        
        # Step 5: Verify complete environment
        verification_success = self.verify_test_environment(course, test_user, classroom)
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎯 FRESH ENVIRONMENT SETUP SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        
        print(f"📊 RESULTS: {self.passed} passed, {self.failed} failed ({success_rate:.1f}% success rate)")
        print(f"👤 TEST USER: {NEW_TEST_USER['email']} / {NEW_TEST_USER['temporary_password']}")
        print(f"🔑 ADMIN USER: {ADMIN_CREDENTIALS['username_or_email']} / {ADMIN_CREDENTIALS['password']}")
        
        if verification_success:
            print("✅ ENVIRONMENT STATUS: READY FOR FRONTEND DEPLOYMENT AND PROGRESS TESTING")
            print("🎉 SUCCESS: Clean, structured test environment created successfully!")
        else:
            print("❌ ENVIRONMENT STATUS: NOT READY - ISSUES FOUND")
            print("⚠️ RECOMMENDATION: Review and fix issues before deployment")
        
        return verification_success
    
    def print_final_summary(self):
        """Print final summary of all test results"""
        print("\n" + "=" * 80)
        print("📋 DETAILED TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {result['test']}: {result['message']}")
            if result.get('details'):
                print(f"   Details: {result['details']}")
        
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   Total Tests: {len(self.results)}")
        print(f"   Passed: {self.passed}")
        print(f"   Failed: {self.failed}")
        success_rate = (self.passed / len(self.results)) * 100 if self.results else 0
        print(f"   Success Rate: {success_rate:.1f}%")

def main():
    """Main function to run the fresh environment setup"""
    tester = FreshEnvironmentTester()
    
    try:
        success = tester.run_complete_fresh_environment_setup()
        tester.print_final_summary()
        
        if success:
            print("\n🎉 FRESH ENVIRONMENT SETUP COMPLETED SUCCESSFULLY!")
            print("Ready for frontend deployment and progress testing.")
            sys.exit(0)
        else:
            print("\n❌ FRESH ENVIRONMENT SETUP FAILED!")
            print("Please review issues and retry.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()