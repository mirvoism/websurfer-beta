from skills.browser_mcp_skills import BrowserMCPSkills

class ADKGraph:
    def __init__(self, llm):
        self.llm = llm  # Accept LLM instance instead of provider string
        self.browser = BrowserMCPSkills()
        self.system_prompt = """
You are WebSurfer-β, an autonomous web-surfing agent powered by Mac Studio LLM with VISION capabilities.

Your workflow:
1. Think → 2. Plan skills → 3. Call skills → 4. Reflect.

For vision-capable models:
- Take screenshots of web pages for visual analysis
- Identify clickable elements, forms, and content visually
- Navigate based on visual understanding of page layout

Always:
- Imitate cautious human browsing
- Random sleep 1-4s between actions
- Respect robots.txt and rate limits
- Log all actions for audit trail
- Use vision when available for better navigation
"""
        self.workflow = [
            "SetGoal",            # Parse and understand user's task
            "PlanBrowsingPath",   # Devise link-traversal strategy
            "IterativeBrowse",    # Loop: (open → screenshot → analyze → decide next)
            "SummarizeOrExtract", # Return findings in JSON or markdown
            "SaveMemory"          # Store useful URLs & takeaways
        ]

    def run_workflow(self, initial_task, model=None):
        """Run the complete ADK workflow with specified model"""
        model = model or self.llm.default_model
        
        print(f"🚀 Running ADK workflow for task: {initial_task}")
        print(f"🧠 Model: {model}")
        
        if self.llm.has_vision(model):
            print(f"👁️  Vision mode: ENABLED - Using visual web browsing")
        else:
            print(f"📝 Vision mode: DISABLED - Using text-only browsing")
        
        # This is a simplified representation of the workflow execution.
        # In a real ADK, this would involve a more complex planner and executor.
        for step in self.workflow:
            print(f"\n📋 Executing step: {step}")
            
            if step == "SetGoal":
                print(f"🎯 Goal set: {initial_task}")
                
            elif step == "PlanBrowsingPath":
                print("🗺️  Planning browsing path...")
                # Use LLM to plan the browsing strategy
                plan_prompt = f"""
Plan a web browsing strategy for: {initial_task}

{"Since I have vision capabilities, I can:" if self.llm.has_vision(model) else "As a text-only model, I will:"}
{"- Take screenshots and analyze page layouts visually" if self.llm.has_vision(model) else "- Focus on text extraction and semantic analysis"}  
{"- Identify clickable elements through visual inspection" if self.llm.has_vision(model) else "- Use CSS selectors and DOM structure"}
{"- Navigate complex modern websites effectively" if self.llm.has_vision(model) else "- Work with accessible text content"}

Provide a step-by-step plan including specific websites to visit and actions to take.
"""
                response = self.llm.chat(
                    messages=[{"role": "user", "content": plan_prompt}],
                    model=model
                )
                print(f"💭 LLM Plan: {response}")
                
            elif step == "IterativeBrowse":
                print("🌐 Iteratively browsing with vision...")
                
                # Example of using browser skills with vision
                print("📄 Opening example page...")
                self.browser.open("https://example.com")
                
                if self.llm.has_vision(model):
                    # Take screenshot for visual analysis
                    print("📸 Taking screenshot for visual analysis...")
                    screenshot_path = self.browser.screenshot()
                    
                    # Analyze page visually
                    visual_prompt = f"""
I'm browsing for: {initial_task}

Please analyze this webpage screenshot and tell me:
1. What is the main content of this page?
2. What clickable elements do you see?
3. Are there any forms, search boxes, or navigation elements?
4. How should I proceed with my task based on what you see?

Be specific about what you observe visually.
"""
                    
                    if screenshot_path and not screenshot_path.startswith("Error"):
                        visual_analysis = self.llm.chat_with_vision(
                            text_prompt=visual_prompt,
                            image_paths=[screenshot_path],
                            model=model
                        )
                        print(f"👁️  Visual Analysis: {visual_analysis}")
                    else:
                        print(f"⚠️  Screenshot failed: {screenshot_path}")
                        
                else:
                    # Fallback to text extraction
                    content = self.browser.extract_text("body")
                    print(f"📄 Extracted: {content}")
                
            elif step == "SummarizeOrExtract":
                print("📊 Summarizing findings...")
                summary_prompt = f"""
Summarize my browsing session for the task: {initial_task}

{"I used vision capabilities to analyze webpage screenshots and navigate visually." if self.llm.has_vision(model) else "I used text extraction to analyze webpage content."}

Provide a comprehensive summary of what was found and accomplished.
"""
                summary = self.llm.chat(
                    messages=[{"role": "user", "content": summary_prompt}],
                    model=model
                )
                print(f"📝 Summary: {summary}")
                
            elif step == "SaveMemory":
                print("💾 Saving to memory...")
                # Future: implement actual memory storage with screenshots if vision enabled
                
        print(f"\n🎉 ADK workflow completed with {'vision-enhanced' if self.llm.has_vision(model) else 'text-only'} browsing!")


