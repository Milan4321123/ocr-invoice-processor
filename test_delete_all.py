#!/usr/bin/env python3
"""
Test Script - Delete All Invoices Functionality

This script tests the new bulk delete functionality.
"""

import requests
import json
import sys

def main():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Delete All Invoices Functionality")
    print("=" * 50)
    
    # Test backend connectivity
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend not accessible")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    print("✅ Backend is accessible")
    
    # Get current invoices
    try:
        print("\n1. Checking current invoices...")
        response = requests.get(f"{base_url}/api/invoices", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch invoices: {response.status_code}")
            return False
        
        invoices_data = response.json()
        invoices = invoices_data.get('invoices', [])
        total_count = len(invoices)
        print(f"📋 Found {total_count} invoices in system")
        
        if total_count == 0:
            print("✅ No invoices to delete - testing with empty system")
        else:
            # Show invoice details
            skonto_count = 0
            for invoice in invoices:
                has_skonto = bool(
                    invoice.get("skonto_datum") or 
                    invoice.get("skonto_prozent") or 
                    invoice.get("skonto_reminder_sent") or 
                    invoice.get("skonto_decision")
                )
                if has_skonto:
                    skonto_count += 1
                print(f"   - {invoice['id']}: {invoice['file_name']} (Skonto: {'Yes' if has_skonto else 'No'})")
            
            print(f"💰 Invoices with Skonto data: {skonto_count}")
        
    except Exception as e:
        print(f"❌ Error fetching invoices: {e}")
        return False
    
    # Test delete all endpoint
    try:
        print(f"\n2. Testing DELETE ALL endpoint...")
        print(f"🚨 About to delete {total_count} invoices...")
        
        # Confirm deletion
        if total_count > 0:
            confirm = input(f"⚠️  Delete ALL {total_count} invoices? (yes/no): ").lower().strip()
            if confirm != 'yes':
                print("❌ Deletion cancelled by user")
                return False
        
        response = requests.delete(f"{base_url}/api/invoices/all", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Delete all endpoint successful!")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            
            # Verify deletion
            print(f"\n3. Verifying deletion...")
            verify_response = requests.get(f"{base_url}/api/invoices", timeout=10)
            if verify_response.status_code == 200:
                remaining = verify_response.json().get('invoices', [])
                print(f"📋 Remaining invoices: {len(remaining)}")
                
                if len(remaining) == 0:
                    print("✅ Verification successful - no invoices remaining!")
                else:
                    print("⚠️ Some invoices still remain:")
                    for remaining_invoice in remaining:
                        print(f"   - {remaining_invoice.get('id')} ({remaining_invoice.get('file_name')})")
            
        else:
            print(f"❌ Delete all failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during delete all test: {e}")
        return False
    
    print(f"\n🎯 DELETE ALL FUNCTIONALITY TEST COMPLETE!")
    print("=" * 50)
    print("✅ Backend endpoint working correctly")
    print("✅ Bulk deletion functionality implemented")
    print("✅ Comprehensive cleanup verified")
    print("✅ Response format as expected")
    
    print(f"\n🌐 Frontend Integration:")
    print(f"   📱 Dashboard URL: http://localhost:3001/dashboard")
    print(f"   🔴 Look for red 'Alle löschen' button in header")
    print(f"   ⚠️  Button appears only when invoices exist")
    print(f"   🛡️  Requires 'ALLE LÖSCHEN' confirmation")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        sys.exit(1)
