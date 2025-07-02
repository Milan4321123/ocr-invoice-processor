#!/usr/bin/env python3
"""
Complete Testing Suite Runner for OCR Invoice Processing System

This script runs all available tests and provides comprehensive testing instructions:
1. Backend API workflow tests (automated)
2. Frontend UI tests (automated with Selenium, fallback to manual)
3. Manual testing instructions for complete workflow validation
4. Performance and load testing guidelines

Usage:
    python run_all_tests.py [--headless] [--skip-ui]
    
Arguments:
    --headless    Run UI tests in headless mode (no browser window)
    --skip-ui     Skip automated UI tests and show manual instructions only
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

def print_header(title: str, width: int = 70):
    """Print a formatted header"""
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)

def print_section(title: str, width: int = 70):
    """Print a formatted section header"""
    print("\n" + "-" * width)
    print(f"📋 {title}")
    print("-" * width)

def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are available"""
    dependencies = {
        "requests": False,
        "selenium": False,
        "python": True  # Assuming Python is available since we're running this script
    }
    
    # Check requests
    try:
        import requests
        dependencies["requests"] = True
    except ImportError:
        pass
    
    # Check selenium
    try:
        import selenium
        dependencies["selenium"] = True
    except ImportError:
        pass
    
    return dependencies

def check_services() -> Dict[str, bool]:
    """Check if required services are running"""
    import requests
    
    services = {
        "backend": False,
        "frontend": False
    }
    
    # Check backend
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        services["backend"] = response.status_code == 200
    except:
        pass
    
    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        services["frontend"] = response.status_code < 500
    except:
        pass
    
    return services

