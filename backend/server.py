from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
import re


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Environment configuration
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here-change-in-production-b7d8f9e2c4a6e8f0d2a4b6c8e0f2a4b6')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))

# Configure logging early
log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Starting LMS API in {ENVIRONMENT} mode")
logger.info(f"Debug mode: {DEBUG}")

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security setup
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'test_database')

logger.info(f"Connecting to MongoDB: {mongo_url[:20]}...")
logger.info(f"Database name: {db_name}")

# Add additional connection options for Atlas MongoDB if needed
try:
    if 'mongodb.net' in mongo_url or 'atlas' in mongo_url.lower():
        # This is likely an Atlas connection
        logger.info("Detected Atlas MongoDB connection, using production settings")
        client = AsyncIOMotorClient(
            mongo_url,
            maxPoolSize=10,
            waitQueueTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            retryWrites=True
        )
    else:
        # Local or other MongoDB connection
        logger.info("Using standard MongoDB connection")
        client = AsyncIOMotorClient(mongo_url)

    db = client[db_name]
    logger.info("MongoDB connection established successfully")
    
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# =============================================================================
# AUTHENTICATION MODELS
# =============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: str = "learner"  # learner, instructor, admin
    department: Optional[str] = None
    temporary_password: str
    
    @validator('temporary_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    full_name: str
    role: str = "learner"
    department: Optional[str] = None
    hashed_password: str
    is_temporary_password: bool = True
    first_login_required: bool = True
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    password_updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    department: Optional[str] = None
    is_active: bool
    first_login_required: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    requires_password_change: bool

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class AdminPasswordResetRequest(BaseModel):
    user_id: str
    new_temporary_password: str
    
    @validator('new_temporary_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in ['admin', 'instructor', 'learner']:
            raise ValueError('Role must be admin, instructor, or learner')
        return v

# =============================================================================
# COURSE AND PROGRAM MODELS
# =============================================================================

class CourseModule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    lessons: List[dict] = []

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Course title")
    description: str = Field(..., min_length=1, max_length=2000, description="Course description")
    category: str = Field(..., min_length=1, max_length=100, description="Course category")
    duration: Optional[str] = Field(None, max_length=50)
    thumbnailUrl: Optional[str] = None
    accessType: Optional[str] = Field("open", pattern="^(open|restricted|invitation)$")
    learningOutcomes: List[str] = []  # What students will learn
    modules: List[CourseModule] = []
    canvaEmbedCode: Optional[str] = None
    
class CourseInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    duration: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    accessType: str = "open"
    learningOutcomes: List[str] = []  # What students will learn
    modules: List[CourseModule] = []
    canvaEmbedCode: Optional[str] = None
    instructorId: str
    instructor: str
    status: str = "published"  # draft, published, archived
    enrolledStudents: int = 0
    rating: float = 4.5
    reviews: List[dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    duration: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    accessType: str
    learningOutcomes: List[str] = []  # What students will learn
    modules: List[dict] = []
    canvaEmbedCode: Optional[str] = None
    instructorId: str
    instructor: str
    status: str
    enrolledStudents: int
    rating: float
    reviews: List[dict] = []
    created_at: datetime
    updated_at: datetime

class ProgramCreate(BaseModel):
    title: str
    description: str
    departmentId: Optional[str] = None
    duration: Optional[str] = None
    courseIds: List[str] = []
    nestedProgramIds: List[str] = []
    
class ProgramInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    departmentId: Optional[str] = None
    duration: Optional[str] = None
    courseIds: List[str] = []
    nestedProgramIds: List[str] = []
    instructorId: str
    instructor: str
    isActive: bool = True
    courseCount: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProgramResponse(BaseModel):
    id: str
    title: str
    description: str
    departmentId: Optional[str] = None
    duration: Optional[str] = None
    courseIds: List[str] = []
    nestedProgramIds: List[str] = []
    instructorId: str
    instructor: str
    isActive: bool
    courseCount: int
    created_at: datetime
    updated_at: datetime

class EnrollmentCreate(BaseModel):
    courseId: str

# Progress tracking models
class LessonProgress(BaseModel):
    lessonId: str
    completed: bool = False
    completedAt: Optional[datetime] = None
    timeSpent: Optional[int] = 0  # in seconds

class ModuleProgress(BaseModel):
    moduleId: str
    lessons: List[LessonProgress] = []
    completed: bool = False
    completedAt: Optional[datetime] = None

class EnrollmentResponse(BaseModel):
    id: str
    userId: str
    courseId: str
    enrolledAt: datetime
    progress: float = 0.0
    completedAt: Optional[datetime] = None
    status: str = "active"  # active, completed, dropped
    currentModuleId: Optional[str] = None
    currentLessonId: Optional[str] = None
    moduleProgress: Optional[List[ModuleProgress]] = None
    lastAccessedAt: Optional[datetime] = None
    timeSpent: Optional[int] = None

class AdminPasswordResetResponse(BaseModel):
    message: str
    user_id: str
    temporary_password: str
    reset_at: datetime


# =============================================================================
# AUTHENTICATION UTILITIES
# =============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current user from JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(**user)

async def get_admin_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current user and verify admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return JWT token."""
    # Find user by username or email
    user = await db.users.find_one({
        "$or": [
            {"username": login_data.username_or_email},
            {"email": login_data.username_or_email}
        ]
    })
    
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(hours=JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(**user)
    
    return LoginResponse(
        access_token=access_token,
        user=user_response,
        requires_password_change=user.get('first_login_required', False)
    )

@api_router.post("/auth/change-password")
async def change_password(
    password_data: PasswordChangeRequest, 
    current_user: UserResponse = Depends(get_current_user)
):
    """Change user password (for first-time login or regular password change)."""
    # Get user from database
    user = await db.users.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)
    
    # Update user password
    await db.users.update_one(
        {"id": current_user.id},
        {
            "$set": {
                "hashed_password": new_hashed_password,
                "is_temporary_password": False,
                "first_login_required": False,
                "password_updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Password changed successfully"}

# Bootstrap endpoint for creating initial admin user
class BootstrapAdminRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = "Admin User"
    username: Optional[str] = None

@api_router.post("/auth/bootstrap")
async def bootstrap_initial_admin(bootstrap_data: BootstrapAdminRequest):
    """
    One-time bootstrap endpoint to create the initial admin user.
    Only works when no users exist in the database.
    Automatically disables itself after creating the first admin user.
    """
    # Check if any users already exist in the database
    existing_user_count = await db.users.count_documents({})
    
    if existing_user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap endpoint is disabled. Admin users already exist in the system."
        )
    
    # Validate password strength
    if len(bootstrap_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Generate username from email if not provided
    username = bootstrap_data.username or bootstrap_data.email.split('@')[0]
    
    # Hash the password
    hashed_password = hash_password(bootstrap_data.password)
    
    # Create the initial admin user
    admin_user_dict = {
        "id": str(uuid.uuid4()),
        "email": bootstrap_data.email,
        "username": username,
        "full_name": bootstrap_data.full_name,
        "role": "admin",
        "department": "Administration",
        "hashed_password": hashed_password,
        "is_temporary_password": False,
        "first_login_required": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "password_updated_at": datetime.utcnow()
    }
    
    # Insert the admin user into the database
    await db.users.insert_one(admin_user_dict)
    
    # Return success response (don't include sensitive data)
    return {
        "success": True,
        "message": "Bootstrap complete! Initial admin user created successfully.",
        "admin_email": bootstrap_data.email,
        "admin_username": username,
        "note": "Bootstrap endpoint is now disabled. Use the admin login to create additional users."
    }

@api_router.post("/auth/admin/create-user", response_model=UserResponse)
async def admin_create_user(
    user_data: UserCreate,
    admin_user: UserResponse = Depends(get_admin_user)
):
    """Admin endpoint to create a new user with temporary password."""
    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"username": user_data.username},
            {"email": user_data.email}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    
    # Hash the temporary password
    hashed_password = hash_password(user_data.temporary_password)
    
    # Create user document
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "department": user_data.department,
        "hashed_password": hashed_password,
        "is_temporary_password": True,
        "first_login_required": True,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "password_updated_at": datetime.utcnow()
    }
    
    # Insert user into database
    await db.users.insert_one(user_dict)
    
    return UserResponse(**user_dict)

@api_router.post("/auth/admin/reset-password", response_model=AdminPasswordResetResponse)
async def admin_reset_user_password(
    reset_data: AdminPasswordResetRequest,
    admin_user: UserResponse = Depends(get_admin_user)
):
    """Admin endpoint to reset a user's password."""
    # Find the user
    user = await db.users.find_one({"id": reset_data.user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Hash the new temporary password
    new_hashed_password = hash_password(reset_data.new_temporary_password)
    
    # Update user password
    reset_time = datetime.utcnow()
    await db.users.update_one(
        {"id": reset_data.user_id},
        {
            "$set": {
                "hashed_password": new_hashed_password,
                "is_temporary_password": True,
                "first_login_required": True,
                "password_updated_at": reset_time
            }
        }
    )
    
    return AdminPasswordResetResponse(
        message=f"Password reset successfully for user {user['username']}",
        user_id=reset_data.user_id,
        temporary_password=reset_data.new_temporary_password,
        reset_at=reset_time
    )

@api_router.get("/auth/admin/users", response_model=List[UserResponse])
async def admin_get_all_users(admin_user: UserResponse = Depends(get_admin_user)):
    """Admin endpoint to get all users."""
    users = await db.users.find().to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.delete("/auth/admin/users/{user_id}")
async def admin_delete_user(
    user_id: str,
    admin_user: UserResponse = Depends(get_admin_user)
):
    """Admin endpoint to delete a user."""
    # Prevent admin from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account"
        )
    
    # Find the user to be deleted
    user_to_delete = await db.users.find_one({"id": user_id})
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if this is the last admin user (prevent deleting the last admin)
    if user_to_delete.get('role') == 'admin':
        admin_count = await db.users.count_documents({"role": "admin", "is_active": True})
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin user. At least one admin must remain."
            )
    
    # Delete the user
    result = await db.users.delete_one({"id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already deleted"
        )
    
    return {
        "message": f"User {user_to_delete['username']} has been successfully deleted",
        "deleted_user": {
            "id": user_id,
            "username": user_to_delete['username'],
            "email": user_to_delete['email'],
            "role": user_to_delete['role']
        }
    }

@api_router.put("/auth/admin/users/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    admin_user: UserResponse = Depends(get_admin_user)
):
    """Admin endpoint to update user details."""
    # Find the user to update
    user_to_update = await db.users.find_one({"id": user_id})
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent changing role of the last admin
    if (update_data.role and update_data.role != 'admin' and 
        user_to_update.get('role') == 'admin'):
        admin_count = await db.users.count_documents({"role": "admin", "is_active": True})
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change role of the last admin user. At least one admin must remain."
            )
    
    # Check if email is being changed to an existing email
    if update_data.email and update_data.email != user_to_update.get('email'):
        existing_email_user = await db.users.find_one({
            "email": update_data.email,
            "id": {"$ne": user_id}
        })
        if existing_email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already in use by another user"
            )
    
    # Build update data (only include fields that are not None)
    update_fields = {}
    if update_data.full_name is not None:
        update_fields["full_name"] = update_data.full_name
    if update_data.email is not None:
        update_fields["email"] = update_data.email
    if update_data.role is not None:
        update_fields["role"] = update_data.role
    if update_data.department is not None:
        update_fields["department"] = update_data.department
    if update_data.is_active is not None:
        update_fields["is_active"] = update_data.is_active
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )
    
    # Add update timestamp
    update_fields["updated_at"] = datetime.utcnow()
    
    # Update the user
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_fields}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or no changes made"
        )
    
    # Get updated user
    updated_user = await db.users.find_one({"id": user_id})
    
    return UserResponse(**updated_user)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# =============================================================================
# COURSE MANAGEMENT ENDPOINTS
# =============================================================================

