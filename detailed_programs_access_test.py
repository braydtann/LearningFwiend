#!/usr/bin/env python3

"""
🔍 DETAILED PROGRAMS ACCESS INVESTIGATION

Since the initial test showed students CAN access programs, let's investigate deeper:
1. Test different program endpoints
2. Check specific program details access
3. Test program access with different student accounts
4. Simulate frontend ClassroomDetail.js workflow
5. Check for any permission edge cases
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://learning-analytics-2.preview.emergentagent.com/api"

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

def authenticate_user(email, password):
    """Authenticate user and return token"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token'), data.get('user', {})
        else:
            return None, None
    except Exception as e:
        return None, None

def test_all_program_endpoints(token, user_type):
    """Test all program-related endpoints"""
    print(f"🔍 Testing All Program Endpoints for {user_type}")
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints_to_test = [
        ("/programs", "GET", "List all programs"),
        ("/programs/my-programs", "GET", "Get my programs"),
    ]
    
    results = {}
    
    for endpoint, method, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            
            results[endpoint] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
            
            if response.status_code == 200:
                data = response.json()
                log_test_result(f"{description} ({user_type})", True, 
                              f"Status: {response.status_code} | Count: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                log_test_result(f"{description} ({user_type})", False, 
                              f"Status: {response.status_code} | Error: {response.text[:100]}")
                
        except Exception as e:
            results[endpoint] = {
                'status_code': None,
                'success': False,
                'data': None,
                'error': str(e)
            }
            log_test_result(f"{description} ({user_type})", False, f"Exception: {str(e)}")
    
    return results

def test_specific_program_access(token, program_id, user_type):
    """Test access to specific program details"""
    print(f"🎯 Testing Specific Program Access for {user_type}")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
        
        if response.status_code == 200:
            program = response.json()
            log_test_result(f"Program Detail Access ({user_type})", True, 
                          f"Program: {program.get('title')} | Courses: {len(program.get('courseIds', []))}")
            return program
        else:
            log_test_result(f"Program Detail Access ({user_type})", False, 
                          f"Status: {response.status_code} | Error: {response.text}")
            return None
            
    except Exception as e:
        log_test_result(f"Program Detail Access ({user_type})", False, f"Exception: {str(e)}")
        return None

