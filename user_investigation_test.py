#!/usr/bin/env python3
"""
USER INVESTIGATION FOR QUIZ SUBMISSION TESTING
Find or create the student user mentioned in the review request
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Admin credentials to check/create users
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class UserInvestigator:
    def __init__(self):
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin to manage users"""
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
                user_info = data.get('user', {})
                print(f"✅ Admin authenticated: {user_info.get('full_name')} ({user_info.get('email')})")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False
    
    def list_all_users(self):
        """List all users in the system"""
        if not self.admin_token:
            print("❌ No admin token available")
            return []
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.admin_token}'}
            )
            
            if response.status_code == 200:
                users = response.json()
                print(f"\n📋 FOUND {len(users)} USERS IN SYSTEM:")
                print("=" * 60)
                
                students = []
                for user in users:
                    role = user.get('role', 'unknown')
                    email = user.get('email', 'N/A')
                    username = user.get('username', 'N/A')
                    full_name = user.get('full_name', 'N/A')
                    is_active = user.get('is_active', False)
                    first_login_required = user.get('first_login_required', False)
                    
                    status_flags = []
                    if not is_active:
                        status_flags.append("INACTIVE")
                    if first_login_required:
                        status_flags.append("TEMP_PASSWORD")
                    
                    status_str = f" [{', '.join(status_flags)}]" if status_flags else ""
                    
                    print(f"👤 {full_name} | {email} | {username} | {role.upper()}{status_str}")
                    
                    if role == 'learner':
                        students.append(user)
                
                print(f"\n📊 BREAKDOWN: {len(students)} students found")
                return users
            else:
                print(f"❌ Failed to get users: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error listing users: {str(e)}")
            return []
    
    def find_target_student(self):
        """Find the target student or similar students"""
        users = self.list_all_users()
        
        # Look for the exact student mentioned in review
        target_email = "brayden.student@learningfwiend.com"
        
        exact_match = None
        similar_students = []
        
        for user in users:
            if user.get('email') == target_email:
                exact_match = user
            elif user.get('role') == 'learner' and 'brayden' in user.get('email', '').lower():
                similar_students.append(user)
        
        if exact_match:
            print(f"\n✅ FOUND EXACT MATCH: {exact_match.get('email')}")
            return exact_match
        elif similar_students:
            print(f"\n⚠️ FOUND SIMILAR STUDENTS:")
            for student in similar_students:
                print(f"   - {student.get('email')} ({student.get('full_name')})")
            return similar_students[0]  # Return first similar student
        else:
            print(f"\n❌ TARGET STUDENT NOT FOUND: {target_email}")
            return None
    
    def create_target_student(self):
        """Create the target student if they don't exist"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None
        
        student_data = {
            "email": "brayden.student@learningfwiend.com",
            "username": "brayden.student",
            "full_name": "Brayden Student",
            "role": "learner",
            "department": "Testing",
            "temporary_password": "Cove1234!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=student_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.admin_token}'
                }
            )
            
            if response.status_code == 200:
                created_user = response.json()
                print(f"✅ CREATED TARGET STUDENT: {created_user.get('email')}")
                print(f"   Username: {created_user.get('username')}")
                print(f"   Password: Cove1234!")
                print(f"   First login required: {created_user.get('first_login_required')}")
                return created_user
            else:
                print(f"❌ Failed to create student: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating student: {str(e)}")
            return None
    
    def test_student_login(self, student_email, password):
        """Test login with student credentials"""
        login_data = {
            "username_or_email": student_email,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                print(f"✅ STUDENT LOGIN SUCCESS: {user_info.get('full_name')}")
                print(f"   Email: {user_info.get('email')}")
                print(f"   Role: {user_info.get('role')}")
                print(f"   Password change required: {requires_password_change}")
                return True
            else:
                print(f"❌ STUDENT LOGIN FAILED: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Student login error: {str(e)}")
            return False
    
    def find_course_ttttt(self):
        """Find the course 'ttttt' mentioned in the review"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.admin_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                print(f"\n📚 FOUND {len(courses)} COURSES:")
                
                target_course = None
                for course in courses:
                    title = course.get('title', 'Untitled')
                    course_id = course.get('id')
                    instructor = course.get('instructor', 'Unknown')
                    
                    print(f"   📖 {title} (ID: {course_id}) by {instructor}")
                    
                    if title.lower() == 'ttttt':
                        target_course = course
                
                if target_course:
                    print(f"\n✅ FOUND TARGET COURSE 'ttttt':")
                    print(f"   ID: {target_course.get('id')}")
                    print(f"   Title: {target_course.get('title')}")
                    print(f"   Instructor: {target_course.get('instructor')}")
                    print(f"   Modules: {len(target_course.get('modules', []))}")
                    return target_course
                else:
                    print(f"\n❌ COURSE 'ttttt' NOT FOUND")
                    return None
            else:
                print(f"❌ Failed to get courses: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error finding course: {str(e)}")
            return None
    
    def run_investigation(self):
        """Run complete user investigation"""
        print("🔍 USER INVESTIGATION FOR QUIZ SUBMISSION TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin access")
            return
        
        # Step 2: Find target student
        student = self.find_target_student()
        
        # Step 3: Create student if not found
        if not student:
            print("\n🔧 CREATING TARGET STUDENT...")
            student = self.create_target_student()
        
        # Step 4: Test student login
        if student:
            print(f"\n🔑 TESTING STUDENT LOGIN...")
            self.test_student_login(student.get('email'), "Cove1234!")
        
        # Step 5: Find target course
        print(f"\n📚 LOOKING FOR COURSE 'ttttt'...")
        course = self.find_course_ttttt()
        
        # Summary
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print("=" * 40)
        print(f"✅ Admin access: {'YES' if self.admin_token else 'NO'}")
        print(f"✅ Target student: {'YES' if student else 'NO'}")
        print(f"✅ Target course: {'YES' if course else 'NO'}")
        
        if student and course:
            print(f"\n🎯 READY FOR QUIZ SUBMISSION TESTING:")
            print(f"   Student: {student.get('email')} / Cove1234!")
            print(f"   Course: {course.get('title')} (ID: {course.get('id')})")

if __name__ == "__main__":
    investigator = UserInvestigator()
    investigator.run_investigation()