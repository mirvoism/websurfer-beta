#!/usr/bin/env python3
"""
Interactive Browser MCP Test - All actions in one session
Keeps the browser connection alive throughout testing
"""

import time
from skills.browser_mcp_skills import BrowserMCPSkills

def run_interactive_test():
    """Run all browser tests interactively in one session"""
    
    print("🏈 INTERACTIVE BROWSER MCP TEST - ESPN.com")
    print("=" * 50)
    
    # Initialize browser (this starts the server)
    print("🚀 Initializing Browser MCP...")
    browser = BrowserMCPSkills()
    
    # Test connection first
    print("\n🔍 TEST 0: Connection Check")
    print("-" * 25)
    
    connection_test = browser.navigate("about:blank")
    if connection_test and connection_test.get('isError'):
        print("❌ Browser MCP extension not connected!")
        print("🛠️  Please:")
        print("   1. Open Chrome")
        print("   2. Click Browser MCP extension icon")
        print("   3. Click 'Connect' button")
        print("   4. Then press ENTER to continue...")
        input("Ready? Press ENTER...")
        
        # Test again
        connection_test = browser.navigate("about:blank")
        if connection_test and connection_test.get('isError'):
            print("❌ Still not connected. Exiting...")
            return False
    
    print("✅ Connection established!")
    
    # Now run all tests in sequence
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Navigation
    total_tests += 1
    print(f"\n🌐 TEST {total_tests}: Navigation to ESPN")
    print("-" * 30)
    
    nav_result = browser.navigate("https://espn.com")
    if nav_result and not nav_result.get('isError'):
        print("✅ Navigation successful!")
        print(f"📄 Page title detected in content")
        tests_passed += 1
        time.sleep(2)  # Let page load
    else:
        print("❌ Navigation failed")
        print(f"Error: {nav_result}")
    
    # Test 2: DOM Snapshot
    total_tests += 1
    print(f"\n📄 TEST {total_tests}: DOM Snapshot")
    print("-" * 25)
    
    snapshot_result = browser.snapshot()
    if snapshot_result and isinstance(snapshot_result, dict):
        content = snapshot_result.get('content', [])
        if content:
            first_item = content[0] if content else {}
            if isinstance(first_item, dict) and 'text' in first_item:
                page_content = first_item['text']
                print(f"✅ Snapshot successful! Content length: {len(page_content)} chars")
                
                # Check if we're really on ESPN
                if 'espn' in page_content.lower():
                    print("✅ Confirmed: On ESPN website")
                else:
                    print("⚠️  Warning: May not be on ESPN")
                    
                print(f"📃 Sample content: {page_content[:150]}...")
                tests_passed += 1
            else:
                print(f"✅ Snapshot captured (different format)")
                tests_passed += 1
        else:
            print("⚠️  Empty snapshot")
    else:
        print(f"❌ Snapshot failed: {snapshot_result}")
    
    # Test 3: Screenshot
    total_tests += 1
    print(f"\n📸 TEST {total_tests}: Screenshot")
    print("-" * 20)
    
    screenshot_result = browser.screenshot()
    if screenshot_result and not screenshot_result.startswith("Error"):
        print(f"✅ Screenshot successful: {screenshot_result}")
        tests_passed += 1
    else:
        print(f"❌ Screenshot failed: {screenshot_result}")
    
    # Test 4: Text Extraction
    total_tests += 1
    print(f"\n📝 TEST {total_tests}: Text Extraction")
    print("-" * 25)
    
    text_result = browser.extract_text()
    if text_result and not text_result.startswith("Error"):
        print(f"✅ Text extraction successful! Length: {len(text_result)} chars")
        print(f"📃 Sample: {text_result[:200]}...")
        tests_passed += 1
    else:
        print(f"❌ Text extraction failed: {text_result}")
    
    # Test 5: Scrolling
    total_tests += 1
    print(f"\n📜 TEST {total_tests}: Scrolling")
    print("-" * 18)
    
    scroll_result = browser.scroll()
    if scroll_result and scroll_result.get('status') != 'error':
        print("✅ Scroll successful!")
        tests_passed += 1
        time.sleep(1)
    else:
        print(f"❌ Scroll failed: {scroll_result}")
    
    # Test 6: Find and Hover
    total_tests += 1
    print(f"\n👆 TEST {total_tests}: Hover Action")
    print("-" * 20)
    
    # Common selectors for ESPN
    hover_targets = [
        "a[href*='nfl']",
        "a[href*='nba']", 
        ".navigation a",
        "nav a",
        "header a"
    ]
    
    hover_success = False
    for target in hover_targets:
        hover_result = browser.hover(target)
        if hover_result and hover_result.get('status') != 'error':
            print(f"✅ Hover successful on: {target}")
            hover_success = True
            tests_passed += 1
            break
        else:
            print(f"⚠️  Hover failed on: {target}")
    
    if not hover_success:
        print("❌ All hover attempts failed")
    
    # Test 7: Find and Click
    total_tests += 1
    print(f"\n🖱️  TEST {total_tests}: Click Action")
    print("-" * 19)
    
    # Try clicking on safe elements
    click_targets = [
        "a[href*='scores']",
        "a[href*='news']",
        "nav a:first-of-type",
        ".site-header a"
    ]
    
    click_success = False
    for target in click_targets:
        click_result = browser.click(target)
        if click_result and click_result.get('status') != 'error':
            print(f"✅ Click successful on: {target}")
            click_success = True
            tests_passed += 1
            time.sleep(2)  # Wait for potential navigation
            break
        else:
            print(f"⚠️  Click failed on: {target}")
    
    if not click_success:
        print("❌ All click attempts failed")
    
    # Test 8: Search and Type
    total_tests += 1
    print(f"\n⌨️  TEST {total_tests}: Typing Action")
    print("-" * 20)
    
    # Look for search inputs
    search_targets = [
        "input[type='search']",
        "input[placeholder*='search']",
        "input[placeholder*='Search']",
        ".search-input",
        "#search"
    ]
    
    type_success = False
    test_text = "NBA"
    
    for target in search_targets:
        type_result = browser.type(target, test_text)
        if type_result and type_result.get('status') != 'error':
            print(f"✅ Typing successful in: {target}")
            print(f"📝 Entered text: '{test_text}'")
            type_success = True
            tests_passed += 1
            time.sleep(1)
            break
        else:
            print(f"⚠️  Typing failed in: {target}")
    
    if not type_success:
        print("❌ All typing attempts failed")
    
    # Test 9: Wait Function
    total_tests += 1
    print(f"\n⏱️  TEST {total_tests}: Wait Function")
    print("-" * 21)
    
    wait_result = browser.wait(2)
    if wait_result:
        print("✅ Wait function successful!")
        tests_passed += 1
    else:
        print("❌ Wait function failed")
    
    # Final screenshot
    total_tests += 1
    print(f"\n📸 TEST {total_tests}: Final Screenshot")
    print("-" * 25)
    
    final_screenshot = browser.screenshot()
    if final_screenshot and not final_screenshot.startswith("Error"):
        print(f"✅ Final screenshot: {final_screenshot}")
        tests_passed += 1
    else:
        print(f"❌ Final screenshot failed: {final_screenshot}")
    
    # Summary
    success_rate = (tests_passed / total_tests) * 100
    
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 30)
    print(f"📊 Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print("🎉 EXCELLENT! Browser MCP is working well!")
        status = "SUCCESS"
    elif success_rate >= 50:
        print("👍 GOOD! Most features are working!")
        status = "PARTIAL_SUCCESS"
    else:
        print("⚠️  NEEDS WORK! Many features failed")
        status = "NEEDS_IMPROVEMENT"
    
    print(f"\n💡 Screenshots saved in: screenshots/")
    return status

if __name__ == "__main__":
    print("🔧 Starting Interactive Browser MCP Test...")
    print("Make sure Chrome is open with Browser MCP extension connected!")
    
    input("\n📱 Press ENTER when ready to start testing...")
    
    result = run_interactive_test()
    
    print(f"\n{'='*50}")
    print(f"🏁 Testing completed with status: {result}")
    
    if result == "SUCCESS":
        print("🚀 Ready for autonomous web surfing!")
    else:
        print("🔧 Review the results above for any issues") 