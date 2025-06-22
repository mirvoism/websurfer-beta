#!/usr/bin/env python3
"""
Comprehensive Browser MCP Test - Single Server Instance
Tests all Browser MCP tools starting from google.com → ESPN
"""

import time
from skills.browser_mcp_skills import BrowserMCPSkills

def comprehensive_browser_test():
    """Test all Browser MCP tools in one session"""
    
    print("🌐 COMPREHENSIVE BROWSER MCP TEST")
    print("=" * 45)
    print("📍 Route: google.com → ESPN.com → Test all tools")
    print("-" * 45)
    
    # Initialize browser (starts MCP server)
    print("🚀 Starting Browser MCP server...")
    browser = BrowserMCPSkills()
    
    test_results = []
    
    # TEST 1: Navigate to Google
    print("\n🔍 TEST 1: Navigate to Google")
    print("-" * 30)
    
    google_result = browser.navigate("https://google.com")
    if google_result and not google_result.get('isError'):
        print("✅ Successfully navigated to Google")
        test_results.append(("Navigate to Google", True))
        time.sleep(2)
    else:
        print("❌ Failed to navigate to Google")
        print(f"Error: {google_result}")
        test_results.append(("Navigate to Google", False))
        # Continue anyway for other tests
    
    # TEST 2: Take screenshot of Google
    print("\n📸 TEST 2: Screenshot Google")
    print("-" * 25)
    
    google_screenshot = browser.screenshot()
    if google_screenshot and not google_screenshot.startswith("Error"):
        print(f"✅ Google screenshot saved: {google_screenshot}")
        test_results.append(("Screenshot Google", True))
    else:
        print(f"❌ Google screenshot failed: {google_screenshot}")
        test_results.append(("Screenshot Google", False))
    
    # TEST 3: Get Google page snapshot
    print("\n📄 TEST 3: Google DOM Snapshot")
    print("-" * 28)
    
    google_snapshot = browser.snapshot()
    if google_snapshot and isinstance(google_snapshot, dict):
        content = google_snapshot.get('content', [])
        if content:
            print("✅ Google DOM snapshot captured")
            # Check if it's really Google
            first_item = content[0] if content else {}
            if isinstance(first_item, dict) and 'text' in first_item:
                page_text = first_item['text'].lower()
                if 'google' in page_text:
                    print("✅ Confirmed: On Google page")
                else:
                    print("⚠️  Warning: May not be on Google")
            test_results.append(("Google DOM Snapshot", True))
        else:
            print("⚠️  Empty Google snapshot")
            test_results.append(("Google DOM Snapshot", False))
    else:
        print(f"❌ Google snapshot failed: {google_snapshot}")
        test_results.append(("Google DOM Snapshot", False))
    
    # TEST 4: Navigate to ESPN
    print("\n🏈 TEST 4: Navigate to ESPN")
    print("-" * 25)
    
    espn_result = browser.navigate("https://espn.com")
    if espn_result and not espn_result.get('isError'):
        print("✅ Successfully navigated to ESPN")
        test_results.append(("Navigate to ESPN", True))
        time.sleep(3)  # Let ESPN load fully
    else:
        print("❌ Failed to navigate to ESPN")
        print(f"Error: {espn_result}")
        test_results.append(("Navigate to ESPN", False))
    
    # TEST 5: ESPN DOM Snapshot
    print("\n📄 TEST 5: ESPN DOM Snapshot")
    print("-" * 27)
    
    espn_snapshot = browser.snapshot()
    if espn_snapshot and isinstance(espn_snapshot, dict):
        content = espn_snapshot.get('content', [])
        if content:
            first_item = content[0] if content else {}
            if isinstance(first_item, dict) and 'text' in first_item:
                espn_text = first_item['text']
                print(f"✅ ESPN snapshot captured - {len(espn_text)} chars")
                
                # Verify we're on ESPN
                if 'espn' in espn_text.lower():
                    print("✅ Confirmed: On ESPN website")
                else:
                    print("⚠️  Warning: May not be on ESPN")
                
                # Show sample content
                print(f"📃 Sample: {espn_text[:200]}...")
                test_results.append(("ESPN DOM Snapshot", True))
            else:
                print("✅ ESPN snapshot captured (different format)")
                test_results.append(("ESPN DOM Snapshot", True))
        else:
            print("⚠️  Empty ESPN snapshot")
            test_results.append(("ESPN DOM Snapshot", False))
    else:
        print(f"❌ ESPN snapshot failed: {espn_snapshot}")
        test_results.append(("ESPN DOM Snapshot", False))
    
    # TEST 6: ESPN Screenshot
    print("\n📸 TEST 6: ESPN Screenshot")
    print("-" * 23)
    
    espn_screenshot = browser.screenshot()
    if espn_screenshot and not espn_screenshot.startswith("Error"):
        print(f"✅ ESPN screenshot saved: {espn_screenshot}")
        test_results.append(("ESPN Screenshot", True))
    else:
        print(f"❌ ESPN screenshot failed: {espn_screenshot}")
        test_results.append(("ESPN Screenshot", False))
    
    # TEST 7: Text Extraction
    print("\n📝 TEST 7: Extract ESPN Text")
    print("-" * 26)
    
    espn_text = browser.extract_text()
    if espn_text and not espn_text.startswith("Error"):
        print(f"✅ Text extracted - {len(espn_text)} characters")
        print(f"📃 Preview: {espn_text[:300]}...")
        test_results.append(("Extract ESPN Text", True))
    else:
        print(f"❌ Text extraction failed: {espn_text}")
        test_results.append(("Extract ESPN Text", False))
    
    # TEST 8: Scroll Page
    print("\n📜 TEST 8: Scroll ESPN Page")
    print("-" * 24)
    
    scroll_result = browser.scroll()
    if scroll_result and scroll_result.get('status') != 'error':
        print("✅ Page scrolled successfully")
        test_results.append(("Scroll ESPN Page", True))
        time.sleep(1)
    else:
        print(f"❌ Scroll failed: {scroll_result}")
        test_results.append(("Scroll ESPN Page", False))
    
    # TEST 9: Hover on Elements
    print("\n👆 TEST 9: Hover on ESPN Elements")
    print("-" * 30)
    
    # ESPN-specific hover targets
    hover_targets = [
        "a[href*='nfl']",        # NFL link
        "a[href*='nba']",        # NBA link
        "a[href*='mlb']",        # MLB link
        "nav a",                 # Navigation link
        ".navigation a",         # Navigation class
        "header a",              # Header link
        ".site-header a"         # Site header
    ]
    
    hover_success = False
    for target in hover_targets:
        print(f"🔍 Trying hover on: {target}")
        hover_result = browser.hover(target)
        
        if hover_result and hover_result.get('status') != 'error':
            print(f"✅ Hover successful on: {target}")
            hover_success = True
            break
        else:
            print(f"⚠️  Hover failed on: {target}")
        time.sleep(0.5)  # Brief pause between attempts
    
    test_results.append(("Hover on ESPN Elements", hover_success))
    
    # TEST 10: Click on Elements
    print("\n🖱️  TEST 10: Click on ESPN Elements")
    print("-" * 30)
    
    # Safe click targets on ESPN
    click_targets = [
        "a[href*='scores']",     # Scores link
        "a[href*='news']",       # News link
        "a[href*='standings']",  # Standings link
        ".site-header a",        # Header link
        "nav a:first-of-type"    # First nav link
    ]
    
    click_success = False
    for target in click_targets:
        print(f"🔍 Trying click on: {target}")
        click_result = browser.click(target)
        
        if click_result and click_result.get('status') != 'error':
            print(f"✅ Click successful on: {target}")
            click_success = True
            time.sleep(2)  # Wait for potential page change
            
            # Verify click worked with a snapshot
            verify_snapshot = browser.snapshot()
            if verify_snapshot:
                print("✅ Page state captured after click")
            break
        else:
            print(f"⚠️  Click failed on: {target}")
        time.sleep(0.5)
    
    test_results.append(("Click on ESPN Elements", click_success))
    
    # TEST 11: Type in Search
    print("\n⌨️  TEST 11: Type in ESPN Search")
    print("-" * 28)
    
    # ESPN search input targets
    search_targets = [
        "input[type='search']",
        "input[placeholder*='search']",
        "input[placeholder*='Search']",
        ".search-input",
        "#search",
        "[data-module='Search'] input",
        ".search-box input"
    ]
    
    type_success = False
    search_text = "Lakers"
    
    for target in search_targets:
        print(f"🔍 Trying to type in: {target}")
        type_result = browser.type(target, search_text)
        
        if type_result and type_result.get('status') != 'error':
            print(f"✅ Typing successful in: {target}")
            print(f"📝 Entered: '{search_text}'")
            type_success = True
            time.sleep(1)
            break
        else:
            print(f"⚠️  Typing failed in: {target}")
        time.sleep(0.5)
    
    test_results.append(("Type in ESPN Search", type_success))
    
    # TEST 12: Wait Function
    print("\n⏱️  TEST 12: Wait Function")
    print("-" * 20)
    
    print("Testing 3-second wait...")
    wait_start = time.time()
    wait_result = browser.wait(3)
    wait_duration = time.time() - wait_start
    
    if wait_result and 2.5 <= wait_duration <= 3.5:
        print(f"✅ Wait successful - {wait_duration:.1f}s")
        test_results.append(("Wait Function", True))
    else:
        print(f"❌ Wait failed - {wait_duration:.1f}s")
        test_results.append(("Wait Function", False))
    
    # TEST 13: Final Screenshot
    print("\n📸 TEST 13: Final State Screenshot")
    print("-" * 32)
    
    final_screenshot = browser.screenshot()
    if final_screenshot and not final_screenshot.startswith("Error"):
        print(f"✅ Final screenshot: {final_screenshot}")
        test_results.append(("Final Screenshot", True))
    else:
        print(f"❌ Final screenshot failed: {final_screenshot}")
        test_results.append(("Final Screenshot", False))
    
    # RESULTS SUMMARY
    print(f"\n🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 40)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    print(f"📊 Overall: {passed}/{total} tests passed ({success_rate:.1f}%)")
    print()
    
    # Detailed results
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n💡 Screenshots saved in: screenshots/")
    
    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT! Browser MCP is fully functional!")
        return "EXCELLENT"
    elif success_rate >= 60:
        print(f"\n👍 GOOD! Most Browser MCP features working!")
        return "GOOD"
    elif success_rate >= 40:
        print(f"\n⚠️  PARTIAL! Some Browser MCP issues detected!")
        return "PARTIAL"
    else:
        print(f"\n❌ POOR! Major Browser MCP issues!")
        return "POOR"

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Browser MCP Test...")
    print("📋 Make sure Browser MCP extension is connected to Chrome!")
    print()
    
    result = comprehensive_browser_test()
    
    print(f"\n{'='*50}")
    print(f"🏁 Test completed with rating: {result}")
    
    if result in ["EXCELLENT", "GOOD"]:
        print("🚀 Browser MCP is ready for autonomous web surfing!")
    else:
        print("🔧 Review failed tests above for troubleshooting") 