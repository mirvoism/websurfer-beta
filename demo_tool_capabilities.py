#!/usr/bin/env python3
"""
Quick demonstration of LLM tool capabilities and structured responses
"""

from skills.browser_mcp_skills import BrowserMCPSkills
from skills.llm_adapter import LLM
import json

def main():
    print("🔧 WEBSURFER-β TOOL CAPABILITIES DEMO")
    print("=" * 45)
    
    # Initialize components
    browser = BrowserMCPSkills()
    llm = LLM(provider="mac_studio")
    
    print(f"🧠 LLM Model: {llm.default_model}")
    print(f"👁️  Vision Capable: {llm.has_vision()}")
    print(f"🌐 Browser MCP: {'Enabled' if browser.enabled else 'Disabled'}")
    
    # 1. Show tool discovery
    print(f"\n📋 TOOL DISCOVERY")
    print("-" * 20)
    capabilities = browser.get_tool_capabilities()
    
    print("Available tool categories:")
    for category, tools in capabilities.items():
        if category != 'recommended_workflows':
            print(f"  {category}: {list(tools.keys())}")
    
    # 2. Show structured responses
    print(f"\n📊 STRUCTURED RESPONSE EXAMPLES")
    print("-" * 35)
    
    # Navigate example
    print("🌐 Navigation Response Structure:")
    nav_result = browser.navigate("https://example.com")
    print(json.dumps(nav_result, indent=2))
    
    # Screenshot example (visual capability)
    if llm.has_vision():
        print(f"\n📸 Screenshot Response (Visual Capability):")
        screenshot_path = browser.screenshot()
        print(f"Screenshot path: {screenshot_path}")
        print(f"LLM can analyze this image for visual navigation")
    
    # Snapshot example (non-visual capability)
    print(f"\n📄 Snapshot Response Structure (Non-Visual):")
    snapshot_result = browser.snapshot()
    # Show structure without full content
    summary = {
        'status': snapshot_result['status'],
        'text_length': snapshot_result['text_length'],
        'element_count': len(snapshot_result['elements']),
        'sample_elements': snapshot_result['elements'][:2] if snapshot_result['elements'] else []
    }
    print(json.dumps(summary, indent=2))
    
    # 3. Show workflow recommendations
    print(f"\n🎯 RECOMMENDED WORKFLOWS FOR LLM")
    print("-" * 35)
    workflows = capabilities['recommended_workflows']
    
    print("Visual Workflow (for vision-capable LLMs):")
    for step in workflows['visual_workflow']:
        print(f"  {step}")
    
    print(f"\nNon-Visual Workflow (for all LLMs):")
    for step in workflows['non_visual_workflow']:
        print(f"  {step}")
    
    print(f"\nHybrid Workflow (adaptive approach):")
    for step in workflows['hybrid_workflow']:
        print(f"  {step}")
    
    # 4. Key advantages
    print(f"\n✅ KEY ADVANTAGES FOR LLM")
    print("-" * 25)
    print("• Structured JSON responses for easy parsing")
    print("• Clear success/error status in all responses")
    print("• Visual + non-visual capabilities available")
    print("• LLM-optimized screenshots (600px max, ~137KB)")
    print("• Element extraction for programmatic interaction")
    print("• Comprehensive tool discovery via get_tool_capabilities()")
    print("• Fallback systems ensure reliability")
    print("• Human-like browsing patterns")
    
    print(f"\n🎉 Demo Complete! LLM has full access to both visual and non-visual browser automation.")

if __name__ == "__main__":
    main() 