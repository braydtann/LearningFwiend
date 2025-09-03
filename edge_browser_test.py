#!/usr/bin/env python3
"""
Edge Browser Compatibility Testing Suite for LearningFwiend LMS Application
Tests backend API compatibility with Microsoft Edge browser characteristics
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://learningfriend-lms.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class EdgeBrowserTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        
        # Edge browser characteristics
        self.edge_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edge/118.0.2088.76"
        ]
        
        self.chrome_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.firefox_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        
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
            self.passed += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def get_edge_headers(self, user_agent_index=0):
        """Get Edge-like headers"""
        return {
            'User-Agent': self.edge_user_agents[user_agent_index],
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def get_chrome_headers(self):
        """Get Chrome-like headers for comparison"""
        return {
            'User-Agent': self.chrome_user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }
    
    def get_firefox_headers(self):
        """Get Firefox-like headers for comparison"""
        return {
            'User-Agent': self.firefox_user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
    
    # =============================================================================
    # EDGE BROWSER COMPATIBILITY TESTS
    # =============================================================================
    
    def test_edge_user_agent_compatibility(self):
        """Test API responses with different Edge user agents"""
        try:
            success_count = 0
            total_tests = len(self.edge_user_agents)
            
            for i, user_agent in enumerate(self.edge_user_agents):
                headers = self.get_edge_headers(i)
                
                response = requests.get(
                    f"{BACKEND_URL}/",
                    headers=headers,
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('message') == 'Hello World':
                        success_count += 1
                        print(f"   ✅ Edge UA {i+1}: {user_agent[:50]}...")
                    else:
                        print(f"   ❌ Edge UA {i+1}: Unexpected response - {data}")
                else:
                    print(f"   ❌ Edge UA {i+1}: Status {response.status_code}")
            
            if success_count == total_tests:
                self.log_result(
                    "Edge User Agent Compatibility",
                    "PASS",
                    f"All {total_tests} Edge user agents work correctly",
                    f"Tested Edge versions: 118, 119, 120"
                )
                return True
            else:
                self.log_result(
                    "Edge User Agent Compatibility",
                    "FAIL",
                    f"Only {success_count}/{total_tests} Edge user agents work",
                    f"Some Edge versions may have compatibility issues"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge User Agent Compatibility",
                "FAIL",
                "Failed to test Edge user agent compatibility",
                str(e)
            )
        return False
    
    def test_cross_browser_api_consistency(self):
        """Test API consistency across Edge, Chrome, and Firefox"""
        try:
            browsers = [
                ("Edge", self.get_edge_headers()),
                ("Chrome", self.get_chrome_headers()),
                ("Firefox", self.get_firefox_headers())
            ]
            
            responses = {}
            
            for browser_name, headers in browsers:
                response = requests.get(
                    f"{BACKEND_URL}/",
                    headers=headers,
                    timeout=TEST_TIMEOUT
                )
                
                responses[browser_name] = {
                    'status_code': response.status_code,
                    'data': response.json() if response.status_code == 200 else None,
                    'headers': dict(response.headers)
                }
            
            # Check if all browsers get the same response
            edge_response = responses.get('Edge')
            chrome_response = responses.get('Chrome')
            firefox_response = responses.get('Firefox')
            
            if (edge_response['status_code'] == chrome_response['status_code'] == firefox_response['status_code'] == 200 and
                edge_response['data'] == chrome_response['data'] == firefox_response['data']):
                
                self.log_result(
                    "Cross-Browser API Consistency",
                    "PASS",
                    "API responses are consistent across Edge, Chrome, and Firefox",
                    f"All browsers received identical responses: {edge_response['data']}"
                )
                return True
            else:
                self.log_result(
                    "Cross-Browser API Consistency",
                    "FAIL",
                    "API responses differ between browsers",
                    f"Edge: {edge_response}, Chrome: {chrome_response}, Firefox: {firefox_response}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Cross-Browser API Consistency",
                "FAIL",
                "Failed to test cross-browser consistency",
                str(e)
            )
        return False
    
    def test_edge_authentication_flow(self):
        """Test authentication flow with Edge headers"""
        try:
            edge_headers = self.get_edge_headers()
            edge_headers['Content-Type'] = 'application/json'
            
            # Test login with Edge headers
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
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
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['edge_admin'] = token
                    
                    # Test authenticated request with Edge headers
                    auth_headers = edge_headers.copy()
                    auth_headers['Authorization'] = f'Bearer {token}'
                    
                    me_response = requests.get(
                        f"{BACKEND_URL}/auth/me",
                        headers=auth_headers,
                        timeout=TEST_TIMEOUT
                    )
                    
                    if me_response.status_code == 200:
                        self.log_result(
                            "Edge Authentication Flow",
                            "PASS",
                            "Edge browser authentication flow works correctly",
                            f"Login successful, token valid, user: {user_info.get('email')}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Edge Authentication Flow",
                            "FAIL",
                            f"Token validation failed with Edge headers: {me_response.status_code}",
                            f"Response: {me_response.text}"
                        )
                else:
                    self.log_result(
                        "Edge Authentication Flow",
                        "FAIL",
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Edge Authentication Flow",
                    "FAIL",
                    f"Edge login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge Authentication Flow",
                "FAIL",
                "Failed to test Edge authentication flow",
                str(e)
            )
        return False
    
    def test_edge_courses_api(self):
        """Test courses API with Edge headers - the main issue reported"""
        if "edge_admin" not in self.auth_tokens:
            # Try to authenticate first
            if not self.test_edge_authentication_flow():
                self.log_result(
                    "Edge Courses API Test",
                    "SKIP",
                    "No Edge admin token available",
                    "Authentication required first"
                )
                return False
        
        try:
            edge_headers = self.get_edge_headers()
            edge_headers['Authorization'] = f'Bearer {self.auth_tokens["edge_admin"]}'
            
            # Test GET /api/courses with Edge headers
            response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                # Compare with Chrome request
                chrome_headers = self.get_chrome_headers()
                chrome_headers['Authorization'] = f'Bearer {self.auth_tokens["edge_admin"]}'
                
                chrome_response = requests.get(
                    f"{BACKEND_URL}/courses",
                    headers=chrome_headers,
                    timeout=TEST_TIMEOUT
                )
                
                if chrome_response.status_code == 200:
                    chrome_courses = chrome_response.json()
                    
                    if len(courses) == len(chrome_courses):
                        self.log_result(
                            "Edge Courses API Test",
                            "PASS",
                            f"Edge and Chrome get same courses data: {len(courses)} courses",
                            f"Edge courses: {[c.get('title', 'No title') for c in courses[:3]]}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Edge Courses API Test",
                            "FAIL",
                            f"Edge gets {len(courses)} courses, Chrome gets {len(chrome_courses)}",
                            f"Course count mismatch indicates Edge-specific issue"
                        )
                else:
                    self.log_result(
                        "Edge Courses API Test",
                        "FAIL",
                        f"Chrome courses request failed: {chrome_response.status_code}",
                        "Cannot compare Edge vs Chrome"
                    )
            else:
                self.log_result(
                    "Edge Courses API Test",
                    "FAIL",
                    f"Edge courses request failed: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge Courses API Test",
                "FAIL",
                "Failed to test Edge courses API",
                str(e)
            )
        return False
    
    def test_edge_cors_handling(self):
        """Test CORS handling with Edge-specific headers"""
        try:
            edge_headers = self.get_edge_headers()
            edge_headers['Origin'] = 'https://learningfriend-lms.preview.emergentagent.com'
            
            # Test preflight request (OPTIONS)
            options_response = requests.options(
                f"{BACKEND_URL}/courses",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            cors_headers = {
                'access-control-allow-origin': options_response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': options_response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': options_response.headers.get('access-control-allow-headers'),
                'access-control-allow-credentials': options_response.headers.get('access-control-allow-credentials')
            }
            
            # Test actual request with CORS headers
            get_response = requests.get(
                f"{BACKEND_URL}/",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            if (options_response.status_code in [200, 204] and 
                get_response.status_code == 200 and
                cors_headers['access-control-allow-origin']):
                
                self.log_result(
                    "Edge CORS Handling",
                    "PASS",
                    "Edge CORS requests handled correctly",
                    f"CORS headers: {cors_headers}"
                )
                return True
            else:
                self.log_result(
                    "Edge CORS Handling",
                    "FAIL",
                    f"CORS issues detected - OPTIONS: {options_response.status_code}, GET: {get_response.status_code}",
                    f"CORS headers: {cors_headers}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge CORS Handling",
                "FAIL",
                "Failed to test Edge CORS handling",
                str(e)
            )
        return False
    
    def test_edge_json_parsing(self):
        """Test JSON response parsing with Edge characteristics"""
        try:
            edge_headers = self.get_edge_headers()
            edge_headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'  # Edge-specific Accept header
            
            response = requests.get(
                f"{BACKEND_URL}/",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    content_type = response.headers.get('content-type', '')
                    
                    if 'application/json' in content_type and data.get('message') == 'Hello World':
                        self.log_result(
                            "Edge JSON Parsing",
                            "PASS",
                            "Edge JSON parsing works correctly",
                            f"Content-Type: {content_type}, Data: {data}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Edge JSON Parsing",
                            "FAIL",
                            f"JSON parsing issue - Content-Type: {content_type}",
                            f"Data: {data}"
                        )
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Edge JSON Parsing",
                        "FAIL",
                        "JSON decode error with Edge headers",
                        f"JSONDecodeError: {str(e)}, Response text: {response.text[:200]}"
                    )
            else:
                self.log_result(
                    "Edge JSON Parsing",
                    "FAIL",
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge JSON Parsing",
                "FAIL",
                "Failed to test Edge JSON parsing",
                str(e)
            )
        return False
    
    def test_edge_token_storage_simulation(self):
        """Test token handling that simulates Edge localStorage behavior"""
        if "edge_admin" not in self.auth_tokens:
            if not self.test_edge_authentication_flow():
                self.log_result(
                    "Edge Token Storage Simulation",
                    "SKIP",
                    "No Edge admin token available",
                    "Authentication required first"
                )
                return False
        
        try:
            token = self.auth_tokens["edge_admin"]
            
            # Simulate Edge token storage/retrieval patterns
            edge_headers = self.get_edge_headers()
            
            # Test 1: Token with Bearer prefix (standard)
            edge_headers['Authorization'] = f'Bearer {token}'
            response1 = requests.get(f"{BACKEND_URL}/auth/me", headers=edge_headers, timeout=TEST_TIMEOUT)
            
            # Test 2: Token without Bearer prefix (Edge might do this)
            edge_headers['Authorization'] = token
            response2 = requests.get(f"{BACKEND_URL}/auth/me", headers=edge_headers, timeout=TEST_TIMEOUT)
            
            # Test 3: Token with extra whitespace (Edge localStorage quirk)
            edge_headers['Authorization'] = f'Bearer  {token}  '
            response3 = requests.get(f"{BACKEND_URL}/auth/me", headers=edge_headers, timeout=TEST_TIMEOUT)
            
            results = [
                ("Bearer prefix", response1.status_code == 200),
                ("No Bearer prefix", response2.status_code == 200),
                ("Extra whitespace", response3.status_code == 200)
            ]
            
            successful_tests = [r for r in results if r[1]]
            
            if len(successful_tests) >= 1:  # At least standard Bearer should work
                self.log_result(
                    "Edge Token Storage Simulation",
                    "PASS",
                    f"Token handling works: {len(successful_tests)}/3 formats",
                    f"Working formats: {[r[0] for r in successful_tests]}"
                )
                return True
            else:
                self.log_result(
                    "Edge Token Storage Simulation",
                    "FAIL",
                    "No token formats work with Edge headers",
                    f"All formats failed: {results}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge Token Storage Simulation",
                "FAIL",
                "Failed to test Edge token storage simulation",
                str(e)
            )
        return False
    
    def test_edge_specific_course_loading(self):
        """Test specific course loading scenarios that might fail in Edge"""
        if "edge_admin" not in self.auth_tokens:
            if not self.test_edge_authentication_flow():
                self.log_result(
                    "Edge Course Loading Test",
                    "SKIP",
                    "No Edge admin token available",
                    "Authentication required first"
                )
                return False
        
        try:
            edge_headers = self.get_edge_headers()
            edge_headers['Authorization'] = f'Bearer {self.auth_tokens["edge_admin"]}'
            
            # Test 1: Get all courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Edge Course Loading Test",
                    "FAIL",
                    f"Failed to get courses list: {courses_response.status_code}",
                    f"Response: {courses_response.text}"
                )
                return False
            
            courses = courses_response.json()
            
            if not courses:
                # Create a test course first
                course_data = {
                    "title": "Edge Compatibility Test Course",
                    "description": "Testing course loading in Microsoft Edge browser",
                    "category": "Testing",
                    "duration": "1 hour",
                    "accessType": "open"
                }
                
                create_response = requests.post(
                    f"{BACKEND_URL}/courses",
                    json=course_data,
                    headers=edge_headers,
                    timeout=TEST_TIMEOUT
                )
                
                if create_response.status_code == 200:
                    created_course = create_response.json()
                    courses = [created_course]
                else:
                    self.log_result(
                        "Edge Course Loading Test",
                        "FAIL",
                        f"Failed to create test course: {create_response.status_code}",
                        f"Response: {create_response.text}"
                    )
                    return False
            
            # Test 2: Get individual course details
            test_course = courses[0]
            course_id = test_course.get('id')
            
            course_detail_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                headers=edge_headers,
                timeout=TEST_TIMEOUT
            )
            
            if course_detail_response.status_code == 200:
                course_detail = course_detail_response.json()
                
                # Verify course data integrity
                if (course_detail.get('id') == course_id and 
                    course_detail.get('title') and 
                    course_detail.get('description')):
                    
                    self.log_result(
                        "Edge Course Loading Test",
                        "PASS",
                        f"Edge course loading works correctly - {len(courses)} courses available",
                        f"Test course: {course_detail.get('title')}, ID: {course_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Edge Course Loading Test",
                        "FAIL",
                        "Course data integrity issues with Edge",
                        f"Missing fields in course detail: {course_detail}"
                    )
            else:
                self.log_result(
                    "Edge Course Loading Test",
                    "FAIL",
                    f"Failed to get course details: {course_detail_response.status_code}",
                    f"Response: {course_detail_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Edge Course Loading Test",
                "FAIL",
                "Failed to test Edge course loading",
                str(e)
            )
        return False
    
    def test_edge_network_request_patterns(self):
        """Test Edge-specific network request patterns"""
        try:
            edge_headers = self.get_edge_headers()
            
            # Test 1: Edge connection keep-alive behavior
            session = requests.Session()
            session.headers.update(edge_headers)
            
            responses = []
            for i in range(3):
                response = session.get(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
                responses.append(response.status_code)
                time.sleep(0.5)
            
            # Test 2: Edge request timing
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}/", headers=edge_headers, timeout=TEST_TIMEOUT)
            request_time = time.time() - start_time
            
            # Test 3: Edge concurrent requests
            import threading
            concurrent_results = []
            
            def make_request():
                try:
                    resp = requests.get(f"{BACKEND_URL}/", headers=edge_headers, timeout=TEST_TIMEOUT)
                    concurrent_results.append(resp.status_code)
                except:
                    concurrent_results.append(0)
            
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Evaluate results
            keep_alive_success = all(status == 200 for status in responses)
            timing_ok = request_time < 5.0  # Should be fast
            concurrent_success = all(status == 200 for status in concurrent_results)
            
            if keep_alive_success and timing_ok and concurrent_success:
                self.log_result(
                    "Edge Network Request Patterns",
                    "PASS",
                    "Edge network patterns work correctly",
                    f"Keep-alive: {responses}, Timing: {request_time:.2f}s, Concurrent: {concurrent_results}"
                )
                return True
            else:
                self.log_result(
                    "Edge Network Request Patterns",
                    "FAIL",
                    "Edge network pattern issues detected",
                    f"Keep-alive OK: {keep_alive_success}, Timing OK: {timing_ok}, Concurrent OK: {concurrent_success}"
                )
        except Exception as e:
            self.log_result(
                "Edge Network Request Patterns",
                "FAIL",
                "Failed to test Edge network patterns",
                str(e)
            )
        return False
    
    def run_all_tests(self):
        """Run all Edge browser compatibility tests"""
        print("🔍 Starting Edge Browser Compatibility Testing...")
        print("=" * 80)
        
        # Core compatibility tests
        self.test_edge_user_agent_compatibility()
        self.test_cross_browser_api_consistency()
        self.test_edge_cors_handling()
        self.test_edge_json_parsing()
        
        # Authentication and token handling
        self.test_edge_authentication_flow()
        self.test_edge_token_storage_simulation()
        
        # Course loading - the main reported issue
        self.test_edge_courses_api()
        self.test_edge_specific_course_loading()
        
        # Network patterns
        self.test_edge_network_request_patterns()
        
        # Summary
        print("\n" + "=" * 80)
        print(f"🏁 Edge Browser Compatibility Testing Complete")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print("\n🚨 EDGE COMPATIBILITY ISSUES DETECTED:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        else:
            print("\n🎉 ALL EDGE COMPATIBILITY TESTS PASSED!")
        
        return self.failed == 0

def main():
    """Main function to run Edge browser compatibility tests"""
    tester = EdgeBrowserTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()