@api_router.post("/courses", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new course."""
    # Only instructors and admins can create courses
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create courses"
        )
    
    # Create course document
    course_dict = {
        "id": str(uuid.uuid4()),
        **course_data.dict(),
        "instructorId": current_user.id,
        "instructor": current_user.full_name,
        "status": "published",
        "enrolledStudents": 0,
        "rating": 4.5,
        "reviews": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert course into database
    await db.courses.insert_one(course_dict)
    
    return CourseResponse(**course_dict)

@api_router.get("/courses", response_model=List[CourseResponse])
async def get_all_courses(current_user: UserResponse = Depends(get_current_user)):
    """Get all published courses (course catalog)."""
    courses = await db.courses.find({"status": "published"}).to_list(1000)
    return [CourseResponse(**course) for course in courses]

@api_router.get("/courses/my-courses", response_model=List[CourseResponse])
async def get_my_courses(current_user: UserResponse = Depends(get_current_user)):
    """Get courses created by current user or enrolled in."""
    if current_user.role in ['instructor', 'admin']:
        # Get courses created by this instructor
        created_courses = await db.courses.find({"instructorId": current_user.id}).to_list(1000)
        return [CourseResponse(**course) for course in created_courses]
    else:
        # Get courses student is enrolled in
        enrollments = await db.enrollments.find({"userId": current_user.id}).to_list(1000)
        course_ids = [enrollment['courseId'] for enrollment in enrollments]
        
        if not course_ids:
            return []
            
        enrolled_courses = await db.courses.find({"id": {"$in": course_ids}}).to_list(1000)
        return [CourseResponse(**course) for course in enrolled_courses]

@api_router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific course by ID."""
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return CourseResponse(**course)

@api_router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_data: CourseCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a course (only by course creator or admin)."""
    # Find the course
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and course['instructorId'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own courses"
        )
    
    # Update course
    update_data = course_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.courses.update_one(
        {"id": course_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or no changes made"
        )
    
    # Get updated course
    updated_course = await db.courses.find_one({"id": course_id})
    return CourseResponse(**updated_course)

@api_router.delete("/courses/{course_id}")
async def delete_course(
    course_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a course (only by course creator or admin)."""
    # Find the course
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and course['instructorId'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own courses"
        )
    
    # Delete all enrollments for this course first
    enrollment_delete_result = await db.enrollments.delete_many({"courseId": course_id})
    print(f"Deleted {enrollment_delete_result.deleted_count} enrollments for course {course_id}")
    
    # Delete the course
    result = await db.courses.delete_one({"id": course_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return {
        "message": f"Course '{course['title']}' and {enrollment_delete_result.deleted_count} associated enrollments have been successfully deleted"
    }


# =============================================================================
# ENROLLMENT ENDPOINTS
# =============================================================================

@api_router.post("/enrollments", response_model=EnrollmentResponse)
async def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Enroll current user in a course."""
    # Only learners can enroll (instructors manage their own courses)
    if current_user.role != 'learner':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll in courses"
        )
    
    # Check if course exists
    course = await db.courses.find_one({"id": enrollment_data.courseId})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing_enrollment = await db.enrollments.find_one({
        "userId": current_user.id,
        "courseId": enrollment_data.courseId
    })
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this course"
        )
    
    # Get course details for response
    course = await db.courses.find_one({"id": enrollment_data.courseId})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Create enrollment
    now = datetime.utcnow()
    enrollment_dict = {
        "id": str(uuid.uuid4()),
        "userId": current_user.id,
        "courseId": enrollment_data.courseId,
        "studentId": current_user.id,
        "courseName": course.get("title", "Unknown Course"),
        "studentName": current_user.full_name,
        "enrollmentDate": now,
        "enrolledAt": now,
        "progress": 0.0,
        "lastAccessedAt": None,
        "completedAt": None,
        "grade": None,
        "status": "active",
        "isActive": True,
        "enrolledBy": current_user.id,
        "created_at": now,
        "updated_at": now
    }
    
    await db.enrollments.insert_one(enrollment_dict)
    
    # Update course enrollment count
    await db.courses.update_one(
        {"id": enrollment_data.courseId},
        {"$inc": {"enrolledStudents": 1}}
    )
    
    return EnrollmentResponse(**enrollment_dict)

@api_router.get("/enrollments", response_model=List[EnrollmentResponse])
async def get_my_enrollments(current_user: UserResponse = Depends(get_current_user)):
    """Get current user's course enrollments."""
    enrollments = await db.enrollments.find({"userId": current_user.id}).to_list(1000)
    return [EnrollmentResponse(**enrollment) for enrollment in enrollments]

@api_router.get("/admin/enrollments", response_model=List[EnrollmentResponse])
async def get_all_enrollments_admin(current_user: UserResponse = Depends(get_current_user)):
    """Get all course enrollments (admin and instructor only) for analytics."""
    if current_user.role not in ['admin', 'instructor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and instructors can access all enrollments"
        )
    
    # For instructors, filter to only their courses
    if current_user.role == 'instructor':
        # Get courses created by this instructor
        instructor_courses = await db.courses.find({"instructor_id": current_user.id}).to_list(1000)
        course_ids = [course["id"] for course in instructor_courses]
        
        if course_ids:
            enrollments = await db.enrollments.find({"courseId": {"$in": course_ids}}).to_list(10000)
        else:
            enrollments = []
    else:
        # Admin gets all enrollments
        enrollments = await db.enrollments.find({}).to_list(10000)
    
    return [EnrollmentResponse(**enrollment) for enrollment in enrollments]

@api_router.delete("/enrollments/{course_id}")
async def unenroll_from_course(
    course_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Unenroll from a course."""
    # Find enrollment
    enrollment = await db.enrollments.find_one({
        "userId": current_user.id,
        "courseId": course_id
    })
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Delete enrollment
    await db.enrollments.delete_one({
        "userId": current_user.id,
        "courseId": course_id
    })
    
    # Update course enrollment count
    await db.courses.update_one(
        {"id": course_id},
        {"$inc": {"enrolledStudents": -1}}
    )
    
    return {"message": "Successfully unenrolled from course"}

class EnrollmentProgressUpdate(BaseModel):
    progress: Optional[float] = None  # Overall progress percentage (0-100)
    currentModuleId: Optional[str] = None
    currentLessonId: Optional[str] = None
    moduleProgress: Optional[List[ModuleProgress]] = None
    lastAccessedAt: Optional[datetime] = None
    timeSpent: Optional[int] = None  # Total time spent in seconds

@api_router.put("/enrollments/{course_id}/progress", response_model=EnrollmentResponse)
async def update_enrollment_progress(
    course_id: str,
    progress_data: EnrollmentProgressUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update progress for a course enrollment."""
    # Find the enrollment
    enrollment = await db.enrollments.find_one({
        "userId": current_user.id,
        "courseId": course_id
    })
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}
    
    if progress_data.progress is not None:
        update_data["progress"] = min(100.0, max(0.0, progress_data.progress))
        
        # Mark as completed if progress reaches 100%
        if progress_data.progress >= 100.0:
            update_data["status"] = "completed"
            update_data["completedAt"] = datetime.utcnow()
    
    if progress_data.currentModuleId is not None:
        update_data["currentModuleId"] = progress_data.currentModuleId
    
    if progress_data.currentLessonId is not None:
        update_data["currentLessonId"] = progress_data.currentLessonId
    
    if progress_data.moduleProgress is not None:
        # Convert Pydantic models to dict for storage
        update_data["moduleProgress"] = [
            module.dict() for module in progress_data.moduleProgress
        ]
    
    if progress_data.lastAccessedAt is not None:
        update_data["lastAccessedAt"] = progress_data.lastAccessedAt
    else:
        update_data["lastAccessedAt"] = datetime.utcnow()
    
    if progress_data.timeSpent is not None:
        update_data["timeSpent"] = progress_data.timeSpent
    
    # Update the enrollment
    result = await db.enrollments.update_one(
        {"userId": current_user.id, "courseId": course_id},
        {"$set": update_data}
    )
    
    # Fetch updated enrollment
    updated_enrollment = await db.enrollments.find_one({
        "userId": current_user.id,
        "courseId": course_id
    })
    
    # Auto-generate certificate when course is completed (100% progress)
    if progress_data.progress is not None and progress_data.progress >= 100.0:
        # Check if certificate already exists
        existing_certificate = await db.certificates.find_one({
            "studentId": current_user.id,
            "courseId": course_id,
            "isActive": True
        })
        
        if not existing_certificate:
            # Get course details for certificate
            course = await db.courses.find_one({"id": course_id})
            if course:
                # Generate certificate
                certificate_number = f"CERT-{course_id[:8].upper()}-{current_user.id[:8].upper()}-{datetime.utcnow().strftime('%Y%m%d')}"
                verification_code = str(uuid.uuid4()).replace('-', '').upper()[:12]
                
                certificate_dict = {
                    "id": str(uuid.uuid4()),
                    "certificateNumber": certificate_number,
                    "studentId": current_user.id,
                    "studentName": current_user.full_name,
                    "studentEmail": current_user.email,
                    "courseId": course_id,
                    "courseName": course.get("title", "Unknown Course"),
                    "programId": None,
                    "programName": None,
                    "type": "completion",
                    "template": "default",
                    "status": "generated",
                    "issueDate": datetime.utcnow(),
                    "expiryDate": None,
                    "grade": "A" if progress_data.progress >= 95 else "B" if progress_data.progress >= 85 else "C",
                    "score": progress_data.progress,
                    "completionDate": datetime.utcnow(),
                    "certificateUrl": None,
                    "issuedBy": "system",
                    "issuedByName": "LearningFwiend System",
                    "verificationCode": verification_code,
                    "isActive": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await db.certificates.insert_one(certificate_dict)
    
    return EnrollmentResponse(**updated_enrollment)

@api_router.post("/enrollments/{enrollment_id}/migrate-progress")
async def migrate_enrollment_progress(
    enrollment_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Migrate existing enrollment to new progress tracking system."""
    # Find the enrollment
    enrollment = await db.enrollments.find_one({
        "id": enrollment_id,
        "userId": current_user.id
    })
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Get the course to understand structure
    course = await db.courses.find_one({"id": enrollment["courseId"]})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Initialize moduleProgress if it doesn't exist
    if "moduleProgress" not in enrollment or not enrollment["moduleProgress"]:
        module_progress = []
        
        for module in course.get("modules", []):
            if module.get("lessons"):
                lesson_progress = []
                for lesson in module["lessons"]:
                    lesson_progress.append({
                        "lessonId": lesson["id"],
                        "completed": False,
                        "completedAt": None,
                        "timeSpent": 0
                    })
                
                module_progress.append({
                    "moduleId": module["id"],
                    "lessons": lesson_progress,
                    "completed": False,
                    "completedAt": None
                })
        
        # Update enrollment with new progress structure
        await db.enrollments.update_one(
            {"id": enrollment_id},
            {
                "$set": {
                    "moduleProgress": module_progress,
                    "progress": 0.0,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Enrollment migrated to new progress tracking system",
            "totalLessons": sum(len(m.get("lessons", [])) for m in course.get("modules", [])),
            "moduleCount": len(course.get("modules", []))
        }
    
    return {"message": "Enrollment already has progress tracking structure"}

@api_router.post("/enrollments/cleanup-orphaned")
async def cleanup_orphaned_enrollments(current_user: UserResponse = Depends(get_current_user)):
    """Clean up enrollment records that reference non-existent courses (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can cleanup orphaned enrollments"
        )
    
    # Get all enrollments
    all_enrollments = await db.enrollments.find({}).to_list(10000)
    
    # Get all valid course IDs
    all_courses = await db.courses.find({}).to_list(10000)
    valid_course_ids = {course["id"] for course in all_courses}
    
    # Find orphaned enrollments
    orphaned_enrollments = []
    for enrollment in all_enrollments:
        if enrollment["courseId"] not in valid_course_ids:
            orphaned_enrollments.append(enrollment)
    
    # Delete orphaned enrollments
    deleted_count = 0
    for enrollment in orphaned_enrollments:
        await db.enrollments.delete_one({"id": enrollment["id"]})
        deleted_count += 1
    
    return {
        "message": f"Successfully cleaned up {deleted_count} orphaned enrollment records",
        "deletedCount": deleted_count,
        "orphanedCourseIds": list(set(e["courseId"] for e in orphaned_enrollments))
    }


# =============================================================================
# PROGRAM MANAGEMENT ENDPOINTS
# =============================================================================

@api_router.post("/programs", response_model=ProgramResponse)
async def create_program(
    program_data: ProgramCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new program."""
    # Only instructors and admins can create programs
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create programs"
        )
    
    # Create program document
    program_dict = {
        "id": str(uuid.uuid4()),
        **program_data.dict(),
        "instructorId": current_user.id,
        "instructor": current_user.full_name,
        "isActive": True,
        "courseCount": len(program_data.courseIds),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert program into database
    await db.programs.insert_one(program_dict)
    
    return ProgramResponse(**program_dict)

@api_router.get("/programs", response_model=List[ProgramResponse])
async def get_all_programs(current_user: UserResponse = Depends(get_current_user)):
    """Get all active programs."""
    programs = await db.programs.find({"isActive": True}).to_list(1000)
    return [ProgramResponse(**program) for program in programs]

@api_router.get("/programs/my-programs", response_model=List[ProgramResponse])
async def get_my_programs(current_user: UserResponse = Depends(get_current_user)):
    """Get programs created by current user."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can access program management"
        )
    
    programs = await db.programs.find({"instructorId": current_user.id}).to_list(1000)
    return [ProgramResponse(**program) for program in programs]

@api_router.get("/programs/{program_id}", response_model=ProgramResponse)
async def get_program(
    program_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific program by ID."""
    program = await db.programs.find_one({"id": program_id})
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    return ProgramResponse(**program)

@api_router.put("/programs/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: str,
    program_data: ProgramCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a program (only by program creator or admin)."""
    # Find the program
    program = await db.programs.find_one({"id": program_id})
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and program['instructorId'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own programs"
        )
    
    # Update program
    update_data = program_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    update_data["courseCount"] = len(program_data.courseIds)
    
    result = await db.programs.update_one(
        {"id": program_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found or no changes made"
        )
    
    # Get updated program
    updated_program = await db.programs.find_one({"id": program_id})
    return ProgramResponse(**updated_program)

@api_router.get("/programs/{program_id}/access-check", response_model=dict)
async def check_program_access(
    program_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Check if the current user can access a program based on classroom end dates."""
    if current_user.role != 'learner':
        # Instructors and admins always have access
        return {"hasAccess": True, "reason": "admin_access"}
    
    # Find all classrooms that contain this program and include the current student
    classrooms = await db.classrooms.find({
        "programIds": program_id,
        "studentIds": current_user.id,
        "isActive": True
    }).to_list(1000)
    
    if not classrooms:
        return {"hasAccess": False, "reason": "not_enrolled", "message": "You are not enrolled in any classroom that includes this program"}
    
    # Check if any classroom allows access (has not passed end date)
    current_time = datetime.utcnow()
    active_classrooms = []
    expired_classrooms = []
    
    for classroom in classrooms:
        end_date = classroom.get('endDate')
        if not end_date:
            # No end date means indefinite access
            active_classrooms.append(classroom)
        elif end_date > current_time:
            # End date hasn't passed
            active_classrooms.append(classroom)
        else:
            # End date has passed
            expired_classrooms.append(classroom)
    
    if active_classrooms:
        # Student has access through at least one active classroom
        return {
            "hasAccess": True, 
            "reason": "classroom_active",
            "activeClassrooms": len(active_classrooms),
            "message": f"Access granted through {len(active_classrooms)} active classroom(s)"
        }
    else:
        # All classrooms have expired
        return {
            "hasAccess": False, 
            "reason": "classroom_expired",
            "expiredClassrooms": len(expired_classrooms),
            "message": f"Program access has expired in all {len(expired_classrooms)} enrolled classroom(s)"
        }

@api_router.delete("/programs/{program_id}")
async def delete_program(
    program_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a program (only by program creator or admin)."""
    # Find the program
    program = await db.programs.find_one({"id": program_id})
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and program['instructorId'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own programs"
        )
    
    # Delete the program
    result = await db.programs.delete_one({"id": program_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    return {"message": f"Program '{program['title']}' has been successfully deleted"}


# =============================================================================
# EXISTING MODELS AND ENDPOINTS (PRESERVED)
# =============================================================================

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# LoginPal OAuth Models (Placeholder)
class LoginPalUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    loginpal_user_id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    role: str = "learner"  # learner, instructor, admin
    verified_email: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LoginPalWebhook(BaseModel):
    event_type: str  # user.created, user.updated, user.deleted, role.changed
    user_id: str
    user_data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserRoleUpdate(BaseModel):
    user_id: str
    new_role: str  # learner, instructor, admin
    permissions: Optional[List[str]] = None

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# =============================================================================
# LOGINPAL OAUTH INTEGRATION ENDPOINTS (PLACEHOLDER)
# =============================================================================

@api_router.get("/auth/loginpal/status")
async def loginpal_auth_status():
    """Status endpoint for LoginPal OAuth integration"""
    return {
        "status": "placeholder",
        "message": "LoginPal OAuth integration will be available once LoginPal service is deployed",
        "ready": False,
        "endpoints": {
            "oauth_init": "/api/auth/loginpal/login",
            "oauth_callback": "/api/auth/loginpal/callback", 
            "webhook": "/api/auth/loginpal/webhook",
            "user_sync": "/api/auth/loginpal/sync"
        }
    }

@api_router.get("/auth/loginpal/login")
async def initiate_loginpal_oauth():
    """Placeholder for LoginPal OAuth initiation"""
    return {
        "status": "placeholder",
        "message": "LoginPal OAuth login will redirect to LoginPal authorization server",
        "authorization_url": "https://auth.loginpal.emergent.com/oauth2/authorize?client_id=YOUR_CLIENT_ID",
        "note": "This is a placeholder - actual implementation pending LoginPal deployment"
    }

@api_router.post("/auth/loginpal/callback")
async def handle_loginpal_callback(code: str, state: str):
    """Placeholder for LoginPal OAuth callback handling"""
    return {
        "status": "placeholder", 
        "message": "LoginPal OAuth callback will exchange code for tokens and create user session",
        "received_code": code[:10] + "..." if len(code) > 10 else code,
        "received_state": state,
        "note": "This is a placeholder - actual implementation pending LoginPal deployment"
    }

@api_router.post("/auth/loginpal/webhook")
async def handle_loginpal_webhook(webhook_data: LoginPalWebhook):
    """Placeholder webhook endpoint for LoginPal events"""
    logger.info(f"LoginPal webhook received: {webhook_data.event_type} for user {webhook_data.user_id}")
    
    # Store webhook for later processing when real integration is ready
    webhook_dict = webhook_data.dict()
    webhook_dict['processed'] = False
    await db.loginpal_webhooks.insert_one(webhook_dict)
    
    return {
        "status": "received",
        "message": "Webhook stored for processing when LoginPal integration is active",
        "event_type": webhook_data.event_type,
        "user_id": webhook_data.user_id
    }

@api_router.get("/auth/loginpal/users")
async def get_loginpal_users():
    """Get all users synced from LoginPal (placeholder)"""
    users = await db.loginpal_users.find().to_list(1000)
    return {
        "status": "placeholder",
        "users": [LoginPalUser(**user) for user in users] if users else [],
        "count": len(users) if users else 0,
        "message": "User data will be synced from LoginPal once integration is active"
    }

@api_router.post("/auth/loginpal/sync-user")
async def sync_user_from_loginpal(user_data: LoginPalUser):
    """Sync user data from LoginPal (placeholder)"""
    user_dict = user_data.dict()
    
    # Check if user already exists
    existing_user = await db.loginpal_users.find_one({"loginpal_user_id": user_data.loginpal_user_id})
    
    if existing_user:
        # Update existing user
        user_dict['updated_at'] = datetime.utcnow()
        await db.loginpal_users.update_one(
            {"loginpal_user_id": user_data.loginpal_user_id},
            {"$set": user_dict}
        )
        action = "updated"
    else:
        # Create new user
        await db.loginpal_users.insert_one(user_dict)
        action = "created"
    
    return {
        "status": "success",
        "action": action,
        "user": user_data,
        "message": f"User {action} in placeholder database - will sync with actual LoginPal when ready"
    }

@api_router.put("/auth/loginpal/user-role")
async def update_user_role(role_update: UserRoleUpdate):
    """Update user role from LoginPal (placeholder)"""
    result = await db.loginpal_users.update_one(
        {"loginpal_user_id": role_update.user_id},
        {
            "$set": {
                "role": role_update.new_role,
                "permissions": role_update.permissions or [],
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "status": "success" if result.modified_count > 0 else "not_found",
        "user_id": role_update.user_id,
        "new_role": role_update.new_role,
        "modified_count": result.modified_count,
        "message": "Role updated in placeholder database - will sync with LoginPal when ready"
    }

@api_router.get("/auth/loginpal/webhooks")
async def get_loginpal_webhooks():
    """Get stored LoginPal webhooks (placeholder)"""
    webhooks = await db.loginpal_webhooks.find().sort("timestamp", -1).to_list(100)
    return {
        "status": "success",
        "webhooks": webhooks,
        "count": len(webhooks),
        "message": "Stored webhooks from LoginPal - ready for processing when integration is active"
    }

# =============================================================================
# END LOGINPAL INTEGRATION ENDPOINTS
# =============================================================================

# =============================================================================
# CATEGORY MODELS
# =============================================================================

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
class CategoryInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    courseCount: int = 0
    isActive: bool = True
    createdBy: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    courseCount: int
    isActive: bool
    createdBy: str
    created_at: datetime
    updated_at: datetime

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    isActive: Optional[bool] = None


# =============================================================================
# CATEGORY ENDPOINTS
# =============================================================================

@api_router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new category (instructors and admins only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create categories"
        )
    
    # Check if category with same name already exists
    existing_category = await db.categories.find_one({"name": category_data.name, "isActive": True})
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    # Create category dictionary
    category_dict = {
        "id": str(uuid.uuid4()),
        **category_data.dict(),
        "courseCount": 0,
        "isActive": True,
        "createdBy": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert category into database
    await db.categories.insert_one(category_dict)
    
    return CategoryResponse(**category_dict)

@api_router.get("/categories", response_model=List[CategoryResponse])
async def get_all_categories(current_user: UserResponse = Depends(get_current_user)):
    """Get all active categories."""
    categories = await db.categories.find({"isActive": True}).to_list(1000)
    
    # Update course counts for each category
    for category in categories:
        course_count = await db.courses.count_documents({"category": category["name"], "status": "published"})
        category["courseCount"] = course_count
    
    return [CategoryResponse(**category) for category in categories]

@api_router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific category by ID."""
    category = await db.categories.find_one({"id": category_id})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Update course count
    course_count = await db.courses.count_documents({"category": category["name"], "status": "published"})
    category["courseCount"] = course_count
    
    return CategoryResponse(**category)

@api_router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a category (only by category creator or admin)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can update categories"
        )
    
    # Find the category
    category = await db.categories.find_one({"id": category_id})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check permissions (admin can edit any, creator can edit their own)
    if current_user.role != 'admin' and category['createdBy'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit categories you created"
        )
    
    # Check if new name already exists (if name is being changed)
    if category_data.name and category_data.name != category['name']:
        existing_category = await db.categories.find_one({"name": category_data.name, "isActive": True})
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
    
    # Update category
    update_data = {k: v for k, v in category_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.categories.update_one(
        {"id": category_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or no changes made"
        )
    
    # Get updated category
    updated_category = await db.categories.find_one({"id": category_id})
    
    # Update course count
    course_count = await db.courses.count_documents({"category": updated_category["name"], "status": "published"})
    updated_category["courseCount"] = course_count
    
    return CategoryResponse(**updated_category)

@api_router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a category (only by category creator or admin)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can delete categories"
        )
    
    # Find the category
    category = await db.categories.find_one({"id": category_id})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check permissions (admin can delete any, creator can delete their own)
    if current_user.role != 'admin' and category['createdBy'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete categories you created"
        )
    
    # Check if category is being used by any courses
    course_count = await db.courses.count_documents({"category": category["name"], "status": "published"})
    if course_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category. It is being used by {course_count} course(s)"
        )
    
    # Soft delete the category (set isActive to False)
    result = await db.categories.update_one(
        {"id": category_id},
        {"$set": {"isActive": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return {"message": f"Category '{category['name']}' has been successfully deleted"}


# =============================================================================
# DEPARTMENT MODELS
# =============================================================================

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
class DepartmentInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    userCount: int = 0
    isActive: bool = True
    createdBy: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DepartmentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    userCount: int
    isActive: bool
    createdBy: str
    created_at: datetime
    updated_at: datetime

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    isActive: Optional[bool] = None


# =============================================================================
# DEPARTMENT ENDPOINTS
# =============================================================================

@api_router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new department (admins only)."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create departments"
        )
    
    # Check if department with same name already exists
    existing_department = await db.departments.find_one({"name": department_data.name, "isActive": True})
    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department with this name already exists"
        )
    
    # Create department dictionary
    department_dict = {
        "id": str(uuid.uuid4()),
        **department_data.dict(),
        "userCount": 0,
        "isActive": True,
        "createdBy": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert department into database
    await db.departments.insert_one(department_dict)
    
    return DepartmentResponse(**department_dict)

@api_router.get("/departments", response_model=List[DepartmentResponse])
async def get_all_departments(current_user: UserResponse = Depends(get_current_user)):
    """Get all active departments."""
    departments = await db.departments.find({"isActive": True}).to_list(1000)
    
    # Update user counts for each department
    for department in departments:
        user_count = await db.users.count_documents({"department": department["name"], "is_active": True})
        department["userCount"] = user_count
    
    return [DepartmentResponse(**department) for department in departments]

@api_router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific department by ID."""
    department = await db.departments.find_one({"id": department_id})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Update user count
    user_count = await db.users.count_documents({"department": department["name"], "is_active": True})
    department["userCount"] = user_count
    
    return DepartmentResponse(**department)

@api_router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a department (admins only)."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update departments"
        )
    
    # Find the department
    department = await db.departments.find_one({"id": department_id})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if new name already exists (if name is being changed)
    if department_data.name and department_data.name != department['name']:
        existing_department = await db.departments.find_one({"name": department_data.name, "isActive": True})
        if existing_department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with this name already exists"
            )
    
    # Update department
    update_data = {k: v for k, v in department_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.departments.update_one(
        {"id": department_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found or no changes made"
        )
    
    # Get updated department
    updated_department = await db.departments.find_one({"id": department_id})
    
    # Update user count
    user_count = await db.users.count_documents({"department": updated_department["name"], "is_active": True})
    updated_department["userCount"] = user_count
    
    return DepartmentResponse(**updated_department)

@api_router.delete("/departments/{department_id}")
async def delete_department(
    department_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a department (admins only)."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete departments"
        )
    
    # Find the department
    department = await db.departments.find_one({"id": department_id})
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if department is being used by any users
    user_count = await db.users.count_documents({"department": department["name"], "is_active": True})
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete department. It is being used by {user_count} user(s)"
        )
    
    # Soft delete the department (set isActive to False)
    result = await db.departments.update_one(
        {"id": department_id},
        {"$set": {"isActive": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    return {"message": f"Department '{department['name']}' has been successfully deleted"}


# =============================================================================
# CLASSROOM MODELS
# =============================================================================

class ClassroomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trainerId: str  # Instructor assigned to this classroom
    courseIds: List[str] = []  # Courses assigned to this classroom
    programIds: List[str] = []  # Programs assigned to this classroom
    studentIds: List[str] = []  # Students enrolled in this classroom
    batchId: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    maxStudents: Optional[int] = None
    department: Optional[str] = None
    
class ClassroomInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    trainerId: str
    trainerName: str  # Denormalized for easy access
    courseIds: List[str] = []
    programIds: List[str] = []
    studentIds: List[str] = []
    batchId: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    maxStudents: Optional[int] = None
    department: Optional[str] = None
    isActive: bool = True
    createdBy: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ClassroomResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    trainerId: str
    trainerName: str
    courseIds: List[str] = []
    programIds: List[str] = []
    studentIds: List[str] = []
    batchId: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    maxStudents: Optional[int] = None
    department: Optional[str] = None
    studentCount: int
    courseCount: int
    programCount: int
    isActive: bool
    createdBy: str
    created_at: datetime
    updated_at: datetime

class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trainerId: Optional[str] = None
    courseIds: Optional[List[str]] = None
    programIds: Optional[List[str]] = None
    studentIds: Optional[List[str]] = None
    batchId: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    maxStudents: Optional[int] = None
    department: Optional[str] = None
    isActive: Optional[bool] = None


# =============================================================================
# CLASSROOM ENDPOINTS
# =============================================================================

@api_router.get("/classrooms/{classroom_id}/students")
async def get_classroom_students(
    classroom_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get students enrolled in a specific classroom."""
    try:
        # Get the classroom
        classroom = await db.classrooms.find_one({"id": classroom_id})
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Classroom not found"
            )
        
        # Check if user has access to view this classroom
        # Instructors can view their own classrooms, admins can view all
        if current_user.role not in ['admin'] and classroom.get('trainerId') != current_user.id:
            # Allow students to view classrooms they're enrolled in
            if current_user.role == 'learner' and current_user.id not in classroom.get('studentIds', []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this classroom"
                )
        
        # Get student details
        students = []
        if classroom.get('studentIds'):
            for student_id in classroom['studentIds']:
                student = await db.users.find_one({"id": student_id})
                if student:
                    # Return safe student info (no password, etc.)
                    student_info = {
                        "id": student["id"],
                        "username": student["username"],
                        "email": student["email"],
                        "full_name": student["full_name"],
                        "role": student["role"],
                        "department": student.get("department", ""),
                        "created_at": student.get("created_at")
                    }
                    students.append(student_info)
        
        return students
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting classroom students: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@api_router.post("/classrooms", response_model=ClassroomResponse)
async def create_classroom(
    classroom_data: ClassroomCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new classroom (instructors and admins only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create classrooms"
        )
    
    # Verify trainer exists and is an instructor
    trainer = await db.users.find_one({"id": classroom_data.trainerId})
    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified trainer not found"
        )
    
    if trainer['role'] != 'instructor':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified trainer must be an instructor"
        )
    
    # Verify courses exist
    for course_id in classroom_data.courseIds:
        course = await db.courses.find_one({"id": course_id})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with ID {course_id} not found"
            )
    
    # Verify programs exist
    for program_id in classroom_data.programIds:
        program = await db.programs.find_one({"id": program_id})
        if not program:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Program with ID {program_id} not found"
            )
    
    # Verify students exist and are learners
    for student_id in classroom_data.studentIds:
        student = await db.users.find_one({"id": student_id})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with ID {student_id} not found"
            )
        if student['role'] != 'learner':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {student_id} must be a learner to be enrolled as student"
            )
    
    # Create classroom dictionary
    classroom_dict = {
        "id": str(uuid.uuid4()),
        **classroom_data.dict(),
        "trainerName": trainer['full_name'],
        "isActive": True,
        "createdBy": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert classroom into database
    await db.classrooms.insert_one(classroom_dict)
    
    # AUTO-ENROLL STUDENTS IN CLASSROOM COURSES AND PROGRAM COURSES
    # When students are assigned to a classroom, automatically enroll them in all courses
    enrollment_count = 0
    for student_id in classroom_data.studentIds:
        student = await db.users.find_one({"id": student_id})
        if student and student['role'] == 'learner':
            
            # Collect all course IDs from direct courses and program courses
            all_course_ids = set(classroom_data.courseIds)
            
            # Add courses from programs
            for program_id in classroom_data.programIds:
                program = await db.programs.find_one({"id": program_id})
                if program and "courseIds" in program:
                    all_course_ids.update(program["courseIds"])
            
            # Enroll in all collected courses
            for course_id in all_course_ids:
                # Check if student is already enrolled in this course
                existing_enrollment = await db.enrollments.find_one({
                    "userId": student_id,
                    "courseId": course_id
                })
                
                if not existing_enrollment:
                    # Get course details for enrollment
                    course = await db.courses.find_one({"id": course_id})
                    if course:
                        # Create enrollment
                        now = datetime.utcnow()
                        enrollment_dict = {
                            "id": str(uuid.uuid4()),
                            "userId": student_id,
                            "courseId": course_id,
                            "studentId": student_id,  # For compatibility
                            "courseName": course.get("title", "Unknown Course"),
                            "studentName": student['full_name'],
                            "enrollmentDate": now,
                            "enrolledAt": now,
                            "progress": 0.0,
                            "lastAccessedAt": None,
                            "completedAt": None,
                            "grade": None,
                            "status": "active",
                            "isActive": True,
                            "enrolledBy": current_user.id,
                            "classroomId": classroom_dict["id"],  # Track which classroom enrolled them
                            "created_at": now,
                            "updated_at": now
                        }
                        
                        await db.enrollments.insert_one(enrollment_dict)
                        enrollment_count += 1
                        
                        # Update course enrollment count
                        await db.courses.update_one(
                            {"id": course_id},
                            {"$inc": {"enrolledStudents": 1}}
                        )
    
    print(f"Auto-enrolled {enrollment_count} student-course combinations from classroom assignment")
    
    # Add calculated fields for response
    classroom_dict["studentCount"] = len(classroom_data.studentIds)
    classroom_dict["courseCount"] = len(classroom_data.courseIds)
    classroom_dict["programCount"] = len(classroom_data.programIds)
    
    return ClassroomResponse(**classroom_dict)

@api_router.get("/classrooms", response_model=List[ClassroomResponse])
async def get_all_classrooms(current_user: UserResponse = Depends(get_current_user)):
    """Get all active classrooms."""
    classrooms = await db.classrooms.find({"isActive": True}).to_list(1000)
    
    # Add calculated fields for each classroom
    for classroom in classrooms:
        classroom["studentCount"] = len(classroom.get("studentIds", []))
        classroom["courseCount"] = len(classroom.get("courseIds", []))
        classroom["programCount"] = len(classroom.get("programIds", []))
    
    return [ClassroomResponse(**classroom) for classroom in classrooms]

@api_router.get("/classrooms/my-classrooms", response_model=List[ClassroomResponse])
async def get_my_classrooms(current_user: UserResponse = Depends(get_current_user)):
    """Get classrooms created by current user or where user is trainer/student."""
    query = {}
    
    if current_user.role == 'instructor':
        # Instructors see classrooms they created or where they are the trainer
        query = {
            "$or": [
                {"createdBy": current_user.id},
                {"trainerId": current_user.id}
            ],
            "isActive": True
        }
    elif current_user.role == 'learner':
        # Students see classrooms where they are enrolled
        query = {
            "studentIds": current_user.id,
            "isActive": True
        }
    elif current_user.role == 'admin':
        # Admins see all classrooms
        query = {"isActive": True}
    
    classrooms = await db.classrooms.find(query).to_list(1000)
    
    # Add calculated fields for each classroom
    for classroom in classrooms:
        classroom["studentCount"] = len(classroom.get("studentIds", []))
        classroom["courseCount"] = len(classroom.get("courseIds", []))
        classroom["programCount"] = len(classroom.get("programIds", []))
    
    return [ClassroomResponse(**classroom) for classroom in classrooms]

@api_router.get("/classrooms/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(
    classroom_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific classroom by ID."""
    classroom = await db.classrooms.find_one({"id": classroom_id})
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    # Add calculated fields
    classroom["studentCount"] = len(classroom.get("studentIds", []))
    classroom["courseCount"] = len(classroom.get("courseIds", []))
    classroom["programCount"] = len(classroom.get("programIds", []))
    
    return ClassroomResponse(**classroom)

@api_router.put("/classrooms/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: str,
    classroom_data: ClassroomUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a classroom (only by classroom creator, trainer, or admin)."""
    # Find the classroom
    classroom = await db.classrooms.find_one({"id": classroom_id})
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    # Check permissions
    can_edit = (
        current_user.role == 'admin' or 
        classroom['createdBy'] == current_user.id or 
        classroom['trainerId'] == current_user.id
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit classrooms you created or where you are the trainer"
        )
    
    # Validate trainer if being updated
    if classroom_data.trainerId:
        trainer = await db.users.find_one({"id": classroom_data.trainerId})
        if not trainer or trainer['role'] != 'instructor':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified trainer must be a valid instructor"
            )
    
    # Update classroom
    update_data = {k: v for k, v in classroom_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Update trainer name if trainer is being changed
    if classroom_data.trainerId:
        trainer = await db.users.find_one({"id": classroom_data.trainerId})
        update_data["trainerName"] = trainer['full_name']
    
    result = await db.classrooms.update_one(
        {"id": classroom_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found or no changes made"
        )
    
    # Get updated classroom
    updated_classroom = await db.classrooms.find_one({"id": classroom_id})
    
    # AUTO-ENROLL NEW STUDENTS (if studentIds were updated)
    # When students are added to an existing classroom, automatically enroll them in all courses
    if classroom_data.studentIds is not None:
        enrollment_count = 0
        
        # Get all course IDs from direct courses and program courses
        all_course_ids = set(updated_classroom.get("courseIds", []))
        
        # Add courses from programs
        for program_id in updated_classroom.get("programIds", []):
            program = await db.programs.find_one({"id": program_id})
            if program and "courseIds" in program:
                all_course_ids.update(program["courseIds"])
        
        # Enroll each student in all collected courses
        for student_id in updated_classroom.get("studentIds", []):
            student = await db.users.find_one({"id": student_id})
            if student and student['role'] == 'learner':
                
                for course_id in all_course_ids:
                    # Check if student is already enrolled in this course
                    existing_enrollment = await db.enrollments.find_one({
                        "userId": student_id,
                        "courseId": course_id
                    })
                    
                    if not existing_enrollment:
                        # Get course details for enrollment
                        course = await db.courses.find_one({"id": course_id})
                        if course:
                            # Create enrollment
                            now = datetime.utcnow()
                            enrollment_dict = {
                                "id": str(uuid.uuid4()),
                                "userId": student_id,
                                "courseId": course_id,
                                "studentId": student_id,  # For compatibility
                                "courseName": course.get("title", "Unknown Course"),
                                "studentName": student['full_name'],
                                "enrollmentDate": now,
                                "enrolledAt": now,
                                "progress": 0.0,
                                "lastAccessedAt": None,
                                "completedAt": None,
                                "grade": None,
                                "status": "active",
                                "isActive": True,
                                "enrolledBy": current_user.id,
                                "classroomId": classroom_id,  # Track which classroom enrolled them
                                "created_at": now,
                                "updated_at": now
                            }
                            
                            await db.enrollments.insert_one(enrollment_dict)
                            enrollment_count += 1
                            
                            # Update course enrollment count
                            await db.courses.update_one(
                                {"id": course_id},
                                {"$inc": {"enrolledStudents": 1}}
                            )
        
        if enrollment_count > 0:
            print(f"Auto-enrolled {enrollment_count} student-course combinations from classroom update")
    
    # Add calculated fields
    updated_classroom["studentCount"] = len(updated_classroom.get("studentIds", []))
    updated_classroom["courseCount"] = len(updated_classroom.get("courseIds", []))
    updated_classroom["programCount"] = len(updated_classroom.get("programIds", []))
    
    return ClassroomResponse(**updated_classroom)

@api_router.delete("/classrooms/{classroom_id}")
async def delete_classroom(
    classroom_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a classroom (only by classroom creator or admin)."""
    # Find the classroom
    classroom = await db.classrooms.find_one({"id": classroom_id})
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    # Check permissions (only creator or admin can delete)
    if current_user.role != 'admin' and classroom['createdBy'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete classrooms you created"
        )
    
    # Delete all enrollments for courses in this classroom
    # First get all course IDs in this classroom
    course_ids_in_classroom = classroom.get('courseIds', [])
    enrollment_delete_count = 0
    
    if course_ids_in_classroom:
        # Delete enrollments for all courses in this classroom
        enrollment_delete_result = await db.enrollments.delete_many({
            "courseId": {"$in": course_ids_in_classroom}
        })
        enrollment_delete_count = enrollment_delete_result.deleted_count
        print(f"Deleted {enrollment_delete_count} enrollments for classroom {classroom_id}")
    
    # Soft delete the classroom (set isActive to False)
    result = await db.classrooms.update_one(
        {"id": classroom_id},
        {"$set": {"isActive": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    return {
        "message": f"Classroom '{classroom['name']}' and {enrollment_delete_count} associated course enrollments have been successfully deleted"
    }


# =============================================================================
# ENROLLMENT MODELS
# =============================================================================

class EnrollmentCreate(BaseModel):
    courseId: str
    studentId: str
    
class EnrollmentInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    courseId: str
    studentId: str
    courseName: str  # Denormalized for easy access
    studentName: str  # Denormalized for easy access
    enrollmentDate: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, completed, dropped, suspended
    progress: float = 0.0  # 0.0 to 100.0
    lastAccessedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    grade: Optional[str] = None
    isActive: bool = True
    enrolledBy: str  # Who enrolled the student (instructor/admin/self)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    enrolledBy: str
    created_at: datetime
    updated_at: datetime

class EnrollmentUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None
    lastAccessedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    grade: Optional[str] = None

class BulkEnrollmentCreate(BaseModel):
    courseId: str
    studentIds: List[str]


# =============================================================================
# ANNOUNCEMENT MODELS
# =============================================================================

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    type: str = "general"  # general, course, urgent, maintenance
    courseId: Optional[str] = None  # If course-specific announcement
    classroomId: Optional[str] = None  # If classroom-specific announcement
    targetAudience: str = "all"  # all, instructors, learners, specific_course, specific_classroom
    priority: str = "normal"  # low, normal, high, urgent
    expiresAt: Optional[datetime] = None
    attachments: List[str] = []  # URLs to attached files
    
class AnnouncementInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    type: str
    courseId: Optional[str] = None
    courseName: Optional[str] = None  # Denormalized
    classroomId: Optional[str] = None
    classroomName: Optional[str] = None  # Denormalized
    targetAudience: str
    priority: str
    isActive: bool = True
    isPinned: bool = False
    viewCount: int = 0
    expiresAt: Optional[datetime] = None
    attachments: List[str] = []
    authorId: str
    authorName: str  # Denormalized
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AnnouncementResponse(BaseModel):
    id: str
    title: str
    content: str
    type: str
    courseId: Optional[str] = None
    courseName: Optional[str] = None
    classroomId: Optional[str] = None
    classroomName: Optional[str] = None
    targetAudience: str
    priority: str
    isActive: bool
    isPinned: bool
    viewCount: int
    expiresAt: Optional[datetime] = None
    attachments: List[str] = []
    authorId: str
    authorName: str
    created_at: datetime
    updated_at: datetime

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    courseId: Optional[str] = None
    classroomId: Optional[str] = None
    targetAudience: Optional[str] = None
    priority: Optional[str] = None
    isPinned: Optional[bool] = None
    expiresAt: Optional[datetime] = None
    attachments: Optional[List[str]] = None


# =============================================================================
# ANNOUNCEMENT ENDPOINTS
# =============================================================================

@api_router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new announcement (instructors and admins only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create announcements"
        )
    
    # Validate course if course-specific announcement
    course_name = None
    if announcement_data.courseId:
        course = await db.courses.find_one({"id": announcement_data.courseId})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified course not found"
            )
        course_name = course['title']
    
    # Validate classroom if classroom-specific announcement
    classroom_name = None
    if announcement_data.classroomId:
        classroom = await db.classrooms.find_one({"id": announcement_data.classroomId})
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified classroom not found"
            )
        classroom_name = classroom['name']
    
    # Create announcement dictionary
    announcement_dict = {
        "id": str(uuid.uuid4()),
        **announcement_data.dict(),
        "courseName": course_name,
        "classroomName": classroom_name,
        "isActive": True,
        "isPinned": False,
        "viewCount": 0,
        "authorId": current_user.id,
        "authorName": current_user.full_name,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert announcement into database
    await db.announcements.insert_one(announcement_dict)
    
    return AnnouncementResponse(**announcement_dict)

@api_router.get("/announcements", response_model=List[AnnouncementResponse])
async def get_announcements(
    current_user: UserResponse = Depends(get_current_user),
    type: Optional[str] = None,
    priority: Optional[str] = None,
    course_id: Optional[str] = None,
    limit: Optional[int] = 50
):
    """Get announcements relevant to current user."""
    
    # Base query for active announcements
    query = {"isActive": True}
    
    # Add expiration filter
    query["$or"] = [
        {"expiresAt": {"$exists": False}},
        {"expiresAt": None},
        {"expiresAt": {"$gt": datetime.utcnow()}}
    ]
    
    # Add type filter if specified
    if type:
        query["type"] = type
    
    # Add priority filter if specified
    if priority:
        query["priority"] = priority
    
    # Add course filter if specified
    if course_id:
        query["courseId"] = course_id
    
    # Role-based filtering
    if current_user.role == 'learner':
        # Students see announcements targeted to them
        query["$and"] = [
            query.get("$and", {}),
            {
                "$or": [
                    {"targetAudience": "all"},
                    {"targetAudience": "learners"}
                ]
            }
        ]
    elif current_user.role == 'instructor':
        # Instructors see announcements targeted to them or all
        query["$and"] = [
            query.get("$and", {}),
            {
                "$or": [
                    {"targetAudience": "all"},
                    {"targetAudience": "instructors"},
                    {"authorId": current_user.id}  # Their own announcements
                ]
            }
        ]
    # Admins see all announcements (no additional filtering)
    
    # Get announcements sorted by pinned status and creation date
    announcements = await db.announcements.find(query).sort([
        ("isPinned", -1),  # Pinned first
        ("priority", -1),  # High priority first
        ("created_at", -1)  # Newest first
    ]).limit(limit).to_list(limit)
    
    return [AnnouncementResponse(**announcement) for announcement in announcements]

@api_router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific announcement by ID and increment view count."""
    announcement = await db.announcements.find_one({"id": announcement_id, "isActive": True})
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    # Increment view count
    await db.announcements.update_one(
        {"id": announcement_id},
        {"$inc": {"viewCount": 1}}
    )
    announcement["viewCount"] += 1
    
    return AnnouncementResponse(**announcement)

@api_router.get("/announcements/my-announcements", response_model=List[AnnouncementResponse])
async def get_my_announcements(current_user: UserResponse = Depends(get_current_user)):
    """Get announcements created by current user."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can view their announcements"
        )
    
    announcements = await db.announcements.find({
        "authorId": current_user.id,
        "isActive": True
    }).sort("created_at", -1).to_list(100)
    
    return [AnnouncementResponse(**announcement) for announcement in announcements]

@api_router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: str,
    announcement_data: AnnouncementUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update an announcement (only by author or admin)."""
    # Find the announcement
    announcement = await db.announcements.find_one({"id": announcement_id})
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    # Check permissions (only author or admin can edit)
    if current_user.role != 'admin' and announcement['authorId'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit announcements you created"
        )
    
    # Validate course if being updated
    if announcement_data.courseId:
        course = await db.courses.find_one({"id": announcement_data.courseId})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified course not found"
            )
    
    # Validate classroom if being updated
    if announcement_data.classroomId:
        classroom = await db.classrooms.find_one({"id": announcement_data.classroomId})
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified classroom not found"
            )
    
    # Update announcement
    update_data = {k: v for k, v in announcement_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Update denormalized fields if necessary
    if announcement_data.courseId:
        course = await db.courses.find_one({"id": announcement_data.courseId})
        update_data["courseName"] = course['title'] if course else None
    
    if announcement_data.classroomId:
        classroom = await db.classrooms.find_one({"id": announcement_data.classroomId})
        update_data["classroomName"] = classroom['name'] if classroom else None
    
    result = await db.announcements.update_one(
        {"id": announcement_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found or no changes made"
        )
    
    # Get updated announcement
    updated_announcement = await db.announcements.find_one({"id": announcement_id})
    return AnnouncementResponse(**updated_announcement)

@api_router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete an announcement (only by author or admin)."""
    # Find the announcement
    announcement = await db.announcements.find_one({"id": announcement_id})
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    # Check permissions (only author or admin can delete)
    if current_user.role != 'admin' and announcement['authorId'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete announcements you created"
        )
    
    # Soft delete the announcement (set isActive to False)
    result = await db.announcements.update_one(
        {"id": announcement_id},
        {"$set": {"isActive": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    return {"message": f"Announcement '{announcement['title']}' has been successfully deleted"}

@api_router.put("/announcements/{announcement_id}/pin")
async def toggle_pin_announcement(
    announcement_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Pin/unpin an announcement (admins only)."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can pin/unpin announcements"
        )
    
    # Find the announcement
    announcement = await db.announcements.find_one({"id": announcement_id})
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    # Toggle pin status
    new_pin_status = not announcement.get('isPinned', False)
    
    result = await db.announcements.update_one(
        {"id": announcement_id},
        {"$set": {"isPinned": new_pin_status, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    pin_action = "pinned" if new_pin_status else "unpinned"
    return {"message": f"Announcement has been successfully {pin_action}"}


# =============================================================================
# CERTIFICATE MODELS
# =============================================================================

class CertificateCreate(BaseModel):
    studentId: Optional[str] = None
    userId: Optional[str] = None  # Accept both studentId and userId
    courseId: Optional[str] = None
    programId: Optional[str] = None
    type: str = "completion"  # completion, achievement, participation
    template: str = "default"  # default, premium, custom
    
    def get_student_id(self):
        """Get student ID from either studentId or userId field"""
        return self.studentId or self.userId
    
class CertificateInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    certificateNumber: str  # Unique certificate number
    studentId: str
    studentName: str  # Denormalized
    studentEmail: str  # Denormalized
    courseId: Optional[str] = None
    courseName: Optional[str] = None  # Denormalized
    programId: Optional[str] = None
    programName: Optional[str] = None  # Denormalized
    type: str
    template: str
    status: str = "generated"  # generated, downloaded, printed, revoked
    issueDate: datetime = Field(default_factory=datetime.utcnow)
    expiryDate: Optional[datetime] = None
    grade: Optional[str] = None
    score: Optional[float] = None
    completionDate: Optional[datetime] = None
    certificateUrl: Optional[str] = None  # URL to certificate file
    issuedBy: str  # Admin/Instructor who issued
    issuedByName: str  # Denormalized
    verificationCode: str  # For certificate verification
    isActive: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CertificateResponse(BaseModel):
    id: str
    certificateNumber: str
    studentId: str
    studentName: str
    studentEmail: str
    courseId: Optional[str] = None
    courseName: Optional[str] = None
    programId: Optional[str] = None
    programName: Optional[str] = None
    type: str
    template: str
    status: str
    issueDate: datetime
    expiryDate: Optional[datetime] = None
    grade: Optional[str] = None
    score: Optional[float] = None
    completionDate: Optional[datetime] = None
    certificateUrl: Optional[str] = None
    issuedBy: str
    issuedByName: str
    verificationCode: str
    isActive: bool
    created_at: datetime
    updated_at: datetime

class CertificateUpdate(BaseModel):
    status: Optional[str] = None
    grade: Optional[str] = None
    score: Optional[float] = None
    completionDate: Optional[datetime] = None
    certificateUrl: Optional[str] = None
    expiryDate: Optional[datetime] = None

class CertificateVerificationResponse(BaseModel):
    isValid: bool
    certificate: Optional[CertificateResponse] = None
    message: str


# =============================================================================
# CERTIFICATE ENDPOINTS
# =============================================================================

@api_router.post("/certificates", response_model=CertificateResponse)
async def create_certificate(
    certificate_data: CertificateCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new certificate (instructors and admins only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create certificates"
        )
    
    # Get the actual student ID (from either studentId or userId)
    student_id = certificate_data.get_student_id()
    if not student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either studentId or userId must be provided"
        )
    
    # Verify student exists and is a learner
    student = await db.users.find_one({"id": student_id})
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified student not found"
        )
    
    if student['role'] != 'learner':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificates can only be issued to learners"
        )
    
    # Validate course if course certificate
    course_name = None
    if certificate_data.courseId:
        course = await db.courses.find_one({"id": certificate_data.courseId})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified course not found"
            )
        course_name = course['title']
        
        # Check if student is enrolled in the course (flexible for admins)
        enrollment = await db.enrollments.find_one({
            "courseId": certificate_data.courseId,
            "studentId": student_id,
            "isActive": True
        })
        
        # Allow admins to issue certificates without strict enrollment requirement
        if not enrollment and current_user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student must be enrolled in the course to receive a certificate (or you must be an admin)"
            )
    
    # Validate program if program certificate
    program_name = None
    if certificate_data.programId:
        program = await db.programs.find_one({"id": certificate_data.programId})
        if not program:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified program not found"
            )
        program_name = program['title']
    
    # Must specify either course or program
    if not certificate_data.courseId and not certificate_data.programId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate must be for either a course or program"
        )
    
    # Check if certificate already exists for this student-course/program combination
    existing_query = {
        "studentId": student_id,
        "isActive": True
    }
    if certificate_data.courseId:
        existing_query["courseId"] = certificate_data.courseId
    if certificate_data.programId:
        existing_query["programId"] = certificate_data.programId
    
    existing_certificate = await db.certificates.find_one(existing_query)
    if existing_certificate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate already exists for this student and course/program"
        )
    
    # Generate unique certificate number
    certificate_number = f"CERT-{datetime.utcnow().year}-{str(uuid.uuid4())[:8].upper()}"
    verification_code = str(uuid.uuid4()).replace('-', '').upper()[:12]
    
    # Create certificate dictionary
    certificate_dict = {
        "id": str(uuid.uuid4()),
        "certificateNumber": certificate_number,
        "studentId": student_id,  # Use the resolved student ID
        "courseId": certificate_data.courseId,
        "programId": certificate_data.programId,
        "type": certificate_data.type,
        "template": certificate_data.template,
        "studentName": student['full_name'],
        "studentEmail": student['email'],
        "courseName": course_name,
        "programName": program_name,
        "status": "generated",
        "issueDate": datetime.utcnow(),
        "completionDate": datetime.utcnow(),  # Default to now, can be updated
        "issuedBy": current_user.id,
        "issuedByName": current_user.full_name,
        "verificationCode": verification_code,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert certificate into database
    await db.certificates.insert_one(certificate_dict)
    
    return CertificateResponse(**certificate_dict)

@api_router.get("/certificates", response_model=List[CertificateResponse])
async def get_certificates(
    current_user: UserResponse = Depends(get_current_user),
    student_id: Optional[str] = None,
    course_id: Optional[str] = None,
    program_id: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None
):
    """Get certificates with optional filtering."""
    
    # Base query for active certificates
    query = {"isActive": True}
    
    # Role-based access control
    if current_user.role == 'learner':
        # Students can only see their own certificates
        query["studentId"] = current_user.id
    elif current_user.role == 'instructor':
        # Instructors can see certificates they issued or all if admin privileges needed
        if student_id and current_user.role != 'admin':
            # Check if instructor has access to this student (through courses they teach)
            pass  # For now, allow instructors to see all
    # Admins can see all certificates (no additional restrictions)
    
    # Add filters
    if student_id and current_user.role != 'learner':
        query["studentId"] = student_id
    if course_id:
        query["courseId"] = course_id
    if program_id:
        query["programId"] = program_id
    if type:
        query["type"] = type
    if status:
        query["status"] = status
    
    certificates = await db.certificates.find(query).sort("created_at", -1).to_list(1000)
    return [CertificateResponse(**certificate) for certificate in certificates]

@api_router.get("/certificates/my-certificates", response_model=List[CertificateResponse])
async def get_my_certificates(current_user: UserResponse = Depends(get_current_user)):
    """Get certificates for current user."""
    if current_user.role != 'learner':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only learners can view their certificates"
        )
    
    certificates = await db.certificates.find({
        "studentId": current_user.id,
        "isActive": True
    }).sort("created_at", -1).to_list(1000)
    
    return [CertificateResponse(**certificate) for certificate in certificates]

@api_router.get("/certificates/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(
    certificate_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific certificate by ID."""
    certificate = await db.certificates.find_one({"id": certificate_id, "isActive": True})
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    # Check permissions
    if (current_user.role == 'learner' and 
        certificate['studentId'] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own certificates"
        )
    
    return CertificateResponse(**certificate)

@api_router.get("/certificates/{certificate_id}/download")
async def download_certificate(
    certificate_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Download certificate as PDF."""
    from fastapi.responses import Response
    import json
    
    certificate = await db.certificates.find_one({"id": certificate_id, "isActive": True})
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    # Check permissions
    if (current_user.role == 'learner' and 
        certificate['studentId'] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only download your own certificates"
        )
    
    # For now, generate a simple text-based certificate
    # In production, this would generate a proper PDF using libraries like reportlab
    
    # Get certificate details with proper fallbacks
    student_name = certificate.get('studentName') or 'Student Name'
    program_name = certificate.get('programName') or certificate.get('courseName') or 'Course/Program'
    issued_date = certificate.get('issuedAt') or certificate.get('issued_at') or certificate.get('completionDate')
    
    # Format date if it's a datetime object
    if issued_date and hasattr(issued_date, 'strftime'):
        issued_date = issued_date.strftime('%B %d, %Y')
    elif issued_date and isinstance(issued_date, str):
        try:
            from datetime import datetime
            parsed_date = datetime.fromisoformat(issued_date.replace('Z', '+00:00'))
            issued_date = parsed_date.strftime('%B %d, %Y')
        except:
            pass
    else:
        issued_date = 'Date Not Available'
    
    certificate_content = f"""
CERTIFICATE OF COMPLETION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is to certify that

{student_name}

has successfully completed the program

{program_name}

Awarded on: {issued_date}
Certificate ID: {certificate.get('id', certificate_id)}
Verification Code: {certificate.get('verificationCode', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LearningFwiend - Learning Management System
"""
    
    # Return as downloadable text file (in production, this would be a PDF)
    program_name = certificate.get('programName') or certificate.get('courseName') or 'achievement'
    filename = f"certificate_{program_name.replace(' ', '_')}.txt"
    
    return Response(
        content=certificate_content.encode('utf-8'),
        media_type='text/plain',
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@api_router.get("/certificates/verify/{verification_code}", response_model=CertificateVerificationResponse)
async def verify_certificate(verification_code: str):
    """Verify a certificate using its verification code (public endpoint)."""
    certificate = await db.certificates.find_one({
        "verificationCode": verification_code.upper(),
        "isActive": True
    })
    
    if not certificate:
        return CertificateVerificationResponse(
            isValid=False,
            certificate=None,
            message="Certificate not found or verification code is invalid"
        )
    
    # Check if certificate is expired
    if certificate.get('expiryDate') and certificate['expiryDate'] < datetime.utcnow():
        return CertificateVerificationResponse(
            isValid=False,
            certificate=CertificateResponse(**certificate),
            message="Certificate has expired"
        )
    
    # Check if certificate is revoked
    if certificate.get('status') == 'revoked':
        return CertificateVerificationResponse(
            isValid=False,
            certificate=CertificateResponse(**certificate),
            message="Certificate has been revoked"
        )
    
    return CertificateVerificationResponse(
        isValid=True,
        certificate=CertificateResponse(**certificate),
        message="Certificate is valid and authentic"
    )

@api_router.put("/certificates/{certificate_id}", response_model=CertificateResponse)
async def update_certificate(
    certificate_id: str,
    certificate_data: CertificateUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a certificate (instructors and admins only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can update certificates"
        )
    
    # Find the certificate
    certificate = await db.certificates.find_one({"id": certificate_id})
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    # Update certificate
    update_data = {k: v for k, v in certificate_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.certificates.update_one(
        {"id": certificate_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found or no changes made"
        )
    
    # Get updated certificate
    updated_certificate = await db.certificates.find_one({"id": certificate_id})
    return CertificateResponse(**updated_certificate)

@api_router.delete("/certificates/{certificate_id}")
async def revoke_certificate(
    certificate_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Revoke a certificate (admins only)."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can revoke certificates"
        )
    
    # Find the certificate
    certificate = await db.certificates.find_one({"id": certificate_id})
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    # Revoke the certificate (set status to revoked but keep active for audit trail)
    result = await db.certificates.update_one(
        {"id": certificate_id},
        {"$set": {"status": "revoked", "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    return {"message": f"Certificate {certificate['certificateNumber']} has been successfully revoked"}


# =============================================================================
# QUIZ/ASSESSMENT MODELS
# =============================================================================

class QuestionCreate(BaseModel):
    type: str = Field(..., pattern="^(multiple_choice|true_false|short_answer|essay|chronological-order|select-all-that-apply)$", description="Question type")
    question: str = Field(..., min_length=1, max_length=1000, description="Question text")
    options: List[str] = Field(default=[], description="Options for multiple choice questions")
    correctAnswer: Optional[str] = Field(None, description="Correct answer (index for MC, text for others, not used for chronological-order)")
    correctAnswers: Optional[List[int]] = Field(None, description="Correct answers for select-all-that-apply questions")
    items: Optional[List[str]] = Field(None, description="Items for chronological-order questions")
    correctOrder: Optional[List[int]] = Field(None, description="Correct order indices for chronological-order questions")
    points: int = Field(1, ge=1, le=100, description="Points for correct answer")
    explanation: Optional[str] = Field(None, max_length=500)

class QuestionInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    question: str
    options: List[str] = []
    correctAnswer: Optional[str] = None  # String representation: index for MC, text for others, not used for chronological-order
    correctAnswers: Optional[List[int]] = None  # For select-all-that-apply questions
    items: Optional[List[str]] = None  # For chronological-order questions
    correctOrder: Optional[List[int]] = None  # For chronological-order questions
    points: int
    explanation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuestionResponse(BaseModel):
    id: str
    type: str
    question: str
    options: List[str] = []
    correctAnswers: Optional[List[int]] = None  # For select-all-that-apply questions
    items: Optional[List[str]] = None  # For chronological-order questions
    correctOrder: Optional[List[int]] = None  # For chronological-order questions
    points: int
    explanation: Optional[str] = None
    created_at: datetime

class QuizCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Quiz title")
    description: Optional[str] = Field(None, max_length=1000)
    courseId: Optional[str] = None  # Optional - can be standalone
    programId: Optional[str] = None  # Optional - can be standalone
    questions: List[QuestionCreate] = Field(..., min_items=1, description="Quiz must have at least one question")
    timeLimit: Optional[int] = Field(None, ge=1, le=300, description="Time limit in minutes (1-300)")
    attempts: int = Field(1, ge=1, le=10, description="Number of allowed attempts (1-10)")
    passingScore: float = Field(70.0, ge=0.0, le=100.0, description="Passing score percentage")
    shuffleQuestions: bool = False
    showResults: bool = True  # Show results immediately after completion
    isPublished: bool = False
    
class QuizInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    courseId: Optional[str] = None
    courseName: Optional[str] = None  # Denormalized
    programId: Optional[str] = None
    programName: Optional[str] = None  # Denormalized
    questions: List[QuestionInDB]
    timeLimit: Optional[int] = None
    attempts: int
    passingScore: float
    shuffleQuestions: bool
    showResults: bool
    isPublished: bool
    totalPoints: int = 0  # Calculated field
    questionCount: int = 0  # Calculated field
    createdBy: str
    createdByName: str  # Denormalized
    isActive: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class QuizResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    courseId: Optional[str] = None
    courseName: Optional[str] = None
    programId: Optional[str] = None
    programName: Optional[str] = None
    timeLimit: Optional[int] = None
    attempts: int
    passingScore: float
    shuffleQuestions: bool
    showResults: bool
    isPublished: bool
    totalPoints: int
    questionCount: int
    createdBy: str
    createdByName: str
    isActive: bool
    created_at: datetime
    updated_at: datetime

class QuizWithQuestionsResponse(QuizResponse):
    questions: List[QuestionResponse]

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    courseId: Optional[str] = None
    programId: Optional[str] = None
    timeLimit: Optional[int] = None
    attempts: Optional[int] = None
    passingScore: Optional[float] = None
    shuffleQuestions: Optional[bool] = None
    showResults: Optional[bool] = None
    isPublished: Optional[bool] = None

class QuizAttemptCreate(BaseModel):
    quizId: str
    answers: List[str]  # Student's answers in order

class QuizAttemptInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quizId: str
    quizTitle: str  # Denormalized
    studentId: str
    studentName: str  # Denormalized
    answers: List[str]
    score: float = 0.0  # Percentage
    pointsEarned: int = 0
    totalPoints: int = 0
    isPassed: bool = False
    timeSpent: Optional[int] = None  # Minutes
    startedAt: datetime = Field(default_factory=datetime.utcnow)
    completedAt: Optional[datetime] = None
    attemptNumber: int = 1
    isActive: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuizAttemptResponse(BaseModel):
    id: str
    quizId: str
    quizTitle: str
    studentId: str
    studentName: str
    score: float
    pointsEarned: int
    totalPoints: int
    isPassed: bool
    timeSpent: Optional[int] = None
    startedAt: datetime
    completedAt: Optional[datetime] = None
    attemptNumber: int
    isActive: bool
    created_at: datetime

class QuizAttemptWithAnswersResponse(QuizAttemptResponse):
    answers: List[str]


# =============================================================================
# FINAL TEST MODELS (PROGRAM-LEVEL TESTS)
# =============================================================================

class FinalTestCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Final test title")
    description: Optional[str] = Field(None, max_length=1000)
    programId: str = Field(..., description="Program ID this test belongs to")
    questions: List[QuestionCreate] = Field(..., min_items=1, description="Test must have at least one question")
    timeLimit: Optional[int] = Field(None, ge=1, le=480, description="Time limit in minutes (1-480)")
    maxAttempts: int = Field(2, ge=1, le=5, description="Maximum attempts allowed (1-5)")
    passingScore: float = Field(75.0, ge=0.0, le=100.0, description="Passing score percentage")
    shuffleQuestions: bool = False
    showResults: bool = True
    isPublished: bool = False

class FinalTestInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    programId: str
    programName: Optional[str] = None  # Denormalized
    questions: List[QuestionInDB]
    timeLimit: Optional[int] = None
    maxAttempts: int
    passingScore: float
    shuffleQuestions: bool
    showResults: bool
    isPublished: bool
    totalPoints: int = 0  # Calculated field
    questionCount: int = 0  # Calculated field
    createdBy: str
    createdByName: str  # Denormalized
    isActive: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FinalTestResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    programId: str
    programName: Optional[str] = None
    timeLimit: Optional[int] = None
    maxAttempts: int
    passingScore: float
    shuffleQuestions: bool
    showResults: bool
    isPublished: bool
    totalPoints: int
    questionCount: int
    createdBy: str
    createdByName: str
    isActive: bool
    created_at: datetime
    updated_at: datetime

class FinalTestWithQuestionsResponse(FinalTestResponse):
    questions: List[QuestionResponse]

class FinalTestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    timeLimit: Optional[int] = None
    maxAttempts: Optional[int] = None
    passingScore: Optional[float] = None
    shuffleQuestions: Optional[bool] = None
    showResults: Optional[bool] = None
    isPublished: Optional[bool] = None

class FinalTestAttemptCreate(BaseModel):
    testId: str
    programId: Optional[str] = None
    answers: List[Dict[str, Any]] = Field(..., description="Student answers with questionId and answer fields")
    timeSpent: Optional[int] = None  # Time spent in seconds

class FinalTestAttemptInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    testId: str
    testTitle: str  # Denormalized
    programId: str  # Denormalized
    programName: str  # Denormalized
    studentId: str
    studentName: str  # Denormalized
    answers: List[Dict[str, Any]]  # Student answers with questionId and answer
    score: float = 0.0  # Percentage
    pointsEarned: int = 0
    totalPoints: int = 0
    isPassed: bool = False
    timeSpent: Optional[int] = None  # Seconds
    startedAt: datetime = Field(default_factory=datetime.utcnow)
    completedAt: Optional[datetime] = None
    attemptNumber: int = 1
    status: str = "completed"  # in_progress, completed, timed_out
    isActive: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FinalTestAttemptResponse(BaseModel):
    id: str
    testId: str
    testTitle: str
    programId: str
    programName: str
    studentId: str
    studentName: str
    score: float
    pointsEarned: int
    totalPoints: int
    isPassed: bool
    timeSpent: Optional[int] = None
    startedAt: datetime
    completedAt: Optional[datetime] = None
    attemptNumber: int
    status: str
    isActive: bool
    created_at: datetime

class FinalTestAttemptWithAnswersResponse(FinalTestAttemptResponse):
    answers: List[Dict[str, Any]]


# =============================================================================
# QUIZ/ASSESSMENT ENDPOINTS
# =============================================================================

@api_router.post("/quizzes", response_model=QuizWithQuestionsResponse)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new quiz (instructors and admins only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create quizzes"
        )
    
    # Validate course if specified
    course_name = None
    if quiz_data.courseId:
        course = await db.courses.find_one({"id": quiz_data.courseId})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified course not found"
            )
        course_name = course['title']
    
    # Validate program if specified
    program_name = None
    if quiz_data.programId:
        program = await db.programs.find_one({"id": quiz_data.programId})
        if not program:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified program not found"
            )
        program_name = program['title']
    
    # Process questions
    questions = []
    total_points = 0
    for q_data in quiz_data.questions:
        question = QuestionInDB(**q_data.dict())
        questions.append(question)
        total_points += q_data.points
    
    # Create quiz dictionary
    quiz_dict = {
        "id": str(uuid.uuid4()),
        "title": quiz_data.title,
        "description": quiz_data.description,
        "courseId": quiz_data.courseId,
        "courseName": course_name,
        "programId": quiz_data.programId,
        "programName": program_name,
        "questions": [q.dict() for q in questions],
        "timeLimit": quiz_data.timeLimit,
        "attempts": quiz_data.attempts,
        "passingScore": quiz_data.passingScore,
        "shuffleQuestions": quiz_data.shuffleQuestions,
        "showResults": quiz_data.showResults,
        "isPublished": quiz_data.isPublished,
        "totalPoints": total_points,
        "questionCount": len(questions),
        "createdBy": current_user.id,
        "createdByName": current_user.full_name,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert quiz into database
    await db.quizzes.insert_one(quiz_dict)
    
    # Prepare response with questions
    quiz_response = QuizWithQuestionsResponse(**quiz_dict)
    quiz_response.questions = [QuestionResponse(**q.dict()) for q in questions]
    
    return quiz_response

@api_router.get("/quizzes", response_model=List[QuizResponse])
async def get_quizzes(
    current_user: UserResponse = Depends(get_current_user),
    course_id: Optional[str] = None,
    program_id: Optional[str] = None,
    published_only: bool = True
):
    """Get quizzes with optional filtering."""
    
    # Base query
    query = {"isActive": True}
    
    # Add course filter if specified
    if course_id:
        query["courseId"] = course_id
    
    # Add program filter if specified
    if program_id:
        query["programId"] = program_id
    
    # Role-based filtering
    if current_user.role == 'learner':
        # Students only see published quizzes
        query["isPublished"] = True
    elif current_user.role == 'instructor':
        # Instructors see their own quizzes + published ones
        if published_only:
            query["$or"] = [
                {"isPublished": True},
                {"createdBy": current_user.id}
            ]
    # Admins see all quizzes (no additional filtering)
    elif published_only and current_user.role == 'admin':
        query["isPublished"] = True
    
    quizzes = await db.quizzes.find(query).sort("created_at", -1).to_list(1000)
    return [QuizResponse(**quiz) for quiz in quizzes]

@api_router.get("/quizzes/{quiz_id}", response_model=QuizWithQuestionsResponse)
async def get_quiz(
    quiz_id: str,
    current_user: UserResponse = Depends(get_current_user),
    include_answers: bool = False
):
    """Get a specific quiz by ID."""
    quiz = await db.quizzes.find_one({"id": quiz_id, "isActive": True})
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check permissions for unpublished quizzes
    if not quiz.get('isPublished', False):
        if current_user.role == 'learner':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Quiz is not published"
            )
        elif current_user.role == 'instructor' and quiz['createdBy'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view quizzes you created"
            )
    
    # Prepare questions (hide correct answers for students unless specifically requested)
    questions = []
    for q in quiz['questions']:
        question = QuestionResponse(**q)
        if current_user.role == 'learner' and not include_answers:
            # Don't include correct answers or explanations for students
            question_dict = question.dict()
            question_dict.pop('explanation', None)
            question = QuestionResponse(**question_dict)
        questions.append(question)
    
    quiz_response = QuizWithQuestionsResponse(**quiz)
    quiz_response.questions = questions
    
    return quiz_response

@api_router.get("/quizzes/my-quizzes", response_model=List[QuizResponse])
async def get_my_quizzes(current_user: UserResponse = Depends(get_current_user)):
    """Get quizzes created by current user."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can view their created quizzes"
        )
    
    quizzes = await db.quizzes.find({
        "createdBy": current_user.id,
        "isActive": True
    }).sort("created_at", -1).to_list(1000)
    
    return [QuizResponse(**quiz) for quiz in quizzes]

@api_router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: str,
    quiz_data: QuizUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a quiz (only by creator or admin)."""
    # Find the quiz
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and quiz['createdBy'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit quizzes you created"
        )
    
    # Update quiz
    update_data = {k: v for k, v in quiz_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Update denormalized fields if necessary
    if quiz_data.courseId:
        course = await db.courses.find_one({"id": quiz_data.courseId})
        update_data["courseName"] = course['title'] if course else None
    
    if quiz_data.programId:
        program = await db.programs.find_one({"id": quiz_data.programId})
        update_data["programName"] = program['title'] if program else None
    
    result = await db.quizzes.update_one(
        {"id": quiz_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found or no changes made"
        )
    
    # Get updated quiz
    updated_quiz = await db.quizzes.find_one({"id": quiz_id})
    return QuizResponse(**updated_quiz)

@api_router.delete("/quizzes/{quiz_id}")
async def delete_quiz(
    quiz_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a quiz (only by creator or admin)."""
    # Find the quiz
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and quiz['createdBy'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete quizzes you created"
        )
    
    # Check if quiz has attempts
    attempt_count = await db.quiz_attempts.count_documents({"quizId": quiz_id, "isActive": True})
    if attempt_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete quiz with {attempt_count} student attempt(s). Consider unpublishing instead."
        )
    
    # Soft delete the quiz
    result = await db.quizzes.update_one(
        {"id": quiz_id},
        {"$set": {"isActive": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return {"message": f"Quiz '{quiz['title']}' has been successfully deleted"}

@api_router.post("/quiz-attempts", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    attempt_data: QuizAttemptCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Submit a quiz attempt (learners only)."""
    if current_user.role != 'learner':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only learners can submit quiz attempts"
        )
    
    # Get quiz
    quiz = await db.quizzes.find_one({"id": attempt_data.quizId, "isActive": True})
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if not quiz.get('isPublished', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quiz is not published"
        )
    
    # Check attempt limit
    existing_attempts = await db.quiz_attempts.count_documents({
        "quizId": attempt_data.quizId,
        "studentId": current_user.id,
        "isActive": True
    })
    
    if existing_attempts >= quiz.get('attempts', 1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum number of attempts ({quiz.get('attempts', 1)}) reached"
        )
    
    # Validate answers count
    if len(attempt_data.answers) != len(quiz['questions']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected {len(quiz['questions'])} answers, got {len(attempt_data.answers)}"
        )
    
    # Calculate score
    points_earned = 0
    total_points = quiz.get('totalPoints', 0)
    
    for i, (answer, question) in enumerate(zip(attempt_data.answers, quiz['questions'])):
        if question['type'] == 'multiple_choice':
            try:
                # Handle both string and integer answers
                answer_index = int(answer) if answer.isdigit() else -1
                correct_index = int(question['correctAnswer']) if question['correctAnswer'].isdigit() else -1
                
                if answer_index >= 0 and correct_index >= 0 and answer_index == correct_index:
                    points_earned += question.get('points', 1)
            except (ValueError, AttributeError):
                # Invalid answer format or missing correctAnswer
                pass
        elif question['type'] == 'true_false':
            # Handle case-insensitive comparison
            if (answer and question.get('correctAnswer') and 
                answer.lower().strip() == question['correctAnswer'].lower().strip()):
                points_earned += question.get('points', 1)
        elif question['type'] in ['short_answer', 'essay']:
            # For exact match on short answers (case-insensitive)
            if (question['type'] == 'short_answer' and answer and question.get('correctAnswer') and
                answer.lower().strip() == question['correctAnswer'].lower().strip()):
                points_earned += question.get('points', 1)
            # Essays require manual grading - skip for now
    
    # Calculate percentage score
    score_percentage = (points_earned / total_points * 100) if total_points > 0 else 0
    is_passed = score_percentage >= quiz.get('passingScore', 70.0)
    
    # Create attempt record
    attempt_dict = {
        "id": str(uuid.uuid4()),
        "quizId": attempt_data.quizId,
        "quizTitle": quiz['title'],
        "studentId": current_user.id,
        "studentName": current_user.full_name,
        "userId": current_user.id,  # Add userId field for analytics
        "answers": attempt_data.answers,
        "score": round(score_percentage, 2),
        "pointsEarned": points_earned,
        "totalPoints": total_points,
        "isPassed": is_passed,
        "status": "completed",  # Add status field for analytics
        "startedAt": datetime.utcnow(),  # Add missing startedAt field
        "completedAt": datetime.utcnow(),
        "attemptNumber": existing_attempts + 1,
        "isActive": True,
        "created_at": datetime.utcnow()
    }
    
    # Insert attempt into database
    await db.quiz_attempts.insert_one(attempt_dict)
    
    return QuizAttemptResponse(**attempt_dict)

@api_router.get("/quiz-attempts", response_model=List[QuizAttemptResponse])
async def get_quiz_attempts(
    current_user: UserResponse = Depends(get_current_user),
    quiz_id: Optional[str] = None,
    student_id: Optional[str] = None
):
    """Get quiz attempts with optional filtering."""
    
    # Base query
    query = {"isActive": True}
    
    # Role-based filtering
    if current_user.role == 'learner':
        # Students only see their own attempts
        query["studentId"] = current_user.id
    elif current_user.role in ['instructor', 'admin']:
        # Instructors and admins can filter by student
        if student_id:
            query["studentId"] = student_id
    
    # Add quiz filter if specified
    if quiz_id:
        query["quizId"] = quiz_id
    
    attempts = await db.quiz_attempts.find(query).sort("created_at", -1).to_list(1000)
    
    # Handle missing fields in existing attempts for backward compatibility
    processed_attempts = []
    for attempt in attempts:
        # Ensure required fields exist
        if 'startedAt' not in attempt:
            attempt['startedAt'] = attempt.get('created_at', datetime.utcnow())
        if 'userId' not in attempt:
            attempt['userId'] = attempt.get('studentId', '')
        if 'status' not in attempt:
            attempt['status'] = 'completed' if attempt.get('completedAt') else 'in_progress'
        
        processed_attempts.append(QuizAttemptResponse(**attempt))
    
    return processed_attempts

@api_router.get("/quiz-attempts/{attempt_id}", response_model=QuizAttemptWithAnswersResponse)
async def get_quiz_attempt(
    attempt_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific quiz attempt by ID."""
    attempt = await db.quiz_attempts.find_one({"id": attempt_id, "isActive": True})
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found"
        )
    
    # Check permissions
    if (current_user.role == 'learner' and 
        attempt['studentId'] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own quiz attempts"
        )
    
    return QuizAttemptWithAnswersResponse(**attempt)


# =============================================================================
# FINAL TEST ENDPOINTS (PROGRAM-LEVEL TESTS)
# =============================================================================

@api_router.post("/final-tests", response_model=FinalTestWithQuestionsResponse)
async def create_final_test(
    test_data: FinalTestCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new final test (instructors and admins only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create final tests"
        )
    
    # Verify program exists
    program = await db.programs.find_one({"id": test_data.programId})
    if not program:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified program not found"
        )
    
    # Check if user has permission to create tests for this program
    if (current_user.role != 'admin' and 
        program.get('instructorId') != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create tests for your own programs"
        )
    
    # Process questions and calculate totals
    questions_data = []
    total_points = 0
    for q_data in test_data.questions:
        question_dict = q_data.dict()
        question_dict['id'] = str(uuid.uuid4())
        question_dict['created_at'] = datetime.utcnow()
        questions_data.append(QuestionInDB(**question_dict))
        total_points += q_data.points
    
    # Create final test dictionary
    test_dict = {
        "id": str(uuid.uuid4()),
        **test_data.dict(exclude={'questions'}),
        "programName": program.get('title', 'Unknown Program'),
        "questions": [q.dict() for q in questions_data],
        "totalPoints": total_points,
        "questionCount": len(questions_data),
        "createdBy": current_user.id,
        "createdByName": current_user.full_name,
        "isActive": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert test into database
    await db.final_tests.insert_one(test_dict)
    
    return FinalTestWithQuestionsResponse(**{
        **test_dict,
        "questions": [QuestionResponse(**q.dict()) for q in questions_data]
    })

@api_router.get("/final-tests", response_model=List[FinalTestResponse])
async def get_all_final_tests(
    current_user: UserResponse = Depends(get_current_user),
    program_id: Optional[str] = None,
    published_only: bool = True
):
    """Get all final tests with optional filtering."""
    
    # Base query
    query = {"isActive": True}
    
    # Add program filter if specified
    if program_id:
        query["programId"] = program_id
    
    # Role-based filtering
    if current_user.role == 'learner':
        # Students can only see published tests
        query["isPublished"] = True
    elif current_user.role == 'instructor' and published_only:
        # Instructors can see published tests for all programs, or all tests for their programs
        instructor_programs = await db.programs.find({"instructorId": current_user.id}).to_list(1000)
        instructor_program_ids = [p['id'] for p in instructor_programs]
        
        query = {
            "$and": [
                query,
                {
                    "$or": [
                        {"isPublished": True},
                        {"programId": {"$in": instructor_program_ids}}
                    ]
                }
            ]
        }
    # Admins can see all tests regardless of published status
    
    tests = await db.final_tests.find(query).sort("created_at", -1).to_list(1000)
    return [FinalTestResponse(**test) for test in tests]

@api_router.get("/final-tests/my-tests", response_model=List[FinalTestResponse])
async def get_my_final_tests(current_user: UserResponse = Depends(get_current_user)):
    """Get final tests created by current user."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can access test management"
        )
    
    tests = await db.final_tests.find({
        "createdBy": current_user.id,
        "isActive": True
    }).sort("created_at", -1).to_list(1000)
    
    return [FinalTestResponse(**test) for test in tests]

@api_router.get("/final-tests/{test_id}", response_model=FinalTestWithQuestionsResponse)
async def get_final_test(
    test_id: str,
    current_user: UserResponse = Depends(get_current_user),
    include_answers: bool = False
):
    """Get a specific final test by ID."""
    test = await db.final_tests.find_one({"id": test_id, "isActive": True})
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final test not found"
        )
    
    # Check access permissions
    if current_user.role == 'learner' and not test.get('isPublished', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test is not published"
        )
    
    # Check if instructor can access (own tests or published tests)
    if (current_user.role == 'instructor' and 
        test['createdBy'] != current_user.id and 
        not test.get('isPublished', False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tests or published tests"
        )
    
    # Prepare questions (hide correct answers for students unless include_answers is True)
    questions = []
    for question in test['questions']:
        q_dict = dict(question)
        if (current_user.role == 'learner' and 
            not include_answers and 
            'correctAnswer' in q_dict):
            q_dict.pop('correctAnswer', None)
        questions.append(QuestionResponse(**q_dict))
    
    return FinalTestWithQuestionsResponse(**{
        **test,
        "questions": questions
    })

@api_router.put("/final-tests/{test_id}", response_model=FinalTestResponse)
async def update_final_test(
    test_id: str,
    test_data: FinalTestUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a final test (only by test creator or admin)."""
    # Find the test
    test = await db.final_tests.find_one({"id": test_id, "isActive": True})
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final test not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and test['createdBy'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own tests"
        )
    
    # Check if test has attempts
    attempt_count = await db.final_test_attempts.count_documents({"testId": test_id, "isActive": True})
    if attempt_count > 0 and test_data.passingScore is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify passing score - test has {attempt_count} student attempt(s)"
        )
    
    # Update test
    update_data = {k: v for k, v in test_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.final_tests.update_one(
        {"id": test_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final test not found or no changes made"
        )
    
    # Get updated test
    updated_test = await db.final_tests.find_one({"id": test_id})
    return FinalTestResponse(**updated_test)

@api_router.delete("/final-tests/{test_id}")
async def delete_final_test(
    test_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a final test (only by test creator or admin)."""
    # Find the test
    test = await db.final_tests.find_one({"id": test_id, "isActive": True})
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final test not found"
        )
    
    # Check permissions
    if current_user.role != 'admin' and test['createdBy'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tests"
        )
    
    # Check if test has attempts
    attempt_count = await db.final_test_attempts.count_documents({"testId": test_id, "isActive": True})
    if attempt_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete test with {attempt_count} student attempt(s). Consider unpublishing instead."
        )
    
    # Soft delete the test
    result = await db.final_tests.update_one(
        {"id": test_id},
        {"$set": {"isActive": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final test not found"
        )
    
    return {"message": f"Final test '{test['title']}' has been successfully deleted"}

@api_router.post("/final-test-attempts", response_model=FinalTestAttemptResponse)
async def submit_final_test_attempt(
    attempt_data: FinalTestAttemptCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Submit a final test attempt (learners only)."""
    if current_user.role != 'learner':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only learners can submit test attempts"
        )
    
    # Get test
    test = await db.final_tests.find_one({"id": attempt_data.testId, "isActive": True})
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final test not found"
        )
    
    if not test.get('isPublished', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test is not published"
        )
    
    # Check attempt limit
    existing_attempts = await db.final_test_attempts.count_documents({
        "testId": attempt_data.testId,
        "studentId": current_user.id,
        "isActive": True
    })
    
    if existing_attempts >= test.get('maxAttempts', 2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum number of attempts ({test.get('maxAttempts', 2)}) reached"
        )
    
    # Validate answers count
    if len(attempt_data.answers) != len(test['questions']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected {len(test['questions'])} answers, got {len(attempt_data.answers)}"
        )
    
    # Calculate score with support for all question types
    points_earned = 0
    total_points = test.get('totalPoints', 0)
    
    # Create a mapping of question IDs to answers
    answer_map = {answer.get('questionId'): answer.get('answer') for answer in attempt_data.answers}
    
    for question in test['questions']:
        question_id = question.get('id')
        student_answer = answer_map.get(question_id)
        question_points = question.get('points', 1)
        
        if question['type'] == 'multiple_choice':
            try:
                answer_index = int(student_answer) if str(student_answer).isdigit() else -1
                correct_index = int(question['correctAnswer']) if str(question['correctAnswer']).isdigit() else -1
                
                if answer_index >= 0 and correct_index >= 0 and answer_index == correct_index:
                    points_earned += question_points
            except (ValueError, AttributeError, TypeError):
                pass
                
        elif question['type'] == 'true_false':
            if (student_answer is not None and question.get('correctAnswer') and 
                str(student_answer).lower().strip() == str(question['correctAnswer']).lower().strip()):
                points_earned += question_points
                
        elif question['type'] in ['short_answer', 'essay']:
            if (question['type'] == 'short_answer' and student_answer and question.get('correctAnswer') and
                str(student_answer).lower().strip() == str(question['correctAnswer']).lower().strip()):
                points_earned += question_points
                
        elif question['type'] == 'select-all-that-apply':
            # Student answer should be a list of indices
            if isinstance(student_answer, list) and question.get('correctAnswers'):
                # Sort both lists to compare regardless of order
                student_set = set(student_answer) if student_answer else set()
                correct_set = set(question['correctAnswers']) if question['correctAnswers'] else set()
                
                # All-or-nothing scoring: full points if all correct, zero otherwise
                if student_set == correct_set:
                    points_earned += question_points
                    
        elif question['type'] == 'chronological-order':
            # Student answer should be a list of indices representing the order
            if isinstance(student_answer, list) and question.get('correctOrder'):
                # Compare the order arrays directly
                if student_answer == question['correctOrder']:
                    points_earned += question_points
    
    # Calculate percentage score
    score_percentage = (points_earned / total_points * 100) if total_points > 0 else 0
    is_passed = score_percentage >= test.get('passingScore', 75.0)
    
    # Get program info
    program = await db.programs.find_one({"id": test['programId']})
    program_name = program.get('title', 'Unknown Program') if program else 'Unknown Program'
    
    # Create attempt record
    attempt_dict = {
        "id": str(uuid.uuid4()),
        "testId": attempt_data.testId,
        "testTitle": test['title'],
        "programId": test['programId'],
        "programName": program_name,
        "studentId": current_user.id,
        "studentName": current_user.full_name,
        "answers": attempt_data.answers,
        "score": round(score_percentage, 2),
        "pointsEarned": points_earned,
        "totalPoints": total_points,
        "isPassed": is_passed,
        "timeSpent": attempt_data.timeSpent,
        "status": "completed",
        "startedAt": datetime.utcnow(),
        "completedAt": datetime.utcnow(),
        "attemptNumber": existing_attempts + 1,
        "isActive": True,
        "created_at": datetime.utcnow()
    }
    
    # Insert attempt into database
    await db.final_test_attempts.insert_one(attempt_dict)
    
    return FinalTestAttemptResponse(**attempt_dict)

@api_router.get("/final-test-attempts", response_model=List[FinalTestAttemptResponse])
async def get_final_test_attempts(
    current_user: UserResponse = Depends(get_current_user),
    test_id: Optional[str] = None,
    program_id: Optional[str] = None,
    student_id: Optional[str] = None
):
    """Get final test attempts with optional filtering."""
    
    # Base query
    query = {"isActive": True}
    
    # Role-based filtering
    if current_user.role == 'learner':
        # Students only see their own attempts
        query["studentId"] = current_user.id
    elif current_user.role in ['instructor', 'admin']:
        # Instructors and admins can filter by student
        if student_id:
            query["studentId"] = student_id
    
    # Add filters if specified
    if test_id:
        query["testId"] = test_id
    if program_id:
        query["programId"] = program_id
    
    attempts = await db.final_test_attempts.find(query).sort("created_at", -1).to_list(1000)
    
    return [FinalTestAttemptResponse(**attempt) for attempt in attempts]

@api_router.get("/final-test-attempts/{attempt_id}", response_model=FinalTestAttemptWithAnswersResponse)
async def get_final_test_attempt(
    attempt_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific final test attempt by ID."""
    attempt = await db.final_test_attempts.find_one({"id": attempt_id, "isActive": True})
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final test attempt not found"
        )
    
    # Check permissions
    if (current_user.role == 'learner' and 
        attempt['studentId'] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own test attempts"
        )
    
    return FinalTestAttemptWithAnswersResponse(**attempt)


# =============================================================================
# ANALYTICS MODELS
# =============================================================================

class UserStatsResponse(BaseModel):
    totalUsers: int
    activeUsers: int
    newUsersThisMonth: int
    usersByRole: dict  # {"admin": 1, "instructor": 5, "learner": 150}
    usersByDepartment: dict

class CourseStatsResponse(BaseModel):
    totalCourses: int
    publishedCourses: int
    draftCourses: int
    coursesThisMonth: int
    coursesByCategory: dict
    enrollmentStats: dict  # {"total": 500, "thisMonth": 50}

class QuizStatsResponse(BaseModel):
    totalQuizzes: int
    publishedQuizzes: int
    totalAttempts: int
    averageScore: float
    passRate: float
    quizzesThisMonth: int

class EnrollmentStatsResponse(BaseModel):
    totalEnrollments: int
    activeEnrollments: int
    completedEnrollments: int
    enrollmentsThisMonth: int
    topCourses: List[dict]  # Top 5 courses by enrollment

class CertificateStatsResponse(BaseModel):
    totalCertificates: int
    certificatesThisMonth: int
    certificatesByType: dict
    certificatesByStatus: dict

class SystemStatsResponse(BaseModel):
    users: UserStatsResponse
    courses: CourseStatsResponse
    quizzes: QuizStatsResponse
    enrollments: EnrollmentStatsResponse
    certificates: CertificateStatsResponse
    announcements: dict

class CourseAnalyticsResponse(BaseModel):
    courseId: str
    courseName: str
    totalEnrollments: int
    activeEnrollments: int
    completionRate: float
    averageProgress: float
    quizPerformance: dict
    enrollmentTrend: List[dict]  # Monthly enrollment data

class UserAnalyticsResponse(BaseModel):
    userId: str
    userName: str
    role: str
    enrolledCourses: int
    completedCourses: int
    averageScore: float
    totalQuizAttempts: int
    certificatesEarned: int
    lastActivity: Optional[datetime] = None


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@api_router.get("/analytics/system-stats", response_model=SystemStatsResponse)
async def get_system_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get comprehensive system statistics (admins and instructors only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can view system statistics"
        )
    
    # Calculate date ranges
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    try:
        # User Statistics
        total_users = await db.users.count_documents({"is_active": True})
        active_users = await db.users.count_documents({"is_active": True})
        new_users_this_month = await db.users.count_documents({
            "created_at": {"$gte": start_of_month},
            "is_active": True
        })
        
        # Users by role
        user_roles_pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        users_by_role_cursor = db.users.aggregate(user_roles_pipeline)
        users_by_role = {doc["_id"]: doc["count"] async for doc in users_by_role_cursor}
        
        # Users by department
        dept_pipeline = [
            {"$match": {"is_active": True, "department": {"$ne": None}}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}}}
        ]
        users_by_dept_cursor = db.users.aggregate(dept_pipeline)
        users_by_department = {doc["_id"]: doc["count"] async for doc in users_by_dept_cursor}
        
        user_stats = UserStatsResponse(
            totalUsers=total_users,
            activeUsers=active_users,
            newUsersThisMonth=new_users_this_month,
            usersByRole=users_by_role,
            usersByDepartment=users_by_department
        )
        
        # Course Statistics
        total_courses = await db.courses.count_documents({"is_active": True})
        published_courses = await db.courses.count_documents({"status": "published", "is_active": True})
        draft_courses = await db.courses.count_documents({"status": "draft", "is_active": True})
        courses_this_month = await db.courses.count_documents({
            "created_at": {"$gte": start_of_month},
            "is_active": True
        })
        
        # Courses by category
        category_pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        courses_by_cat_cursor = db.courses.aggregate(category_pipeline)
        courses_by_category = {doc["_id"]: doc["count"] async for doc in courses_by_cat_cursor}
        
        total_enrollments = await db.enrollments.count_documents({"isActive": True})
        enrollments_this_month = await db.enrollments.count_documents({
            "created_at": {"$gte": start_of_month},
            "isActive": True
        })
        
        course_stats = CourseStatsResponse(
            totalCourses=total_courses,
            publishedCourses=published_courses,
            draftCourses=draft_courses,
            coursesThisMonth=courses_this_month,
            coursesByCategory=courses_by_category,
            enrollmentStats={"total": total_enrollments, "thisMonth": enrollments_this_month}
        )
        
        # Quiz Statistics - Read from enrollments instead of quiz_attempts
        # Count courses with quiz lessons as total quizzes
        quiz_courses_pipeline = [
            {"$match": {"is_active": True}},
            {"$unwind": {"path": "$modules", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$modules.lessons", "preserveNullAndEmptyArrays": True}},
            {"$match": {"modules.lessons.type": "quiz"}},
            {"$group": {"_id": "$id"}}
        ]
        quiz_courses_cursor = db.courses.aggregate(quiz_courses_pipeline)
        quiz_courses = await quiz_courses_cursor.to_list(None)
        total_quizzes = len(quiz_courses)
        
        # Published quizzes (courses with quiz lessons that are published)
        published_quiz_courses_pipeline = [
            {"$match": {"is_active": True, "status": "published"}},
            {"$unwind": {"path": "$modules", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$modules.lessons", "preserveNullAndEmptyArrays": True}},
            {"$match": {"modules.lessons.type": "quiz"}},
            {"$group": {"_id": "$id"}}
        ]
        published_quiz_courses_cursor = db.courses.aggregate(published_quiz_courses_pipeline)
        published_quiz_courses = await published_quiz_courses_cursor.to_list(None)
        published_quizzes = len(published_quiz_courses)
        
        # Quiz courses created this month
        quiz_courses_month_pipeline = [
            {"$match": {"is_active": True, "created_at": {"$gte": start_of_month}}},
            {"$unwind": {"path": "$modules", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$modules.lessons", "preserveNullAndEmptyArrays": True}},
            {"$match": {"modules.lessons.type": "quiz"}},
            {"$group": {"_id": "$id"}}
        ]
        quiz_courses_month_cursor = db.courses.aggregate(quiz_courses_month_pipeline)
        quiz_courses_month = await quiz_courses_month_cursor.to_list(None)
        quizzes_this_month = len(quiz_courses_month)
        
        # Get quiz completion data from enrollments (progress >= 100 indicates quiz completion)
        total_attempts = await db.enrollments.count_documents({
            "isActive": True, 
            "progress": {"$gte": 100}
        })
        
        # Calculate average score and pass rate from enrollment progress
        # In this system, progress of 100% means quiz passed, anything less means failed
        enrollment_stats_pipeline = [
            {"$match": {"isActive": True, "progress": {"$gt": 0}}},
            {"$group": {
                "_id": None,
                "avgProgress": {"$avg": "$progress"},
                "totalPassed": {"$sum": {"$cond": [{"$gte": ["$progress", 100]}, 1, 0]}},
                "totalAttempts": {"$sum": 1}
            }}
        ]
        enrollment_stats_cursor = db.enrollments.aggregate(enrollment_stats_pipeline)
        enrollment_stats = await enrollment_stats_cursor.to_list(1)
        
        average_score = enrollment_stats[0]["avgProgress"] if enrollment_stats else 0.0
        pass_rate = (enrollment_stats[0]["totalPassed"] / enrollment_stats[0]["totalAttempts"] * 100) if enrollment_stats and enrollment_stats[0]["totalAttempts"] > 0 else 0.0
        
        quiz_stats = QuizStatsResponse(
            totalQuizzes=total_quizzes,
            publishedQuizzes=published_quizzes,
            totalAttempts=total_attempts,
            averageScore=round(average_score, 2),
            passRate=round(pass_rate, 2),
            quizzesThisMonth=quizzes_this_month
        )
        
        # Enrollment Statistics
        active_enrollments = await db.enrollments.count_documents({"status": "active", "isActive": True})
        completed_enrollments = await db.enrollments.count_documents({"status": "completed", "isActive": True})
        
        # Top courses by enrollment
        top_courses_pipeline = [
            {"$match": {"isActive": True}},
            {"$group": {"_id": "$courseId", "count": {"$sum": 1}, "courseName": {"$first": "$courseName"}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_courses_cursor = db.enrollments.aggregate(top_courses_pipeline)
        top_courses = [
            {"courseId": doc["_id"], "courseName": doc["courseName"], "enrollments": doc["count"]}
            async for doc in top_courses_cursor
        ]
        
        enrollment_stats = EnrollmentStatsResponse(
            totalEnrollments=total_enrollments,
            activeEnrollments=active_enrollments,
            completedEnrollments=completed_enrollments,
            enrollmentsThisMonth=enrollments_this_month,
            topCourses=top_courses
        )
        
        # Certificate Statistics
        total_certificates = await db.certificates.count_documents({"isActive": True})
        certificates_this_month = await db.certificates.count_documents({
            "created_at": {"$gte": start_of_month},
            "isActive": True
        })
        
        # Certificates by type
        cert_type_pipeline = [
            {"$match": {"isActive": True}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        cert_type_cursor = db.certificates.aggregate(cert_type_pipeline)
        certificates_by_type = {doc["_id"]: doc["count"] async for doc in cert_type_cursor}
        
        # Certificates by status
        cert_status_pipeline = [
            {"$match": {"isActive": True}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        cert_status_cursor = db.certificates.aggregate(cert_status_pipeline)
        certificates_by_status = {doc["_id"]: doc["count"] async for doc in cert_status_cursor}
        
        certificate_stats = CertificateStatsResponse(
            totalCertificates=total_certificates,
            certificatesThisMonth=certificates_this_month,
            certificatesByType=certificates_by_type,
            certificatesByStatus=certificates_by_status
        )
        
        # Announcement Statistics
        total_announcements = await db.announcements.count_documents({"isActive": True})
        announcements_this_month = await db.announcements.count_documents({
            "created_at": {"$gte": start_of_month},
            "isActive": True
        })
        
        announcement_stats = {
            "total": total_announcements,
            "thisMonth": announcements_this_month,
            "pinned": await db.announcements.count_documents({"isPinned": True, "isActive": True})
        }
        
        return SystemStatsResponse(
            users=user_stats,
            courses=course_stats,
            quizzes=quiz_stats,
            enrollments=enrollment_stats,
            certificates=certificate_stats,
            announcements=announcement_stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating system statistics: {str(e)}"
        )

@api_router.get("/analytics/course/{course_id}", response_model=CourseAnalyticsResponse)
async def get_course_analytics(
    course_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get detailed analytics for a specific course."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can view course analytics"
        )
    
    # Verify course exists
    course = await db.courses.find_one({"id": course_id, "is_active": True})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    try:
        # Basic enrollment stats
        total_enrollments = await db.enrollments.count_documents({"courseId": course_id, "isActive": True})
        active_enrollments = await db.enrollments.count_documents({
            "courseId": course_id,
            "status": "active",
            "isActive": True
        })
        completed_enrollments = await db.enrollments.count_documents({
            "courseId": course_id,
            "status": "completed",
            "isActive": True
        })
        
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Average progress calculation
        progress_pipeline = [
            {"$match": {"courseId": course_id, "isActive": True}},
            {"$group": {"_id": None, "avgProgress": {"$avg": "$progress"}}}
        ]
        progress_cursor = db.enrollments.aggregate(progress_pipeline)
        progress_stats = await progress_cursor.to_list(1)
        average_progress = progress_stats[0]["avgProgress"] if progress_stats else 0.0
        
        # Quiz performance for this course
        quiz_performance = {}
        course_quizzes = await db.quizzes.find({"courseId": course_id, "isActive": True}).to_list(100)
        if course_quizzes:
            quiz_ids = [quiz["id"] for quiz in course_quizzes]
            quiz_stats_pipeline = [
                {"$match": {"quizId": {"$in": quiz_ids}, "isActive": True}},
                {"$group": {
                    "_id": None,
                    "totalAttempts": {"$sum": 1},
                    "avgScore": {"$avg": "$score"},
                    "passRate": {"$avg": {"$cond": ["$isPassed", 1, 0]}}
                }}
            ]
            quiz_stats_cursor = db.quiz_attempts.aggregate(quiz_stats_pipeline)
            quiz_stats = await quiz_stats_cursor.to_list(1)
            
            if quiz_stats:
                quiz_performance = {
                    "totalAttempts": quiz_stats[0]["totalAttempts"],
                    "averageScore": round(quiz_stats[0]["avgScore"], 2),
                    "passRate": round(quiz_stats[0]["passRate"] * 100, 2)
                }
        
        # Enrollment trend (last 6 months)
        enrollment_trend = []
        for i in range(6):
            month_start = (datetime.utcnow().replace(day=1) - timedelta(days=i*30)).replace(hour=0, minute=0, second=0, microsecond=0)
            month_end = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
            
            month_enrollments = await db.enrollments.count_documents({
                "courseId": course_id,
                "created_at": {"$gte": month_start, "$lt": month_end},
                "isActive": True
            })
            
            enrollment_trend.insert(0, {
                "month": month_start.strftime("%Y-%m"),
                "enrollments": month_enrollments
            })
        
        return CourseAnalyticsResponse(
            courseId=course_id,
            courseName=course["title"],
            totalEnrollments=total_enrollments,
            activeEnrollments=active_enrollments,
            completionRate=round(completion_rate, 2),
            averageProgress=round(average_progress, 2),
            quizPerformance=quiz_performance,
            enrollmentTrend=enrollment_trend
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating course analytics: {str(e)}"
        )

@api_router.get("/analytics/user/{user_id}", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get detailed analytics for a specific user."""
    # Permission check
    if current_user.role == 'learner' and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Learners can only view their own analytics"
        )
    elif current_user.role not in ['instructor', 'admin', 'learner']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Verify user exists
    user = await db.users.find_one({"id": user_id, "is_active": True})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Enrollment statistics
        enrolled_courses = await db.enrollments.count_documents({
            "studentId": user_id,
            "isActive": True
        })
        completed_courses = await db.enrollments.count_documents({
            "studentId": user_id,
            "status": "completed",
            "isActive": True
        })
        
        # Quiz performance - count completed enrollments as quiz attempts
        total_quiz_attempts = await db.enrollments.count_documents({
            "studentId": user_id,
            "isActive": True,
            "progress": {"$gte": 100}
        })
        
        # Calculate average score from enrollment progress
        avg_score_pipeline = [
            {"$match": {
                "studentId": user_id, 
                "isActive": True, 
                "progress": {"$gt": 0}
            }},
            {"$group": {"_id": None, "avgScore": {"$avg": "$progress"}}}
        ]
        avg_score_cursor = db.enrollments.aggregate(avg_score_pipeline)
        avg_score_stats = await avg_score_cursor.to_list(1)
        average_score = avg_score_stats[0]["avgScore"] if avg_score_stats else 0.0
        
        # Certificates earned
        certificates_earned = await db.certificates.count_documents({
            "studentId": user_id,
            "isActive": True
        })
        
        # Last activity (latest enrollment or quiz attempt)
        last_enrollment = await db.enrollments.find({
            "studentId": user_id,
            "isActive": True
        }).sort("created_at", -1).limit(1).to_list(1)
        
        last_quiz_completion = await db.enrollments.find({
            "studentId": user_id,
            "isActive": True,
            "progress": {"$gte": 100}
        }).sort("completedAt", -1).limit(1).to_list(1)
        
        last_activity = None
        if last_enrollment or last_quiz_completion:
            enrollment_date = last_enrollment[0]["created_at"] if last_enrollment else datetime.min
            quiz_date = last_quiz_completion[0]["completedAt"] if last_quiz_completion else datetime.min
            last_activity = max(enrollment_date, quiz_date)
        
        return UserAnalyticsResponse(
            userId=user_id,
            userName=user["full_name"],
            role=user["role"],
            enrolledCourses=enrolled_courses,
            completedCourses=completed_courses,
            averageScore=round(average_score, 2),
            totalQuizAttempts=total_quiz_attempts,
            certificatesEarned=certificates_earned,
            lastActivity=last_activity
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating user analytics: {str(e)}"
        )

@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard(current_user: UserResponse = Depends(get_current_user)):
    """Get role-specific analytics dashboard data."""
    if current_user.role not in ['instructor', 'admin', 'learner']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )
    
    try:
        dashboard_data = {}
        
        if current_user.role == 'learner':
            # Student dashboard analytics
            enrolled_courses = await db.enrollments.count_documents({
                "studentId": current_user.id,
                "isActive": True
            })
            completed_courses = await db.enrollments.count_documents({
                "studentId": current_user.id,
                "status": "completed",
                "isActive": True
            })
            certificates_earned = await db.certificates.count_documents({
                "studentId": current_user.id,
                "isActive": True
            })
            
            # Recent quiz completions from enrollments (progress >= 100)
            recent_completions = await db.enrollments.find({
                "studentId": current_user.id,
                "isActive": True,
                "progress": {"$gte": 100}
            }).sort("completedAt", -1).limit(5).to_list(5)
            
            # Get course names for recent completions
            recent_attempts = []
            for completion in recent_completions:
                course = await db.courses.find_one({"id": completion["courseId"]})
                if course:
                    recent_attempts.append({
                        "quizTitle": f"Quiz - {course.get('title', 'Unknown Course')}",
                        "score": completion["progress"],
                        "isPassed": completion["progress"] >= 100,
                        "completedAt": completion.get("completedAt")
                    })
            
            dashboard_data = {
                "enrolledCourses": enrolled_courses,
                "completedCourses": completed_courses,
                "certificatesEarned": certificates_earned,
                "recentQuizAttempts": recent_attempts
            }
            
        elif current_user.role == 'instructor':
            # Instructor dashboard analytics
            created_courses = await db.courses.count_documents({
                "instructor_id": current_user.id,
                "is_active": True
            })
            # Count courses with quiz lessons created by this instructor
            instructor_quiz_courses = await db.courses.count_documents({
                "instructor_id": current_user.id,
                "is_active": True,
                "modules.lessons.type": "quiz"
            })
            
            # Students taught (unique students enrolled in instructor's courses)
            instructor_courses = await db.courses.find({
                "instructor_id": current_user.id,
                "is_active": True
            }).to_list(100)
            
            course_ids = [course["id"] for course in instructor_courses]
            students_taught = len(await db.enrollments.distinct("studentId", {
                "courseId": {"$in": course_ids},
                "isActive": True
            })) if course_ids else 0
            
            dashboard_data = {
                "createdCourses": created_courses,
                "createdQuizzes": instructor_quiz_courses,
                "studentsTaught": students_taught,
                "courseIds": course_ids
            }
            
        elif current_user.role == 'admin':
            # Admin dashboard analytics (simplified system overview)
            total_users = await db.users.count_documents({"is_active": True})
            total_courses = await db.courses.count_documents({"is_active": True})
            total_enrollments = await db.enrollments.count_documents({"isActive": True})
            total_certificates = await db.certificates.count_documents({"isActive": True})
            
            dashboard_data = {
                "totalUsers": total_users,
                "totalCourses": total_courses,
                "totalEnrollments": total_enrollments,
                "totalCertificates": total_certificates
            }
        
        return {"status": "success", "data": dashboard_data}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard analytics: {str(e)}"
        )


# =============================================================================
# GRADING SYSTEM FOR SUBJECTIVE QUESTIONS
# =============================================================================

# Pydantic models for grading endpoints
class SubjectiveSubmissionRequest(BaseModel):
    questionId: str
    questionText: str
    studentAnswer: str
    courseId: str
    lessonId: str
    questionType: str

class SubjectiveSubmissionsRequest(BaseModel):
    submissions: List[SubjectiveSubmissionRequest]

class SubjectiveQuestionSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    studentId: str
    studentName: str
    courseId: str
    lessonId: str
    questionId: str
    questionText: str
    studentAnswer: str
    submittedAt: datetime = Field(default_factory=datetime.utcnow)
    gradedAt: Optional[datetime] = None
    gradedBy: Optional[str] = None
    gradedByName: Optional[str] = None
    score: Optional[float] = None  # 0-100
    feedback: Optional[str] = None
    status: str = "pending"  # pending, graded, needs_review

class GradingRequest(BaseModel):
    score: float  # 0-100
    feedback: Optional[str] = None

@api_router.post("/quiz-submissions/subjective")
async def submit_subjective_answers(
    submission_request: SubjectiveSubmissionsRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Store subjective question submissions for grading."""
    logger.info(f"Received subjective submissions from user {current_user.id}: {len(submission_request.submissions)} submissions")
    try:
        # Store each submission in the database
        for submission_data in submission_request.submissions:
            submission_doc = {
                "id": str(uuid.uuid4()),
                "studentId": current_user.id,
                "studentName": current_user.full_name,
                "courseId": submission_data.courseId,
                "lessonId": submission_data.lessonId,
                "questionId": submission_data.questionId,
                "questionText": submission_data.questionText,
                "studentAnswer": submission_data.studentAnswer,
                "questionType": submission_data.questionType,
                "submittedAt": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
                "score": None,
                "feedback": None,
                "gradedAt": None,
                "gradedBy": None,
                "gradedByName": None
            }
            
            await db.subjective_submissions.insert_one(submission_doc)
            logger.info(f"Stored submission: {submission_doc['id']} for question {submission_doc['questionId']}")
        
        logger.info(f"Successfully stored {len(submission_request.submissions)} submissions")
        return {"success": True, "message": f"Submitted {len(submission_request.submissions)} subjective answers for grading"}
        
    except Exception as e:
        logger.error(f"Error storing subjective submissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store submissions")

@api_router.get("/courses/{course_id}/submissions")
async def get_course_submissions(
    course_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all subjective question submissions for a course (instructors only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can view submissions"
        )
    
    # Get actual submissions from the database
    submissions = []
    
    try:
        # Get submissions from the subjective_submissions collection
        submission_docs = await db.subjective_submissions.find({"courseId": course_id}).to_list(1000)
        
        for doc in submission_docs:
            submissions.append({
                "id": doc.get("id"),
                "studentId": doc.get("studentId"),
                "studentName": doc.get("studentName", "Unknown Student"),
                "courseId": doc.get("courseId"),
                "lessonId": doc.get("lessonId"),
                "questionId": doc.get("questionId"),
                "questionText": doc.get("questionText"),
                "studentAnswer": doc.get("studentAnswer"),
                "questionType": doc.get("questionType"),
                "submittedAt": doc.get("submittedAt"),
                "gradedAt": doc.get("gradedAt"),
                "gradedBy": doc.get("gradedBy"),
                "gradedByName": doc.get("gradedByName"),
                "score": doc.get("score"),
                "feedback": doc.get("feedback"),
                "status": doc.get("status", "pending"),
                "source": "quiz"
            })
        
        # Also check for final test submissions with subjective questions
        final_test_attempts = await db.final_test_attempts.find({"programId": {"$exists": True}}).to_list(1000)
        
        for attempt in final_test_attempts:
            student_id = attempt.get("studentId")
            if not student_id:
                continue
                
            # Get student info
            student = await db.users.find_one({"id": student_id})
            if not student:
                continue
            
            # Get the final test to check for subjective questions
            test = await db.final_tests.find_one({"id": attempt.get("testId")})
            if not test:
                continue
            
            # Extract subjective answers from the attempt
            for i, answer in enumerate(attempt.get("answers", [])):
                question_id = answer.get("questionId")
                student_answer = answer.get("answer")
                
                # Find the question details
                question = None
                for q in test.get("questions", []):
                    if q.get("id") == question_id:
                        question = q
                        break
                
                if question and question.get("type") in ["short-answer", "long-form"]:
                    submission_id = f"final-{attempt['id']}-{question_id}"
                    submissions.append({
                        "id": submission_id,
                        "studentId": student_id,
                        "studentName": student.get("full_name", "Unknown Student"),
                        "courseId": course_id,
                        "lessonId": "final-test",
                        "questionId": question_id,
                        "questionText": question.get("question", "Question text not available"),
                        "studentAnswer": student_answer,
                        "submittedAt": attempt.get("submittedAt", attempt.get("created_at")),
                        "gradedAt": None,
                        "gradedBy": None,
                        "gradedByName": None,
                        "score": None,
                        "feedback": None,
                        "status": "pending",
                        "source": "final_test"
                    })
        
        return {"submissions": submissions, "count": len(submissions)}
        
    except Exception as e:
        logger.error(f"Error fetching course submissions: {str(e)}")
        return {"submissions": [], "count": 0, "error": str(e)}

@api_router.post("/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: str,
    grading_data: GradingRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Grade a subjective question submission (instructors only)."""
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can grade submissions"
        )
    
    # Validate score
    if grading_data.score < 0 or grading_data.score > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score must be between 0 and 100"
        )
    
    # Store grading data in a separate collection
    grading_dict = {
        "id": str(uuid.uuid4()),
        "submissionId": submission_id,
        "gradedBy": current_user.id,
        "gradedByName": current_user.full_name,
        "score": grading_data.score,
        "feedback": grading_data.feedback,
        "gradedAt": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    # Check if already graded and update, otherwise insert
    existing_grade = await db.submission_grades.find_one({"submissionId": submission_id})
    
    if existing_grade:
        # Update existing grade
        await db.submission_grades.update_one(
            {"submissionId": submission_id},
            {"$set": grading_dict}
        )
        action = "updated"
    else:
        # Insert new grade
        await db.submission_grades.insert_one(grading_dict)
        action = "created"
    
    # Also update the submission status in subjective_submissions collection
    await db.subjective_submissions.update_one(
        {"id": submission_id},
        {"$set": {
            "status": "graded",
            "score": grading_data.score,
            "feedback": grading_data.feedback,
            "gradedAt": datetime.utcnow().isoformat(),
            "gradedBy": current_user.id,
            "gradedByName": current_user.full_name
        }}
    )
    
    return {
        "success": True,
        "action": action,
        "message": f"Submission grade {action} successfully",
        "submissionId": submission_id,
        "score": grading_data.score,
        "gradedBy": current_user.full_name,
        "gradedAt": datetime.utcnow()
    }

@api_router.get("/submissions/{submission_id}/grade")
async def get_submission_grade(
    submission_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get the grade for a specific submission."""
    grade = await db.submission_grades.find_one({"submissionId": submission_id})
    
    if not grade:
        return {"graded": False, "message": "Submission not yet graded"}
    
    return {
        "graded": True,
        "score": grade.get("score"),
        "feedback": grade.get("feedback"),
        "gradedBy": grade.get("gradedByName"),
        "gradedAt": grade.get("gradedAt"),
        "id": grade.get("id")
    }


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@api_router.get("/health")
async def health_check():
    """Health check endpoint for deployment verification."""
    try:
        # Test database connection
        await client.admin.command('ping')
        logger.info("Health check: Database connection successful")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Include the router in the main app
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "LMS API is running", "status": "active"}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    """Test database connection on startup"""
    try:
        logger.info("Testing database connection...")
        await client.admin.command('ping')
        logger.info("Database connection test successful")
        
        # Test if we can access our specific database
        collections = await db.list_collection_names()
        logger.info(f"Found {len(collections)} collections in database '{db_name}'")
        
    except Exception as e:
        logger.error(f"Database connection failed during startup: {str(e)}")
        # Don't raise here as it will prevent the app from starting
        # The health check endpoint will catch this

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Shutting down database client")
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=DEBUG)