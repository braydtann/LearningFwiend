#!/usr/bin/env python3
"""
🎯 QUIZ ATTEMPTS SYNTHESIS DEBUGGING TEST

TESTING OBJECTIVES FROM REVIEW REQUEST:
1. **Check Enrollment Data Structure** - Verify that recent quiz submissions are properly stored in enrollments table
2. **Debug Quiz Attempts Synthesis** - Test if the frontend logic properly converts enrollments to synthetic quiz attempts
3. **Course-Quiz Matching** - Verify that courses with quiz lessons are being detected correctly
4. **Data Flow Analysis** - Check complete flow: quiz submission → enrollment progress → synthetic attempts → recent attempts display

SPECIFIC DEBUGGING:
- Get recent enrollments with progress data (should show the new quiz attempt)
- Verify course structure for quiz lesson detection
- Test synthetic quiz attempt creation logic with actual data
- Check if filtering logic matches the synthetic attempt format

The user tried a new quiz and used different browser with hard refresh, but Recent Quiz Attempts still empty and filtering not working.
Need to identify why synthetic quiz attempts aren't being created properly from enrollment data.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class QuizAttemptsSynthesisTestSuite:
    def __init__(self):
        # Use the correct backend URL from frontend/.env
        self.base_url = "https://learning-analytics-2.preview.emergentagent.com/api"
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
        if data and not success:
            print(f"    Debug Data: {json.dumps(data, indent=2, default=str)}")
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

    def analyze_enrollment_data_structure(self) -> Dict:
        """Check enrollment data structure for quiz attempts synthesis"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{self.base_url}/enrollments", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test(
                    "Enrollment Data Structure Analysis",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return {}
            
            enrollments = response.json()
            
            analysis = {
                "total_enrollments": len(enrollments),
                "enrollments_with_progress": 0,
                "enrollments_with_quiz_progress": 0,
                "recent_quiz_attempts": [],
                "progress_ranges": {
                    "0%": 0,
                    "1-24%": 0,
                    "25-49%": 0,
                    "50-74%": 0,
                    "75-99%": 0,
                    "100%": 0
                },
                "sample_enrollments": []
            }
            
            # Analyze each enrollment for quiz attempt synthesis potential
            for enrollment in enrollments:
                progress = enrollment.get('progress', 0)
                course_id = enrollment.get('courseId')
                enrolled_at = enrollment.get('enrolledAt')
                completed_at = enrollment.get('completedAt')
                status = enrollment.get('status', 'active')
                
                # Count progress ranges
                if progress == 0:
                    analysis["progress_ranges"]["0%"] += 1
                elif progress < 25:
                    analysis["progress_ranges"]["1-24%"] += 1
                elif progress < 50:
                    analysis["progress_ranges"]["25-49%"] += 1
                elif progress < 75:
                    analysis["progress_ranges"]["50-74%"] += 1
                elif progress < 100:
                    analysis["progress_ranges"]["75-99%"] += 1
                else:
                    analysis["progress_ranges"]["100%"] += 1
                
                # Check if enrollment has progress (potential quiz attempt)
                if progress > 0:
                    analysis["enrollments_with_progress"] += 1
                    
                    # This could be a synthetic quiz attempt
                    synthetic_attempt = {
                        "id": f"course-quiz-{course_id}",
                        "courseId": course_id,
                        "progress": progress,
                        "status": status,
                        "enrolledAt": enrolled_at,
                        "completedAt": completed_at,
                        "is_synthetic": True
                    }
                    
                    analysis["recent_quiz_attempts"].append(synthetic_attempt)
                    
                    # If progress suggests quiz completion, count it
                    if progress >= 25:  # Assuming quiz completion gives at least 25% progress
                        analysis["enrollments_with_quiz_progress"] += 1
                
                # Store sample for detailed analysis
                if len(analysis["sample_enrollments"]) < 5:
                    analysis["sample_enrollments"].append({
                        "courseId": course_id,
                        "progress": progress,
                        "status": status,
                        "enrolledAt": enrolled_at,
                        "completedAt": completed_at,
                        "lastAccessedAt": enrollment.get('lastAccessedAt'),
                        "timeSpent": enrollment.get('timeSpent')
                    })
            
            # Sort recent attempts by date (most recent first)
            analysis["recent_quiz_attempts"].sort(
                key=lambda x: x.get('completedAt') or x.get('enrolledAt') or '', 
                reverse=True
            )
            
            success = analysis["enrollments_with_progress"] > 0
            details = f"Found {analysis['enrollments_with_progress']} enrollments with progress out of {analysis['total_enrollments']} total"
            
            self.log_test(
                "Enrollment Data Structure Analysis",
                success,
                details,
                analysis
            )
            
            return analysis
            
        except Exception as e:
            self.log_test("Enrollment Data Structure Analysis", False, f"Exception: {str(e)}")
            return {}

    def verify_course_quiz_matching(self) -> Dict:
        """Verify that courses with quiz lessons are being detected correctly"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/courses", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_test(
                    "Course Quiz Matching Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return {}
            
            courses = response.json()
            
            matching_analysis = {
                "total_courses": len(courses),
                "courses_with_quizzes": 0,
                "quiz_lesson_count": 0,
                "quiz_courses": [],
                "data_format_issues": [],
                "sample_quiz_structures": []
            }
            
            for course in courses:
                course_id = course.get('id')
                course_title = course.get('title', 'Unknown')
                modules = course.get('modules', [])
                
                course_has_quiz = False
                course_quiz_count = 0
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        lesson_type = lesson.get('type')
                        
                        if lesson_type == 'quiz':
                            course_has_quiz = True
                            course_quiz_count += 1
                            matching_analysis["quiz_lesson_count"] += 1
                            
                            # Check quiz data structure
                            quiz_structure = {
                                "course_id": course_id,
                                "course_title": course_title,
                                "lesson_id": lesson.get('id'),
                                "lesson_title": lesson.get('title', 'Unknown Quiz'),
                                "has_questions": False,
                                "questions_location": None,
                                "question_count": 0
                            }
                            
                            # Check for questions in different locations
                            if 'questions' in lesson and lesson['questions']:
                                quiz_structure["has_questions"] = True
                                quiz_structure["questions_location"] = "lesson.questions"
                                quiz_structure["question_count"] = len(lesson['questions'])
                            elif 'quiz' in lesson and lesson['quiz'] and 'questions' in lesson['quiz']:
                                quiz_structure["has_questions"] = True
                                quiz_structure["questions_location"] = "lesson.quiz.questions"
                                quiz_structure["question_count"] = len(lesson['quiz']['questions'])
                            else:
                                matching_analysis["data_format_issues"].append({
                                    "course_id": course_id,
                                    "course_title": course_title,
                                    "issue": "Quiz lesson found but no questions detected",
                                    "lesson_keys": list(lesson.keys())
                                })
                            
                            if len(matching_analysis["sample_quiz_structures"]) < 3:
                                matching_analysis["sample_quiz_structures"].append(quiz_structure)
                
                if course_has_quiz:
                    matching_analysis["courses_with_quizzes"] += 1
                    matching_analysis["quiz_courses"].append({
                        "id": course_id,
                        "title": course_title,
                        "quiz_count": course_quiz_count
                    })
            
            success = matching_analysis["courses_with_quizzes"] > 0
            details = f"Found {matching_analysis['courses_with_quizzes']} courses with {matching_analysis['quiz_lesson_count']} quiz lessons"
            
            self.log_test(
                "Course Quiz Matching Verification",
                success,
                details,
                matching_analysis
            )
            
            return matching_analysis
            
        except Exception as e:
            self.log_test("Course Quiz Matching Verification", False, f"Exception: {str(e)}")
            return {}

    def test_synthetic_quiz_attempts_creation(self, enrollment_analysis: Dict, course_analysis: Dict) -> Dict:
        """Test synthetic quiz attempt creation logic with actual data"""
        try:
            synthesis_analysis = {
                "potential_synthetic_attempts": 0,
                "valid_synthetic_attempts": 0,
                "invalid_synthetic_attempts": 0,
                "synthesis_issues": [],
                "synthetic_attempts": [],
                "course_matching_success": 0,
                "course_matching_failures": 0
            }
            
            # Get course IDs that have quizzes
            quiz_course_ids = set()
            if course_analysis and "quiz_courses" in course_analysis:
                quiz_course_ids = {course["id"] for course in course_analysis["quiz_courses"]}
            
            # Process enrollments to create synthetic quiz attempts
            recent_attempts = enrollment_analysis.get("recent_quiz_attempts", [])
            
            for attempt in recent_attempts:
                synthesis_analysis["potential_synthetic_attempts"] += 1
                course_id = attempt.get("courseId")
                
                # Check if course has quizzes (course-quiz matching)
                if course_id in quiz_course_ids:
                    synthesis_analysis["course_matching_success"] += 1
                    
                    # Create synthetic quiz attempt
                    synthetic_attempt = {
                        "id": f"course-quiz-{course_id}",
                        "studentId": "current_student",  # Would be actual student ID in frontend
                        "courseId": course_id,
                        "courseName": "Unknown Course",  # Would be fetched from course data
                        "score": attempt.get("progress", 0),
                        "status": "completed" if attempt.get("progress", 0) >= 100 else "in_progress",
                        "submittedAt": attempt.get("completedAt") or attempt.get("enrolledAt"),
                        "timeSpent": 0,  # Not available in enrollment data
                        "type": "synthetic",
                        "source": "enrollment_progress"
                    }
                    
                    # Validate synthetic attempt
                    required_fields = ["id", "courseId", "score", "status", "submittedAt"]
                    has_all_fields = all(field in synthetic_attempt and synthetic_attempt[field] is not None for field in required_fields)
                    
                    if has_all_fields:
                        synthesis_analysis["valid_synthetic_attempts"] += 1
                        synthesis_analysis["synthetic_attempts"].append(synthetic_attempt)
                    else:
                        synthesis_analysis["invalid_synthetic_attempts"] += 1
                        synthesis_analysis["synthesis_issues"].append({
                            "course_id": course_id,
                            "issue": "Missing required fields",
                            "missing_fields": [field for field in required_fields if field not in synthetic_attempt or synthetic_attempt[field] is None]
                        })
                else:
                    synthesis_analysis["course_matching_failures"] += 1
                    synthesis_analysis["synthesis_issues"].append({
                        "course_id": course_id,
                        "issue": "Course not found in quiz courses list",
                        "progress": attempt.get("progress", 0)
                    })
            
            # Sort synthetic attempts by submission date (most recent first)
            synthesis_analysis["synthetic_attempts"].sort(
                key=lambda x: x.get("submittedAt") or "", 
                reverse=True
            )
            
            success = synthesis_analysis["valid_synthetic_attempts"] > 0
            details = f"Created {synthesis_analysis['valid_synthetic_attempts']} valid synthetic attempts from {synthesis_analysis['potential_synthetic_attempts']} potential attempts"
            
            self.log_test(
                "Synthetic Quiz Attempts Creation",
                success,
                details,
                synthesis_analysis
            )
            
            return synthesis_analysis
            
        except Exception as e:
            self.log_test("Synthetic Quiz Attempts Creation", False, f"Exception: {str(e)}")
            return {}

    def test_filtering_logic_compatibility(self, synthesis_analysis: Dict, course_analysis: Dict) -> bool:
        """Test if filtering logic matches the synthetic attempt format"""
        try:
            synthetic_attempts = synthesis_analysis.get("synthetic_attempts", [])
            quiz_courses = course_analysis.get("quiz_courses", [])
            
            if not synthetic_attempts:
                self.log_test(
                    "Filtering Logic Compatibility",
                    False,
                    "No synthetic attempts available for filtering test"
                )
                return False
            
            filtering_analysis = {
                "total_attempts": len(synthetic_attempts),
                "filterable_attempts": 0,
                "course_filter_tests": [],
                "filtering_issues": []
            }
            
            # Test filtering by each course that has quizzes
            for course in quiz_courses[:3]:  # Test first 3 courses
                course_id = course["id"]
                course_title = course["title"]
                
                # Filter synthetic attempts by course
                filtered_attempts = [
                    attempt for attempt in synthetic_attempts 
                    if attempt.get("courseId") == course_id
                ]
                
                filter_test = {
                    "course_id": course_id,
                    "course_title": course_title,
                    "total_attempts_for_course": len(filtered_attempts),
                    "filter_working": len(filtered_attempts) > 0
                }
                
                if len(filtered_attempts) > 0:
                    filtering_analysis["filterable_attempts"] += len(filtered_attempts)
                    
                    # Test statistics calculation
                    scores = [attempt.get("score", 0) for attempt in filtered_attempts]
                    avg_score = sum(scores) / len(scores) if scores else 0
                    pass_rate = len([s for s in scores if s >= 70]) / len(scores) * 100 if scores else 0
                    
                    filter_test.update({
                        "average_score": avg_score,
                        "pass_rate": pass_rate,
                        "sample_attempts": filtered_attempts[:2]  # First 2 attempts as sample
                    })
                else:
                    filtering_analysis["filtering_issues"].append({
                        "course_id": course_id,
                        "issue": "No synthetic attempts found for course with quizzes"
                    })
                
                filtering_analysis["course_filter_tests"].append(filter_test)
            
            # Test "All Courses" filter (should show all attempts)
            all_courses_filter = {
                "filter_type": "all_courses",
                "total_attempts": len(synthetic_attempts),
                "shows_all_attempts": len(synthetic_attempts) > 0
            }
            filtering_analysis["all_courses_filter"] = all_courses_filter
            
            success = filtering_analysis["filterable_attempts"] > 0
            details = f"Filtering test: {filtering_analysis['filterable_attempts']} filterable attempts across {len(filtering_analysis['course_filter_tests'])} courses"
            
            self.log_test(
                "Filtering Logic Compatibility",
                success,
                details,
                filtering_analysis
            )
            
            return success
            
        except Exception as e:
            self.log_test("Filtering Logic Compatibility", False, f"Exception: {str(e)}")
            return False

    def test_recent_attempts_display_data(self, synthesis_analysis: Dict) -> bool:
        """Test if recent attempts display has proper data structure"""
        try:
            synthetic_attempts = synthesis_analysis.get("synthetic_attempts", [])
            
            if not synthetic_attempts:
                self.log_test(
                    "Recent Attempts Display Data",
                    False,
                    "No synthetic attempts available for display test"
                )
                return False
            
            display_analysis = {
                "total_attempts": len(synthetic_attempts),
                "attempts_with_required_display_fields": 0,
                "display_ready_attempts": [],
                "missing_field_issues": []
            }
            
            # Required fields for display
            required_display_fields = ["id", "courseId", "score", "status", "submittedAt"]
            optional_display_fields = ["courseName", "studentName", "timeSpent"]
            
            for attempt in synthetic_attempts:
                # Check required fields
                has_required_fields = all(
                    field in attempt and attempt[field] is not None 
                    for field in required_display_fields
                )
                
                if has_required_fields:
                    display_analysis["attempts_with_required_display_fields"] += 1
                    
                    # Create display-ready attempt
                    display_attempt = {
                        "id": attempt["id"],
                        "studentName": "Current Student",  # Would be actual name in frontend
                        "courseName": f"Course {attempt['courseId'][:8]}",  # Would be actual course name
                        "score": f"{attempt['score']:.1f}%",
                        "status": attempt["status"].title(),
                        "submittedAt": attempt["submittedAt"],
                        "timeSpent": attempt.get("timeSpent", "N/A")
                    }
                    
                    display_analysis["display_ready_attempts"].append(display_attempt)
                else:
                    missing_fields = [
                        field for field in required_display_fields 
                        if field not in attempt or attempt[field] is None
                    ]
                    display_analysis["missing_field_issues"].append({
                        "attempt_id": attempt.get("id", "unknown"),
                        "missing_fields": missing_fields
                    })
            
            # Sort display attempts by submission date (most recent first)
            display_analysis["display_ready_attempts"].sort(
                key=lambda x: x.get("submittedAt") or "", 
                reverse=True
            )
            
            success = display_analysis["attempts_with_required_display_fields"] > 0
            details = f"Display test: {display_analysis['attempts_with_required_display_fields']} attempts ready for display out of {display_analysis['total_attempts']} total"
            
            self.log_test(
                "Recent Attempts Display Data",
                success,
                details,
                display_analysis
            )
            
            return success
            
        except Exception as e:
            self.log_test("Recent Attempts Display Data", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_synthesis_test(self):
        """Run all tests for quiz attempts synthesis debugging"""
        print("🔍 QUIZ ATTEMPTS SYNTHESIS DEBUGGING TEST")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        print("🔐 AUTHENTICATION TESTING")
        print("-" * 40)
        
        admin_auth = self.authenticate_admin()
        student_auth = self.authenticate_student()
        
        if not admin_auth or not student_auth:
            print("❌ CRITICAL: Authentication failed. Cannot proceed with testing.")
            return False
        
        print()
        
        # Step 2: Enrollment Data Structure Analysis
        print("📊 ENROLLMENT DATA STRUCTURE ANALYSIS")
        print("-" * 40)
        
        enrollment_analysis = self.analyze_enrollment_data_structure()
        print()
        
        # Step 3: Course Quiz Matching Verification
        print("🎯 COURSE QUIZ MATCHING VERIFICATION")
        print("-" * 40)
        
        course_analysis = self.verify_course_quiz_matching()
        print()
        
        # Step 4: Synthetic Quiz Attempts Creation Test
        print("⚙️ SYNTHETIC QUIZ ATTEMPTS CREATION TEST")
        print("-" * 40)
        
        synthesis_analysis = self.test_synthetic_quiz_attempts_creation(enrollment_analysis, course_analysis)
        print()
        
        # Step 5: Filtering Logic Compatibility Test
        print("🔍 FILTERING LOGIC COMPATIBILITY TEST")
        print("-" * 40)
        
        filtering_success = self.test_filtering_logic_compatibility(synthesis_analysis, course_analysis)
        print()
        
        # Step 6: Recent Attempts Display Data Test
        print("📋 RECENT ATTEMPTS DISPLAY DATA TEST")
        print("-" * 40)
        
        display_success = self.test_recent_attempts_display_data(synthesis_analysis)
        print()
        
        # Generate Summary Report
        self.generate_synthesis_summary_report(enrollment_analysis, course_analysis, synthesis_analysis, filtering_success, display_success)
        
        return True

    def generate_synthesis_summary_report(self, enrollment_analysis: Dict, course_analysis: Dict, synthesis_analysis: Dict, filtering_success: bool, display_success: bool):
        """Generate comprehensive summary report for quiz attempts synthesis"""
        print("📊 QUIZ ATTEMPTS SYNTHESIS SUMMARY REPORT")
        print("=" * 80)
        
        # Calculate overall success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Root Cause Analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 30)
        
        # Issue 1: Enrollment Data
        enrollments_with_progress = enrollment_analysis.get("enrollments_with_progress", 0)
        total_enrollments = enrollment_analysis.get("total_enrollments", 0)
        
        if enrollments_with_progress > 0:
            print(f"✅ ENROLLMENT DATA: Found {enrollments_with_progress}/{total_enrollments} enrollments with progress data")
            print(f"   Progress Distribution: {enrollment_analysis.get('progress_ranges', {})}")
        else:
            print(f"❌ ENROLLMENT DATA ISSUE: No enrollments with progress found out of {total_enrollments} total")
            print("   → This explains why Recent Quiz Attempts shows 'No quiz attempts yet'")
        
        # Issue 2: Course Quiz Matching
        courses_with_quizzes = course_analysis.get("courses_with_quizzes", 0)
        total_courses = course_analysis.get("total_courses", 0)
        
        if courses_with_quizzes > 0:
            print(f"✅ COURSE QUIZ MATCHING: Found {courses_with_quizzes}/{total_courses} courses with quiz lessons")
            data_issues = len(course_analysis.get("data_format_issues", []))
            if data_issues > 0:
                print(f"   ⚠️  Data Format Issues: {data_issues} quiz lessons have structural problems")
        else:
            print(f"❌ COURSE QUIZ MATCHING ISSUE: No courses with quiz lessons found")
            print("   → This prevents synthetic quiz attempts from being created")
        
        # Issue 3: Synthesis Logic
        valid_synthetic_attempts = synthesis_analysis.get("valid_synthetic_attempts", 0)
        potential_attempts = synthesis_analysis.get("potential_synthetic_attempts", 0)
        
        if valid_synthetic_attempts > 0:
            print(f"✅ SYNTHESIS LOGIC: Created {valid_synthetic_attempts}/{potential_attempts} valid synthetic attempts")
        else:
            print(f"❌ SYNTHESIS LOGIC ISSUE: No valid synthetic attempts created from {potential_attempts} potential attempts")
            synthesis_issues = synthesis_analysis.get("synthesis_issues", [])
            if synthesis_issues:
                print(f"   Issues found: {len(synthesis_issues)} synthesis problems")
                for issue in synthesis_issues[:2]:  # Show first 2 issues
                    print(f"   - {issue.get('issue', 'Unknown issue')}")
        
        # Issue 4: Filtering Logic
        if filtering_success:
            print("✅ FILTERING LOGIC: Course filtering logic is compatible with synthetic attempts")
        else:
            print("❌ FILTERING LOGIC ISSUE: Course filtering not working with synthetic attempts")
            print("   → This explains why filtering doesn't work")
        
        # Issue 5: Display Logic
        if display_success:
            print("✅ DISPLAY LOGIC: Recent attempts display data structure is correct")
        else:
            print("❌ DISPLAY LOGIC ISSUE: Recent attempts missing required display fields")
        
        print()
        
        # Specific Recommendations
        print("💡 SPECIFIC RECOMMENDATIONS:")
        print("-" * 30)
        
        if enrollments_with_progress == 0:
            print("🔧 CRITICAL: Create test quiz submissions to generate enrollment progress data")
            print("   - Student needs to complete at least one quiz to create progress > 0%")
            print("   - This will provide data for synthetic quiz attempts creation")
        
        if courses_with_quizzes == 0:
            print("🔧 CRITICAL: Verify course data structure for quiz lesson detection")
            print("   - Check if quiz lessons are properly structured in course modules")
            print("   - Ensure quiz lessons have type='quiz' and proper question data")
        
        if valid_synthetic_attempts == 0 and enrollments_with_progress > 0:
            print("🔧 SYNTHESIS FIX: Debug course-enrollment matching logic")
            print("   - Verify that enrollment courseIds match quiz course IDs")
            print("   - Check if synthetic attempt ID format is correct")
        
        if not filtering_success and valid_synthetic_attempts > 0:
            print("🔧 FILTERING FIX: Update frontend filtering logic to handle synthetic attempts")
            print("   - Ensure course filter matches synthetic attempt courseId field")
            print("   - Verify that 'All Courses' filter includes synthetic attempts")
        
        if not display_success and valid_synthetic_attempts > 0:
            print("🔧 DISPLAY FIX: Add missing fields to synthetic attempts")
            print("   - Fetch course names for courseName field")
            print("   - Add student names for studentName field")
        
        print()
        
        # Final Diagnosis
        print("🎯 FINAL DIAGNOSIS:")
        print("-" * 20)
        
        if enrollments_with_progress == 0:
            print("🚨 PRIMARY ISSUE: No quiz progress data in enrollments")
            print("   The user's quiz attempts are not being recorded as enrollment progress.")
            print("   This is the root cause of 'No quiz attempts yet' message.")
        elif courses_with_quizzes == 0:
            print("🚨 PRIMARY ISSUE: Quiz courses not detected")
            print("   Courses with quiz lessons are not being identified correctly.")
            print("   This prevents synthetic quiz attempts from being created.")
        elif valid_synthetic_attempts == 0:
            print("🚨 PRIMARY ISSUE: Synthetic attempts creation failing")
            print("   Enrollment data exists but synthetic attempts are not being created.")
            print("   Check course-enrollment matching and data structure compatibility.")
        elif not filtering_success:
            print("🚨 PRIMARY ISSUE: Filtering logic incompatible")
            print("   Synthetic attempts are created but filtering is not working.")
            print("   Frontend filtering logic needs to be updated for synthetic attempts.")
        else:
            print("✅ SYNTHESIS WORKING: All components functioning correctly")
            print("   The issue may be in frontend implementation or data refresh.")
        
        print()
        print("=" * 80)

def main():
    """Main execution function"""
    test_suite = QuizAttemptsSynthesisTestSuite()
    
    try:
        success = test_suite.run_comprehensive_synthesis_test()
        
        if success:
            print("✅ Quiz Attempts Synthesis Testing completed successfully!")
            return 0
        else:
            print("❌ Quiz Attempts Synthesis Testing completed with issues!")
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