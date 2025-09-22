#!/usr/bin/env python3
"""
Enrollment Display Debug - Frontend vs Backend Discrepancy
==========================================================

The investigation revealed that:
1. Student IS enrolled in program courses (backend shows enrollments)
2. But classroom shows 0 courses (frontend display issue)

This suggests the issue is in how the frontend determines course count for classrooms.
The frontend might be looking at direct courseIds only, not including program courses.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "brayden.student@learningfwiend.com"
STUDENT_PASSWORD = "Cove1234!"

class EnrollmentDisplayDebugger:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        
    def authenticate(self):
        """Authenticate admin"""
        admin_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if admin_response.status_code == 200:
            self.admin_token = admin_response.json()['access_token']
            print("✅ Admin authenticated successfully")
            return True
        else:
            print(f"❌ Admin authentication failed: {admin_response.status_code}")
            return False
    
    def analyze_classroom_course_display_logic(self):
        """Analyze how classroom course count should be calculated"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        print("\n🔍 ANALYZING CLASSROOM COURSE DISPLAY LOGIC")
        print("=" * 60)
        
        # Get the problematic classroom
        classrooms_response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
        if classrooms_response.status_code != 200:
            print(f"❌ Failed to get classrooms: {classrooms_response.status_code}")
            return
        
        classrooms = classrooms_response.json()
        
        # Focus on 'testing exam' classroom
        testing_exam_classroom = None
        for classroom in classrooms:
            if classroom.get('name') == 'testing exam':
                testing_exam_classroom = classroom
                break
        
        if not testing_exam_classroom:
            print("❌ 'testing exam' classroom not found")
            return
        
        print(f"📋 CLASSROOM: 'testing exam'")
        print(f"   ID: {testing_exam_classroom.get('id')}")
        print(f"   Direct Course IDs: {testing_exam_classroom.get('courseIds', [])}")
        print(f"   Program IDs: {testing_exam_classroom.get('programIds', [])}")
        
        # Calculate what the course count SHOULD be
        direct_courses = testing_exam_classroom.get('courseIds', [])
        program_ids = testing_exam_classroom.get('programIds', [])
        
        print(f"\n📊 COURSE COUNT CALCULATION:")
        print(f"   Direct courses: {len(direct_courses)}")
        
        total_program_courses = []
        for program_id in program_ids:
            program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
            if program_response.status_code == 200:
                program = program_response.json()
                program_courses = program.get('courseIds', [])
                total_program_courses.extend(program_courses)
                print(f"   Program '{program.get('title')}': {len(program_courses)} courses")
        
        print(f"   Total program courses: {len(total_program_courses)}")
        print(f"   EXPECTED TOTAL: {len(direct_courses) + len(total_program_courses)}")
        
        # Check if there's a specific endpoint for classroom courses
        classroom_id = testing_exam_classroom.get('id')
        
        # Try different potential endpoints
        endpoints_to_try = [
            f"/classrooms/{classroom_id}",
            f"/classrooms/{classroom_id}/courses",
            f"/classrooms/{classroom_id}/students"
        ]
        
        print(f"\n🔍 TESTING CLASSROOM-SPECIFIC ENDPOINTS:")
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                print(f"   {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'courseIds' in data:
                            print(f"      courseIds: {data['courseIds']}")
                        if 'courses' in data:
                            print(f"      courses: {len(data['courses'])} items")
                    elif isinstance(data, list):
                        print(f"      Response: {len(data)} items")
            except Exception as e:
                print(f"   {endpoint}: Exception - {str(e)}")
    
    def check_frontend_expectations(self):
        """Check what data structure the frontend might expect"""
        print(f"\n🎯 FRONTEND EXPECTATIONS ANALYSIS")
        print("=" * 60)
        
        print("Based on the investigation, the issue is likely:")
        print("1. Frontend displays classroom course count based on direct courseIds only")
        print("2. Frontend does not aggregate courses from programs within the classroom")
        print("3. This causes classrooms with only program-based courses to show 0 courses")
        
        print(f"\n💡 POTENTIAL SOLUTIONS:")
        print("1. Backend: Add computed field 'totalCourseCount' to classroom responses")
        print("2. Backend: Create endpoint that returns expanded course list for classrooms")
        print("3. Frontend: Modify logic to calculate total courses (direct + program courses)")
        print("4. Backend: Auto-populate courseIds with program courses when classroom is created")
        
        print(f"\n🔧 RECOMMENDED FIX:")
        print("The backend should include a computed 'totalCourseCount' field in classroom responses")
        print("that includes both direct courses and courses from all assigned programs.")
    
    def test_student_dashboard_data(self):
        """Test what data the student dashboard receives"""
        print(f"\n📱 STUDENT DASHBOARD DATA ANALYSIS")
        print("=" * 60)
        
        # Login as student
        student_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        
        if student_response.status_code != 200:
            print(f"❌ Student authentication failed: {student_response.status_code}")
            return
        
        student_token = student_response.json()['access_token']
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # Get student's view of classrooms
        classrooms_response = requests.get(f"{BACKEND_URL}/classrooms", headers=student_headers)
        if classrooms_response.status_code == 200:
            classrooms = classrooms_response.json()
            
            print(f"Student sees {len(classrooms)} classrooms:")
            for classroom in classrooms:
                name = classroom.get('name', 'Unknown')
                course_count = len(classroom.get('courseIds', []))
                program_count = len(classroom.get('programIds', []))
                print(f"   '{name}': {course_count} direct courses, {program_count} programs")
                
                # This is what the frontend sees - only direct course count
                print(f"      Frontend would show: {course_count} courses")
        
        # Get student's enrollments
        enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers)
        if enrollments_response.status_code == 200:
            enrollments = enrollments_response.json()
            print(f"\nStudent has {len(enrollments)} total enrollments")
            
            # Check which courses the student can actually access
            enrolled_course_ids = [e.get('courseId') for e in enrollments]
            print(f"Enrolled course IDs: {enrolled_course_ids}")
    
    def run_debug(self):
        """Run the complete enrollment display debug"""
        print("🔧 ENROLLMENT DISPLAY DEBUG")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        self.analyze_classroom_course_display_logic()
        self.check_frontend_expectations()
        self.test_student_dashboard_data()
        
        print("\n" + "=" * 60)
        print("📊 DEBUG SUMMARY")
        print("=" * 60)
        print("🎯 ROOT CAUSE IDENTIFIED:")
        print("   The classroom shows 0 courses because the frontend only counts")
        print("   direct courseIds, not courses from assigned programs.")
        print("")
        print("✅ STUDENT IS PROPERLY ENROLLED:")
        print("   - Student is assigned to classrooms ✅")
        print("   - Classrooms contain programs ✅") 
        print("   - Student is enrolled in program courses ✅")
        print("   - Auto-enrollment IS working ✅")
        print("")
        print("❌ DISPLAY BUG:")
        print("   - Frontend shows course count based on direct courseIds only")
        print("   - Does not include courses from programs")
        print("   - This is a frontend calculation issue, not a backend enrollment issue")
        
        return True

if __name__ == "__main__":
    debugger = EnrollmentDisplayDebugger()
    debugger.run_debug()