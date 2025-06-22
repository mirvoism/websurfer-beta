# WebSurfer-β 🌐🤖

An **autonomous web-surfing agent** powered by Mac Studio LLM integration and **vision-capable AI** for intelligent web browsing and research.

## ✨ **New: Vision-Enhanced Web Browsing**

WebSurfer-β now features **visual intelligence** powered by `llama4:scout` with vision capabilities:
- 📷 **Screenshots with AI Analysis**: Captures and analyzes webpage visuals
- 🔍 **Visual Element Recognition**: Identifies buttons, forms, and interactive elements
- 🎯 **Smart Visual Navigation**: Makes decisions based on what it "sees"
- 📊 **Visual Content Extraction**: Analyzes charts, images, and visual layouts

## 🚀 **Features**

- **🧠 Mac Studio Integration**: Uses local LLM endpoint with 5 powerful models
- **👁️ Vision-Capable AI**: llama4:scout with image analysis capabilities
- **🌐 Real Chrome Browser Control**: Browser MCP integration for actual web browsing
- **🏃‍♂️ ADK Workflow**: 5-step autonomous research process
- **🔒 Privacy-First**: All processing happens locally on your Mac Studio
- **⚡ High Performance**: No API limits, runs on your hardware

## 🛠️ **Setup Instructions**

### **Prerequisites**

1. **Node.js** (required for Browser MCP)
   ```bash
   # Check if installed
   node --version
   
   # If not installed, download from https://nodejs.org
   ```

2. **Mac Studio with Ollama** (your local LLM endpoint)
3. **Chrome Browser** with Browser MCP extension

### **Installation**

#### **Step 1: Install Browser MCP Server**
```bash
# Install Browser MCP globally
npm install -g @browsermcp/mcp@latest

# Verify installation
npx @browsermcp/mcp@latest --version
```

