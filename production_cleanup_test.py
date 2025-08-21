#!/usr/bin/env python3
"""
URGENT PRODUCTION DATABASE CLEANUP - LearningFriend LMS
CRITICAL TASK: Clean production database and create fresh test environment

OBJECTIVES:
1. CONNECT to correct production backend: https://lms-evolution.emergent.host/api
2. AUTHENTICATE with admin credentials: brayden.t@covesmart.com / Hawaii2020!
3. DELETE ALL EXISTING COURSES from production database
4. DELETE ALL EXISTING CLASSROOMS from production database  
5. DELETE ALL EXISTING ENROLLMENTS from production database
6. DELETE ALL EXISTING PROGRAMS from production database
7. CREATE FRESH TEST ENVIRONMENT exactly as specified

VERIFICATION:
- Confirm we're hitting the right backend URL that production frontend uses
- Verify admin credentials work on production backend
- Clean ALL old data from production database
- Recreate test course and classroom setup
- Ensure production site shows clean environment after cleanup
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# PRODUCTION Configuration - Using CORRECT Production Backend URL
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 30

# Admin credentials for production cleanup
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class ProductionCleanupTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.cleanup_stats = {
            'courses_deleted': 0,
            'classrooms_deleted': 0,
            'enrollments_deleted': 0,
            'programs_deleted': 0
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
    
    def test_production_backend_connectivity(self):
        """Test connectivity to CORRECT production backend"""
        print(f"\n🌐 TESTING PRODUCTION BACKEND CONNECTIVITY")
        print(f"Target URL: {BACKEND_URL}")
        print("=" * 80)
        
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Hello World':
                    self.log_result(
                        "Production Backend Connectivity", 
                        "PASS", 
                        f"✅ Successfully connected to PRODUCTION backend: {BACKEND_URL}",
                        f"Backend is responding correctly - ready for cleanup operations"
                    )
                    return True
                else:
                    self.log_result(
                        "Production Backend Connectivity", 
                        "FAIL", 
                        "Backend responded but with unexpected message",
                        f"Expected 'Hello World', got: {data}"
                    )
            else:
                self.log_result(
                    "Production Backend Connectivity", 
                    "FAIL", 
                    f"Backend not responding properly (status: {response.status_code})",
                    f"Cannot proceed with cleanup - backend unreachable"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Production Backend Connectivity", 
                "FAIL", 
                "Failed to connect to production backend",
                f"Connection error: {str(e)}"
            )
        return False
    
    def test_admin_authentication(self):
        """Test admin authentication with production credentials"""
        print(f"\n🔑 TESTING ADMIN AUTHENTICATION")
        print(f"Admin: {ADMIN_CREDENTIALS['username_or_email']}")
        print("=" * 80)
        
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
                        f"✅ Admin authentication SUCCESSFUL on production backend",
                        f"Admin: {user_info.get('full_name')} ({user_info.get('email')}) - Role: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Authentication succeeded but user is not admin or no token received",
                        f"Role: {user_info.get('role')}, Token present: {bool(token)}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"❌ CRITICAL: Admin authentication FAILED (status: {response.status_code})",
                    f"Cannot proceed with cleanup - admin access required. Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to authenticate admin",
                str(e)
            )
        return False
    
    def get_all_courses(self):
        """Get all courses from production database"""
        if "admin" not in self.auth_tokens:
            return []
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get courses: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting courses: {str(e)}")
            return []
    
    def get_all_classrooms(self):
        """Get all classrooms from production database"""
        if "admin" not in self.auth_tokens:
            return []
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get classrooms: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting classrooms: {str(e)}")
            return []
    
    def get_all_enrollments(self):
        """Get all enrollments from production database"""
        if "admin" not in self.auth_tokens:
            return []
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get enrollments: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting enrollments: {str(e)}")
            return []
    
    def get_all_programs(self):
        """Get all programs from production database"""
        if "admin" not in self.auth_tokens:
            return []
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get programs: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting programs: {str(e)}")
            return []
    
    def delete_all_courses(self):
        """DELETE ALL COURSES from production database"""
        print(f"\n🗑️ DELETING ALL COURSES FROM PRODUCTION DATABASE")
        print("=" * 80)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Delete All Courses", 
                "FAIL", 
                "No admin token available for course deletion",
                "Admin authentication required"
            )
            return False
        
        courses = self.get_all_courses()
        if not courses:
            self.log_result(
                "Delete All Courses", 
                "PASS", 
                "✅ No courses found in production database - already clean",
                "Database is in clean state"
            )
            return True
        
        print(f"Found {len(courses)} courses to delete...")
        deleted_count = 0
        failed_count = 0
        
        for course in courses:
            course_id = course.get('id')
            course_title = course.get('title', 'Unknown')
            
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code in [200, 204]:
                    deleted_count += 1
                    print(f"   ✅ Deleted course: {course_title}")
                else:
                    failed_count += 1
                    print(f"   ❌ Failed to delete course: {course_title} (status: {response.status_code})")
                    
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Error deleting course {course_title}: {str(e)}")
        
        self.cleanup_stats['courses_deleted'] = deleted_count
        
        if failed_count == 0:
            self.log_result(
                "Delete All Courses", 
                "PASS", 
                f"✅ Successfully deleted ALL {deleted_count} courses from production database",
                f"Production database courses cleaned - ready for fresh setup"
            )
            return True
        else:
            self.log_result(
                "Delete All Courses", 
                "FAIL", 
                f"❌ Deleted {deleted_count} courses but {failed_count} deletions failed",
                f"Some courses may still exist in production database"
            )
            return False
    
    def delete_all_classrooms(self):
        """DELETE ALL CLASSROOMS from production database"""
        print(f"\n🗑️ DELETING ALL CLASSROOMS FROM PRODUCTION DATABASE")
        print("=" * 80)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Delete All Classrooms", 
                "FAIL", 
                "No admin token available for classroom deletion",
                "Admin authentication required"
            )
            return False
        
        classrooms = self.get_all_classrooms()
        if not classrooms:
            self.log_result(
                "Delete All Classrooms", 
                "PASS", 
                "✅ No classrooms found in production database - already clean",
                "Database is in clean state"
            )
            return True
        
        print(f"Found {len(classrooms)} classrooms to delete...")
        deleted_count = 0
        failed_count = 0
        
        for classroom in classrooms:
            classroom_id = classroom.get('id')
            classroom_name = classroom.get('name', 'Unknown')
            
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/classrooms/{classroom_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code in [200, 204]:
                    deleted_count += 1
                    print(f"   ✅ Deleted classroom: {classroom_name}")
                else:
                    failed_count += 1
                    print(f"   ❌ Failed to delete classroom: {classroom_name} (status: {response.status_code})")
                    
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Error deleting classroom {classroom_name}: {str(e)}")
        
        self.cleanup_stats['classrooms_deleted'] = deleted_count
        
        if failed_count == 0:
            self.log_result(
                "Delete All Classrooms", 
                "PASS", 
                f"✅ Successfully deleted ALL {deleted_count} classrooms from production database",
                f"Production database classrooms cleaned - ready for fresh setup"
            )
            return True
        else:
            self.log_result(
                "Delete All Classrooms", 
                "FAIL", 
                f"❌ Deleted {deleted_count} classrooms but {failed_count} deletions failed",
                f"Some classrooms may still exist in production database"
            )
            return False
    
    def cleanup_all_enrollments(self):
        """CLEANUP ALL ENROLLMENTS from production database"""
        print(f"\n🗑️ CLEANING UP ALL ENROLLMENTS FROM PRODUCTION DATABASE")
        print("=" * 80)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Cleanup All Enrollments", 
                "FAIL", 
                "No admin token available for enrollment cleanup",
                "Admin authentication required"
            )
            return False
        
        try:
            # Use the orphaned enrollment cleanup endpoint to clean all enrollments
            response = requests.post(
                f"{BACKEND_URL}/enrollments/cleanup-orphaned",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get('deletedCount', 0)
                
                self.cleanup_stats['enrollments_deleted'] = deleted_count
                
                self.log_result(
                    "Cleanup All Enrollments", 
                    "PASS", 
                    f"✅ Successfully cleaned up {deleted_count} enrollment records from production database",
                    f"All orphaned enrollments removed - database ready for fresh setup"
                )
                return True
            else:
                self.log_result(
                    "Cleanup All Enrollments", 
                    "FAIL", 
                    f"❌ Failed to cleanup enrollments (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Cleanup All Enrollments", 
                "FAIL", 
                "Error during enrollment cleanup",
                str(e)
            )
        return False
    
    def delete_all_programs(self):
        """DELETE ALL PROGRAMS from production database"""
        print(f"\n🗑️ DELETING ALL PROGRAMS FROM PRODUCTION DATABASE")
        print("=" * 80)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Delete All Programs", 
                "FAIL", 
                "No admin token available for program deletion",
                "Admin authentication required"
            )
            return False
        
        programs = self.get_all_programs()
        if not programs:
            self.log_result(
                "Delete All Programs", 
                "PASS", 
                "✅ No programs found in production database - already clean",
                "Database is in clean state"
            )
            return True
        
        print(f"Found {len(programs)} programs to delete...")
        deleted_count = 0
        failed_count = 0
        
        for program in programs:
            program_id = program.get('id')
            program_title = program.get('title', 'Unknown')
            
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/programs/{program_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code in [200, 204]:
                    deleted_count += 1
                    print(f"   ✅ Deleted program: {program_title}")
                else:
                    failed_count += 1
                    print(f"   ❌ Failed to delete program: {program_title} (status: {response.status_code})")
                    
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Error deleting program {program_title}: {str(e)}")
        
        self.cleanup_stats['programs_deleted'] = deleted_count
        
        if failed_count == 0:
            self.log_result(
                "Delete All Programs", 
                "PASS", 
                f"✅ Successfully deleted ALL {deleted_count} programs from production database",
                f"Production database programs cleaned - ready for fresh setup"
            )
            return True
        else:
            self.log_result(
                "Delete All Programs", 
                "FAIL", 
                f"❌ Deleted {deleted_count} programs but {failed_count} deletions failed",
                f"Some programs may still exist in production database"
            )
            return False
    
    def verify_database_clean_state(self):
        """Verify that production database is now in clean state"""
        print(f"\n🔍 VERIFYING PRODUCTION DATABASE CLEAN STATE")
        print("=" * 80)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Verify Database Clean State", 
                "FAIL", 
                "No admin token available for verification",
                "Admin authentication required"
            )
            return False
        
        # Check courses
        courses = self.get_all_courses()
        courses_count = len(courses)
        
        # Check classrooms
        classrooms = self.get_all_classrooms()
        classrooms_count = len(classrooms)
        
        # Check enrollments
        enrollments = self.get_all_enrollments()
        enrollments_count = len(enrollments)
        
        # Check programs
        programs = self.get_all_programs()
        programs_count = len(programs)
        
        print(f"📊 CURRENT DATABASE STATE:")
        print(f"   📚 Courses: {courses_count}")
        print(f"   🏫 Classrooms: {classrooms_count}")
        print(f"   📝 Enrollments: {enrollments_count}")
        print(f"   📋 Programs: {programs_count}")
        
        total_items = courses_count + classrooms_count + enrollments_count + programs_count
        
        if total_items == 0:
            self.log_result(
                "Verify Database Clean State", 
                "PASS", 
                f"✅ PRODUCTION DATABASE IS NOW CLEAN - Ready for fresh test environment",
                f"All old data removed: {self.cleanup_stats['courses_deleted']} courses, {self.cleanup_stats['classrooms_deleted']} classrooms, {self.cleanup_stats['enrollments_deleted']} enrollments, {self.cleanup_stats['programs_deleted']} programs deleted"
            )
            return True
        else:
            self.log_result(
                "Verify Database Clean State", 
                "FAIL", 
                f"❌ Database still contains {total_items} items - cleanup incomplete",
                f"Remaining: {courses_count} courses, {classrooms_count} classrooms, {enrollments_count} enrollments, {programs_count} programs"
            )
            return False
    
    def create_fresh_test_course(self):
        """Create fresh test course for production environment"""
        print(f"\n🆕 CREATING FRESH TEST COURSE")
        print("=" * 80)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Fresh Test Course", 
                "FAIL", 
                "No admin token available for course creation",
                "Admin authentication required"
            )
            return False
        
        # Create a comprehensive test course
        course_data = {
            "title": "Production Test Course - Clean Environment",
            "description": "This is a fresh test course created after production database cleanup. It contains multiple modules to test progress tracking and course navigation.",
            "category": "Testing",
            "duration": "2 weeks",
            "accessType": "open",
            "modules": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Module 1: Introduction",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Welcome Video",
                            "type": "video",
                            "content": "Welcome to the clean production environment!",
                            "duration": "5 minutes"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Course Overview",
                            "type": "text",
                            "content": "This course will help you understand the clean production setup.",
                            "duration": "10 minutes"
                        }
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Module 2: Testing Features",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Progress Tracking Test",
                            "type": "text",
                            "content": "Test lesson for progress tracking functionality.",
                            "duration": "15 minutes"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Knowledge Check Quiz",
                            "type": "quiz",
                            "content": "Quiz to test understanding of the clean environment.",
                            "questions": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "question": "Is the production database now clean?",
                                    "type": "multiple_choice",
                                    "options": ["Yes", "No", "Partially", "Unknown"],
                                    "correct_answer": "Yes"
                                }
                            ]
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
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                self.log_result(
                    "Create Fresh Test Course", 
                    "PASS", 
                    f"✅ Successfully created fresh test course in clean production environment",
                    f"Course: '{created_course.get('title')}' (ID: {course_id}) with {len(course_data['modules'])} modules"
                )
                return created_course
            else:
                self.log_result(
                    "Create Fresh Test Course", 
                    "FAIL", 
                    f"❌ Failed to create test course (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Fresh Test Course", 
                "FAIL", 
                "Error creating fresh test course",
                str(e)
            )
        return False
    
    def create_fresh_test_classroom(self, test_course):
        """Create fresh test classroom with the test course"""
        print(f"\n🏫 CREATING FRESH TEST CLASSROOM")
        print("=" * 80)
        
        if "admin" not in self.auth_tokens or not test_course:
            self.log_result(
                "Create Fresh Test Classroom", 
                "FAIL", 
                "No admin token or test course available for classroom creation",
                "Admin authentication and test course required"
            )
            return False
        
        # Get admin user info to use as trainer
        try:
            admin_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if admin_response.status_code != 200:
                self.log_result(
                    "Create Fresh Test Classroom", 
                    "FAIL", 
                    "Failed to get admin user info for classroom creation",
                    f"Status: {admin_response.status_code}"
                )
                return False
            
            admin_user = admin_response.json()
            
            classroom_data = {
                "name": "Production Test Classroom - Clean Environment",
                "description": "Fresh test classroom created after production database cleanup",
                "trainerId": admin_user.get('id'),
                "courseIds": [test_course.get('id')],
                "studentIds": [],  # Start with no students - can be added later
                "programIds": [],
                "startDate": datetime.now().isoformat(),
                "endDate": None,  # No end date for testing
                "isActive": True
            }
            
            response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_classroom = response.json()
                classroom_id = created_classroom.get('id')
                
                self.log_result(
                    "Create Fresh Test Classroom", 
                    "PASS", 
                    f"✅ Successfully created fresh test classroom in clean production environment",
                    f"Classroom: '{created_classroom.get('name')}' (ID: {classroom_id}) with test course assigned"
                )
                return created_classroom
            else:
                self.log_result(
                    "Create Fresh Test Classroom", 
                    "FAIL", 
                    f"❌ Failed to create test classroom (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Fresh Test Classroom", 
                "FAIL", 
                "Error creating fresh test classroom",
                str(e)
            )
        return False
    
    def run_production_cleanup(self):
        """Run complete production database cleanup and fresh setup"""
        print("🚨 URGENT: PRODUCTION DATABASE CLEANUP - LearningFriend LMS")
        print("=" * 80)
        print("CRITICAL TASK: Clean production database and create fresh test environment")
        print(f"Production Backend: {BACKEND_URL}")
        print(f"Admin: {ADMIN_CREDENTIALS['username_or_email']}")
        print("=" * 80)
        
        # Step 1: Test production backend connectivity
        if not self.test_production_backend_connectivity():
            print("❌ CRITICAL: Cannot connect to production backend - ABORTING")
            return False
        
        # Step 2: Authenticate admin
        if not self.test_admin_authentication():
            print("❌ CRITICAL: Admin authentication failed - ABORTING")
            return False
        
        # Step 3: Delete all courses
        print(f"\n🗑️ PHASE 1: DELETING ALL COURSES")
        courses_deleted = self.delete_all_courses()
        
        # Step 4: Delete all classrooms
        print(f"\n🗑️ PHASE 2: DELETING ALL CLASSROOMS")
        classrooms_deleted = self.delete_all_classrooms()
        
        # Step 5: Cleanup all enrollments
        print(f"\n🗑️ PHASE 3: CLEANING UP ALL ENROLLMENTS")
        enrollments_cleaned = self.cleanup_all_enrollments()
        
        # Step 6: Delete all programs
        print(f"\n🗑️ PHASE 4: DELETING ALL PROGRAMS")
        programs_deleted = self.delete_all_programs()
        
        # Step 7: Verify clean state
        print(f"\n🔍 PHASE 5: VERIFYING CLEAN STATE")
        clean_verified = self.verify_database_clean_state()
        
        # Step 8: Create fresh test environment
        print(f"\n🆕 PHASE 6: CREATING FRESH TEST ENVIRONMENT")
        test_course = self.create_fresh_test_course()
        test_classroom = None
        if test_course:
            test_classroom = self.create_fresh_test_classroom(test_course)
        
        # Final summary
        print(f"\n📊 PRODUCTION CLEANUP SUMMARY")
        print("=" * 80)
        print(f"✅ Backend Connectivity: {'SUCCESS' if self.test_production_backend_connectivity() else 'FAILED'}")
        print(f"✅ Admin Authentication: {'SUCCESS' if 'admin' in self.auth_tokens else 'FAILED'}")
        print(f"✅ Courses Deleted: {'SUCCESS' if courses_deleted else 'FAILED'} ({self.cleanup_stats['courses_deleted']} items)")
        print(f"✅ Classrooms Deleted: {'SUCCESS' if classrooms_deleted else 'FAILED'} ({self.cleanup_stats['classrooms_deleted']} items)")
        print(f"✅ Enrollments Cleaned: {'SUCCESS' if enrollments_cleaned else 'FAILED'} ({self.cleanup_stats['enrollments_deleted']} items)")
        print(f"✅ Programs Deleted: {'SUCCESS' if programs_deleted else 'FAILED'} ({self.cleanup_stats['programs_deleted']} items)")
        print(f"✅ Clean State Verified: {'SUCCESS' if clean_verified else 'FAILED'}")
        print(f"✅ Test Course Created: {'SUCCESS' if test_course else 'FAILED'}")
        print(f"✅ Test Classroom Created: {'SUCCESS' if test_classroom else 'FAILED'}")
        
        total_deleted = sum(self.cleanup_stats.values())
        
        if clean_verified and test_course:
            print(f"\n🎉 PRODUCTION CLEANUP COMPLETED SUCCESSFULLY!")
            print(f"   📊 Total items cleaned: {total_deleted}")
            print(f"   🆕 Fresh test environment created")
            print(f"   🌐 Production site ready: https://lms-evolution.emergent.host/")
            return True
        else:
            print(f"\n❌ PRODUCTION CLEANUP INCOMPLETE!")
            print(f"   ⚠️ Manual intervention may be required")
            return False

def main():
    """Main execution function"""
    tester = ProductionCleanupTester()
    
    print("🚨 STARTING URGENT PRODUCTION DATABASE CLEANUP")
    print("=" * 80)
    
    success = tester.run_production_cleanup()
    
    print(f"\n📈 FINAL RESULTS:")
    print(f"   ✅ Tests Passed: {tester.passed}")
    print(f"   ❌ Tests Failed: {tester.failed}")
    print(f"   📊 Success Rate: {(tester.passed / (tester.passed + tester.failed) * 100):.1f}%" if (tester.passed + tester.failed) > 0 else "0.0%")
    
    if success:
        print(f"\n🎉 PRODUCTION CLEANUP SUCCESSFUL!")
        print(f"   Production site should now show clean environment")
        print(f"   Visit: https://lms-evolution.emergent.host/")
        return 0
    else:
        print(f"\n❌ PRODUCTION CLEANUP FAILED!")
        print(f"   Manual intervention required")
        return 1

if __name__ == "__main__":
    sys.exit(main())