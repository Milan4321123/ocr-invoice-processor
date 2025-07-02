#!/usr/bin/env python3
"""
Cleanup Script - Delete All Invoices

This script will delete all invoices from the system to start fresh.
"""

import requests
import json
import sys

def main():
    base_url = "http://localhost:8000"
    
    print("🧹 Starting invoice cleanup...")
    
    # Get all invoices
    try:
        response = requests.get(f"{base_url}/api/invoices")
        if response.status_code != 200:
            print(f"❌ Failed to get invoices: {response.status_code}")
            sys.exit(1)
            
        data = response.json()
        invoices = data.get('invoices', [])
        print(f"📋 Found {len(invoices)} invoices to delete")
        
        if len(invoices) == 0:
            print("✅ No invoices to delete - system is already clean!")
            return
            
        # Delete each invoice
        deleted_count = 0
        failed_count = 0
        
        for invoice in invoices:
            invoice_id = invoice.get('id')
            filename = invoice.get('filename', 'Unknown')
            status = invoice.get('status', 'Unknown')
            
            print(f"🗑️ Deleting invoice {invoice_id} (Status: {status})")
            
            try:
                delete_response = requests.delete(f"{base_url}/api/invoices/{invoice_id}")
                
                if delete_response.status_code in [200, 204, 404]:
                    print(f"   ✅ Deleted successfully")
                    deleted_count += 1
                else:
                    print(f"   ❌ Delete failed: {delete_response.status_code}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"   ❌ Delete error: {str(e)}")
                failed_count += 1
        
        # Summary
        print("\n" + "="*50)
        print("📊 CLEANUP SUMMARY")
        print("="*50)
        print(f"✅ Successfully deleted: {deleted_count}")
        print(f"❌ Failed to delete: {failed_count}")
        print(f"📋 Total processed: {len(invoices)}")
        
        if failed_count == 0:
            print("\n🎉 All invoices successfully deleted! System is now clean.")
        else:
            print(f"\n⚠️ {failed_count} invoices could not be deleted.")
            
        # Verify cleanup
        print("\n🔍 Verifying cleanup...")
        verify_response = requests.get(f"{base_url}/api/invoices")
        if verify_response.status_code == 200:
            remaining = verify_response.json().get('invoices', [])
            print(f"📋 Remaining invoices: {len(remaining)}")
            
            if len(remaining) == 0:
                print("✅ Cleanup verified - no invoices remaining!")
            else:
                print("⚠️ Some invoices still remain:")
                for remaining_invoice in remaining:
                    print(f"   - {remaining_invoice.get('id')} ({remaining_invoice.get('status')})")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
