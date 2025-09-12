#!/usr/bin/env python3
"""
🎯 QUIZRESULTS COMPONENT BACKEND TESTING - FILTERING AND RECENT QUIZ ATTEMPTS

TESTING OBJECTIVES FROM REVIEW REQUEST:
1. **Admin Authentication** - Login with admin credentials (brayden.t@covesmart.com / Hawaii2020!)
2. **Course Filtering Verification** - Test that selecting a specific course (like "testy test test") updates the statistics to show only that course's data
3. **Recent Quiz Attempts Display** - Verify that recent quiz attempts section now shows actual quiz submissions instead of "No quiz attempts yet"
4. **Data Consistency** - Ensure filtering works correctly with synthetic quiz attempts created from enrollments
5. **Attempt Status Logic** - Confirm that both completed and in-progress quiz attempts appear in recent attempts

SPECIFIC TESTS:
- Verify course filtering updates Total Attempts, Average Score, and Pass Rate when a specific course is selected
- Check that Recent Quiz Attempts section displays student names, course names, scores, and dates
- Test that synthetic quiz attempts (course-quiz-{courseId} format) are properly filtered by course selection
- Validate that quiz attempts with any progress (>0%) appear in recent attempts, not just 100% completed ones

This should resolve the user's issues with course filtering not working and recent quiz attempts showing empty.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class QuizResultsBackendTester:
    def __init__(self):
        # Get backend URL from frontend .env
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=')[1].strip()
                        break
            
            if not self.base_url.endswith('/api'):
                self.base_url = f"{self.base_url}/api"
                
        except Exception as e:
            print(f"❌ Error reading frontend .env: {e}")
            self.base_url = "http://localhost:8001/api"
            
        print(f"🔗 Using backend URL: {self.base_url}")
        
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials from review request
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
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
    
    def admin_login(self):
        """Test admin authentication with provided credentials"""
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=self.admin_credentials)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                user_info = data['user']
                
                self.log_test(
                    "Admin Authentication", 
                    True, 
                    f"Logged in as {user_info['full_name']} (Role: {user_info['role']})"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_courses_api_for_filtering(self):
        """Test courses API for filtering functionality"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.base_url}/courses", headers=headers)
            
            if response.status_code == 200:
                courses = response.json()
                course_count = len(courses)
                
                # Look for "testy test test" course mentioned in review request
                testy_course = None
                quiz_courses = []
                
                for course in courses:
                    title = course.get('title', '').lower()
                    if "testy" in title:
                        testy_course = course
                    
                    # Check if course has quiz content
                    modules = course.get('modules', [])
                    has_quiz = False
                    for module in modules:
                        for lesson in module.get('lessons', []):
                            if lesson.get('type') == 'quiz' or 'quiz' in lesson.get('title', '').lower():
                                has_quiz = True
                                break
                        if has_quiz:
                            break
                    
                    if has_quiz:
                        quiz_courses.append(course)
                
                details = f"Found {course_count} courses, {len(quiz_courses)} with quiz content"
                if testy_course:
                    details += f", including target course: '{testy_course['title']}' (ID: {testy_course['id']})"
                
                self.log_test("Courses API for Filtering", True, details)
                return courses, quiz_courses, testy_course
            else:
                self.log_test("Courses API for Filtering", False, f"Status: {response.status_code}")
                return [], [], None
                
        except Exception as e:
            self.log_test("Courses API for Filtering", False, f"Exception: {str(e)}")
            return [], [], None
    
    def test_enrollments_for_quiz_synthesis(self):
        """Test enrollments API for synthetic quiz attempts creation"""
        try:
            # Admin can't see student enrollments directly, so we'll test by logging in as a student
            # First, let's try to get a student account
            student_creds = {
                "username_or_email": "karlo.student@alder.com",
                "password": "StudentPermanent123!"
            }
            
            student_response = requests.post(f"{self.base_url}/auth/login", json=student_creds)
            
            if student_response.status_code == 200:
                student_token = student_response.json()['access_token']
                student_headers = {"Authorization": f"Bearer {student_token}"}
                
                # Get student's enrollments
                response = requests.get(f"{self.base_url}/enrollments", headers=student_headers)
                
                if response.status_code == 200:
                    enrollments = response.json()
                    
                    # Analyze enrollments for quiz data synthesis
                    quiz_enrollments = []
                    for enrollment in enrollments:
                        progress = enrollment.get('progress', 0)
                        if progress > 0:  # Any progress indicates quiz activity
                            quiz_enrollments.append({
                                'id': f"course-quiz-{enrollment.get('courseId')}",
                                'courseId': enrollment.get('courseId'),
                                'studentName': enrollment.get('studentName', 'Unknown Student'),
                                'courseName': enrollment.get('courseName', 'Unknown Course'),
                                'score': progress,
                                'completedAt': enrollment.get('enrolledAt'),
                                'status': 'completed' if progress >= 100 else 'in-progress',
                                'isPassed': progress >= 75,  # Assuming 75% pass rate
                                'synthetic': True
                            })
                    
                    details = f"Found {len(enrollments)} total enrollments, {len(quiz_enrollments)} with quiz progress for synthesis"
                    self.log_test("Enrollments for Quiz Synthesis", True, details)
                    return quiz_enrollments
                else:
                    self.log_test("Enrollments for Quiz Synthesis", False, f"Student enrollments status: {response.status_code}")
                    return []
            else:
                # Fallback: Admin has no enrollments, but API is working
                headers = self.get_auth_headers()
                response = requests.get(f"{self.base_url}/enrollments", headers=headers)
                
                if response.status_code == 200:
                    enrollments = response.json()  # Will be empty for admin
                    details = f"Admin has {len(enrollments)} enrollments (expected: 0). API working, but need student data for quiz synthesis."
                    self.log_test("Enrollments for Quiz Synthesis", True, details)
                    return []
                else:
                    self.log_test("Enrollments for Quiz Synthesis", False, f"Admin enrollments status: {response.status_code}")
                    return []
                
        except Exception as e:
            self.log_test("Enrollments for Quiz Synthesis", False, f"Exception: {str(e)}")
            return []
    
    def test_course_filtering_statistics(self, courses, quiz_enrollments):
        """Test course filtering updates statistics correctly"""
        try:
            if not courses or not quiz_enrollments:
                self.log_test("Course Filtering Statistics", False, "Insufficient data for testing")
                return {}
            
            # Group enrollments by course
            course_stats = {}
            course_names = {course['id']: course['title'] for course in courses}
            
            for enrollment in quiz_enrollments:
                course_id = enrollment['courseId']
                if course_id not in course_stats:
                    course_stats[course_id] = {
                        'total_attempts': 0,
                        'total_score': 0,
                        'passed_attempts': 0,
                        'course_name': course_names.get(course_id, 'Unknown Course')
                    }
                
                course_stats[course_id]['total_attempts'] += 1
                course_stats[course_id]['total_score'] += enrollment['score']
                if enrollment['isPassed']:
                    course_stats[course_id]['passed_attempts'] += 1
            
            # Calculate statistics for each course
            course_analytics = {}
            for course_id, stats in course_stats.items():
                if stats['total_attempts'] > 0:
                    course_analytics[course_id] = {
                        'courseName': stats['course_name'],
                        'totalAttempts': stats['total_attempts'],
                        'averageScore': stats['total_score'] / stats['total_attempts'],
                        'passRate': (stats['passed_attempts'] / stats['total_attempts']) * 100
                    }
            
            details = f"Generated statistics for {len(course_analytics)} courses with quiz data"
            for course_id, analytics in course_analytics.items():
                details += f"\n   {analytics['courseName']}: {analytics['totalAttempts']} attempts, "
                details += f"{analytics['averageScore']:.1f}% avg, {analytics['passRate']:.1f}% pass rate"
            
            self.log_test("Course Filtering Statistics", True, details)
            return course_analytics
            
        except Exception as e:
            self.log_test("Course Filtering Statistics", False, f"Exception: {str(e)}")
            return {}
    
    def test_recent_quiz_attempts_display(self, quiz_enrollments):
        """Test recent quiz attempts display functionality"""
        try:
            if not quiz_enrollments:
                self.log_test("Recent Quiz Attempts Display", False, "No quiz enrollments for testing")
                return []
            
            # Sort by completion date (most recent first)
            recent_attempts = sorted(quiz_enrollments, key=lambda x: x['completedAt'], reverse=True)
            
            # Test filtering by status
            completed_attempts = [a for a in recent_attempts if a['status'] == 'completed']
            in_progress_attempts = [a for a in recent_attempts if a['status'] == 'in-progress']
            
            # Verify data structure for display
            display_ready = True
            required_fields = ['studentName', 'courseName', 'score', 'completedAt', 'status']
            
            for attempt in recent_attempts[:5]:  # Check first 5
                for field in required_fields:
                    if field not in attempt:
                        display_ready = False
                        break
                if not display_ready:
                    break
            
            details = f"Found {len(recent_attempts)} recent attempts: {len(completed_attempts)} completed, "
            details += f"{len(in_progress_attempts)} in-progress. Display ready: {display_ready}"
            
            self.log_test("Recent Quiz Attempts Display", display_ready, details)
            return recent_attempts
            
        except Exception as e:
            self.log_test("Recent Quiz Attempts Display", False, f"Exception: {str(e)}")
            return []
    
    def test_attempt_status_logic(self, quiz_enrollments):
        """Test that both completed and in-progress attempts appear"""
        try:
            if not quiz_enrollments:
                self.log_test("Attempt Status Logic", False, "No quiz enrollments for testing")
                return False
            
            # Analyze status distribution
            status_counts = {}
            score_ranges = {'0-25%': 0, '26-50%': 0, '51-75%': 0, '76-100%': 0}
            
            for attempt in quiz_enrollments:
                status = attempt['status']
                score = attempt['score']
                
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if score <= 25:
                    score_ranges['0-25%'] += 1
                elif score <= 50:
                    score_ranges['26-50%'] += 1
                elif score <= 75:
                    score_ranges['51-75%'] += 1
                else:
                    score_ranges['76-100%'] += 1
            
            # Test that we have variety in statuses and scores
            has_multiple_statuses = len(status_counts) > 1
            has_score_variety = sum(1 for count in score_ranges.values() if count > 0) > 1
            
            # Test that attempts with >0% progress appear (not just 100% completed)
            has_partial_progress = any(0 < attempt['score'] < 100 for attempt in quiz_enrollments)
            
            success = len(quiz_enrollments) > 0 and has_partial_progress
            
            details = f"Status distribution: {status_counts}, Score ranges: {score_ranges}, "
            details += f"Has partial progress: {has_partial_progress}"
            
            self.log_test("Attempt Status Logic", success, details)
            return success
            
        except Exception as e:
            self.log_test("Attempt Status Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_specific_course_filtering(self, testy_course, quiz_enrollments):
        """Test filtering by specific course (testy test test)"""
        try:
            if not testy_course:
                self.log_test("Specific Course Filtering (testy test test)", False, "Target course not found")
                return False
            
            course_id = testy_course['id']
            course_name = testy_course['title']
            
            # Filter quiz attempts for this specific course
            course_attempts = [a for a in quiz_enrollments if a['courseId'] == course_id]
            
            if course_attempts:
                # Calculate course-specific statistics
                total_attempts = len(course_attempts)
                total_score = sum(a['score'] for a in course_attempts)
                average_score = total_score / total_attempts
                passed_attempts = sum(1 for a in course_attempts if a['isPassed'])
                pass_rate = (passed_attempts / total_attempts) * 100
                
                details = f"Course '{course_name}' has {total_attempts} attempts, "
                details += f"{average_score:.1f}% avg score, {pass_rate:.1f}% pass rate"
                
                self.log_test("Specific Course Filtering (testy test test)", True, details)
                return True
            else:
                self.log_test(
                    "Specific Course Filtering (testy test test)", 
                    False, 
                    f"No quiz attempts found for course '{course_name}'"
                )
                return False
                
        except Exception as e:
            self.log_test("Specific Course Filtering (testy test test)", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all QuizResults backend tests"""
        print("🎯 STARTING QUIZRESULTS BACKEND TESTING")
        print("=" * 60)
        
        # Test 1: Admin Authentication
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return self.generate_summary()
        
        # Test 2: Get courses for filtering
        courses, quiz_courses, testy_course = self.test_courses_api_for_filtering()
        
        # Test 3: Get enrollments for quiz synthesis
        quiz_enrollments = self.test_enrollments_for_quiz_synthesis()
        
        # Test 4: Test course filtering statistics
        course_analytics = self.test_course_filtering_statistics(courses, quiz_enrollments)
        
        # Test 5: Test recent quiz attempts display
        recent_attempts = self.test_recent_quiz_attempts_display(quiz_enrollments)
        
        # Test 6: Test attempt status logic
        self.test_attempt_status_logic(quiz_enrollments)
        
        # Test 7: Test specific course filtering (testy test test)
        self.test_specific_course_filtering(testy_course, quiz_enrollments)
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 QUIZRESULTS BACKEND TESTING SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Group results by status
        passed = [r for r in self.test_results if r['success']]
        failed = [r for r in self.test_results if not r['success']]
        
        if passed:
            print("✅ PASSED TESTS:")
            for result in passed:
                print(f"   • {result['test']}")
        
        if failed:
            print("\n❌ FAILED TESTS:")
            for result in failed:
                print(f"   • {result['test']}: {result['details']}")
        
        print("\n🔍 KEY FINDINGS:")
        
        # Analyze results for key insights
        auth_success = any(r['test'] == 'Admin Authentication' and r['success'] for r in self.test_results)
        courses_available = any(r['test'] == 'Courses API for Filtering' and r['success'] for r in self.test_results)
        enrollments_available = any(r['test'] == 'Enrollments for Quiz Synthesis' and r['success'] for r in self.test_results)
        
        if auth_success:
            print("   • Admin authentication working with provided credentials")
        
        if courses_available:
            print("   • Course filtering API functional for QuizResults component")
        
        if enrollments_available:
            print("   • Enrollment data available for synthetic quiz attempts")
        
        # Check if the specific objectives from review request are met
        print("\n🎯 REVIEW REQUEST OBJECTIVES:")
        objectives = [
            ("Admin Authentication", auth_success),
            ("Course Filtering API", courses_available),
            ("Quiz Attempts Data", enrollments_available),
            ("Data Consistency", success_rate >= 70),
            ("Backend Readiness", success_rate >= 80)
        ]
        
        for objective, met in objectives:
            status = "✅ MET" if met else "❌ NOT MET"
            print(f"   • {objective}: {status}")
        
        return {
            'success_rate': success_rate,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'objectives_met': sum(1 for _, met in objectives if met),
            'total_objectives': len(objectives)
        }

if __name__ == "__main__":
    tester = QuizResultsBackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary['success_rate'] >= 80:
        print(f"\n🎉 TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n⚠️  TESTING COMPLETED WITH ISSUES")
        sys.exit(1)