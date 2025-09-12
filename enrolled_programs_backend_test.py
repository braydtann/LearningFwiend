#!/usr/bin/env python3

"""
Backend Testing for Student Dashboard Enhanced with Enrolled Programs Functionality
Testing the backend support for the new "Enrolled Programs" dashboard section

Review Request Focus:
1. Student authentication with brayden.student@learningfwiend.com / Cove1234!
2. GET /api/enrollments - verify student enrollments are returned
3. GET /api/classrooms - verify student can access classrooms they're enrolled in  
4. GET /api/programs - verify student can access programs
5. GET /api/courses - verify student can access courses
6. Test the data structure needed for the new enrolled programs section:
   - Verify classroom assignments with program IDs
   - Check program course IDs and course completion status
   - Test program progress calculation logic
7. Verify the program final exam route structure for /final-test/program/:programId
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use frontend env URL
BACKEND_URL = "https://learning-analytics-2.preview.emergentagent.com/api"

# Test credentials from review request
STUDENT_EMAIL = "brayden.student@learningfwiend.com"
STUDENT_PASSWORD = "Cove1234!"

class EnrolledProgramsTester:
    def __init__(self):
        self.session = requests.Session()
        self.student_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_student(self):
        """Test student authentication with provided credentials"""
        print("🔐 Testing Student Authentication...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.student_token}'
                })
                
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                self.log_test(
                    "Student Authentication", 
                    True, 
                    f"Student: {user_info.get('full_name')} ({user_info.get('email')}) - Role: {user_info.get('role')} - Password Change Required: {requires_password_change}"
                )
                return True
            else:
                self.log_test(
                    "Student Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def test_student_enrollments(self):
        """Test GET /api/enrollments - verify student enrollments are returned"""
        print("📚 Testing Student Enrollments API...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/enrollments")
            
            if response.status_code == 200:
                enrollments = response.json()
                enrollment_count = len(enrollments)
                
                # Analyze enrollment data structure for enrolled programs
                enrollment_details = []
                course_ids = set()
                
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId', 'N/A')
                    progress = enrollment.get('progress', 0)
                    status = enrollment.get('status', 'N/A')
                    enrolled_at = enrollment.get('enrolledAt', 'N/A')
                    
                    course_ids.add(course_id)
                    
                    if len(enrollment_details) < 3:  # Show first 3 for details
                        enrollment_details.append(f"Course: {course_id[:8]}... Progress: {progress}% Status: {status}")
                
                self.log_test(
                    "GET /api/enrollments", 
                    True, 
                    f"Found {enrollment_count} enrollments. Unique courses: {len(course_ids)}. Sample: {'; '.join(enrollment_details[:2])}"
                )
                return enrollments
            else:
                self.log_test(
                    "GET /api/enrollments", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test("GET /api/enrollments", False, f"Exception: {str(e)}")
            return []

    def test_student_classrooms_access(self):
        """Test GET /api/classrooms - verify student can access classrooms they're enrolled in"""
        print("🏫 Testing Student Classrooms Access...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/classrooms")
            
            if response.status_code == 200:
                classrooms = response.json()
                classroom_count = len(classrooms)
                
                # Analyze classroom data structure for program assignments
                classroom_details = []
                program_classrooms = 0
                total_programs = 0
                total_direct_courses = 0
                
                for classroom in classrooms:
                    classroom_id = classroom.get('id', 'N/A')
                    title = classroom.get('title', 'N/A')
                    program_ids = classroom.get('programIds', [])
                    course_ids = classroom.get('courseIds', [])
                    student_ids = classroom.get('studentIds', [])
                    
                    total_programs += len(program_ids)
                    total_direct_courses += len(course_ids)
                    
                    if program_ids:
                        program_classrooms += 1
                        if len(classroom_details) < 3:
                            classroom_details.append(f"{title}: {len(program_ids)} programs, {len(course_ids)} direct courses, {len(student_ids)} students")
                    else:
                        if len(classroom_details) < 3:
                            classroom_details.append(f"{title}: {len(course_ids)} direct courses only, {len(student_ids)} students")
                
                self.log_test(
                    "GET /api/classrooms", 
                    True, 
                    f"Found {classroom_count} classrooms ({program_classrooms} with programs). Total programs: {total_programs}, Direct courses: {total_direct_courses}. Sample: {'; '.join(classroom_details[:2])}"
                )
                return classrooms
            else:
                self.log_test(
                    "GET /api/classrooms", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test("GET /api/classrooms", False, f"Exception: {str(e)}")
            return []

    def test_student_programs_access(self):
        """Test GET /api/programs - verify student can access programs"""
        print("📋 Testing Student Programs Access...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/programs")
            
            if response.status_code == 200:
                programs = response.json()
                program_count = len(programs)
                
                # Analyze program data structure for course IDs and completion tracking
                program_details = []
                total_program_courses = 0
                
                for program in programs:
                    program_id = program.get('id', 'N/A')
                    title = program.get('title', 'N/A')
                    course_ids = program.get('courseIds', [])
                    nested_program_ids = program.get('nestedProgramIds', [])
                    is_active = program.get('isActive', False)
                    course_count = len(course_ids)
                    
                    total_program_courses += course_count
                    
                    if len(program_details) < 3:  # Show first 3 for details
                        program_details.append(f"{title}: {course_count} courses, {len(nested_program_ids)} nested programs, Active: {is_active}")
                
                self.log_test(
                    "GET /api/programs", 
                    True, 
                    f"Found {program_count} programs with {total_program_courses} total courses. Sample: {'; '.join(program_details[:2])}"
                )
                return programs
            else:
                self.log_test(
                    "GET /api/programs", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test("GET /api/programs", False, f"Exception: {str(e)}")
            return []

    def test_student_courses_access(self):
        """Test GET /api/courses - verify student can access courses"""
        print("📖 Testing Student Courses Access...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/courses")
            
            if response.status_code == 200:
                courses = response.json()
                course_count = len(courses)
                
                # Analyze course data structure for completion tracking
                course_details = []
                courses_with_modules = 0
                
                for course in courses:
                    course_id = course.get('id', 'N/A')
                    title = course.get('title', 'N/A')
                    status = course.get('status', 'N/A')
                    modules = course.get('modules', [])
                    enrolled_students = course.get('enrolledStudents', 0)
                    
                    if modules:
                        courses_with_modules += 1
                    
                    if len(course_details) < 3:  # Show first 3 for details
                        course_details.append(f"{title}: {len(modules)} modules, {enrolled_students} students, status: {status}")
                
                self.log_test(
                    "GET /api/courses", 
                    True, 
                    f"Found {course_count} courses ({courses_with_modules} with modules). Sample: {'; '.join(course_details[:2])}"
                )
                return courses
            else:
                self.log_test(
                    "GET /api/courses", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test("GET /api/courses", False, f"Exception: {str(e)}")
            return []

    def test_classroom_program_assignments(self, classrooms, programs):
        """Verify classroom assignments with program IDs"""
        print("🔗 Testing Classroom Program Assignments...")
        
        try:
            # Find classrooms with program assignments
            classrooms_with_programs = [c for c in classrooms if c.get('programIds')]
            
            assignment_details = []
            valid_assignments = 0
            
            for classroom in classrooms_with_programs:
                classroom_title = classroom.get('title', 'N/A')
                program_ids = classroom.get('programIds', [])
                
                # Verify each program ID exists in programs list
                valid_program_ids = []
                for program_id in program_ids:
                    program_exists = any(p.get('id') == program_id for p in programs)
                    if program_exists:
                        valid_program_ids.append(program_id)
                        valid_assignments += 1
                
                if len(assignment_details) < 3:
                    assignment_details.append(f"{classroom_title}: {len(valid_program_ids)}/{len(program_ids)} valid programs")
            
            self.log_test(
                "Classroom Program Assignments", 
                len(classrooms_with_programs) > 0, 
                f"Found {len(classrooms_with_programs)} classrooms with programs, {valid_assignments} valid assignments. Sample: {'; '.join(assignment_details[:2])}"
            )
            return classrooms_with_programs
            
        except Exception as e:
            self.log_test("Classroom Program Assignments", False, f"Exception: {str(e)}")
            return []

    def test_program_course_completion_status(self, programs, enrollments):
        """Check program course IDs and course completion status"""
        print("📊 Testing Program Course Completion Status...")
        
        try:
            enrolled_course_ids = {e.get('courseId') for e in enrollments}
            
            program_completion_data = []
            total_program_courses = 0
            enrolled_program_courses = 0
            
            for program in programs:
                program_id = program.get('id')
                program_title = program.get('title', 'N/A')
                course_ids = program.get('courseIds', [])
                
                total_program_courses += len(course_ids)
                
                # Check which program courses the student is enrolled in
                enrolled_courses = [cid for cid in course_ids if cid in enrolled_course_ids]
                enrolled_program_courses += len(enrolled_courses)
                
                # Calculate completion status for enrolled courses
                completed_courses = 0
                total_progress = 0
                
                for course_id in enrolled_courses:
                    enrollment = next((e for e in enrollments if e.get('courseId') == course_id), None)
                    if enrollment:
                        progress = enrollment.get('progress', 0)
                        total_progress += progress
                        if progress >= 100:
                            completed_courses += 1
                
                if enrolled_courses:
                    avg_progress = total_progress / len(enrolled_courses)
                    completion_rate = (completed_courses / len(enrolled_courses)) * 100
                    
                    if len(program_completion_data) < 3:
                        program_completion_data.append(
                            f"{program_title}: {len(enrolled_courses)}/{len(course_ids)} enrolled, "
                            f"{completed_courses} completed, {avg_progress:.1f}% avg progress"
                        )
            
            self.log_test(
                "Program Course Completion Status", 
                True, 
                f"Analyzed {len(programs)} programs. Total courses: {total_program_courses}, Enrolled: {enrolled_program_courses}. Sample: {'; '.join(program_completion_data[:2])}"
            )
            return program_completion_data
            
        except Exception as e:
            self.log_test("Program Course Completion Status", False, f"Exception: {str(e)}")
            return []

    def test_program_progress_calculation(self, classrooms, programs, enrollments):
        """Test program progress calculation logic"""
        print("🧮 Testing Program Progress Calculation Logic...")
        
        try:
            enrolled_course_ids = {e.get('courseId') for e in enrollments}
            
            # Find student's classrooms with programs
            student_program_progress = {}
            
            for classroom in classrooms:
                program_ids = classroom.get('programIds', [])
                classroom_title = classroom.get('title', 'N/A')
                
                for program_id in program_ids:
                    # Find the program
                    program = next((p for p in programs if p.get('id') == program_id), None)
                    if program:
                        program_title = program.get('title', 'N/A')
                        course_ids = program.get('courseIds', [])
                        
                        # Calculate progress for this program
                        enrolled_courses = [cid for cid in course_ids if cid in enrolled_course_ids]
                        
                        if enrolled_courses:
                            total_progress = 0
                            completed_courses = 0
                            course_progress_details = []
                            
                            for course_id in enrolled_courses:
                                enrollment = next((e for e in enrollments if e.get('courseId') == course_id), None)
                                if enrollment:
                                    progress = enrollment.get('progress', 0)
                                    status = enrollment.get('status', 'active')
                                    total_progress += progress
                                    
                                    if progress >= 100:
                                        completed_courses += 1
                                    
                                    course_progress_details.append({
                                        'course_id': course_id,
                                        'progress': progress,
                                        'status': status
                                    })
                            
                            avg_progress = total_progress / len(enrolled_courses) if enrolled_courses else 0
                            completion_rate = (completed_courses / len(course_ids)) * 100
                            
                            student_program_progress[program_id] = {
                                'program_title': program_title,
                                'classroom_title': classroom_title,
                                'total_courses': len(course_ids),
                                'enrolled_courses': len(enrolled_courses),
                                'completed_courses': completed_courses,
                                'average_progress': avg_progress,
                                'completion_rate': completion_rate,
                                'course_details': course_progress_details
                            }
            
            # Generate progress calculation summary
            progress_summary = []
            for prog_id, prog_data in list(student_program_progress.items())[:3]:
                progress_summary.append(
                    f"{prog_data['program_title']}: {prog_data['completed_courses']}/{prog_data['total_courses']} courses, "
                    f"{prog_data['average_progress']:.1f}% progress, {prog_data['completion_rate']:.1f}% completion"
                )
            
            self.log_test(
                "Program Progress Calculation Logic", 
                len(student_program_progress) > 0, 
                f"Calculated progress for {len(student_program_progress)} programs. Sample: {'; '.join(progress_summary[:2])}"
            )
            return student_program_progress
            
        except Exception as e:
            self.log_test("Program Progress Calculation Logic", False, f"Exception: {str(e)}")
            return {}

    def test_final_exam_route_structure(self, programs):
        """Verify the program final exam route structure for /final-test/program/:programId"""
        print("🎯 Testing Program Final Exam Route Structure...")
        
        try:
            # Test route structure for programs with courses
            programs_ready_for_final_exam = []
            
            for program in programs:
                program_id = program.get('id')
                title = program.get('title', 'N/A')
                course_ids = program.get('courseIds', [])
                is_active = program.get('isActive', False)
                
                # Programs need courses to have final exams
                if course_ids and is_active:
                    final_exam_route = f"/final-test/program/{program_id}"
                    
                    programs_ready_for_final_exam.append({
                        'program_id': program_id,
                        'title': title,
                        'course_count': len(course_ids),
                        'final_exam_route': final_exam_route,
                        'is_active': is_active
                    })
            
            # Verify route structure components
            route_examples = []
            for prog in programs_ready_for_final_exam[:3]:  # Show first 3
                route_examples.append(f"{prog['title']}: {prog['final_exam_route']} ({prog['course_count']} courses)")
            
            self.log_test(
                "Program Final Exam Route Structure", 
                len(programs_ready_for_final_exam) > 0, 
                f"Found {len(programs_ready_for_final_exam)} programs ready for final exams. Routes: {'; '.join(route_examples[:2])}"
            )
            return programs_ready_for_final_exam
            
        except Exception as e:
            self.log_test("Program Final Exam Route Structure", False, f"Exception: {str(e)}")
            return []

    def run_comprehensive_test(self):
        """Run all tests for student dashboard enhanced with enrolled programs functionality"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING FOR STUDENT DASHBOARD ENHANCED WITH ENROLLED PROGRAMS")
        print("=" * 100)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Student Credentials: {STUDENT_EMAIL} / {STUDENT_PASSWORD}")
        print("=" * 100)
        print()
        
        # Test 1: Student Authentication
        if not self.authenticate_student():
            print("❌ Authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Student Enrollments
        enrollments = self.test_student_enrollments()
        
        # Test 3: Student Classrooms Access
        classrooms = self.test_student_classrooms_access()
        
        # Test 4: Student Programs Access
        programs = self.test_student_programs_access()
        
        # Test 5: Student Courses Access
        courses = self.test_student_courses_access()
        
        # Test 6: Classroom Program Assignments
        program_classrooms = self.test_classroom_program_assignments(classrooms, programs)
        
        # Test 7: Program Course Completion Status
        completion_data = self.test_program_course_completion_status(programs, enrollments)
        
        # Test 8: Program Progress Calculation Logic
        progress_data = self.test_program_progress_calculation(classrooms, programs, enrollments)
        
        # Test 9: Final Exam Route Structure
        final_exam_programs = self.test_final_exam_route_structure(programs)
        
        # Summary
        print("=" * 100)
        print("📊 TEST SUMMARY")
        print("=" * 100)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {total_tests - passed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("🎯 ENROLLED PROGRAMS FUNCTIONALITY ASSESSMENT:")
        
        if success_rate >= 85:
            print("✅ EXCELLENT - Backend fully supports enrolled programs functionality")
        elif success_rate >= 70:
            print("⚠️  GOOD - Backend mostly supports enrolled programs functionality with minor issues")
        else:
            print("❌ NEEDS WORK - Backend has significant issues supporting enrolled programs functionality")
        
        # Specific recommendations for enrolled programs dashboard
        print()
        print("📋 BACKEND READINESS FOR ENROLLED PROGRAMS DASHBOARD:")
        
        auth_working = any(r['test'] == 'Student Authentication' and r['success'] for r in self.test_results)
        enrollments_working = any(r['test'] == 'GET /api/enrollments' and r['success'] for r in self.test_results)
        classrooms_working = any(r['test'] == 'GET /api/classrooms' and r['success'] for r in self.test_results)
        programs_working = any(r['test'] == 'GET /api/programs' and r['success'] for r in self.test_results)
        courses_working = any(r['test'] == 'GET /api/courses' and r['success'] for r in self.test_results)
        assignments_working = any(r['test'] == 'Classroom Program Assignments' and r['success'] for r in self.test_results)
        completion_working = any(r['test'] == 'Program Course Completion Status' and r['success'] for r in self.test_results)
        progress_working = any(r['test'] == 'Program Progress Calculation Logic' and r['success'] for r in self.test_results)
        final_exam_working = any(r['test'] == 'Program Final Exam Route Structure' and r['success'] for r in self.test_results)
        
        print(f"✅ Student Authentication: {'Working' if auth_working else 'Failed'}")
        print(f"✅ Enrollment Data API: {'Available' if enrollments_working else 'Failed'}")
        print(f"✅ Classroom Data API: {'Available' if classrooms_working else 'Failed'}")
        print(f"✅ Program Data API: {'Available' if programs_working else 'Failed'}")
        print(f"✅ Course Data API: {'Available' if courses_working else 'Failed'}")
        print(f"✅ Program Assignments: {'Valid' if assignments_working else 'Invalid'}")
        print(f"✅ Completion Tracking: {'Functional' if completion_working else 'Not Functional'}")
        print(f"✅ Progress Calculation: {'Working' if progress_working else 'Not Working'}")
        print(f"✅ Final Exam Routes: {'Ready' if final_exam_working else 'Not Ready'}")
        
        print()
        print("🎉 CONCLUSION:")
        if success_rate >= 85:
            print("The backend is READY to support the new 'Enrolled Programs' dashboard section!")
            print("All required APIs and data structures are working correctly.")
        elif success_rate >= 70:
            print("The backend is MOSTLY READY with minor issues that should be addressed.")
        else:
            print("The backend needs significant work before supporting enrolled programs functionality.")
        
        return success_rate >= 70

def main():
    """Main function to run the enrolled programs backend tests"""
    tester = EnrolledProgramsTester()
    
    try:
        success = tester.run_comprehensive_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()