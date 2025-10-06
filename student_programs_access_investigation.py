#!/usr/bin/env python3

"""
🚨 CRITICAL: Student Programs Access Investigation

ISSUE: ClassroomDetail.js course count fix isn't working for students. Console shows 403 errors and "Admin access required" messages.

INVESTIGATION NEEDED:
1. Test Student Programs Access - Can students access GET /api/programs endpoint?
2. Test Student Classroom Access - Can students get classroom details with programs?
3. Check API Permissions - Which endpoints require admin vs student access?
4. Test Course Loading - Are courses loading properly for students?

SPECIFIC TESTS:
- Login as student: brayden.student@learningfwiend.com / Cove1234!
- GET /api/programs - Test if students can access programs
- GET /api/classrooms/{testing_exam_id} - Test classroom detail access
- GET /api/courses - Test if students can get courses list
- Identify permission issues blocking course count display

HYPOTHESIS: Students don't have access to programs endpoint, so `availablePrograms` stays empty, breaking the course count calculation.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"

# Test credentials
STUDENT_EMAIL = "brayden.student@learningfwiend.com"
STUDENT_PASSWORD = "Cove1234!"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

def log_test_result(test_name, success, details):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"[{timestamp}] {status} - {test_name}")
    print(f"    Details: {details}")
    print()

def authenticate_user(email, password, user_type):
    """Authenticate user and return token"""
    print(f"🔐 Authenticating {user_type}: {email}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_info = data.get('user', {})
            requires_password_change = data.get('requires_password_change', False)
            
            log_test_result(f"{user_type} Authentication", True, 
                          f"User: {user_info.get('full_name', 'Unknown')} | Role: {user_info.get('role', 'Unknown')} | Password Change Required: {requires_password_change}")
            return token, user_info, requires_password_change
        else:
            log_test_result(f"{user_type} Authentication", False, 
                          f"Status: {response.status_code} | Error: {response.text}")
            return None, None, None
            
    except Exception as e:
        log_test_result(f"{user_type} Authentication", False, f"Exception: {str(e)}")
        return None, None, None

def test_programs_access(token, user_type):
    """Test access to GET /api/programs endpoint"""
    print(f"🔍 Testing Programs Access for {user_type}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
        
        if response.status_code == 200:
            programs = response.json()
            log_test_result(f"Programs Access ({user_type})", True, 
                          f"Found {len(programs)} programs | Sample: {programs[0].get('title', 'N/A') if programs else 'No programs'}")
            return programs
        elif response.status_code == 403:
            log_test_result(f"Programs Access ({user_type})", False, 
                          f"403 Forbidden - Admin access required")
            return None
        else:
            log_test_result(f"Programs Access ({user_type})", False, 
                          f"Status: {response.status_code} | Error: {response.text}")
            return None
            
    except Exception as e:
        log_test_result(f"Programs Access ({user_type})", False, f"Exception: {str(e)}")
        return None

def test_classrooms_access(token, user_type):
    """Test access to GET /api/classrooms endpoint"""
    print(f"🏫 Testing Classrooms Access for {user_type}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
        
        if response.status_code == 200:
            classrooms = response.json()
            log_test_result(f"Classrooms Access ({user_type})", True, 
                          f"Found {len(classrooms)} classrooms")
            
            # Look for 'testing exam' classroom specifically
            testing_exam_classroom = None
            for classroom in classrooms:
                if 'testing exam' in classroom.get('name', '').lower():
                    testing_exam_classroom = classroom
                    break
            
            if testing_exam_classroom:
                print(f"    📋 Found 'testing exam' classroom:")
                print(f"        ID: {testing_exam_classroom.get('id')}")
                print(f"        Name: {testing_exam_classroom.get('name')}")
                print(f"        Direct Courses: {len(testing_exam_classroom.get('courseIds', []))}")
                print(f"        Programs: {len(testing_exam_classroom.get('programIds', []))}")
                print(f"        Students: {len(testing_exam_classroom.get('studentIds', []))}")
                return classrooms, testing_exam_classroom
            else:
                print(f"    ⚠️  'testing exam' classroom not found in {len(classrooms)} classrooms")
                return classrooms, None
        else:
            log_test_result(f"Classrooms Access ({user_type})", False, 
                          f"Status: {response.status_code} | Error: {response.text}")
            return None, None
            
    except Exception as e:
        log_test_result(f"Classrooms Access ({user_type})", False, f"Exception: {str(e)}")
        return None, None

def test_classroom_detail_access(token, classroom_id, user_type):
    """Test access to specific classroom details"""
    print(f"🔍 Testing Classroom Detail Access for {user_type}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/classrooms/{classroom_id}", headers=headers)
        
        if response.status_code == 200:
            classroom = response.json()
            log_test_result(f"Classroom Detail Access ({user_type})", True, 
                          f"Classroom: {classroom.get('name')} | Programs: {len(classroom.get('programIds', []))} | Courses: {len(classroom.get('courseIds', []))}")
            return classroom
        else:
            log_test_result(f"Classroom Detail Access ({user_type})", False, 
                          f"Status: {response.status_code} | Error: {response.text}")
            return None
            
    except Exception as e:
        log_test_result(f"Classroom Detail Access ({user_type})", False, f"Exception: {str(e)}")
        return None

def test_courses_access(token, user_type):
    """Test access to GET /api/courses endpoint"""
    print(f"📚 Testing Courses Access for {user_type}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/courses", headers=headers)
        
        if response.status_code == 200:
            courses = response.json()
            log_test_result(f"Courses Access ({user_type})", True, 
                          f"Found {len(courses)} courses")
            return courses
        else:
            log_test_result(f"Courses Access ({user_type})", False, 
                          f"Status: {response.status_code} | Error: {response.text}")
            return None
            
    except Exception as e:
        log_test_result(f"Courses Access ({user_type})", False, f"Exception: {str(e)}")
        return None

def test_enrollments_access(token, user_type):
    """Test access to GET /api/enrollments endpoint"""
    print(f"📝 Testing Enrollments Access for {user_type}")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
        
        if response.status_code == 200:
            enrollments = response.json()
            log_test_result(f"Enrollments Access ({user_type})", True, 
                          f"Found {len(enrollments)} enrollments")
            return enrollments
        else:
            log_test_result(f"Enrollments Access ({user_type})", False, 
                          f"Status: {response.status_code} | Error: {response.text}")
            return None
            
    except Exception as e:
        log_test_result(f"Enrollments Access ({user_type})", False, f"Exception: {str(e)}")
        return None

def analyze_course_count_calculation(programs, classroom, user_type):
    """Analyze how course count should be calculated"""
    print(f"🧮 Analyzing Course Count Calculation for {user_type}")
    
    if not classroom:
        log_test_result(f"Course Count Analysis ({user_type})", False, "No classroom data available")
        return
    
    direct_courses = len(classroom.get('courseIds', []))
    program_ids = classroom.get('programIds', [])
    
    program_courses = 0
    if programs:
        for program_id in program_ids:
            program = next((p for p in programs if p.get('id') == program_id), None)
            if program:
                program_courses += len(program.get('courseIds', []))
    
    total_courses = direct_courses + program_courses
    
    log_test_result(f"Course Count Analysis ({user_type})", True, 
                  f"Direct: {direct_courses} + Program: {program_courses} = Total: {total_courses}")
    
    print(f"    📊 Course Count Breakdown:")
    print(f"        Direct Courses: {direct_courses}")
    print(f"        Program Courses: {program_courses}")
    print(f"        Total Expected: {total_courses}")
    print()

def main():
    """Main investigation function"""
    print("🚨 CRITICAL: Student Programs Access Investigation")
    print("=" * 60)
    print()
    
    # Test 1: Admin Authentication (baseline)
    print("📋 PHASE 1: Admin Authentication (Baseline)")
    admin_token, admin_info, admin_pwd_change = authenticate_user(ADMIN_EMAIL, ADMIN_PASSWORD, "Admin")
    
    if not admin_token:
        print("❌ Cannot proceed without admin authentication")
        return
    
    # Test 2: Student Authentication
    print("📋 PHASE 2: Student Authentication")
    student_token, student_info, student_pwd_change = authenticate_user(STUDENT_EMAIL, STUDENT_PASSWORD, "Student")
    
    if not student_token:
        print("❌ Cannot proceed without student authentication")
        return
    
    # Test 3: Programs Access Comparison
    print("📋 PHASE 3: Programs Access Comparison")
    admin_programs = test_programs_access(admin_token, "Admin")
    student_programs = test_programs_access(student_token, "Student")
    
    # Test 4: Classrooms Access Comparison
    print("📋 PHASE 4: Classrooms Access Comparison")
    admin_classrooms, admin_testing_exam = test_classrooms_access(admin_token, "Admin")
    student_classrooms, student_testing_exam = test_classrooms_access(student_token, "Student")
    
    # Test 5: Classroom Detail Access (if testing exam found)
    if admin_testing_exam:
        print("📋 PHASE 5: Classroom Detail Access")
        classroom_id = admin_testing_exam.get('id')
        admin_classroom_detail = test_classroom_detail_access(admin_token, classroom_id, "Admin")
        student_classroom_detail = test_classroom_detail_access(student_token, classroom_id, "Student")
    
    # Test 6: Courses Access Comparison
    print("📋 PHASE 6: Courses Access Comparison")
    admin_courses = test_courses_access(admin_token, "Admin")
    student_courses = test_courses_access(student_token, "Student")
    
    # Test 7: Enrollments Access
    print("📋 PHASE 7: Enrollments Access")
    student_enrollments = test_enrollments_access(student_token, "Student")
    
    # Test 8: Course Count Analysis
    print("📋 PHASE 8: Course Count Analysis")
    if admin_testing_exam:
        analyze_course_count_calculation(admin_programs, admin_testing_exam, "Admin (with programs)")
        analyze_course_count_calculation(student_programs, student_testing_exam, "Student (with/without programs)")
    
    # Summary
    print("📋 INVESTIGATION SUMMARY")
    print("=" * 60)
    
    print(f"🔐 Authentication:")
    print(f"    Admin: {'✅ Success' if admin_token else '❌ Failed'}")
    print(f"    Student: {'✅ Success' if student_token else '❌ Failed'}")
    
    print(f"🔍 API Access:")
    print(f"    Programs (Admin): {'✅ Success' if admin_programs else '❌ Failed'}")
    print(f"    Programs (Student): {'✅ Success' if student_programs else '❌ Failed/Forbidden'}")
    print(f"    Classrooms (Admin): {'✅ Success' if admin_classrooms else '❌ Failed'}")
    print(f"    Classrooms (Student): {'✅ Success' if student_classrooms else '❌ Failed'}")
    print(f"    Courses (Admin): {'✅ Success' if admin_courses else '❌ Failed'}")
    print(f"    Courses (Student): {'✅ Success' if student_courses else '❌ Failed'}")
    
    print(f"🎯 Root Cause Analysis:")
    if not student_programs and admin_programs:
        print(f"    ❌ CRITICAL ISSUE: Students cannot access /api/programs endpoint")
        print(f"    📊 Impact: Course count calculation will fail because availablePrograms stays empty")
        print(f"    🔧 Solution: Either allow student access to programs OR modify course count calculation")
    elif student_programs:
        print(f"    ✅ Students can access programs - issue may be elsewhere")
    else:
        print(f"    ⚠️  Neither admin nor student can access programs - API may be down")
    
    print()
    print("🚨 INVESTIGATION COMPLETE")

if __name__ == "__main__":
    main()