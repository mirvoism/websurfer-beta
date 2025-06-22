import os
import argparse
from skills.llm_adapter import LLM
from skills.browser_mcp_skills import BrowserMCPSkills
from skills.adk_graph import ADKGraph
from skills.design_rules import DesignRules

def main():
    parser = argparse.ArgumentParser(description="Autonomous Web-Surfing Agent")
    parser.add_argument("task", type=str, help="The task for the agent to perform.")
    parser.add_argument("--provider", type=str, default="gemini",
                        help="LLM provider (e.g., gemini, openai, claude)")
    args = parser.parse_args()

    # Initialize components
    llm = LLM(provider=args.provider)
    browser_skills = BrowserMCPSkills()
    design_rules = DesignRules()
    adk_graph = ADKGraph(llm_provider=args.provider)

    print(f"\n--- Starting WebSurfer-β with task: {args.task} ---")
    print(f"Using LLM provider: {args.provider}")

    # Example of using design rules
    design_rules.human_like_pause()
    design_rules.log_skill_call("main_execution", url="startup")

    # Run the ADK workflow
    adk_graph.run_workflow(args.task)

    print("\n--- WebSurfer-β finished. ---")

if __name__ == "__main__":
    main()


