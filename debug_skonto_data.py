#!/usr/bin/env python3
"""
Debug script to check what invoices exist in Supabase with Skonto data
"""
import sys
import os
sys.path.append('/Users/milanadhokari/Documents/OCR-Fresh/ocr-invoice-processor/backend')

from services.database import db_service

def debug_skonto_data():
    print("🔍 Checking all invoices with Skonto data...")
    
    # Get all invoices with Skonto data
    result = db_service.get_all_invoices_with_skonto_data()
    
    if not result["success"]:
        print(f"❌ Failed to get invoices: {result.get('error')}")
        return
    
    invoices = result.get("data", [])
    print(f"📊 Found {len(invoices)} invoices with Skonto data")
    
    if not invoices:
        print("No invoices found. Let's check all invoices...")
        # Get ALL invoices to see what we have
        all_result = db_service.get_all_invoices()
        if all_result["success"]:
            all_invoices = all_result.get("data", [])
            print(f"📋 Total invoices in database: {len(all_invoices)}")
            
            for i, invoice in enumerate(all_invoices[:5]):
                print(f"  {i+1}. File: {invoice.get('file_name')}")
                print(f"      Skonto %: {invoice.get('skonto_prozent')}")
                print(f"      Skonto Date: {invoice.get('skonto_datum')}")
                print(f"      Decision: {invoice.get('skonto_decision')}")
                print()
        return
    
    # Show details of found invoices
    for i, invoice in enumerate(invoices):
        print(f"\n{i+1}. Invoice ID: {invoice.get('id')}")
        print(f"   File: {invoice.get('file_name')}")
        print(f"   Supplier: {invoice.get('rechnungssteller')}")
        print(f"   Amount: {invoice.get('rechnungsbetrag')}")
        print(f"   Skonto %: {invoice.get('skonto_prozent')}")
        print(f"   Skonto Date: {invoice.get('skonto_datum')}")
        print(f"   Decision: {invoice.get('skonto_decision')}")
        print(f"   Status: {invoice.get('status')}")
        print(f"   Created: {invoice.get('created_at')}")

if __name__ == "__main__":
    debug_skonto_data()
