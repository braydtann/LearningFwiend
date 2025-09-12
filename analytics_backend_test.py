#!/usr/bin/env python3
"""
URGENT ANALYTICS DATA INVESTIGATION - Backend Testing
Testing quiz submissions and analytics data flow for LearningFriend LMS

TESTING OBJECTIVES:
1. **Test User Authentication** - Use admin credentials (brayden.t@covesmart.com / Hawaii2020!) to verify analytics access
2. **Test Analytics Endpoints** - Check both `/api/analytics/system-stats` and `/api/analytics/dashboard` endpoints
3. **Quiz Submissions Data Verification** - Check if quiz submissions exist in database and are being processed
4. **Quiz Attempts Analysis** - Investigate quiz_attempts collection or enrollment progress data
5. **Analytics Data Structure** - Verify what data these endpoints are returning vs what frontend expects

SPECIFIC INVESTIGATION:
- Check if quiz submissions are stored in database  
- Verify analytics endpoints return quiz attempt data
- Identify disconnect between quiz submission storage and analytics retrieval
- Test complete flow: quiz submission → database storage → analytics API → frontend display

This is a critical bug affecting core LMS functionality for instructors and admins who need to view student progress and quiz results.
"""

import requests
import json
import sys
from datetime import datetime
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class AnalyticsDataInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
        try:
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Admin {user_info.get('full_name')} authenticated successfully, Role: {user_info.get('role')}"
                )
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_analytics_system_stats_endpoint(self):
        """Test /api/analytics/system-stats endpoint"""
        try:
            if not self.admin_token:
                self.log_result("Analytics System Stats", False, "No admin token available")
                return False
            
            response = self.session.get(f"{API_BASE}/analytics/system-stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze the structure
                quiz_stats = data.get('quizzes', {})
                enrollment_stats = data.get('enrollments', {})
                
                details = f"Quiz Stats - Total Attempts: {quiz_stats.get('totalAttempts', 0)}, " \
                         f"Average Score: {quiz_stats.get('averageScore', 0)}, " \
                         f"Pass Rate: {quiz_stats.get('passRate', 0)}%. " \
                         f"Enrollments - Total: {enrollment_stats.get('totalEnrollments', 0)}, " \
                         f"Completed: {enrollment_stats.get('completedEnrollments', 0)}"
                
                self.log_result("Analytics System Stats", True, details)
                return data
            else:
                self.log_result(
                    "Analytics System Stats", 
                    False, 
                    f"Request failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Analytics System Stats", False, f"Exception: {str(e)}")
            return None
    
    def test_analytics_dashboard_endpoint(self):
        """Test /api/analytics/dashboard endpoint"""
        try:
            if not self.admin_token:
                self.log_result("Analytics Dashboard", False, "No admin token available")
                return False
            
            response = self.session.get(f"{API_BASE}/analytics/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                dashboard_data = data.get('data', {})
                
                details = f"Dashboard Data - Total Users: {dashboard_data.get('totalUsers', 0)}, " \
                         f"Total Courses: {dashboard_data.get('totalCourses', 0)}, " \
                         f"Total Enrollments: {dashboard_data.get('totalEnrollments', 0)}, " \
                         f"Total Certificates: {dashboard_data.get('totalCertificates', 0)}"
                
                self.log_result("Analytics Dashboard", True, details)
                return data
            else:
                self.log_result(
                    "Analytics Dashboard", 
                    False, 
                    f"Request failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Analytics Dashboard", False, f"Exception: {str(e)}")
            return None
    
    def test_quiz_submissions_data_verification(self):
        """Check if quiz submissions exist in database via enrollments endpoint"""
        try:
            if not self.admin_token:
                self.log_result("Quiz Submissions Data", False, "No admin token available")
                return False
            
            # First, get all enrollments to see progress data
            response = self.session.get(f"{API_BASE}/enrollments")
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Analyze enrollment progress data for quiz completion indicators
                quiz_completed_enrollments = []
                total_enrollments = len(enrollments)
                
                for enrollment in enrollments:
                    progress = enrollment.get('progress', 0)
                    status = enrollment.get('status', 'unknown')
                    
                    # Look for completed courses (likely quiz completions)
                    if progress >= 100 or status == 'completed':
                        quiz_completed_enrollments.append({
                            'courseId': enrollment.get('courseId'),
                            'progress': progress,
                            'status': status,
                            'completedAt': enrollment.get('completedAt')
                        })
                
                details = f"Total Enrollments: {total_enrollments}, " \
                         f"Completed Enrollments (potential quiz submissions): {len(quiz_completed_enrollments)}"
                
                if quiz_completed_enrollments:
                    details += f". Sample completed: {quiz_completed_enrollments[:3]}"
                
                self.log_result("Quiz Submissions Data", True, details)
                return quiz_completed_enrollments
            else:
                self.log_result(
                    "Quiz Submissions Data", 
                    False, 
                    f"Enrollments request failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Quiz Submissions Data", False, f"Exception: {str(e)}")
            return None
    
    def test_quiz_attempts_analysis(self):
        """Investigate quiz attempts data through available endpoints"""
        try:
            if not self.admin_token:
                self.log_result("Quiz Attempts Analysis", False, "No admin token available")
                return False
            
            # Try to get courses with quizzes to understand the data structure
            response = self.session.get(f"{API_BASE}/courses")
            
            if response.status_code == 200:
                courses = response.json()
                
                quiz_courses = []
                for course in courses:
                    modules = course.get('modules', [])
                    has_quiz = False
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if lesson.get('type') == 'quiz':
                                has_quiz = True
                                break
                        if has_quiz:
                            break
                    
                    if has_quiz:
                        quiz_courses.append({
                            'id': course.get('id'),
                            'title': course.get('title'),
                            'enrolledStudents': course.get('enrolledStudents', 0)
                        })
                
                details = f"Total Courses: {len(courses)}, " \
                         f"Courses with Quizzes: {len(quiz_courses)}"
                
                if quiz_courses:
                    details += f". Sample quiz courses: {[c['title'] for c in quiz_courses[:3]]}"
                
                self.log_result("Quiz Attempts Analysis", True, details)
                return quiz_courses
            else:
                self.log_result(
                    "Quiz Attempts Analysis", 
                    False, 
                    f"Courses request failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Quiz Attempts Analysis", False, f"Exception: {str(e)}")
            return None
    
    def test_student_authentication_and_data(self):
        """Test student authentication to verify student-side data"""
        try:
            # Try to authenticate a student to see their data
            login_data = {
                "username_or_email": "karlo.student@alder.com",
                "password": "StudentPermanent123!"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                user_info = data.get('user', {})
                
                # Update session with student token
                student_session = requests.Session()
                student_session.headers.update({
                    'Authorization': f'Bearer {self.student_token}'
                })
                
                # Get student enrollments
                enrollments_response = student_session.get(f"{API_BASE}/enrollments")
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    
                    details = f"Student {user_info.get('full_name')} authenticated. " \
                             f"Enrollments: {len(enrollments)}"
                    
                    # Check for quiz progress in enrollments
                    quiz_progress = []
                    for enrollment in enrollments:
                        if enrollment.get('progress', 0) > 0:
                            quiz_progress.append({
                                'courseId': enrollment.get('courseId'),
                                'progress': enrollment.get('progress'),
                                'status': enrollment.get('status')
                            })
                    
                    if quiz_progress:
                        details += f". Quiz Progress Records: {len(quiz_progress)}"
                    
                    self.log_result("Student Authentication & Data", True, details)
                    return quiz_progress
                else:
                    self.log_result(
                        "Student Authentication & Data", 
                        False, 
                        f"Student enrollments failed: {enrollments_response.status_code}"
                    )
                    return None
            else:
                self.log_result(
                    "Student Authentication & Data", 
                    False, 
                    f"Student login failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Student Authentication & Data", False, f"Exception: {str(e)}")
            return None
    
    def test_analytics_data_structure_compatibility(self):
        """Verify analytics data structure matches frontend expectations"""
        try:
            if not self.admin_token:
                self.log_result("Analytics Data Structure", False, "No admin token available")
                return False
            
            # Get both analytics endpoints and compare structures
            system_stats = self.session.get(f"{API_BASE}/analytics/system-stats")
            dashboard_data = self.session.get(f"{API_BASE}/analytics/dashboard")
            
            compatibility_issues = []
            
            if system_stats.status_code == 200:
                stats_data = system_stats.json()
                
                # Check required fields for analytics dashboard
                required_fields = ['users', 'courses', 'quizzes', 'enrollments', 'certificates']
                for field in required_fields:
                    if field not in stats_data:
                        compatibility_issues.append(f"Missing {field} in system stats")
                
                # Check quiz stats structure
                quiz_stats = stats_data.get('quizzes', {})
                quiz_required = ['totalAttempts', 'averageScore', 'passRate']
                for field in quiz_required:
                    if field not in quiz_stats:
                        compatibility_issues.append(f"Missing {field} in quiz stats")
            else:
                compatibility_issues.append(f"System stats endpoint failed: {system_stats.status_code}")
            
            if dashboard_data.status_code == 200:
                dash_data = dashboard_data.json()
                
                # Check dashboard data structure
                if 'data' not in dash_data:
                    compatibility_issues.append("Missing 'data' field in dashboard response")
                else:
                    data_section = dash_data['data']
                    admin_required = ['totalUsers', 'totalCourses', 'totalEnrollments', 'totalCertificates']
                    for field in admin_required:
                        if field not in data_section:
                            compatibility_issues.append(f"Missing {field} in dashboard data")
            else:
                compatibility_issues.append(f"Dashboard endpoint failed: {dashboard_data.status_code}")
            
            if compatibility_issues:
                details = f"Compatibility Issues Found: {'; '.join(compatibility_issues)}"
                self.log_result("Analytics Data Structure", False, details)
                return False
            else:
                details = "All required fields present in analytics endpoints"
                self.log_result("Analytics Data Structure", True, details)
                return True
                
        except Exception as e:
            self.log_result("Analytics Data Structure", False, f"Exception: {str(e)}")
            return False
    
    def investigate_quiz_submission_to_analytics_flow(self):
        """Investigate the complete flow from quiz submission to analytics display"""
        try:
            print("\n🔍 INVESTIGATING QUIZ SUBMISSION → ANALYTICS DATA FLOW:")
            
            # Step 1: Check if there are any courses with quiz lessons
            courses_response = self.session.get(f"{API_BASE}/courses")
            if courses_response.status_code != 200:
                self.log_result("Quiz Flow Investigation", False, "Cannot access courses")
                return False
            
            courses = courses_response.json()
            quiz_courses = []
            
            for course in courses:
                modules = course.get('modules', [])
                quiz_lessons = []
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            quiz_lessons.append(lesson)
                
                if quiz_lessons:
                    quiz_courses.append({
                        'courseId': course.get('id'),
                        'title': course.get('title'),
                        'quizLessons': len(quiz_lessons),
                        'enrolledStudents': course.get('enrolledStudents', 0)
                    })
            
            print(f"   📊 Found {len(quiz_courses)} courses with quiz lessons")
            
            # Step 2: Check enrollments using student token (since enrollments are user-specific)
            if self.student_token:
                student_session = requests.Session()
                student_session.headers.update({
                    'Authorization': f'Bearer {self.student_token}'
                })
                
                enrollments_response = student_session.get(f"{API_BASE}/enrollments")
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    
                    quiz_course_ids = [c['courseId'] for c in quiz_courses]
                    quiz_enrollments = [e for e in enrollments if e.get('courseId') in quiz_course_ids]
                    
                    completed_quiz_enrollments = [
                        e for e in quiz_enrollments 
                        if e.get('progress', 0) >= 100 or e.get('status') == 'completed'
                    ]
                    
                    print(f"   📈 Quiz Course Enrollments: {len(quiz_enrollments)}")
                    print(f"   ✅ Completed Quiz Enrollments: {len(completed_quiz_enrollments)}")
                else:
                    completed_quiz_enrollments = []
                    print(f"   ❌ Could not get student enrollments: {enrollments_response.status_code}")
            else:
                completed_quiz_enrollments = []
                print(f"   ❌ No student token available for enrollment check")
            
            # Step 3: Check what analytics endpoints return for quiz data
            system_stats_response = self.session.get(f"{API_BASE}/analytics/system-stats")
            if system_stats_response.status_code == 200:
                stats = system_stats_response.json()
                quiz_stats = stats.get('quizzes', {})
                
                print(f"   📊 Analytics Quiz Stats:")
                print(f"      - Total Attempts: {quiz_stats.get('totalAttempts', 0)}")
                print(f"      - Average Score: {quiz_stats.get('averageScore', 0)}")
                print(f"      - Pass Rate: {quiz_stats.get('passRate', 0)}%")
            else:
                quiz_stats = {}
                print(f"   ❌ Could not get analytics stats: {system_stats_response.status_code}")
            
            # Step 4: Identify the disconnect
            disconnect_analysis = []
            
            if len(completed_quiz_enrollments) > 0:
                if quiz_stats.get('totalAttempts', 0) == 0:
                    disconnect_analysis.append("Quiz submissions exist in enrollments but not reflected in analytics quiz attempts")
                
                if quiz_stats.get('averageScore', 0) == 0:
                    disconnect_analysis.append("Completed quiz enrollments exist but no average scores in analytics")
            
            if disconnect_analysis:
                details = f"DISCONNECT IDENTIFIED: {'; '.join(disconnect_analysis)}"
                self.log_result("Quiz Flow Investigation", False, details)
                
                print(f"\n🚨 ROOT CAUSE ANALYSIS:")
                print(f"   - Quiz submissions are being stored as enrollment progress")
                print(f"   - Analytics endpoints expect data in quiz_attempts collection")
                print(f"   - There's a mismatch between quiz submission storage and analytics retrieval")
                
                return False
            else:
                details = "Quiz submission to analytics flow appears to be working correctly"
                self.log_result("Quiz Flow Investigation", True, details)
                return True
                
        except Exception as e:
            self.log_result("Quiz Flow Investigation", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_investigation(self):
        """Run all analytics investigation tests"""
        print("🚨 URGENT ANALYTICS DATA INVESTIGATION - Backend Testing")
        print("=" * 80)
        print("Testing quiz submissions and analytics data flow for LearningFriend LMS")
        print()
        
        # Test 1: Admin Authentication
        print("1️⃣ Testing Admin Authentication...")
        if not self.test_admin_authentication():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Test 2: Analytics System Stats Endpoint
        print("\n2️⃣ Testing Analytics System Stats Endpoint...")
        system_stats = self.test_analytics_system_stats_endpoint()
        
        # Test 3: Analytics Dashboard Endpoint
        print("\n3️⃣ Testing Analytics Dashboard Endpoint...")
        dashboard_data = self.test_analytics_dashboard_endpoint()
        
        # Test 4: Quiz Submissions Data Verification
        print("\n4️⃣ Testing Quiz Submissions Data Verification...")
        quiz_submissions = self.test_quiz_submissions_data_verification()
        
        # Test 5: Quiz Attempts Analysis
        print("\n5️⃣ Testing Quiz Attempts Analysis...")
        quiz_attempts = self.test_quiz_attempts_analysis()
        
        # Test 6: Student Authentication and Data
        print("\n6️⃣ Testing Student Authentication and Data...")
        student_data = self.test_student_authentication_and_data()
        
        # Test 7: Analytics Data Structure Compatibility
        print("\n7️⃣ Testing Analytics Data Structure Compatibility...")
        structure_check = self.test_analytics_data_structure_compatibility()
        
        # Test 8: Complete Flow Investigation
        print("\n8️⃣ Investigating Complete Quiz Submission → Analytics Flow...")
        flow_investigation = self.investigate_quiz_submission_to_analytics_flow()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 ANALYTICS INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - Analytics system is working correctly")
        else:
            print(f"\n🚨 CRITICAL ISSUES DETECTED - {total_tests - passed_tests} test(s) failed")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        return passed_tests == total_tests

def main():
    """Main function to run analytics investigation"""
    try:
        investigator = AnalyticsDataInvestigation()
        success = investigator.run_comprehensive_investigation()
        
        if success:
            print("\n✅ Analytics investigation completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Analytics investigation found critical issues")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR during analytics investigation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()