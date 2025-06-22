import logging
import os
import time
import subprocess
import asyncio
import threading
import json
from typing import Optional, Any, Dict

# Import safe screenshot wrapper
from .safe_screenshot_wrapper import process_screenshot

# Configure logging for the module
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class BrowserMCPSkills:
    def __init__(self):
        self.server_process = None
        self.enabled = os.getenv('BROWSER_MCP_ENABLED', 'true').lower() == 'true'
        self.timeout = int(os.getenv('BROWSER_MCP_TIMEOUT', '30'))
        self._loop = None
        self._loop_thread = None
        self._server_ready = False
        
        if self.enabled:
            self._check_prerequisites()
            self._start_background_loop()
    
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
    
    def _start_background_loop(self):
        """Start a background event loop for all Browser MCP operations"""
        if not self.enabled:
            return
            
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_forever()
            finally:
                self._loop.close()
        
        self._loop_thread = threading.Thread(target=run_loop, daemon=True)
        self._loop_thread.start()
        
        # Wait for loop to be ready
        while self._loop is None:
            time.sleep(0.1)
    
    def _cleanup_server(self):
        """Clean up existing server process"""
        if self.server_process:
            try:
                self.server_process.terminate()
                logger.info("🔚 Browser MCP server terminated")
            except:
                pass
            self.server_process = None
            self._server_ready = False
    
    async def _start_mcp_server_async(self):
        """Start Browser MCP server process asynchronously"""
        if self._server_ready and self.server_process:
            return True
            
        try:
            logger.info("🚀 Starting Browser MCP server...")
            
            # Clean up any existing server
            if self.server_process:
                self.server_process.terminate()
                await asyncio.sleep(0.5)
            
            # Start the Browser MCP server as a subprocess
            self.server_process = await asyncio.create_subprocess_exec(
                'npx', '@browsermcp/mcp@latest',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for server to initialize
            await asyncio.sleep(2)
            
            logger.info("✅ Browser MCP server started")
            self._server_ready = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Browser MCP server: {e}")
            return False
    
    async def _send_mcp_request_async(self, method: str, params: Optional[Dict] = None):
        """Send MCP request to server asynchronously"""
        if not self.server_process:
            raise Exception("MCP server not started")
        
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
            
            # Ensure server is running
            if not self._server_ready:
                server_started = await self._start_mcp_server_async()
                if not server_started:
                    raise Exception("Failed to start MCP server")
            
            # Send tool call request
            result = await self._send_mcp_request_async("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            logger.info(f"✅ Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Browser MCP tool '{tool_name}' failed: {e}")
            raise
    
    def _run_in_loop(self, coro):
        """Run coroutine in the background event loop"""
        if not self._loop or not self.enabled:
            raise Exception("Background loop not available")
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=self.timeout)
    
    def _call_mcp_tool(self, tool_name: str, arguments: Optional[Dict] = None):
        """Synchronous wrapper for async MCP tool calls"""
        if not self.enabled:
            raise Exception("Browser MCP is disabled")
        
        return self._run_in_loop(self._call_mcp_tool_async(tool_name, arguments))

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
        """Take screenshot using Browser MCP with safe screenshot processing"""
        logger.info("📸 Taking screenshot")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - using safe screenshot fallback")
            return process_screenshot("Error: Browser MCP disabled")
        
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
                        
                        logger.info(f"✅ Browser MCP screenshot saved: {screenshot_path}")
                        
                        # Process through safe screenshot for LLM optimization
                        logger.info("🔄 Processing through safe screenshot for LLM optimization...")
                        safe_screenshot_path = process_screenshot(screenshot_path)
                        
                        return safe_screenshot_path
            
            logger.warning("⚠️  No screenshot data received from Browser MCP")
            return process_screenshot("Error: No screenshot data")
            
        except Exception as e:
            logger.error(f"❌ Browser MCP screenshot failed: {e}")
            # Fallback to safe screenshot
            return process_screenshot(f"Error: {e}")
    
    def test_connection(self):
        """Test Browser MCP connection"""
        logger.info("🔍 Testing Browser MCP connection...")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP is disabled")
            return False
        
        try:
            # Test with a simple browser action
            logger.info("🔧 Testing basic Browser MCP functionality...")
            
            # Use about:blank for simple test
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
        """Cleanup MCP server process and event loop on destruction"""
        self._cleanup_server()
        if self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)


