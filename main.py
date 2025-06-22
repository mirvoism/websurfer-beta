import os
import argparse
from dotenv import load_dotenv
from skills.llm_adapter import LLM
from skills.browser_mcp_skills import BrowserMCPSkills
from skills.adk_graph import ADKGraph
from skills.design_rules import DesignRules

def main():
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
    args = parser.parse_args()

    # Initialize components with configuration management
    try:
        llm = LLM(provider="mac_studio")
        
        print(f"\n🤖 WebSurfer-β Agent")
        
        if args.debug:
            print(f"🔧 Configuration:")
            config = llm.get_config()
            for key, value in config.items():
                print(f"   {key}: {value}")
        
        # Test connection if requested
        if args.test:
            return 0 if llm.test_connection() else 1
        
        # Require task if not testing
        if not args.task:
            print("❌ Error: Task is required (or use --test to test connection)")
            print("Example: python main.py 'find the best Python tutorials'")
            return 1
        
        browser_skills = BrowserMCPSkills()
        design_rules = DesignRules()
        adk_graph = ADKGraph(llm=llm)
        
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
        adk_graph.run_workflow(args.task, model=model)

        print("\n✅ WebSurfer-β finished successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your .env file is configured correctly (copy from .env.example)")
        return 1

if __name__ == "__main__":
    exit(main())


