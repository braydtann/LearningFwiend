#!/usr/bin/env python3
"""
Specific Edge Course Loading Issue Investigation
Deep dive into the reported issue: "Courses are showing up in Chrome and Firefox but not in Microsoft Edge"
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-rebuild.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class EdgeCourseLoadingTester:
    def __init__(self):
        self.results = []
        self.auth_tokens = {}
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.results.append(result)
        
        if status == 'PASS':
            print(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            print(f"❌ {test_name}: {message}")
        else:
            print(f"ℹ️  {test_name}: {message}")
            
        if details:
            print(f"   Details: {details}")
    
    def authenticate_as_different_users(self):
        """Authenticate as different user types to test course visibility"""
        users = [
            ("admin", "brayden.t@covesmart.com", "Hawaii2020!"),
            ("instructor", "instructor", "Instructor123!"),
            ("student", "student", "Student123!")
        ]
        
        for role, username, password in users:
            try:
                login_data = {
                    "username_or_email": username,
                    "password": password
                }
                
                # Test with Edge-like headers
                edge_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/plain, */*',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    headers=edge_headers,
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    if token:
                        self.auth_tokens[role] = token
                        self.log_result(
                            f"Edge Authentication - {role.title()}",
                            "PASS",
                            f"Successfully authenticated as {role}",
                            f"User: {username}, Token length: {len(token)}"
                        )
                    else:
                        self.log_result(
                            f"Edge Authentication - {role.title()}",
                            "FAIL",
                            f"No token received for {role}",
                            f"Response: {data}"
                        )
                else:
                    self.log_result(
                        f"Edge Authentication - {role.title()}",
                        "FAIL",
                        f"Authentication failed for {role}: {response.status_code}",
                        f"Response: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    f"Edge Authentication - {role.title()}",
                    "FAIL",
                    f"Exception during {role} authentication",
                    str(e)
                )
    
    def test_course_loading_by_user_type(self):
        """Test course loading for different user types with Edge headers"""
        edge_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        for role, token in self.auth_tokens.items():
            try:
                auth_headers = edge_headers.copy()
                auth_headers['Authorization'] = f'Bearer {token}'
                
                # Test GET /api/courses
                response = requests.get(
                    f"{BACKEND_URL}/courses",
                    headers=auth_headers,
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    courses = response.json()
                    
                    # Test course data structure
                    course_issues = []
                    for i, course in enumerate(courses[:3]):  # Check first 3 courses
                        required_fields = ['id', 'title', 'description', 'instructor']
                        missing_fields = [field for field in required_fields if not course.get(field)]
                        if missing_fields:
                            course_issues.append(f"Course {i+1} missing: {missing_fields}")
                    
                    if not course_issues:
                        self.log_result(
                            f"Edge Course Loading - {role.title()}",
                            "PASS",
                            f"{role.title()} can load {len(courses)} courses with Edge",
                            f"Sample courses: {[c.get('title', 'No title')[:30] for c in courses[:3]]}"
                        )
                    else:
                        self.log_result(
                            f"Edge Course Loading - {role.title()}",
                            "FAIL",
                            f"Course data structure issues for {role}",
                            f"Issues: {course_issues}"
                        )
                else:
                    self.log_result(
                        f"Edge Course Loading - {role.title()}",
                        "FAIL",
                        f"Failed to load courses for {role}: {response.status_code}",
                        f"Response: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    f"Edge Course Loading - {role.title()}",
                    "FAIL",
                    f"Exception during course loading for {role}",
                    str(e)
                )
    
    def test_edge_vs_chrome_course_responses(self):
        """Compare course responses between Edge and Chrome headers"""
        if 'admin' not in self.auth_tokens:
            self.log_result(
                "Edge vs Chrome Comparison",
                "SKIP",
                "No admin token available",
                "Authentication required"
            )
            return
        
        token = self.auth_tokens['admin']
        
        # Edge headers
        edge_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {token}',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"'
        }
        
        # Chrome headers
        chrome_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {token}'
        }
        
        try:
            # Get courses with Edge headers
            edge_response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            # Get courses with Chrome headers
            chrome_response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=chrome_headers,
                timeout=TEST_TIMEOUT
            )
            
            if edge_response.status_code == 200 and chrome_response.status_code == 200:
                edge_courses = edge_response.json()
                chrome_courses = chrome_response.json()
                
                # Compare responses
                edge_count = len(edge_courses)
                chrome_count = len(chrome_courses)
                
                if edge_count == chrome_count:
                    # Check if course data is identical
                    edge_ids = set(c.get('id') for c in edge_courses)
                    chrome_ids = set(c.get('id') for c in chrome_courses)
                    
                    if edge_ids == chrome_ids:
                        self.log_result(
                            "Edge vs Chrome Comparison",
                            "PASS",
                            f"Edge and Chrome get identical course data: {edge_count} courses",
                            f"Response times - Edge: {edge_response.elapsed.total_seconds():.3f}s, Chrome: {chrome_response.elapsed.total_seconds():.3f}s"
                        )
                    else:
                        self.log_result(
                            "Edge vs Chrome Comparison",
                            "FAIL",
                            "Edge and Chrome get different courses",
                            f"Edge IDs: {list(edge_ids)[:3]}, Chrome IDs: {list(chrome_ids)[:3]}"
                        )
                else:
                    self.log_result(
                        "Edge vs Chrome Comparison",
                        "FAIL",
                        f"Course count mismatch - Edge: {edge_count}, Chrome: {chrome_count}",
                        f"This indicates the reported Edge issue exists"
                    )
            else:
                self.log_result(
                    "Edge vs Chrome Comparison",
                    "FAIL",
                    f"Request failures - Edge: {edge_response.status_code}, Chrome: {chrome_response.status_code}",
                    f"Edge response: {edge_response.text[:200]}, Chrome response: {chrome_response.text[:200]}"
                )
        except Exception as e:
            self.log_result(
                "Edge vs Chrome Comparison",
                "FAIL",
                "Exception during comparison",
                str(e)
            )
    
    def test_edge_specific_headers_impact(self):
        """Test if specific Edge headers cause issues"""
        if 'admin' not in self.auth_tokens:
            return
        
        token = self.auth_tokens['admin']
        base_headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json, text/plain, */*'
        }
        
        # Test different Edge-specific header combinations
        header_tests = [
            ("Basic", {}),
            ("Edge User-Agent", {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
            }),
            ("Edge sec-ch-ua", {
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }),
            ("Edge Accept-Language", {
                'Accept-Language': 'en-US,en;q=0.9'
            }),
            ("Full Edge Headers", {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br'
            })
        ]
        
        results = []
        for test_name, extra_headers in header_tests:
            try:
                headers = base_headers.copy()
                headers.update(extra_headers)
                
                response = requests.get(
                    f"{BACKEND_URL}/courses",
                    headers=headers,
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    courses = response.json()
                    results.append((test_name, len(courses), "SUCCESS"))
                else:
                    results.append((test_name, 0, f"FAILED-{response.status_code}"))
            except Exception as e:
                results.append((test_name, 0, f"ERROR-{str(e)[:50]}"))
        
        # Analyze results
        course_counts = [r[1] for r in results if r[2] == "SUCCESS"]
        if course_counts and all(count == course_counts[0] for count in course_counts):
            self.log_result(
                "Edge Headers Impact Test",
                "PASS",
                f"All Edge header combinations work consistently: {course_counts[0]} courses",
                f"Test results: {results}"
            )
        else:
            self.log_result(
                "Edge Headers Impact Test",
                "FAIL",
                "Edge headers cause inconsistent results",
                f"Test results: {results}"
            )
    
    def test_course_detail_loading(self):
        """Test individual course detail loading with Edge"""
        if 'admin' not in self.auth_tokens:
            return
        
        token = self.auth_tokens['admin']
        edge_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json, text/plain, */*'
        }
        
        try:
            # First get courses list
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            if courses_response.status_code == 200:
                courses = courses_response.json()
                if courses:
                    # Test loading individual course details
                    test_course = courses[0]
                    course_id = test_course.get('id')
                    
                    detail_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        headers=edge_headers,
                        timeout=TEST_TIMEOUT
                    )
                    
                    if detail_response.status_code == 200:
                        course_detail = detail_response.json()
                        
                        # Verify course detail completeness
                        required_fields = ['id', 'title', 'description', 'instructor', 'modules']
                        missing_fields = [field for field in required_fields if field not in course_detail]
                        
                        if not missing_fields:
                            self.log_result(
                                "Edge Course Detail Loading",
                                "PASS",
                                f"Course detail loading works with Edge",
                                f"Course: {course_detail.get('title')}, Modules: {len(course_detail.get('modules', []))}"
                            )
                        else:
                            self.log_result(
                                "Edge Course Detail Loading",
                                "FAIL",
                                f"Course detail missing fields: {missing_fields}",
                                f"Course data: {course_detail}"
                            )
                    else:
                        self.log_result(
                            "Edge Course Detail Loading",
                            "FAIL",
                            f"Failed to load course detail: {detail_response.status_code}",
                            f"Response: {detail_response.text}"
                        )
                else:
                    self.log_result(
                        "Edge Course Detail Loading",
                        "SKIP",
                        "No courses available to test detail loading",
                        "Need courses in database"
                    )
            else:
                self.log_result(
                    "Edge Course Detail Loading",
                    "FAIL",
                    f"Failed to get courses list: {courses_response.status_code}",
                    f"Response: {courses_response.text}"
                )
        except Exception as e:
            self.log_result(
                "Edge Course Detail Loading",
                "FAIL",
                "Exception during course detail loading test",
                str(e)
            )
    
    def run_investigation(self):
        """Run the complete Edge course loading investigation"""
        print("🔍 EDGE COURSE LOADING ISSUE INVESTIGATION")
        print("=" * 80)
        print("Problem: Courses showing in Chrome/Firefox but not in Microsoft Edge")
        print("Testing backend API compatibility with Edge browser characteristics...")
        print()
        
        # Step 1: Authenticate as different users
        print("📋 Step 1: Authentication Testing")
        self.authenticate_as_different_users()
        print()
        
        # Step 2: Test course loading by user type
        print("📋 Step 2: Course Loading by User Type")
        self.test_course_loading_by_user_type()
        print()
        
        # Step 3: Compare Edge vs Chrome responses
        print("📋 Step 3: Edge vs Chrome Response Comparison")
        self.test_edge_vs_chrome_course_responses()
        print()
        
        # Step 4: Test Edge-specific headers impact
        print("📋 Step 4: Edge Headers Impact Analysis")
        self.test_edge_specific_headers_impact()
        print()
        
        # Step 5: Test course detail loading
        print("📋 Step 5: Course Detail Loading Test")
        self.test_course_detail_loading()
        print()
        
        # Summary
        print("=" * 80)
        print("🏁 INVESTIGATION COMPLETE")
        
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        passed_tests = [r for r in self.results if r['status'] == 'PASS']
        
        print(f"✅ Passed: {len(passed_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        
        if failed_tests:
            print("\n🚨 POTENTIAL EDGE COMPATIBILITY ISSUES:")
            for result in failed_tests:
                print(f"   • {result['test']}: {result['message']}")
        else:
            print("\n🎉 NO BACKEND EDGE COMPATIBILITY ISSUES FOUND!")
            print("The course loading issue may be frontend-related.")
        
        return len(failed_tests) == 0

def main():
    tester = EdgeCourseLoadingTester()
    tester.run_investigation()

if __name__ == "__main__":
    main()