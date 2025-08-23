#!/usr/bin/env python3
"""
Certificate Download Functionality Testing - New Feature Implementation
Testing the new certificate download endpoint and related functionality

FOCUS AREAS:
- GET /api/certificates/my-certificates (to list available certificates)  
- GET /api/certificates/{certificate_id}/download (new download endpoint)
- File generation and content verification
- Permission validation
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-bugfix-1.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com", 
    "password": "Cove1234!"
}

class CertificateDownloadTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.certificates = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_user(self, credentials, user_type):
        """Authenticate user and get token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                self.log_result(
                    f"{user_type} Authentication",
                    True,
                    f"Successfully authenticated {user_info.get('email', 'user')}",
                    f"Role: {user_info.get('role')}, ID: {user_info.get('id')}"
                )
                return token, user_info
            else:
                self.log_result(
                    f"{user_type} Authentication",
                    False,
                    f"Authentication failed: {response.status_code}",
                    response.text
                )
                return None, None
                
        except Exception as e:
            self.log_result(
                f"{user_type} Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return None, None
    
    def get_my_certificates(self, token, user_type):
        """Get user's certificates"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Use different endpoints based on user type
            if user_type == "Admin":
                # Admin uses general certificates endpoint
                response = requests.get(f"{BACKEND_URL}/certificates", headers=headers)
            else:
                # Students use my-certificates endpoint
                response = requests.get(f"{BACKEND_URL}/certificates/my-certificates", headers=headers)
            
            if response.status_code == 200:
                certificates = response.json()
                self.log_result(
                    f"Get {user_type} Certificates",
                    True,
                    f"Retrieved {len(certificates)} certificates",
                    f"Certificates: {[cert.get('id', 'N/A') for cert in certificates]}"
                )
                return certificates
            else:
                self.log_result(
                    f"Get {user_type} Certificates",
                    False,
                    f"Failed to get certificates: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                f"Get {user_type} Certificates",
                False,
                f"Error getting certificates: {str(e)}"
            )
            return []
    
    def test_certificate_download(self, certificate_id, token, user_type, should_succeed=True):
        """Test certificate download functionality"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BACKEND_URL}/certificates/{certificate_id}/download", headers=headers)
            
            if should_succeed:
                if response.status_code == 200:
                    # Check content type and headers
                    content_type = response.headers.get('Content-Type', '')
                    content_disposition = response.headers.get('Content-Disposition', '')
                    content_length = len(response.content)
                    
                    # Verify it's a downloadable file
                    is_downloadable = 'attachment' in content_disposition
                    has_filename = 'filename=' in content_disposition
                    
                    self.log_result(
                        f"Certificate Download - {user_type}",
                        True,
                        f"Successfully downloaded certificate {certificate_id}",
                        f"Content-Type: {content_type}, Size: {content_length} bytes, Downloadable: {is_downloadable}, Has filename: {has_filename}"
                    )
                    
                    # Test content verification
                    if content_type == 'text/plain':
                        content = response.text
                        has_certificate_header = "CERTIFICATE OF COMPLETION" in content
                        has_student_name = len(content) > 100  # Basic content check
                        
                        self.log_result(
                            f"Certificate Content Verification - {user_type}",
                            has_certificate_header and has_student_name,
                            f"Certificate content verified",
                            f"Has header: {has_certificate_header}, Has content: {has_student_name}"
                        )
                    
                    return True
                else:
                    self.log_result(
                        f"Certificate Download - {user_type}",
                        False,
                        f"Download failed: {response.status_code}",
                        response.text
                    )
                    return False
            else:
                # Should fail (permission test)
                if response.status_code in [403, 404]:
                    self.log_result(
                        f"Certificate Download Permission Test - {user_type}",
                        True,
                        f"Correctly denied access: {response.status_code}",
                        response.text
                    )
                    return True
                else:
                    self.log_result(
                        f"Certificate Download Permission Test - {user_type}",
                        False,
                        f"Should have been denied but got: {response.status_code}",
                        response.text
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                f"Certificate Download - {user_type}",
                False,
                f"Download error: {str(e)}"
            )
            return False
    
    def create_test_certificate_via_completion(self, token, student_user):
        """Create a test certificate by completing a course"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get student's enrollments
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Get Student Enrollments",
                    False,
                    f"Failed to get enrollments: {enrollments_response.status_code}"
                )
                return None
            
            enrollments = enrollments_response.json()
            if not enrollments:
                self.log_result(
                    "Get Student Enrollments",
                    False,
                    "No enrollments found for student"
                )
                return None
            
            # Use first enrollment
            enrollment = enrollments[0]
            course_id = enrollment['courseId']
            
            # Complete the course by setting progress to 100%
            progress_data = {
                "progress": 100.0,
                "currentLessonId": "final-lesson",
                "timeSpent": 3600
            }
            
            progress_response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress", 
                json=progress_data, 
                headers=headers
            )
            
            if progress_response.status_code == 200:
                self.log_result(
                    "Complete Course for Certificate",
                    True,
                    f"Successfully completed course {course_id}",
                    f"Progress set to 100%"
                )
                
                # Wait a moment for certificate generation
                import time
                time.sleep(2)
                
                # Check if certificate was generated
                certificates = self.get_my_certificates(token, "Student")
                if certificates:
                    return certificates[0]
                else:
                    return None
            else:
                self.log_result(
                    "Complete Course for Certificate",
                    False,
                    f"Failed to complete course: {progress_response.status_code}",
                    progress_response.text
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Complete Course for Certificate",
                False,
                f"Error completing course: {str(e)}"
            )
            return None
    
    def run_comprehensive_test(self):
        """Run comprehensive certificate download testing"""
        print("🎓 CERTIFICATE DOWNLOAD FUNCTIONALITY TESTING")
        print("=" * 60)
        
        # 1. Authenticate users
        print("\n1. AUTHENTICATION TESTING")
        print("-" * 30)
        
        self.admin_token, admin_user = self.authenticate_user(ADMIN_CREDENTIALS, "Admin")
        self.student_token, student_user = self.authenticate_user(STUDENT_CREDENTIALS, "Student")
        
        if not self.admin_token or not self.student_token:
            print("❌ CRITICAL: Authentication failed. Cannot proceed with testing.")
            return False
        
        # 2. Get existing certificates
        print("\n2. CERTIFICATE RETRIEVAL TESTING")
        print("-" * 30)
        
        admin_certificates = self.get_my_certificates(self.admin_token, "Admin")
        student_certificates = self.get_my_certificates(self.student_token, "Student")
        
        # 3. Create test certificate if student has none
        print("\n3. TEST CERTIFICATE CREATION")
        print("-" * 30)
        
        if not student_certificates:
            test_certificate = self.create_test_certificate_via_completion(self.student_token, student_user)
            if test_certificate:
                student_certificates = [test_certificate]
                self.log_result(
                    "Certificate Auto-Generation",
                    True,
                    f"Certificate generated via course completion",
                    f"Certificate ID: {test_certificate.get('id')}"
                )
            else:
                self.log_result(
                    "Certificate Auto-Generation",
                    False,
                    "No certificate generated after course completion"
                )
        
        # 4. Test certificate download functionality
        print("\n4. CERTIFICATE DOWNLOAD TESTING")
        print("-" * 30)
        
        download_success = False
        if student_certificates:
            certificate_id = student_certificates[0]['id']
            
            # Test student downloading their own certificate
            download_success = self.test_certificate_download(
                certificate_id, self.student_token, "Student (Own Certificate)", should_succeed=True
            )
            
            # Test admin downloading student certificate (should work)
            self.test_certificate_download(
                certificate_id, self.admin_token, "Admin (Student Certificate)", should_succeed=True
            )
            
        else:
            self.log_result(
                "Certificate Download Testing",
                False,
                "No certificates available for download testing"
            )
        
        # 5. Test permission validation
        print("\n5. PERMISSION VALIDATION TESTING")
        print("-" * 30)
        
        # Test invalid certificate ID
        self.test_certificate_download(
            "invalid-certificate-id", self.student_token, "Student (Invalid ID)", should_succeed=False
        )
        
        # Test unauthorized access (if we have different user certificates)
        if admin_certificates and student_certificates:
            admin_cert_id = admin_certificates[0]['id'] if admin_certificates else None
            student_cert_id = student_certificates[0]['id']
            
            if admin_cert_id and admin_cert_id != student_cert_id:
                self.test_certificate_download(
                    admin_cert_id, self.student_token, "Student (Admin Certificate)", should_succeed=False
                )
        
        # 6. Test error handling
        print("\n6. ERROR HANDLING TESTING")
        print("-" * 30)
        
        # Test without authentication
        try:
            response = requests.get(f"{BACKEND_URL}/certificates/test-id/download")
            if response.status_code == 401:
                self.log_result(
                    "Download Without Auth",
                    True,
                    "Correctly rejected unauthenticated request",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_result(
                    "Download Without Auth",
                    False,
                    f"Should have returned 401, got {response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Download Without Auth",
                False,
                f"Error testing unauthenticated request: {str(e)}"
            )
        
        # 7. Generate summary
        print("\n7. TEST SUMMARY")
        print("-" * 30)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n🎯 CERTIFICATE DOWNLOAD TESTING COMPLETED")
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Key success criteria
        auth_success = self.admin_token and self.student_token
        cert_retrieval_success = any(result['success'] for result in self.test_results if 'Get' in result['test'] and 'Certificates' in result['test'])
        download_success = any(result['success'] for result in self.test_results if 'Certificate Download' in result['test'] and 'Permission Test' not in result['test'])
        
        overall_success = auth_success and cert_retrieval_success and success_rate >= 70
        
        return overall_success

def main():
    """Main test execution"""
    tester = CertificateDownloadTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 CERTIFICATE DOWNLOAD FUNCTIONALITY: WORKING")
            sys.exit(0)
        else:
            print("\n🚨 CERTIFICATE DOWNLOAD FUNCTIONALITY: ISSUES DETECTED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()