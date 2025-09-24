"""
Debug endpoint for Render authentication troubleshooting
"""
from fastapi import APIRouter, HTTPException
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/render-auth-status")
async def render_auth_status():
    """
    Debug endpoint to check authentication status on Render
    Only works when NODE_ENV != production for security
    """
    node_env = os.getenv("NODE_ENV", "development")
    
    # Security check - only allow in non-production
    if node_env == "production":
        return {"error": "Debug endpoint disabled in production", "hint": "Set NODE_ENV=development temporarily to use this"}
    
    try:
        from ...services.auth_service import auth_service
        from ...services.database import db_service
        
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        # Environment check
        env_status = {
            "NODE_ENV": node_env,
            "ADMIN_USERNAME": admin_username,
            "ADMIN_PASSWORD": "***SET***" if admin_password else "***NOT_SET***",
            "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL", "NOT_SET"),
            "JWT_SECRET": "***SET***" if os.getenv("JWT_SECRET") else "***NOT_SET***",
            "SUPA_URL": os.getenv("SUPA_URL", "NOT_SET"),
            "SUPA_SERVICE_ROLE_KEY": "***SET***" if os.getenv("SUPA_SERVICE_ROLE_KEY") else "***NOT_SET***",
        }
        
        # Database connectivity
        db_status = {
            "available": db_service.is_available,
            "connection": "OK" if db_service.is_available else "FAILED"
        }
        
        # Check admin user in database
        admin_user_status = {"exists": False, "active": False, "email": None}
        try:
            if db_service.is_available:
                user_result = await db_service.get_user_by_username(admin_username)
                if user_result and user_result.get("success") and user_result.get("data"):
                    user = user_result["data"]
                    admin_user_status = {
                        "exists": True,
                        "active": user.get("is_active", False),
                        "email": user.get("email"),
                        "created_at": user.get("created_at")
                    }
        except Exception as e:
            admin_user_status["error"] = str(e)
        
        # Password validation check
        password_validation = {"valid": False, "errors": []}
        if admin_password:
            password_validation["length"] = len(admin_password)
            password_validation["min_required"] = 12 if node_env == "production" else 1
            
            if node_env == "production":
                if len(admin_password) < 12:
                    password_validation["errors"].append("Password too short for production (minimum 12)")
                
                weak_passwords = ["admin123", "password", "123456", "admin", "password123"]
                if admin_password.lower() in weak_passwords:
                    password_validation["errors"].append("Password is too weak")
            
            password_validation["valid"] = len(password_validation["errors"]) == 0
        else:
            password_validation["errors"].append("No password set")
        
        return {
            "status": "Debug information for Render authentication",
            "environment": env_status,
            "database": db_status,
            "admin_user": admin_user_status,
            "password_validation": password_validation,
            "recommendations": [
                "1. Ensure all environment variables are set in Render dashboard",
                "2. Check that admin user was created during startup",
                "3. Verify password meets production requirements",
                "4. Check Render deployment logs for errors"
            ]
        }
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return {"error": f"Debug check failed: {str(e)}"}


@router.post("/test-admin-login")
async def test_admin_login():
    """
    Test admin login without JWT token creation
    Only works when NODE_ENV != production for security
    """
    node_env = os.getenv("NODE_ENV", "development")
    
    # Security check
    if node_env == "production":
        return {"error": "Test login disabled in production"}
    
    try:
        from ...services.auth_service import auth_service
        
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        if not admin_password:
            return {"error": "ADMIN_PASSWORD not set"}
        
        # Get user
        user = await auth_service.get_user_by_username(admin_username)
        if not user:
            return {"error": f"Admin user '{admin_username}' not found"}
        
        # Test password
        is_valid = auth_service.verify_password(admin_password, user.get("hashed_password", ""))
        
        return {
            "username": admin_username,
            "password_test": "PASS" if is_valid else "FAIL",
            "user_found": True,
            "user_active": user.get("is_active", False),
            "recommendation": "Password verification successful" if is_valid else "Password does not match stored hash"
        }
        
    except Exception as e:
        logger.error(f"Test login error: {e}")
        return {"error": f"Test login failed: {str(e)}"}