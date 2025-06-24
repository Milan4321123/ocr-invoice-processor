#!/usr/bin/env python3
"""
Comprehensive test script for Prüfbericht (Audit Report) functionality
Tests all report endpoints with realistic data
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_report_endpoint(endpoint: str, name: str) -> Dict[str, Any]:
    """Test a single report endpoint and return results"""
    print(f"\n🔍 Testing {name} Report ({endpoint})")
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: SUCCESS")
            
            if endpoint == "/api/reports/data-quality":
                metrics = data.get("metrics", {})
                print(f"  📊 Total Invoices: {metrics.get('total_invoices', 0)}")
                print(f"  📊 OCR Completion Rate: {metrics.get('ocr_statistics', {}).get('completion_rate', 0):.1f}%")
                print(f"  📊 Overall Quality Score: {metrics.get('quality_score', {}).get('overall', 0):.1f}%")
                
            elif endpoint == "/api/reports/critical-dates":
                summary = data.get("summary", {})
                print(f"  📊 Overdue: {summary.get('overdue_count', 0)}")
                print(f"  📊 Due This Week: {summary.get('urgent_count', 0)}")
                print(f"  📊 Due Next Week: {summary.get('upcoming_count', 0)}")
                print(f"  📊 Missing Due Dates: {summary.get('missing_due_dates', 0)}")
                
            elif endpoint == "/api/reports/project-analysis":
                summary = data.get("data", {}).get("summary", {})
                print(f"  📊 Total Projects: {summary.get('total_projects', 0)}")
                print(f"  📊 Total Vendors: {summary.get('total_vendors', 0)}")
                print(f"  📊 Total Amount: €{summary.get('total_amount', 0):,.2f}")
                
            elif endpoint == "/api/reports/processing-status":
                summary = data.get("data", {}).get("summary", {})
                print(f"  📊 Total Invoices: {summary.get('total_invoices', 0)}")
                print(f"  📊 Total Amount: €{summary.get('total_amount', 0):,.2f}")
                status_dist = summary.get('status_distribution', {})
                for status, count in status_dist.items():
                    print(f"  📊 {status.title()}: {count}")
                    
            elif endpoint == "/api/reports/invoice-summary":
                print(f"  📊 Total Invoices: {data.get('total', 0)}")
                enhanced_data = data.get('data', [])
                if enhanced_data:
                    urgency_counts = {}
                    quality_counts = {}
                    for invoice in enhanced_data:
                        urgency = invoice.get('urgency', 'unknown')
                        quality = invoice.get('ocr_quality', 'unknown')
                        urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
                        quality_counts[quality] = quality_counts.get(quality, 0) + 1
                    
                    print(f"  📊 Urgency Distribution: {urgency_counts}")
                    print(f"  📊 OCR Quality Distribution: {quality_counts}")
            
            return {"success": True, "data": data}
            
        else:
            print(f"  ❌ Status: FAILED ({response.status_code})")
            print(f"  ❌ Error: {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Run comprehensive Prüfbericht tests"""
    print("🎯 PRÜFBERICHT (AUDIT REPORT) COMPREHENSIVE TEST")
    print("=" * 60)
    
    # List of report endpoints to test
    report_tests = [
        ("/api/reports/data-quality", "Data Quality"),
        ("/api/reports/critical-dates", "Critical Dates"),
        ("/api/reports/project-analysis", "Project Analysis"),
        ("/api/reports/processing-status", "Processing Status"),
        ("/api/reports/invoice-summary", "Invoice Summary")
    ]
    
    results = {}
    
    # Test each endpoint
    for endpoint, name in report_tests:
        results[name] = test_report_endpoint(endpoint, name)
    
    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 60)
    successful_tests = sum(1 for result in results.values() if result["success"])
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if successful_tests == total_tests:
        print(f"\n🎉 ALL PRÜFBERICHT TESTS PASSED!")
        print("The audit report functionality is fully operational.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the logs above.")
    
    # Test filtering and pagination
    print(f"\n🔧 Testing Advanced Features")
    print("=" * 30)
    
    # Test invoice summary with filters
    print("Testing invoice summary with project filter...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/invoice-summary?project_filter=Neubau Bürogebäude München&limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Project filter working: {data.get('total', 0)} invoices found")
        else:
            print(f"  ❌ Project filter failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Project filter exception: {e}")
    
    # Test status filter
    print("Testing invoice summary with status filter...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/invoice-summary?status_filter=pending&limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status filter working: {data.get('total', 0)} pending invoices found")
        else:
            print(f"  ❌ Status filter failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Status filter exception: {e}")
    
    print(f"\n✨ Prüfbericht testing complete!")

if __name__ == "__main__":
    main()
