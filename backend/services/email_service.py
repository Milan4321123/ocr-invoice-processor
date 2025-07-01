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
    <title>Rechnung zur Genehmigung - {{ invoice_number or 'N/A' }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f5f7fa; }
        .container { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 28px; font-weight: 300; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .content { padding: 30px; }
        .invoice-summary { background: #f8f9fc; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .invoice-details { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 25px 0; }
        .detail-section { background: #ffffff; border: 1px solid #e1e5e9; border-radius: 8px; padding: 20px; }
        .detail-section h3 { color: #667eea; margin-top: 0; margin-bottom: 15px; font-size: 16px; font-weight: 600; border-bottom: 2px solid #f0f2f7; padding-bottom: 8px; }
        .detail-row { display: flex; justify-content: space-between; margin-bottom: 12px; padding: 8px 0; border-bottom: 1px solid #f5f7fa; }
        .detail-label { font-weight: 600; color: #4a5568; min-width: 140px; }
        .detail-value { color: #2d3748; flex: 1; text-align: right; }
        .amount-highlight { background: #e6fffa; border: 2px solid #38b2ac; border-radius: 8px; padding: 15px; text-align: center; margin: 20px 0; }
        .amount-highlight .amount { font-size: 24px; font-weight: bold; color: #38b2ac; }
        .changes-section { background: #fff5f5; border: 1px solid #fed7d7; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .change-item { background: white; padding: 12px; margin: 8px 0; border-left: 4px solid #4299e1; border-radius: 4px; }
        .pdf-link { background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 8px; padding: 15px; margin: 20px 0; text-align: center; }
        .pdf-link a { color: #1890ff; text-decoration: none; font-weight: 600; }
        .action-buttons { background: #f7fafc; border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0; }
        .action-buttons h3 { color: #2d3748; margin-bottom: 20px; }
        .approve-btn { display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); color: white; text-decoration: none; border-radius: 8px; margin: 10px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(72, 187, 120, 0.3); transition: all 0.3s ease; }
        .approve-btn:hover { box-shadow: 0 6px 8px rgba(72, 187, 120, 0.4); transform: translateY(-2px); }
        .reject-btn { display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%); color: white; text-decoration: none; border-radius: 8px; margin: 10px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(245, 101, 101, 0.3); transition: all 0.3s ease; }
        .reject-btn:hover { box-shadow: 0 6px 8px rgba(245, 101, 101, 0.4); transform: translateY(-2px); }
        .view-btn { display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); color: white; text-decoration: none; border-radius: 6px; margin: 10px; font-weight: 500; font-size: 14px; }
        .footer { background: #f7fafc; padding: 25px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #718096; }
        .security-notice { background: #fffbeb; border: 1px solid #f6e05e; border-radius: 8px; padding: 15px; margin: 20px 0; }
        .security-notice strong { color: #744210; }
        .status-badge { display: inline-block; padding: 4px 12px; background: #48bb78; color: white; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .priority-high { border-left-color: #f56565; }
        .priority-medium { border-left-color: #ed8936; }
        .priority-low { border-left-color: #48bb78; }
        @media (max-width: 768px) {
            .invoice-details { grid-template-columns: 1fr; }
            .detail-row { flex-direction: column; }
            .detail-value { text-align: left; margin-top: 5px; }
            .action-buttons { padding: 20px; }
            .approve-btn, .reject-btn { display: block; margin: 10px 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Rechnung zur Genehmigung</h1>
            <p><strong>Eingereicht am:</strong> {{ submission_date }}</p>
            <p><strong>Bearbeitet von:</strong> {{ editor_name }} ({{ editor_email }})</p>
        </div>
        
        <div class="content">
            <!-- Invoice Summary -->
            <div class="invoice-summary">
                <h2 style="margin: 0 0 15px 0; color: #2d3748;">📄 {{ invoice_number or 'Rechnung ohne Nummer' }}</h2>
                <p style="margin: 0; font-size: 16px;"><strong>Lieferant:</strong> {{ supplier_name or 'Nicht verfügbar' }}</p>
                <p style="margin: 5px 0 0 0; color: #718096;">Status: <span class="status-badge">Zur Genehmigung</span></p>
            </div>

            <!-- Amount Highlight -->
            {% if total_amount %}
            <div class="amount-highlight">
                <div style="color: #4a5568; margin-bottom: 5px;">Rechnungsbetrag</div>
                <div class="amount">{{ total_amount }}{% if currency %} {{ currency }}{% else %} EUR{% endif %}</div>
                {% if skonto_prozent and skonto_datum %}
                <div style="color: #718096; font-size: 14px; margin-top: 8px;">
                    Skonto: {{ skonto_prozent }}% bis {{ skonto_datum }}
                </div>
                {% endif %}
            </div>
            {% endif %}

            <!-- Detailed Invoice Information -->
            <div class="invoice-details">
                <!-- Basic Information -->
                <div class="detail-section">
                    <h3>📋 Grunddaten</h3>
                    <div class="detail-row">
                        <span class="detail-label">Rechnungsnummer:</span>
                        <span class="detail-value">{{ invoice_number or 'Nicht verfügbar' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Rechnungsempfänger:</span>
                        <span class="detail-value">{{ rechnungsempfaenger or 'Nicht verfügbar' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Rechnungssteller:</span>
                        <span class="detail-value">{{ rechnungssteller or supplier_name or 'Nicht verfügbar' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Rechnungsdatum:</span>
                        <span class="detail-value">{{ invoice_date or 'Nicht verfügbar' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Rechnungseingang:</span>
                        <span class="detail-value">{{ rechnungseingang or 'Nicht verfügbar' }}</span>
                    </div>
                </div>

                <!-- Project & Trade Information -->
                <div class="detail-section">
                    <h3>🏗️ Projekt & Gewerk</h3>
                    <div class="detail-row">
                        <span class="detail-label">Projekt:</span>
                        <span class="detail-value">{{ projekt or 'Nicht zugeordnet' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Gewerk:</span>
                        <span class="detail-value">{{ gewerk or 'Nicht zugeordnet' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Kostenstelle:</span>
                        <span class="detail-value">{{ kostenstelle or 'Nicht zugeordnet' }}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Weiter berechnen an:</span>
                        <span class="detail-value">{{ weiter_berechnen_an or 'Nicht festgelegt' }}</span>
                    </div>
                </div>

                <!-- Financial Information -->
                <div class="detail-section">
                    <h3>💰 Finanzdaten</h3>
                    <div class="detail-row">
                        <span class="detail-label">Rechnungsbetrag:</span>
                        <span class="detail-value"><strong>{{ total_amount or rechnungsbetrag or 'Nicht verfügbar' }}{% if currency %} {{ currency }}{% else %} EUR{% endif %}</strong></span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Fälligkeit:</span>
                        <span class="detail-value">{{ faelligkeit or 'Nicht festgelegt' }}</span>
                    </div>
                    {% if skonto_datum %}
                    <div class="detail-row">
                        <span class="detail-label">Skonto Datum:</span>
                        <span class="detail-value">{{ skonto_datum }}</span>
                    </div>
                    {% endif %}
                    {% if skonto_prozent %}
                    <div class="detail-row">
                        <span class="detail-label">Skonto Prozent:</span>
                        <span class="detail-value">{{ skonto_prozent }}%</span>
                    </div>
                    {% endif %}
                    {% if kfw_anrechenbare_kosten %}
                    <div class="detail-row">
                        <span class="detail-label">KfW anrechenbare Kosten:</span>
                        <span class="detail-value">{{ kfw_anrechenbare_kosten }}{% if currency %} {{ currency }}{% else %} EUR{% endif %}</span>
                    </div>
                    {% endif %}
                </div>

                <!-- Additional Information -->
                <div class="detail-section">
                    <h3>📝 Zusatzinformationen</h3>
                    {% if liefertermin %}
                    <div class="detail-row">
                        <span class="detail-label">Liefertermin:</span>
                        <span class="detail-value">{{ liefertermin }}</span>
                    </div>
                    {% endif %}
                    {% if aufmass_datum %}
                    <div class="detail-row">
                        <span class="detail-label">Aufmaß Datum:</span>
                        <span class="detail-value">{{ aufmass_datum }}</span>
                    </div>
                    {% endif %}
                    {% if bestellnummer %}
                    <div class="detail-row">
                        <span class="detail-label">Bestellnummer:</span>
                        <span class="detail-value">{{ bestellnummer }}</span>
                    </div>
                    {% endif %}
                    {% if material_kosten %}
                    <div class="detail-row">
                        <span class="detail-label">Materialkosten:</span>
                        <span class="detail-value">{{ material_kosten }}{% if currency %} {{ currency }}{% else %} EUR{% endif %}</span>
                    </div>
                    {% endif %}
                    {% if lohn_kosten %}
                    <div class="detail-row">
                        <span class="detail-label">Lohnkosten:</span>
                        <span class="detail-value">{{ lohn_kosten }}{% if currency %} {{ currency }}{% else %} EUR{% endif %}</span>
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- PDF Link -->
            {% if pdf_url %}
            <div class="pdf-link">
                <strong>📄 Original Rechnung anzeigen:</strong><br>
                <a href="{{ pdf_url }}" target="_blank" class="view-btn">PDF öffnen</a>
                <p style="font-size: 12px; color: #718096; margin: 10px 0 0 0;">
                    Klicken Sie hier, um die Original-Rechnung als PDF zu öffnen
                </p>
            </div>
            {% endif %}

            <!-- Changes Summary -->
            {% if changes_summary and changes_summary|length > 0 %}
            <div class="changes-section">
                <h3 style="color: #e53e3e; margin-top: 0;">🔄 Durchgeführte Bearbeitungen</h3>
                <p style="color: #4a5568; margin-bottom: 15px;">
                    Folgende Änderungen wurden an der Rechnung vorgenommen:
                </p>
                {% for change in changes_summary %}
                <div class="change-item">
                    <strong>{{ change.field }}:</strong>
                    {% if change.old_value %}
                        Von "<span style="color: #e53e3e;">{{ change.old_value }}</span>" zu "<span style="color: #48bb78;">{{ change.new_value }}</span>"
                    {% else %}
                        Neu hinzugefügt: "<span style="color: #48bb78;">{{ change.new_value }}</span>"
                    {% endif %}
                    {% if change.timestamp %}
                    <br><small style="color: #718096;">Geändert am: {{ change.timestamp }}</small>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}

            <!-- Action Buttons -->
            <div class="action-buttons">
                <h3>🎯 Genehmigung erforderlich</h3>
                <p style="color: #4a5568; margin-bottom: 25px;">
                    Bitte prüfen Sie die Rechnung sorgfältig und treffen Sie eine Entscheidung:
                </p>
                <a href="{{ approve_url }}" class="approve-btn">
                    ✅ RECHNUNG GENEHMIGEN
                </a>
                <a href="{{ reject_url }}" class="reject-btn">
                    ❌ RECHNUNG ABLEHNEN
                </a>
                <br><br>
                <p style="font-size: 14px; color: #718096;">
                    Nach Ihrer Entscheidung wird das System automatisch die nächsten Schritte einleiten.
                </p>
            </div>

            <!-- Security Notice -->
            <div class="security-notice">
                <strong>🔒 Sicherheitshinweis:</strong> Diese Genehmigungslinks sind verschlüsselt und verfallen automatisch in 7 Tagen. 
                Klicken Sie nur auf Links in E-Mails, die Sie erwartet haben. Bei Verdacht auf Manipulation kontaktieren Sie sofort den System-Administrator.
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p><strong>🤖 Automatisch generiert vom Rechnungsverarbeitungssystem</strong></p>
            <p><strong>Zeitstempel:</strong> {{ timestamp }}</p>
            <p><strong>Token gültig bis:</strong> {{ token_expires }}</p>
            <p><strong>E-Mail ID:</strong> {{ email_id or 'N/A' }}</p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 15px 0;">
            <p>Diese E-Mail wurde automatisch versendet. Bei Fragen oder Problemen wenden Sie sich an den System-Administrator.</p>
            <p><strong>Technischer Support:</strong> Für Unterstützung bei der Rechnungsverarbeitung kontaktieren Sie das IT-Team.</p>
        </div>
    </div>
</body>
</html>
            """,
            
            "dropdown_change_notification": """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dropdown Changes Notification</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .content { background: white; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; }
        .changes-section { margin-top: 20px; }
        .change-item { padding: 10px; border-left: 4px solid #007bff; margin-bottom: 10px; background: #f8f9fa; }
        .change-add { border-left-color: #28a745; background: #f8fff9; }
        .change-delete { border-left-color: #dc3545; background: #fff8f8; }
        .footer { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; font-size: 0.9em; color: #666; }
        .timestamp { font-size: 0.9em; color: #666; }
        .field-name { font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Dropdown Options Updated</h1>
        <p><strong>Date:</strong> {{ timestamp }}</p>
        <p><strong>Updated by:</strong> {{ user_email }}</p>
        <p><strong>Total changes:</strong> {{ changes|length }}</p>
    </div>
    
    <div class="content">
        <h2>Changes Summary</h2>
        <div class="changes-section">
            {% for change in changes %}
            <div class="change-item change-{{ change.type }}">
                <h4>
                    {% if change.type == 'add' %}
                        ➕ Added new option
                    {% elif change.type == 'delete' %}
                        ➖ Deleted option
                    {% endif %}
                </h4>
                <p><strong>Field:</strong> <span class="field-name">{{ change.fieldName }}</span></p>
                <p><strong>Option:</strong> {{ change.optionLabel }}</p>
                <p><strong>Value:</strong> <code>{{ change.optionValue }}</code></p>
                <p class="timestamp"><strong>Time:</strong> {{ change.timestamp }}</p>
                {% if change.success is defined %}
                    <p><strong>Status:</strong> 
                        {% if change.success %}
                            <span style="color: #28a745;">✅ Success</span>
                        {% else %}
                            <span style="color: #dc3545;">❌ Failed</span>
                        {% endif %}
                    </p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p><strong>System Information:</strong></p>
            <p>This notification confirms that dropdown options have been updated in the invoice management system.</p>
            <p>All changes are tracked for audit purposes.</p>
            <p><strong>Timestamp:</strong> {{ iso_timestamp }}</p>
        </div>
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
            
            # Generate PDF URL if file path exists
            pdf_url = None
            if invoice_data.get("file_path"):
                pdf_url = f"https://bdtcfypvadryfeabqnlc.supabase.co/storage/v1/object/public/invoices/{invoice_data['file_path']}"
            
            # Prepare comprehensive template context with ALL invoice fields
            context = {
                # Email metadata
                "submission_date": datetime.now().strftime("%d.%m.%Y um %H:%M"),
                "editor_name": editor_name,
                "editor_email": editor_email,
                "timestamp": datetime.now().isoformat(),
                "email_id": f"INV-{invoice_data.get('id', 'N/A')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "changes_summary": changes_summary or [],
                "approve_url": approve_url,
                "reject_url": reject_url,
                "token_expires": (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y um %H:%M"),
                "pdf_url": pdf_url,
                
                # Basic invoice information
                "invoice_number": invoice_data.get("rechnungsnummer"),
                "supplier_name": invoice_data.get("lieferant"),
                "invoice_date": invoice_data.get("rechnungsdatum"),
                "total_amount": invoice_data.get("rechnungsbetrag"),
                "currency": invoice_data.get("currency", "EUR"),
                
                # German business fields - comprehensive invoice data
                "rechnungsempfaenger": invoice_data.get("rechnungsempfaenger"),
                "rechnungssteller": invoice_data.get("rechnungssteller"),
                "projekt": invoice_data.get("projekt"),
                "gewerk": invoice_data.get("gewerk"),
                "kostenstelle": invoice_data.get("kostenstelle"),
                "rechnungseingang": invoice_data.get("rechnungseingang"),
                "faelligkeit": invoice_data.get("faelligkeit"),
                "skonto_datum": invoice_data.get("skonto_datum"),
                "skonto_prozent": invoice_data.get("skonto_prozent"),
                "kfw_anrechenbare_kosten": invoice_data.get("kfw_anrechenbare_kosten"),
                "weiter_berechnen_an": invoice_data.get("weiter_berechnen_an"),
                
                # Additional financial information
                "material_kosten": invoice_data.get("material_kosten"),
                "lohn_kosten": invoice_data.get("lohn_kosten"),
                "bestellnummer": invoice_data.get("bestellnummer"),
                "liefertermin": invoice_data.get("liefertermin"),
                "aufmass_datum": invoice_data.get("aufmass_datum"),
                
                # Status and workflow information
                "status": invoice_data.get("status", "zur_genehmigung"),
                "review_status": invoice_data.get("review_status", "pending"),
                "created_at": invoice_data.get("created_at"),
                "updated_at": invoice_data.get("updated_at")
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
    
    async def send_dropdown_change_notification(
        self,
        user_email: str,
        changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send notification email about dropdown option changes.
        """
        try:
            # Prepare template context
            context = {
                "user_email": user_email,
                "changes": changes,
                "timestamp": datetime.now().strftime("%d.%m.%Y um %H:%M"),
                "iso_timestamp": datetime.now().isoformat()
            }
            
            # Render template
            template = self.jinja_env.get_template("dropdown_change_notification")
            html_content = template.render(**context)
            
            # Email details
            subject = f"Dropdown Options Updated - {len(changes)} changes"
            
            # Send email
            result = await self._send_email(
                to_email=user_email,
                to_name=user_email.split('@')[0].title(),
                subject=subject,
                html_content=html_content,
                email_type="dropdown_change_notification",
                invoice_id=None,
                template_used="dropdown_change_notification"
            )
            
            if result["success"]:
                logger.info(f"Dropdown change notification sent successfully to {user_email}")
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to send dropdown change notification: {str(e)}")
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
            
            # Store in database using database service method
            expires_at = datetime.now() + timedelta(days=7)
            
            # Use database service to create approval token
            token_result = db_service.create_approval_token(
                token_hash=token_hash,
                invoice_id=str(invoice_id),
                action=action,
                user_email=user_email,
                expires_at=expires_at,
                nonce=token_data["nonce"]
            )
            
            if not token_result.get("success"):
                raise Exception(f"Failed to store approval token: {token_result.get('error')}")
            
            return jwt_token
            
        except Exception as e:
            logger.error(f"Failed to generate approval token: {str(e)}")
            raise e
    
    async def _update_invoice_after_email_send(self, invoice_id: UUID, email_type: str, result: Dict[str, Any]):
        """Update invoice email-related fields after successful email send (NO status changes)"""
        try:
            if email_type == "editor_notification":
                # Use database service to update ONLY email-related fields, not status
                email_log_entry = json.dumps([{
                    "type": "editor_notification",
                    "sent_at": datetime.now().isoformat(),
                    "success": result["success"],
                    "message_id": result.get("message_id")
                }])
                
                # Call database service method for email logging (no status change)
                update_result = db_service.log_email_send(
                    invoice_id=str(invoice_id),
                    email_type=email_type,
                    log_entry=email_log_entry
                )
                
                if not update_result.get("success"):
                    logger.warning(f"Failed to log email send: {update_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to update invoice after email send: {str(e)}")
            raise e
    
    async def _update_invoice_after_bauleiter_email(self, invoice_id: UUID, bauleiter_email: str, result: Dict[str, Any]):
        """Update invoice email-related fields after Bau-Leiter email send (NO status changes)"""
        try:
            # Use database service to update ONLY email-related fields, not status
            email_log_entry = json.dumps([{
                "type": "bauleiter_approval",
                "sent_at": datetime.now().isoformat(),
                "success": result["success"],
                "message_id": result.get("message_id")
            }])
            
            # Call database service method to update email fields only
            update_result = db_service.update_bauleiter_email_sent(
                invoice_id=str(invoice_id),
                bauleiter_email=bauleiter_email,
                log_entry=email_log_entry
            )
            
            if not update_result.get("success"):
                logger.warning(f"Failed to log Bauleiter email send: {update_result.get('error')}")
            
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
            # Use database service to create email audit log
            audit_result = db_service.create_email_audit_log(
                invoice_id=str(invoice_id) if invoice_id else None,
                email_type=email_type,
                recipient_email=recipient_email,
                subject=subject,
                send_success=send_success,
                provider_message_id=provider_message_id,
                provider_response=provider_response,
                template_used=template_used,
                email_size_bytes=email_size_bytes
            )
            
            if not audit_result.get("success"):
                logger.warning(f"Failed to log email audit: {audit_result.get('error')}")
            
        except Exception as e:
            logger.error(f"Failed to log email send: {str(e)}")
            # Don't raise - this is audit logging and shouldn't break the main flow

# Global email service instance
email_service = EmailService()
