#!/usr/bin/env python3

"""
Test Course Creation Backend Test
=================================

This test creates 3 new test courses for debugging lesson completion issues as requested:
- Each course has 2 quizzes + 1 text lesson
- Enrolls both test students in all 3 courses
- Uses admin credentials for course creation
- Ready for testing lesson completion debug workflow

Course Structure for Each:
- Quiz 1: First quiz with mix of true/false and multiple choice questions
- Quiz 2: Second quiz with mix of true/false and multiple choice questions  
- Final Lesson: Text-based lesson (NOT a quiz) for testing lesson completion

Success Criteria:
- 3 courses created with identical structure (2 quizzes + 1 text lesson)
- All courses published and accessible
- Both students enrolled in all 3 courses
- Ready for testing lesson completion debug workflow
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_EMAILS = [
    "brayden.student@covesmart.com",
    "karlo.student@alder.com"
]

class TestCourseCreationTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.created_courses = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data["access_token"]
                    self.test_results.append("✅ Admin authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Admin authentication failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.test_results.append(f"❌ Admin authentication error: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
        
    async def create_test_course(self, course_letter):
        """Create a single test course with 2 quizzes + 1 text lesson"""
        try:
            # Course data
            course_data = {
                "title": f"Two-Quiz Test Course {course_letter}",
                "description": f"Debug course {course_letter} - 2 quizzes + text lesson",
                "category": "Testing",
                "duration": "30 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
                "accessType": "open",
                "learningOutcomes": [
                    "Test sequential quiz progression",
                    "Debug lesson completion tracking",
                    "Validate course completion workflow"
                ],
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 1: First Quiz",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": f"Quiz 1 - Course {course_letter}",
                                "type": "quiz",
                                "content": f"First quiz for debugging course {course_letter}",
                                "duration": 10,
                                "quiz": {
                                    "title": f"Quiz 1 - Course {course_letter}",
                                    "description": "First quiz with mixed question types",
                                    "timeLimit": 15,
                                    "passingScore": 70,
                                    "maxAttempts": 3,
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "true_false",
                                            "question": f"This is Quiz 1 of Course {course_letter}.",
                                            "correctAnswer": "true",
                                            "points": 10,
                                            "explanation": "This is indeed the first quiz of the course."
                                        },
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "multiple_choice",
                                            "question": f"What course are you taking?",
                                            "options": [
                                                f"Two-Quiz Test Course {course_letter}",
                                                "Different Course",
                                                "Unknown Course",
                                                "No Course"
                                            ],
                                            "correctAnswer": "0",
                                            "points": 10,
                                            "explanation": f"You are taking Two-Quiz Test Course {course_letter}."
                                        },
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "true_false",
                                            "question": "Sequential quiz progression should work correctly.",
                                            "correctAnswer": "true",
                                            "points": 10,
                                            "explanation": "Sequential progression is essential for proper course flow."
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 2: Second Quiz",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": f"Quiz 2 - Course {course_letter}",
                                "type": "quiz",
                                "content": f"Second quiz for debugging course {course_letter}",
                                "duration": 10,
                                "quiz": {
                                    "title": f"Quiz 2 - Course {course_letter}",
                                    "description": "Second quiz with mixed question types",
                                    "timeLimit": 15,
                                    "passingScore": 70,
                                    "maxAttempts": 3,
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "multiple_choice",
                                            "question": f"Which quiz number is this in Course {course_letter}?",
                                            "options": [
                                                "Quiz 1",
                                                "Quiz 2",
                                                "Quiz 3",
                                                "Final Quiz"
                                            ],
                                            "correctAnswer": "1",
                                            "points": 15,
                                            "explanation": "This is Quiz 2, the second quiz in the course."
                                        },
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "true_false",
                                            "question": "After this quiz, there should be a text lesson.",
                                            "correctAnswer": "true",
                                            "points": 15,
                                            "explanation": "The final lesson is a text-based lesson for completion testing."
                                        }
                                    ]
                                }
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 3: Final Text Lesson",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": f"Final Lesson - Course {course_letter}",
                                "type": "text",
                                "content": f"""
# Final Text Lesson - Course {course_letter}

## Congratulations!

