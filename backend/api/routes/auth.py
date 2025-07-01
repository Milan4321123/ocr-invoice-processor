"""
Authentication API Routes
Handles login, token validation, and user management
"""
from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from typing import Dict, Any
import logging
from pydantic import BaseModel

from services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Security scheme for token validation
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    message: str

class UserResponse(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    is_active: bool

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    username = payload.get("sub")
    
    user = await auth_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/token", response_model=LoginResponse)
async def login_for_access_token(request: LoginRequest):
    """Login endpoint - authenticate user and return access token"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(request.username, request.password)
        if not user:
            logger.warning(f"❌ Failed login attempt for username: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user["username"]}
        )
        
        logger.info(f"✅ Successful login for user: {request.username}")
        
        return LoginResponse(
            access_token=access_token,
            username=user["username"],
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/login", response_model=LoginResponse)
async def form_login(username: str = Form(...), password: str = Form(...)):
    """Form-based login endpoint for frontend integration"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(username, password)
        if not user:
            logger.warning(f"❌ Failed login attempt for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user["username"]}
        )
        
        logger.info(f"✅ Successful form login for user: {username}")
        
        return LoginResponse(
            access_token=access_token,
            username=user["username"],
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Form login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        username=current_user["username"],
        email=current_user.get("email"),
        full_name=current_user.get("full_name"),
        is_active=current_user.get("is_active", True)
    )

@router.post("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if a token is valid"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return {
            "valid": True,
            "username": payload.get("sub"),
            "expires": payload.get("exp")
        }
    except HTTPException:
        return {"valid": False}

@router.post("/initialize")
async def initialize_auth_system():
    """Initialize authentication system with default admin user"""
    try:
        # Ensure users table exists
        from services.database import db_service
        table_result = await db_service.ensure_users_table_exists()
        
        # Initialize default user
        user_result = await auth_service.initialize_default_user()
        
        return {
            "success": True,
            "message": "Authentication system initialized",
            "table_status": table_result,
            "user_status": user_result
        }
        
    except Exception as e:
        logger.error(f"Auth initialization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize auth system: {str(e)}"
        )

@router.get("/debug/user/{username}")
async def debug_user_lookup(username: str):
    """Debug endpoint to check if user exists and test password verification"""
    try:
        # Get user from database
        user = await auth_service.get_user_by_username(username)
        
        if not user:
            return {
                "success": False,
                "message": f"User '{username}' not found in database",
                "user_exists": False
            }
        
        # Test password verification with known password
        password_test = auth_service.verify_password("admin123", user["hashed_password"])
        
        return {
            "success": True,
            "message": f"User '{username}' found",
            "user_exists": True,
            "user_data": {
                "id": user.get("id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_active": user.get("is_active"),
                "created_at": user.get("created_at")
            },
            "password_test_admin123": password_test,
            "hashed_password_preview": user["hashed_password"][:20] + "..." if user.get("hashed_password") else None
        }
        
    except Exception as e:
        logger.error(f"Debug user lookup error: {e}")
        return {
            "success": False,
            "message": f"Error looking up user: {str(e)}"
        }

@router.get("/debug/hash-test")
async def debug_hash_test():
    """Debug endpoint to test password hashing"""
    test_password = "admin123"
    generated_hash = auth_service.get_password_hash(test_password)
    verification_test = auth_service.verify_password(test_password, generated_hash)
    
    return {
        "test_password": test_password,
        "generated_hash": generated_hash,
        "verification_test": verification_test,
        "hash_preview": generated_hash[:20] + "..."
    }

@router.post("/debug/reset-admin-password")
async def debug_reset_admin_password():
    """Debug endpoint to reset admin password to admin123"""
    try:
        from services.database import db_service
        
        # Generate correct hash
        correct_hash = auth_service.get_password_hash("admin123")
        
        # Update admin user password in database
        response = db_service.client.table("users").update({
            "hashed_password": correct_hash
        }).eq("username", "admin").execute()
        
        if response.data:
            return {
                "success": True,
                "message": "Admin password reset to 'admin123'",
                "new_hash_preview": correct_hash[:20] + "...",
                "updated_user": response.data[0]["username"]
            }
        else:
            return {
                "success": False,
                "message": "Failed to update admin password"
            }
            
    except Exception as e:
        logger.error(f"Error resetting admin password: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
