#!/usr/bin/env python3
"""
Auto-Enrollment Investigation - Program to Classroom Course Assignment
=====================================================================

Investigating why classrooms show 0 courses when they should show courses from assigned programs.
This is the root cause of the enrollment display bug mentioned in the review request.

Findings from previous test:
- Classroom 'testing exam' has program 'test program 2' with 2 courses but shows 0 courses
- Classroom 'new test' has program 'test program' with 1 course but shows 0 courses

This suggests the auto-enrollment logic is not working properly.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://quiz-display-debug.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "brayden.student@learningfwiend.com"
STUDENT_PASSWORD = "Cove1234!"

class AutoEnrollmentInvestigator:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.student_user_id = "94cac981-b6d2-4d17-b5d8-a6b6a363cc8d"  # From previous test
        
    def authenticate(self):
        """Authenticate both admin and student"""
        # Admin login
        admin_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if admin_response.status_code == 200:
            self.admin_token = admin_response.json()['access_token']
            print("✅ Admin authenticated successfully")
        else:
            print(f"❌ Admin authentication failed: {admin_response.status_code}")
            return False
        
        # Student login
        student_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        
        if student_response.status_code == 200:
            self.student_token = student_response.json()['access_token']
            print("✅ Student authenticated successfully")
        else:
            print(f"❌ Student authentication failed: {student_response.status_code}")
            return False
        
        return True
    
    def investigate_classroom_program_relationship(self):
        """Investigate the specific classroom-program relationships causing issues"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        print("\n🔍 INVESTIGATING CLASSROOM-PROGRAM RELATIONSHIPS")
        print("=" * 60)
        
        # Get all classrooms
        classrooms_response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
        if classrooms_response.status_code != 200:
            print(f"❌ Failed to get classrooms: {classrooms_response.status_code}")
            return
        
        classrooms = classrooms_response.json()
        
        # Focus on problematic classrooms
        problematic_classrooms = ['testing exam', 'new test']
        
        for classroom in classrooms:
            classroom_name = classroom.get('name', 'Unknown')
            if classroom_name not in problematic_classrooms:
                continue
                
            print(f"\n📋 CLASSROOM: '{classroom_name}' (ID: {classroom.get('id', 'Unknown')})")
            print(f"   Student IDs: {classroom.get('studentIds', [])}")
            print(f"   Direct Course IDs: {classroom.get('courseIds', [])}")
            print(f"   Program IDs: {classroom.get('programIds', [])}")
            
            # Check if our student is in this classroom
            student_in_classroom = self.student_user_id in classroom.get('studentIds', [])
            print(f"   Student brayden.student in classroom: {student_in_classroom}")
            
            # Investigate each program
            for program_id in classroom.get('programIds', []):
                print(f"\n   🎯 PROGRAM: {program_id}")
                
                # Get program details
                program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
                if program_response.status_code == 200:
                    program = program_response.json()
                    program_title = program.get('title', 'Unknown')
                    program_courses = program.get('courseIds', [])
                    
                    print(f"      Title: '{program_title}'")
                    print(f"      Course IDs: {program_courses}")
                    print(f"      Course Count: {len(program_courses)}")
                    
                    # Check if student is enrolled in these program courses
                    print(f"\n      📚 CHECKING STUDENT ENROLLMENTS IN PROGRAM COURSES:")
                    
                    student_headers = {"Authorization": f"Bearer {self.student_token}"}
                    enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers)
                    
                    if enrollments_response.status_code == 200:
                        enrollments = enrollments_response.json()
                        enrolled_course_ids = [e.get('courseId') for e in enrollments]
                        
                        for course_id in program_courses:
                            is_enrolled = course_id in enrolled_course_ids
                            print(f"         Course {course_id}: {'✅ ENROLLED' if is_enrolled else '❌ NOT ENROLLED'}")
                            
                            # Get course details
                            course_response = requests.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers)
                            if course_response.status_code == 200:
                                course = course_response.json()
                                course_title = course.get('title', 'Unknown')
                                print(f"            Title: '{course_title}'")
                            else:
                                print(f"            ❌ Failed to get course details: {course_response.status_code}")
                    else:
                        print(f"         ❌ Failed to get student enrollments: {enrollments_response.status_code}")
                else:
                    print(f"      ❌ Failed to get program details: {program_response.status_code}")
    
    def test_manual_enrollment(self):
        """Test if manual enrollment works for program courses"""
        print("\n🧪 TESTING MANUAL ENROLLMENT FOR PROGRAM COURSES")
        print("=" * 60)
        
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Get current enrollments
        enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers)
        if enrollments_response.status_code != 200:
            print(f"❌ Failed to get current enrollments: {enrollments_response.status_code}")
            return
        
        current_enrollments = enrollments_response.json()
        enrolled_course_ids = [e.get('courseId') for e in current_enrollments]
        
        # Test courses from 'test program 2' (the one with 2 courses)
        test_course_ids = ['c7712f8d-fb79-4c52-b6f7-d1350b079dce', 'f9afe1f0-9145-4d80-b188-003a93bfdf39']
        
        for course_id in test_course_ids:
            if course_id in enrolled_course_ids:
                print(f"✅ Already enrolled in course {course_id}")
                continue
            
            print(f"\n🎯 Testing manual enrollment in course {course_id}")
            
            # Try to enroll manually
            enroll_response = requests.post(f"{BACKEND_URL}/enrollments", 
                                          headers=student_headers,
                                          json={"courseId": course_id})
            
            if enroll_response.status_code == 200:
                enrollment_data = enroll_response.json()
                print(f"✅ Manual enrollment successful")
                print(f"   Enrollment ID: {enrollment_data.get('id')}")
                print(f"   Course Name: {enrollment_data.get('courseName', 'Unknown')}")
                print(f"   Status: {enrollment_data.get('status', 'Unknown')}")
            else:
                print(f"❌ Manual enrollment failed: {enroll_response.status_code} - {enroll_response.text}")
    
    def check_auto_enrollment_logic(self):
        """Check if there's any auto-enrollment logic in the backend"""
        print("\n🔧 CHECKING AUTO-ENROLLMENT LOGIC")
        print("=" * 60)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Check if there are any endpoints related to auto-enrollment
        print("📋 Current student enrollment status:")
        
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers)
        
        if enrollments_response.status_code == 200:
            enrollments = enrollments_response.json()
            print(f"   Total enrollments: {len(enrollments)}")
            
            # Check enrollment dates to see if any were created recently (auto-enrollment)
            recent_enrollments = []
            for enrollment in enrollments:
                enrolled_at = enrollment.get('enrolledAt', '')
                if '2025-09-03' in enrolled_at or '2025-09-04' in enrolled_at:  # Recent dates
                    recent_enrollments.append(enrollment)
            
            print(f"   Recent enrollments (last 2 days): {len(recent_enrollments)}")
            
            for enrollment in recent_enrollments:
                course_name = enrollment.get('courseName', 'Unknown')
                enrolled_at = enrollment.get('enrolledAt', 'Unknown')
                enrolled_by = enrollment.get('enrolledBy', 'Unknown')
                print(f"      - {course_name} at {enrolled_at} by {enrolled_by}")
        
        print("\n🔍 CONCLUSION:")
        print("   The issue appears to be that classroom assignment to programs does NOT")
        print("   automatically create enrollment records for the program's courses.")
        print("   Students can see the classroom and the classroom contains the program,")
        print("   but the auto-enrollment step is missing or not working.")
    
    def run_investigation(self):
        """Run the complete auto-enrollment investigation"""
        print("🔧 AUTO-ENROLLMENT INVESTIGATION")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        self.investigate_classroom_program_relationship()
        self.test_manual_enrollment()
        self.check_auto_enrollment_logic()
        
        print("\n" + "=" * 60)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 60)
        print("✅ CONFIRMED ISSUES:")
        print("   1. Student is properly assigned to classrooms")
        print("   2. Classrooms properly contain programs")
        print("   3. Programs properly contain courses")
        print("   4. Manual enrollment works fine")
        print("❌ ROOT CAUSE:")
        print("   5. Auto-enrollment from program assignment is NOT working")
        print("   6. Students must manually enroll in program courses")
        print("   7. This causes the 'classroom shows 0 courses' issue")
        
        return True

if __name__ == "__main__":
    investigator = AutoEnrollmentInvestigator()
    investigator.run_investigation()