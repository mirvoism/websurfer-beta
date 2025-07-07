import os
import argparse
import asyncio
from dotenv import load_dotenv
from skills.llm_adapter import LLM
from skills.browser import Browser
from skills.adk_graph import ADKGraph
from skills.design_rules import DesignRules
from skills.memory import Memory

async def main():
    # Load environment variables first
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="WebSurfer-β: Autonomous Web-Surfing Agent")
    parser.add_argument("task", type=str, nargs='?', help="The task for the agent to perform.")
    parser.add_argument("--model", type=str, default=None,
                        help="LLM model to use (overrides DEFAULT_MODEL from .env)")
    parser.add_argument("--debug", action="store_true",
                        help="Show configuration details")
    parser.add_argument("--test", action="store_true",
                        help="Test Mac Studio LLM connection")
    parser.add_argument("--test-browser", action="store_true",
                        help="Test Browser MCP connection")
    parser.add_argument("--test-all", action="store_true",
                        help="Test both LLM and Browser MCP connections")
    args = parser.parse_args()

    # Initialize components with configuration management
    try:
        llm = LLM(provider="mac_studio")
        memory = Memory()
        browser = Browser(llm=llm, memory=memory)
        
        print(f"\n🤖 WebSurfer-β v2.0 Agent")
        
        if args.debug:
            print(f"🔧 Configuration:")
            config = llm.get_config()
            for key, value in config.items():
                print(f"   {key}: {value}")
        
        # Test connections if requested
        if args.test or args.test_all:
            llm_success = llm.test_connection()
            if not args.test_all:
                return 0 if llm_success else 1
        
        if args.test_browser or args.test_all:
            browser_success = await browser.start()
            if browser_success:
                await browser.stop()
            if args.test_all:
                return 0 if (llm_success and browser_success) else 1
            else:
                return 0 if browser_success else 1
        
        # Require task if not testing
        if not args.task:
            print("❌ Error: Task is required (or use --test/--test-browser/--test-all)")
            print("Example: python main.py 'find the best Python tutorials'")
            print("Testing: python main.py --test-all")
            return 1
        
        design_rules = DesignRules()
        adk_graph = ADKGraph(llm=llm, browser=browser, memory=memory)
        
        print(f"📝 Task: {args.task}")
        
        # Use specified model or default
        model = args.model or llm.default_model
        print(f"🧠 Using model: {model}")
        
        # Validate model is available
        if model not in llm.available_models:
            print(f"❌ Error: Model '{model}' not available")
            print(f"Available models: {llm.available_models}")
            return 1
        
        # Example of using design rules
        design_rules.human_like_pause()
        design_rules.log_skill_call("main_execution", url="startup")

        # Run the ADK workflow
        await adk_graph.run_workflow(args.task, model=model)

        print("\n✅ WebSurfer-β v2.0 finished successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your .env file is configured correctly (copy from .env.example)")
        print("💡 Ensure Chrome has Browser MCP extension installed")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))


