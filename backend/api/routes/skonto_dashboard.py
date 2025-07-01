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
        
        # Get current opportunities
        opportunities_result = db_service.execute_query("""
            SELECT 
                COUNT(*) as total_opportunities,
                COALESCE(SUM(rechnungsbetrag * skonto_prozent / 100), 0) as total_potential,
                COUNT(CASE WHEN (skonto_datum::date - CURRENT_DATE) <= 3 THEN 1 END) as urgent_count,
                COALESCE(SUM(CASE WHEN (skonto_datum::date - CURRENT_DATE) <= 3 
                    THEN (rechnungsbetrag * skonto_prozent / 100) END), 0) as urgent_potential
            FROM invoices_clean 
            WHERE skonto_datum IS NOT NULL 
              AND skonto_prozent IS NOT NULL
              AND skonto_decision = 'pending'
              AND skonto_datum::date >= CURRENT_DATE
        """)
        
        # Get historical performance
        performance_result = db_service.execute_query("""
            SELECT 
                AVG(monthly_savings) as avg_monthly_savings,
                AVG(success_rate) as avg_success_rate,
                SUM(reminders_sent) as total_reminders_sent
            FROM (
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    SUM(CASE WHEN skonto_decision = 'taken' THEN actual_skonto_savings ELSE 0 END) as monthly_savings,
                    CASE 
                        WHEN COUNT(CASE WHEN skonto_decision IN ('taken', 'missed') THEN 1 END) > 0
                        THEN COUNT(CASE WHEN skonto_decision = 'taken' THEN 1 END)::DECIMAL / 
                             COUNT(CASE WHEN skonto_decision IN ('taken', 'missed') THEN 1 END) * 100
                        ELSE 0
                    END as success_rate,
                    COUNT(CASE WHEN skonto_reminder_sent = TRUE THEN 1 END) as reminders_sent
                FROM invoices_clean 
                WHERE skonto_datum IS NOT NULL 
                  AND created_at >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', created_at)
            ) monthly_stats
        """)
        
        if not opportunities_result["success"] or not performance_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to fetch Skonto summary data")
        
        opportunities = opportunities_result["data"][0] if opportunities_result["data"] else {}
        performance = performance_result["data"][0] if performance_result["data"] else {}
        
        return SkontoSummaryResponse(
            total_opportunities=opportunities.get("total_opportunities", 0),
            total_potential_savings=float(opportunities.get("total_potential", 0)),
            urgent_count=opportunities.get("urgent_count", 0),
            urgent_potential=float(opportunities.get("urgent_potential", 0)),
            monthly_average_savings=float(performance.get("avg_monthly_savings", 0)),
            success_rate=float(performance.get("avg_success_rate", 0)),
            reminders_sent_count=performance.get("total_reminders_sent", 0)
        )
        
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
        
        result = db_service.execute_query("""
            SELECT 
                TO_CHAR(month, 'YYYY-MM') as month,
                total_invoices_with_skonto as total_invoices,
                skonto_taken_count as skonto_taken,
                skonto_missed_count as skonto_missed,
                reminders_sent_count as reminders_sent,
                total_savings_achieved as savings_achieved,
                total_savings_missed as savings_missed,
                COALESCE(skonto_success_rate, 0) as success_rate
            FROM skonto_performance_summary
            WHERE month >= CURRENT_DATE - INTERVAL '%s months'
            ORDER BY month DESC
            LIMIT %s
        """, (months, months))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to fetch performance data")
        
        performance_data = []
        for row in result["data"]:
            performance_data.append(SkontoPerformanceResponse(
                month=row["month"],
                total_invoices=row["total_invoices"],
                skonto_taken=row["skonto_taken"],
                skonto_missed=row["skonto_missed"],
                reminders_sent=row["reminders_sent"],
                savings_achieved=float(row["savings_achieved"]),
                savings_missed=float(row["savings_missed"]),
                success_rate=float(row["success_rate"])
            ))
        
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
        
        where_clause = ""
        if urgency and urgency != "all":
            urgency_days = {
                "urgent": 1,
                "important": 3,
                "upcoming": 7
            }
            days = urgency_days.get(urgency, 7)
            where_clause = f"AND (skonto_datum::date - CURRENT_DATE) <= {days}"
        
        result = db_service.execute_query(f"""
            SELECT 
                id,
                rechnungsnummer as invoice_number,
                lieferant as supplier,
                rechnungsbetrag as amount,
                skonto_prozent as skonto_percentage,
                skonto_datum,
                potential_savings,
                days_until_expiry,
                urgency_level,
                (CASE WHEN skonto_reminder_sent THEN true ELSE false END) as reminder_sent
            FROM current_skonto_opportunities
            WHERE 1=1 {where_clause}
            ORDER BY days_until_expiry ASC, potential_savings DESC
            LIMIT %s
        """, (limit,))
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to fetch opportunities")
        
        opportunities = []
        for row in result["data"]:
            opportunities.append(SkontoOpportunityResponse(
                id=str(row["id"]),
                invoice_number=row["invoice_number"] or "N/A",
                supplier=row["supplier"] or "N/A",
                amount=float(row["amount"]),
                skonto_percentage=float(row["skonto_percentage"]),
                skonto_date=row["skonto_datum"],
                potential_savings=float(row["potential_savings"]),
                days_until_expiry=row["days_until_expiry"],
                urgency_level=row["urgency_level"],
                reminder_sent=bool(row["reminder_sent"])
            ))
        
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
        
        # Current potential
        current_potential = db_service.execute_query("""
            SELECT 
                COUNT(*) as active_opportunities,
                SUM(rechnungsbetrag * skonto_prozent / 100) as total_potential,
                AVG(rechnungsbetrag * skonto_prozent / 100) as avg_potential,
                MIN(days_until_expiry) as earliest_expiry,
                MAX(days_until_expiry) as latest_expiry
            FROM current_skonto_opportunities
        """)
        
        # Historical savings
        historical_savings = db_service.execute_query("""
            SELECT 
                COUNT(CASE WHEN skonto_decision = 'taken' THEN 1 END) as taken_count,
                COUNT(CASE WHEN skonto_decision = 'missed' THEN 1 END) as missed_count,
                SUM(CASE WHEN skonto_decision = 'taken' THEN actual_skonto_savings ELSE 0 END) as total_saved,
                SUM(CASE WHEN skonto_decision = 'missed' AND skonto_prozent IS NOT NULL 
                    THEN (rechnungsbetrag * skonto_prozent / 100) ELSE 0 END) as total_missed
            FROM invoices_clean 
            WHERE skonto_datum IS NOT NULL 
              AND skonto_decision IN ('taken', 'missed')
              AND created_at >= CURRENT_DATE - INTERVAL '12 months'
        """)
        
        if not current_potential["success"] or not historical_savings["success"]:
            raise HTTPException(status_code=500, detail="Failed to generate savings report")
        
        current = current_potential["data"][0] if current_potential["data"] else {}
        historical = historical_savings["data"][0] if historical_savings["data"] else {}
        
        return {
            "success": True,
            "report": {
                "current_opportunities": {
                    "count": current.get("active_opportunities", 0),
                    "total_potential": float(current.get("total_potential", 0)),
                    "average_potential": float(current.get("avg_potential", 0)),
                    "earliest_expiry_days": current.get("earliest_expiry"),
                    "latest_expiry_days": current.get("latest_expiry")
                },
                "historical_performance": {
                    "taken_count": historical.get("taken_count", 0),
                    "missed_count": historical.get("missed_count", 0),
                    "total_saved": float(historical.get("total_saved", 0)),
                    "total_missed": float(historical.get("total_missed", 0)),
                    "success_rate": round(
                        (historical.get("taken_count", 0) / 
                         max(1, historical.get("taken_count", 0) + historical.get("missed_count", 0))) * 100, 2
                    )
                }
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate savings potential report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
