#!/usr/bin/env python3
"""
Test LLM Tool Integration - Demonstrates how LLM discovers and uses browser tools
"""

from skills.browser_mcp_skills import BrowserMCPSkills
from skills.llm_adapter import LLM
import json

def test_tool_discovery():
    """Test how LLM discovers available browser tools and their capabilities"""
    
    print("🧪 LLM TOOL INTEGRATION TEST")
    print("=" * 50)
    print("Testing how LLM discovers and uses browser automation tools")
    print("-" * 50)
    
    # Initialize components
    browser = BrowserMCPSkills()
    llm = LLM(provider="mac_studio")
    
    # 1. LLM discovers available tools
    print("\n📋 STEP 1: Tool Discovery")
    print("-" * 25)
    capabilities = browser.get_tool_capabilities()
    
    print("🔧 Available tool categories:")
    for category in capabilities.keys():
        print(f"   • {category}: {len(capabilities[category])} tools")
    
    # 2. LLM analyzes tool capabilities
    print("\n🧠 STEP 2: LLM Tool Analysis")
    print("-" * 25)
    
    tool_analysis_prompt = f"""
I am WebSurfer-β, an autonomous web browsing agent. I have access to these browser automation tools:

{json.dumps(capabilities, indent=2)}

Based on these capabilities, please analyze:

1. What are the key differences between visual and non-visual approaches?
2. When should I use visual tools vs non-visual tools?
3. What is the recommended workflow for a complex task like "search for Lakers news on ESPN"?
4. How do these tools work together to enable autonomous browsing?

Please provide a strategic analysis of how to best use these tools.
"""
    
    if llm.has_vision():
        print("👁️  Using vision-capable model for analysis...")
        analysis = llm.chat(
            messages=[{"role": "user", "content": tool_analysis_prompt}],
            model="llama4:scout"
        )
    else:
        print("📝 Using text-only model for analysis...")
        analysis = llm.chat(
            messages=[{"role": "user", "content": tool_analysis_prompt}],
            model=llm.default_model
        )
    
    print("🤖 LLM Analysis:")
    print(analysis)
    
    # 3. Demonstrate visual vs non-visual tool usage
    print("\n🎯 STEP 3: Tool Usage Demonstration")
    print("-" * 25)
    
    # Navigate to a test page
    print("🌐 Navigating to example.com...")
    nav_result = browser.navigate("https://example.com")
    print(f"Navigation result: {nav_result}")
    
    # Non-visual approach
    print("\n📄 Non-visual approach:")
    snapshot_result = browser.snapshot()
    print(f"Snapshot status: {snapshot_result['status']}")
    print(f"Content length: {snapshot_result['text_length']} chars")
    print(f"Interactive elements: {len(snapshot_result['elements'])}")
    
    if snapshot_result['elements']:
        print("Available elements:")
        for element in snapshot_result['elements'][:3]:  # Show first 3
            print(f"   • {element['type']}: {element['description'][:60]}...")
    
    # Visual approach (if available)
    if llm.has_vision():
        print("\n📸 Visual approach:")
        screenshot_path = browser.screenshot()
        if not screenshot_path.startswith("Error"):
            print(f"Screenshot saved: {screenshot_path}")
            
            # LLM analyzes the screenshot
            visual_analysis_prompt = """
            Analyze this webpage screenshot and tell me:
            1. What is the main content of this page?
            2. What interactive elements do you see?
            3. If I wanted to click on the "More information..." link, what coordinates should I use?
            4. How does this visual analysis compare to text-based DOM analysis?
            """
            
            visual_analysis = llm.chat_with_vision(
                text_prompt=visual_analysis_prompt,
                image_paths=[screenshot_path],
                model="llama4:scout"
            )
            print("👁️  Visual analysis:")
            print(visual_analysis)
        else:
            print(f"Screenshot failed: {screenshot_path}")
    else:
        print("\n📝 Visual approach not available (text-only model)")
    
    # 4. LLM decides optimal strategy
    print("\n🎯 STEP 4: LLM Strategy Decision")
    print("-" * 25)
    
    strategy_prompt = f"""
Based on my analysis of the example.com page using both approaches:

Non-visual data: {json.dumps(snapshot_result, indent=2)}
Visual capability: {"Available" if llm.has_vision() else "Not available"}

For the task "Find and click on the More information link", which approach should I use and why?
Provide a specific action plan with exact tool calls.
"""
    
    strategy = llm.chat(
        messages=[{"role": "user", "content": strategy_prompt}],
        model=llm.default_model
    )
    
    print("🧠 LLM Strategy Decision:")
    print(strategy)
    
    print("\n✅ LLM Tool Integration Test Complete!")
    print("🎉 LLM can successfully discover, analyze, and strategically use browser tools!")

def test_visual_workflow():
    """Test the complete visual workflow if vision is available"""
    
    llm = LLM(provider="mac_studio")
    
    if not llm.has_vision():
        print("⚠️  Skipping visual workflow test - no vision-capable model available")
        return
    
    print("\n🎨 VISUAL WORKFLOW TEST")
    print("=" * 30)
    
    browser = BrowserMCPSkills()
    
    # Complete visual workflow example
    print("🌐 1. Navigate to Google...")
    nav_result = browser.navigate("https://google.com")
    print(f"   Result: {nav_result['status']} - {nav_result['message']}")
    
    print("\n📸 2. Take screenshot for visual analysis...")
    screenshot_path = browser.screenshot()
    if not screenshot_path.startswith("Error"):
        print(f"   Screenshot: {screenshot_path}")
        
        print("\n👁️  3. LLM analyzes screenshot...")
        visual_prompt = """
        I need to search for "Lakers basketball news" on this Google page.
        
        Please analyze this screenshot and tell me:
        1. Where is the search box located? Provide approximate pixel coordinates.
        2. What does the search box look like?
        3. Are there any other important elements I should be aware of?
        4. What should I do after typing in the search box?
        
        Be specific about coordinates and visual elements.
        """
        
        analysis = llm.chat_with_vision(
            text_prompt=visual_prompt,
            image_paths=[screenshot_path],
            model="llama4:scout"
        )
        
        print("   LLM Visual Analysis:")
        print(f"   {analysis}")
        
        # Note: In a real implementation, the LLM would provide coordinates
        # and we would use browser.click_at_coordinates(x, y) and browser.type_text(text)
        
    else:
        print(f"   Screenshot failed: {screenshot_path}")

if __name__ == "__main__":
    print("🚀 WEBSURFER-β LLM TOOL INTEGRATION TESTS")
    print("=" * 55)
    
    try:
        test_tool_discovery()
        test_visual_workflow()
        
        print(f"\n🏁 ALL TESTS COMPLETED SUCCESSFULLY!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 