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
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import re


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security setup
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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
    title: str
    description: str
    category: str
    duration: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    accessType: Optional[str] = "open"  # open, restricted, invitation
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

class EnrollmentResponse(BaseModel):
    id: str
    userId: str
    courseId: str
    enrolledAt: datetime
    progress: float = 0.0
    completedAt: Optional[datetime] = None
    status: str = "active"  # active, completed, dropped

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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()