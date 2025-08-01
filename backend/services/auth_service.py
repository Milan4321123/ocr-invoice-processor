"""
Authentication service for Invoice Management System.
Handles user authentication, password management, and JWT tokens.
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from services.database import db_service

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for managing users and sessions"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET")
        
        # Check if JWT_SECRET is properly configured
        if not self.secret_key or self.secret_key.startswith("your-"):
            if os.getenv("NODE_ENV") == "production":
                logger.error("❌ CRITICAL: JWT_SECRET not properly configured for production!")
                logger.error("Generate a secure secret: openssl rand -base64 64")
                raise ValueError("JWT_SECRET must be set to a secure random value in production")
            else:
                # Development/demo mode - use default but warn
                logger.warning("⚠️  WARNING: Using development JWT_SECRET - not secure for production!")
                logger.warning("For production: Generate with 'openssl rand -base64 64'")
                self.secret_key = "dev-jwt-secret-for-testing-only-not-secure"
        
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30 * 24 * 60  # 30 days for simple auth
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        return user
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username from database"""
        try:
            if not db_service.is_available:
                return None
                
            response = db_service.client.table("users").select("*").eq("username", username).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None
    
    async def create_user(self, username: str, password: str, email: str = None, full_name: str = None) -> Dict[str, Any]:
        """Create a new user"""
        try:
            if not db_service.is_available:
                return {"success": False, "error": "Database unavailable"}
            
            # Check if user already exists
            existing_user = await self.get_user_by_username(username)
            if existing_user:
                return {"success": False, "error": "User already exists"}
            
            # Hash password
            hashed_password = self.get_password_hash(password)
            
            # Create user record
            user_data = {
                "username": username,
                "hashed_password": hashed_password,
                "email": email,
                "full_name": full_name,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = db_service.client.table("users").insert(user_data).execute()
            
            if response.data:
                logger.info(f"✅ User created: {username}")
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "Failed to create user"}
                
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return {"success": False, "error": str(e)}
    
    async def initialize_default_user(self) -> Dict[str, Any]:
        """Initialize a default admin user for first setup"""
        # Get admin credentials from environment variables
        default_username = os.getenv("ADMIN_USERNAME", "admin")
        default_password = os.getenv("ADMIN_PASSWORD")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@yourcompany.com")
        admin_name = os.getenv("ADMIN_FULL_NAME", "System Administrator")
        
        # Validate that admin password is provided
        if not default_password:
            logger.error("❌ CRITICAL: ADMIN_PASSWORD environment variable not set!")
            logger.error("Please set ADMIN_PASSWORD in your .env file for secure admin account creation")
            return {"success": False, "error": "ADMIN_PASSWORD environment variable required"}
        
        # Validate password strength in production
        if os.getenv("NODE_ENV") == "production":
            if len(default_password) < 12:
                logger.error("❌ CRITICAL: Admin password too short for production (minimum 12 characters)")
                return {"success": False, "error": "Admin password must be at least 12 characters in production"}
            
            # Check for common weak passwords
            weak_passwords = ["admin123", "password", "123456", "admin", "password123"]
            if default_password.lower() in weak_passwords:
                logger.error("❌ CRITICAL: Weak admin password detected in production")
                return {"success": False, "error": "Admin password is too weak for production use"}
        
        existing_user = await self.get_user_by_username(default_username)
        if existing_user:
            logger.info("✅ Default admin user already exists")
            return {"success": True, "message": "Default user already exists"}
        
        result = await self.create_user(
            username=default_username,
            password=default_password,
            email=admin_email,
            full_name=admin_name
        )
        
        if result["success"]:
            logger.info(f"✅ Default admin user created: {default_username}")
            # Don't log the password for security
            return {"success": True, "message": f"Default user created: {default_username}"}
        else:
            logger.error(f"❌ Failed to create default user: {result['error']}")
            return result

# Global auth service instance
auth_service = AuthService()
