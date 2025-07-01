"""
Skonto Dashboard API Routes
Enhanced reporting and analytics for Skonto performance tracking.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from services.database import db_service
from services.skonto_scheduler import skonto_scheduler, run_manual_skonto_check

logger = logging.getLogger(__name__)
router = APIRouter()

# Response Models
class SkontoSummaryResponse(BaseModel):
    total_opportunities: int
    total_potential_savings: float
    urgent_count: int
    urgent_potential: float
    monthly_average_savings: float
    success_rate: float
    reminders_sent_count: int

class SkontoPerformanceResponse(BaseModel):
    month: str
    total_invoices: int
    skonto_taken: int
    skonto_missed: int
    reminders_sent: int
    savings_achieved: float
    savings_missed: float
    success_rate: float

class SkontoOpportunityResponse(BaseModel):
    id: str
    invoice_number: str
    supplier: str
    amount: float
    skonto_percentage: float
    skonto_date: str
    potential_savings: float
    days_until_expiry: int
    urgency_level: str
    reminder_sent: bool

@router.get("/skonto/dashboard/summary", response_model=SkontoSummaryResponse)
async def get_skonto_summary():
    """
    Get comprehensive Skonto performance summary.
    Returns current opportunities, savings potential, and performance metrics.
    """
    try:
        logger.info("📊 Fetching Skonto dashboard summary")
        
        # Use database service methods instead of raw SQL
        skonto_opportunities = db_service.get_invoices_with_skonto_due(days_ahead=365)  # Get all active Skonto opportunities
        
        if not skonto_opportunities["success"]:
            logger.error(f"Failed to get Skonto opportunities: {skonto_opportunities.get('error')}")
            raise HTTPException(status_code=500, detail="Failed to fetch Skonto opportunities")
        
        invoices = skonto_opportunities["data"]
        
        # Calculate summary metrics
        total_opportunities = len(invoices)
        total_potential_savings = 0.0
        urgent_count = 0
        urgent_potential = 0.0
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        urgent_cutoff = today + timedelta(days=3)
        
        for invoice in invoices:
            # Calculate potential savings
            amount = invoice.get("rechnungsbetrag", 0) or 0
            percentage = invoice.get("skonto_prozent", 0) or 0
            potential = float(amount) * float(percentage) / 100 if amount and percentage else 0
            total_potential_savings += potential
            
            # Check if urgent (expiring within 3 days)
            skonto_datum = invoice.get("skonto_datum")
            if skonto_datum:
                try:
                    if isinstance(skonto_datum, str):
                        if "-" in skonto_datum:
                            skonto_date = datetime.strptime(skonto_datum, "%Y-%m-%d").date()
                        else:
                            skonto_date = datetime.strptime(skonto_datum, "%d.%m.%Y").date()
                    else:
                        skonto_date = skonto_datum
                    
                    if skonto_date <= urgent_cutoff:
                        urgent_count += 1
                        urgent_potential += potential
                except:
                    logger.warning(f"Could not parse skonto date: {skonto_datum}")
        
        # Get historical performance (simplified)
        # For now, use default values since we need proper aggregation queries
        monthly_average_savings = 0.0
        success_rate = 0.0
        reminders_sent_count = 0
        
        # Count reminders sent
        for invoice in invoices:
            if invoice.get("skonto_reminder_sent"):
                reminders_sent_count += 1
        
        response = SkontoSummaryResponse(
            total_opportunities=total_opportunities,
            total_potential_savings=total_potential_savings,
            urgent_count=urgent_count,
            urgent_potential=urgent_potential,
            monthly_average_savings=monthly_average_savings,
            success_rate=success_rate,
            reminders_sent_count=reminders_sent_count
        )
        
        logger.info(f"✅ Skonto summary: {response.total_opportunities} opportunities, €{response.total_potential_savings:.2f} potential")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get Skonto summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Skonto summary: {str(e)}")

@router.get("/skonto/dashboard/performance", response_model=List[SkontoPerformanceResponse])
async def get_skonto_performance(months: int = Query(default=12, ge=1, le=24)):
    """
    Get monthly Skonto performance metrics.
    
    Args:
        months: Number of months to retrieve (1-24)
    """
    try:
        logger.info(f"📈 Fetching Skonto performance for last {months} months")
        
        # Get all invoices from database and perform calculations in Python
        invoices_result = db_service.get_all_invoices(limit=10000)  # Get enough history
        
        if not invoices_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to fetch invoices")
        
        invoices = invoices_result.get("data", [])
        
        # Group invoices by month and calculate metrics
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        monthly_data = defaultdict(lambda: {
            "total_invoices": 0,
            "skonto_taken": 0,
            "skonto_missed": 0,
            "reminders_sent": 0,
            "savings_achieved": 0.0,
            "savings_missed": 0.0
        })
        
        for invoice in invoices:
            # Parse created_at date
            created_at = invoice.get("created_at")
            if not created_at:
                continue
                
            try:
                if isinstance(created_at, str):
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).replace(tzinfo=None)
                else:
                    created_date = created_at
                    
                # Skip if too old
                if created_date < cutoff_date:
                    continue
                    
                month_key = created_date.strftime('%Y-%m')
                
                # Check if invoice has Skonto data
                skonto_prozent = invoice.get("skonto_prozent")
                skonto_datum = invoice.get("skonto_datum")
                
                if skonto_prozent and skonto_datum:
                    monthly_data[month_key]["total_invoices"] += 1
                    
                    # Check Skonto decision
                    skonto_decision = invoice.get("skonto_decision")
                    if skonto_decision == "taken":
                        monthly_data[month_key]["skonto_taken"] += 1
                        # Use actual savings if available, otherwise calculate
                        actual_savings = invoice.get("actual_skonto_savings")
                        if actual_savings:
                            monthly_data[month_key]["savings_achieved"] += float(actual_savings)
                        else:
                            rechnungsbetrag = invoice.get("rechnungsbetrag") or invoice.get("gesamt_brutto", 0)
                            if rechnungsbetrag:
                                calculated_savings = float(rechnungsbetrag) * float(skonto_prozent) / 100
                                monthly_data[month_key]["savings_achieved"] += calculated_savings
                    elif skonto_decision == "missed":
                        monthly_data[month_key]["skonto_missed"] += 1
                        # Calculate missed savings
                        rechnungsbetrag = invoice.get("rechnungsbetrag") or invoice.get("gesamt_brutto", 0)
                        if rechnungsbetrag:
                            missed_savings = float(rechnungsbetrag) * float(skonto_prozent) / 100
                            monthly_data[month_key]["savings_missed"] += missed_savings
                    
                    # Check if reminder was sent
                    if invoice.get("skonto_reminder_sent"):
                        monthly_data[month_key]["reminders_sent"] += 1
                        
            except Exception as e:
                logger.warning(f"Failed to process invoice {invoice.get('id')} for performance: {e}")
                continue
        
        # Convert to response format
        performance_data = []
        for month_key in sorted(monthly_data.keys(), reverse=True):
            data = monthly_data[month_key]
            
            # Calculate success rate
            total_decisions = data["skonto_taken"] + data["skonto_missed"]
            success_rate = (data["skonto_taken"] / total_decisions * 100) if total_decisions > 0 else 0.0
            
            performance_data.append(SkontoPerformanceResponse(
                month=month_key,
                total_invoices=data["total_invoices"],
                skonto_taken=data["skonto_taken"],
                skonto_missed=data["skonto_missed"],
                reminders_sent=data["reminders_sent"],
                savings_achieved=round(data["savings_achieved"], 2),
                savings_missed=round(data["savings_missed"], 2),
                success_rate=round(success_rate, 2)
            ))
        
        # Limit to requested months
        performance_data = performance_data[:months]
        
        logger.info(f"✅ Retrieved {len(performance_data)} months of performance data")
        return performance_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get Skonto performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Skonto performance: {str(e)}")

@router.get("/skonto/dashboard/opportunities", response_model=List[SkontoOpportunityResponse])
async def get_skonto_opportunities(
    urgency: Optional[str] = Query(default=None, regex="^(urgent|important|upcoming|all)$"),
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Get current Skonto opportunities.
    
    Args:
        urgency: Filter by urgency level (urgent, important, upcoming, all)
        limit: Maximum number of opportunities to return
    """
    try:
        logger.info(f"🎯 Fetching Skonto opportunities (urgency: {urgency}, limit: {limit})")
        
        # Get all invoices and filter for Skonto opportunities
        invoices_result = db_service.get_all_invoices(limit=10000)
        
        if not invoices_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to fetch invoices")
        
        invoices = invoices_result.get("data", [])
        opportunities = []
        
        from datetime import datetime
        today = datetime.now().date()
        
        for invoice in invoices:
            # Check if invoice has Skonto available
            skonto_prozent = invoice.get("skonto_prozent")
            skonto_datum = invoice.get("skonto_datum")
            skonto_decision = invoice.get("skonto_decision")
            
            # Skip if no Skonto data
            if not skonto_prozent or not skonto_datum:
                continue
                
            # Skip if Skonto percentage is 0 or less
            try:
                if float(skonto_prozent) <= 0:
                    continue
            except (ValueError, TypeError):
                continue
                
            # Skip if decision already made (not pending or null)
            if skonto_decision and skonto_decision != "pending":
                continue
            
            try:
                # Parse Skonto date
                if isinstance(skonto_datum, str):
                    if "." in skonto_datum:
                        skonto_date = datetime.strptime(skonto_datum, "%d.%m.%Y").date()
                    elif "-" in skonto_datum:
                        skonto_date = datetime.strptime(skonto_datum, "%Y-%m-%d").date()
                    else:
                        skonto_date = datetime.strptime(skonto_datum, "%Y%m%d").date()
                else:
                    skonto_date = skonto_datum
                
                # Skip if Skonto has expired
                if skonto_date < today:
                    continue
                
                # Calculate days until expiry
                days_until_expiry = (skonto_date - today).days
                
                # Determine urgency level
                if days_until_expiry <= 1:
                    urgency_level = "urgent"
                elif days_until_expiry <= 3:
                    urgency_level = "important"
                elif days_until_expiry <= 7:
                    urgency_level = "upcoming"
                else:
                    urgency_level = "normal"
                
                # Filter by urgency if specified
                if urgency and urgency != "all":
                    urgency_days = {
                        "urgent": 1,
                        "important": 3,
                        "upcoming": 7
                    }
                    max_days = urgency_days.get(urgency, 7)
                    if days_until_expiry > max_days:
                        continue
                
                # Get amount (try different field names)
                amount = invoice.get("rechnungsbetrag") or invoice.get("gesamt_brutto", 0)
                if not amount:
                    continue
                
                # Calculate potential savings
                potential_savings = float(amount) * float(skonto_prozent) / 100
                
                opportunities.append(SkontoOpportunityResponse(
                    id=str(invoice["id"]),
                    invoice_number=invoice.get("file_name") or "N/A",  # Use file_name from your schema
                    supplier=invoice.get("rechnungssteller") or "N/A",  # Use rechnungssteller from your schema
                    amount=float(amount),
                    skonto_percentage=float(skonto_prozent),
                    skonto_date=skonto_datum,
                    potential_savings=round(potential_savings, 2),
                    days_until_expiry=days_until_expiry,
                    urgency_level=urgency_level,
                    reminder_sent=bool(invoice.get("skonto_reminder_sent", False))
                ))
                
            except Exception as e:
                logger.warning(f"Failed to process Skonto opportunity for invoice {invoice.get('id')}: {e}")
                continue
        
        # Sort by urgency (least days first) and then by potential savings (highest first)
        opportunities.sort(key=lambda x: (x.days_until_expiry, -x.potential_savings))
        
        # Limit results
        opportunities = opportunities[:limit]
        
        logger.info(f"✅ Retrieved {len(opportunities)} Skonto opportunities")
        return opportunities
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get Skonto opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Skonto opportunities: {str(e)}")

