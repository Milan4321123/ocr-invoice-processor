"""
Email Testing API Routes
Dedicated endpoints for testing email functionality during development
"""
from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from services.database import db_service
from services.email_service import email_service
from api.dependencies.auth import require_auth

router = APIRouter(prefix="/api/email-test", tags=["email-testing"])
logger = logging.getLogger(__name__)

@router.post("/bauleiter-approval")
async def test_bauleiter_approval_email(
    request_data: Dict[str, Any] = Body(...)
):  # Removed authentication for demo
    """
    Test endpoint for sending Bauleiter approval email with sample or real invoice data
    
    Expected request format:
    {
        "invoice_id": "optional - if provided, will use real invoice data",
        "bauleiter_email": "bauleiter@company.com",
        "editor_name": "Test Editor",
        "editor_email": "editor@company.com",
        "use_sample_data": true/false,
        "sample_data": {
            // Optional override data for testing
        }
    }
    """
    try:
        # Extract request parameters
        invoice_id = request_data.get("invoice_id")
        bauleiter_email = request_data.get("bauleiter_email", "bauleiter@company.com")
        editor_name = request_data.get("editor_name", "Test Editor")
        editor_email = request_data.get("editor_email", "editor@company.com")
        use_sample_data = request_data.get("use_sample_data", True)
        sample_data_override = request_data.get("sample_data", {})
        
        # Prepare invoice data
        if invoice_id and db_service.is_available and not use_sample_data:
            # Use real invoice data
            invoice_result = db_service.get_invoice(invoice_id)
            if not invoice_result["success"]:
                raise HTTPException(status_code=404, detail=f"Invoice not found: {invoice_result['error']}")
            invoice_data = invoice_result["data"]
        else:
            # Use sample data for testing
            invoice_data = {
                "id": "test-email-001",
                "rechnungsnummer": "RE-2025-001234",
                "rechnungsempfaenger": "Mustermann Bauunternehmen GmbH",
                "rechnungssteller": "Lieferant ABC GmbH",
                "lieferant": "Lieferant ABC GmbH",
                "projekt": "Neubau Bürogebäude München",
                "gewerk": "Elektroinstallation",
                "kostenstelle": "KS-2025-001",
                "rechnungsbetrag": "15.750,50",
                "currency": "EUR",
                "rechnungsdatum": "15.06.2025",
                "rechnungseingang": "28.06.2025",
                "faelligkeit": "28.07.2025",
                "skonto_datum": "08.07.2025",
                "skonto_prozent": "2,0",
                "kfw_anrechenbare_kosten": "12.500,00",
                "weiter_berechnen_an": "Bauherr Schmidt KG",
                "material_kosten": "12.000,00",
                "lohn_kosten": "3.750,50",
                "bestellnummer": "BO-2025-0456",
                "liefertermin": "10.06.2025",
                "aufmass_datum": "12.06.2025",
                "status": "edited",
                "review_status": "under_review",
                "created_at": "2025-06-15T10:30:00",
                "updated_at": "2025-06-28T14:45:00",
                "file_path": "sample/sample_invoice.pdf"
            }
            
            # Apply any override data
            invoice_data.update(sample_data_override)
        
        # Prepare sample changes summary
        changes_summary = request_data.get("changes_summary", [
            {
                "field": "Rechnungsbetrag",
                "old_value": "15.500,00 EUR",
                "new_value": "15.750,50 EUR",
                "timestamp": "28.06.2025 14:45"
            },
            {
                "field": "Projekt",
                "old_value": None,
                "new_value": "Neubau Bürogebäude München",
                "timestamp": "28.06.2025 14:42"
            },
            {
                "field": "KfW anrechenbare Kosten",
                "old_value": "10.000,00 EUR",
                "new_value": "12.500,00 EUR",
                "timestamp": "28.06.2025 14:44"
            }
        ])
        
        # Send the approval email
        email_result = await email_service.send_bauleiter_approval_request(
            invoice_data=invoice_data,
            bauleiter_email=bauleiter_email,
            editor_name=editor_name,
            editor_email=editor_email,
            changes_summary=changes_summary
        )
        
        return {
            "success": email_result["success"],
            "message": "Bauleiter approval email test completed",
            "email_result": email_result,
            "test_parameters": {
                "invoice_id": invoice_id,
                "bauleiter_email": bauleiter_email,
                "editor_name": editor_name,
                "editor_email": editor_email,
                "used_sample_data": use_sample_data or not invoice_id,
                "invoice_data_preview": {
                    "rechnungsnummer": invoice_data.get("rechnungsnummer"),
                    "lieferant": invoice_data.get("lieferant"),
                    "rechnungsbetrag": invoice_data.get("rechnungsbetrag"),
                    "projekt": invoice_data.get("projekt")
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")

@router.post("/editor-notification")
async def test_editor_notification_email(
    request_data: Dict[str, Any] = Body(...)
):
    """
    Test endpoint for sending editor notification email
    """
    try:
        # Extract request parameters
        invoice_id = request_data.get("invoice_id")
        editor_email = request_data.get("editor_email", "editor@company.com")
        editor_name = request_data.get("editor_name", "Test Editor")
        use_sample_data = request_data.get("use_sample_data", True)
        
        # Prepare invoice data (similar to above)
        if invoice_id and db_service.is_available and not use_sample_data:
            invoice_result = db_service.get_invoice(invoice_id)
            if not invoice_result["success"]:
                raise HTTPException(status_code=404, detail=f"Invoice not found: {invoice_result['error']}")
            invoice_data = invoice_result["data"]
        else:
            invoice_data = {
                "id": "test-editor-001",
                "rechnungsnummer": "RE-2025-001234",
                "lieferant": "Lieferant ABC GmbH",
                "rechnungsdatum": "15.06.2025",
                "rechnungsbetrag": "15.750,50",
                "currency": "EUR",
                "status": "completed"
            }
        
        changes_summary = request_data.get("changes_summary", [
            {
                "field": "Rechnungsbetrag",
                "old_value": "15.500,00 EUR",
                "new_value": "15.750,50 EUR",
                "timestamp": "28.06.2025 14:45"
            }
        ])
        
        # Send editor notification
        email_result = await email_service.send_editor_notification(
            invoice_data=invoice_data,
            editor_email=editor_email,
            editor_name=editor_name,
            changes_summary=changes_summary,
            request_id="TEST-" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        
        return {
            "success": email_result["success"],
            "message": "Editor notification email test completed",
            "email_result": email_result,
            "test_parameters": {
                "editor_email": editor_email,
                "editor_name": editor_name,
                "invoice_data": invoice_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Editor notification test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Editor notification test failed: {str(e)}")

@router.get("/email-config")
async def get_email_configuration():
    """
    Get current email service configuration for debugging
    """
    try:
        import os
        
        config = {
            "sendgrid_configured": bool(os.getenv("SENDGRID_API_KEY")),
            "smtp_configured": bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USERNAME")),
            "from_email": os.getenv("FROM_EMAIL", "noreply@company.com"),
            "from_name": os.getenv("FROM_NAME", "Invoice System"),
            "base_url": os.getenv("BASE_URL", "http://localhost:8001"),
            "email_service_available": email_service is not None,
            "available_templates": ["editor_notification", "bauleiter_approval", "dropdown_change_notification"]
        }
        
        return {
            "success": True,
            "email_configuration": config,
            "recommendations": _get_email_config_recommendations(config)
        }
        
    except Exception as e:
        logger.error(f"Failed to get email configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get email configuration: {str(e)}")

def _get_email_config_recommendations(config: Dict[str, Any]) -> List[str]:
    """Generate configuration recommendations"""
    recommendations = []
    
    if not config["sendgrid_configured"] and not config["smtp_configured"]:
        recommendations.append("❌ No email service configured. Set up either SendGrid (SENDGRID_API_KEY) or SMTP (SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD)")
    
    if config["sendgrid_configured"]:
        recommendations.append("✅ SendGrid is configured and ready")
    
    if config["smtp_configured"]:
        recommendations.append("✅ SMTP is configured and ready")
    
    if config["from_email"] == "noreply@company.com":
        recommendations.append("⚠️ Using default FROM_EMAIL. Consider setting a company-specific email address")
    
    if config["base_url"] == "http://localhost:8001":
        recommendations.append("⚠️ Using localhost BASE_URL. Update for production deployment")
    
    return recommendations

@router.post("/send-sample-invoice-workflow")
async def test_complete_invoice_workflow(
    request_data: Dict[str, Any] = Body(...)
):
    """
    Test complete invoice workflow: editor notification + bauleiter approval
    """
    try:
        # Get parameters
        editor_email = request_data.get("editor_email", "editor@company.com")
        bauleiter_email = request_data.get("bauleiter_email", "bauleiter@company.com")
        editor_name = request_data.get("editor_name", "Test Editor")
        
        # Sample invoice data
        invoice_data = {
            "id": "workflow-test-001",
            "rechnungsnummer": "RE-2025-WORKFLOW-001",
            "rechnungsempfaenger": "Mustermann Bauunternehmen GmbH",
            "rechnungssteller": "Premium Elektro Solutions GmbH",
            "lieferant": "Premium Elektro Solutions GmbH",
            "projekt": "Neubau Bürogebäude München - Phase 2",
            "gewerk": "Elektroinstallation & Automation",
            "kostenstelle": "KS-2025-ELE-001",
            "rechnungsbetrag": "28.950,75",
            "currency": "EUR",
            "rechnungsdatum": "20.06.2025",
            "rechnungseingang": "28.06.2025",
            "faelligkeit": "20.08.2025",
            "skonto_datum": "10.07.2025",
            "skonto_prozent": "3,0",
            "kfw_anrechenbare_kosten": "22.500,00",
            "weiter_berechnen_an": "Bauherr Immobilien AG",
            "material_kosten": "18.500,00",
            "lohn_kosten": "10.450,75",
            "bestellnummer": "BO-2025-ELE-0789",
            "liefertermin": "15.06.2025",
            "aufmass_datum": "18.06.2025",
            "status": "completed",
            "review_status": "completed_review"
        }
        
        changes_summary = [
            {
                "field": "Rechnungsbetrag",
                "old_value": "28.750,00 EUR",
                "new_value": "28.950,75 EUR",
                "timestamp": "28.06.2025 15:30"
            },
            {
                "field": "KfW anrechenbare Kosten",
                "old_value": "20.000,00 EUR",
                "new_value": "22.500,00 EUR",
                "timestamp": "28.06.2025 15:32"
            },
            {
                "field": "Skonto Prozent",
                "old_value": "2,0%",
                "new_value": "3,0%",
                "timestamp": "28.06.2025 15:34"
            },
            {
                "field": "Projekt",
                "old_value": "Neubau Bürogebäude München",
                "new_value": "Neubau Bürogebäude München - Phase 2",
                "timestamp": "28.06.2025 15:28"
            }
        ]
        
        results = {}
        
        # Step 1: Send editor notification
        try:
            editor_result = await email_service.send_editor_notification(
                invoice_data=invoice_data,
                editor_email=editor_email,
                editor_name=editor_name,
                changes_summary=changes_summary,
                request_id="WORKFLOW-TEST-" + datetime.now().strftime("%Y%m%d%H%M%S")
            )
            results["editor_notification"] = editor_result
        except Exception as e:
            results["editor_notification"] = {"success": False, "error": str(e)}
        
        # Step 2: Send bauleiter approval request
        try:
            bauleiter_result = await email_service.send_bauleiter_approval_request(
                invoice_data=invoice_data,
                bauleiter_email=bauleiter_email,
                editor_name=editor_name,
                editor_email=editor_email,
                changes_summary=changes_summary
            )
            results["bauleiter_approval"] = bauleiter_result
        except Exception as e:
            results["bauleiter_approval"] = {"success": False, "error": str(e)}
        
        # Summary
        all_success = all(result.get("success", False) for result in results.values())
        
        return {
            "success": all_success,
            "message": "Complete invoice workflow test completed",
            "workflow_results": results,
            "test_parameters": {
                "editor_email": editor_email,
                "bauleiter_email": bauleiter_email,
                "editor_name": editor_name,
                "invoice_preview": {
                    "rechnungsnummer": invoice_data["rechnungsnummer"],
                    "lieferant": invoice_data["lieferant"],
                    "rechnungsbetrag": invoice_data["rechnungsbetrag"],
                    "projekt": invoice_data["projekt"]
                }
            },
            "summary": {
                "emails_sent": sum(1 for result in results.values() if result.get("success", False)),
                "total_emails": len(results),
                "all_successful": all_success
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Complete workflow test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Complete workflow test failed: {str(e)}")
