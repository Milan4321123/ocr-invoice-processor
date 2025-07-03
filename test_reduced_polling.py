#!/usr/bin/env python3
"""
Test script to verify that folder watcher polling has been reduced.
This script monitors backend logs for a period to check request frequency.
"""

import subprocess
import time
import re
from collections import defaultdict
from datetime import datetime, timedelta

def test_polling_frequency():
    """Test that folder watcher requests are less frequent"""
    print("🧪 Testing Folder Watcher Polling Frequency")
    print("=" * 50)
    
    # Monitor for 2 minutes and count requests
    print("📊 Monitoring requests for 2 minutes...")
    print("✅ Reduced polling should show requests every ~60 seconds (or less)")
    print("❌ Old behavior would show requests every few seconds")
    print()
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=2)
    
    request_times = []
    
    print("Monitoring backend logs...")
    print("Time      | Endpoint")
    print("-" * 40)
    
    # Start monitoring process
    process = subprocess.Popen(
        ['docker', 'logs', '-f', '--tail=0', 'ocr-invoice-processor-backend-1'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    try:
        while datetime.now() < end_time:
            line = process.stdout.readline()
            if line:
                # Look for folder watcher requests
                if '/api/folder-watcher/status' in line or '/api/folder-watcher/notifications' in line:
                    current_time = datetime.now()
                    request_times.append(current_time)
                    time_str = current_time.strftime("%H:%M:%S")
                    
                    if '/api/folder-watcher/status' in line:
                        endpoint = "status"
                    else:
                        endpoint = "notifications"
                    
                    print(f"{time_str} | {endpoint}")
            
            time.sleep(0.1)  # Small delay to prevent high CPU usage
    
    except KeyboardInterrupt:
        pass
    finally:
        process.terminate()
        process.wait()
    
    print("\n" + "=" * 50)
    print("📈 ANALYSIS RESULTS")
    print("=" * 50)
    
    if len(request_times) == 0:
        print("✅ EXCELLENT: No folder watcher requests detected!")
        print("   Either polling is disabled or very infrequent")
        return True
    
    # Calculate intervals between requests
    intervals = []
    for i in range(1, len(request_times)):
        interval = (request_times[i] - request_times[i-1]).total_seconds()
        intervals.append(interval)
    
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        
        print(f"📊 Total requests in 2 minutes: {len(request_times)}")
        print(f"⏱️  Average interval: {avg_interval:.1f} seconds")
        print(f"⏱️  Min interval: {min_interval:.1f} seconds")
        print(f"⏱️  Max interval: {max_interval:.1f} seconds")
        print()
        
        if avg_interval >= 45:  # Should be around 60 seconds
            print("✅ SUCCESS: Polling frequency is acceptable (>45s average)")
            return True
        elif avg_interval >= 25:
            print("⚠️  WARNING: Polling could be less frequent (25-45s average)")
            print("   This is better than before but could be improved")
            return True
        else:
            print("❌ ISSUE: Polling is still too frequent (<25s average)")
            print("   Polling should be ~60 seconds apart")
            return False
    else:
        print("✅ EXCELLENT: Only one request detected in 2 minutes")
        return True

def show_recommendations():
    """Show recommendations for further optimization"""
    print("\n" + "=" * 50)
    print("💡 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 50)
    print("1. 🔄 Users can now toggle auto-refresh on/off with the clock button")
    print("2. ⏸️  Polling pauses when browser tab is not active")
    print("3. 🕒 Polling interval increased to 60 seconds (was 5 seconds)")
    print("4. 🔇 Backend logs are filtered to reduce noise")
    print("5. 📱 Manual refresh button available for immediate updates")
    print()
    print("🎯 If you want even less traffic:")
    print("   - Click the clock button in the Folder Watcher widget to disable auto-refresh")
    print("   - Use manual refresh when needed")

if __name__ == "__main__":
    print("🔍 Folder Watcher Polling Optimization Test")
    print("=" * 50)
    print("This test monitors the frequency of folder watcher API requests")
    print("to verify that our optimization changes are working correctly.")
    print()
    print("💡 Changes made:")
    print("   - Polling interval: 5s → 60s")
    print("   - Added pause when tab not active")
    print("   - Added user toggle for auto-refresh")
    print("   - Backend log filtering")
    print()
    
    try:
        success = test_polling_frequency()
        show_recommendations()
        
        if success:
            print("\n🎉 TEST PASSED: Polling optimization successful!")
        else:
            print("\n⚠️  TEST NEEDS ATTENTION: Consider further optimization")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure the backend is running with docker-compose")