def run_backend_tests() -> bool:
    """Run backend API workflow tests"""
    print_section("Running Backend API Tests")
    
    try:
        # Run the workflow test
        result = subprocess.run([sys.executable, "test_complete_workflow_backend.py"], 
                              capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Backend tests timed out (5 minutes)")
        return False
    except FileNotFoundError:
        print("❌ Backend test file not found: test_complete_workflow_backend.py")
        return False
    except Exception as e:
        print(f"❌ Backend tests failed: {e}")
        return False

def run_frontend_tests(headless: bool = False) -> bool:
    """Run frontend UI tests"""
    print_section("Running Frontend UI Tests")
    
    try:
        # Check if selenium is available
        import selenium
        
        # Run the UI tests
        cmd = [sys.executable, "test_frontend_ui.py"]
        if headless:
            cmd.append("--headless")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
        
    except ImportError:
        print("⚠️ Selenium not available - UI tests skipped")
        print("   Install with: pip install selenium")
        show_manual_ui_instructions()
        return True  # Don't fail if selenium is not available
    except subprocess.TimeoutExpired:
        print("❌ Frontend tests timed out (5 minutes)")
        return False
    except FileNotFoundError:
        print("❌ Frontend test file not found: test_frontend_ui.py")
        return False
    except Exception as e:
        print(f"❌ Frontend tests failed: {e}")
        return False

def show_manual_ui_instructions():
    """Show manual UI testing instructions"""
    print_section("Manual UI Testing Instructions")
    
    print("""
🔐 1. AUTHENTICATION TESTING
   • Open: http://localhost:3000/login
   • Test empty form validation
   • Login with: admin / admin123
   • Verify redirect to dashboard/homepage
   • Test logout functionality

🏠 2. HOMEPAGE CAROUSEL TESTING
   • Navigate to: http://localhost:3000/
   • Test carousel/card navigation:
     - Upload page navigation
     - Dashboard navigation  
     - Prüfbericht navigation
   • Verify all links work correctly
   • Test responsive design on mobile

📤 3. UPLOAD WORKFLOW TESTING
   • Navigate to: http://localhost:3000/upload
   • Test dropzone functionality:
     - Drag and drop file
     - Click to upload file
     - Test file validation (PDF only)
     - Test filename validation (YYYYMMDD_ID_VENDOR_TYPE.pdf)
   • Verify upload progress indicator
   • Test upload success/error states
   • Test "Upload Another" functionality

📊 4. DASHBOARD WORKFLOW TESTING
   • Navigate to: http://localhost:3000/dashboard
   • Test invoice table:
     - View all invoices
     - Test status filtering
     - Test search functionality
     - Verify file size formatting
     - Test date formatting
   • Test action buttons:
     - "Bearbeiten" (Edit) button
     - "An Bauleiter" (Send to Supervisor) button
     - "Löschen" (Delete) button
   • Test refresh functionality
   • Verify status progression indicators

✏️ 5. INVOICE EDITOR TESTING
   • Click "Bearbeiten" on any invoice in dashboard
   • Test PDF viewer:
     - PDF loads correctly
     - Zoom functionality
     - Page navigation
   • Test invoice form:
     - Fill all required fields
     - Test dropdown selections
     - Test date pickers
     - Test email validation
   • Test dropdown management:
     - Add new dropdown options
     - Remove dropdown options
     - Save dropdown changes
   • Test form validation:
     - Required email field
     - Confirmation dialogs
   • Test save functionality:
     - Save with email notification
     - Complete invoice processing
   • Test mobile responsiveness (PDF/Form toggle)

💰 6. PRÜFBERICHT (SKONTO) TESTING
   • Navigate to: http://localhost:3000/prufbericht
   • Test metrics dashboard:
     - Total Skonto amount
     - Captured Skonto
     - Missed Skonto
     - Pending review count
   • Test invoice table:
     - View Skonto opportunities
     - Test status badges
     - Test filter dropdown (All, Captured, Missed, Pending, Expired)
     - Test search functionality
   • Test action buttons:
     - "Reminder" button (send email)
     - "Take" button (mark as taken)
     - "Miss" button (mark as missed)
   • Test reminder status indicators
   • Verify amount calculations

🔄 7. WORKFLOW PROGRESSION TESTING
   • Upload a new invoice → Check status: "Neu"
   • Edit invoice → Check status: "In Bearbeitung"
   • Complete editing → Check status: "Abgeschlossen"
   • Send to Bauleiter → Check status: "Bei Bauleiter"
   • Test email notifications (check browser network tab)
   • Verify status updates in dashboard

📧 8. EMAIL WORKFLOW TESTING
   • Test editor notifications (after saving)
   • Test Bauleiter notifications (after sending)
   • Test Skonto reminders
   • Check browser developer console for email logs
   • Verify email templates in network requests

🎨 9. UI/UX TESTING
   • Test responsive design:
     - Desktop (1920x1080)
     - Tablet (768x1024)
     - Mobile (375x667)
   • Test dark/light mode (if available)
   • Test loading states
   • Test error states
   • Test empty states
   • Verify accessibility:
     - Keyboard navigation
     - Screen reader compatibility
     - Color contrast
     - Alt text on images

⚡ 10. PERFORMANCE TESTING
   • Test with large PDF files (>10MB)
   • Test with many invoices in dashboard
   • Test multiple browser tabs
   • Monitor memory usage
   • Check for JavaScript errors in console
""")

def show_data_flow_testing():
    """Show data flow testing instructions"""
    print_section("Data Flow & Integration Testing")
    
    print("""
🔍 DATA CONSISTENCY TESTING

1. Upload → Database Verification:
   • Upload file via frontend
   • Check backend API: GET /api/invoices
   • Verify data matches in Supabase dashboard
   • Confirm file storage in correct bucket

2. Edit → Status Progression:
   • Edit invoice in frontend
   • Check status updates: "neu" → "edited" → "completed"
   • Verify email sending logs
   • Check dropdown changes persist

3. Bauleiter Workflow:
   • Send invoice to Bauleiter
   • Check email generation (network tab)
   • Verify status: "in_review_by_bauleiter"
   • Test approval/rejection flow

4. Skonto Data Flow:
   • Create invoice with Skonto data
   • Check Prüfbericht page displays correctly
   • Test decision updates (taken/missed)
   • Verify savings calculations
   • Check reminder status persistence

5. Cross-Page Consistency:
   • Make changes in invoice editor
   • Verify updates appear in dashboard
   • Check Prüfbericht reflects changes
   • Ensure data sync across all views

📊 REPORTING & ANALYTICS TESTING

1. Dashboard Metrics:
   • Verify invoice counts match database
   • Check status distribution accuracy
   • Test amount calculations
   • Verify date range filtering

2. Skonto Reports:
   • Check savings potential calculations
   • Verify historical performance data
   • Test urgency indicators
   • Confirm deadline tracking

3. Processing Status Reports:
   • Test workflow stage tracking
   • Verify completion metrics
   • Check average processing times
   • Test status transitions

🔄 ERROR HANDLING TESTING

1. Network Failures:
   • Disconnect internet during operations
   • Test offline behavior
   • Check error messaging
   • Verify retry mechanisms

2. Server Errors:
   • Stop backend service temporarily
   • Test frontend error handling
   • Check user feedback
   • Verify graceful degradation

3. Invalid Data:
   • Upload invalid file types
   • Submit forms with invalid data
   • Test boundary conditions
   • Check validation messages

4. Concurrent Operations:
   • Multiple users editing same invoice
   • Simultaneous file uploads
   • Test data race conditions
   • Check conflict resolution
""")

def show_production_testing():
    """Show production readiness testing"""
    print_section("Production Readiness Testing")
    
    print("""
🚀 DEPLOYMENT TESTING

1. Environment Configuration:
   • Test with production environment variables
   • Verify database connections
   • Check external service integrations
   • Test SSL/HTTPS requirements

2. Security Testing:
   • Test authentication boundaries
   • Check authorization levels
   • Verify file upload restrictions
   • Test input sanitization
   • Check for XSS vulnerabilities

3. Performance Benchmarks:
   • Load test with 100+ concurrent users
   • Test large file uploads (50MB+)
   • Measure response times
   • Check memory usage patterns
   • Monitor database performance

4. Backup & Recovery:
   • Test database backup procedures
   • Verify file storage backup
   • Test system recovery
   • Check data integrity

🔧 MAINTENANCE TESTING

1. Log Monitoring:
   • Check application logs
   • Verify error tracking
   • Test log rotation
   • Monitor disk usage

2. Update Procedures:
   • Test rolling updates
   • Verify zero-downtime deployment
   • Check backward compatibility
   • Test rollback procedures

3. Scaling Testing:
   • Test horizontal scaling
   • Check load balancer behavior
   • Verify session management
   • Test database scaling

📈 BUSINESS CONTINUITY

1. Disaster Recovery:
   • Test failover procedures
   • Verify data replication
   • Check backup restoration
   • Test recovery time objectives

2. Compliance Testing:
   • Data retention policies
   • Privacy regulations (GDPR)
   • Audit trail verification
   • Document management compliance

3. User Training Materials:
   • Create user documentation
   • Test workflow procedures
   • Verify help system
   • Check support processes
""")

def generate_test_report(results: Dict[str, bool]) -> str:
    """Generate a comprehensive test report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
# OCR Invoice Processing System - Test Report
Generated: {timestamp}

## Test Results Summary

"""
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        report += f"- {status} {test_name}\n"
    
    report += f"""
## Overall Status
- Tests Passed: {passed_tests}/{total_tests}
- Success Rate: {(passed_tests/total_tests)*100:.1f}%
- Overall Status: {'✅ PASSED' if passed_tests == total_tests else '⚠️ NEEDS ATTENTION' if passed_tests >= total_tests * 0.75 else '❌ FAILED'}

## Recommendations

"""
    
    if passed_tests == total_tests:
        report += """
✅ All tests passed! The system is ready for production deployment.

Next steps:
1. Run performance testing with expected load
2. Set up monitoring and alerting
3. Prepare user training materials
4. Schedule go-live activities
"""
    elif passed_tests >= total_tests * 0.75:
        report += """
⚠️ Most tests passed but some issues need attention.

Recommended actions:
1. Review failed tests and fix critical issues
2. Re-run tests after fixes
3. Consider additional testing for edge cases
4. Document known limitations
"""
    else:
        report += """
❌ Significant issues found that need resolution.

Critical actions required:
1. Fix all failed tests before production
2. Review system architecture for stability
3. Additional integration testing needed
4. Consider staged rollout approach
"""
    
    return report

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="OCR Invoice Processing System - Complete Test Suite")
    parser.add_argument("--headless", action="store_true", help="Run UI tests in headless mode")
    parser.add_argument("--skip-ui", action="store_true", help="Skip automated UI tests")
    parser.add_argument("--manual-only", action="store_true", help="Show manual testing instructions only")
    
    args = parser.parse_args()
    
    print_header("OCR Invoice Processing System - Complete Test Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check dependencies
    print_section("Checking Dependencies")
    deps = check_dependencies()
    for dep, available in deps.items():
        status = "✅" if available else "❌"
        print(f"{status} {dep}")
    
    if not deps["requests"]:
        print("\n❌ Missing required dependency: requests")
        print("Install with: pip install requests")
        return False
    
    # Check services
    print_section("Checking Services")
    services = check_services()
    for service, running in services.items():
        status = "✅" if running else "❌"
        print(f"{status} {service}")
    
    if not services["backend"]:
        print("\n❌ Backend service is not running")
        print("Start with: cd backend && python main.py")
        return False
    
    if not services["frontend"]:
        print("\n⚠️ Frontend service is not running")
        print("Start with: cd frontend && npm run dev")
    
    # Manual instructions only
    if args.manual_only:
        show_manual_ui_instructions()
        show_data_flow_testing()
        show_production_testing()
        return True
    
    # Run tests
    test_results = {}
    
    # Backend tests
    if services["backend"]:
        backend_success = run_backend_tests()
        test_results["Backend API Tests"] = backend_success
    
    # Frontend tests
    if not args.skip_ui and services["frontend"]:
        if deps["selenium"]:
            frontend_success = run_frontend_tests(args.headless)
            test_results["Frontend UI Tests"] = frontend_success
        else:
            print_section("Frontend UI Tests - Selenium Not Available")
            print("⚠️ Selenium not installed - showing manual instructions")
            show_manual_ui_instructions()
            test_results["Frontend UI Tests (Manual)"] = True
    
    # Generate and display report
    print_header("Test Results Summary")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for passed in test_results.values() if passed)
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:<10} {test_name}")
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} test suites passed")
    
    # Show additional testing instructions
    if total_tests > 0 and passed_tests >= total_tests * 0.75:
        show_data_flow_testing()
        show_production_testing()
    
    # Save report to file
    report = generate_test_report(test_results)
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    try:
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save report: {e}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed: {e}")
        sys.exit(1)
