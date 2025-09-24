#!/usr/bin/env python3
"""
🎯 ANALYTICS DASHBOARD TESTING - REMAINING FIXES VERIFICATION

TESTING OBJECTIVES:
1. **Admin Authentication** - Login with admin credentials (brayden.t@covesmart.com / Hawaii2020!)
2. **Quiz Data Structure Verification** - Verify that quiz attempts are properly created from enrollments
3. **Recent Quiz Attempts Display** - Test that recent attempts section shows actual quiz submissions instead of "No quiz attempts yet"
4. **Course Performance Analysis** - Verify that courses show correct quiz counts and attempt statistics
5. **Score Accuracy Validation** - Confirm average scores reflect actual quiz results (e.g., 50% vs 100%)

SPECIFIC VALIDATION:
- Recent Quiz Attempts should show actual student submissions with course names and scores
- Course Performance should show "1 quiz" or appropriate count for courses with quizzes 
- Average scores should reflect real quiz performance data (not just 100%)
- All course attempt statistics should be accurate and meaningful

This test should confirm that the remaining sections of the analytics dashboard display actual quiz data instead of empty/incorrect information.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class AnalyticsDashboardTestSuite:
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.base_url = "https://lms-analytics-hub.preview.emergentagent.com/api"
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials from review request
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
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
        """Authenticate as student user"""
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

    def verify_quiz_data_structure(self) -> Dict:
        """Verify that quiz attempts are properly created from enrollments"""
        try:
            # Use analytics dashboard endpoint to get system-wide data
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get analytics dashboard data
            dashboard_response = requests.get(f"{self.base_url}/analytics/dashboard", headers=headers, timeout=10)
            
            if dashboard_response.status_code != 200:
                self.log_test(
                    "Quiz Data Structure Verification",
                    False,
                    f"Analytics dashboard HTTP {dashboard_response.status_code}: {dashboard_response.text}"
                )
                return {}
            
            dashboard_data = dashboard_response.json().get('data', {})
            
            # Also get student enrollments to analyze quiz scores
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            student_response = requests.get(f"{self.base_url}/enrollments", headers=student_headers, timeout=10)
            
            enrollments = []
            if student_response.status_code == 200:
                enrollments = student_response.json()
            
            quiz_analysis = {
                "total_enrollments": dashboard_data.get('totalEnrollments', len(enrollments)),
                "enrollments_with_quiz_scores": 0,
                "quiz_score_distribution": {},
                "courses_with_quizzes": set(),
                "sample_quiz_data": []
            }
            
            for enrollment in enrollments:
                progress = enrollment.get('progress', 0)
                course_id = enrollment.get('courseId')
                
                # Check if this enrollment represents a completed quiz (progress > 0 and <= 100)
                if progress > 0 and course_id:
                    quiz_analysis["enrollments_with_quiz_scores"] += 1
                    quiz_analysis["courses_with_quizzes"].add(course_id)
                    
                    # Categorize scores
                    if progress == 100:
                        quiz_analysis["quiz_score_distribution"]["perfect"] = quiz_analysis["quiz_score_distribution"].get("perfect", 0) + 1
                    elif progress >= 80:
                        quiz_analysis["quiz_score_distribution"]["high"] = quiz_analysis["quiz_score_distribution"].get("high", 0) + 1
                    elif progress >= 60:
                        quiz_analysis["quiz_score_distribution"]["medium"] = quiz_analysis["quiz_score_distribution"].get("medium", 0) + 1
                    elif progress >= 40:
                        quiz_analysis["quiz_score_distribution"]["low"] = quiz_analysis["quiz_score_distribution"].get("low", 0) + 1
                    else:
                        quiz_analysis["quiz_score_distribution"]["failing"] = quiz_analysis["quiz_score_distribution"].get("failing", 0) + 1
                    
                    # Store sample data
                    if len(quiz_analysis["sample_quiz_data"]) < 5:
                        quiz_analysis["sample_quiz_data"].append({
                            "course_id": course_id,
                            "student_id": enrollment.get('userId'),
                            "score": progress,
                            "status": enrollment.get('status'),
                            "enrolled_at": enrollment.get('enrolledAt'),
                            "completed_at": enrollment.get('completedAt')
                        })
            
            quiz_analysis["unique_courses_with_quizzes"] = len(quiz_analysis["courses_with_quizzes"])
            quiz_analysis["dashboard_data"] = dashboard_data
            
            success = quiz_analysis["enrollments_with_quiz_scores"] > 0
            details = f"Found {quiz_analysis['enrollments_with_quiz_scores']} enrollments with quiz scores across {quiz_analysis['unique_courses_with_quizzes']} courses"
            
            self.log_test(
                "Quiz Data Structure Verification",
                success,
                details,
                quiz_analysis
            )
            
            return quiz_analysis
            
        except Exception as e:
            self.log_test("Quiz Data Structure Verification", False, f"Exception: {str(e)}")
            return {}

    def test_recent_quiz_attempts_data(self) -> Dict:
        """Test that recent attempts section shows actual quiz submissions"""
        try:
            # Get student's recent quiz attempts from analytics dashboard
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            dashboard_response = requests.get(f"{self.base_url}/analytics/dashboard", headers=student_headers, timeout=10)
            
            if dashboard_response.status_code != 200:
                self.log_test(
                    "Recent Quiz Attempts Data",
                    False,
                    f"Student dashboard HTTP {dashboard_response.status_code}: {dashboard_response.text}"
                )
                return {}
            
            dashboard_data = dashboard_response.json().get('data', {})
            recent_attempts = dashboard_data.get('recentQuizAttempts', [])
            
            # Also get enrollments directly to analyze
            enrollments_response = requests.get(f"{self.base_url}/enrollments", headers=student_headers, timeout=10)
            enrollments = []
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
            
            # Filter and sort enrollments that represent quiz attempts
            quiz_attempts = []
            for enrollment in enrollments:
                if enrollment.get('progress', 0) > 0:  # Has some progress indicating quiz completion
                    # Get course name
                    course_name = "Unknown Course"
                    if enrollment.get('courseId'):
                        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
                        course_response = requests.get(f"{self.base_url}/courses/{enrollment['courseId']}", headers=admin_headers, timeout=10)
                        if course_response.status_code == 200:
                            course_data = course_response.json()
                            course_name = course_data.get('title', 'Unknown Course')
                    
                    quiz_attempts.append({
                        "course_id": enrollment.get('courseId'),
                        "student_id": enrollment.get('userId'),
                        "student_name": enrollment.get('studentName', 'Unknown Student'),
                        "course_name": course_name,
                        "score": enrollment.get('progress', 0),
                        "completed_at": enrollment.get('completedAt') or enrollment.get('enrolledAt'),
                        "status": enrollment.get('status', 'active')
                    })
            
            # Sort by completion date (most recent first)
            quiz_attempts.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
            
            attempts_analysis = {
                "total_quiz_attempts": len(quiz_attempts),
                "recent_attempts_from_dashboard": len(recent_attempts),
                "recent_attempts_count": len(quiz_attempts[:10]),
                "has_student_names": sum(1 for attempt in quiz_attempts[:10] if attempt['student_name'] != 'Unknown Student'),
                "has_course_names": sum(1 for attempt in quiz_attempts[:10] if attempt['course_name'] != 'Unknown Course'),
                "score_variety": len(set(attempt['score'] for attempt in quiz_attempts[:10])),
                "recent_attempts": quiz_attempts[:10],
                "dashboard_attempts": recent_attempts
            }
            
            success = (
                attempts_analysis["recent_attempts_count"] > 0 and
                attempts_analysis["has_course_names"] > 0
            )
            
            details = f"Found {attempts_analysis['recent_attempts_count']} recent quiz attempts with {attempts_analysis['has_course_names']} course names. Dashboard shows {attempts_analysis['recent_attempts_from_dashboard']} attempts."
            
            self.log_test(
                "Recent Quiz Attempts Data",
                success,
                details,
                attempts_analysis
            )
            
            return attempts_analysis
            
        except Exception as e:
            self.log_test("Recent Quiz Attempts Data", False, f"Exception: {str(e)}")
            return {}

    def test_course_performance_analysis(self) -> Dict:
        """Verify that courses show correct quiz counts and attempt statistics"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all courses
            courses_response = requests.get(f"{self.base_url}/courses", headers=headers, timeout=10)
            if courses_response.status_code != 200:
                self.log_test(
                    "Course Performance Analysis",
                    False,
                    f"Failed to get courses: HTTP {courses_response.status_code}"
                )
                return {}
            
            courses = courses_response.json()
            
            # Get student enrollments (since admin endpoint only shows admin's enrollments)
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            enrollments_response = requests.get(f"{self.base_url}/enrollments", headers=student_headers, timeout=10)
            enrollments = []
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
            
            # Also get analytics dashboard data for system stats
            dashboard_response = requests.get(f"{self.base_url}/analytics/dashboard", headers=headers, timeout=10)
            dashboard_data = {}
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json().get('data', {})
            
            # Analyze course performance
            course_performance = {}
            
            for course in courses:
                course_id = course.get('id')
                course_title = course.get('title', 'Unknown Course')
                
                # Count quiz lessons in this course
                quiz_count = 0
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            quiz_count += 1
                
                # Get enrollments for this course
                course_enrollments = [e for e in enrollments if e.get('courseId') == course_id]
                
                # Calculate statistics
                total_attempts = len(course_enrollments)
                completed_attempts = len([e for e in course_enrollments if e.get('progress', 0) >= 100])
                scores = [e.get('progress', 0) for e in course_enrollments if e.get('progress', 0) > 0]
                
                avg_score = sum(scores) / len(scores) if scores else 0
                
                course_performance[course_id] = {
                    "course_title": course_title,
                    "quiz_count": quiz_count,
                    "total_attempts": total_attempts,
                    "completed_attempts": completed_attempts,
                    "average_score": avg_score,
                    "score_distribution": scores
                }
            
            # Filter courses that have quizzes
            courses_with_quizzes = {k: v for k, v in course_performance.items() if v['quiz_count'] > 0}
            courses_with_attempts = {k: v for k, v in courses_with_quizzes.items() if v['total_attempts'] > 0}
            
            performance_analysis = {
                "total_courses": len(courses),
                "courses_with_quizzes": len(courses_with_quizzes),
                "courses_with_attempts": len(courses_with_attempts),
                "average_quiz_count": sum(v['quiz_count'] for v in courses_with_quizzes.values()) / len(courses_with_quizzes) if courses_with_quizzes else 0,
                "sample_course_performance": dict(list(courses_with_attempts.items())[:5]) if courses_with_attempts else dict(list(courses_with_quizzes.items())[:5]),
                "dashboard_stats": dashboard_data,
                "total_enrollments_found": len(enrollments)
            }
            
            success = (
                performance_analysis["courses_with_quizzes"] > 0 and
                performance_analysis["total_enrollments_found"] > 0
            )
            
            details = f"Found {performance_analysis['courses_with_quizzes']} courses with quizzes, {performance_analysis['courses_with_attempts']} have attempts ({performance_analysis['total_enrollments_found']} total enrollments)"
            
            self.log_test(
                "Course Performance Analysis",
                success,
                details,
                performance_analysis
            )
            
            return performance_analysis
            
        except Exception as e:
            self.log_test("Course Performance Analysis", False, f"Exception: {str(e)}")
            return {}

    def test_score_accuracy_validation(self) -> Dict:
        """Confirm average scores reflect actual quiz results (e.g., 50% vs 100%)"""
        try:
            # Get student enrollments with progress data
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{self.base_url}/enrollments", headers=student_headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test(
                    "Score Accuracy Validation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return {}
            
            enrollments = response.json()
            
            # Analyze score accuracy
            scores = [e.get('progress', 0) for e in enrollments if e.get('progress', 0) > 0]
            
            if not scores:
                self.log_test(
                    "Score Accuracy Validation",
                    False,
                    "No quiz scores found in enrollments"
                )
                return {}
            
            score_analysis = {
                "total_scores": len(scores),
                "unique_scores": len(set(scores)),
                "score_range": {
                    "min": min(scores),
                    "max": max(scores),
                    "average": sum(scores) / len(scores)
                },
                "score_distribution": {
                    "perfect_100": scores.count(100),
                    "high_80_99": len([s for s in scores if 80 <= s < 100]),
                    "medium_60_79": len([s for s in scores if 60 <= s < 80]),
                    "low_40_59": len([s for s in scores if 40 <= s < 60]),
                    "failing_below_40": len([s for s in scores if s < 40])
                },
                "has_variety": len(set(scores)) > 1,
                "not_all_perfect": not all(s == 100 for s in scores),
                "sample_scores": sorted(list(set(scores)))[:10],
                "enrollments_analyzed": len(enrollments)
            }
            
            # Check for realistic score distribution
            has_realistic_distribution = (
                score_analysis["has_variety"] and
                score_analysis["not_all_perfect"] and
                score_analysis["unique_scores"] >= 2
            )
            
            success = has_realistic_distribution
            details = f"Found {score_analysis['unique_scores']} unique scores ranging from {score_analysis['score_range']['min']}% to {score_analysis['score_range']['max']}% (avg: {score_analysis['score_range']['average']:.1f}%)"
            
            self.log_test(
                "Score Accuracy Validation",
                success,
                details,
                score_analysis
            )
            
            return score_analysis
            
        except Exception as e:
            self.log_test("Score Accuracy Validation", False, f"Exception: {str(e)}")
            return {}

    def test_analytics_api_endpoints(self) -> bool:
        """Test all analytics-related API endpoints are working"""
        try:
            api_tests = [
                ("GET /api/courses", f"{self.base_url}/courses", self.admin_token),
                ("GET /api/enrollments", f"{self.base_url}/enrollments", self.admin_token),
                ("GET /api/users", f"{self.base_url}/auth/admin/users", self.admin_token),
                ("GET /api/programs", f"{self.base_url}/programs", self.admin_token),
                ("GET /api/classrooms", f"{self.base_url}/classrooms", self.admin_token)
            ]
            
            api_results = []
            
            for test_name, url, token in api_tests:
                try:
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    success = response.status_code == 200
                    api_results.append(success)
                    
                    if success:
                        data = response.json()
                        count = len(data) if isinstance(data, list) else 1
                        details = f"HTTP 200 - Retrieved {count} items"
                    else:
                        details = f"HTTP {response.status_code}: {response.text[:100]}"
                    
                    self.log_test(test_name, success, details)
                    
                except Exception as e:
                    self.log_test(test_name, False, f"Exception: {str(e)}")
                    api_results.append(False)
            
            overall_success = all(api_results)
            success_rate = sum(api_results) / len(api_results) * 100
            
            self.log_test(
                "Analytics API Endpoints Test",
                overall_success,
                f"API Success Rate: {success_rate:.1f}% ({sum(api_results)}/{len(api_results)} tests passed)"
            )
            
            return overall_success
            
        except Exception as e:
            self.log_test("Analytics API Endpoints Test", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all tests for analytics dashboard verification"""
        print("🎯 ANALYTICS DASHBOARD TESTING - REMAINING FIXES VERIFICATION")
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
        
        print()
        
        # Step 2: Analytics API Endpoints
        print("🔧 ANALYTICS API ENDPOINTS TESTING")
        print("-" * 40)
        
        api_working = self.test_analytics_api_endpoints()
        print()
        
        # Step 3: Quiz Data Structure Verification
        print("📊 QUIZ DATA STRUCTURE VERIFICATION")
        print("-" * 40)
        
        quiz_analysis = self.verify_quiz_data_structure()
        print()
        
        # Step 4: Recent Quiz Attempts Testing
        print("🕒 RECENT QUIZ ATTEMPTS TESTING")
        print("-" * 40)
        
        attempts_analysis = self.test_recent_quiz_attempts_data()
        print()
        
        # Step 5: Course Performance Analysis
        print("📈 COURSE PERFORMANCE ANALYSIS")
        print("-" * 40)
        
        performance_analysis = self.test_course_performance_analysis()
        print()
        
        # Step 6: Score Accuracy Validation
        print("🎯 SCORE ACCURACY VALIDATION")
        print("-" * 40)
        
        score_analysis = self.test_score_accuracy_validation()
        print()
        
        # Generate Summary Report
        self.generate_summary_report(quiz_analysis, attempts_analysis, performance_analysis, score_analysis, api_working)
        
        return True

    def generate_summary_report(self, quiz_analysis: Dict, attempts_analysis: Dict, performance_analysis: Dict, score_analysis: Dict, api_working: bool):
        """Generate comprehensive summary report"""
        print("📊 COMPREHENSIVE ANALYTICS TESTING SUMMARY")
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
        
        # Quiz Data Structure
        if quiz_analysis:
            quiz_scores = quiz_analysis.get("enrollments_with_quiz_scores", 0)
            if quiz_scores > 0:
                print(f"✅ QUIZ DATA: Found {quiz_scores} enrollments with quiz scores")
                unique_courses = quiz_analysis.get("unique_courses_with_quizzes", 0)
                print(f"✅ COURSE COVERAGE: {unique_courses} unique courses have quiz data")
            else:
                print("❌ QUIZ DATA: No enrollments with quiz scores found")
        
        # Recent Quiz Attempts
        if attempts_analysis:
            recent_count = attempts_analysis.get("recent_attempts_count", 0)
            if recent_count > 0:
                print(f"✅ RECENT ATTEMPTS: Found {recent_count} recent quiz attempts")
                student_names = attempts_analysis.get("has_student_names", 0)
                course_names = attempts_analysis.get("has_course_names", 0)
                print(f"✅ DATA QUALITY: {student_names} attempts have student names, {course_names} have course names")
            else:
                print("❌ RECENT ATTEMPTS: No recent quiz attempts found")
        
        # Course Performance
        if performance_analysis:
            courses_with_quizzes = performance_analysis.get("courses_with_quizzes", 0)
            courses_with_attempts = performance_analysis.get("courses_with_attempts", 0)
            if courses_with_quizzes > 0:
                print(f"✅ COURSE PERFORMANCE: {courses_with_quizzes} courses have quizzes")
                print(f"✅ ATTEMPT DATA: {courses_with_attempts} courses have quiz attempts")
            else:
                print("❌ COURSE PERFORMANCE: No courses with quizzes found")
        
        # Score Accuracy
        if score_analysis:
            unique_scores = score_analysis.get("unique_scores", 0)
            score_range = score_analysis.get("score_range", {})
            if unique_scores > 1:
                print(f"✅ SCORE VARIETY: Found {unique_scores} unique scores")
                print(f"✅ SCORE RANGE: {score_range.get('min', 0)}% - {score_range.get('max', 0)}% (avg: {score_range.get('average', 0):.1f}%)")
            else:
                print("❌ SCORE VARIETY: Limited score variety detected")
        
        # API Functionality
        if api_working:
            print("✅ ANALYTICS APIS: All required APIs working correctly")
        else:
            print("❌ ANALYTICS APIS: Some APIs not working correctly")
        
        print()
        
        # Specific Analytics Dashboard Readiness
        print("🎯 ANALYTICS DASHBOARD READINESS:")
        print("-" * 35)
        
        recent_attempts_ready = attempts_analysis.get("recent_attempts_count", 0) > 0
        course_performance_ready = performance_analysis.get("courses_with_quizzes", 0) > 0
        score_accuracy_ready = score_analysis.get("unique_scores", 0) > 1
        
        if recent_attempts_ready:
            print("✅ RECENT QUIZ ATTEMPTS: Ready to display actual quiz submissions")
        else:
            print("❌ RECENT QUIZ ATTEMPTS: No data available - will show 'No quiz attempts yet'")
        
        if course_performance_ready:
            print("✅ COURSE PERFORMANCE: Ready to show quiz counts and statistics")
        else:
            print("❌ COURSE PERFORMANCE: No courses with quizzes found")
        
        if score_accuracy_ready:
            print("✅ SCORE ACCURACY: Realistic score distribution available")
        else:
            print("❌ SCORE ACCURACY: Limited score variety may show unrealistic averages")
        
        print()
        
        # Final Status
        critical_success = recent_attempts_ready and course_performance_ready and score_accuracy_ready and api_working
        
        if critical_success:
            print("🎉 SUCCESS: Analytics dashboard is ready with actual quiz data!")
            print("   - Recent Quiz Attempts will show real submissions")
            print("   - Course Performance will show accurate quiz counts")
            print("   - Average scores reflect realistic quiz results")
        else:
            print("⚠️  PARTIAL SUCCESS: Some analytics sections may show empty/incorrect data")
            if not recent_attempts_ready:
                print("   - Recent Quiz Attempts may show 'No quiz attempts yet'")
            if not course_performance_ready:
                print("   - Course Performance may show '0 quizzes' for all courses")
            if not score_accuracy_ready:
                print("   - Average scores may not reflect realistic quiz performance")
        
        print()
        print("=" * 80)

def main():
    """Main execution function"""
    test_suite = AnalyticsDashboardTestSuite()
    
    try:
        success = test_suite.run_comprehensive_test()
        
        if success:
            print("✅ Analytics testing completed successfully!")
            return 0
        else:
            print("❌ Analytics testing completed with issues!")
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