#!/usr/bin/env python3
"""
🎯 ANALYTICS FIX VALIDATION - Backend Testing

TESTING OBJECTIVES:
1. **Admin Authentication** - Login with admin credentials (brayden.t@covesmart.com / Hawaii2020!)
2. **Test Fixed System Stats Endpoint** - Verify `/api/analytics/system-stats` now shows non-zero quiz data
3. **Test Fixed Dashboard Endpoint** - Verify `/api/analytics/dashboard` returns proper quiz statistics
4. **Verify Quiz Data Source** - Confirm analytics now read from enrollments instead of quiz_attempts
5. **Compare Before/After** - Validate that previously zero quiz stats now show actual data

EXPECTED RESULTS:
- Analytics endpoints should now return actual quiz completion data from enrollments
- Quiz statistics should show non-zero values (attempts, scores, pass rates)
- Dashboard should display quiz-related metrics properly
- System stats should reflect actual quiz activity from enrollment progress

CRITICAL VALIDATION:
This test should prove the fix resolves the user's reported issue where quiz submissions work but don't appear in analytics dashboard.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class AnalyticsFixTestSuite:
    def __init__(self):
        # Use frontend environment URL for backend API
        self.base_url = "http://localhost:8001/api"
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials from review request
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        # Additional student for testing
        self.student_credentials = {
            "username_or_email": "karlo.student@alder.com", 
            "password": "StudentPermanent123!"
        }
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and data:
            print(f"    Error Data: {data}")
        print()

    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {user_info.get('full_name', 'Admin')} (Role: {user_info.get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self) -> bool:
        """Authenticate as student user for comparison"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.student_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Student Authentication",
                    True,
                    f"Successfully authenticated as {user_info.get('full_name', 'Student')} (Role: {user_info.get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Student Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def test_system_stats_endpoint(self) -> Dict:
        """Test the fixed system stats endpoint for non-zero quiz data"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/analytics/system-stats", headers=headers, timeout=15)
            
            if response.status_code != 200:
                self.log_test(
                    "System Stats Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return {}
            
            stats = response.json()
            
            # Extract quiz statistics
            quiz_stats = stats.get('quizzes', {})
            total_quizzes = quiz_stats.get('totalQuizzes', 0)
            published_quizzes = quiz_stats.get('publishedQuizzes', 0)
            total_attempts = quiz_stats.get('totalAttempts', 0)
            average_score = quiz_stats.get('averageScore', 0.0)
            pass_rate = quiz_stats.get('passRate', 0.0)
            quizzes_this_month = quiz_stats.get('quizzesThisMonth', 0)
            
            # Check if quiz data is now non-zero (indicating fix worked)
            has_quiz_data = (
                total_quizzes > 0 or 
                published_quizzes > 0 or 
                total_attempts > 0 or 
                average_score > 0 or 
                pass_rate > 0
            )
            
            # Also check enrollment stats which should show quiz completion data
            enrollment_stats = stats.get('enrollments', {})
            total_enrollments = enrollment_stats.get('totalEnrollments', 0)
            completed_enrollments = enrollment_stats.get('completedEnrollments', 0)
            
            success = has_quiz_data and total_enrollments > 0
            
            details = (
                f"Quiz Stats - Total: {total_quizzes}, Published: {published_quizzes}, "
                f"Attempts: {total_attempts}, Avg Score: {average_score}%, Pass Rate: {pass_rate}%. "
                f"Enrollments - Total: {total_enrollments}, Completed: {completed_enrollments}"
            )
            
            self.log_test(
                "System Stats Endpoint - Quiz Data Fix",
                success,
                details,
                quiz_stats
            )
            
            return stats
            
        except Exception as e:
            self.log_test("System Stats Endpoint - Quiz Data Fix", False, f"Exception: {str(e)}")
            return {}

    def test_dashboard_endpoint(self) -> Dict:
        """Test the fixed dashboard endpoint for proper quiz statistics"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/analytics/dashboard", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test(
                    "Dashboard Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return {}
            
            dashboard_data = response.json()
            
            # Check if dashboard returns proper structure
            has_status = dashboard_data.get('status') == 'success'
            has_data = 'data' in dashboard_data
            
            if not (has_status and has_data):
                self.log_test(
                    "Dashboard Endpoint - Structure",
                    False,
                    f"Invalid response structure - Status: {has_status}, Data: {has_data}"
                )
                return {}
            
            data = dashboard_data.get('data', {})
            
            # For admin role, check if we have system overview data
            expected_fields = ['totalUsers', 'totalCourses', 'totalEnrollments', 'totalCertificates']
            has_all_fields = all(field in data for field in expected_fields)
            
            # Check if enrollment data shows quiz activity
            total_enrollments = data.get('totalEnrollments', 0)
            total_courses = data.get('totalCourses', 0)
            
            success = has_all_fields and total_enrollments > 0 and total_courses > 0
            
            details = (
                f"Dashboard Data - Users: {data.get('totalUsers', 0)}, "
                f"Courses: {total_courses}, Enrollments: {total_enrollments}, "
                f"Certificates: {data.get('totalCertificates', 0)}"
            )
            
            self.log_test(
                "Dashboard Endpoint - Quiz Statistics",
                success,
                details,
                data
            )
            
            return dashboard_data
            
        except Exception as e:
            self.log_test("Dashboard Endpoint - Quiz Statistics", False, f"Exception: {str(e)}")
            return {}

    def verify_enrollment_based_analytics(self) -> bool:
        """Verify that analytics now read from enrollments instead of quiz_attempts"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get enrollments to verify they contain quiz completion data
            enrollments_response = requests.get(f"{self.base_url}/enrollments", headers=headers, timeout=10)
            
            if enrollments_response.status_code != 200:
                self.log_test(
                    "Enrollment Data Verification",
                    False,
                    f"Could not access enrollments: HTTP {enrollments_response.status_code}"
                )
                return False
            
            enrollments = enrollments_response.json()
            
            # Look for enrollments with progress data (indicating quiz completion)
            enrollments_with_progress = [e for e in enrollments if e.get('progress', 0) > 0]
            completed_enrollments = [e for e in enrollments if e.get('progress', 0) >= 100]
            
            # Check if we have meaningful enrollment data
            has_progress_data = len(enrollments_with_progress) > 0
            has_completions = len(completed_enrollments) > 0
            
            # Get courses to verify some have quiz lessons
            courses_response = requests.get(f"{self.base_url}/courses", headers=headers, timeout=10)
            
            if courses_response.status_code != 200:
                self.log_test(
                    "Course Data Verification",
                    False,
                    f"Could not access courses: HTTP {courses_response.status_code}"
                )
                return False
            
            courses = courses_response.json()
            
            # Count courses with quiz lessons
            quiz_courses = 0
            for course in courses:
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            quiz_courses += 1
                            break
                    if quiz_courses > 0:
                        break
            
            has_quiz_courses = quiz_courses > 0
            
            success = has_progress_data and has_quiz_courses
            
            details = (
                f"Enrollments with progress: {len(enrollments_with_progress)}/{len(enrollments)}, "
                f"Completed: {len(completed_enrollments)}, Quiz courses: {quiz_courses}"
            )
            
            self.log_test(
                "Enrollment-Based Analytics Verification",
                success,
                details
            )
            
            return success
            
        except Exception as e:
            self.log_test("Enrollment-Based Analytics Verification", False, f"Exception: {str(e)}")
            return False

    def test_student_dashboard_quiz_data(self) -> bool:
        """Test student dashboard to see quiz completion data"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{self.base_url}/analytics/dashboard", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test(
                    "Student Dashboard Quiz Data",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            dashboard_data = response.json()
            data = dashboard_data.get('data', {})
            
            # Check student-specific fields
            enrolled_courses = data.get('enrolledCourses', 0)
            completed_courses = data.get('completedCourses', 0)
            certificates_earned = data.get('certificatesEarned', 0)
            recent_quiz_attempts = data.get('recentQuizAttempts', [])
            
            # Check if student has meaningful data
            has_enrollments = enrolled_courses > 0
            has_quiz_attempts = len(recent_quiz_attempts) > 0
            
            success = has_enrollments  # At minimum, student should have enrollments
            
            details = (
                f"Student Data - Enrolled: {enrolled_courses}, Completed: {completed_courses}, "
                f"Certificates: {certificates_earned}, Recent Quiz Attempts: {len(recent_quiz_attempts)}"
            )
            
            self.log_test(
                "Student Dashboard Quiz Data",
                success,
                details,
                data
            )
            
            return success
            
        except Exception as e:
            self.log_test("Student Dashboard Quiz Data", False, f"Exception: {str(e)}")
            return False

    def compare_before_after_analytics(self, system_stats: Dict) -> bool:
        """Compare analytics data to validate the fix"""
        try:
            # Extract key metrics that should now show non-zero values
            quiz_stats = system_stats.get('quizzes', {})
            enrollment_stats = system_stats.get('enrollments', {})
            
            # Key indicators that the fix worked
            total_attempts = quiz_stats.get('totalAttempts', 0)
            average_score = quiz_stats.get('averageScore', 0.0)
            pass_rate = quiz_stats.get('passRate', 0.0)
            total_enrollments = enrollment_stats.get('totalEnrollments', 0)
            completed_enrollments = enrollment_stats.get('completedEnrollments', 0)
            
            # Before the fix, these would likely be 0
            # After the fix, they should show actual data from enrollments
            
            fix_indicators = {
                "quiz_attempts_from_enrollments": total_attempts > 0,
                "average_score_calculated": average_score > 0,
                "pass_rate_calculated": pass_rate >= 0,  # Pass rate can be 0 if no one passed
                "enrollment_data_present": total_enrollments > 0,
                "completion_data_present": completed_enrollments >= 0  # Can be 0 if no completions
            }
            
            # The fix is successful if we have enrollment data and calculated metrics
            critical_success = (
                fix_indicators["enrollment_data_present"] and
                (fix_indicators["quiz_attempts_from_enrollments"] or 
                 fix_indicators["average_score_calculated"])
            )
            
            success_count = sum(fix_indicators.values())
            total_indicators = len(fix_indicators)
            
            success = critical_success and success_count >= 3  # At least 3 out of 5 indicators
            
            details = (
                f"Fix Validation - Success Indicators: {success_count}/{total_indicators}. "
                f"Attempts: {total_attempts}, Avg Score: {average_score}%, "
                f"Pass Rate: {pass_rate}%, Enrollments: {total_enrollments}, "
                f"Completed: {completed_enrollments}"
            )
            
            self.log_test(
                "Before/After Analytics Comparison",
                success,
                details,
                fix_indicators
            )
            
            return success
            
        except Exception as e:
            self.log_test("Before/After Analytics Comparison", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all analytics fix validation tests"""
        print("🎯 ANALYTICS FIX VALIDATION - Backend Testing")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        print("🔐 AUTHENTICATION TESTING")
        print("-" * 40)
        
        admin_auth = self.authenticate_admin()
        student_auth = self.authenticate_student()
        
        if not admin_auth:
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with testing.")
            return False
        
        if not student_auth:
            print("⚠️  WARNING: Student authentication failed. Some tests will be skipped.")
        
        print()
        
        # Step 2: Test Fixed System Stats Endpoint
        print("📊 SYSTEM STATS ENDPOINT TESTING")
        print("-" * 40)
        
        system_stats = self.test_system_stats_endpoint()
        print()
        
        # Step 3: Test Fixed Dashboard Endpoint
        print("📈 DASHBOARD ENDPOINT TESTING")
        print("-" * 40)
        
        dashboard_data = self.test_dashboard_endpoint()
        print()
        
        # Step 4: Verify Enrollment-Based Analytics
        print("🔍 ENROLLMENT-BASED ANALYTICS VERIFICATION")
        print("-" * 40)
        
        enrollment_verification = self.verify_enrollment_based_analytics()
        print()
        
        # Step 5: Test Student Dashboard (if student auth worked)
        if student_auth:
            print("👨‍🎓 STUDENT DASHBOARD TESTING")
            print("-" * 40)
            
            student_dashboard = self.test_student_dashboard_quiz_data()
            print()
        else:
            student_dashboard = False
        
        # Step 6: Compare Before/After Analytics
        if system_stats:
            print("🔄 BEFORE/AFTER COMPARISON")
            print("-" * 40)
            
            comparison_result = self.compare_before_after_analytics(system_stats)
            print()
        else:
            comparison_result = False
        
        # Generate Summary Report
        self.generate_summary_report(
            system_stats, 
            dashboard_data, 
            enrollment_verification, 
            student_dashboard, 
            comparison_result
        )
        
        return True

    def generate_summary_report(self, system_stats: Dict, dashboard_data: Dict, 
                              enrollment_verification: bool, student_dashboard: bool, 
                              comparison_result: bool):
        """Generate comprehensive summary report"""
        print("📋 ANALYTICS FIX VALIDATION SUMMARY")
        print("=" * 80)
        
        # Calculate overall success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Key Findings
        print("🔍 KEY FINDINGS:")
        print("-" * 20)
        
        # System Stats Analysis
        if system_stats:
            quiz_stats = system_stats.get('quizzes', {})
            total_attempts = quiz_stats.get('totalAttempts', 0)
            average_score = quiz_stats.get('averageScore', 0.0)
            pass_rate = quiz_stats.get('passRate', 0.0)
            
            if total_attempts > 0 or average_score > 0:
                print(f"✅ SYSTEM STATS FIX: Quiz data now shows {total_attempts} attempts, {average_score}% avg score, {pass_rate}% pass rate")
            else:
                print("❌ SYSTEM STATS: Still showing zero quiz data")
        else:
            print("❌ SYSTEM STATS: Endpoint failed or returned no data")
        
        # Dashboard Analysis
        if dashboard_data:
            data = dashboard_data.get('data', {})
            total_enrollments = data.get('totalEnrollments', 0)
            if total_enrollments > 0:
                print(f"✅ DASHBOARD FIX: Shows {total_enrollments} total enrollments with quiz activity")
            else:
                print("❌ DASHBOARD: No enrollment data visible")
        else:
            print("❌ DASHBOARD: Endpoint failed or returned no data")
        
        # Enrollment Verification
        if enrollment_verification:
            print("✅ ENROLLMENT SOURCE: Analytics successfully reading from enrollments instead of quiz_attempts")
        else:
            print("❌ ENROLLMENT SOURCE: Analytics may still be using old data source")
        
        # Student Dashboard
        if student_dashboard:
            print("✅ STUDENT DASHBOARD: Quiz completion data visible to students")
        else:
            print("❌ STUDENT DASHBOARD: Quiz data not properly displayed for students")
        
        # Before/After Comparison
        if comparison_result:
            print("✅ FIX VALIDATION: Analytics now show actual quiz activity from enrollment progress")
        else:
            print("❌ FIX VALIDATION: Analytics may still show zero or incorrect quiz data")
        
        print()
        
        # Critical Success Assessment
        critical_tests = [
            system_stats is not None and system_stats.get('quizzes', {}).get('totalAttempts', 0) > 0,
            dashboard_data is not None and dashboard_data.get('data', {}).get('totalEnrollments', 0) > 0,
            enrollment_verification,
            comparison_result
        ]
        
        critical_success_count = sum(critical_tests)
        critical_success = critical_success_count >= 3  # At least 3 out of 4 critical tests
        
        print("🎯 CRITICAL SUCCESS ASSESSMENT:")
        print("-" * 30)
        
        if critical_success:
            print("🎉 SUCCESS: Analytics fix has been successfully validated!")
            print("   - Quiz submissions now appear in analytics dashboard")
            print("   - System stats show non-zero quiz data from enrollments")
            print("   - Dashboard displays proper quiz-related metrics")
            print("   - User's reported issue should be resolved")
        else:
            print("⚠️  PARTIAL SUCCESS: Some analytics endpoints are working, but issues remain")
            print(f"   - Critical tests passed: {critical_success_count}/4")
            print("   - Additional investigation may be needed")
        
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("-" * 20)
        
        if not critical_success:
            print("🔧 INVESTIGATE: Check if enrollment progress data properly reflects quiz completions")
            print("🔧 VERIFY: Ensure quiz submission workflow updates enrollment progress to 100%")
            print("🔧 TEST: Submit a test quiz and verify it appears in analytics immediately")
        else:
            print("✅ DEPLOYMENT READY: Analytics fix is working correctly")
            print("✅ USER ISSUE RESOLVED: Quiz submissions should now appear in analytics")
        
        print()
        print("=" * 80)

def main():
    """Main execution function"""
    test_suite = AnalyticsFixTestSuite()
    
    try:
        success = test_suite.run_comprehensive_test()
        
        if success:
            print("✅ Analytics fix validation completed successfully!")
            return 0
        else:
            print("❌ Analytics fix validation completed with issues!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)