#### **Step 2: Install Chrome Browser MCP Extension**
1. Visit [Browser MCP Chrome Extension](https://browsermcp.io/setup-extension)
2. Install the extension in Chrome
3. Enable the extension and grant permissions

#### **Step 3: Setup Python Environment**
```bash
# Clone and setup project
git clone https://github.com/mirvoism/websurfer-beta.git
cd websurfer-beta/web_surfing_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install Python dependencies
pip install -r requirements.txt
```

#### **Step 4: Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Mac Studio endpoint
nano .env
```

### **Configuration**

Update your `.env` file:

```env
# Mac Studio LLM Configuration
MAC_STUDIO_ENDPOINT=https://matiass-mac-studio.tail174e9b.ts.net/v1
MAC_STUDIO_API_KEY=ollama
LLM_MODEL=llama4:scout  # Vision-capable model
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.1

# Browser MCP Configuration
BROWSER_MCP_ENABLED=true
BROWSER_MCP_TIMEOUT=30

# Debug Configuration
DEBUG_MODE=false
TEST_MODE=false
```

## 🎯 **Available Models**

| Model | Capabilities | Best For |
|-------|-------------|----------|
| `llama4:scout` | **Vision + Text** | 📷 Visual browsing, screenshots |
| `llama4:maverick` | Text reasoning | 🧠 Complex analysis |
| `deepseek-r1` | Advanced reasoning | 🔬 Research tasks |
| `qwen3:32b` | Large context | 📚 Long documents |
| `qwen25` | General purpose | ⚡ Fast responses |

## 🏃‍♂️ **Usage**

### **Basic Usage**
```bash
# Run the agent
python main.py

# Example task
python main.py --task "Research the top 3 Python web frameworks, visit their websites, take screenshots, and create a detailed comparison"
```

### **Vision-Enhanced Browsing**
```bash
# Enable vision mode (default with llama4:scout)
python main.py --vision --task "Analyze the visual design of Apple's website and compare it to Microsoft's"
```

### **Debug Mode**
```bash
# See detailed logs and save screenshots
python main.py --debug --task "Navigate to GitHub and find trending Python repositories"
```

## 🔧 **Testing**

```bash
# Test Mac Studio connection
python -c "from skills.llm_adapter import LLMAdapter; adapter = LLMAdapter(); adapter.test_connection()"

# Test Browser MCP connection
python -c "from skills.browser_mcp_skills import BrowserMCPSkills; browser = BrowserMCPSkills(); browser.test_connection()"

# Full system test
python main.py --test
```

## 🏗️ **Architecture**

### **ADK Workflow (Autonomous Decision-making + Knowledge)**
1. **SetGoal**: Analyze and set research objectives
2. **PlanBrowsingPath**: Create navigation strategy
3. **IterativeBrowse**: Navigate with **vision analysis**
4. **SummarizeOrExtract**: Process and analyze content
5. **SaveMemory**: Store results and insights

### **Vision-Enhanced Browsing Flow**
```
Navigate → Screenshot → Vision Analysis → Decision → Action
```

### **Components**
- **LLM Adapter**: Mac Studio integration with 5 models
- **Browser MCP Skills**: Real Chrome browser control
- **ADK Graph**: Autonomous workflow engine
- **Vision System**: Image analysis with llama4:scout

## 🌐 **Browser MCP Integration**

This project uses the official [Browser MCP](https://github.com/BrowserMCP/mcp) for real browser control:

- **Real Chrome Browser**: Uses your actual Chrome profile
- **Stealth Mode**: Avoids bot detection
- **Logged-in Sessions**: Maintains your authentication
- **Local Processing**: No remote browser automation

### **Available Browser Actions**
- `navigate(url)` - Navigate to URL
- `click(element)` - Click elements
- `type(element, text)` - Type text
- `hover(element)` - Hover over elements
- `screenshot()` - Take screenshots
- `snapshot()` - Get DOM snapshot
- `extract_text()` - Extract page text

## 🔍 **Troubleshooting**

### **Browser MCP Issues**
```bash
# Check Node.js installation
node --version

# Reinstall Browser MCP
npm uninstall -g @browsermcp/mcp
npm install -g @browsermcp/mcp@latest

# Check Chrome extension
# Visit chrome://extensions/ and ensure Browser MCP is enabled
```

### **Mac Studio Connection Issues**
```bash
# Test endpoint directly
curl https://matiass-mac-studio.tail174e9b.ts.net/v1/models

# Check if models are loaded
python -c "from skills.llm_adapter import LLMAdapter; adapter = LLMAdapter(); print(adapter.list_models())"
```

### **Vision Issues**
```bash
# Test vision capabilities
python -c "from skills.llm_adapter import LLMAdapter; adapter = LLMAdapter(); print(f'Vision enabled: {adapter.has_vision()}')"
```

## 📊 **Performance**

- **Vision Analysis**: ~2-3 seconds per screenshot
- **LLM Response**: ~1-2 seconds (local processing)
- **Browser Action**: ~500ms per action
- **Memory Usage**: ~2GB for full workflow

## 🔐 **Security**

- **Local Processing**: All AI processing on Mac Studio
- **No API Keys**: No external API calls required
- **Browser Isolation**: Uses your existing Chrome profile safely
- **Environment Isolation**: Credentials in `.env` file only

## 🌟 **Advanced Features**

### **Custom Research Workflows**
```bash
# Multi-step research with vision
python main.py --task "Research and visually analyze the design trends of top 5 SaaS landing pages, take screenshots, and create a design comparison report"

# Technical analysis with code extraction
python main.py --task "Find and analyze the GitHub repositories of popular Python web frameworks, extract code examples, and create technical documentation"
```

### **Batch Processing**
```bash
# Process multiple tasks
python main.py --batch tasks.json
```

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Credits**

- **Browser MCP**: [BrowserMCP/mcp](https://github.com/BrowserMCP/mcp)
- **Ollama**: Local LLM inference
- **Mac Studio**: High-performance local AI processing

---

**WebSurfer-β v1.0** - Autonomous Web Research with Vision Intelligence 🌐👁️🤖


