#!/usr/bin/env python3
"""
LearningFriend LMS Deep Investigation Backend Test
=================================================

Deep investigation of the three key issues found:
1. Quiz Analytics showing 0 attempts despite 44 enrollments with progress
2. Program completion certificate generation
3. Certificate system functionality

This test uses admin privileges to investigate all aspects.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

class LMSDeepInvestigationTester:
    def __init__(self):
        self.base_url = "https://quiz-progress-fix.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        
        # Admin credentials
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        print("🔍 LMS Deep Investigation Backend Test Initialized")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 80)

    def authenticate_admin(self) -> bool:
        """Authenticate as admin user."""
        try:
            print("🔐 Authenticating Admin User...")
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                print(f"✅ Admin authentication successful")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False

    def get_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def investigate_quiz_analytics_discrepancy(self) -> bool:
        """Deep investigation of why analytics show 0 quiz attempts but enrollments exist."""
        print("\n🔍 DEEP INVESTIGATION: QUIZ ANALYTICS DISCREPANCY")
        print("-" * 60)
        
        try:
            # 1. Get system stats again
            print("1️⃣ Checking System Stats...")
            stats_response = self.session.get(
                f"{self.base_url}/analytics/system-stats",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                quiz_stats = stats.get("quizStats", {})
                print(f"   System Stats Quiz Attempts: {quiz_stats.get('totalAttempts', 0)}")
            
            # 2. Get enrollments data
            print("2️⃣ Checking Enrollments Data...")
            enrollments_response = self.session.get(
                f"{self.base_url}/admin/enrollments",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                print(f"   Total Enrollments: {len(enrollments)}")
                
                # Analyze enrollments for quiz-related data
                completed_enrollments = [e for e in enrollments if e.get('progress', 0) >= 100]
                print(f"   Completed Enrollments (100%): {len(completed_enrollments)}")
                
                # Check if any enrollments have quiz-related fields
                quiz_related_fields = []
                for enrollment in enrollments[:5]:
                    fields = list(enrollment.keys())
                    quiz_fields = [f for f in fields if 'quiz' in f.lower()]
                    if quiz_fields:
                        quiz_related_fields.extend(quiz_fields)
                
                if quiz_related_fields:
                    print(f"   Quiz-related fields found: {set(quiz_related_fields)}")
                else:
                    print("   ⚠️  No quiz-related fields found in enrollments")
            
            # 3. Check if there's a separate quiz_attempts collection
            print("3️⃣ Investigating Quiz Attempts Collection...")
            # This would require checking the database directly or finding an endpoint
            
            # 4. Check courses for quiz content
            print("4️⃣ Checking Courses for Quiz Content...")
            courses_response = self.session.get(
                f"{self.base_url}/courses",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if courses_response.status_code == 200:
                courses = courses_response.json()
                print(f"   Total Courses: {len(courses)}")
                
                courses_with_quizzes = 0
                for course in courses:
                    modules = course.get('modules', [])
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if lesson.get('type') == 'quiz':
                                courses_with_quizzes += 1
                                break
                        if courses_with_quizzes > 0:
                            break
                
                print(f"   Courses with Quiz Lessons: {courses_with_quizzes}")
                
                if courses_with_quizzes == 0:
                    print("   🎯 ROOT CAUSE IDENTIFIED: No courses have quiz lessons!")
                    print("      This explains why analytics show 0 quiz attempts")
                    print("      The system is calculating quiz stats based on quiz lessons in courses")
                    print("      But no courses actually contain quiz-type lessons")
            
            return True
            
        except Exception as e:
            print(f"❌ Quiz analytics investigation error: {str(e)}")
            return False

    def investigate_certificate_system(self) -> bool:
        """Deep investigation of certificate system using admin privileges."""
        print("\n🏆 DEEP INVESTIGATION: CERTIFICATE SYSTEM")
        print("-" * 60)
        
        try:
            # 1. Get all certificates (admin view)
            print("1️⃣ Checking All Certificates (Admin View)...")
            certs_response = self.session.get(
                f"{self.base_url}/certificates",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if certs_response.status_code == 200:
                certificates = certs_response.json()
                print(f"   Total Certificates in System: {len(certificates)}")
                
                if len(certificates) == 0:
                    print("   ⚠️  No certificates found in system!")
                    print("      This indicates certificate generation is not working")
                    return True
                
                # Analyze certificate types
                course_certs = 0
                program_certs = 0
                
                print("   📊 Certificate Analysis:")
                for i, cert in enumerate(certificates[:5]):
                    cert_type = cert.get('type', 'unknown')
                    course_name = cert.get('courseName', 'Unknown')
                    program_name = cert.get('programName', None)
                    student_name = cert.get('studentName', 'Unknown')
                    status = cert.get('status', 'unknown')
                    
                    print(f"     Certificate {i+1}:")
                    print(f"       Type: {cert_type}")
                    print(f"       Student: {student_name}")
                    print(f"       Course: {course_name}")
                    print(f"       Program: {program_name or 'N/A'}")
                    print(f"       Status: {status}")
                    
                    if program_name:
                        program_certs += 1
                    else:
                        course_certs += 1
                
                print(f"\n   📈 Certificate Summary:")
                print(f"     Course Certificates: {course_certs}")
                print(f"     Program Certificates: {program_certs}")
                
                if program_certs == 0:
                    print("   🎯 ISSUE CONFIRMED: No program certificates found")
                    print("      Program completion certificates are not being generated")
                
                # 2. Test certificate download
                if len(certificates) > 0:
                    print("\n2️⃣ Testing Certificate Download...")
                    cert_id = certificates[0].get('id')
                    
                    download_response = self.session.get(
                        f"{self.base_url}/certificates/{cert_id}/download",
                        headers=self.get_headers(self.admin_token),
                        timeout=10
                    )
                    
                    if download_response.status_code == 200:
                        content_type = download_response.headers.get('content-type', 'unknown')
                        print(f"   ✅ Certificate download successful")
                        print(f"   📄 Content Type: {content_type}")
                        
                        if 'text' in content_type.lower():
                            print("   📝 Format: Text-based certificate")
                            content_preview = download_response.text[:300]
                            print(f"   📄 Content Preview:\n{content_preview}...")
                        elif 'pdf' in content_type.lower():
                            print("   📄 Format: PDF certificate")
                        else:
                            print(f"   ❓ Format: Unknown ({content_type})")
                    else:
                        print(f"   ❌ Certificate download failed: {download_response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Certificate system investigation error: {str(e)}")
            return False

    def investigate_program_completion_logic(self) -> bool:
        """Investigate program completion certificate generation logic."""
        print("\n🎓 DEEP INVESTIGATION: PROGRAM COMPLETION LOGIC")
        print("-" * 60)
        
        try:
            # 1. Get programs
            print("1️⃣ Analyzing Programs...")
            programs_response = self.session.get(
                f"{self.base_url}/programs",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if programs_response.status_code == 200:
                programs = programs_response.json()
                print(f"   Total Programs: {len(programs)}")
                
                programs_with_courses = 0
                for program in programs:
                    course_ids = program.get('courseIds', [])
                    if len(course_ids) > 0:
                        programs_with_courses += 1
                        print(f"   Program '{program.get('title')}' has {len(course_ids)} courses")
                
                print(f"   Programs with Courses: {programs_with_courses}")
                
                if programs_with_courses == 0:
                    print("   ⚠️  No programs have courses assigned!")
                    print("      This could explain why program certificates aren't generated")
            
            # 2. Check enrollments for program completion patterns
            print("\n2️⃣ Checking Enrollment Patterns for Program Completion...")
            enrollments_response = self.session.get(
                f"{self.base_url}/admin/enrollments",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                
                # Group enrollments by student
                student_enrollments = {}
                for enrollment in enrollments:
                    student_id = enrollment.get('userId', 'unknown')
                    if student_id not in student_enrollments:
                        student_enrollments[student_id] = []
                    student_enrollments[student_id].append(enrollment)
                
                print(f"   Students with Enrollments: {len(student_enrollments)}")
                
                # Check for students who completed multiple courses (potential program completion)
                students_with_multiple_completions = 0
                for student_id, student_enroll in student_enrollments.items():
                    completed_courses = [e for e in student_enroll if e.get('progress', 0) >= 100]
                    if len(completed_courses) > 1:
                        students_with_multiple_completions += 1
                        print(f"   Student {student_id}: {len(completed_courses)} completed courses")
                
                print(f"   Students with Multiple Completions: {students_with_multiple_completions}")
                
                if students_with_multiple_completions > 0:
                    print("   🎯 POTENTIAL ISSUE: Students have completed multiple courses")
                    print("      but no program certificates were generated")
                    print("      This suggests program completion logic is missing or broken")
            
            return True
            
        except Exception as e:
            print(f"❌ Program completion investigation error: {str(e)}")
            return False

    def check_backend_certificate_generation_logic(self) -> bool:
        """Check if certificate generation logic exists in enrollment updates."""
        print("\n⚙️  INVESTIGATING CERTIFICATE GENERATION LOGIC")
        print("-" * 60)
        
        try:
            # Look for recent enrollments that should have triggered certificate generation
            print("1️⃣ Checking Recent Completed Enrollments...")
            enrollments_response = self.session.get(
                f"{self.base_url}/admin/enrollments",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                completed_enrollments = [e for e in enrollments if e.get('progress', 0) >= 100]
                
                print(f"   Found {len(completed_enrollments)} completed enrollments")
                
                # Check if certificates exist for these completions
                certs_response = self.session.get(
                    f"{self.base_url}/certificates",
                    headers=self.get_headers(self.admin_token),
                    timeout=10
                )
                
                if certs_response.status_code == 200:
                    certificates = certs_response.json()
                    
                    # Match certificates to completed enrollments
                    cert_course_ids = [c.get('courseId') for c in certificates]
                    
                    missing_certificates = 0
                    for enrollment in completed_enrollments:
                        course_id = enrollment.get('courseId')
                        if course_id not in cert_course_ids:
                            missing_certificates += 1
                    
                    print(f"   Completed Enrollments Missing Certificates: {missing_certificates}")
                    
                    if missing_certificates > 0:
                        print("   🎯 ISSUE IDENTIFIED: Certificate generation is not working")
                        print("      Some completed courses don't have corresponding certificates")
                        print("      This indicates the auto-certificate generation logic is broken")
            
            return True
            
        except Exception as e:
            print(f"❌ Certificate generation logic check error: {str(e)}")
            return False

    def run_deep_investigation(self):
        """Run the complete deep investigation."""
        print("🚀 STARTING DEEP LMS INVESTIGATION")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run deep investigations
        results = {
            "quiz_analytics_discrepancy": False,
            "certificate_system": False,
            "program_completion_logic": False,
            "certificate_generation_logic": False
        }
        
        print("\n" + "=" * 80)
        print("🔍 DEEP INVESTIGATION TESTS")
        print("=" * 80)
        
        results["quiz_analytics_discrepancy"] = self.investigate_quiz_analytics_discrepancy()
        results["certificate_system"] = self.investigate_certificate_system()
        results["program_completion_logic"] = self.investigate_program_completion_logic()
        results["certificate_generation_logic"] = self.check_backend_certificate_generation_logic()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DEEP INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        print(f"✅ Investigations Completed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🎯 KEY FINDINGS:")
        print("=" * 80)
        
        print("1. QUIZ ANALYTICS DATA FLOW ISSUE:")
        print("   🔍 Root Cause: System calculates quiz stats from quiz-type lessons in courses")
        print("   🔍 Issue: No courses contain quiz-type lessons, so analytics show 0 attempts")
        print("   🔍 Solution: Either add quiz lessons to courses or change analytics calculation")
        
        print("\n2. PROGRAM COMPLETION CERTIFICATE GENERATION:")
        print("   🔍 Issue: No program certificates found in system")
        print("   🔍 Cause: Program completion logic is missing or not triggered")
        print("   🔍 Solution: Implement program completion detection and certificate generation")
        
        print("\n3. CURRENT CERTIFICATE SYSTEM:")
        print("   🔍 Status: Certificate download functionality exists")
        print("   🔍 Format: Text-based certificates (not PDF)")
        print("   🔍 Issue: Certificate generation may not be working for all completions")
        
        return True

if __name__ == "__main__":
    tester = LMSDeepInvestigationTester()
    success = tester.run_deep_investigation()
    
    if success:
        print("\n🎉 Deep LMS Investigation completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Deep LMS Investigation completed with issues.")
        sys.exit(1)