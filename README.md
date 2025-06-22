# WebSurfer-β: Vision-Enhanced Autonomous Web-Surfing Agent

This project implements a **vision-enhanced** autonomous web-surfing agent designed to mimic intelligent human browsing behavior. It can read web pages, take screenshots, analyze visual content, click links, fill forms, wait for content to load, summarize findings, and extract structured data.

## 🔥 Key Features

### **Vision Capabilities (NEW!)**
- **Visual Page Analysis:** Uses llama4:scout vision model to analyze webpage screenshots
- **Visual Navigation:** Identifies clickable elements, forms, and content through visual inspection  
- **Modern Web Support:** Handles complex layouts and dynamic content through visual understanding
- **Screenshot Integration:** Automatic webpage capture and visual processing

### **Core Capabilities**
- **Human-like Browsing:** Obeys rate limits, respects `robots.txt`, and randomizes small pauses to stay human-like
- **Modular Architecture:** Built with Google ADK (Agent Development Kit) principles, orchestrating browsing, memory, and reasoning skills
- **Mac Studio Integration:** Direct connection to local LLM endpoint with 5 available models

## Core Tech Stack
- **Mac Studio LLM Endpoint:** Local Ollama server with vision-capable models
- **Browser MCP:** Chrome extension integration for real browser automation
- **llama4:scout:** Vision-capable language model for visual web analysis
- **Google ADK:** Task/skill orchestration framework

## Agent Architecture
The agent operates with a **vision-enhanced** 5-step workflow:
1. **SetGoal:** Defines the user's query or task
2. **PlanBrowsingPath:** Devises a visual navigation strategy  
3. **IterativeBrowse:** Loops through: open → screenshot → visual analysis → action
4. **SummarizeOrExtract:** Returns findings in JSON or Markdown format
5. **SaveMemory:** Stores useful URLs, screenshots, and takeaways

## Available Models

| Model | Capabilities | Best For |
|-------|-------------|----------|
| **llama4:scout** 🔥 | **Vision + Text** | **Visual web browsing (DEFAULT)** |
| deepseek-r1 | Text + Reasoning | Complex problem solving |
| qwen3:32b | Text | Large context tasks |
| qwen25 | Text | General purpose |
| llama4:maverick | Text | Alternative reasoning |

## Key Design Rules
- **Vision-First:** Uses visual analysis when available for better navigation
- **Mac Studio Native:** Optimized for local LLM endpoint performance
- **Human-like timing:** Randomized delays between actions; throttles concurrent tabs (≤ 3)
- **Ethical / legal:** Checks `robots.txt` before scraping; aborts on disallowed paths
- **Observability:** Logs every skill call (`skill_name`, `url`, `selector`, `ts`) to `agent.log`
- **Memory:** Uses ADK vector memory for visited URLs and high-level notes (∼500 tokens/item)
- **Retry & fallback:** On network error, retries 3 times with exponential backoff

## Quick Start

### 1. Prerequisites
- **Mac Studio** with Ollama server running
- **Chrome browser** with MCP extension installed
- **Python 3.8+**

### 2. Installation
```bash
git clone https://github.com/mirvoism/websurfer-beta.git
cd websurfer-beta
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Mac Studio endpoint (should work as-is)
# OPENAI_API_BASE=https://matiass-mac-studio.tail174e9b.ts.net/v1
# DEFAULT_MODEL=llama4:scout
```

### 4. Test System
```bash
# Test Mac Studio LLM connection
python main.py --test

# Test Chrome Browser MCP connection  
python main.py --test-browser

# Test both systems
python main.py --test-all --debug
```

### 5. Run Vision-Enhanced Agent
```bash
# Simple task with vision
python main.py "analyze this webpage visually and find contact information"

# Complex research task
python main.py "compare the features of the top 3 Python web frameworks by visiting their websites"

# Specific model selection
python main.py "find pricing information" --model llama4:scout
```

## Project Structure
```
.
├── main.py                    # Entry point with vision support
├── skills/
│   ├── __init__.py
│   ├── adk_graph.py          # Vision-enhanced ADK workflow
│   ├── browser_mcp_skills.py # Chrome MCP integration
│   ├── design_rules.py       # Ethical constraints & timing
│   └── llm_adapter.py        # Mac Studio + vision support
├── tests/
│   ├── test_llm_adapter.py
│   └── test_browser_mcp_skills.py
├── .env.example              # Configuration template
├── requirements.txt          # Dependencies
└── README.md
```

## Success Criteria Examples

### **Vision-Enhanced Browsing**
Given the goal *"Find and compare pricing plans on 3 SaaS websites,"* the agent should:
- Navigate to each website and take screenshots
- Visually identify pricing sections and plans
- Extract pricing information through visual analysis
- Compare features in a structured format
- Complete the task in under 5 minutes with visual citations

### **Complex Research Task**
Given the goal *"Research the best React component libraries for 2024,"* the agent should:
- Search and visit 5+ relevant websites
- Visually analyze documentation and feature lists
- Screenshot important sections for reference
- Summarize findings with pros/cons
- Provide recommendations with visual evidence

## Environment Variables

```bash
# Mac Studio LLM Configuration
OPENAI_API_BASE=https://matiass-mac-studio.tail174e9b.ts.net/v1
OPENAI_API_KEY=ollama
DEFAULT_MODEL=llama4:scout

# Browser Configuration  
BROWSER_MCP_ENABLED=true
BROWSER_MCP_TIMEOUT=30

# Agent Behavior
HUMAN_LIKE_DELAYS=true
MAX_RETRIES=3
LOG_LEVEL=INFO
```

## Advanced Usage

### **Debug Mode**
```bash
python main.py "your task" --debug --model llama4:scout
```

### **Vision-Specific Methods**
```python
from skills.llm_adapter import LLM

llm = LLM()
# Check if model has vision
if llm.has_vision():
    response = llm.chat_with_vision(
        text_prompt="What do you see on this webpage?",
        image_paths=["screenshot.png"]
    )
```

## Repository
🔗 **GitHub:** [https://github.com/mirvoism/websurfer-beta](https://github.com/mirvoism/websurfer-beta)

---

**WebSurfer-β** represents the evolution of web automation from text-only to **vision-enhanced intelligent browsing**, powered by Mac Studio's local LLM infrastructure. 🚀👁️


