#!/usr/bin/env python3
"""
Browser MCP Extension Setup Guide
Step-by-step instructions for connecting Chrome extension
"""

def print_setup_guide():
    """Print detailed setup instructions for Browser MCP extension"""
    
    print("🔗 BROWSER MCP EXTENSION SETUP GUIDE")
    print("=" * 50)
    
    print("\n📋 STEP-BY-STEP INSTRUCTIONS:")
    print("-" * 30)
    
    print("\n1. 🌐 OPEN CHROME BROWSER")
    print("   • Open Google Chrome")
    print("   • Make sure it's the same browser where you want automation")
    
    print("\n2. 🔍 FIND BROWSER MCP EXTENSION")
    print("   • Look in the Chrome toolbar for the Browser MCP extension icon")
    print("   • It might be hidden in the extensions menu (puzzle piece icon)")
    print("   • If not found, you may need to install it from:")
    print("     → Chrome Web Store: Search 'Browser MCP'")
    print("     → Or visit: https://browsermcp.io/setup-extension")
    
    print("\n3. 🌐 NAVIGATE TO TARGET WEBSITE")
    print("   • In Chrome, navigate to the website you want to automate")
    print("   • Example: Go to https://espn.com")
    print("   • Wait for the page to fully load")
    
    print("\n4. 🔗 CONNECT THE EXTENSION")
    print("   • Click the Browser MCP extension icon in the toolbar")
    print("   • You should see a popup with a 'Connect' button")
    print("   • Click the 'Connect' button")
    print("   • The extension should now be connected to this tab")
    
    print("\n5. ✅ VERIFY CONNECTION")
    print("   • The extension icon should change to show it's connected")
    print("   • You might see a green indicator or 'Connected' status")
    print("   • Keep this tab active (don't close it)")
    
    print("\n🚨 IMPORTANT NOTES:")
    print("-" * 20)
    print("• The extension connects to ONE TAB at a time")
    print("• You must connect it to the SPECIFIC tab you want to automate")
    print("• If you navigate to a different page, you may need to reconnect")
    print("• Keep the connected tab as the active/focused tab")
    
    print("\n🔧 TROUBLESHOOTING:")
    print("-" * 20)
    print("• If no extension icon: Install Browser MCP extension first")
    print("• If no 'Connect' button: Try refreshing the page")
    print("• If connection fails: Try closing and reopening Chrome")
    print("• If still issues: Check Chrome developer console for errors")
    
    print("\n📊 TESTING CONNECTION:")
    print("-" * 25)
    print("After connecting, you should be able to:")
    print("• See different content in our test results")
    print("• Get actual page content instead of connection errors")
    print("• Successfully take screenshots")
    print("• Control the actual browser tab")

def check_connection_status():
    """Try to check if Browser MCP is connected"""
    print("\n🔍 TESTING CURRENT CONNECTION STATUS")
    print("-" * 40)
    
    try:
        from skills.browser_mcp_skills import BrowserMCPSkills
        browser = BrowserMCPSkills()
        
        print("🧪 Testing basic connection...")
        result = browser.navigate("about:blank")
        
        if result and result.get('isError'):
            print("❌ EXTENSION NOT CONNECTED")
            print("💡 Please follow the setup guide above")
            print(f"🔍 Error details: {result.get('content', [{}])[0].get('text', 'Unknown error')}")
            return False
        else:
            print("✅ EXTENSION APPEARS TO BE CONNECTED!")
            print("🎉 You can now run browser automation tests")
            return True
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print_setup_guide()
    
    print("\n" + "="*50)
    input("📱 Press ENTER after you've connected the extension...")
    
    # Test connection after user setup
    connected = check_connection_status()
    
    if connected:
        print("\n🚀 READY TO TEST!")
        print("You can now run:")
        print("  python test_browser_actions.py")
    else:
        print("\n🔄 Please try the setup steps again")
        print("Make sure to:")
        print("1. Connect the extension to the correct tab")
        print("2. Keep that tab active/focused")
        print("3. Don't close the connected tab") 