#!/usr/bin/env python3
"""
Test script for real Browser MCP navigation to ChatGPT
This demonstrates end-to-end browser automation with vision capabilities
"""

import time
import os
from skills.browser_mcp_skills import BrowserMCPSkills
from skills.llm_adapter import LLM

def test_chatgpt_navigation():
    """Test complete ChatGPT navigation workflow"""
    
    print("🚀 Starting ChatGPT Navigation Test")
    print("=" * 50)
    
    # Initialize browser and LLM
    browser = BrowserMCPSkills()
    llm = LLM()
    
    # Test 1: Check connections
    print("\n🔍 Step 1: Testing connections...")
    
    if not browser.test_connection():
        print("❌ Browser MCP connection failed!")
        return False
    
    if not llm.test_connection():
        print("❌ LLM connection failed!")
        return False
    
    print("✅ All connections successful!")
    
    # Test 2: Navigate to ChatGPT
    print("\n🌐 Step 2: Navigating to ChatGPT...")
    
    chatgpt_url = "https://chatgpt.com"
    result = browser.navigate(chatgpt_url)
    
    if result.get('status') == 'error':
        print(f"❌ Navigation failed: {result.get('message')}")
        return False
    
    print(f"✅ Successfully navigated to {chatgpt_url}")
    
    # Wait for page to load
    print("⏱️  Waiting for page to load...")
    browser.wait(3)
    
    # Test 3: Take screenshot for visual analysis
    print("\n📸 Step 3: Taking screenshot for visual analysis...")
    
    screenshot_path = browser.screenshot()
    if screenshot_path and not screenshot_path.startswith("Error"):
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # Use vision model to analyze the page
        if llm.has_vision():
            print("👁️  Analyzing page with vision model...")
            try:
                analysis = llm.chat_with_vision(
                    text_prompt="What do you see on this ChatGPT webpage? Describe the main elements and identify any buttons or input areas.",
                    image_paths=[screenshot_path]
                )
                print(f"🔍 Vision Analysis: {analysis}")
            except Exception as e:
                print(f"⚠️  Vision analysis failed: {e}")
    else:
        print(f"❌ Screenshot failed: {screenshot_path}")
    
    # Test 4: Look for new chat button/area
    print("\n🖱️  Step 4: Looking for new chat interface...")
    
    # Try to find and click new chat button
    # Common selectors for ChatGPT new chat
    new_chat_selectors = [
        "button[aria-label='New chat']",
        "button:contains('New chat')",
        "[data-testid='new-chat-button']",
        ".new-chat-button",
        "button[title='New chat']"
    ]
    
    new_chat_clicked = False
    for selector in new_chat_selectors:
        try:
            print(f"🔍 Trying selector: {selector}")
            result = browser.click(selector)
            if result.get('status') != 'error':
                print(f"✅ Successfully clicked new chat button: {selector}")
                new_chat_clicked = True
                break
        except Exception as e:
            print(f"⚠️  Selector {selector} failed: {e}")
            continue
    
    if not new_chat_clicked:
        print("⚠️  Could not find new chat button, continuing anyway...")
    
    # Wait for interface to update
    browser.wait(2)
    
    # Test 5: Find and use the chat input
    print("\n⌨️  Step 5: Finding chat input area...")
    
    # Common selectors for ChatGPT input
    input_selectors = [
        "textarea[placeholder*='Message']",
        "textarea[data-id='chat-input']",
        "[contenteditable='true']",
        "textarea[role='textbox']",
        ".chat-input textarea",
        "#prompt-textarea"
    ]
    
    question = "What day of the week is it today?"
    input_found = False
    
    for selector in input_selectors:
        try:
            print(f"🔍 Trying input selector: {selector}")
            result = browser.type(selector, question)
            if result.get('status') != 'error':
                print(f"✅ Successfully typed question: {selector}")
                input_found = True
                break
        except Exception as e:
            print(f"⚠️  Input selector {selector} failed: {e}")
            continue
    
    if not input_found:
        print("❌ Could not find chat input area")
        return False
    
    # Test 6: Submit the question
    print(f"\n🚀 Step 6: Submitting question: '{question}'")
    
    # Try to find and click send button
    send_selectors = [
        "button[aria-label='Send']",
        "button[data-testid='send-button']",
        "button:contains('Send')",
        ".send-button",
        "button[type='submit']"
    ]
    
    # Wait a moment before sending
    browser.wait(1)
    
    send_clicked = False
    for selector in send_selectors:
        try:
            print(f"🔍 Trying send selector: {selector}")
            result = browser.click(selector)
            if result.get('status') != 'error':
                print(f"✅ Successfully clicked send button: {selector}")
                send_clicked = True
                break
        except Exception as e:
            print(f"⚠️  Send selector {selector} failed: {e}")
            continue
    
    if not send_clicked:
        print("⚠️  Could not find send button, trying Enter key...")
        # Try pressing Enter as fallback
        try:
            browser.scroll()  # This uses press_key internally
            print("✅ Attempted to send via keyboard")
        except Exception as e:
            print(f"❌ Keyboard send failed: {e}")
    
    # Test 7: Wait for response and take final screenshot
    print("\n⏱️  Step 7: Waiting for ChatGPT response...")
    browser.wait(5)  # Wait for response
    
    print("📸 Taking final screenshot...")
    final_screenshot = browser.screenshot()
    if final_screenshot and not final_screenshot.startswith("Error"):
        print(f"✅ Final screenshot saved: {final_screenshot}")
        
        # Analyze the response with vision
        if llm.has_vision():
            print("👁️  Analyzing ChatGPT response with vision...")
            try:
                response_analysis = llm.chat_with_vision(
                    text_prompt="What is ChatGPT's response to the question about the day of the week? Extract the text from the response.",
                    image_paths=[final_screenshot]
                )
                print(f"🤖 ChatGPT Response Analysis: {response_analysis}")
            except Exception as e:
                print(f"⚠️  Response analysis failed: {e}")
    
    # Test 8: Extract text content
    print("\n📄 Step 8: Extracting page text...")
    try:
        page_text = browser.extract_text()
        if page_text and not page_text.startswith("Error"):
            print("✅ Successfully extracted page text")
            # Look for day-related content in the text
            text_lower = page_text.lower()
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            found_days = [day for day in days if day in text_lower]
            if found_days:
                print(f"🗓️  Found day references: {found_days}")
            else:
                print("🔍 No specific day mentions found in extracted text")
        else:
            print(f"❌ Text extraction failed: {page_text}")
    except Exception as e:
        print(f"❌ Text extraction error: {e}")
    
    print("\n🎉 ChatGPT Navigation Test Complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    # Set up logging for better visibility
    import logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    # Run the test
    success = test_chatgpt_navigation()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("💡 Check the screenshots/ directory for visual captures")
    else:
        print("\n❌ Test encountered issues")
        print("💡 Check the logs above for details") 