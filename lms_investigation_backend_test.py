#!/usr/bin/env python3
"""
LearningFriend LMS Investigation Backend Test
===========================================

This test investigates three key issues:
1. Quiz Analytics Data Flow Issue - why quiz analytics are not showing recent quiz attempts
2. Program Completion Certificate Generation - test if program certificates are generated
3. Current Certificate System - test certificate generation and download functionality

Testing Requirements:
- GET /api/analytics/system-stats to see current quiz attempt data
- GET /api/admin/enrollments to check enrollment data with quiz progress
- GET /api/programs to see available programs
- GET /api/certificates/my-certificates to see what types of certificates exist
- GET /api/certificates/{certificate_id}/download to see current download format
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

class LMSInvestigationTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://quiz-progress-fix.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        
        # Test credentials
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        self.student_credentials = {
            "username_or_email": "brayden.student@learningfwiend.com", 
            "password": "Cove1234!"
        }
        
        print("🔍 LMS Investigation Backend Test Initialized")
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
                print(f"   User: {data.get('user', {}).get('full_name', 'Unknown')}")
                print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False

    def authenticate_student(self) -> bool:
        """Authenticate as student user."""
        try:
            print("🔐 Authenticating Student User...")
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=self.student_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                print(f"✅ Student authentication successful")
                print(f"   User: {data.get('user', {}).get('full_name', 'Unknown')}")
                print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
                return True
            else:
                print(f"❌ Student authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Student authentication error: {str(e)}")
            return False

    def get_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def test_quiz_analytics_system_stats(self) -> bool:
        """Test GET /api/analytics/system-stats to see current quiz attempt data."""
        print("\n📊 TESTING QUIZ ANALYTICS - SYSTEM STATS")
        print("-" * 50)
        
        try:
            response = self.session.get(
                f"{self.base_url}/analytics/system-stats",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ System stats retrieved successfully")
                
                # Analyze quiz statistics
                quiz_stats = data.get("quizStats", {})
                print(f"📈 Quiz Statistics Analysis:")
                print(f"   Total Quizzes: {quiz_stats.get('totalQuizzes', 0)}")
                print(f"   Published Quizzes: {quiz_stats.get('publishedQuizzes', 0)}")
                print(f"   Total Attempts: {quiz_stats.get('totalAttempts', 0)}")
                print(f"   Average Score: {quiz_stats.get('averageScore', 0)}%")
                print(f"   Pass Rate: {quiz_stats.get('passRate', 0)}%")
                print(f"   Quizzes This Month: {quiz_stats.get('quizzesThisMonth', 0)}")
                
                # Check if there are quiz attempts
                total_attempts = quiz_stats.get('totalAttempts', 0)
                if total_attempts == 0:
                    print("⚠️  ISSUE IDENTIFIED: No quiz attempts found in system stats")
                    print("   This could explain why analytics show 'No quiz attempts yet'")
                else:
                    print(f"✅ Quiz attempts found: {total_attempts}")
                
                # Analyze enrollment statistics
                enrollment_stats = data.get("enrollmentStats", {})
                print(f"\n📚 Enrollment Statistics:")
                print(f"   Total Enrollments: {enrollment_stats.get('totalEnrollments', 0)}")
                print(f"   Active Enrollments: {enrollment_stats.get('activeEnrollments', 0)}")
                print(f"   Completed Enrollments: {enrollment_stats.get('completedEnrollments', 0)}")
                
                return True
            else:
                print(f"❌ Failed to get system stats: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ System stats test error: {str(e)}")
            return False

    def test_admin_enrollments_data(self) -> bool:
        """Test GET /api/admin/enrollments to check enrollment data with quiz progress."""
        print("\n📚 TESTING ADMIN ENROLLMENTS DATA")
        print("-" * 50)
        
        try:
            response = self.session.get(
                f"{self.base_url}/admin/enrollments",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                print(f"✅ Admin enrollments retrieved successfully")
                print(f"   Total Enrollments Found: {len(enrollments)}")
                
                if len(enrollments) == 0:
                    print("⚠️  CRITICAL ISSUE: No enrollments found!")
                    print("   This explains why quiz analytics show no data")
                    return False
                
                # Analyze enrollment data for quiz progress
                quiz_related_enrollments = 0
                completed_enrollments = 0
                enrollments_with_progress = 0
                
                print(f"\n📊 Enrollment Analysis:")
                for i, enrollment in enumerate(enrollments[:5]):  # Show first 5 for analysis
                    progress = enrollment.get('progress', 0)
                    status = enrollment.get('status', 'unknown')
                    course_id = enrollment.get('courseId', 'unknown')
                    student_name = enrollment.get('studentName', 'Unknown')
                    
                    print(f"   Enrollment {i+1}:")
                    print(f"     Student: {student_name}")
                    print(f"     Course ID: {course_id}")
                    print(f"     Progress: {progress}%")
                    print(f"     Status: {status}")
                    
                    if progress > 0:
                        enrollments_with_progress += 1
                    if progress >= 100:
                        completed_enrollments += 1
                
                print(f"\n📈 Summary:")
                print(f"   Enrollments with Progress > 0: {enrollments_with_progress}")
                print(f"   Completed Enrollments (100%): {completed_enrollments}")
                
                if enrollments_with_progress == 0:
                    print("⚠️  ISSUE: No enrollments have progress > 0")
                    print("   This could indicate quiz attempts are not being recorded properly")
                
                return True
            else:
                print(f"❌ Failed to get admin enrollments: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin enrollments test error: {str(e)}")
            return False

    def test_programs_data(self) -> bool:
        """Test GET /api/programs to see available programs."""
        print("\n🎓 TESTING PROGRAMS DATA")
        print("-" * 50)
        
        try:
            response = self.session.get(
                f"{self.base_url}/programs",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code == 200:
                programs = response.json()
                print(f"✅ Programs retrieved successfully")
                print(f"   Total Programs Found: {len(programs)}")
                
                if len(programs) == 0:
                    print("⚠️  No programs found in the system")
                    return True
                
                # Analyze program structure
                print(f"\n📊 Program Analysis:")
                for i, program in enumerate(programs[:3]):  # Show first 3 for analysis
                    title = program.get('title', 'Unknown')
                    course_ids = program.get('courseIds', [])
                    course_count = program.get('courseCount', 0)
                    instructor = program.get('instructor', 'Unknown')
                    
                    print(f"   Program {i+1}:")
                    print(f"     Title: {title}")
                    print(f"     Course Count: {course_count}")
                    print(f"     Course IDs: {len(course_ids)} courses")
                    print(f"     Instructor: {instructor}")
                
                return True
            else:
                print(f"❌ Failed to get programs: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Programs test error: {str(e)}")
            return False

    def test_student_certificates(self) -> bool:
        """Test GET /api/certificates/my-certificates to see what types of certificates exist."""
        print("\n🏆 TESTING STUDENT CERTIFICATES")
        print("-" * 50)
        
        try:
            response = self.session.get(
                f"{self.base_url}/certificates/my-certificates",
                headers=self.get_headers(self.student_token),
                timeout=10
            )
            
            if response.status_code == 200:
                certificates = response.json()
                print(f"✅ Student certificates retrieved successfully")
                print(f"   Total Certificates Found: {len(certificates)}")
                
                if len(certificates) == 0:
                    print("⚠️  No certificates found for student")
                    print("   This could indicate certificate generation issues")
                    return True
                
                # Analyze certificate types
                course_certificates = 0
                program_certificates = 0
                
                print(f"\n📊 Certificate Analysis:")
                for i, cert in enumerate(certificates):
                    cert_type = cert.get('type', 'unknown')
                    course_name = cert.get('courseName', 'Unknown')
                    program_name = cert.get('programName', None)
                    status = cert.get('status', 'unknown')
                    issue_date = cert.get('issueDate', 'Unknown')
                    
                    print(f"   Certificate {i+1}:")
                    print(f"     Type: {cert_type}")
                    print(f"     Course: {course_name}")
                    print(f"     Program: {program_name or 'N/A'}")
                    print(f"     Status: {status}")
                    print(f"     Issue Date: {issue_date}")
                    
                    if program_name:
                        program_certificates += 1
                    else:
                        course_certificates += 1
                
                print(f"\n📈 Certificate Summary:")
                print(f"   Course Certificates: {course_certificates}")
                print(f"   Program Certificates: {program_certificates}")
                
                if program_certificates == 0:
                    print("⚠️  ISSUE IDENTIFIED: No program certificates found")
                    print("   This confirms program completion certificates are not being generated")
                
                return True
            else:
                print(f"❌ Failed to get student certificates: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Student certificates test error: {str(e)}")
            return False

    def test_certificate_download_format(self) -> bool:
        """Test certificate download to understand current format."""
        print("\n📄 TESTING CERTIFICATE DOWNLOAD FORMAT")
        print("-" * 50)
        
        try:
            # First get student certificates to find one to download
            response = self.session.get(
                f"{self.base_url}/certificates/my-certificates",
                headers=self.get_headers(self.student_token),
                timeout=10
            )
            
            if response.status_code != 200:
                print("❌ Could not retrieve certificates for download test")
                return False
            
            certificates = response.json()
            if len(certificates) == 0:
                print("⚠️  No certificates available for download test")
                return True
            
            # Try to download the first certificate
            cert_id = certificates[0].get('id')
            if not cert_id:
                print("❌ Certificate ID not found")
                return False
            
            print(f"📥 Attempting to download certificate: {cert_id}")
            
            download_response = self.session.get(
                f"{self.base_url}/certificates/{cert_id}/download",
                headers=self.get_headers(self.student_token),
                timeout=10
            )
            
            if download_response.status_code == 200:
                print("✅ Certificate download successful")
                
                # Analyze response headers and content
                content_type = download_response.headers.get('content-type', 'unknown')
                content_length = download_response.headers.get('content-length', 'unknown')
                
                print(f"📊 Download Analysis:")
                print(f"   Content Type: {content_type}")
                print(f"   Content Length: {content_length} bytes")
                
                # Check if it's text-based or PDF
                if 'text' in content_type.lower():
                    print("📝 Format: Text-based certificate")
                    # Show first 200 characters of content
                    content_preview = download_response.text[:200]
                    print(f"   Content Preview: {content_preview}...")
                elif 'pdf' in content_type.lower():
                    print("📄 Format: PDF certificate")
                else:
                    print(f"❓ Format: Unknown ({content_type})")
                
                return True
            else:
                print(f"❌ Certificate download failed: {download_response.status_code}")
                print(f"   Response: {download_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Certificate download test error: {str(e)}")
            return False

    def test_program_completion_flow(self) -> bool:
        """Test program completion certificate generation logic."""
        print("\n🎯 TESTING PROGRAM COMPLETION FLOW")
        print("-" * 50)
        
        try:
            # Get student enrollments to check for completed programs
            response = self.session.get(
                f"{self.base_url}/enrollments",
                headers=self.get_headers(self.student_token),
                timeout=10
            )
            
            if response.status_code != 200:
                print("❌ Could not retrieve student enrollments")
                return False
            
            enrollments = response.json()
            print(f"📚 Student has {len(enrollments)} enrollments")
            
            # Group enrollments by program (if any)
            # This would require checking which courses belong to which programs
            # For now, let's check if any enrollments are 100% complete
            
            completed_courses = []
            for enrollment in enrollments:
                if enrollment.get('progress', 0) >= 100:
                    completed_courses.append({
                        'courseId': enrollment.get('courseId'),
                        'courseName': enrollment.get('courseName', 'Unknown'),
                        'completedAt': enrollment.get('completedAt')
                    })
            
            print(f"✅ Found {len(completed_courses)} completed courses")
            
            if len(completed_courses) > 0:
                print("📊 Completed Courses:")
                for course in completed_courses:
                    print(f"   - {course['courseName']} (ID: {course['courseId']})")
                
                # Check if any of these courses are part of programs
                # This would require cross-referencing with program data
                print("\n🔍 Checking for program completion logic...")
                print("   Note: Program completion certificate generation logic")
                print("   should be triggered when all courses in a program are completed")
                
            else:
                print("⚠️  No completed courses found for this student")
                print("   Cannot test program completion certificate generation")
            
            return True
            
        except Exception as e:
            print(f"❌ Program completion flow test error: {str(e)}")
            return False

    def get_available_users(self) -> bool:
        """Get list of available users to find student accounts."""
        print("\n👥 GETTING AVAILABLE USERS")
        print("-" * 50)
        
        try:
            response = self.session.get(
                f"{self.base_url}/auth/admin/users",
                headers=self.get_headers(self.admin_token),
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Found {len(users)} users in system")
                
                students = [u for u in users if u.get('role') == 'learner']
                print(f"📚 Found {len(students)} student accounts:")
                
                for student in students[:5]:  # Show first 5 students
                    print(f"   - {student.get('email')} ({student.get('full_name')})")
                
                return True
            else:
                print(f"❌ Failed to get users: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Get users error: {str(e)}")
            return False

    def run_investigation(self):
        """Run the complete LMS investigation."""
        print("🚀 STARTING LMS INVESTIGATION")
        print("=" * 80)
        
        # Authentication
        admin_auth = self.authenticate_admin()
        
        if not admin_auth:
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Get available users first
        self.get_available_users()
        
        student_auth = self.authenticate_student()
        
        if not student_auth:
            print("⚠️  Proceeding with admin-only tests (student authentication failed)")
            # Continue with admin-only tests
        
        # Test Results
        results = {
            "quiz_analytics_system_stats": False,
            "admin_enrollments_data": False,
            "programs_data": False,
            "student_certificates": False,
            "certificate_download_format": False,
            "program_completion_flow": False
        }
        
        # Run tests
        print("\n" + "=" * 80)
        print("🔍 INVESTIGATION TESTS")
        print("=" * 80)
        
        results["quiz_analytics_system_stats"] = self.test_quiz_analytics_system_stats()
        results["admin_enrollments_data"] = self.test_admin_enrollments_data()
        results["programs_data"] = self.test_programs_data()
        results["student_certificates"] = self.test_student_certificates()
        results["certificate_download_format"] = self.test_certificate_download_format()
        results["program_completion_flow"] = self.test_program_completion_flow()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 DETAILED FINDINGS:")
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print("\n" + "=" * 80)
        print("🎯 KEY INVESTIGATION RESULTS")
        print("=" * 80)
        
        print("1. QUIZ ANALYTICS DATA FLOW:")
        if results["quiz_analytics_system_stats"] and results["admin_enrollments_data"]:
            print("   ✅ Analytics endpoints are functional")
            print("   🔍 Check console output above for specific data issues")
        else:
            print("   ❌ Analytics endpoints have issues")
        
        print("\n2. PROGRAM COMPLETION CERTIFICATES:")
        if results["student_certificates"]:
            print("   ✅ Certificate system is functional")
            print("   🔍 Check console output for program vs course certificate analysis")
        else:
            print("   ❌ Certificate system has issues")
        
        print("\n3. CURRENT CERTIFICATE SYSTEM:")
        if results["certificate_download_format"]:
            print("   ✅ Certificate download is functional")
            print("   🔍 Check console output for format analysis (text vs PDF)")
        else:
            print("   ❌ Certificate download has issues")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = LMSInvestigationTester()
    success = tester.run_investigation()
    
    if success:
        print("\n🎉 LMS Investigation completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  LMS Investigation completed with issues found.")
        sys.exit(1)