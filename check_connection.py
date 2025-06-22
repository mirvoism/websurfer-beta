#!/usr/bin/env python3
"""
Quick Browser MCP Connection Checker
Use this to verify extension connection before running tests
"""

from skills.browser_mcp_skills import BrowserMCPSkills

def check_connection():
    """Quick check if Browser MCP extension is connected"""
    
    print("🔍 BROWSER MCP CONNECTION CHECK")
    print("=" * 35)
    
    browser = BrowserMCPSkills()
    
    # Test navigation to a simple page
    print("🧪 Testing navigation...")
    result = browser.navigate("about:blank")
    
    if result and result.get('isError'):
        print("❌ EXTENSION NOT CONNECTED")
        print("🔧 Error:", result.get('content', [{}])[0].get('text', 'Unknown error'))
        print()
        print("📋 TO CONNECT:")
        print("1. Open Chrome")
        print("2. Navigate to google.com")  
        print("3. Click Browser MCP extension icon")
        print("4. Click 'Connect' button")
        print("5. Run this script again")
        return False
    else:
        print("✅ EXTENSION CONNECTED!")
        print("🎉 Browser MCP is ready for automation")
        
        # Quick functionality test
        print("\n🧪 Testing basic functionality...")
        
        # Test snapshot
        snapshot = browser.snapshot()
        if snapshot and isinstance(snapshot, dict):
            print("✅ DOM snapshot: Working")
        else:
            print("❌ DOM snapshot: Failed")
        
        # Test scroll
        scroll = browser.scroll()
        if scroll and scroll.get('status') != 'error':
            print("✅ Scrolling: Working")
        else:
            print("❌ Scrolling: Failed")
        
        print("\n🚀 Ready to run comprehensive tests!")
        return True

if __name__ == "__main__":
    connected = check_connection()
    
    if connected:
        print("\n" + "="*50)
        print("✅ CONNECTION VERIFIED!")
        print("You can now run: python comprehensive_browser_test.py")
    else:
        print("\n" + "="*50)
        print("❌ CONNECTION NEEDED!")
        print("Follow the steps above, then try again") 