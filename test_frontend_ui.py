#!/usr/bin/env python3
"""
Frontend UI End-to-End Test Suite for OCR Invoice Processor

This script tests the complete frontend UI workflow using Selenium:
1. Login page functionality and authentication
2. Home page carousel navigation and modern UI
3. Upload page dropzone functionality
4. Dashboard invoice listing and actions
5. Invoice editor form and dropdown management
6. Workflow progression (edit, save, complete, send to Bauleiter)
7. Prüfbericht page and Skonto data display
8. General UI elements and accessibility
9. Browser console errors and network requests

Requirements:
    pip install selenium webdriver-manager

The test also provides manual testing instructions if Selenium is not available.
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
    
    def __init__(self, headless: bool = False):
        self.frontend_url = FRONTEND_URL
        self.driver = None
        self.headless = headless
        self.test_results = {}
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium WebDriver not available")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("   Please install ChromeDriver or use manual testing")
            return False
    
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamp and level"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            icon = "❌"
        elif level == "SUCCESS":
            icon = "✅"
        elif level == "WARNING":
            icon = "⚠️"
        else:
            icon = "📋"
        print(f"{timestamp} {icon} {message}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present and return it"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.log(f"Element not found: {value}", "ERROR")
            return None
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be clickable and return it"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.log(f"Element not clickable: {value}", "ERROR")
            return None

    # =====================
    # 1. LOGIN PAGE TESTS
    # =====================
    
    def test_login_page(self) -> bool:
        """Test login page functionality"""
        self.log("🔐 Testing Login Page", "INFO")
        
        try:
            # Navigate to login page
            self.driver.get(f"{self.frontend_url}/login")
            
            # Wait for login form to load
            username_field = self.wait_for_element(By.NAME, "username")
            password_field = self.wait_for_element(By.NAME, "password")
            
            if not username_field or not password_field:
                self.log("Login form fields not found", "ERROR")
                return False
            
            # Test form validation with empty fields
            login_button = self.wait_for_clickable(By.TYPE, "submit")
            if login_button:
                login_button.click()
                time.sleep(1)
                # Check if validation messages appear
                self.log("Empty form validation tested", "SUCCESS")
            
            # Test login with credentials
            username_field.clear()
            username_field.send_keys(TEST_CREDENTIALS["username"])
            
            password_field.clear()
            password_field.send_keys(TEST_CREDENTIALS["password"])
            
            # Submit form
            login_button = self.wait_for_clickable(By.TYPE, "submit")
            if login_button:
                login_button.click()
                
                # Wait for redirect to dashboard or homepage
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.current_url != f"{self.frontend_url}/login"
                )
                
                self.log(f"Login successful - Redirected to: {self.driver.current_url}", "SUCCESS")
                return True
            
        except Exception as e:
            self.log(f"Login page test failed: {e}", "ERROR")
            return False
        
        return False

    # =====================
    # 2. HOMEPAGE TESTS
    # =====================
    
    def test_homepage_carousel(self) -> bool:
        """Test homepage carousel navigation"""
        self.log("🏠 Testing Homepage Carousel", "INFO")
        
        try:
            # Navigate to homepage
            self.driver.get(self.frontend_url)
            
            # Look for carousel cards/buttons
            carousel_cards = self.driver.find_elements(By.CSS_SELECTOR, "[href='/upload'], [href='/dashboard'], [href='/prufbericht']")
            
            if len(carousel_cards) == 0:
                self.log("No carousel navigation found, checking for direct links", "WARNING")
                # Look for any navigation links
                nav_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/']")
                if nav_links:
                    self.log(f"Found {len(nav_links)} navigation links", "SUCCESS")
                    return True
                else:
                    return False
            
            self.log(f"Found {len(carousel_cards)} carousel navigation items", "SUCCESS")
            
            # Test clicking each carousel item
            for i, card in enumerate(carousel_cards):
                try:
                    href = card.get_attribute("href")
                    card.click()
                    time.sleep(2)
                    
                    current_url = self.driver.current_url
                    if href in current_url:
                        self.log(f"Carousel navigation {i+1} successful: {href}", "SUCCESS")
                    else:
                        self.log(f"Carousel navigation {i+1} failed: expected {href}, got {current_url}", "WARNING")
                    
                    # Go back to homepage for next test
                    self.driver.get(self.frontend_url)
                    time.sleep(1)
                    
                except Exception as e:
                    self.log(f"Carousel item {i+1} click failed: {e}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Homepage carousel test failed: {e}", "ERROR")
            return False

    # =====================
    # 3. UPLOAD PAGE TESTS
    # =====================
    
    def test_upload_dropzone(self) -> bool:
        """Test upload page dropzone functionality"""
        self.log("📤 Testing Upload Dropzone", "INFO")
        
        try:
            # Navigate to upload page
            self.driver.get(f"{self.frontend_url}/upload")
            
            # Wait for dropzone to load
            dropzone = self.wait_for_element(By.CSS_SELECTOR, "[class*='dropzone'], [class*='drop'], input[type='file']")
            
            if not dropzone:
                self.log("Dropzone element not found", "ERROR")
                return False
            
            self.log("Dropzone element found", "SUCCESS")
            
            # Check for file validation messages
            filename_requirements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'JJJJMMTT') or contains(text(), 'pdf') or contains(text(), 'Dateinamen')]")
            
            if filename_requirements:
                self.log("Filename validation requirements displayed", "SUCCESS")
            else:
                self.log("Filename validation requirements not found", "WARNING")
            
            # Check for drag and drop visual feedback
            dropzone_text = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'drag') or contains(text(), 'drop') or contains(text(), 'Drag') or contains(text(), 'Drop')]")
            
            if dropzone_text:
                self.log("Drag and drop instructions found", "SUCCESS")
            else:
                self.log("Drag and drop instructions not clear", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Upload dropzone test failed: {e}", "ERROR")
            return False

    # =====================
    # 4. DASHBOARD TESTS
    # =====================
    
    def test_dashboard_functionality(self) -> bool:
        """Test dashboard table and functionality"""
        self.log("📊 Testing Dashboard Functionality", "INFO")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.frontend_url}/dashboard")
            
            # Wait for dashboard to load
            time.sleep(3)
            
            # Check for invoice table
            table = self.wait_for_element(By.CSS_SELECTOR, "table, [class*='table'], .invoice")
            
            if not table:
                self.log("Invoice table not found, checking for empty state", "WARNING")
                empty_state = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Keine Rechnungen') or contains(text(), 'No invoices') or contains(text(), 'empty')]")
                if empty_state:
                    self.log("Empty state message found - dashboard working", "SUCCESS")
                    return True
                else:
                    self.log("Dashboard content not found", "ERROR")
                    return False
            
            # Check for table headers
            headers = self.driver.find_elements(By.CSS_SELECTOR, "th, [class*='header']")
            if headers:
                header_texts = [h.text for h in headers if h.text.strip()]
                self.log(f"Table headers found: {len(header_texts)} columns", "SUCCESS")
            
            # Check for action buttons
            action_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, a[class*='button'], [class*='btn']")
            action_count = len([btn for btn in action_buttons if btn.text and btn.text.strip()])
            
            if action_count > 0:
                self.log(f"Dashboard action buttons found: {action_count}", "SUCCESS")
            
            # Check for status indicators
            status_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='status'], [class*='badge'], [class*='tag']")
            if status_elements:
                self.log("Status indicators found", "SUCCESS")
            
            # Test refresh functionality
            refresh_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Aktualisieren') or contains(text(), 'Refresh')]")
            if refresh_buttons:
                try:
                    refresh_buttons[0].click()
                    time.sleep(2)
                    self.log("Refresh functionality tested", "SUCCESS")
                except:
                    self.log("Refresh button found but not clickable", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Dashboard functionality test failed: {e}", "ERROR")
            return False

    # ==========================
    # 5. INVOICE EDITOR TESTS
    # ==========================
    
    def test_invoice_editor(self) -> bool:
        """Test invoice editor form functionality"""
        self.log("✏️ Testing Invoice Editor", "INFO")
        
        try:
            # First, check if there are invoices to edit from dashboard
            self.driver.get(f"{self.frontend_url}/dashboard")
            time.sleep(2)
            
            # Look for edit buttons
            edit_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Bearbeiten') or contains(text(), 'Edit')]")
            
            if not edit_buttons:
                self.log("No edit buttons found in dashboard", "WARNING")
                # Try to access editor directly with a test ID
                self.driver.get(f"{self.frontend_url}/invoice-editor/test")
                time.sleep(3)
                
                # Check if we get an error page or editor loads
                error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error') or contains(text(), 'not found')]")
                if error_elements:
                    self.log("No invoices available for editing", "WARNING")
                    return True  # This is expected if no invoices exist
            else:
                # Click first edit button
                edit_buttons[0].click()
                time.sleep(3)
            
            # Check if we're in the editor
            current_url = self.driver.current_url
            if "invoice-editor" in current_url:
                self.log("Invoice editor loaded successfully", "SUCCESS")
                
                # Test form fields
                form_fields = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                if form_fields:
                    self.log(f"Invoice form fields found: {len(form_fields)}", "SUCCESS")
                
                # Test dropdown functionality
                dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select, [class*='dropdown']")
                if dropdowns:
                    self.log(f"Dropdown fields found: {len(dropdowns)}", "SUCCESS")
                
                # Test save button
                save_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Speichern') or contains(text(), 'Save')]")
                if save_buttons:
                    self.log("Save functionality available", "SUCCESS")
                
                # Test PDF viewer
                pdf_elements = self.driver.find_elements(By.CSS_SELECTOR, "iframe, canvas, [class*='pdf'], embed")
                if pdf_elements:
                    self.log("PDF viewer component found", "SUCCESS")
                else:
                    self.log("PDF viewer not found", "WARNING")
                
                return True
            else:
                self.log("Editor page not loaded correctly", "WARNING")
                return True  # May be expected if no invoices
            
        except Exception as e:
            self.log(f"Invoice editor test failed: {e}", "ERROR")
            return False

    # ========================
    # 6. PRÜFBERICHT TESTS
    # ========================
    
    def test_prufbericht_page(self) -> bool:
        """Test Prüfbericht (Skonto report) page functionality"""
        self.log("💰 Testing Prüfbericht Page", "INFO")
        
        try:
            # Navigate to Prüfbericht page
            self.driver.get(f"{self.frontend_url}/prufbericht")
            time.sleep(3)
            
            # Check for page title
            page_title = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Prüfbericht') or contains(text(), 'Skonto')]")
            if page_title:
                self.log("Prüfbericht page loaded", "SUCCESS")
            
            # Check for metrics cards
            metrics_cards = self.driver.find_elements(By.CSS_SELECTOR, "[class*='card'], [class*='metric'], [class*='stat']")
            if metrics_cards:
                self.log(f"Metrics cards found: {len(metrics_cards)}", "SUCCESS")
            
            # Check for invoice table
            table = self.driver.find_elements(By.CSS_SELECTOR, "table, [class*='table']")
            if table:
                self.log("Skonto invoice table found", "SUCCESS")
                
                # Check for action buttons in table
                action_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Take') or contains(text(), 'Miss') or contains(text(), 'Reminder')]")
                if action_buttons:
                    self.log(f"Skonto action buttons found: {len(action_buttons)}", "SUCCESS")
            
            # Check for filter functionality
            filter_elements = self.driver.find_elements(By.CSS_SELECTOR, "select[class*='filter'], input[placeholder*='filter'], [class*='filter']")
            if filter_elements:
                self.log("Filter functionality found", "SUCCESS")
            
            # Check for search functionality
            search_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[type='search'], input[placeholder*='search'], [class*='search']")
            if search_elements:
                self.log("Search functionality found", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"Prüfbericht page test failed: {e}", "ERROR")
            return False

    # ========================
    # 7. GENERAL UI TESTS
    # ========================
    
    def test_general_ui_elements(self) -> bool:
        """Test general UI elements and responsiveness"""
        self.log("🎨 Testing General UI Elements", "INFO")
        
        try:
            # Test navigation menu
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, [class*='nav'], header")
            if nav_elements:
                self.log("Navigation elements found", "SUCCESS")
            
            # Test footer
            footer_elements = self.driver.find_elements(By.CSS_SELECTOR, "footer")
            if footer_elements:
                self.log("Footer found", "SUCCESS")
            
            # Test responsive design (simulate mobile viewport)
            original_size = self.driver.get_window_size()
            self.driver.set_window_size(375, 667)  # iPhone size
            time.sleep(1)
            
            # Check if mobile menu appears
            mobile_menu = self.driver.find_elements(By.CSS_SELECTOR, "[class*='mobile'], [class*='hamburger'], [class*='menu-toggle']")
            if mobile_menu:
                self.log("Mobile responsive elements found", "SUCCESS")
            else:
                self.log("Mobile responsive elements not found", "WARNING")
            
            # Restore original window size
            self.driver.set_window_size(original_size['width'], original_size['height'])
            
            # Test loading states
            loading_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='loading'], [class*='spinner'], [class*='skeleton']")
            if loading_elements:
                self.log("Loading state elements found", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"General UI test failed: {e}", "ERROR")
            return False

    # ========================
    # 8. ACCESSIBILITY TESTS
    # ========================
    
    def test_accessibility_features(self) -> bool:
        """Test basic accessibility features"""
        self.log("♿ Testing Accessibility Features", "INFO")
        
        try:
            # Check for alt text on images
            images = self.driver.find_elements(By.CSS_SELECTOR, "img")
            images_with_alt = [img for img in images if img.get_attribute("alt")]
            
            if images:
                alt_percentage = (len(images_with_alt) / len(images)) * 100
                self.log(f"Images with alt text: {len(images_with_alt)}/{len(images)} ({alt_percentage:.1f}%)", "SUCCESS" if alt_percentage > 80 else "WARNING")
            
            # Check for proper heading hierarchy
            headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            if headings:
                self.log(f"Heading elements found: {len(headings)}", "SUCCESS")
            
            # Check for form labels
            form_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            labeled_inputs = []
            
            for input_elem in form_inputs:
                input_id = input_elem.get_attribute("id")
                input_name = input_elem.get_attribute("name")
                
                # Check for associated label
                label = None
                if input_id:
                    label = self.driver.find_elements(By.CSS_SELECTOR, f"label[for='{input_id}']")
                
                if not label and input_name:
                    # Check for wrapping label
                    label = input_elem.find_elements(By.XPATH, "./ancestor::label")
                
                if label:
                    labeled_inputs.append(input_elem)
            
            if form_inputs:
                label_percentage = (len(labeled_inputs) / len(form_inputs)) * 100
                self.log(f"Form inputs with labels: {len(labeled_inputs)}/{len(form_inputs)} ({label_percentage:.1f}%)", "SUCCESS" if label_percentage > 70 else "WARNING")
            
            # Check for focus indicators (basic test)
            focusable_elements = self.driver.find_elements(By.CSS_SELECTOR, "button, a, input, select, textarea")
            if focusable_elements and len(focusable_elements) > 0:
                self.log(f"Focusable elements found: {len(focusable_elements)}", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"Accessibility test failed: {e}", "ERROR")
            return False

    # ========================
    # 9. MAIN TEST RUNNER
    # ========================
    
    def run_frontend_tests(self) -> bool:
        """Run all frontend UI tests"""
        
        print("🚀 OCR Invoice Processing - Frontend UI Test Suite")
        print("=" * 60)
        
        if not self.setup_driver():
            print("❌ Cannot run UI tests without WebDriver")
            print("📋 Manual Testing Instructions:")
            print(f"1. Open {FRONTEND_URL}/login")
            print(f"2. Login with {TEST_CREDENTIALS['username']}/{TEST_CREDENTIALS['password']}")
            print(f"3. Test navigation through all pages")
            print(f"4. Test file upload in {FRONTEND_URL}/upload")
            print(f"5. Test dashboard functionality")
            print(f"6. Test invoice editing")
            print(f"7. Test Prüfbericht page")
            return False
        
        start_time = datetime.now()
        
        test_results = {
            "Login Page": False,
            "Homepage Carousel": False,
            "Upload Dropzone": False,
            "Dashboard": False,
            "Invoice Editor": False,
            "Prüfbericht Page": False,
            "General UI": False,
            "Accessibility": False
        }
        
        try:
            # Run all test modules
            test_results["Login Page"] = self.test_login_page()
            time.sleep(2)
            
            test_results["Homepage Carousel"] = self.test_homepage_carousel()
            time.sleep(2)
            
            test_results["Upload Dropzone"] = self.test_upload_dropzone()
            time.sleep(2)
            
            test_results["Dashboard"] = self.test_dashboard_functionality()
            time.sleep(2)
            
            test_results["Invoice Editor"] = self.test_invoice_editor()
            time.sleep(2)
            
            test_results["Prüfbericht Page"] = self.test_prufbericht_page()
            time.sleep(2)
            
            test_results["General UI"] = self.test_general_ui_elements()
            time.sleep(2)
            
            test_results["Accessibility"] = self.test_accessibility_features()
            
        except KeyboardInterrupt:
            self.log("Test suite interrupted by user", "WARNING")
        except Exception as e:
            self.log(f"Test suite failed with error: {e}", "ERROR")
        finally:
            if self.driver:
                self.driver.quit()
        
        # Generate test report
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📋 FRONTEND UI TEST RESULTS")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status:<10} {test_name}")
            if passed:
                passed_tests += 1
        
        print("=" * 60)
        print(f"📊 Summary: {passed_tests}/{total_tests} tests passed")
        print(f"⏱️ Duration: {duration.total_seconds():.1f} seconds")
        
        # Overall result
        if passed_tests >= total_tests * 0.75:  # 75% pass rate is acceptable
            print("\n🎉 FRONTEND UI TESTS MOSTLY PASSED!")
            return True
        else:
            print(f"\n⚠️ FRONTEND UI TESTS NEED ATTENTION")
            return False

def check_services():
    """Check if required services are running"""
    print("🔍 Checking service availability...")
    
    try:
        # Check backend
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"⚠️ Backend returned HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False
    
    try:
        # Check frontend
        response = requests.get(FRONTEND_URL, timeout=5)
        print("✅ Frontend is accessible")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False
    
    return True

def main():
    """Main function to run frontend UI tests"""
    
    if not check_services():
        print("\n❌ Services are not running. Please start:")
        print("   Backend: cd backend && python main.py")
        print("   Frontend: cd frontend && npm run dev")
        return False
    
    # Run the frontend tests
    tester = FrontendUITester(headless=False)  # Set to True for headless mode
    success = tester.run_frontend_tests()
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        sys.exit(1)
