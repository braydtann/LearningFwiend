from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


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
