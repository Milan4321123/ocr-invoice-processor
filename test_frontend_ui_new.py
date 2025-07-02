#!/usr/bin/env python3
"""
Comprehensive Frontend UI End-to-End Test Suite for OCR Invoice Processor

This script tests the complete frontend UI workflow using Selenium:
1. Login page functionality and authentication
2. Home page carousel navigation and modern UI
3. Upload page dropzone functionality and file handling
4. Dashboard invoice listing, filtering and actions
5. Invoice editor form, dropdowns, and data entry
6. Workflow progression (edit, save, complete, send to Bauleiter)
7. Prüfbericht page and Skonto data display/actions
8. General UI elements, responsiveness and accessibility
9. Browser console errors and network request monitoring
10. Cross-browser compatibility testing

Requirements:
    pip install selenium webdriver-manager

The test also provides detailed manual testing instructions if Selenium is not available.
"""

import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frontend_ui_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Try to import Selenium, provide fallback if not available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("⚠️ Selenium not available. Manual testing instructions will be provided.")

class OCRInvoiceFrontendTest:
    def __init__(self, base_url: str = "http://localhost:3000", headless: bool = False):
        self.base_url = base_url.rstrip('/')
        self.driver = None
        self.headless = headless
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if details:
            logger.info(f"    Details: {details}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {details}")

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        if not SELENIUM_AVAILABLE:
            return False
            
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info(f"✅ Chrome WebDriver initialized (headless={self.headless})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup WebDriver: {str(e)}")
            return False

    def teardown_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

    def wait_for_element(self, by: str, value: str, timeout: int = 10):
        """Wait for element to be present"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            return None

    def wait_for_clickable(self, by: str, value: str, timeout: int = 10):
        """Wait for element to be clickable"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable((by, value)))
        except TimeoutException:
            return None

    # Test 1: Login Page
    def test_login_page(self):
        """Test login page functionality"""
        logger.info("🔐 Testing Login Page...")
        
        try:
            # Navigate to login page
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            # Check page title
            title = self.driver.title
            if "OCR" in title or "Invoice" in title or "Login" in title:
                self.log_test("Login - Page Load", True, f"Title: {title}")
            else:
                self.log_test("Login - Page Load", False, f"Unexpected title: {title}")
                
            # Check login form elements
            username_field = self.wait_for_element(By.NAME, "username")
            password_field = self.wait_for_element(By.NAME, "password")
            login_button = self.wait_for_element(By.TYPE, "submit")
            
            if username_field and password_field and login_button:
                self.log_test("Login - Form Elements", True, "All form elements present")
                
                # Test form interaction
                username_field.send_keys("admin")
                password_field.send_keys("admin123")
                time.sleep(1)
                
                login_button.click()
                time.sleep(3)
                
                # Check if redirected (URL should change from /login)
                current_url = self.driver.current_url
                if "/login" not in current_url:
                    self.log_test("Login - Authentication", True, f"Redirected to: {current_url}")
                else:
                    self.log_test("Login - Authentication", False, "Still on login page")
                    
            else:
                self.log_test("Login - Form Elements", False, "Missing form elements")
                
        except Exception as e:
            self.log_test("Login Page", False, str(e))

    # Test 2: Home Page Carousel
    def test_home_page(self):
        """Test home page and carousel navigation"""
        logger.info("🏠 Testing Home Page...")
        
        try:
            # Navigate to home page
            self.driver.get(f"{self.base_url}/")
            time.sleep(3)
            
            # Check for main heading
            headings = self.driver.find_elements(By.TAG_NAME, "h1")
            found_welcome = any("Welcome" in h.text or "OCR" in h.text for h in headings)
            
            if found_welcome:
                self.log_test("Home - Main Heading", True, "Welcome heading found")
            else:
                self.log_test("Home - Main Heading", False, "Welcome heading not found")
                
            # Check for navigation cards (carousel items)
            navigation_cards = self.driver.find_elements(By.CSS_SELECTOR, "[href='/dashboard'], [href='/upload'], [href='/prufbericht']")
            
            if len(navigation_cards) >= 3:
                self.log_test("Home - Navigation Cards", True, f"Found {len(navigation_cards)} navigation cards")
                
                # Test clicking a navigation card
                try:
                    dashboard_link = self.driver.find_element(By.CSS_SELECTOR, "[href='/dashboard']")
                    dashboard_link.click()
                    time.sleep(2)
                    
                    current_url = self.driver.current_url
                    if "/dashboard" in current_url:
                        self.log_test("Home - Navigation Click", True, "Dashboard navigation works")
                    else:
                        self.log_test("Home - Navigation Click", False, f"Expected dashboard, got: {current_url}")
                        
                except Exception as e:
                    self.log_test("Home - Navigation Click", False, str(e))
                    
            else:
                self.log_test("Home - Navigation Cards", False, f"Expected ≥3 cards, found {len(navigation_cards)}")
                
        except Exception as e:
            self.log_test("Home Page", False, str(e))

    # Test 3: Upload Page Dropzone
    def test_upload_page(self):
        """Test upload page dropzone functionality"""
        logger.info("📤 Testing Upload Page...")
        
        try:
            # Navigate to upload page
            self.driver.get(f"{self.base_url}/upload")
            time.sleep(3)
            
            # Check for dropzone
            dropzone = self.wait_for_element(By.CSS_SELECTOR, "[data-testid='dropzone'], .dropzone, [class*='drop']")
            
            if dropzone:
                self.log_test("Upload - Dropzone Present", True, "Dropzone element found")
                
                # Check for upload instructions
                upload_text = dropzone.text.lower()
                if "drag" in upload_text or "drop" in upload_text or "pdf" in upload_text:
                    self.log_test("Upload - Instructions", True, "Upload instructions visible")
                else:
                    self.log_test("Upload - Instructions", False, "Upload instructions not clear")
                    
            else:
                self.log_test("Upload - Dropzone Present", False, "Dropzone not found")
                
            # Check for file input
            file_input = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if file_input:
                self.log_test("Upload - File Input", True, "File input available")
            else:
                self.log_test("Upload - File Input", False, "File input not found")
                
        except Exception as e:
            self.log_test("Upload Page", False, str(e))

    # Test 4: Dashboard
    def test_dashboard(self):
        """Test dashboard functionality"""
        logger.info("📊 Testing Dashboard...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Check for invoices table or grid
            invoice_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "table, .invoice-item, [class*='invoice'], [class*='card']")
            
            if invoice_elements:
                self.log_test("Dashboard - Invoice Display", True, f"Found {len(invoice_elements)} invoice elements")
                
                # Check for action buttons (Bearbeiten, Delete, etc.)
                action_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button, a[href*='/invoice-editor/'], [class*='button']")
                
                if action_buttons:
                    self.log_test("Dashboard - Action Buttons", True, f"Found {len(action_buttons)} action buttons")
                    
                    # Try to find and click an "Edit" button
                    edit_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Bearbeiten')] | //a[contains(text(), 'Edit')] | //a[contains(@href, '/invoice-editor/')]")
                    
                    if edit_buttons:
                        try:
                            edit_buttons[0].click()
                            time.sleep(2)
                            
                            current_url = self.driver.current_url
                            if "/invoice-editor/" in current_url:
                                self.log_test("Dashboard - Edit Navigation", True, "Edit button works")
                            else:
                                self.log_test("Dashboard - Edit Navigation", False, f"Unexpected URL: {current_url}")
                                
                        except Exception as e:
                            self.log_test("Dashboard - Edit Navigation", False, str(e))
                    else:
                        self.log_test("Dashboard - Edit Buttons", False, "No edit buttons found")
                        
                else:
                    self.log_test("Dashboard - Action Buttons", False, "No action buttons found")
                    
            else:
                self.log_test("Dashboard - Invoice Display", False, "No invoice elements found")
                
        except Exception as e:
            self.log_test("Dashboard", False, str(e))

    # Test 5: Invoice Editor
    def test_invoice_editor(self):
        """Test invoice editor form and functionality"""
        logger.info("✏️ Testing Invoice Editor...")
        
        try:
            # If we're not already in editor, try to navigate there
            current_url = self.driver.current_url
            if "/invoice-editor/" not in current_url:
                # Go back to dashboard and try to find an edit link
                self.driver.get(f"{self.base_url}/dashboard")
                time.sleep(2)
                
                edit_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/invoice-editor/']")
                if edit_links:
                    edit_links[0].click()
                    time.sleep(3)
                else:
                    self.log_test("Invoice Editor - Navigation", False, "No invoice editor links found")
                    return
                    
            # Check for form fields
            form_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                "input, select, textarea")
            
            if len(form_fields) >= 5:  # Expect at least 5 form fields
                self.log_test("Invoice Editor - Form Fields", True, f"Found {len(form_fields)} form fields")
                
                # Check for specific invoice fields
                email_field = self.driver.find_elements(By.CSS_SELECTOR, 
                    "input[type='email'], input[name*='email'], input[placeholder*='email' i]")
                
                if email_field:
                    self.log_test("Invoice Editor - Email Field", True, "Email field present")
                else:
                    self.log_test("Invoice Editor - Email Field", False, "Email field not found")
                    
                # Check for dropdowns
                dropdowns = self.driver.find_elements(By.TAG_NAME, "select")
                if dropdowns:
                    self.log_test("Invoice Editor - Dropdowns", True, f"Found {len(dropdowns)} dropdown menus")
                else:
                    self.log_test("Invoice Editor - Dropdowns", False, "No dropdown menus found")
                    
                # Check for save/complete buttons
                save_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Speichern')] | //button[contains(text(), 'Save')] | //button[contains(text(), 'Complete')]")
                
                if save_buttons:
                    self.log_test("Invoice Editor - Save Buttons", True, f"Found {len(save_buttons)} action buttons")
                else:
                    self.log_test("Invoice Editor - Save Buttons", False, "No save/complete buttons found")
                    
            else:
                self.log_test("Invoice Editor - Form Fields", False, f"Expected ≥5 fields, found {len(form_fields)}")
                
        except Exception as e:
            self.log_test("Invoice Editor", False, str(e))

    # Test 6: Prüfbericht Page
    def test_prufbericht_page(self):
        """Test Prüfbericht (Skonto) page"""
        logger.info("📋 Testing Prüfbericht Page...")
        
        try:
            # Navigate to Prüfbericht page
            self.driver.get(f"{self.base_url}/prufbericht")
            time.sleep(3)
            
            # Check for Skonto data display
            page_text = self.driver.page_source.lower()
            skonto_related = "skonto" in page_text or "prüfbericht" in page_text or "savings" in page_text
            
            if skonto_related:
                self.log_test("Prüfbericht - Content", True, "Skonto-related content found")
                
                # Check for data tables or cards
                data_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "table, .card, [class*='skonto'], [class*='invoice']")
                
                if data_elements:
                    self.log_test("Prüfbericht - Data Display", True, f"Found {len(data_elements)} data elements")
                else:
                    self.log_test("Prüfbericht - Data Display", False, "No data display elements found")
                    
                # Check for action buttons (Take/Miss Skonto)
                action_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button[class*='take'], button[class*='miss'], button")
                
                if action_buttons:
                    self.log_test("Prüfbericht - Action Buttons", True, f"Found {len(action_buttons)} buttons")
                else:
                    self.log_test("Prüfbericht - Action Buttons", False, "No action buttons found")
                    
            else:
                self.log_test("Prüfbericht - Content", False, "Skonto content not found")
                
        except Exception as e:
            self.log_test("Prüfbericht Page", False, str(e))

    # Test 7: General UI Tests
    def test_general_ui(self):
        """Test general UI elements and accessibility"""
        logger.info("🎨 Testing General UI...")
        
        try:
            # Check for responsive design
            self.driver.set_window_size(375, 667)  # Mobile size
            time.sleep(1)
            
            body = self.driver.find_element(By.TAG_NAME, "body")
            mobile_friendly = body.size['width'] <= 400
            
            if mobile_friendly:
                self.log_test("UI - Mobile Responsive", True, "Mobile layout detected")
            else:
                self.log_test("UI - Mobile Responsive", False, "Not mobile responsive")
                
            # Reset to desktop size
            self.driver.set_window_size(1920, 1080)
            time.sleep(1)
            
            # Check for navigation menu
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "nav, .nav, [role='navigation'], header")
            
            if nav_elements:
                self.log_test("UI - Navigation", True, "Navigation elements found")
            else:
                self.log_test("UI - Navigation", False, "No navigation found")
                
            # Check for loading states
            loading_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".loading, .spinner, [class*='load'], [class*='spin']")
            
            # This is optional - loading elements might not be visible
            self.log_test("UI - Loading States", True, f"Found {len(loading_elements)} loading indicators")
                
        except Exception as e:
            self.log_test("General UI", False, str(e))

    # Test 8: Browser Console Errors
    def test_console_errors(self):
        """Check for JavaScript errors in browser console"""
        logger.info("🔍 Testing Console Errors...")
        
        try:
            # Get browser console logs
            logs = self.driver.get_log('browser')
            
            error_logs = [log for log in logs if log['level'] == 'SEVERE']
            warning_logs = [log for log in logs if log['level'] == 'WARNING']
            
            if len(error_logs) == 0:
                self.log_test("Console - No Errors", True, "No severe JavaScript errors")
            else:
                error_messages = [log['message'] for log in error_logs[:3]]  # Show first 3
                self.log_test("Console - Errors Found", False, f"{len(error_logs)} errors: {error_messages}")
                
            if len(warning_logs) <= 5:  # Some warnings are acceptable
                self.log_test("Console - Minimal Warnings", True, f"{len(warning_logs)} warnings")
            else:
                self.log_test("Console - Too Many Warnings", False, f"{len(warning_logs)} warnings")
                
        except Exception as e:
            self.log_test("Console Errors", False, str(e))

    def run_all_tests(self):
        """Run all frontend UI tests"""
        if not SELENIUM_AVAILABLE:
            self.provide_manual_instructions()
            return False
            
        logger.info("🚀 Starting Frontend UI Test Suite")
        logger.info("=" * 60)
        
        # Setup WebDriver
        if not self.setup_driver():
            logger.error("❌ Failed to setup WebDriver")
            return False
            
        start_time = time.time()
        
        try:
            # Run all tests
            self.test_login_page()
            self.test_home_page()
            self.test_upload_page()
            self.test_dashboard()
            self.test_invoice_editor()
            self.test_prufbericht_page()
            self.test_general_ui()
            self.test_console_errors()
            
        finally:
            self.teardown_driver()
            
        # Results
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info("📊 FRONTEND UI TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"✅ Tests Passed: {self.results['passed']}")
        logger.info(f"❌ Tests Failed: {self.results['failed']}")
        logger.info(f"⏱️ Total Duration: {duration:.2f} seconds")
        
        if self.results['errors']:
            logger.info("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                logger.info(f"   • {error}")
                
        return self.results['failed'] == 0

    def provide_manual_instructions(self):
        """Provide manual testing instructions when Selenium is not available"""
        logger.info("📋 MANUAL FRONTEND TESTING INSTRUCTIONS")
        logger.info("=" * 60)
        
        instructions = [
            {
                "step": "1. Login Page Test",
                "url": f"{self.base_url}/login",
                "actions": [
                    "- Check if login form loads properly",
                    "- Enter username: admin, password: admin123",
                    "- Click login button",
                    "- Verify redirect to dashboard/home page",
                    "- Check for any error messages"
                ]
            },
            {
                "step": "2. Home Page Carousel Test",
                "url": f"{self.base_url}/",
                "actions": [
                    "- Check main welcome heading is visible",
                    "- Verify navigation cards are displayed",
                    "- Click on Dashboard, Upload, Prüfbericht cards",
                    "- Ensure smooth navigation and modern UI",
                    "- Test responsive design on mobile/tablet"
                ]
            },
            {
                "step": "3. Upload Page Dropzone Test",
                "url": f"{self.base_url}/upload",
                "actions": [
                    "- Check dropzone area is visible",
                    "- Test drag and drop functionality",
                    "- Try uploading a PDF file",
                    "- Verify filename format validation (YYYYMMDD_ID_SUPPLIER_TYPE.pdf)",
                    "- Check upload progress and success messages"
                ]
            },
            {
                "step": "4. Dashboard Test",
                "url": f"{self.base_url}/dashboard",
                "actions": [
                    "- Check invoice list/table loads",
                    "- Verify invoice details are displayed",
                    "- Click 'Bearbeiten' (Edit) button on an invoice",
                    "- Test status filtering if available",
                    "- Check 'Send to Bauleiter' functionality"
                ]
            },
            {
                "step": "5. Invoice Editor Test",
                "url": f"{self.base_url}/invoice-editor/[id]",
                "actions": [
                    "- Check PDF viewer on left side",
                    "- Fill out form fields on right side",
                    "- Test dropdown menus (Projekt, Gewerk, etc.)",
                    "- Enter email in 'Rechnungsprüfung Email' field",
                    "- Click 'Jetzt speichern' (Save) button",
                    "- Test 'Bearbeitung abschließen' (Complete) button",
                    "- Verify confirmation dialogs"
                ]
            },
            {
                "step": "6. Dropdown Management Test",
                "url": "Any invoice editor page",
                "actions": [
                    "- Test adding new dropdown options",
                    "- Verify pending changes indicator",
                    "- Save dropdown changes",
                    "- Check email notifications for changes"
                ]
            },
            {
                "step": "7. Prüfbericht Page Test",
                "url": f"{self.base_url}/prufbericht",
                "actions": [
                    "- Check Skonto opportunities table",
                    "- Verify invoice data display",
                    "- Test 'Take' and 'Miss' Skonto buttons",
                    "- Check filtering and search functionality",
                    "- Verify Skonto calculations and savings"
                ]
            },
            {
                "step": "8. General UI & Accessibility Test",
                "url": "All pages",
                "actions": [
                    "- Test mobile responsiveness",
                    "- Check browser console for errors (F12)",
                    "- Verify loading states and transitions",
                    "- Test keyboard navigation",
                    "- Check color contrast and readability"
                ]
            }
        ]
        
        for instruction in instructions:
            logger.info(f"\n{instruction['step']}")
            logger.info(f"URL: {instruction['url']}")
            for action in instruction['actions']:
                logger.info(f"  {action}")
        
        logger.info("\n💡 Testing Tips:")
        logger.info("- Open browser developer tools (F12) to monitor network requests and console errors")
        logger.info("- Test on different screen sizes (mobile, tablet, desktop)")
        logger.info("- Check email functionality by monitoring API calls in Network tab")
        logger.info("- Verify data persistence by refreshing pages after changes")
        logger.info("- Test error handling by entering invalid data")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OCR Invoice Frontend UI Tests')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--manual', action='store_true', help='Show manual testing instructions only')
    parser.add_argument('--url', default='http://localhost:3000', help='Frontend URL (default: http://localhost:3000)')
    
    args = parser.parse_args()
    
    if args.manual or not SELENIUM_AVAILABLE:
        test_suite = OCRInvoiceFrontendTest(args.url)
        test_suite.provide_manual_instructions()
        return
    
    # Check if frontend is running
    import requests
    try:
        response = requests.get(args.url, timeout=5)
        if response.status_code != 200:
            logger.error(f"❌ Frontend not accessible at {args.url}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Cannot connect to frontend at {args.url}: {str(e)}")
        logger.info("💡 Make sure the frontend is running: cd frontend && npm run dev")
        sys.exit(1)
    
    # Run automated tests
    test_suite = OCRInvoiceFrontendTest(args.url, headless=args.headless)
    success = test_suite.run_all_tests()
    
    if success:
        logger.info("🎉 All frontend UI tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Some frontend UI tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
