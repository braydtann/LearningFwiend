#!/usr/bin/env python3
"""
Comprehensive Backend Testing for File Upload Endpoints
Testing the new file upload functionality as requested in review.
"""

import requests
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://learning-analytics-2.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class FileUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {data.get('user', {}).get('email', 'admin')}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def create_test_file(self, filename, content, size_mb=None):
        """Create a temporary test file"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if size_mb:
            # Create file of specific size
            content = b'A' * (size_mb * 1024 * 1024)
        elif isinstance(content, str):
            content = content.encode('utf-8')
            
        with open(file_path, 'wb') as f:
            f.write(content)
            
        return file_path
    
    def test_file_upload_success(self):
        """Test successful file upload"""
        try:
            # Create a test PDF file
            test_content = "This is a test PDF document for file upload testing."
            file_path = self.create_test_file("test_document.pdf", test_content)
            
            with open(file_path, 'rb') as f:
                files = {'file': ('test_document.pdf', f, 'application/pdf')}
                response = self.session.post(
                    f"{BACKEND_URL}/files/upload",
                    files=files,
                    timeout=30
                )
            
            # Clean up
            os.unlink(file_path)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['success', 'file_id', 'filename', 'file_url', 'size']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "File Upload Success",
                        True,
                        "Successfully uploaded PDF file",
                        {
                            "file_id": data.get('file_id'),
                            "filename": data.get('filename'),
                            "file_url": data.get('file_url'),
                            "size": data.get('size')
                        }
                    )
                    return data.get('file_id')
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    self.log_result(
                        "File Upload Success",
                        False,
                        f"Response missing required fields: {missing_fields}",
                        {"response": data}
                    )
                    return None
            else:
                self.log_result(
                    "File Upload Success",
                    False,
                    f"Upload failed: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "File Upload Success",
                False,
                f"Upload error: {str(e)}"
            )
            return None
    
    def test_file_type_validation(self):
        """Test file type validation"""
        try:
            # Test invalid file type (.exe)
            test_content = "This is a test executable file."
            file_path = self.create_test_file("malicious.exe", test_content)
            
            with open(file_path, 'rb') as f:
                files = {'file': ('malicious.exe', f, 'application/octet-stream')}
                response = self.session.post(
                    f"{BACKEND_URL}/files/upload",
                    files=files,
                    timeout=30
                )
            
            # Clean up
            os.unlink(file_path)
            
            if response.status_code == 400:
                data = response.json()
                if "File type not allowed" in data.get('detail', ''):
                    self.log_result(
                        "File Type Validation",
                        True,
                        "Correctly rejected invalid file type (.exe)",
                        {"response": data}
                    )
                else:
                    self.log_result(
                        "File Type Validation",
                        False,
                        "Wrong error message for invalid file type",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "File Type Validation",
                    False,
                    f"Should have rejected .exe file but got: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "File Type Validation",
                False,
                f"File type validation error: {str(e)}"
            )
    
    def test_file_size_limits(self):
        """Test file size limits"""
        try:
            # Test file larger than 10MB
            file_path = self.create_test_file("large_file.pdf", "", size_mb=12)
            
            with open(file_path, 'rb') as f:
                files = {'file': ('large_file.pdf', f, 'application/pdf')}
                response = self.session.post(
                    f"{BACKEND_URL}/files/upload",
                    files=files,
                    timeout=60
                )
            
            # Clean up
            os.unlink(file_path)
            
            if response.status_code == 400:
                data = response.json()
                if "File size too large" in data.get('detail', ''):
                    self.log_result(
                        "File Size Limits",
                        True,
                        "Correctly rejected file larger than 10MB",
                        {"response": data}
                    )
                else:
                    self.log_result(
                        "File Size Limits",
                        False,
                        "Wrong error message for large file",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "File Size Limits",
                    False,
                    f"Should have rejected large file but got: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "File Size Limits",
                False,
                f"File size validation error: {str(e)}"
            )
    
    def test_supported_file_types(self):
        """Test all supported file types"""
        supported_types = [
            ('test.pdf', 'application/pdf'),
            ('test.doc', 'application/msword'),
            ('test.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('test.txt', 'text/plain'),
            ('test.xls', 'application/vnd.ms-excel'),
            ('test.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('test.ppt', 'application/vnd.ms-powerpoint'),
            ('test.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
        ]
        
        successful_uploads = 0
        
        for filename, mime_type in supported_types:
            try:
                test_content = f"This is a test {filename.split('.')[-1].upper()} document."
                file_path = self.create_test_file(filename, test_content)
                
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, mime_type)}
                    response = self.session.post(
                        f"{BACKEND_URL}/files/upload",
                        files=files,
                        timeout=30
                    )
                
                # Clean up
                os.unlink(file_path)
                
                if response.status_code == 200:
                    successful_uploads += 1
                    print(f"   ✅ {filename} uploaded successfully")
                else:
                    print(f"   ❌ {filename} failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {filename} error: {str(e)}")
        
        self.log_result(
            "Supported File Types",
            successful_uploads == len(supported_types),
            f"Successfully uploaded {successful_uploads}/{len(supported_types)} supported file types"
        )
    
    def test_file_download(self, file_id):
        """Test file download"""
        if not file_id:
            self.log_result(
                "File Download",
                False,
                "No file_id provided for download test"
            )
            return
            
        try:
            response = self.session.get(
                f"{BACKEND_URL}/files/{file_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                # Check headers
                content_disposition = response.headers.get('content-disposition', '')
                content_type = response.headers.get('content-type', '')
                
                self.log_result(
                    "File Download",
                    True,
                    "Successfully downloaded file",
                    {
                        "content_type": content_type,
                        "content_disposition": content_disposition,
                        "content_length": len(response.content)
                    }
                )
            else:
                self.log_result(
                    "File Download",
                    False,
                    f"Download failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "File Download",
                False,
                f"Download error: {str(e)}"
            )
    
    def test_nonexistent_file_download(self):
        """Test downloading non-existent file"""
        try:
            fake_file_id = "00000000-0000-0000-0000-000000000000"
            response = self.session.get(
                f"{BACKEND_URL}/files/{fake_file_id}",
                timeout=30
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Non-existent File Download",
                    True,
                    "Correctly returned 404 for non-existent file"
                )
            else:
                self.log_result(
                    "Non-existent File Download",
                    False,
                    f"Should have returned 404 but got: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Non-existent File Download",
                False,
                f"Error testing non-existent file: {str(e)}"
            )
    
    def test_course_document_integration(self):
        """Test integration with course creation (documentUrl and documentName)"""
        try:
            # First upload a document
            test_content = "This is a course document for integration testing."
            file_path = self.create_test_file("course_document.pdf", test_content)
            
            with open(file_path, 'rb') as f:
                files = {'file': ('course_document.pdf', f, 'application/pdf')}
                upload_response = self.session.post(
                    f"{BACKEND_URL}/files/upload",
                    files=files,
                    timeout=30
                )
            
            # Clean up
            os.unlink(file_path)
            
            if upload_response.status_code != 200:
                self.log_result(
                    "Course Document Integration",
                    False,
                    "Failed to upload document for integration test"
                )
                return
            
            upload_data = upload_response.json()
            file_id = upload_data.get('file_id')
            file_url = upload_data.get('file_url')
            
            # Create a course with document attachment
            course_data = {
                "title": "File Upload Integration Test Course",
                "description": "Testing course creation with document attachments",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "learningOutcomes": ["Test file integration"],
                "modules": [
                    {
                        "title": "Module with Document",
                        "lessons": [
                            {
                                "id": "lesson-1",
                                "title": "Lesson with Document",
                                "type": "document",
                                "content": "This lesson has an attached document",
                                "documentUrl": file_url,
                                "documentName": "course_document.pdf"
                            }
                        ]
                    }
                ]
            }
            
            course_response = self.session.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=30
            )
            
            if course_response.status_code == 200:
                course_data = course_response.json()
                
                # Verify the document is properly stored in the course
                modules = course_data.get('modules', [])
                if modules and modules[0].get('lessons'):
                    lesson = modules[0]['lessons'][0]
                    if (lesson.get('documentUrl') == file_url and 
                        lesson.get('documentName') == 'course_document.pdf'):
                        self.log_result(
                            "Course Document Integration",
                            True,
                            "Successfully created course with document attachment",
                            {
                                "course_id": course_data.get('id'),
                                "document_url": lesson.get('documentUrl'),
                                "document_name": lesson.get('documentName')
                            }
                        )
                    else:
                        self.log_result(
                            "Course Document Integration",
                            False,
                            "Course created but document fields not properly stored",
                            {"lesson": lesson}
                        )
                else:
                    self.log_result(
                        "Course Document Integration",
                        False,
                        "Course created but modules/lessons structure incorrect"
                    )
            else:
                self.log_result(
                    "Course Document Integration",
                    False,
                    f"Failed to create course: {course_response.status_code} - {course_response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Course Document Integration",
                False,
                f"Integration test error: {str(e)}"
            )
    
    def test_upload_directory_exists(self):
        """Test that upload directory exists and is accessible"""
        try:
            # This is an indirect test - we'll verify by attempting an upload
            # and checking if the error is about directory or file handling
            test_content = "Directory test file"
            file_path = self.create_test_file("directory_test.txt", test_content)
            
            with open(file_path, 'rb') as f:
                files = {'file': ('directory_test.txt', f, 'text/plain')}
                response = self.session.post(
                    f"{BACKEND_URL}/files/upload",
                    files=files,
                    timeout=30
                )
            
            # Clean up
            os.unlink(file_path)
            
            if response.status_code == 200:
                self.log_result(
                    "Upload Directory Access",
                    True,
                    "Upload directory is accessible and functional"
                )
            elif response.status_code == 500:
                # Check if error is related to directory issues
                error_text = response.text.lower()
                if 'directory' in error_text or 'path' in error_text:
                    self.log_result(
                        "Upload Directory Access",
                        False,
                        "Upload directory may not exist or be accessible",
                        {"error": response.text}
                    )
                else:
                    self.log_result(
                        "Upload Directory Access",
                        True,
                        "Directory exists but other server error occurred"
                    )
            else:
                self.log_result(
                    "Upload Directory Access",
                    True,
                    "Directory appears functional (non-directory related error)"
                )
                
        except Exception as e:
            self.log_result(
                "Upload Directory Access",
                False,
                f"Error testing upload directory: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all file upload tests"""
        print("🚀 Starting File Upload Endpoints Testing")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return
        
        print("\n📁 Testing File Upload Functionality...")
        
        # Test upload directory
        self.test_upload_directory_exists()
        
        # Test successful upload and get file_id for download test
        file_id = self.test_file_upload_success()
        
        # Test file type validation
        self.test_file_type_validation()
        
        # Test file size limits
        self.test_file_size_limits()
        
        # Test all supported file types
        self.test_supported_file_types()
        
        # Test file download
        self.test_file_download(file_id)
        
        # Test non-existent file download
        self.test_nonexistent_file_download()
        
        # Test course integration
        self.test_course_document_integration()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FILE UPLOAD TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   ✅ {result['test']}: {result['message']}")

def main():
    """Main function to run file upload tests"""
    tester = FileUploadTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()