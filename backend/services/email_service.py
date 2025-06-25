"""
Email Service for Invoice Workflow
Handles editor notifications and Bau-Leiter approval emails with audit logging.
"""
import logging
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import UUID
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import jwt
from jinja2 import Environment, FileSystemLoader, BaseLoader, Template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

from .database import db_service

logger = logging.getLogger(__name__)

class StringTemplateLoader(BaseLoader):
    """Custom Jinja2 loader for string templates"""
    def __init__(self, templates: Dict[str, str]):
        self.templates = templates
    
    def get_source(self, environment, template):
        if template in self.templates:
            source = self.templates[template]
            return source, None, lambda: True
        raise FileNotFoundError(f"Template {template} not found")

class EmailService:
    """
    Professional email service for invoice workflow with security and audit logging.
    Supports both SendGrid and SMTP backends.
    """
    
    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@company.com")
        self.from_name = os.getenv("FROM_NAME", "Invoice System")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secure-jwt-secret")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8001")
        
        # Initialize template environment
        self.templates = self._load_templates()
        self.jinja_env = Environment(
            loader=StringTemplateLoader(self.templates),
            autoescape=True
        )
    
    def _load_templates(self) -> Dict[str, str]:
        """Load email templates"""
        return {
            "editor_notification": """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prüfbericht - Rechnung bearbeitet</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .content { background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; }
        .invoice-details { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .changes-section { margin-top: 20px; }
        .change-item { padding: 10px; border-left: 4px solid #007bff; margin-bottom: 10px; background: #f8f9fa; }
        .footer { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; font-size: 0.9em; color: #666; }
        .button { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .status-badge { padding: 4px 8px; background: #28a745; color: white; border-radius: 3px; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Prüfbericht - Rechnung bearbeitet</h1>
        <p><strong>Datum:</strong> {{ completion_date }}</p>
        <p><strong>Bearbeiter:</strong> {{ editor_name }} ({{ editor_email }})</p>
    </div>
    
    <div class="content">
        <h2>Rechnung Details</h2>
        <div class="invoice-details">
            <p><strong>Rechnungsnummer:</strong> {{ invoice_number or 'Nicht verfügbar' }}</p>
            <p><strong>Lieferant:</strong> {{ supplier_name or 'Nicht verfügbar' }}</p>
            <p><strong>Rechnungsdatum:</strong> {{ invoice_date or 'Nicht verfügbar' }}</p>
            <p><strong>Betrag:</strong> {{ total_amount or 'Nicht verfügbar' }}{% if currency %} {{ currency }}{% endif %}</p>
            <p><strong>Status:</strong> <span class="status-badge">{{ status }}</span></p>
        </div>
        
        {% if changes_summary and changes_summary|length > 0 %}
        <div class="changes-section">
            <h3>Durchgeführte Änderungen</h3>
            {% for change in changes_summary %}
            <div class="change-item">
                <strong>{{ change.field }}:</strong>
                {% if change.old_value %}
                Von "{{ change.old_value }}" zu "{{ change.new_value }}"
                {% else %}
                Neu hinzugefügt: "{{ change.new_value }}"
                {% endif %}
                {% if change.timestamp %}
                <br><small>Geändert am: {{ change.timestamp }}</small>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div style="margin-top: 30px;">
            <h3>Nächste Schritte</h3>
            <p>Die Rechnung wurde erfolgreich bearbeitet und ist nun für die Bau-Leiter Prüfung vorbereitet. 
               Das System wird automatisch eine Benachrichtigung an den zuständigen Bau-Leiter senden.</p>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>Automatisch generiert vom Rechnungssystem</strong></p>
        <p>Zeitstempel: {{ timestamp }}</p>
        <p>Request ID: {{ request_id }}</p>
        <p>Diese E-Mail wurde automatisch versendet. Bitte antworten Sie nicht auf diese E-Mail.</p>
    </div>
</body>
</html>
            """,
            
            "bauleiter_approval": """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rechnung zur Genehmigung</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .content { background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; }
        .invoice-details { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .action-buttons { margin: 30px 0; text-align: center; }
        .approve-btn { display: inline-block; padding: 15px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 10px; font-weight: bold; }
        .reject-btn { display: inline-block; padding: 15px 30px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 10px; font-weight: bold; }
        .footer { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; font-size: 0.9em; color: #666; }
        .security-notice { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Rechnung zur Genehmigung</h1>
        <p><strong>Eingereicht am:</strong> {{ submission_date }}</p>
        <p><strong>Bearbeitet von:</strong> {{ editor_name }} ({{ editor_email }})</p>
    </div>
    
    <div class="content">
        <h2>Rechnung Details</h2>
        <div class="invoice-details">
            <p><strong>Rechnungsnummer:</strong> {{ invoice_number or 'Nicht verfügbar' }}</p>
            <p><strong>Lieferant:</strong> {{ supplier_name or 'Nicht verfügbar' }}</p>
            <p><strong>Rechnungsdatum:</strong> {{ invoice_date or 'Nicht verfügbar' }}</p>
            <p><strong>Betrag:</strong> {{ total_amount or 'Nicht verfügbar' }}{% if currency %} {{ currency }}{% endif %}</p>
        </div>
        
        {% if changes_summary and changes_summary|length > 0 %}
        <h3>Durchgeführte Bearbeitungen</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            {% for change in changes_summary %}
            <p><strong>{{ change.field }}:</strong> 
               {% if change.old_value %}Von "{{ change.old_value }}" zu "{{ change.new_value }}"{% else %}Neu: "{{ change.new_value }}"{% endif %}</p>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="action-buttons">
            <h3>Genehmigung erforderlich</h3>
            <p>Bitte prüfen Sie die Rechnung und wählen Sie eine Option:</p>
            <a href="{{ approve_url }}" class="approve-btn">✅ GENEHMIGEN</a>
            <a href="{{ reject_url }}" class="reject-btn">❌ ABLEHNEN</a>
        </div>
        
        <div class="security-notice">
            <strong>🔒 Sicherheitshinweis:</strong> Diese Links sind verschlüsselt und verfallen in 7 Tagen. 
            Klicken Sie nur auf Links in E-Mails, die Sie erwartet haben.
        </div>
    </div>
    
    <div class="footer">
        <p><strong>Automatisch generiert vom Rechnungssystem</strong></p>
        <p>Zeitstempel: {{ timestamp }}</p>
        <p>Token gültig bis: {{ token_expires }}</p>
        <p>Diese E-Mail wurde automatisch versendet. Bei Fragen wenden Sie sich an den System-Administrator.</p>
    </div>
</body>
</html>
            """
        }
    
    async def send_editor_notification(
        self, 
        invoice_data: Dict[str, Any], 
        editor_email: str, 
        editor_name: str,
        changes_summary: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send professional HTML email notification to editor after invoice completion.
        Only marks invoice as completed after successful email send.
        """
        try:
            # Prepare template context
            context = {
                "editor_name": editor_name,
                "editor_email": editor_email,
                "completion_date": datetime.now().strftime("%d.%m.%Y um %H:%M"),
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id or "N/A",
                "invoice_number": invoice_data.get("rechnungsnummer"),
                "supplier_name": invoice_data.get("lieferant"),
                "invoice_date": invoice_data.get("rechnungsdatum"),
                "total_amount": invoice_data.get("rechnungsbetrag"),
                "currency": invoice_data.get("currency", "EUR"),
                "status": "Bearbeitung abgeschlossen",
                "changes_summary": changes_summary or []
            }
            
            # Render template
            template = self.jinja_env.get_template("editor_notification")
            html_content = template.render(**context)
            
            # Email details
            subject = f"Prüfbericht - Rechnung bearbeitet ({context['invoice_number'] or 'N/A'})"
            
            # Send email
            result = await self._send_email(
                to_email=editor_email,
                to_name=editor_name,
                subject=subject,
                html_content=html_content,
                email_type="editor_notification",
                invoice_id=invoice_data.get("id"),
                template_used="editor_notification"
            )
            
            if result["success"]:
                # Update invoice status and log email send
                await self._update_invoice_after_email_send(
                    invoice_id=invoice_data["id"],
                    email_type="editor_notification",
                    result=result
                )
                
                logger.info(f"Editor notification sent successfully to {editor_email} for invoice {invoice_data.get('id')}")
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to send editor notification: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None
            }
    
    async def send_bauleiter_approval_request(
        self,
        invoice_data: Dict[str, Any],
        bauleiter_email: str,
        editor_name: str,
        editor_email: str,
        changes_summary: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send approval request to Bau-Leiter with secure approval/rejection links.
        """
        try:
            # Generate secure approval tokens
            approve_token = await self._generate_approval_token(
                invoice_id=invoice_data["id"],
                action="approve",
                user_email=bauleiter_email
            )
            
            reject_token = await self._generate_approval_token(
                invoice_id=invoice_data["id"],
                action="reject",
                user_email=bauleiter_email
            )
            
            # Build approval URLs
            approve_url = f"{self.base_url}/api/approval/{approve_token}"
            reject_url = f"{self.base_url}/api/approval/{reject_token}"
            
            # Prepare template context
            context = {
                "submission_date": datetime.now().strftime("%d.%m.%Y um %H:%M"),
                "editor_name": editor_name,
                "editor_email": editor_email,
                "timestamp": datetime.now().isoformat(),
                "invoice_number": invoice_data.get("rechnungsnummer"),
                "supplier_name": invoice_data.get("lieferant"),
                "invoice_date": invoice_data.get("rechnungsdatum"),
                "total_amount": invoice_data.get("rechnungsbetrag"),
                "currency": invoice_data.get("currency", "EUR"),
                "changes_summary": changes_summary or [],
                "approve_url": approve_url,
                "reject_url": reject_url,
                "token_expires": (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")
            }
            
            # Render template
            template = self.jinja_env.get_template("bauleiter_approval")
            html_content = template.render(**context)
            
            # Email details
            subject = f"Rechnung zur Genehmigung - {context['invoice_number'] or 'N/A'} ({context['supplier_name'] or 'N/A'})"
            
            # Send email
            result = await self._send_email(
                to_email=bauleiter_email,
                to_name="Bau-Leiter",
                subject=subject,
                html_content=html_content,
                email_type="bauleiter_approval",
                invoice_id=invoice_data.get("id"),
                template_used="bauleiter_approval"
            )
            
            if result["success"]:
                # Update invoice status
                await self._update_invoice_after_bauleiter_email(
                    invoice_id=invoice_data["id"],
                    bauleiter_email=bauleiter_email,
                    result=result
                )
                
                logger.info(f"Bau-Leiter approval request sent to {bauleiter_email} for invoice {invoice_data.get('id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send Bau-Leiter approval request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None
            }
    
    async def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        to_name: str = None,
        invoice_id: Optional[UUID] = None,
        email_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Send HTML email using the configured email providers.
        Generic method for sending any HTML email with fallback support.
        """
        try:
            # Use configured name if not provided
            if not to_name:
                to_name = to_email.split('@')[0].title()
            
            # Send email with retry and fallback
            result = await self._send_email(
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                html_content=html_content,
                email_type=email_type,
                invoice_id=invoice_id,
                template_used="custom_html"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send HTML email to {to_email}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": "none"
            }
    
    async def _send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        email_type: str,
        invoice_id: Optional[UUID] = None,
        template_used: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email using configured provider with audit logging.
        """
        start_time = datetime.now()
        email_size = len(html_content.encode('utf-8'))
        
        try:
            # Try SendGrid first, fall back to SMTP on failure
            result = None
            last_error = None
            
            # Primary: Try SendGrid
            if self.sendgrid_api_key:
                try:
                    result = await self._send_via_sendgrid(to_email, to_name, subject, html_content)
                    if result["success"]:
                        result["provider"] = "sendgrid"
                        logger.info(f"Email sent successfully via SendGrid")
                    else:
                        raise Exception(f"SendGrid failed: {result.get('error', 'Unknown error')}")
                except Exception as sg_error:
                    logger.warning(f"SendGrid failed: {sg_error}")
                    last_error = sg_error
                    result = None
            
            # Fallback: Try SMTP if SendGrid failed or not configured
            if not result or not result.get("success"):
                if self.smtp_host:
                    try:
                        logger.info("Attempting SMTP fallback...")
                        result = await self._send_via_smtp(to_email, to_name, subject, html_content)
                        if result["success"]:
                            result["provider"] = "smtp"
                            logger.info(f"Email sent successfully via SMTP fallback")
                        else:
                            raise Exception(f"SMTP failed: {result.get('error', 'Unknown error')}")
                    except Exception as smtp_error:
                        logger.error(f"SMTP fallback also failed: {smtp_error}")
                        last_error = smtp_error
                        result = {"success": False, "error": str(smtp_error), "provider": "smtp"}
                else:
                    logger.error("No SMTP configuration available for fallback")
            
            # If both failed, return error
            if not result or not result.get("success"):
                if not self.sendgrid_api_key and not self.smtp_host:
                    raise ValueError("No email provider configured")
                else:
                    raise Exception(f"All email providers failed. Last error: {last_error}")
            
            # Log email send attempt
            await self._log_email_send(
                invoice_id=invoice_id,
                email_type=email_type,
                recipient_email=to_email,
                subject=subject,
                send_success=result["success"],
                provider_message_id=result.get("message_id"),
                provider_response=result.get("response"),
                template_used=template_used,
                email_size_bytes=email_size
            )
            
            return result
            
        except Exception as e:
            # Log failed send attempt
            await self._log_email_send(
                invoice_id=invoice_id,
                email_type=email_type,
                recipient_email=to_email,
                subject=subject,
                send_success=False,
                provider_response={"error": str(e)},
                template_used=template_used,
                email_size_bytes=email_size
            )
            raise e
    
    async def _send_via_sendgrid(self, to_email: str, to_name: str, subject: str, html_content: str) -> Dict[str, Any]:
        """Send email via SendGrid"""
        try:
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=[(to_email, to_name)],
                subject=subject,
                html_content=html_content
            )
            
            response = sg.send(message)
            
            return {
                "success": True,
                "message_id": response.headers.get("X-Message-Id"),
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
            }
            
        except Exception as e:
            logger.error(f"SendGrid send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    async def _send_via_smtp(self, to_email: str, to_name: str, subject: str, html_content: str) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = f"{to_name} <{to_email}>"
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return {
                "success": True,
                "message_id": f"smtp-{secrets.token_hex(8)}",
                "response": {
                    "provider": "SMTP",
                    "sent_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"SMTP send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    async def _generate_approval_token(self, invoice_id: UUID, action: str, user_email: str) -> str:
        """Generate secure approval token with database storage"""
        try:
            # Generate secure token components
            token_data = {
                "invoice_id": str(invoice_id),
                "action": action,
                "user_email": user_email,
                "nonce": secrets.token_hex(16),
                "created_at": datetime.now().isoformat()
            }
            
            # Create JWT token
            jwt_token = jwt.encode(
                token_data,
                self.jwt_secret,
                algorithm="HS256"
            )
            
            # Hash token for database storage
            token_hash = hashlib.sha256(jwt_token.encode()).hexdigest()
            
            # Store in database
            expires_at = datetime.now() + timedelta(days=7)
            
            query = """
            INSERT INTO approval_tokens 
            (token_hash, invoice_id, action, user_email, expires_at, nonce)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            await db_service.execute_query(
                query,
                (token_hash, str(invoice_id), action, user_email, expires_at, token_data["nonce"])
            )
            
            return jwt_token
            
        except Exception as e:
            logger.error(f"Failed to generate approval token: {str(e)}")
            raise e
    
    async def _update_invoice_after_email_send(self, invoice_id: UUID, email_type: str, result: Dict[str, Any]):
        """Update invoice status after successful email send"""
        try:
            if email_type == "editor_notification":
                query = """
                UPDATE invoices_clean 
                SET 
                    status = 'edit_completed',
                    edit_bericht_sent_at = NOW(),
                    email_logs = COALESCE(email_logs, '[]'::jsonb) || %s::jsonb
                WHERE id = %s
                """
                
                email_log_entry = json.dumps([{
                    "type": "editor_notification",
                    "sent_at": datetime.now().isoformat(),
                    "success": result["success"],
                    "message_id": result.get("message_id")
                }])
                
                await db_service.execute_query(query, (email_log_entry, str(invoice_id)))
                
        except Exception as e:
            logger.error(f"Failed to update invoice after email send: {str(e)}")
            raise e
    
    async def _update_invoice_after_bauleiter_email(self, invoice_id: UUID, bauleiter_email: str, result: Dict[str, Any]):
        """Update invoice status after Bau-Leiter email send"""
        try:
            query = """
            UPDATE invoices_clean 
            SET 
                status = 'in_review_by_bauleiter',
                bauleiter_email = %s,
                bauleiter_review_sent_at = NOW(),
                email_logs = COALESCE(email_logs, '[]'::jsonb) || %s::jsonb
            WHERE id = %s
            """
            
            email_log_entry = json.dumps([{
                "type": "bauleiter_approval",
                "sent_at": datetime.now().isoformat(),
                "success": result["success"],
                "message_id": result.get("message_id")
            }])
            
            await db_service.execute_query(query, (bauleiter_email, email_log_entry, str(invoice_id)))
            
        except Exception as e:
            logger.error(f"Failed to update invoice after Bau-Leiter email: {str(e)}")
            raise e
    
    async def _log_email_send(
        self,
        invoice_id: Optional[UUID],
        email_type: str,
        recipient_email: str,
        subject: str,
        send_success: bool,
        provider_message_id: Optional[str] = None,
        provider_response: Optional[Dict] = None,
        template_used: Optional[str] = None,
        email_size_bytes: Optional[int] = None
    ):
        """Log email send attempt to audit table"""
        try:
            query = """
            INSERT INTO email_audit_log 
            (invoice_id, email_type, recipient_email, subject, send_success, 
             provider_message_id, provider_response, template_used, email_size_bytes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_service.execute_query(
                query,
                (
                    str(invoice_id) if invoice_id else None,
                    email_type,
                    recipient_email,
                    subject,
                    send_success,
                    provider_message_id,
                    json.dumps(provider_response) if provider_response else None,
                    template_used,
                    email_size_bytes
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to log email send: {str(e)}")
            # Don't raise - this is audit logging and shouldn't break the main flow

# Global email service instance
email_service = EmailService()
