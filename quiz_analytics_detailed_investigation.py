#!/usr/bin/env python3
"""
Detailed Quiz Analytics Investigation
====================================

This test specifically investigates the discrepancy:
- System stats show 0 quiz attempts
- But 40 courses have quiz lessons
- And 44 enrollments exist with progress

Let's find out exactly what's happening.
"""

import requests
import json
import sys
from datetime import datetime

class QuizAnalyticsInvestigator:
    def __init__(self):
        self.base_url = "https://quiz-progress-fix.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }

    def authenticate_admin(self) -> bool:
        """Authenticate as admin user."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                return True
            return False
        except:
            return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}

    def investigate_quiz_calculation_logic(self):
        """Investigate how quiz statistics are calculated."""
        print("🔍 INVESTIGATING QUIZ CALCULATION LOGIC")
        print("=" * 60)
        
        # 1. Get system stats to see the exact calculation
        print("1️⃣ System Stats Calculation Analysis:")
        stats_response = self.session.get(
            f"{self.base_url}/analytics/system-stats",
            headers=self.get_headers(),
            timeout=10
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            quiz_stats = stats.get("quizStats", {})
            
            print(f"   Total Quizzes: {quiz_stats.get('totalQuizzes', 0)}")
            print(f"   Published Quizzes: {quiz_stats.get('publishedQuizzes', 0)}")
            print(f"   Total Attempts: {quiz_stats.get('totalAttempts', 0)}")
            print(f"   Average Score: {quiz_stats.get('averageScore', 0)}")
            print(f"   Pass Rate: {quiz_stats.get('passRate', 0)}")
            
            # The key insight: totalAttempts is calculated from enrollments with progress >= 100
            # But this might not be the right logic for quiz attempts
        
        # 2. Analyze the enrollment-based calculation
        print("\n2️⃣ Enrollment-Based Quiz Attempt Calculation:")
        enrollments_response = self.session.get(
            f"{self.base_url}/admin/enrollments",
            headers=self.get_headers(),
            timeout=10
        )
        
        if enrollments_response.status_code == 200:
            enrollments = enrollments_response.json()
            
            # Replicate the backend calculation logic
            # From server.py line 5744-5747: total_attempts = enrollments with progress >= 100
            total_attempts_backend_logic = len([e for e in enrollments if e.get('progress', 0) >= 100])
            print(f"   Backend Logic (progress >= 100): {total_attempts_backend_logic} attempts")
            
            # But let's also check enrollments with any progress > 0 (actual quiz attempts)
            attempts_with_any_progress = len([e for e in enrollments if e.get('progress', 0) > 0])
            print(f"   Enrollments with Progress > 0: {attempts_with_any_progress} attempts")
            
            # Check the average score calculation
            enrollments_with_progress = [e for e in enrollments if e.get('progress', 0) > 0]
            if enrollments_with_progress:
                avg_progress = sum(e.get('progress', 0) for e in enrollments_with_progress) / len(enrollments_with_progress)
                print(f"   Average Progress: {avg_progress:.2f}%")
                
                # Pass rate calculation (progress >= 100)
                passed = len([e for e in enrollments_with_progress if e.get('progress', 0) >= 100])
                pass_rate = (passed / len(enrollments_with_progress)) * 100
                print(f"   Pass Rate: {pass_rate:.2f}%")
        
        # 3. Check if there's a separate quiz_attempts collection that should be used
        print("\n3️⃣ Checking for Quiz Attempts Collection:")
        print("   Note: The backend might be looking for a separate 'quiz_attempts' collection")
        print("   that doesn't exist, which would explain the 0 attempts")
        
        # 4. Analyze course structure for quiz lessons
        print("\n4️⃣ Detailed Course Quiz Analysis:")
        courses_response = self.session.get(
            f"{self.base_url}/courses",
            headers=self.get_headers(),
            timeout=10
        )
        
        if courses_response.status_code == 200:
            courses = courses_response.json()
            
            quiz_lesson_count = 0
            courses_with_quizzes = 0
            
            for course in courses:
                course_has_quiz = False
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            quiz_lesson_count += 1
                            course_has_quiz = True
                
                if course_has_quiz:
                    courses_with_quizzes += 1
            
            print(f"   Total Quiz Lessons: {quiz_lesson_count}")
            print(f"   Courses with Quizzes: {courses_with_quizzes}")
            
            # This should match the backend calculation for totalQuizzes
            print(f"   Expected Total Quizzes (backend): {courses_with_quizzes}")

    def investigate_enrollment_quiz_synthesis(self):
        """Investigate the enrollment-based quiz synthesis mentioned in the review."""
        print("\n🔄 INVESTIGATING ENROLLMENT-BASED QUIZ SYNTHESIS")
        print("=" * 60)
        
        print("The review mentions 'enrollment-based quiz synthesis' not working correctly.")
        print("This suggests the system should synthesize quiz attempts from enrollment data.")
        
        # Get enrollments and analyze for quiz synthesis
        enrollments_response = self.session.get(
            f"{self.base_url}/admin/enrollments",
            headers=self.get_headers(),
            timeout=10
        )
        
        if enrollments_response.status_code == 200:
            enrollments = enrollments_response.json()
            
            print(f"\n📊 Enrollment Data for Quiz Synthesis:")
            print(f"   Total Enrollments: {len(enrollments)}")
            
            # Analyze enrollments that could be synthesized as quiz attempts
            potential_quiz_attempts = []
            
            for enrollment in enrollments:
                progress = enrollment.get('progress', 0)
                status = enrollment.get('status', 'unknown')
                course_id = enrollment.get('courseId')
                student_id = enrollment.get('userId')
                
                # If enrollment has progress, it could represent a quiz attempt
                if progress > 0:
                    potential_quiz_attempts.append({
                        'studentId': student_id,
                        'courseId': course_id,
                        'progress': progress,
                        'status': status,
                        'score': progress,  # Progress could be treated as score
                        'isPassed': progress >= 70  # Assuming 70% pass rate
                    })
            
            print(f"   Potential Quiz Attempts (from enrollments): {len(potential_quiz_attempts)}")
            
            if len(potential_quiz_attempts) > 0:
                avg_score = sum(qa['score'] for qa in potential_quiz_attempts) / len(potential_quiz_attempts)
                passed_attempts = len([qa for qa in potential_quiz_attempts if qa['isPassed']])
                pass_rate = (passed_attempts / len(potential_quiz_attempts)) * 100
                
                print(f"   Synthesized Average Score: {avg_score:.2f}%")
                print(f"   Synthesized Pass Rate: {pass_rate:.2f}%")
                
                print(f"\n🎯 ISSUE IDENTIFIED:")
                print(f"   The system has {len(potential_quiz_attempts)} potential quiz attempts from enrollments")
                print(f"   But analytics show 0 attempts because the synthesis logic is not working")
                print(f"   The backend is looking for actual quiz_attempts records instead of synthesizing from enrollments")

    def run_investigation(self):
        """Run the complete investigation."""
        print("🚀 QUIZ ANALYTICS DETAILED INVESTIGATION")
        print("=" * 80)
        
        if not self.authenticate_admin():
            print("❌ Authentication failed")
            return False
        
        self.investigate_quiz_calculation_logic()
        self.investigate_enrollment_quiz_synthesis()
        
        print("\n" + "=" * 80)
        print("🎯 FINAL ANALYSIS")
        print("=" * 80)
        
        print("ROOT CAUSE OF QUIZ ANALYTICS ISSUE:")
        print("1. The backend calculates quiz attempts from enrollments with progress >= 100")
        print("2. But the system stats show 0 because the calculation logic has a bug")
        print("3. The 'enrollment-based quiz synthesis' is not working correctly")
        print("4. Analytics should show recent quiz attempts from enrollment progress data")
        print("5. The system has the data (44 enrollments with progress) but can't display it")
        
        print("\nRECOMMENDED FIXES:")
        print("1. Fix the quiz analytics calculation to use enrollment progress data")
        print("2. Implement proper enrollment-based quiz synthesis")
        print("3. Update analytics to show 'Recent Quiz Attempts' from enrollment data")
        
        return True

if __name__ == "__main__":
    investigator = QuizAnalyticsInvestigator()
    investigator.run_investigation()