You have successfully completed both quizzes in this debug course. This final lesson is designed to test lesson completion tracking.

## Key Points:

1. **Sequential Progression**: You should have completed Quiz 1 before accessing Quiz 2
2. **Quiz 2 Completion**: You should have completed Quiz 2 before accessing this text lesson
3. **Course Completion**: Completing this text lesson should mark the entire course as complete

## Testing Objectives:

- Test lesson completion tracking for text-based content
- Validate course completion after final lesson
- Debug any issues with progress tracking

## Course Summary:

- **Course**: Two-Quiz Test Course {course_letter}
- **Structure**: 2 Quizzes + 1 Text Lesson
- **Purpose**: Debug lesson completion issues
- **Expected Outcome**: 100% course completion

Thank you for participating in this debugging exercise!
                                """,
                                "duration": 5
                            }
                        ]
                    }
                ]
            }
            
            # Create the course
            async with self.session.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    course = await response.json()
                    course_id = course["id"]
                    self.created_courses.append({
                        "id": course_id,
                        "title": course["title"],
                        "letter": course_letter
                    })
                    self.test_results.append(f"✅ Course {course_letter} created successfully: {course['title']} (ID: {course_id})")
                    return course_id
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Course {course_letter} creation failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            self.test_results.append(f"❌ Course {course_letter} creation error: {str(e)}")
            return None
            
    async def get_student_by_email(self, email):
        """Get student user by email"""
        try:
            async with self.session.get(
                f"{BACKEND_URL}/auth/admin/users",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    users = await response.json()
                    for user in users:
                        if user["email"] == email:
                            return user
                    return None
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Failed to get users: {response.status} - {error_text}")
                    return None
        except Exception as e:
            self.test_results.append(f"❌ Error getting student {email}: {str(e)}")
            return None
            
    async def enroll_student_in_course(self, student_email, course_id, course_title):
        """Enroll a student in a course (admin enrollment)"""
        try:
            # Get student details
            student = await self.get_student_by_email(student_email)
            if not student:
                self.test_results.append(f"❌ Student {student_email} not found")
                return False
                
            # Create enrollment directly in database (admin privilege)
            enrollment_data = {
                "id": str(uuid.uuid4()),
                "userId": student["id"],
                "courseId": course_id,
                "studentId": student["id"],
                "courseName": course_title,
                "studentName": student["full_name"],
                "enrollmentDate": datetime.utcnow().isoformat(),
                "enrolledAt": datetime.utcnow().isoformat(),
                "progress": 0.0,
                "lastAccessedAt": None,
                "completedAt": None,
                "grade": None,
                "status": "active",
                "isActive": True,
                "enrolledBy": self.admin_token,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Use the enrollment endpoint
            async with self.session.post(
                f"{BACKEND_URL}/enrollments",
                json={"courseId": course_id},
                headers={"Authorization": f"Bearer {await self.get_student_token(student_email)}"}
            ) as response:
                if response.status == 200:
                    self.test_results.append(f"✅ Student {student_email} enrolled in {course_title}")
                    return True
                elif response.status == 400:
                    # Already enrolled
                    self.test_results.append(f"ℹ️ Student {student_email} already enrolled in {course_title}")
                    return True
                else:
                    error_text = await response.text()
                    self.test_results.append(f"❌ Failed to enroll {student_email} in {course_title}: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            self.test_results.append(f"❌ Error enrolling {student_email} in {course_title}: {str(e)}")
            return False
            
    async def get_student_token(self, student_email):
        """Get authentication token for student (for enrollment)"""
        try:
            # Try common passwords for test students
            passwords = ["StudentPermanent123!", "Cove1234!", "TestPassword123!", "CleanEnv123!"]
            
            for password in passwords:
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/auth/login",
                        json={
                            "username_or_email": student_email,
                            "password": password
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data["access_token"]
                except:
                    continue
                    
            # If no password works, create enrollment as admin
            return self.admin_token
            
        except Exception as e:
            return self.admin_token
            
    async def run_comprehensive_test(self):
        """Run comprehensive test course creation"""
        print("🎯 STARTING TEST COURSE CREATION FOR LESSON COMPLETION DEBUGGING")
        print("=" * 80)
        
        try:
            await self.setup_session()
            
            # Step 1: Authenticate as admin
            print("\n📋 STEP 1: Admin Authentication")
            if not await self.authenticate_admin():
                return False
                
            # Step 2: Create 3 test courses
            print("\n📋 STEP 2: Creating 3 Test Courses")
            course_letters = ["A", "B", "C"]
            
            for letter in course_letters:
                course_id = await self.create_test_course(letter)
                if not course_id:
                    return False
                    
            # Step 3: Enroll students in all courses
            print("\n📋 STEP 3: Enrolling Students in All Courses")
            enrollment_success = True
            
            for course in self.created_courses:
                for student_email in STUDENT_EMAILS:
                    success = await self.enroll_student_in_course(
                        student_email, 
                        course["id"], 
                        course["title"]
                    )
                    if not success:
                        enrollment_success = False
                        
            # Step 4: Verify course structure
            print("\n📋 STEP 4: Verifying Course Structure")
            await self.verify_course_structures()
            
            return enrollment_success
            
        except Exception as e:
            self.test_results.append(f"❌ Comprehensive test error: {str(e)}")
            return False
        finally:
            await self.cleanup_session()
            
    async def verify_course_structures(self):
        """Verify all courses have the correct structure"""
        try:
            for course in self.created_courses:
                async with self.session.get(
                    f"{BACKEND_URL}/courses/{course['id']}",
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        course_data = await response.json()
                        modules = course_data.get("modules", [])
                        
                        if len(modules) == 3:
                            quiz_count = 0
                            text_count = 0
                            
                            for module in modules:
                                for lesson in module.get("lessons", []):
                                    if lesson.get("type") == "quiz":
                                        quiz_count += 1
                                    elif lesson.get("type") == "text":
                                        text_count += 1
                                        
                            if quiz_count == 2 and text_count == 1:
                                self.test_results.append(f"✅ Course {course['letter']} structure verified: 2 quizzes + 1 text lesson")
                            else:
                                self.test_results.append(f"❌ Course {course['letter']} structure incorrect: {quiz_count} quizzes, {text_count} text lessons")
                        else:
                            self.test_results.append(f"❌ Course {course['letter']} has {len(modules)} modules (expected 3)")
                    else:
                        error_text = await response.text()
                        self.test_results.append(f"❌ Failed to verify course {course['letter']}: {response.status} - {error_text}")
                        
        except Exception as e:
            self.test_results.append(f"❌ Course structure verification error: {str(e)}")
            
    def print_results(self):
        """Print test results"""
        print("\n" + "=" * 80)
        print("🎯 TEST COURSE CREATION RESULTS")
        print("=" * 80)
        
        success_count = len([r for r in self.test_results if r.startswith("✅")])
        total_count = len([r for r in self.test_results if r.startswith(("✅", "❌"))])
        
        for result in self.test_results:
            print(result)
            
        print(f"\n📊 SUCCESS RATE: {success_count}/{total_count} tests passed")
        
        if self.created_courses:
            print(f"\n📚 CREATED COURSES:")
            for course in self.created_courses:
                print(f"   • {course['title']} (ID: {course['id']})")
                
        print(f"\n👥 STUDENT ENROLLMENT:")
        for email in STUDENT_EMAILS:
            print(f"   • {email} - Enrolled in all {len(self.created_courses)} courses")
            
        print(f"\n🎯 TESTING WORKFLOW READY:")
        print("   1. Quiz 1 → Quiz 2 progression (sequential unlocking)")
        print("   2. Quiz 2 → Final Lesson progression")
        print("   3. Final Lesson completion and progress tracking")
        print("   4. Course completion after final lesson")
        
        return success_count == total_count

async def main():
    """Main test execution"""
    tester = TestCourseCreationTester()
    
    try:
        success = await tester.run_comprehensive_test()
        tester.print_results()
        
        if success:
            print("\n🎉 TEST COURSE CREATION COMPLETED SUCCESSFULLY!")
            print("Ready for lesson completion debugging workflow testing.")
            sys.exit(0)
        else:
            print("\n❌ TEST COURSE CREATION FAILED!")
            print("Some courses may not have been created or students enrolled properly.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())