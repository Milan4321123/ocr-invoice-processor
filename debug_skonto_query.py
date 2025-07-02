#!/usr/bin/env python3
"""
Debug Skonto query
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv()

def debug_skonto_query():
    """Debug the Skonto query"""
    url = os.getenv("SUPA_URL")
    key = os.getenv("SUPA_KEY")
    
    if not url or not key:
        print("❌ Missing database credentials")
        return
    
    try:
        # Create database client
        client = create_client(url, key)
        
        # Test basic query first
        print("🔍 Testing basic invoice query...")
        response = client.table('invoices_clean').select("*").limit(5).execute()
        print(f"Found {len(response.data)} total invoices")
        
        # Test Skonto field query
        print("\n🔍 Testing Skonto fields query...")
        response = client.table('invoices_clean')\
            .select("id, file_name, skonto_datum, skonto_prozent, skonto_decision")\
            .not_.is_("skonto_datum", "null")\
            .execute()
        print(f"Found {len(response.data)} invoices with Skonto data")
        
        for invoice in response.data:
            print(f"  📄 {invoice.get('file_name')}: Skonto {invoice.get('skonto_prozent')}% until {invoice.get('skonto_datum')} (Decision: {invoice.get('skonto_decision')})")
        
        # Test the specific query
        print("\n🔍 Testing specific Skonto due query...")
        response = client.table('invoices_clean')\
            .select("*")\
            .not_.is_("skonto_datum", "null")\
            .not_.is_("skonto_prozent", "null")\
            .eq("skonto_decision", "pending")\
            .execute()
        print(f"Found {len(response.data)} invoices with pending Skonto decisions")
        
        # Manual date filtering
        today = datetime.now().date()
        future_date = today + timedelta(days=7)
        print(f"\n📅 Date range: {today} to {future_date}")
        
        filtered_invoices = []
        for invoice in response.data:
            try:
                skonto_datum = invoice.get("skonto_datum")
                if not skonto_datum:
                    continue
                    
                print(f"  Processing: {invoice.get('file_name')} - Skonto date: {skonto_datum} (type: {type(skonto_datum)})")
                
                # Parse different date formats
                if isinstance(skonto_datum, str):
                    if "." in skonto_datum:
                        skonto_date = datetime.strptime(skonto_datum, "%d.%m.%Y").date()
                    elif "-" in skonto_datum:
                        skonto_date = datetime.strptime(skonto_datum, "%Y-%m-%d").date()
                    else:
                        skonto_date = datetime.strptime(skonto_datum, "%Y%m%d").date()
                else:
                    skonto_date = skonto_datum
                    
                print(f"    Parsed date: {skonto_date}")
                print(f"    In range: {today <= skonto_date <= future_date}")
                
                # Check if Skonto is due within the specified period
                if today <= skonto_date <= future_date:
                    filtered_invoices.append(invoice)
                    print(f"    ✅ Added to results")
                else:
                    print(f"    ❌ Not in range")
                    
            except Exception as e:
                print(f"    ❌ Error parsing date: {e}")
                continue
        
        print(f"\n🎯 Final result: {len(filtered_invoices)} invoices with Skonto due")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_skonto_query()
