#!/usr/bin/env python3
"""
Complete Browser MCP Functionality Test
Tests all Browser MCP tools starting from google.com → ESPN
Run after reconnecting Browser MCP extension
"""

import time
from skills.browser_mcp_skills import BrowserMCPSkills

def test_complete_browser_mcp():
    """Complete test of all Browser MCP functionality"""
    
    print("🌐 COMPLETE BROWSER MCP TEST")
    print("=" * 50)
    print("📍 Route: google.com → ESPN → Test all tools")
    print("🔧 Make sure Browser MCP extension is connected!")
    print("-" * 50)
    
    # Initialize browser (starts MCP server)
    print("🚀 Starting Browser MCP server...")
    browser = BrowserMCPSkills()
    
    test_results = []
    
    def log_test(test_name, result, details=""):
        """Log test result"""
        # More robust error checking
        is_error = False
        if isinstance(result, dict) and result.get('isError'):
            is_error = True
        elif isinstance(result, str) and result.startswith("Error:"):
            is_error = True
        
        status = "❌ FAIL" if is_error else "✅ PASS"
        test_results.append((test_name, status, details))
        print(f"{status} {test_name}: {details}")
    
    # TEST 1: Navigate to Google
    print("\n🔍 TEST 1: Navigate to Google")
    print("-" * 25)
    google_result = browser.navigate("https://google.com")
    log_test("Navigate to Google", google_result, "Initial navigation")
    time.sleep(2)
    
    # TEST 2: Take Google screenshot
    print("\n📸 TEST 2: Screenshot Google")
    print("-" * 25)
    google_screenshot = browser.screenshot()
    log_test("Google Screenshot", google_screenshot, f"Saved: {google_screenshot}")
    
    # TEST 3: Get Google page snapshot
    print("\n📄 TEST 3: Google Page Snapshot")
    print("-" * 25)
    google_snapshot = browser.snapshot()
    if google_snapshot and isinstance(google_snapshot, dict):
        content = google_snapshot.get('content', [])
        if content:
            # Handle different content structures
            try:
                if isinstance(content[0], dict):
                    text_content = content[0].get('text', '')
                else:
                    text_content = str(content[0])
                text_length = len(text_content)
                log_test("Google Snapshot", google_snapshot, f"Content length: {text_length} chars")
            except (IndexError, AttributeError) as e:
                log_test("Google Snapshot", google_snapshot, f"Content structure: {type(content)}")
        else:
            log_test("Google Snapshot", google_snapshot, "No content received")
    else:
        log_test("Google Snapshot", google_snapshot, "Invalid snapshot format")
    
    # TEST 4: Navigate to ESPN
    print("\n🏈 TEST 4: Navigate to ESPN")
    print("-" * 25)
    espn_result = browser.navigate("https://espn.com")
    log_test("Navigate to ESPN", espn_result, "Navigation to sports site")
    time.sleep(3)  # Wait for ESPN to load
    
    # TEST 5: Take ESPN screenshot
    print("\n📸 TEST 5: Screenshot ESPN")
    print("-" * 25)
    espn_screenshot = browser.screenshot()
    log_test("ESPN Screenshot", espn_screenshot, f"Saved: {espn_screenshot}")
    
    # TEST 6: Get ESPN page snapshot
    print("\n📄 TEST 6: ESPN Page Snapshot")
    print("-" * 25)
    espn_snapshot = browser.snapshot()
    if espn_snapshot and isinstance(espn_snapshot, dict):
        content = espn_snapshot.get('content', [])
        if content:
            try:
                if isinstance(content[0], dict):
                    text_content = content[0].get('text', '')
                else:
                    text_content = str(content[0])
                log_test("ESPN Snapshot", espn_snapshot, f"Content length: {len(text_content)} chars")
                
                # Check if we're actually on ESPN
                if 'espn' in text_content.lower() or 'sports' in text_content.lower():
                    print("✅ Confirmed: Successfully on ESPN website")
                else:
                    print("⚠️  Warning: May not be on ESPN website")
            except (IndexError, AttributeError) as e:
                log_test("ESPN Snapshot", espn_snapshot, f"Content structure: {type(content)}")
        else:
            log_test("ESPN Snapshot", espn_snapshot, "No content received")
    else:
        log_test("ESPN Snapshot", espn_snapshot, "Invalid snapshot format")
    
    # TEST 7: Extract text content
    print("\n📝 TEST 7: Extract Text Content")
    print("-" * 25)
    try:
        text_content = browser.extract_text()
        if text_content and not text_content.startswith("Error"):
            log_test("Text Extraction", text_content, f"Extracted {len(text_content)} characters")
            print(f"📋 Text preview: {text_content[:200]}...")
        else:
            log_test("Text Extraction", text_content, "Failed to extract text")
    except Exception as e:
        log_test("Text Extraction", str(e), f"Exception: {e}")
    
    # TEST 8: Scroll down
    print("\n📜 TEST 8: Scroll Down")
    print("-" * 25)
    scroll_result = browser.scroll("PageDown")
    log_test("Scroll Down", scroll_result, "PageDown key press")
    time.sleep(1)
    
    # TEST 9: Take screenshot after scroll
    print("\n📸 TEST 9: Screenshot After Scroll")
    print("-" * 25)
    scroll_screenshot = browser.screenshot()
    log_test("Post-Scroll Screenshot", scroll_screenshot, f"Saved: {scroll_screenshot}")
    
    # TEST 10: Hover over element
    print("\n👋 TEST 10: Hover Over Element")
    print("-" * 25)
    # Try to hover over a common ESPN element
    hover_result = browser.hover("a[href*='nfl'], .headline a, h1 a")
    log_test("Hover Element", hover_result, "Hover over link/headline")
    time.sleep(1)
    
    # TEST 11: Click on element
    print("\n🖱️  TEST 11: Click Element")
    print("-" * 25)
    # Try to click on a safe element (like a section link)
    click_result = browser.click("a[href*='scores'], .scores a, [data-module='scores']")
    log_test("Click Element", click_result, "Click on scores link")
    time.sleep(2)
    
    # TEST 12: Take screenshot after click
    print("\n📸 TEST 12: Screenshot After Click")
    print("-" * 25)
    click_screenshot = browser.screenshot()
    log_test("Post-Click Screenshot", click_screenshot, f"Saved: {click_screenshot}")
    
    # TEST 13: Try typing in search (if available)
    print("\n⌨️  TEST 13: Type in Search")
    print("-" * 25)
    # Look for search input
    type_result = browser.type("input[type='search'], input[placeholder*='search'], .search-input", "Lakers")
    log_test("Type in Search", type_result, "Typed 'Lakers' in search field")
    time.sleep(1)
    
    # TEST 14: Wait function
    print("\n⏱️  TEST 14: Wait Function")
    print("-" * 25)
    wait_result = browser.wait(2)
    log_test("Wait Function", wait_result, "Waited 2 seconds")
    
    # TEST 15: Final page state
    print("\n🎯 TEST 15: Final Page State")
    print("-" * 25)
    final_snapshot = browser.snapshot()
    if final_snapshot and isinstance(final_snapshot, dict):
        content = final_snapshot.get('content', [])
        if content:
            try:
                if isinstance(content[0], dict):
                    final_text = content[0].get('text', '')
                else:
                    final_text = str(content[0])
                log_test("Final State", final_snapshot, f"Final content: {len(final_text)} chars")
            except (IndexError, AttributeError) as e:
                log_test("Final State", final_snapshot, f"Content structure: {type(content)}")
        else:
            log_test("Final State", final_snapshot, "No final content")
    else:
        log_test("Final State", final_snapshot, "Invalid final snapshot")
    
    # SUMMARY REPORT
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 50)
    
    passed_tests = 0
    failed_tests = 0
    
    for test_name, status, details in test_results:
        print(f"{status} {test_name}")
        if "PASS" in status:
            passed_tests += 1
        else:
            failed_tests += 1
    
    print("-" * 50)
    print(f"📈 RESULTS: {passed_tests} PASSED, {failed_tests} FAILED")
    print(f"📊 SUCCESS RATE: {(passed_tests/(passed_tests+failed_tests)*100):.1f}%")
    
    if passed_tests >= 12:  # Most tests should pass
        print("🎉 BROWSER MCP IS FULLY FUNCTIONAL!")
        print("✅ Ready for production WebSurfer-β deployment")
    elif passed_tests >= 8:
        print("⚠️  BROWSER MCP IS PARTIALLY FUNCTIONAL")
        print("🔧 Some features may need attention")
    else:
        print("❌ BROWSER MCP NEEDS TROUBLESHOOTING")
        print("🔧 Check Browser MCP extension connection")
    
    print("\n📁 Screenshots saved in screenshots/ directory:")
    print("   • Automatically timestamped filenames")
    print("   • Check screenshots/ folder for all captured images")
    
    return passed_tests, failed_tests

if __name__ == "__main__":
    print("🧪 BROWSER MCP COMPLETE FUNCTIONALITY TEST")
    print("=" * 55)
    print("⚠️  IMPORTANT: Browser MCP extension should be connected!")
    print("🚀 Starting test automatically...")
    print()
    
    try:
        passed, failed = test_complete_browser_mcp()
        
        print(f"\n🏁 TEST COMPLETED: {passed} passed, {failed} failed")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 