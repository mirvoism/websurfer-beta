#!/usr/bin/env python3
"""
Simple Browser MCP test - just navigation to verify functionality
"""

import time
from skills.browser_mcp_skills import BrowserMCPSkills

def simple_navigation_test():
    """Test basic navigation functionality"""
    
    print("🚀 Simple Browser MCP Navigation Test")
    print("=" * 40)
    
    # Initialize browser
    browser = BrowserMCPSkills()
    
    # Test 1: Navigate to a simple page
    print("\n🌐 Test 1: Navigate to ChatGPT")
    result = browser.navigate("https://chatgpt.com")
    print(f"Result: {result}")
    
    # Wait a moment
    print("\n⏱️  Waiting 3 seconds...")
    time.sleep(3)
    
    # Test 2: Take a screenshot
    print("\n📸 Test 2: Take screenshot")
    screenshot_path = browser.screenshot()
    print(f"Screenshot result: {screenshot_path}")
    
    # Test 3: Get page snapshot
    print("\n📄 Test 3: Get page snapshot")
    snapshot_result = browser.snapshot()
    print(f"Snapshot result: {type(snapshot_result)} - {len(str(snapshot_result))} chars")
    
    print("\n✅ Simple test completed!")
    return True

if __name__ == "__main__":
    simple_navigation_test() 