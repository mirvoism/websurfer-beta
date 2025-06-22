#!/usr/bin/env python3
"""
Comprehensive Browser MCP Actions Test
Tests each browser automation tool systematically using ESPN.com
"""

import time
from skills.browser_mcp_skills import BrowserMCPSkills

def test_browser_actions():
    """Test all Browser MCP actions systematically"""
    
    print("🏈 BROWSER MCP ACTIONS TEST - ESPN.com")
    print("=" * 50)
    
    # Initialize browser
    browser = BrowserMCPSkills()
    
    # Test 1: Navigation
    print("\n🌐 TEST 1: Navigation")
    print("-" * 20)
    espn_url = "https://espn.com"
    print(f"Navigating to: {espn_url}")
    
    nav_result = browser.navigate(espn_url)
    print(f"✅ Navigation result: {nav_result}")
    
    if nav_result.get('isError'):
        print("❌ Navigation failed - stopping test")
        return False
    
    # Wait for page to load
    print("⏱️  Waiting 3 seconds for page load...")
    time.sleep(3)
    
    # Test 2: Screenshot
    print("\n📸 TEST 2: Screenshot")
    print("-" * 20)
    screenshot_result = browser.screenshot()
    print(f"Screenshot result: {screenshot_result}")
    
    if screenshot_result and not screenshot_result.startswith("Error"):
        print(f"✅ Screenshot saved successfully: {screenshot_result}")
    else:
        print(f"❌ Screenshot failed: {screenshot_result}")
    
    # Test 3: DOM Snapshot  
    print("\n📄 TEST 3: DOM Snapshot")
    print("-" * 20)
    snapshot_result = browser.snapshot()
    
    if snapshot_result and isinstance(snapshot_result, dict):
        content = snapshot_result.get('content', [])
        if content:
            # Show page info
            first_item = content[0] if content else {}
            if isinstance(first_item, dict) and 'text' in first_item:
                page_info = first_item['text'][:300]
                print(f"✅ Snapshot captured - Page info: {page_info}...")
                
                # Check if we're on ESPN
                if 'espn' in page_info.lower():
                    print("✅ Confirmed: Successfully on ESPN website!")
                else:
                    print("⚠️  Warning: May not be on ESPN page")
            else:
                print(f"✅ Snapshot captured - Content type: {type(first_item)}")
        else:
            print("⚠️  Empty snapshot content")
    else:
        print(f"❌ Snapshot failed: {snapshot_result}")
    
    # Test 4: Text Extraction
    print("\n📝 TEST 4: Text Extraction")
    print("-" * 20)
    text_result = browser.extract_text()
    if text_result and not text_result.startswith("Error"):
        print(f"✅ Text extracted - Length: {len(text_result)} chars")
        print(f"📃 First 200 chars: {text_result[:200]}...")
    else:
        print(f"❌ Text extraction failed: {text_result}")
    
    # Test 5: Scrolling
    print("\n📜 TEST 5: Scrolling")
    print("-" * 20)
    scroll_result = browser.scroll()
    print(f"Scroll result: {scroll_result}")
    
    if scroll_result and scroll_result.get('status') != 'error':
        print("✅ Scrolling successful")
    else:
        print("❌ Scrolling failed")
    
    # Wait after scroll
    time.sleep(2)
    
    # Test 6: Hover (try to hover over a common element)
    print("\n👆 TEST 6: Hover")
    print("-" * 20)
    # Common selectors that might exist on ESPN
    hover_selectors = [
        "a[href*='nfl']",  # NFL link
        "a[href*='nba']",  # NBA link  
        ".navigation a",   # Navigation link
        "header a",        # Header link
        "nav a"            # Nav link
    ]
    
    hover_success = False
    for selector in hover_selectors:
        print(f"🔍 Trying hover on: {selector}")
        hover_result = browser.hover(selector)
        
        if hover_result and hover_result.get('status') != 'error':
            print(f"✅ Hover successful on: {selector}")
            hover_success = True
            break
        else:
            print(f"⚠️  Hover failed on: {selector}")
    
    if not hover_success:
        print("❌ All hover attempts failed - elements may not exist")
    
    # Test 7: Clicking (try to click a link)
    print("\n🖱️  TEST 7: Clicking")
    print("-" * 20)
    # Common clickable elements on ESPN
    click_selectors = [
        "a[href*='scores']",    # Scores link
        "a[href*='news']",      # News link
        ".site-header a",       # Header link
        "nav a:first-child",    # First nav link
        "a[href='/']"           # Home link
    ]
    
    click_success = False
    for selector in click_selectors:
        print(f"🔍 Trying click on: {selector}")
        click_result = browser.click(selector)
        
        if click_result and click_result.get('status') != 'error':
            print(f"✅ Click successful on: {selector}")
            click_success = True
            
            # Wait for potential page change
            time.sleep(2)
            
            # Verify click worked by taking another snapshot
            print("📄 Verifying click result...")
            verify_snapshot = browser.snapshot()
            if verify_snapshot:
                print("✅ Page state captured after click")
            break
        else:
            print(f"⚠️  Click failed on: {selector}")
    
    if not click_success:
        print("❌ All click attempts failed - elements may not exist")
    
    # Test 8: Typing (try to find and use a search box)
    print("\n⌨️  TEST 8: Typing")
    print("-" * 20)
    # Common search input selectors
    search_selectors = [
        "input[type='search']",
        "input[placeholder*='search']",
        "input[placeholder*='Search']",
        ".search-input",
        "#search",
        "[data-search]"
    ]
    
    type_success = False
    test_text = "NFL"
    
    for selector in search_selectors:
        print(f"🔍 Trying to type in: {selector}")
        type_result = browser.type(selector, test_text)
        
        if type_result and type_result.get('status') != 'error':
            print(f"✅ Typing successful in: {selector}")
            print(f"📝 Typed: '{test_text}'")
            type_success = True
            
            # Wait to see the effect
            time.sleep(1)
            break
        else:
            print(f"⚠️  Typing failed in: {selector}")
    
    if not type_success:
        print("❌ All typing attempts failed - search elements may not exist")
    
    # Test 9: Wait Function
    print("\n⏱️  TEST 9: Wait Function")
    print("-" * 20)
    print("Testing 2-second wait...")
    wait_result = browser.wait(2)
    print(f"✅ Wait completed: {wait_result}")
    
    # Final screenshot to see end state
    print("\n📸 FINAL: End State Screenshot")
    print("-" * 20)
    final_screenshot = browser.screenshot()
    if final_screenshot and not final_screenshot.startswith("Error"):
        print(f"✅ Final screenshot saved: {final_screenshot}")
    else:
        print(f"❌ Final screenshot failed: {final_screenshot}")
    
    # Test Summary
    print("\n🎯 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Navigation", nav_result and not nav_result.get('isError')),
        ("Screenshot", screenshot_result and not screenshot_result.startswith("Error")),
        ("DOM Snapshot", snapshot_result and isinstance(snapshot_result, dict)),
        ("Text Extraction", text_result and not text_result.startswith("Error")),
        ("Scrolling", scroll_result and scroll_result.get('status') != 'error'),
        ("Hover", hover_success),
        ("Clicking", click_success),
        ("Typing", type_success),
        ("Wait", wait_result),
        ("Final Screenshot", final_screenshot and not final_screenshot.startswith("Error"))
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    if passed >= 7:  # Most tests should pass
        print(f"\n🎉 SUCCESS: Browser MCP is working well! ({passed}/{total})")
        return True
    else:
        print(f"\n⚠️  PARTIAL: Some issues detected ({passed}/{total})")
        return False

if __name__ == "__main__":
    # Set up logging for better visibility
    import logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    # Run the comprehensive test
    success = test_browser_actions()
    
    print(f"\n{'='*50}")
    if success:
        print("🏆 Browser MCP testing completed successfully!")
        print("💡 Check the screenshots/ directory for visual captures")
    else:
        print("🔧 Browser MCP testing completed with some issues")
        print("💡 Review the test results above for details") 