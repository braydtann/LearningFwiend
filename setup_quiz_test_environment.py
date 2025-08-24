#!/usr/bin/env python3
"""
SETUP QUIZ TEST ENVIRONMENT
Reset student password and create course 'ttttt' for testing
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-rebuild.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Admin credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class QuizTestSetup:
    def __init__(self):
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                print(f"✅ Admin authenticated successfully")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False
    
    def reset_student_password(self):
        """Reset the student password to match the review request"""
        if not self.admin_token:
            return False
        
        # First, find the student
        try:
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.admin_token}'}
            )
            
            if users_response.status_code != 200:
                print(f"❌ Failed to get users: {users_response.status_code}")
                return False
            
            users = users_response.json()
            student = None
            
            for user in users:
                if user.get('email') == 'brayden.student@learningfwiend.com':
                    student = user
                    break
            
            if not student:
                print(f"❌ Student not found")
                return False
            
            # Reset password
            reset_data = {
                "user_id": student.get('id'),
                "new_temporary_password": "Cove1234!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/reset-password",
                json=reset_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.admin_token}'
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Student password reset to 'Cove1234!'")
                return True
            else:
                print(f"❌ Password reset failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error resetting password: {str(e)}")
            return False
    
    def create_course_ttttt(self):
        """Create the course 'ttttt' with quiz content"""
        if not self.admin_token:
            return False
        
        # Create a course with quiz lessons
        course_data = {
            "title": "ttttt",
            "description": "Test course for quiz submission debugging",
            "category": "Testing",
            "duration": "30 minutes",
            "accessType": "open",
            "modules": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Quiz Module",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Quiz Lesson 1",
                            "type": "quiz",
                            "content": {
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
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.admin_token}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                print(f"✅ Course 'ttttt' created successfully")
                print(f"   Course ID: {created_course.get('id')}")
                print(f"   Modules: {len(created_course.get('modules', []))}")
                return created_course
            else:
                print(f"❌ Course creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating course: {str(e)}")
            return None
    
    def enroll_student_in_course(self, course_id):
        """Enroll the student in the course"""
        if not self.admin_token:
            return False
        
        # First login as student to enroll
        student_login_data = {
            "username_or_email": "brayden.student@learningfwiend.com",
            "password": "Cove1234!"
        }
        
        try:
            # Login as student
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                print(f"❌ Student login failed: {login_response.status_code}")
                return False
            
            student_data = login_response.json()
            student_token = student_data.get('access_token')
            
            if not student_token:
                print(f"❌ No student token received")
                return False
            
            # Enroll in course
            enrollment_data = {
                "courseId": course_id
            }
            
            enrollment_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {student_token}'
                }
            )
            
            if enrollment_response.status_code == 200:
                enrollment = enrollment_response.json()
                print(f"✅ Student enrolled in course 'ttttt'")
                print(f"   Enrollment ID: {enrollment.get('id')}")
                print(f"   Progress: {enrollment.get('progress', 0)}%")
                return True
            else:
                print(f"❌ Enrollment failed: {enrollment_response.status_code}")
                print(f"Response: {enrollment_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error enrolling student: {str(e)}")
            return False
    
    def verify_setup(self):
        """Verify the setup is working"""
        print(f"\n🔍 VERIFYING SETUP...")
        
        # Test student login
        student_login_data = {
            "username_or_email": "brayden.student@learningfwiend.com",
            "password": "Cove1234!"
        }
        
        try:
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code == 200:
                print(f"✅ Student login verification: SUCCESS")
                
                student_data = login_response.json()
                student_token = student_data.get('access_token')
                
                # Check enrollments
                enrollments_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {student_token}'}
                )
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    ttttt_enrollment = None
                    
                    for enrollment in enrollments:
                        # Get course details to check title
                        course_response = requests.get(
                            f"{BACKEND_URL}/courses/{enrollment.get('courseId')}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {student_token}'}
                        )
                        
                        if course_response.status_code == 200:
                            course = course_response.json()
                            if course.get('title') == 'ttttt':
                                ttttt_enrollment = enrollment
                                break
                    
                    if ttttt_enrollment:
                        print(f"✅ Course 'ttttt' enrollment verification: SUCCESS")
                        print(f"   Course ID: {ttttt_enrollment.get('courseId')}")
                        return True
                    else:
                        print(f"❌ Course 'ttttt' enrollment verification: FAILED")
                        return False
                else:
                    print(f"❌ Enrollments check failed: {enrollments_response.status_code}")
                    return False
            else:
                print(f"❌ Student login verification: FAILED ({login_response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {str(e)}")
            return False
    
    def run_setup(self):
        """Run complete setup"""
        print("🔧 SETTING UP QUIZ TEST ENVIRONMENT")
        print("=" * 60)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Setup failed - cannot authenticate as admin")
            return False
        
        # Step 2: Reset student password
        print(f"\n🔑 RESETTING STUDENT PASSWORD...")
        if not self.reset_student_password():
            print("❌ Setup failed - cannot reset student password")
            return False
        
        # Step 3: Create course 'ttttt'
        print(f"\n📚 CREATING COURSE 'ttttt'...")
        course = self.create_course_ttttt()
        if not course:
            print("❌ Setup failed - cannot create course")
            return False
        
        # Step 4: Enroll student in course
        print(f"\n📝 ENROLLING STUDENT IN COURSE...")
        if not self.enroll_student_in_course(course.get('id')):
            print("❌ Setup failed - cannot enroll student")
            return False
        
        # Step 5: Verify setup
        if not self.verify_setup():
            print("❌ Setup verification failed")
            return False
        
        print(f"\n🎉 QUIZ TEST ENVIRONMENT SETUP COMPLETE!")
        print("=" * 60)
        print(f"✅ Student: brayden.student@learningfwiend.com / Cove1234!")
        print(f"✅ Course: 'ttttt' (ID: {course.get('id')})")
        print(f"✅ Student enrolled and ready for quiz submission testing")
        
        return True

if __name__ == "__main__":
    setup = QuizTestSetup()
    setup.run_setup()