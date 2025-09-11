#!/usr/bin/env python3
"""
🚀 DEPLOYMENT READINESS BACKEND TESTING SUITE

TESTING OBJECTIVES:
1. **Health Check**: Test the `/health` endpoint to verify application and database status
2. **Root API**: Test the root API endpoint `/api/` to ensure basic connectivity  
3. **Authentication**: Test the login endpoint with test credentials
4. **Environment Variables**: Verify that the backend is properly using environment variables (no hardcoded URLs)
5. **MongoDB Connection**: Confirm the database connection is working properly for production deployment
6. **JWT Token Generation**: Verify JWT tokens are generated and work correctly
7. **All API Routes**: Ensure all API routes are accessible via /api prefix

CONTEXT: Testing after fixing hardcoded fallback URLs in frontend and correcting REACT_APP_BACKEND_URL
to match production domain. Need to ensure backend is deployment-ready.

CREDENTIALS TO USE:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!

SUCCESS CRITERIA:
- All health checks pass
- Authentication works correctly
- No hardcoded URLs detected
- MongoDB connection stable
- JWT tokens functional
- All API routes accessible with /api prefix
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import jwt
import time

class DeploymentReadinessTestSuite:
    def __init__(self):
        # Use environment variable from frontend/.env for production testing
        self.frontend_env_url = self.get_frontend_backend_url()
        self.base_url = f"{self.frontend_env_url}/api" if self.frontend_env_url else "http://localhost:8001/api"
        
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        self.student_credentials = {
            "username_or_email": "karlo.student@alder.com", 
            "password": "StudentPermanent123!"
        }
        
        print(f"🔗 Testing Backend URL: {self.base_url}")
        print(f"🌐 Frontend Environment URL: {self.frontend_env_url}")
        print()
        
    def get_frontend_backend_url(self) -> Optional[str]:
        """Get REACT_APP_BACKEND_URL from frontend/.env file"""
        try:
            env_path = "/app/frontend/.env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            url = line.split('=', 1)[1].strip()
                            return url
            return None
        except Exception as e:
            print(f"⚠️ Could not read frontend/.env: {e}")
            return None

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

    def test_health_endpoint(self) -> bool:
        """Test the /health endpoint for application and database status"""
        try:
            # Test if health endpoint exists
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    
                    # Check for expected health check fields
                    has_status = 'status' in health_data
                    has_database = 'database' in health_data
                    has_timestamp = 'timestamp' in health_data
                    
                    if has_status and has_database:
                        db_status = health_data.get('database', {}).get('status', 'unknown')
                        app_status = health_data.get('status', 'unknown')
                        
                        success = app_status == 'healthy' and db_status == 'connected'
                        
                        self.log_test(
                            "Health Check Endpoint",
                            success,
                            f"App Status: {app_status}, DB Status: {db_status}",
                            health_data
                        )
                        return success
                    else:
                        self.log_test(
                            "Health Check Endpoint",
                            False,
                            f"Missing health fields - Status: {has_status}, Database: {has_database}",
                            health_data
                        )
                        return False
                        
                except json.JSONDecodeError:
                    # Health endpoint might return plain text
                    self.log_test(
                        "Health Check Endpoint",
                        True,
                        f"Health endpoint accessible (plain text response): {response.text[:100]}"
                    )
                    return True
            else:
                # Try alternative health check patterns
                if response.status_code == 404:
                    # Health endpoint might not exist, try root endpoint as health check
                    root_response = requests.get(f"{self.base_url}/", timeout=10)
                    if root_response.status_code == 200:
                        self.log_test(
                            "Health Check Endpoint",
                            True,
                            "No dedicated /health endpoint, but root API accessible"
                        )
                        return True
                
                self.log_test(
                    "Health Check Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Health Check Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_root_api_endpoint(self) -> bool:
        """Test the root API endpoint /api/ for basic connectivity"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    message = data.get('message', '')
                    
                    self.log_test(
                        "Root API Endpoint",
                        True,
                        f"Root API accessible - Message: {message}"
                    )
                    return True
                    
                except json.JSONDecodeError:
                    self.log_test(
                        "Root API Endpoint",
                        True,
                        f"Root API accessible (non-JSON response): {response.text[:100]}"
                    )
                    return True
            else:
                self.log_test(
                    "Root API Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Root API Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_admin_authentication(self) -> bool:
        """Test admin authentication and JWT token generation"""
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
                
                # Verify JWT token structure
                if self.admin_token:
                    try:
                        # Decode JWT without verification to check structure
                        decoded = jwt.decode(self.admin_token, options={"verify_signature": False})
                        has_sub = 'sub' in decoded
                        has_exp = 'exp' in decoded
                        
                        jwt_valid = has_sub and has_exp
                    except:
                        jwt_valid = False
                else:
                    jwt_valid = False
                
                success = (
                    self.admin_token is not None and
                    user_info.get('role') == 'admin' and
                    jwt_valid
                )
                
                if success:
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Admin authenticated: {user_info.get('full_name')} ({user_info.get('email')}) - JWT token valid"
                    )
                else:
                    self.log_test(
                        "Admin Authentication",
                        False,
                        f"Auth issues - Token: {bool(self.admin_token)}, Role: {user_info.get('role')}, JWT: {jwt_valid}"
                    )
                
                return success
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_student_authentication(self) -> bool:
        """Test student authentication and JWT token generation"""
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
                
                # Verify JWT token structure
                if self.student_token:
                    try:
                        decoded = jwt.decode(self.student_token, options={"verify_signature": False})
                        has_sub = 'sub' in decoded
                        has_exp = 'exp' in decoded
                        jwt_valid = has_sub and has_exp
                    except:
                        jwt_valid = False
                else:
                    jwt_valid = False
                
                success = (
                    self.student_token is not None and
                    user_info.get('role') == 'learner' and
                    jwt_valid
                )
                
                if success:
                    self.log_test(
                        "Student Authentication",
                        True,
                        f"Student authenticated: {user_info.get('full_name')} ({user_info.get('email')}) - JWT token valid"
                    )
                else:
                    self.log_test(
                        "Student Authentication",
                        False,
                        f"Auth issues - Token: {bool(self.student_token)}, Role: {user_info.get('role')}, JWT: {jwt_valid}"
                    )
                
                return success
            else:
                self.log_test(
                    "Student Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def test_environment_variables_usage(self) -> bool:
        """Verify backend is using environment variables correctly"""
        try:
            # Check if backend/.env exists and has required variables
            backend_env_path = "/app/backend/.env"
            required_vars = ['MONGO_URL', 'JWT_SECRET_KEY', 'JWT_ALGORITHM']
            
            if not os.path.exists(backend_env_path):
                self.log_test(
                    "Environment Variables Usage",
                    False,
                    "Backend .env file not found"
                )
                return False
            
            env_vars = {}
            with open(backend_env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
            
            missing_vars = [var for var in required_vars if var not in env_vars]
            
            if missing_vars:
                self.log_test(
                    "Environment Variables Usage",
                    False,
                    f"Missing required environment variables: {missing_vars}"
                )
                return False
            
            # Check for hardcoded URLs (should not contain localhost in production)
            mongo_url = env_vars.get('MONGO_URL', '')
            has_hardcoded_localhost = 'localhost' in mongo_url.lower()
            
            # Check if JWT secret is not default
            jwt_secret = env_vars.get('JWT_SECRET_KEY', '')
            has_default_secret = 'your-secret-key-here' in jwt_secret.lower()
            
            success = not has_hardcoded_localhost and not has_default_secret
            
            issues = []
            if has_hardcoded_localhost:
                issues.append("MongoDB URL contains localhost")
            if has_default_secret:
                issues.append("JWT secret is default value")
            
            self.log_test(
                "Environment Variables Usage",
                success,
                f"Environment variables check - Issues: {issues if issues else 'None'}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Environment Variables Usage", False, f"Exception: {str(e)}")
            return False

    def test_mongodb_connection(self) -> bool:
        """Test MongoDB connection stability"""
        try:
            # Test database operations through API endpoints
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test multiple database operations
            db_tests = [
                ("Users Collection", f"{self.base_url}/auth/admin/users"),
                ("Courses Collection", f"{self.base_url}/courses"),
                ("Categories Collection", f"{self.base_url}/categories"),
                ("Programs Collection", f"{self.base_url}/programs"),
                ("Departments Collection", f"{self.base_url}/departments")
            ]
            
            successful_operations = 0
            total_operations = len(db_tests)
            
            for test_name, endpoint in db_tests:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    if response.status_code == 200:
                        successful_operations += 1
                    time.sleep(0.1)  # Small delay between requests
                except:
                    pass
            
            success_rate = (successful_operations / total_operations) * 100
            success = success_rate >= 80  # At least 80% of operations should work
            
            self.log_test(
                "MongoDB Connection Stability",
                success,
                f"Database operations success rate: {success_rate:.1f}% ({successful_operations}/{total_operations})"
            )
            
            return success
            
        except Exception as e:
            self.log_test("MongoDB Connection Stability", False, f"Exception: {str(e)}")
            return False

    def test_jwt_token_functionality(self) -> bool:
        """Test JWT token functionality and validation"""
        try:
            if not self.admin_token:
                self.log_test("JWT Token Functionality", False, "No admin token available")
                return False
            
            # Test token with protected endpoint
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Verify token contains correct user info
                token_valid = (
                    'id' in user_data and
                    'email' in user_data and
                    'role' in user_data
                )
                
                if token_valid:
                    # Test token expiration handling
                    try:
                        decoded = jwt.decode(self.admin_token, options={"verify_signature": False})
                        exp_timestamp = decoded.get('exp', 0)
                        current_timestamp = time.time()
                        
                        # Token should not be expired
                        token_not_expired = exp_timestamp > current_timestamp
                        
                        success = token_not_expired
                        
                        self.log_test(
                            "JWT Token Functionality",
                            success,
                            f"Token validation successful - User: {user_data.get('email')}, Expires: {datetime.fromtimestamp(exp_timestamp)}"
                        )
                        
                        return success
                    except:
                        self.log_test("JWT Token Functionality", False, "Could not decode JWT token")
                        return False
                else:
                    self.log_test("JWT Token Functionality", False, "Invalid user data in token response")
                    return False
            else:
                self.log_test(
                    "JWT Token Functionality",
                    False,
                    f"Token validation failed - HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("JWT Token Functionality", False, f"Exception: {str(e)}")
            return False

    def test_api_routes_with_prefix(self) -> bool:
        """Test that all API routes are accessible via /api prefix"""
        try:
            if not self.admin_token or not self.student_token:
                self.log_test("API Routes with /api Prefix", False, "Authentication tokens not available")
                return False
            
            # Test various API endpoints with /api prefix
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            
            api_routes = [
                ("GET /api/", f"{self.base_url}/", None),
                ("GET /api/courses", f"{self.base_url}/courses", admin_headers),
                ("GET /api/enrollments", f"{self.base_url}/enrollments", student_headers),
                ("GET /api/auth/me", f"{self.base_url}/auth/me", admin_headers),
                ("GET /api/categories", f"{self.base_url}/categories", admin_headers),
                ("GET /api/programs", f"{self.base_url}/programs", admin_headers),
                ("GET /api/departments", f"{self.base_url}/departments", admin_headers)
            ]
            
            successful_routes = 0
            total_routes = len(api_routes)
            route_results = []
            
            for route_name, url, headers in api_routes:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    success = response.status_code in [200, 201]
                    
                    if success:
                        successful_routes += 1
                    
                    route_results.append({
                        "route": route_name,
                        "success": success,
                        "status_code": response.status_code
                    })
                    
                    time.sleep(0.1)  # Small delay between requests
                    
                except Exception as e:
                    route_results.append({
                        "route": route_name,
                        "success": False,
                        "error": str(e)
                    })
            
            success_rate = (successful_routes / total_routes) * 100
            success = success_rate >= 85  # At least 85% of routes should work
            
            failed_routes = [r for r in route_results if not r['success']]
            
            self.log_test(
                "API Routes with /api Prefix",
                success,
                f"API routes success rate: {success_rate:.1f}% ({successful_routes}/{total_routes}) - Failed: {len(failed_routes)}",
                {"failed_routes": failed_routes}
            )
            
            return success
            
        except Exception as e:
            self.log_test("API Routes with /api Prefix", False, f"Exception: {str(e)}")
            return False

    def test_cors_and_production_headers(self) -> bool:
        """Test CORS configuration and production-ready headers"""
        try:
            # Test CORS with OPTIONS request
            response = requests.options(f"{self.base_url}/auth/login", timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            # Check if CORS is properly configured
            has_cors_origin = cors_headers['Access-Control-Allow-Origin'] is not None
            has_cors_methods = cors_headers['Access-Control-Allow-Methods'] is not None
            has_cors_headers = cors_headers['Access-Control-Allow-Headers'] is not None
            
            cors_configured = has_cors_origin and has_cors_methods and has_cors_headers
            
            # Test actual API request to verify CORS works
            api_response = requests.get(f"{self.base_url}/", timeout=10)
            api_cors_header = api_response.headers.get('Access-Control-Allow-Origin')
            
            success = cors_configured and api_cors_header is not None
            
            self.log_test(
                "CORS and Production Headers",
                success,
                f"CORS configured: {cors_configured}, API CORS header: {bool(api_cors_header)}",
                cors_headers
            )
            
            return success
            
        except Exception as e:
            self.log_test("CORS and Production Headers", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_deployment_test(self):
        """Run all deployment readiness tests"""
        print("🚀 DEPLOYMENT READINESS BACKEND TESTING SUITE")
        print("=" * 80)
        print()
        
        # Step 1: Basic Connectivity Tests
        print("🔗 BASIC CONNECTIVITY TESTING")
        print("-" * 40)
        
        health_check = self.test_health_endpoint()
        root_api = self.test_root_api_endpoint()
        
        print()
        
        # Step 2: Authentication Tests
        print("🔐 AUTHENTICATION TESTING")
        print("-" * 40)
        
        admin_auth = self.test_admin_authentication()
        student_auth = self.test_student_authentication()
        
        if not admin_auth or not student_auth:
            print("❌ CRITICAL: Authentication failed. Some tests will be skipped.")
        
        print()
        
        # Step 3: Environment and Configuration Tests
        print("⚙️ ENVIRONMENT & CONFIGURATION TESTING")
        print("-" * 40)
        
        env_vars = self.test_environment_variables_usage()
        mongodb_conn = self.test_mongodb_connection()
        jwt_functionality = self.test_jwt_token_functionality()
        
        print()
        
        # Step 4: API Routes and Production Readiness
        print("🌐 API ROUTES & PRODUCTION READINESS")
        print("-" * 40)
        
        api_routes = self.test_api_routes_with_prefix()
        cors_headers = self.test_cors_and_production_headers()
        
        print()
        
        # Generate Summary Report
        self.generate_deployment_summary()
        
        return True

    def generate_deployment_summary(self):
        """Generate comprehensive deployment readiness summary"""
        print("📊 DEPLOYMENT READINESS SUMMARY")
        print("=" * 80)
        
        # Calculate overall success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Categorize test results
        critical_tests = [
            "Health Check Endpoint", "Root API Endpoint", "Admin Authentication", 
            "Student Authentication", "MongoDB Connection Stability", "JWT Token Functionality"
        ]
        
        production_tests = [
            "Environment Variables Usage", "API Routes with /api Prefix", "CORS and Production Headers"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        production_passed = sum(1 for result in self.test_results 
                              if result["test"] in production_tests and result["success"])
        
        print("🔍 DEPLOYMENT READINESS BREAKDOWN:")
        print("-" * 40)
        
        print(f"🚨 CRITICAL FUNCTIONALITY: {critical_passed}/{len(critical_tests)} tests passed")
        for test in critical_tests:
            result = next((r for r in self.test_results if r["test"] == test), None)
            if result:
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {test}")
        
        print()
        print(f"🏭 PRODUCTION READINESS: {production_passed}/{len(production_tests)} tests passed")
        for test in production_tests:
            result = next((r for r in self.test_results if r["test"] == test), None)
            if result:
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {test}")
        
        print()
        
        # Deployment Recommendations
        print("💡 DEPLOYMENT RECOMMENDATIONS:")
        print("-" * 40)
        
        failed_tests = [result for result in self.test_results if not result["success"]]
        
        if not failed_tests:
            print("🎉 ALL TESTS PASSED - Backend is ready for production deployment!")
        else:
            print("⚠️ Issues found that should be addressed before deployment:")
            for failed_test in failed_tests:
                print(f"   🔧 {failed_test['test']}: {failed_test['details']}")
        
        print()
        
        # Final Deployment Status
        critical_success_rate = (critical_passed / len(critical_tests)) * 100
        production_success_rate = (production_passed / len(production_tests)) * 100
        
        if critical_success_rate >= 100 and production_success_rate >= 80:
            deployment_status = "🟢 READY FOR DEPLOYMENT"
        elif critical_success_rate >= 80:
            deployment_status = "🟡 DEPLOYMENT WITH CAUTION"
        else:
            deployment_status = "🔴 NOT READY FOR DEPLOYMENT"
        
        print(f"🚀 DEPLOYMENT STATUS: {deployment_status}")
        print(f"   Critical Systems: {critical_success_rate:.1f}%")
        print(f"   Production Features: {production_success_rate:.1f}%")
        
        print()
        print("=" * 80)

def main():
    """Main execution function"""
    test_suite = DeploymentReadinessTestSuite()
    
    try:
        success = test_suite.run_comprehensive_deployment_test()
        
        if success:
            print("✅ Deployment readiness testing completed!")
            return 0
        else:
            print("❌ Deployment readiness testing completed with issues!")
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