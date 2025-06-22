"""
Reports API routes for Prüfbericht (Audit Report) functionality
Provides comprehensive invoice data analysis for Bau-Leiter dashboard
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from services.database import db_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/reports/invoice-summary")
async def get_invoice_summary(
    limit: int = Query(50, description="Number of invoices to return"),
    offset: int = Query(0, description="Offset for pagination"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    project_filter: Optional[str] = Query(None, description="Filter by project")
):
    """
    Get comprehensive invoice summary for Prüfbericht dashboard
    Returns: List of all invoices with key fields for Bau-Leiter review
    """
    try:
        if not db_service.is_available:
            return {
                "success": False,
                "message": "Demo mode - Database not configured",
                "data": []
            }
        
        # Build filters
        filters = {}
        if status_filter:
            filters['status'] = status_filter
        if project_filter:
            filters['projekt'] = project_filter
        
        # Get invoices from database
        result = db_service.get_invoices(limit=limit, offset=offset, filters=filters)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {result.get('error')}")
        
        invoices = result.get("data", [])
        
        # Enhance data with computed fields
        enhanced_invoices = []
        for invoice in invoices:
            enhanced_invoice = invoice.copy()
            
            # Calculate urgency for due dates
            if invoice.get('due_date'):
                try:
                    due_date = datetime.fromisoformat(invoice['due_date'].replace('Z', '+00:00')).date()
                    today = datetime.now().date()
                    days_until_due = (due_date - today).days
                    
                    if days_until_due < 0:
                        enhanced_invoice['urgency'] = 'overdue'
                        enhanced_invoice['days_until_due'] = days_until_due
                    elif days_until_due <= 7:
                        enhanced_invoice['urgency'] = 'due_this_week'
                        enhanced_invoice['days_until_due'] = days_until_due
                    elif days_until_due <= 14:
                        enhanced_invoice['urgency'] = 'due_next_week'
                        enhanced_invoice['days_until_due'] = days_until_due
                    else:
                        enhanced_invoice['urgency'] = 'future'
                        enhanced_invoice['days_until_due'] = days_until_due
                except:
                    enhanced_invoice['urgency'] = 'unknown'
                    enhanced_invoice['days_until_due'] = None
            else:
                enhanced_invoice['urgency'] = 'no_due_date'
                enhanced_invoice['days_until_due'] = None
            
            # Add data quality indicators
            enhanced_invoice['has_missing_data'] = (
                not invoice.get('due_date') or 
                not invoice.get('total_amount') or 
                not invoice.get('vendor_name')
            )
            
            # OCR quality assessment
            confidence = invoice.get('ocr_confidence', 0)
            if confidence >= 0.8:
                enhanced_invoice['ocr_quality'] = 'high'
            elif confidence >= 0.6:
                enhanced_invoice['ocr_quality'] = 'medium'
            else:
                enhanced_invoice['ocr_quality'] = 'low'
            
            enhanced_invoices.append(enhanced_invoice)
        
        return {
            "success": True,
            "data": enhanced_invoices,
            "total": result.get("count", len(enhanced_invoices)),
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(enhanced_invoices) == limit
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get invoice summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get invoice summary: {str(e)}")

@router.get("/reports/data-quality")
async def get_data_quality():
    """
    Get data quality metrics (OCR accuracy, missing fields, etc.)
    Returns: Quality statistics and missing data summary
    """
    try:
        if not db_service.is_available:
            return {
                "success": False,
                "message": "Demo mode - Database not configured",
                "metrics": {}
            }
        
        # Get all invoices for analysis
        result = db_service.get_invoices(limit=1000)  # Get more for accurate statistics
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {result.get('error')}")
        
        invoices = result.get("data", [])
        total_invoices = len(invoices)
        
        if total_invoices == 0:
            return {
                "success": True,
                "metrics": {
                    "total_invoices": 0,
                    "message": "No invoices found"
                }
            }
        
        # Calculate metrics
        ocr_completed = sum(1 for inv in invoices if inv.get('ocr_status') == 'completed')
        ocr_pending = sum(1 for inv in invoices if inv.get('ocr_status') == 'pending')
        ocr_failed = sum(1 for inv in invoices if inv.get('ocr_status') == 'failed')
        
        missing_due_dates = sum(1 for inv in invoices if not inv.get('due_date'))
        missing_amounts = sum(1 for inv in invoices if not inv.get('total_amount'))
        missing_vendors = sum(1 for inv in invoices if not inv.get('vendor_name'))
        
        # Calculate average confidence
        confidences = [inv.get('ocr_confidence', 0) for inv in invoices if inv.get('ocr_confidence') is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Calculate quality score (0-100)
        ocr_score = (ocr_completed / total_invoices) * 100 if total_invoices > 0 else 0
        completeness_score = ((total_invoices - missing_due_dates - missing_amounts - missing_vendors) / (total_invoices * 3)) * 100 if total_invoices > 0 else 0
        confidence_score = avg_confidence * 100
        
        overall_quality = (ocr_score + completeness_score + confidence_score) / 3
        
        return {
            "success": True,
            "metrics": {
                "total_invoices": total_invoices,
                "ocr_statistics": {
                    "completed": ocr_completed,
                    "pending": ocr_pending,
                    "failed": ocr_failed,
                    "completion_rate": (ocr_completed / total_invoices) * 100 if total_invoices > 0 else 0
                },
                "missing_data": {
                    "due_dates": missing_due_dates,
                    "amounts": missing_amounts,
                    "vendors": missing_vendors,
                    "total_missing": missing_due_dates + missing_amounts + missing_vendors
                },
                "confidence_metrics": {
                    "average": avg_confidence,
                    "average_percentage": avg_confidence * 100,
                    "high_confidence": sum(1 for c in confidences if c >= 0.8),
                    "medium_confidence": sum(1 for c in confidences if 0.6 <= c < 0.8),
                    "low_confidence": sum(1 for c in confidences if c < 0.6)
                },
                "quality_score": {
                    "overall": round(overall_quality, 1),
                    "ocr_processing": round(ocr_score, 1),
                    "data_completeness": round(completeness_score, 1),
                    "ocr_confidence": round(confidence_score, 1)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get data quality metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get data quality metrics: {str(e)}")

@router.get("/reports/critical-dates")
async def get_critical_dates():
    """
    Get payment deadline overview
    Returns: Invoices grouped by due date urgency
    """
    try:
        if not db_service.is_available:
            return {
                "success": False,
                "message": "Demo mode - Database not configured",
                "data": {}
            }
        
        # Get all invoices
        result = db_service.get_invoices(limit=1000)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {result.get('error')}")
        
        invoices = result.get("data", [])
        today = datetime.now().date()
        
        # Group invoices by urgency
        grouped_invoices = {
            "overdue": [],
            "due_this_week": [],
            "due_next_week": [],
            "future": [],
            "no_due_date": []
        }
        
        for invoice in invoices:
            if not invoice.get('due_date'):
                grouped_invoices["no_due_date"].append(invoice)
                continue
            
            try:
                due_date = datetime.fromisoformat(invoice['due_date'].replace('Z', '+00:00')).date()
                days_until_due = (due_date - today).days
                
                if days_until_due < 0:
                    grouped_invoices["overdue"].append(invoice)
                elif days_until_due <= 7:
                    grouped_invoices["due_this_week"].append(invoice)
                elif days_until_due <= 14:
                    grouped_invoices["due_next_week"].append(invoice)
                else:
                    grouped_invoices["future"].append(invoice)
            except:
                grouped_invoices["no_due_date"].append(invoice)
        
        # Calculate totals for each group
        summary = {}
        for category, invoices_list in grouped_invoices.items():
            total_amount = sum(
                float(inv.get('total_amount', 0)) for inv in invoices_list 
                if inv.get('total_amount')
            )
            summary[category] = {
                "count": len(invoices_list),
                "total_amount": total_amount,
                "invoices": invoices_list
            }
        
        return {
            "success": True,
            "data": summary,
            "summary": {
                "total_invoices": len(invoices),
                "overdue_count": len(grouped_invoices["overdue"]),
                "urgent_count": len(grouped_invoices["due_this_week"]),
                "upcoming_count": len(grouped_invoices["due_next_week"]),
                "missing_due_dates": len(grouped_invoices["no_due_date"])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get critical dates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get critical dates: {str(e)}")

@router.get("/reports/project-analysis")
async def get_project_analysis():
    """
    Get invoice distribution by project and vendor
    Returns: Project/vendor breakdown with totals
    """
    try:
        if not db_service.is_available:
            return {
                "success": False,
                "message": "Demo mode - Database not configured",
                "data": {}
            }
        
        # Get all invoices
        result = db_service.get_invoices(limit=1000)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {result.get('error')}")
        
        invoices = result.get("data", [])
        
        # Group by project
        projects = {}
        vendors = {}
        
        for invoice in invoices:
            project = invoice.get('projekt') or 'Unassigned'
            vendor = invoice.get('vendor_name') or 'Unknown Vendor'
            amount = float(invoice.get('total_amount', 0)) if invoice.get('total_amount') else 0
            confidence = float(invoice.get('ocr_confidence', 0)) if invoice.get('ocr_confidence') else 0
            
            # Project analysis
            if project not in projects:
                projects[project] = {
                    "name": project,
                    "invoice_count": 0,
                    "total_amount": 0,
                    "vendors": set(),
                    "confidences": []
                }
            
            projects[project]["invoice_count"] += 1
            projects[project]["total_amount"] += amount
            projects[project]["vendors"].add(vendor)
            projects[project]["confidences"].append(confidence)
            
            # Vendor analysis
            if vendor not in vendors:
                vendors[vendor] = {
                    "name": vendor,
                    "invoice_count": 0,
                    "total_amount": 0,
                    "projects": set(),
                    "confidences": []
                }
            
            vendors[vendor]["invoice_count"] += 1
            vendors[vendor]["total_amount"] += amount
            vendors[vendor]["projects"].add(project)
            vendors[vendor]["confidences"].append(confidence)
        
        # Process project data
        project_data = []
        for project_name, data in projects.items():
            avg_confidence = sum(data["confidences"]) / len(data["confidences"]) if data["confidences"] else 0
            project_data.append({
                "name": project_name,
                "invoice_count": data["invoice_count"],
                "total_amount": data["total_amount"],
                "vendor_count": len(data["vendors"]),
                "vendors": list(data["vendors"]),
                "avg_confidence": avg_confidence
            })
        
        # Process vendor data
        vendor_data = []
        for vendor_name, data in vendors.items():
            avg_confidence = sum(data["confidences"]) / len(data["confidences"]) if data["confidences"] else 0
            vendor_data.append({
                "name": vendor_name,
                "invoice_count": data["invoice_count"],
                "total_amount": data["total_amount"],
                "project_count": len(data["projects"]),
                "projects": list(data["projects"]),
                "avg_confidence": avg_confidence
            })
        
        # Sort by total amount
        project_data.sort(key=lambda x: x["total_amount"], reverse=True)
        vendor_data.sort(key=lambda x: x["total_amount"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "projects": project_data,
                "vendors": vendor_data,
                "summary": {
                    "total_projects": len(project_data),
                    "total_vendors": len(vendor_data),
                    "total_invoices": len(invoices),
                    "total_amount": sum(p["total_amount"] for p in project_data)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get project analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get project analysis: {str(e)}")

@router.get("/reports/processing-status")
async def get_processing_status():
    """
    Get workflow status overview
    Returns: Count of invoices by processing status
    """
    try:
        if not db_service.is_available:
            return {
                "success": False,
                "message": "Demo mode - Database not configured",
                "data": {}
            }
        
        # Get all invoices
        result = db_service.get_invoices(limit=1000)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {result.get('error')}")
        
        invoices = result.get("data", [])
        
        # Group by status
        status_groups = {}
        ocr_status_groups = {}
        
        for invoice in invoices:
            # Processing status
            status = invoice.get('status', 'unknown')
            if status not in status_groups:
                status_groups[status] = {
                    "count": 0,
                    "total_amount": 0,
                    "invoices": []
                }
            
            amount = float(invoice.get('total_amount', 0)) if invoice.get('total_amount') else 0
            status_groups[status]["count"] += 1
            status_groups[status]["total_amount"] += amount
            status_groups[status]["invoices"].append(invoice)
            
            # OCR status
            ocr_status = invoice.get('ocr_status', 'unknown')
            if ocr_status not in ocr_status_groups:
                ocr_status_groups[ocr_status] = {
                    "count": 0,
                    "total_amount": 0,
                    "invoices": []
                }
            
            ocr_status_groups[ocr_status]["count"] += 1
            ocr_status_groups[ocr_status]["total_amount"] += amount
            ocr_status_groups[ocr_status]["invoices"].append(invoice)
        
        return {
            "success": True,
            "data": {
                "processing_status": status_groups,
                "ocr_status": ocr_status_groups,
                "summary": {
                    "total_invoices": len(invoices),
                    "total_amount": sum(
                        float(inv.get('total_amount', 0)) for inv in invoices 
                        if inv.get('total_amount')
                    ),
                    "status_distribution": {
                        status: data["count"] for status, data in status_groups.items()
                    },
                    "ocr_distribution": {
                        status: data["count"] for status, data in ocr_status_groups.items()
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get processing status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing status: {str(e)}")
