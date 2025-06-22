import logging
import os
import time
import subprocess
import asyncio
from typing import Optional, Any, Dict

# Configure logging for the module
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class BrowserMCPSkills:
    def __init__(self):
        self.server_process = None
        self.enabled = os.getenv('BROWSER_MCP_ENABLED', 'true').lower() == 'true'
        self.timeout = int(os.getenv('BROWSER_MCP_TIMEOUT', '30'))
        
        if self.enabled:
            self._check_prerequisites()
    
    def _check_prerequisites(self):
        """Check if Node.js and Browser MCP are available"""
        try:
            # Check Node.js
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise Exception("Node.js not found")
            
            node_version = result.stdout.strip()
            logger.info(f"✅ Node.js found: {node_version}")
            
            # Check if Browser MCP is installed
            result = subprocess.run(['npx', '@browsermcp/mcp@latest', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.warning("⚠️  Browser MCP not found, will attempt to use if available")
            else:
                logger.info(f"✅ Browser MCP available")
            
        except Exception as e:
            logger.error(f"❌ Prerequisites check failed: {e}")
            logger.error("💡 Make sure Node.js is installed: https://nodejs.org")
            logger.error("💡 Install Browser MCP: npm install -g @browsermcp/mcp@latest")
            self.enabled = False
    
    async def _start_mcp_server(self):
        """Start Browser MCP server process"""
        try:
            logger.info("🚀 Starting Browser MCP server...")
            
            # Start the Browser MCP server as a subprocess
            self.server_process = await asyncio.create_subprocess_exec(
                'npx', '@browsermcp/mcp@latest',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info("✅ Browser MCP server started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Browser MCP server: {e}")
            return False
    
    async def _send_mcp_request(self, method: str, params: Optional[Dict] = None):
        """Send MCP request to server"""
        if not self.server_process:
            raise Exception("MCP server not started")
        
        import json
        
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response
        response_line = await self.server_process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        if 'error' in response:
            raise Exception(f"MCP Error: {response['error']}")
        
        return response.get('result')
    
    async def _call_mcp_tool_async(self, tool_name: str, arguments: Optional[Dict] = None):
        """Call Browser MCP tool asynchronously"""
        try:
            arguments = arguments or {}
            logger.info(f"🔧 Calling Browser MCP tool: {tool_name} with args: {arguments}")
            
            # Send tool call request
            result = await self._send_mcp_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            logger.info(f"✅ Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Browser MCP tool '{tool_name}' failed: {e}")
            raise
    
    def _call_mcp_tool(self, tool_name: str, arguments: Optional[Dict] = None):
        """Synchronous wrapper for async MCP tool calls"""
        if not self.enabled:
            raise Exception("Browser MCP is disabled")
        
        return asyncio.run(self._execute_tool(tool_name, arguments))
    
    async def _execute_tool(self, tool_name: str, arguments: Optional[Dict] = None):
        """Execute tool with proper server lifecycle"""
        server_started = False
        try:
            # Start server if not already running
            if not self.server_process:
                server_started = await self._start_mcp_server()
                if not server_started:
                    raise Exception("Failed to start MCP server")
                
                # Wait for server to initialize
                await asyncio.sleep(2)
            
            # Call the tool
            return await self._call_mcp_tool_async(tool_name, arguments)
            
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            raise
        finally:
            # Keep server running for subsequent calls
            pass

    def navigate(self, url: str):
        """Navigate to URL using Browser MCP"""
        logger.info(f"🌐 Navigating to URL: {url}")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot navigate")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            result = self._call_mcp_tool("browser_navigate", {"url": url})
            logger.info(f"✅ Successfully navigated to: {url}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to URL: {e}")
            return {"status": "error", "message": str(e)}

    def open(self, url: str):
        """Alias for navigate - for backward compatibility"""
        return self.navigate(url)

    def click(self, element: str):
        """Click element using Browser MCP"""
        logger.info(f"🖱️  Clicking element: {element}")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot click")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            result = self._call_mcp_tool("browser_click", {"element": element})
            logger.info(f"✅ Successfully clicked: {element}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to click element: {e}")
            return {"status": "error", "message": str(e)}

    def type(self, element: str, text: str):
        """Type text into element using Browser MCP"""
        logger.info(f"⌨️  Typing '{text}' into element: {element}")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot type")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            result = self._call_mcp_tool("browser_type", {
                "element": element,
                "text": text
            })
            logger.info(f"✅ Successfully typed into: {element}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to type text: {e}")
            return {"status": "error", "message": str(e)}

    def hover(self, element: str):
        """Hover over element using Browser MCP"""
        logger.info(f"👆 Hovering over element: {element}")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot hover")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            result = self._call_mcp_tool("browser_hover", {"element": element})
            logger.info(f"✅ Successfully hovered over: {element}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to hover over element: {e}")
            return {"status": "error", "message": str(e)}

    def scroll(self, x: Optional[int] = None, y: Optional[int] = None):
        """Scroll page using Browser MCP"""
        logger.info(f"📜 Scrolling page")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot scroll")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            # Use PageDown key for scrolling (Browser MCP approach)
            result = self._call_mcp_tool("browser_press_key", {"key": "PageDown"})
            logger.info(f"✅ Successfully scrolled page")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to scroll: {e}")
            return {"status": "error", "message": str(e)}

    def wait(self, seconds: float):
        """Wait for specified seconds using Browser MCP"""
        logger.info(f"⏱️  Waiting for {seconds} seconds")
        
        if not self.enabled:
            # Fallback to regular sleep
            time.sleep(seconds)
            logger.info(f"✅ Wait completed (fallback)")
            return {"status": "completed", "method": "fallback"}
        
        try:
            result = self._call_mcp_tool("browser_wait", {"time": seconds})
            logger.info(f"✅ Wait completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to wait: {e}")
            # Fallback to regular sleep
            time.sleep(seconds)
            return {"status": "completed", "method": "fallback", "error": str(e)}

    def snapshot(self):
        """Take DOM snapshot using Browser MCP"""
        logger.info("📄 Taking DOM snapshot")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot take snapshot")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            result = self._call_mcp_tool("browser_snapshot")
            logger.info(f"✅ Successfully took DOM snapshot")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to take snapshot: {e}")
            return {"status": "error", "message": str(e)}

    def extract_text(self, selector: Optional[str] = None):
        """Extract text from page using snapshot"""
        logger.info(f"📄 Extracting text from page")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - using placeholder")
            return "Placeholder text (Browser MCP disabled)"
        
        try:
            # Get page snapshot which includes text content
            snapshot_result = self.snapshot()
            
            if snapshot_result and isinstance(snapshot_result, dict):
                if 'content' in snapshot_result:
                    # Extract text from snapshot content
                    text_content = []
                    content = snapshot_result['content']
                    if isinstance(content, list):
                        for content_item in content:
                            if isinstance(content_item, dict) and content_item.get('type') == 'text':
                                text_content.append(content_item.get('text', ''))
                    
                    extracted_text = '\n'.join(text_content)
                    logger.info(f"✅ Successfully extracted text from page")
                    return extracted_text
            
            return "No text content found in snapshot"
            
        except Exception as e:
            logger.error(f"❌ Failed to extract text: {e}")
            return f"Error extracting text: {e}"

    def screenshot(self):
        """Take screenshot using Browser MCP"""
        logger.info("📸 Taking screenshot")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - using placeholder")
            return "screenshot_placeholder.png"
        
        try:
            result = self._call_mcp_tool("browser_screenshot")
            
            if result and isinstance(result, dict) and 'content' in result:
                # Browser MCP returns screenshot as base64
                content = result['content']
                if isinstance(content, list) and len(content) > 0:
                    screenshot_data = content[0].get('data', '') if isinstance(content[0], dict) else ''
                    
                    if screenshot_data:
                        # Save screenshot to file
                        import base64
                        
                        os.makedirs("screenshots", exist_ok=True)
                        screenshot_name = f"screenshot_{int(time.time())}.png"
                        screenshot_path = os.path.join("screenshots", screenshot_name)
                        
                        # Decode and save
                        if screenshot_data.startswith('data:image'):
                            # Remove data:image/png;base64, prefix
                            screenshot_data = screenshot_data.split(',')[1]
                        
                        with open(screenshot_path, 'wb') as f:
                            f.write(base64.b64decode(screenshot_data))
                        
                        logger.info(f"✅ Screenshot saved: {screenshot_path}")
                        return screenshot_path
            
            logger.warning("⚠️  No screenshot data received")
            return "Error: No screenshot data"
            
        except Exception as e:
            logger.error(f"❌ Failed to take screenshot: {e}")
            return f"Error: {e}"
    
    def test_connection(self):
        """Test Browser MCP connection"""
        logger.info("🔍 Testing Browser MCP connection...")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP is disabled")
            return False
        
        try:
            # Test with a simple browser action
            logger.info("🔧 Testing basic Browser MCP functionality...")
            
            # Try to get a simple page snapshot or status
            result = self.navigate("about:blank")
            
            if result and result.get('status') != 'error':
                logger.info(f"✅ Browser MCP connection successful!")
                logger.info(f"🌐 Chrome browser is responding to MCP commands")
                return True
            else:
                logger.error(f"❌ Browser MCP returned error: {result}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Browser MCP connection failed: {e}")
            logger.error("💡 Make sure:")
            logger.error("   1. Node.js is installed")
            logger.error("   2. Chrome has Browser MCP extension installed") 
            logger.error("   3. Chrome is running")
            logger.error("   4. Install Browser MCP: npm install -g @browsermcp/mcp@latest")
            return False
    
    def __del__(self):
        """Cleanup MCP server process on destruction"""
        if self.server_process:
            try:
                self.server_process.terminate()
                logger.info("🔚 Browser MCP server terminated")
            except:
                pass