@router.post("/skonto/scheduler/run-check")
async def run_skonto_reminder_check():
    """
    Manually trigger a Skonto reminder check.
    Useful for testing or immediate processing.
    """
    try:
        logger.info("🔧 Manual Skonto reminder check triggered")
        
        result = await run_manual_skonto_check()
        
        logger.info("✅ Manual Skonto reminder check completed")
        return {
            "success": True,
            "message": "Skonto reminder check completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to run manual Skonto check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to run Skonto check: {str(e)}")

@router.get("/skonto/scheduler/status")
async def get_scheduler_status():
    """
    Get current status of the Skonto reminder scheduler.
    """
    try:
        status = skonto_scheduler.get_status()
        
        return {
            "success": True,
            "scheduler_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")

@router.post("/skonto/test/send-reminder/{invoice_id}")
async def send_test_skonto_reminder(
    invoice_id: str,
    recipient_email: str = Query(..., description="Email address to send test reminder to")
):
    """
    Send a test Skonto reminder for a specific invoice.
    Useful for testing the email functionality.
    """
    try:
        logger.info(f"🧪 Sending test Skonto reminder for invoice {invoice_id} to {recipient_email}")
        
        from services.skonto_scheduler import send_test_skonto_reminder
        result = await send_test_skonto_reminder(invoice_id, recipient_email)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Test Skonto reminder sent to {recipient_email}",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send test Skonto reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send test reminder: {str(e)}")

