
# WebSurfer-β: Autonomous Web-Surfing Agent

This project implements an autonomous web-surfing agent designed to mimic a diligent human researcher. It can read web pages, scroll, click links, fill forms, wait for content to load, summarize findings, and extract structured data.

## Features
- **Human-like Browsing:** Obeys rate limits, respects `robots.txt`, and randomizes small pauses to stay human-like.
- **Modular Architecture:** Built with Google ADK (Agent Development Kit) principles, orchestrating browsing, memory, and reasoning skills.
- **LLM-Agnostic:** Supports multiple LLM providers (Gemini, OpenAI, Claude) via a thin adapter.

## Core Tech Stack
- **Google ADK (Agent Development Kit):** For task/skill orchestration.
- **Browser MCP:** Exposes core browser actions like `open`, `click`, `type`, `scroll`, `wait`, `extract_text`, `screenshot`.
- **LLM Brain:** Integrates with various Large Language Models for reasoning and summarization.

## Agent Architecture
The agent operates based on a defined workflow:
1. **SetGoal:** Defines the user's query or task.
2. **PlanBrowsingPath:** Devises a link-traversal strategy.
3. **IterativeBrowse:** Loops through opening pages, extracting content, and deciding the next action.
4. **SummarizeOrExtract:** Returns findings in JSON or Markdown format.
5. **SaveMemory:** Stores useful URLs and takeaways.

## Key Design Rules
- **LLM-agnostic:** Only LLM-specific code resides in the LLM adapter.
- **Human-like timing:** Randomized delays between actions; throttles concurrent tabs (≤ 3).
- **Ethical / legal:** Checks `robots.txt` before scraping; aborts on disallowed paths.
- **Observability:** Logs every skill call (`skill_name`, `url`, `selector`, `ts`) to `agent.log`.
- **Memory:** Uses ADK vector memory for visited URLs and high-level notes (∼500 tokens/item).
- **Retry & fallback:** On network error, retries 3 times with exponential backoff; escalates to user after 3rd failure.

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Set API Key
Create a `.env` file based on `.env.example` and set your chosen LLM provider's API key.

### 3. Run the Agent
```bash
python main.py "find the three best Rust tutorials"
```

## Project Structure
```
. 
├── main.py
├── skills/
│   ├── __init__.py
│   ├── adk_graph.py
│   ├── browser_mcp_skills.py
│   ├── design_rules.py
│   └── llm_adapter.py
├── README.md
├── .env.example
└── tests/
    ├── __init__.py
    ├── test_llm_adapter.py
    └── test_browser_mcp_skills.py
```

## Success Criteria (Example)
Given the goal “Compare 2025 Mac Studio vs Mac Pro reviews,” the agent should:
- Open at least five credible tech-review sites.
- Extract pros/cons and price tables.
- Produce a bullet-point comparison in under 3 min, with URLs cited.


