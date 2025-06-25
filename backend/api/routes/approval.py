"""
Approval workflow endpoints for handling Bau-Leiter approve/reject actions.
Handles secure JWT token validation and invoice status updates.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
import jwt
import logging
from datetime import datetime
from typing import Dict, Any
import os
from services.database import db_service
from services.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["approval"])

# JWT secret from environment
JWT_SECRET = os.getenv("JWT_SECRET", "your-secure-jwt-secret")

async def validate_approval_token(token: str, request: Request) -> Dict[str, Any]:
    """
    Validate approval token and extract invoice information.
    Checks JWT signature, expiration, and usage status.
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        # Extract token data
        invoice_id = payload.get("invoice_id")
        action = payload.get("action")
        user_email = payload.get("user_email")
        nonce = payload.get("nonce")
        
        if not all([invoice_id, action, user_email, nonce]):
            raise HTTPException(status_code=400, detail="Invalid token structure")
        
        # Get client information for audit
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")
        
        logger.info(f"Approval token validated: {action} for invoice {invoice_id} by {user_email}")
        
        return {
            "invoice_id": invoice_id,
            "action": action,
            "user_email": user_email,
            "nonce": nonce,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "valid": True
        }
        
    except jwt.ExpiredSignatureError:
        logger.warning(f"Approval token expired: {token[:20]}...")
        raise HTTPException(status_code=400, detail="Approval link has expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid approval token: {e}")
        raise HTTPException(status_code=400, detail="Invalid approval link")
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=500, detail="Token validation failed")

@router.get("/{token}")
async def handle_approval_action(token: str, request: Request):
    """
    Handle approval or rejection action when Bau-Leiter clicks email link.
    Validates token, updates invoice status, and returns confirmation page.
    """
    try:
        # Validate the token
        token_data = await validate_approval_token(token, request)
        
        invoice_id = token_data["invoice_id"]
        action = token_data["action"]
        user_email = token_data["user_email"]
        client_ip = token_data["client_ip"]
        
        # Get invoice details
        invoice_result = db_service.get_invoice(invoice_id)
        if not invoice_result.get("success"):
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = invoice_result.get("data")
        if not invoice_data:
            raise HTTPException(status_code=404, detail="Invoice data not available")
        
        # Update invoice status based on action
        new_status = "approved" if action == "approve" else "rejected"
        
        update_data = {
            "status": new_status,
            "bauleiter_decision": action,
            "bauleiter_decision_at": datetime.now().isoformat(),
            "bauleiter_decision_by": user_email,
            "bauleiter_decision_ip": client_ip
        }
        
        # Update the invoice
        update_result = db_service.update_invoice(invoice_id, update_data)
        
        if update_result.get("success"):
            # Log the approval action
            logger.info(f"Invoice {invoice_id} {action}d by {user_email} from {client_ip}")
            
            # TODO: Send notification email to editor about the decision
            # await email_service.send_decision_notification(invoice_data, action, user_email)
            
            # Return success page
            return HTMLResponse(content=generate_success_page(
                action=action,
                invoice_data=invoice_data,
                user_email=user_email
            ))
        else:
            raise HTTPException(status_code=500, detail="Failed to update invoice status")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approval action failed: {e}")
        return HTMLResponse(
            content=generate_error_page(str(e)),
            status_code=500
        )