@router.get("/skonto/reports/savings-potential")
async def get_savings_potential_report():
    """
    Get detailed report on Skonto savings potential and missed opportunities.
    """
    try:
        logger.info("📊 Generating Skonto savings potential report")
        
        # Get all invoices and calculate metrics in Python
        invoices_result = db_service.get_all_invoices(limit=10000)
        
        if not invoices_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to fetch invoices")
        
        invoices = invoices_result.get("data", [])
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        cutoff_date = datetime.now() - timedelta(days=365)  # Last 12 months
        
        # Initialize counters
        current_opportunities = {
            "count": 0,
            "total_potential": 0.0,
            "potential_values": [],
            "expiry_days": []
        }
        
        historical_performance = {
            "taken_count": 0,
            "missed_count": 0,
            "total_saved": 0.0,
            "total_missed": 0.0
        }
        
        for invoice in invoices:
            # Check for current opportunities
            skonto_prozent = invoice.get("skonto_prozent")
            skonto_datum = invoice.get("skonto_datum")
            skonto_decision = invoice.get("skonto_decision")
            
            if skonto_prozent and skonto_datum:
                try:
                    # Parse Skonto date
                    if isinstance(skonto_datum, str):
                        if "." in skonto_datum:
                            skonto_date = datetime.strptime(skonto_datum, "%d.%m.%Y").date()
                        elif "-" in skonto_datum:
                            skonto_date = datetime.strptime(skonto_datum, "%Y-%m-%d").date()
                        else:
                            skonto_date = datetime.strptime(skonto_datum, "%Y%m%d").date()
                    else:
                        skonto_date = skonto_datum
                    
                    # Current opportunities (still valid, decision pending)
                    if (skonto_decision == "pending" or not skonto_decision) and skonto_date >= today:
                        rechnungsbetrag = invoice.get("rechnungsbetrag") or invoice.get("gesamt_brutto", 0)
                        if rechnungsbetrag and float(skonto_prozent) > 0:
                            potential_savings = float(rechnungsbetrag) * float(skonto_prozent) / 100
                            current_opportunities["count"] += 1
                            current_opportunities["total_potential"] += potential_savings
                            current_opportunities["potential_values"].append(potential_savings)
                            
                            days_until_expiry = (skonto_date - today).days
                            current_opportunities["expiry_days"].append(days_until_expiry)
                    
                    # Historical performance (check if invoice is from last 12 months)
                    created_at = invoice.get("created_at")
                    if created_at:
                        try:
                            if isinstance(created_at, str):
                                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).replace(tzinfo=None)
                            else:
                                created_date = created_at
                                
                            if created_date >= cutoff_date:
                                if skonto_decision == "taken":
                                    historical_performance["taken_count"] += 1
                                    # Use actual savings if available, otherwise calculate
                                    actual_savings = invoice.get("actual_skonto_savings")
                                    if actual_savings:
                                        historical_performance["total_saved"] += float(actual_savings)
                                    else:
                                        rechnungsbetrag = invoice.get("rechnungsbetrag") or invoice.get("gesamt_brutto", 0)
                                        if rechnungsbetrag:
                                            calculated_savings = float(rechnungsbetrag) * float(skonto_prozent) / 100
                                            historical_performance["total_saved"] += calculated_savings
                                elif skonto_decision == "missed":
                                    historical_performance["missed_count"] += 1
                                    # Calculate missed savings
                                    rechnungsbetrag = invoice.get("rechnungsbetrag") or invoice.get("gesamt_brutto", 0)
                                    if rechnungsbetrag:
                                        missed_savings = float(rechnungsbetrag) * float(skonto_prozent) / 100
                                        historical_performance["total_missed"] += missed_savings
                        except Exception as e:
                            logger.warning(f"Failed to parse created_at for invoice {invoice.get('id')}: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Failed to process invoice {invoice.get('id')} for savings report: {e}")
                    continue
        
        # Calculate derived metrics
        avg_potential = (current_opportunities["total_potential"] / current_opportunities["count"]) if current_opportunities["count"] > 0 else 0.0
        earliest_expiry = min(current_opportunities["expiry_days"]) if current_opportunities["expiry_days"] else None
        latest_expiry = max(current_opportunities["expiry_days"]) if current_opportunities["expiry_days"] else None
        
        total_decisions = historical_performance["taken_count"] + historical_performance["missed_count"]
        success_rate = (historical_performance["taken_count"] / total_decisions * 100) if total_decisions > 0 else 0.0
        
        return {
            "success": True,
            "report": {
                "current_opportunities": {
                    "count": current_opportunities["count"],
                    "total_potential": round(current_opportunities["total_potential"], 2),
                    "average_potential": round(avg_potential, 2),
                    "earliest_expiry_days": earliest_expiry,
                    "latest_expiry_days": latest_expiry
                },
                "historical_performance": {
                    "taken_count": historical_performance["taken_count"],
                    "missed_count": historical_performance["missed_count"],
                    "total_saved": round(historical_performance["total_saved"], 2),
                    "total_missed": round(historical_performance["total_missed"], 2),
                    "success_rate": round(success_rate, 2)
                }
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate savings potential report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