def simulate_classroom_detail_workflow(token, user_type):
    """Simulate the exact workflow that ClassroomDetail.js would follow"""
    print(f"🎭 Simulating ClassroomDetail.js Workflow for {user_type}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 1: Get classrooms (like ClassroomDetail.js would)
    try:
        classrooms_response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
        if classrooms_response.status_code != 200:
            log_test_result(f"Workflow Step 1 - Get Classrooms ({user_type})", False, 
                          f"Status: {classrooms_response.status_code}")
            return
        
        classrooms = classrooms_response.json()
        testing_exam = None
        for classroom in classrooms:
            if 'testing exam' in classroom.get('name', '').lower():
                testing_exam = classroom
                break
        
        if not testing_exam:
            log_test_result(f"Workflow Step 1 - Find Testing Exam ({user_type})", False, 
                          "Testing exam classroom not found")
            return
        
        log_test_result(f"Workflow Step 1 - Get Classrooms ({user_type})", True, 
                      f"Found testing exam classroom with {len(testing_exam.get('programIds', []))} programs")
        
        # Step 2: Get programs (like ClassroomDetail.js would for course count)
        programs_response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
        if programs_response.status_code != 200:
            log_test_result(f"Workflow Step 2 - Get Programs ({user_type})", False, 
                          f"Status: {programs_response.status_code} | Error: {programs_response.text}")
            return
        
        programs = programs_response.json()
        log_test_result(f"Workflow Step 2 - Get Programs ({user_type})", True, 
                      f"Retrieved {len(programs)} programs for course count calculation")
        
        # Step 3: Calculate course count (like ClassroomDetail.js would)
        direct_courses = len(testing_exam.get('courseIds', []))
        program_courses = 0
        
        for program_id in testing_exam.get('programIds', []):
            program = next((p for p in programs if p.get('id') == program_id), None)
            if program:
                program_courses += len(program.get('courseIds', []))
        
        total_courses = direct_courses + program_courses
        
        log_test_result(f"Workflow Step 3 - Calculate Course Count ({user_type})", True, 
                      f"Direct: {direct_courses} + Program: {program_courses} = Total: {total_courses}")
        
        # Step 4: Test individual program access (potential issue point)
        for program_id in testing_exam.get('programIds', []):
            program_detail_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
            if program_detail_response.status_code == 200:
                program_detail = program_detail_response.json()
                log_test_result(f"Workflow Step 4 - Program Detail {program_id[:8]} ({user_type})", True, 
                              f"Program: {program_detail.get('title')} | Courses: {len(program_detail.get('courseIds', []))}")
            else:
                log_test_result(f"Workflow Step 4 - Program Detail {program_id[:8]} ({user_type})", False, 
                              f"Status: {program_detail_response.status_code} | Error: {program_detail_response.text}")
        
        return True
        
    except Exception as e:
        log_test_result(f"Workflow Simulation ({user_type})", False, f"Exception: {str(e)}")
        return False

def test_program_access_with_different_headers(token, user_type):
    """Test program access with different request headers to identify potential issues"""
    print(f"🌐 Testing Program Access with Different Headers for {user_type}")
    
    test_cases = [
        {"Authorization": f"Bearer {token}"},
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        {"Authorization": f"Bearer {token}", "Accept": "application/json"},
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"},
    ]
    
    for i, headers in enumerate(test_cases, 1):
        try:
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
            
            if response.status_code == 200:
                programs = response.json()
                log_test_result(f"Header Test {i} ({user_type})", True, 
                              f"Status: {response.status_code} | Programs: {len(programs)}")
            else:
                log_test_result(f"Header Test {i} ({user_type})", False, 
                              f"Status: {response.status_code} | Error: {response.text[:100]}")
                
        except Exception as e:
            log_test_result(f"Header Test {i} ({user_type})", False, f"Exception: {str(e)}")

def check_cors_and_preflight(user_type):
    """Check for CORS issues that might affect frontend"""
    print(f"🌍 Testing CORS and Preflight for {user_type}")
    
    try:
        # Test OPTIONS request (preflight)
        options_response = requests.options(f"{BACKEND_URL}/programs")
        log_test_result(f"OPTIONS Preflight ({user_type})", 
                      options_response.status_code in [200, 204], 
                      f"Status: {options_response.status_code} | Headers: {dict(options_response.headers)}")
        
    except Exception as e:
        log_test_result(f"OPTIONS Preflight ({user_type})", False, f"Exception: {str(e)}")

def main():
    """Main detailed investigation function"""
    print("🔍 DETAILED PROGRAMS ACCESS INVESTIGATION")
    print("=" * 60)
    print()
    
    # Authenticate users
    print("🔐 Authentication Phase")
    admin_token, admin_info = authenticate_user(ADMIN_EMAIL, ADMIN_PASSWORD)
    student_token, student_info = authenticate_user(STUDENT_EMAIL, STUDENT_PASSWORD)
    
    if not admin_token or not student_token:
        print("❌ Authentication failed - cannot proceed")
        return
    
    print(f"✅ Admin: {admin_info.get('full_name')} ({admin_info.get('role')})")
    print(f"✅ Student: {student_info.get('full_name')} ({student_info.get('role')})")
    print()
    
    # Test 1: All program endpoints
    print("📋 PHASE 1: All Program Endpoints")
    admin_results = test_all_program_endpoints(admin_token, "Admin")
    student_results = test_all_program_endpoints(student_token, "Student")
    
    # Test 2: Specific program access
    print("📋 PHASE 2: Specific Program Access")
    # Get a program ID from admin results
    if admin_results.get('/programs', {}).get('data'):
        programs = admin_results['/programs']['data']
        if programs:
            test_program_id = programs[0].get('id')
            admin_program = test_specific_program_access(admin_token, test_program_id, "Admin")
            student_program = test_specific_program_access(student_token, test_program_id, "Student")
    
    # Test 3: Simulate ClassroomDetail.js workflow
    print("📋 PHASE 3: ClassroomDetail.js Workflow Simulation")
    admin_workflow = simulate_classroom_detail_workflow(admin_token, "Admin")
    student_workflow = simulate_classroom_detail_workflow(student_token, "Student")
    
    # Test 4: Different headers
    print("📋 PHASE 4: Different Request Headers")
    test_program_access_with_different_headers(admin_token, "Admin")
    test_program_access_with_different_headers(student_token, "Student")
    
    # Test 5: CORS and preflight
    print("📋 PHASE 5: CORS and Preflight")
    check_cors_and_preflight("General")
    
    # Summary
    print("📋 DETAILED INVESTIGATION SUMMARY")
    print("=" * 60)
    
    print("🔍 Endpoint Access Summary:")
    for endpoint in ['/programs', '/programs/my-programs']:
        admin_success = admin_results.get(endpoint, {}).get('success', False)
        student_success = student_results.get(endpoint, {}).get('success', False)
        print(f"    {endpoint}:")
        print(f"        Admin: {'✅ Success' if admin_success else '❌ Failed'}")
        print(f"        Student: {'✅ Success' if student_success else '❌ Failed'}")
        
        if not student_success and endpoint in student_results:
            error_info = student_results[endpoint]
            print(f"        Student Error: {error_info.get('status_code')} - {error_info.get('error', 'Unknown')}")
    
    print(f"\n🎭 Workflow Simulation:")
    print(f"    Admin: {'✅ Success' if admin_workflow else '❌ Failed'}")
    print(f"    Student: {'✅ Success' if student_workflow else '❌ Failed'}")
    
    print(f"\n🎯 Key Findings:")
    if student_results.get('/programs', {}).get('success'):
        print(f"    ✅ Students CAN access GET /api/programs")
        print(f"    ✅ No 403 'Admin access required' errors detected")
        print(f"    🤔 The issue reported in ClassroomDetail.js may be:")
        print(f"        - Frontend caching/state management issue")
        print(f"        - Race condition in component lifecycle")
        print(f"        - Different environment/URL being used")
        print(f"        - Browser-specific issue")
    else:
        print(f"    ❌ Students CANNOT access GET /api/programs")
        print(f"    🎯 This confirms the hypothesis in the review request")
        error_info = student_results.get('/programs', {})
        print(f"    📋 Error Details: {error_info.get('status_code')} - {error_info.get('error')}")
    
    print()
    print("🚨 DETAILED INVESTIGATION COMPLETE")

if __name__ == "__main__":
    main()