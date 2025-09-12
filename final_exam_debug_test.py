#!/usr/bin/env python3

"""
Final Exam Access Debug Test
============================

This test specifically debugs the final exam access issue where students see 
"no final exam created for that program" even though admin/instructor created one.

Test Focus:
1. Final Exam Creation Debug - Check how final exams are created and what program ID is stored
2. Final Exam Retrieval Debug - Check how final exams are retrieved with program_id filters  
3. Program ID Consistency Check - Get lists of programs and final tests to check for mismatches
4. Student Access Flow Debug - Test student login and program completion detection

Credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://fixfriend.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamDebugTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        
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
    
    def get_all_programs(self) -> List[Dict]:
        """Get all programs to analyze program IDs."""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
            
            if response.status_code == 200:
                programs = response.json()
                self.log_result("Get All Programs", True, f"Retrieved {len(programs)} programs")
                
                # Log program details for debugging
                print("\n=== PROGRAM ID ANALYSIS ===")
                for program in programs[:5]:  # Show first 5 programs
                    print(f"Program: {program['title']}")
                    print(f"  ID: {program['id']}")
                    print(f"  Course Count: {program.get('courseCount', 0)}")
                    print(f"  Instructor: {program.get('instructor', 'Unknown')}")
                    print()
                
                return programs
            else:
                self.log_result("Get All Programs", False, f"Failed with status {response.status_code}", response.json())
                return []
        except Exception as e:
            self.log_result("Get All Programs", False, f"Exception: {str(e)}")
            return []
    
    def get_all_final_tests(self) -> List[Dict]:
        """Get all final tests to analyze program ID references."""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers)
            
            if response.status_code == 200:
                final_tests = response.json()
                self.log_result("Get All Final Tests", True, f"Retrieved {len(final_tests)} final tests")
                
                # Log final test details for debugging
                print("\n=== FINAL TEST PROGRAM ID ANALYSIS ===")
                for test in final_tests:
                    print(f"Final Test: {test['title']}")
                    print(f"  ID: {test['id']}")
                    print(f"  Program ID: {test['programId']}")
                    print(f"  Program Name: {test.get('programName', 'Unknown')}")
                    print(f"  Published: {test.get('isPublished', False)}")
                    print(f"  Created By: {test.get('createdByName', 'Unknown')}")
                    print()
                
                return final_tests
            else:
                self.log_result("Get All Final Tests", False, f"Failed with status {response.status_code}", response.json())
                return []
        except Exception as e:
            self.log_result("Get All Final Tests", False, f"Exception: {str(e)}")
            return []
    
    def check_program_id_consistency(self, programs: List[Dict], final_tests: List[Dict]) -> bool:
        """Check for program ID mismatches between programs and final tests."""
        try:
            program_ids = {p['id'] for p in programs}
            final_test_program_ids = {ft['programId'] for ft in final_tests}
            
            # Find mismatches
            orphaned_final_tests = final_test_program_ids - program_ids
            programs_without_tests = program_ids - final_test_program_ids
            
            print("\n=== PROGRAM ID CONSISTENCY CHECK ===")
            print(f"Total Programs: {len(program_ids)}")
            print(f"Total Final Tests: {len(final_tests)}")
            print(f"Unique Program IDs in Final Tests: {len(final_test_program_ids)}")
            print(f"Orphaned Final Tests (no matching program): {len(orphaned_final_tests)}")
            print(f"Programs Without Final Tests: {len(programs_without_tests)}")
            
            if orphaned_final_tests:
                print("\n❌ ORPHANED FINAL TESTS:")
                for test in final_tests:
                    if test['programId'] in orphaned_final_tests:
                        print(f"  - {test['title']} (Program ID: {test['programId']})")
            
            if programs_without_tests:
                print(f"\n📝 PROGRAMS WITHOUT FINAL TESTS: {len(programs_without_tests)}")
                for program in programs:
                    if program['id'] in programs_without_tests:
                        print(f"  - {program['title']} (ID: {program['id']})")
            
            success = len(orphaned_final_tests) == 0
            details = f"Found {len(orphaned_final_tests)} orphaned final tests, {len(programs_without_tests)} programs without tests"
            self.log_result("Program ID Consistency Check", success, details)
            
            return success
            
        except Exception as e:
            self.log_result("Program ID Consistency Check", False, f"Exception: {str(e)}")
            return False
    
    def test_final_exam_creation(self) -> bool:
        """Test creating a final exam and verify program ID storage."""
        try:
            # First, get a program to create a test for
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            programs_response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
            
            if programs_response.status_code != 200:
                self.log_result("Final Exam Creation Test", False, "Could not retrieve programs for test creation")
                return False
            
            programs = programs_response.json()
            if not programs:
                self.log_result("Final Exam Creation Test", False, "No programs available for test creation")
                return False
            
            # Use the first program
            test_program = programs[0]
            
            # Create a test final exam
            test_data = {
                "title": "Debug Test Final Exam",
                "description": "Test final exam created for debugging program ID consistency",
                "programId": test_program['id'],
                "questions": [
                    {
                        "type": "multiple-choice",
                        "question": "What is 2 + 2?",
                        "options": ["3", "4", "5", "6"],
                        "correctAnswer": 1,
                        "points": 10,
                        "explanation": "Basic arithmetic"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            response = requests.post(f"{BACKEND_URL}/final-tests", json=test_data, headers=headers)
            
            if response.status_code == 200:
                created_test = response.json()
                stored_program_id = created_test.get('programId')
                expected_program_id = test_program['id']
                
                print(f"\n=== FINAL EXAM CREATION DEBUG ===")
                print(f"Expected Program ID: {expected_program_id}")
                print(f"Stored Program ID: {stored_program_id}")
                print(f"Program Name: {created_test.get('programName', 'Unknown')}")
                print(f"Test ID: {created_test.get('id')}")
                print(f"Published: {created_test.get('isPublished', False)}")
                
                success = stored_program_id == expected_program_id
                details = f"Program ID consistency: {'✅ MATCH' if success else '❌ MISMATCH'}"
                self.log_result("Final Exam Creation Test", success, details, {
                    "expected_program_id": expected_program_id,
                    "stored_program_id": stored_program_id,
                    "test_id": created_test.get('id')
                })
                
                return success
            else:
                self.log_result("Final Exam Creation Test", False, f"Failed to create test: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Final Exam Creation Test", False, f"Exception: {str(e)}")
            return False
    
    def test_final_exam_retrieval_with_filters(self) -> bool:
        """Test final exam retrieval with program_id filters."""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get all programs first
            programs_response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
            if programs_response.status_code != 200:
                self.log_result("Final Exam Retrieval Test", False, "Could not retrieve programs")
                return False
            
            programs = programs_response.json()
            if not programs:
                self.log_result("Final Exam Retrieval Test", False, "No programs available")
                return False
            
            print(f"\n=== FINAL EXAM RETRIEVAL DEBUG ===")
            
            # Test retrieval for each program
            success_count = 0
            total_tests = 0
            
            for program in programs[:3]:  # Test first 3 programs
                program_id = program['id']
                program_title = program['title']
                
                # Test without filter
                all_tests_response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers)
                all_tests = all_tests_response.json() if all_tests_response.status_code == 200 else []
                
                # Test with program_id filter
                filtered_response = requests.get(
                    f"{BACKEND_URL}/final-tests?program_id={program_id}&published_only=true", 
                    headers=headers
                )
                
                if filtered_response.status_code == 200:
                    filtered_tests = filtered_response.json()
                    
                    print(f"\nProgram: {program_title}")
                    print(f"  Program ID: {program_id}")
                    print(f"  All Final Tests: {len(all_tests)}")
                    print(f"  Filtered Tests: {len(filtered_tests)}")
                    
                    # Check if any tests match this program ID
                    matching_tests = [t for t in all_tests if t.get('programId') == program_id]
                    print(f"  Expected Matches: {len(matching_tests)}")
                    
                    if len(filtered_tests) == len(matching_tests):
                        success_count += 1
                        print(f"  Status: ✅ CORRECT")
                    else:
                        print(f"  Status: ❌ MISMATCH")
                        print(f"  Expected: {len(matching_tests)}, Got: {len(filtered_tests)}")
                    
                    total_tests += 1
                else:
                    print(f"\nProgram: {program_title}")
                    print(f"  Status: ❌ FAILED - HTTP {filtered_response.status_code}")
                    total_tests += 1
            
            success = success_count == total_tests
            details = f"Filter accuracy: {success_count}/{total_tests} programs returned correct results"
            self.log_result("Final Exam Retrieval Test", success, details)
            
            return success
            
        except Exception as e:
            self.log_result("Final Exam Retrieval Test", False, f"Exception: {str(e)}")
            return False
    
    def test_student_program_completion_flow(self) -> bool:
        """Test student program completion detection and final exam access."""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            print(f"\n=== STUDENT PROGRAM COMPLETION FLOW DEBUG ===")
            
            # Get student enrollments
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            if enrollments_response.status_code != 200:
                self.log_result("Student Program Completion Flow", False, "Could not retrieve student enrollments")
                return False
            
            enrollments = enrollments_response.json()
            print(f"Student Enrollments: {len(enrollments)}")
            
            # Get student's classrooms (to determine program access)
            classrooms_response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
            classrooms = []
            if classrooms_response.status_code == 200:
                all_classrooms = classrooms_response.json()
                # Filter classrooms where student is enrolled
                classrooms = [c for c in all_classrooms if self.student_user['id'] in c.get('studentIds', [])]
            
            print(f"Student Classrooms: {len(classrooms)}")
            
            # Analyze program completion
            program_completion = {}
            
            for classroom in classrooms:
                for program_id in classroom.get('programIds', []):
                    if program_id not in program_completion:
                        program_completion[program_id] = {
                            'classroom': classroom['name'],
                            'courses': [],
                            'completed_courses': 0,
                            'total_courses': 0
                        }
                    
                    # Get program details
                    program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
                    if program_response.status_code == 200:
                        program = program_response.json()
                        course_ids = program.get('courseIds', [])
                        program_completion[program_id]['total_courses'] = len(course_ids)
                        
                        # Check completion for each course
                        for course_id in course_ids:
                            enrollment = next((e for e in enrollments if e['courseId'] == course_id), None)
                            if enrollment:
                                progress = enrollment.get('progress', 0)
                                if progress >= 100:
                                    program_completion[program_id]['completed_courses'] += 1
                                program_completion[program_id]['courses'].append({
                                    'courseId': course_id,
                                    'progress': progress,
                                    'completed': progress >= 100
                                })
            
            # Check final exam access for completed programs
            completed_programs = []
            for program_id, completion in program_completion.items():
                completion_rate = completion['completed_courses'] / completion['total_courses'] if completion['total_courses'] > 0 else 0
                is_completed = completion_rate >= 1.0
                
                print(f"\nProgram ID: {program_id}")
                print(f"  Classroom: {completion['classroom']}")
                print(f"  Completion: {completion['completed_courses']}/{completion['total_courses']} ({completion_rate*100:.1f}%)")
                print(f"  Status: {'✅ COMPLETED' if is_completed else '⏳ IN PROGRESS'}")
                
                if is_completed:
                    completed_programs.append(program_id)
                    
                    # Test final exam access for completed program
                    final_tests_response = requests.get(
                        f"{BACKEND_URL}/final-tests?program_id={program_id}&published_only=true",
                        headers=headers
                    )
                    
                    if final_tests_response.status_code == 200:
                        final_tests = final_tests_response.json()
                        print(f"  Final Exams Available: {len(final_tests)}")
                        
                        if len(final_tests) == 0:
                            print(f"  ❌ ISSUE: No final exam found for completed program!")
                        else:
                            for test in final_tests:
                                print(f"    - {test['title']} (Published: {test.get('isPublished', False)})")
                    else:
                        print(f"  ❌ ERROR: Could not retrieve final tests (HTTP {final_tests_response.status_code})")
            
            success = len(completed_programs) > 0
            details = f"Found {len(completed_programs)} completed programs for student"
            self.log_result("Student Program Completion Flow", success, details, {
                "completed_programs": completed_programs,
                "total_programs": len(program_completion)
            })
            
            return success
            
        except Exception as e:
            self.log_result("Student Program Completion Flow", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_debug(self):
        """Run all debug tests."""
        print("🔍 FINAL EXAM ACCESS DEBUG TEST")
        print("=" * 50)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        if not self.authenticate_student():
            print("❌ Cannot proceed without student authentication")
            return
        
        # Get data for analysis
        programs = self.get_all_programs()
        final_tests = self.get_all_final_tests()
        
        # Run debug tests
        self.check_program_id_consistency(programs, final_tests)
        self.test_final_exam_creation()
        self.test_final_exam_retrieval_with_filters()
        self.test_student_program_completion_flow()
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 FINAL EXAM DEBUG SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Root cause analysis
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        failed_tests = [r for r in self.test_results if not r['success']]
        
        if not failed_tests:
            print("✅ All tests passed - final exam system appears to be working correctly")
        else:
            print("❌ Issues detected:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = FinalExamDebugTester()
    success = tester.run_comprehensive_debug()
    sys.exit(0 if success else 1)