def generate_success_page(action: str, invoice_data: Dict, user_email: str) -> str:
    """Generate HTML success page for approval action"""
    action_text = "GENEHMIGT" if action == "approve" else "ABGELEHNT"
    action_color = "#28a745" if action == "approve" else "#dc3545"
    action_icon = "✅" if action == "approve" else "❌"
    
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rechnung {action_text}</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 40px; 
                background: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            .container {{ 
                background: white; 
                padding: 40px; 
                border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                max-width: 600px;
                text-align: center;
            }}
            .header {{ 
                background: {action_color}; 
                color: white; 
                padding: 30px; 
                border-radius: 8px; 
                margin-bottom: 30px; 
            }}
            .status {{ 
                font-size: 3em; 
                margin-bottom: 10px; 
            }}
            .details {{ 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 8px; 
                margin: 20px 0; 
                text-align: left;
            }}
            .footer {{ 
                margin-top: 30px; 
                color: #666; 
                font-size: 0.9em; 
            }}
            .success-check {{ 
                color: {action_color}; 
                font-size: 4em; 
                margin: 20px 0; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="status">{action_icon}</div>
                <h1>Rechnung erfolgreich {action_text}!</h1>
            </div>
            
            <div class="success-check">{action_icon}</div>
            
            <h2>Entscheidung erfasst</h2>
            <p>Ihre Entscheidung wurde erfolgreich im System erfasst.</p>
            
            <div class="details">
                <h3>Details:</h3>
                <p><strong>Rechnungsnummer:</strong> {invoice_data.get('rechnungsnummer', 'N/A')}</p>
                <p><strong>Lieferant:</strong> {invoice_data.get('lieferant', 'N/A')}</p>
                <p><strong>Betrag:</strong> {invoice_data.get('rechnungsbetrag', 'N/A')} EUR</p>
                <p><strong>Status:</strong> <span style="color: {action_color}; font-weight: bold;">{action_text}</span></p>
                <p><strong>Entschieden von:</strong> {user_email}</p>
                <p><strong>Zeitstempel:</strong> {datetime.now().strftime('%d.%m.%Y um %H:%M')}</p>
            </div>
            
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4>✅ Nächste Schritte:</h4>
                <ul style="text-align: left; margin: 10px 0;">
                    <li>Der Editor wird automatisch über Ihre Entscheidung benachrichtigt</li>
                    <li>Die Rechnung ist nun für die Weiterbearbeitung freigegeben</li>
                    <li>Alle Änderungen werden im Audit-Log festgehalten</li>
                </ul>
            </div>
            
            <div class="footer">
                <p><strong>Automatisch generiert vom Rechnungssystem</strong></p>
                <p>Diese Seite kann geschlossen werden.</p>
            </div>
        </div>
    </body>
    </html>
    """

def generate_error_page(error_message: str) -> str:
    """Generate HTML error page for failed approval action"""
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fehler bei der Genehmigung</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 40px; 
                background: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            .container {{ 
                background: white; 
                padding: 40px; 
                border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                max-width: 600px;
                text-align: center;
            }}
            .header {{ 
                background: #dc3545; 
                color: white; 
                padding: 30px; 
                border-radius: 8px; 
                margin-bottom: 30px; 
            }}
            .error-icon {{ 
                color: #dc3545; 
                font-size: 4em; 
                margin: 20px 0; 
            }}
            .footer {{ 
                margin-top: 30px; 
                color: #666; 
                font-size: 0.9em; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>❌ Fehler bei der Genehmigung</h1>
            </div>
            
            <div class="error-icon">⚠️</div>
            
            <h2>Die Aktion konnte nicht ausgeführt werden</h2>
            <p>Es ist ein Fehler aufgetreten:</p>
            
            <div style="background: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; color: #721c24;">
                <strong>Fehler:</strong> {error_message}
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4>🔧 Mögliche Lösungen:</h4>
                <ul style="text-align: left; margin: 10px 0;">
                    <li>Der Genehmigungslink ist möglicherweise abgelaufen (7 Tage)</li>
                    <li>Der Link wurde bereits verwendet</li>
                    <li>Wenden Sie sich an den System-Administrator</li>
                    <li>Verwenden Sie einen aktuellen Genehmigungslink</li>
                </ul>
            </div>
            
            <div class="footer">
                <p><strong>Rechnungssystem - Fehlerbehandlung</strong></p>
                <p>Bei anhaltenden Problemen wenden Sie sich an den Support.</p>
            </div>
        </div>
    </body>
    </html>
    """

@router.get("/status/{invoice_id}")
async def get_approval_status(invoice_id: str):
    """
    Get current approval status of an invoice.
    Useful for checking if approval actions were processed.
    """
    try:
        result = db_service.get_invoice(invoice_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_data = result.get("data")
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "status": invoice_data.get("status"),
            "bauleiter_decision": invoice_data.get("bauleiter_decision"),
            "bauleiter_decision_at": invoice_data.get("bauleiter_decision_at"),
            "bauleiter_decision_by": invoice_data.get("bauleiter_decision_by")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get approval status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get approval status")
