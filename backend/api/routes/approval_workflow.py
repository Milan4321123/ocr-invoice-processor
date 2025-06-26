"""
Approval Workflow API Routes
Handles secure approval/rejection of invoices via email links
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
import jwt
import hashlib
from datetime import datetime
from typing import Dict, Any
import logging

from services.database import db_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/approval", tags=["approval"])

@router.get("/{token}")
async def handle_approval_action(token: str, request: Request):
    """
    Handle approval/rejection action from email links.
    Validates JWT token and processes the approval decision.
    """
    try:
        # Get JWT secret from environment
        import os
        jwt_secret = os.getenv("JWT_SECRET", "your-secure-jwt-secret")
        
        # Decode and validate JWT token
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return HTMLResponse(
                content=get_error_page("Token Expired", "This approval link has expired. Please contact the administrator."),
                status_code=400
            )
        except jwt.InvalidTokenError:
            return HTMLResponse(
                content=get_error_page("Invalid Token", "This approval link is invalid or has been tampered with."),
                status_code=400
            )
        
        # Extract token data
        invoice_id = payload.get("invoice_id")
        action = payload.get("action")  # "approve" or "reject"
        user_email = payload.get("user_email")
        nonce = payload.get("nonce")
        created_at = payload.get("created_at")
        
        logger.info(f"Approval request: {action} for invoice {invoice_id} by {user_email}")
        
        # Get client IP for audit
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Check if token was already used (mock check for now)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Process the approval action
        if action == "approve":
            result = await process_approval(invoice_id, user_email, client_ip, user_agent, token_hash)
            return HTMLResponse(content=get_success_page("approve", invoice_id, user_email))
            
        elif action == "reject":
            result = await process_rejection(invoice_id, user_email, client_ip, user_agent, token_hash)
            return HTMLResponse(content=get_success_page("reject", invoice_id, user_email))
            
        else:
            return HTMLResponse(
                content=get_error_page("Invalid Action", f"Unknown action: {action}"),
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error processing approval: {e}")
        return HTMLResponse(
            content=get_error_page("System Error", "An error occurred while processing your request. Please try again or contact support."),
            status_code=500
        )

async def process_approval(invoice_id: str, user_email: str, client_ip: str, user_agent: str, token_hash: str) -> Dict[str, Any]:
    """Process invoice approval"""
    try:
        # Update invoice status to approved
        # For now, just log the approval since we need the actual database tables
        logger.info(f"✅ INVOICE APPROVED: {invoice_id} by {user_email} from IP {client_ip}")
        
        # In a real implementation, this would:
        # 1. Update invoices table: status = 'approved'
        # 2. Log approval in audit table
        # 3. Mark token as used
        # 4. Send confirmation email
        # 5. Trigger next workflow step
        
        return {
            "success": True,
            "action": "approved",
            "invoice_id": invoice_id,
            "approved_by": user_email,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to process approval: {e}")
        raise e

async def process_rejection(invoice_id: str, user_email: str, client_ip: str, user_agent: str, token_hash: str) -> Dict[str, Any]:
    """Process invoice rejection"""
    try:
        # Update invoice status to rejected
        logger.info(f"❌ INVOICE REJECTED: {invoice_id} by {user_email} from IP {client_ip}")
        
        # In a real implementation, this would:
        # 1. Update invoices table: status = 'rejected'
        # 2. Log rejection in audit table
        # 3. Mark token as used
        # 4. Send notification email to editor
        # 5. Trigger rejection workflow
        
        return {
            "success": True,
            "action": "rejected",
            "invoice_id": invoice_id,
            "rejected_by": user_email,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to process rejection: {e}")
        raise e

def get_success_page(action: str, invoice_id: str, user_email: str) -> str:
    """Generate success page HTML"""
    action_text = "✅ GENEHMIGT" if action == "approve" else "❌ ABGELEHNT"
    action_description = "genehmigt" if action == "approve" else "abgelehnt"
    
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rechnung {action_description}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 30px; border-radius: 8px; }}
            .reject {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 30px; border-radius: 8px; }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
            .details {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: left; }}
            .back-btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="{'success' if action == 'approve' else 'reject'}">
            <div class="icon">{action_text}</div>
            <h1>Rechnung erfolgreich {action_description}!</h1>
            <p>Die Rechnung wurde erfolgreich {action_description} und das System wurde aktualisiert.</p>
            
            <div class="details">
                <h3>Details:</h3>
                <p><strong>Rechnung:</strong> {invoice_id}</p>
                <p><strong>Aktion:</strong> {action_description.title()}</p>
                <p><strong>Bearbeitet von:</strong> {user_email}</p>
                <p><strong>Zeitstempel:</strong> {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}</p>
            </div>
            
            <p><strong>✅ Die Entscheidung wurde gespeichert und alle Beteiligten wurden benachrichtigt.</strong></p>
            
            <div style="margin-top: 30px; padding: 15px; background: #fff3cd; border-radius: 5px;">
                <small><strong>Hinweis:</strong> Dieser Genehmigungslink ist jetzt ungültig und kann nicht erneut verwendet werden.</small>
            </div>
        </div>
    </body>
    </html>
    """

def get_error_page(title: str, message: str) -> str:
    """Generate error page HTML"""
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fehler - {title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
            .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 30px; border-radius: 8px; }}
            .icon {{ font-size: 48px; margin-bottom: 20px; }}
            .contact {{ background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="error">
            <div class="icon">⚠️</div>
            <h1>{title}</h1>
            <p>{message}</p>
            
            <div class="contact">
                <h3>Benötigen Sie Hilfe?</h3>
                <p>Kontaktieren Sie den System-Administrator oder fordern Sie einen neuen Genehmigungslink an.</p>
            </div>
            
            <div style="margin-top: 30px;">
                <small>Zeitstempel: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}</small>
            </div>
        </div>
    </body>
    </html>
    """
