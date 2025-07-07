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
    """
    Browser MCP Skills for WebSurfer-β Agent
    
    Provides both VISUAL and NON-VISUAL browser automation capabilities optimized for LLM usage.
    
    VISUAL CAPABILITIES (for vision-enabled LLMs):
    - screenshot(): Get visual snapshots for LLM analysis
    - click_at_coordinates(x, y): Click at specific pixel coordinates identified by LLM
    - Visual workflow: screenshot → LLM analysis → coordinate-based actions
    
    NON-VISUAL CAPABILITIES (for all LLMs):
    - navigate(url): Navigate to websites  
    - snapshot(): Get DOM structure and text content
    - extract_text(): Get readable text from pages
    - Element-based actions using fresh DOM references
    
    HYBRID APPROACH:
    - LLM can choose visual or non-visual methods based on task complexity
    - Visual for complex modern websites, non-visual for simple content extraction
    - Robust fallback systems ensure reliability
    
    All methods return structured results for easy LLM processing.
    """
    
    def __init__(self):
        """Initialize Browser MCP with both visual and non-visual capabilities"""
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
        """Send MCP request to server asynchronously with chunked response handling"""
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
        
        # Read response with chunked handling for large responses
        response_data = b''
        max_attempts = 100  # Prevent infinite loops
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Try to read a chunk of data
                chunk = await asyncio.wait_for(self.server_process.stdout.read(8192), timeout=1.0)
                if not chunk:
                    break
                    
                response_data += chunk
                
                # Try to parse as complete JSON response
                try:
                    response_str = response_data.decode('utf-8').strip()
                    
                    # For very large responses (like screenshots), try to parse incrementally
                    if len(response_data) > 100000:  # 100KB threshold
                        # Look for JSON response boundaries more carefully
                        start_idx = response_str.find('{"jsonrpc"')
                        if start_idx >= 0:
                            # Find the matching closing brace
                            brace_count = 0
                            end_idx = -1
                            in_string = False
                            escape_next = False
                            
                            for i, char in enumerate(response_str[start_idx:], start_idx):
                                if escape_next:
                                    escape_next = False
                                    continue
                                if char == '\\':
                                    escape_next = True
                                    continue
                                if char == '"' and not escape_next:
                                    in_string = not in_string
                                    continue
                                if not in_string:
                                    if char == '{':
                                        brace_count += 1
                                    elif char == '}':
                                        brace_count -= 1
                                        if brace_count == 0:
                                            end_idx = i + 1
                                            break
                            
                            if end_idx > 0:
                                json_str = response_str[start_idx:end_idx]
                                try:
                                    response = json.loads(json_str)
                                    if 'error' in response:
                                        raise Exception(f"MCP Error: {response['error']}")
                                    return response.get('result')
                                except json.JSONDecodeError as e:
                                    logger.debug(f"Large response JSON parse failed: {e}")
                    
                    # Look for complete JSON response (ends with })
                    if response_str.endswith('}') or response_str.endswith('}\n'):
                        # Try to find the start of JSON response
                        lines = response_str.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('{') and line.endswith('}'):
                                try:
                                    response = json.loads(line)
                                    if 'error' in response:
                                        raise Exception(f"MCP Error: {response['error']}")
                                    return response.get('result')
                                except json.JSONDecodeError:
                                    continue
                        
                        # If we can't find a complete JSON line, try parsing the whole thing
                        try:
                            response = json.loads(response_str)
                            if 'error' in response:
                                raise Exception(f"MCP Error: {response['error']}")
                            return response.get('result')
                        except json.JSONDecodeError:
                            pass
                            
                except UnicodeDecodeError:
                    # Continue reading if we have incomplete UTF-8
                    pass
                    
                attempt += 1
                
            except asyncio.TimeoutError:
                # No more data available, try to parse what we have
                break
        
        # Final attempt to parse accumulated data
        try:
            response_str = response_data.decode('utf-8').strip()
            # Try each line separately
            lines = response_str.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('{'):
                    try:
                        response = json.loads(line)
                        if 'error' in response:
                            raise Exception(f"MCP Error: {response['error']}")
                        return response.get('result')
                    except json.JSONDecodeError:
                        continue
                        
            raise Exception(f"Failed to parse MCP response after {attempt} attempts. Data length: {len(response_data)}")
            
        except UnicodeDecodeError as e:
            raise Exception(f"Failed to decode MCP response: {e}")
        except Exception as e:
            raise Exception(f"Failed to parse MCP response: {e}")
    
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

    def navigate(self, url: str) -> dict:
        """
        Navigate to a URL and return page information
        
        Args:
            url (str): The URL to navigate to
            
        Returns:
            dict: {
                'status': 'success'|'error',
                'url': str,  # Final URL after redirects
                'title': str,  # Page title
                'content': str,  # Page content summary
                'message': str  # Human-readable result
            }
            
        LLM Usage:
            - Use this to start browsing or move between pages
            - Check returned URL to confirm navigation worked
            - Use title and content for context about the page
            
        Example:
            result = browser.navigate("https://google.com")
            if result['status'] == 'success':
                print(f"Now on: {result['title']}")
        """
        logger.info(f"🌐 Navigating to URL: {url}")
        
        if not self.enabled:
            return {
                'status': 'disabled',
                'url': url,
                'title': '',
                'content': '',
                'message': 'Browser MCP is disabled'
            }
        
        try:
            result = self._call_mcp_tool("browser_navigate", {"url": url})
            
            # Extract page information from result
            page_info = self._extract_page_info(result)
            
            logger.info(f"✅ Successfully navigated to: {url}")
            return {
                'status': 'success',
                'url': url,
                'title': page_info.get('title', ''),
                'content': page_info.get('content_preview', ''),
                'message': f"Successfully navigated to {url}"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to URL: {e}")
            return {
                'status': 'error',
                'url': url,
                'title': '',
                'content': '',
                'message': str(e)
            }

    def open(self, url: str):
        """Alias for navigate - for backward compatibility"""
        return self.navigate(url)

    def _get_element_ref(self, element_description: str):
        """Get current element reference from fresh DOM snapshot"""
        try:
            # Get fresh snapshot
            snapshot = self.snapshot()
            if not isinstance(snapshot, dict) or 'content' not in snapshot:
                return None
            
            content = snapshot['content'][0]['text'] if snapshot['content'] else ''
            lines = content.split('\n')
            
            # Look for element matching description
            import re
            for line in lines:
                # Match various patterns for the element
                if element_description.lower() in line.lower() and '[ref=' in line:
                    # Extract reference like s1e58 from [ref=s1e58]
                    match = re.search(r'\[ref=([^\]]+)\]', line)
                    if match:
                        ref = match.group(1)
                        # Extract element type (link, button, combobox, etc.)
                        element_match = re.search(r'- (\w+)', line.strip())
                        element_type = element_match.group(1) if element_match else 'element'
                        return {'ref': ref, 'type': element_type, 'line': line.strip()}
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get element reference: {e}")
            return None

    def click(self, element: str):
        """Click element using Browser MCP with fresh element reference"""
        logger.info(f"🖱️  Clicking element: {element}")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot click")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            # Try to get fresh element reference
            element_info = self._get_element_ref(element)
            if element_info:
                logger.info(f"📍 Found element reference: {element_info['ref']} ({element_info['type']})")
                result = self._call_mcp_tool("browser_click", {
                    "element": element_info['type'],
                    "ref": element_info['ref']
                })
            else:
                # Fallback to original approach for CSS selectors
                logger.info(f"⚠️  Using fallback CSS selector approach")
                result = self._call_mcp_tool("browser_click", {"element": element})
            
            logger.info(f"✅ Successfully clicked: {element}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to click element: {e}")
            return {"status": "error", "message": str(e)}

    def type(self, element: str, text: str):
        """Type text into element using Browser MCP with fresh element reference"""
        logger.info(f"⌨️  Typing '{text}' into element: {element}")
        
        if not self.enabled:
            logger.warning("⚠️  Browser MCP disabled - cannot type")
            return {"status": "disabled", "message": "Browser MCP is disabled"}
        
        try:
            # Get fresh element reference
            element_info = self._get_element_ref(element)
            if element_info:
                logger.info(f"📍 Found element reference: {element_info['ref']} ({element_info['type']})")
                
                # First click to focus the element (as user suggested)
                logger.info(f"🖱️  Clicking to focus element first...")
                click_result = self._call_mcp_tool("browser_click", {
                    "element": element_info['type'],
                    "ref": element_info['ref']
                })
                
                # Small delay after click
                import time
                time.sleep(0.5)
                
                # Then type into the focused element
                result = self._call_mcp_tool("browser_type", {
                    "element": element_info['type'],
                    "text": text,
                    "ref": element_info['ref'],
                    "submit": False
                })
            else:
                # Fallback to original approach
                logger.info(f"⚠️  Using fallback CSS selector approach")
                result = self._call_mcp_tool("browser_type", {
                    "element": element,
                    "text": text,
                    "ref": "",
                    "submit": False
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

    def snapshot(self) -> dict:
        """
        Get DOM structure and text content (NON-VISUAL capability)
        
        Returns:
            dict: {
                'status': 'success'|'error',
                'content': str,  # DOM structure in YAML format
                'text_length': int,
                'elements': list,  # Available interactive elements
                'message': str
            }
            
        LLM Usage:
            - Use for text-based analysis and element identification
            - Get structured view of page content and interactive elements
            - Alternative to visual analysis for simple pages
            - Extract element references for non-visual clicking/typing
            
        Example:
            snapshot = browser.snapshot()
            if snapshot['status'] == 'success':
                # LLM can analyze the DOM structure
                elements = snapshot['elements']
                # Find search box in elements list
        """
        logger.info("📄 Taking DOM snapshot")
        
        if not self.enabled:
            return {
                'status': 'disabled',
                'content': '',
                'text_length': 0,
                'elements': [],
                'message': 'Browser MCP is disabled'
            }
        
        try:
            result = self._call_mcp_tool("browser_snapshot")
            
            if result and isinstance(result, dict) and 'content' in result:
                content = result['content'][0]['text'] if result['content'] else ''
                
                # Extract interactive elements
                elements = self._extract_interactive_elements(content)
                
                logger.info(f"✅ Successfully took DOM snapshot")
                return {
                    'status': 'success',
                    'content': content,
                    'text_length': len(content),
                    'elements': elements,
                    'message': f"DOM snapshot captured ({len(content)} chars, {len(elements)} interactive elements)"
                }
            else:
                return {
                    'status': 'error',
                    'content': '',
                    'text_length': 0,
                    'elements': [],
                    'message': 'Failed to capture DOM snapshot'
                }
            
        except Exception as e:
            logger.error(f"❌ Failed to take snapshot: {e}")
            return {
                'status': 'error',
                'content': '',
                'text_length': 0,
                'elements': [],
                'message': str(e)
            }

    def extract_text(self, selector: Optional[str] = None) -> dict:
        """
        Extract readable text content from the page (NON-VISUAL capability)
        
        Args:
            selector (str, optional): CSS selector to extract text from specific element
            
        Returns:
            dict: {
                'status': 'success'|'error',
                'text': str,  # Extracted text content
                'length': int,
                'message': str
            }
            
        LLM Usage:
            - Use for content analysis and information extraction
            - Get clean, readable text without HTML markup
            - Perfect for research, fact-finding, and content summarization
            - Faster than visual analysis for text-heavy pages
            
        Example:
            content = browser.extract_text()
            if content['status'] == 'success':
                # LLM can analyze the text content
                text = content['text']
                # Extract specific information from text
        """
        logger.info(f"📄 Extracting text from page")
        
        if not self.enabled:
            return {
                'status': 'disabled',
                'text': 'Browser MCP disabled',
                'length': 0,
                'message': 'Browser MCP is disabled'
            }
        
        try:
            # Get page snapshot which includes text content
            snapshot_result = self.snapshot()
            
            if snapshot_result['status'] == 'success':
                # Extract text from snapshot content
                text_content = []
                content = snapshot_result['content']
                if content:
                    lines = content.split('\n')
                    for line in lines:
                        # Extract readable text, skip YAML structure
                        if not line.strip().startswith('-') and not line.strip().startswith('```'):
                            clean_line = line.strip()
                            if clean_line and not clean_line.startswith('/url:'):
                                text_content.append(clean_line)
                
                extracted_text = '\n'.join(text_content)
                logger.info(f"✅ Successfully extracted text from page")
                return {
                    'status': 'success',
                    'text': extracted_text,
                    'length': len(extracted_text),
                    'message': f"Extracted {len(extracted_text)} characters of text"
                }
            else:
                return {
                    'status': 'error',
                    'text': '',
                    'length': 0,
                    'message': 'Failed to get page snapshot for text extraction'
                }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract text: {e}")
            return {
                'status': 'error',
                'text': '',
                'length': 0,
                'message': str(e)
            }

    def screenshot(self) -> str:
        """
        Take a screenshot of the current page (VISUAL capability)
        
        Returns:
            str: Path to saved screenshot file, or error message
            
        LLM Usage:
            - Use this for visual analysis of web pages
            - Screenshots are optimized for LLM processing (600px max, ~137KB)
            - Perfect for identifying clickable elements, forms, layouts
            - Combine with click_at_coordinates() for visual navigation
            
        Example:
            screenshot_path = browser.screenshot()
            if not screenshot_path.startswith("Error"):
                # Send to LLM for visual analysis
                analysis = llm.analyze_image(screenshot_path, "Find the search box")
        """
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

    def click_at_coordinates(self, x: int, y: int) -> dict:
        """
        Click at specific pixel coordinates (VISUAL capability)
        
        Args:
            x (int): X coordinate in pixels
            y (int): Y coordinate in pixels
            
        Returns:
            dict: {
                'status': 'success'|'error',
                'coordinates': [x, y],
                'message': str
            }
            
        LLM Usage:
            - Use this after visual analysis of screenshots
            - LLM identifies clickable elements and provides coordinates
            - Most reliable method for complex modern websites
            - Bypasses element reference complexity
            
        Example:
            # After LLM analyzes screenshot and identifies search box at (500, 300)
            result = browser.click_at_coordinates(500, 300)
            if result['status'] == 'success':
                # Now type in the focused field
                browser.type_text("search query")
        """
        logger.info(f"🖱️  Clicking at coordinates: ({x}, {y})")
        
        if not self.enabled:
            return {
                'status': 'disabled',
                'coordinates': [x, y],
                'message': 'Browser MCP is disabled'
            }
        
        try:
            # Use Browser MCP coordinate clicking if available
            # Note: This might need to be implemented based on Browser MCP capabilities
            result = self._call_mcp_tool("browser_click_coordinates", {
                "x": x,
                "y": y
            })
            
            logger.info(f"✅ Successfully clicked at coordinates: ({x}, {y})")
            return {
                'status': 'success',
                'coordinates': [x, y],
                'message': f"Clicked at ({x}, {y})"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to click at coordinates: {e}")
            return {
                'status': 'error',
                'coordinates': [x, y],
                'message': str(e)
            }

    def type_text(self, text: str) -> dict:
        """
        Type text into the currently focused element
        
        Args:
            text (str): Text to type
            
        Returns:
            dict: {
                'status': 'success'|'error',
                'text': str,
                'message': str
            }
            
        LLM Usage:
            - Use after clicking on an input field (click_at_coordinates or click)
            - Works with any focused text input, textarea, or editable element
            - Simpler than element-based typing for visual workflows
            
        Example:
            # After clicking on search box
            result = browser.type_text("Lakers basketball news")
            if result['status'] == 'success':
                # Press Enter or click search button
        """
        logger.info(f"⌨️  Typing text: '{text}'")
        
        if not self.enabled:
            return {
                'status': 'disabled',
                'text': text,
                'message': 'Browser MCP is disabled'
            }
        
        try:
            # Type into currently focused element
            result = self._call_mcp_tool("browser_type_text", {
                "text": text
            })
            
            logger.info(f"✅ Successfully typed text: '{text}'")
            return {
                'status': 'success',
                'text': text,
                'message': f"Typed: {text}"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to type text: {e}")
            return {
                'status': 'error',
                'text': text,
                'message': str(e)
            }

    def get_tool_capabilities(self) -> dict:
        """
        Get information about available tools and their capabilities for LLM
        
        Returns:
            dict: Complete tool schema and capability information
            
        LLM Usage:
            - Call this to understand available browser automation capabilities
            - Get tool schemas, parameters, and usage examples
            - Decide between visual vs non-visual approaches
        """
        return {
            'visual_tools': {
                'screenshot': {
                    'description': 'Take visual snapshot of current page',
                    'returns': 'Path to LLM-optimized image file (600px max)',
                    'use_case': 'Visual analysis, element identification, layout understanding',
                    'best_for': 'Complex modern websites, visual elements, forms'
                },
                'click_at_coordinates': {
                    'description': 'Click at specific pixel coordinates',
                    'parameters': {'x': 'int', 'y': 'int'},
                    'use_case': 'After visual analysis identifies clickable elements',
                    'best_for': 'Precise clicking based on visual analysis'
                },
                'type_text': {
                    'description': 'Type into currently focused element',
                    'parameters': {'text': 'str'},
                    'use_case': 'After clicking on input fields',
                    'best_for': 'Simple text input after visual element selection'
                }
            },
            'non_visual_tools': {
                'navigate': {
                    'description': 'Navigate to URL and get page information',
                    'parameters': {'url': 'str'},
                    'returns': 'Page title, URL, content summary',
                    'best_for': 'Moving between pages, starting browsing sessions'
                },
                'snapshot': {
                    'description': 'Get DOM structure and interactive elements',
                    'returns': 'YAML DOM structure, element list with references',
                    'best_for': 'Understanding page structure, finding elements'
                },
                'extract_text': {
                    'description': 'Get clean readable text content',
                    'returns': 'Plain text content without markup',
                    'best_for': 'Content analysis, research, fact extraction'
                },
                'click': {
                    'description': 'Click element using description or CSS selector',
                    'parameters': {'element': 'str (description or selector)'},
                    'best_for': 'Clicking known elements when visual analysis not needed'
                },
                'type': {
                    'description': 'Type into specific element (auto-clicks first)',
                    'parameters': {'element': 'str', 'text': 'str'},
                    'best_for': 'Form filling when element can be described'
                }
            },
            'utility_tools': {
                'scroll': {
                    'description': 'Scroll page down',
                    'best_for': 'Revealing more content, pagination'
                },
                'wait': {
                    'description': 'Wait for specified seconds',
                    'parameters': {'seconds': 'float'},
                    'best_for': 'Waiting for page loads, animations'
                },
                'hover': {
                    'description': 'Hover over element to reveal dropdowns/tooltips',
                    'parameters': {'element': 'str'},
                    'best_for': 'Revealing hidden navigation, tooltips'
                }
            },
            'recommended_workflows': {
                'visual_workflow': [
                    '1. navigate(url) - Go to target page',
                    '2. screenshot() - Get visual snapshot',
                    '3. LLM analyzes image and identifies elements',
                    '4. click_at_coordinates(x, y) - Click identified elements',
                    '5. type_text(text) - Type into focused fields',
                    '6. Repeat steps 2-5 as needed'
                ],
                'non_visual_workflow': [
                    '1. navigate(url) - Go to target page',
                    '2. snapshot() or extract_text() - Get page content',
                    '3. LLM analyzes text/DOM structure',
                    '4. click(element) or type(element, text) - Interact with elements',
                    '5. Repeat steps 2-4 as needed'
                ],
                'hybrid_workflow': [
                    '1. Start with non-visual tools for simple navigation',
                    '2. Switch to visual tools for complex interactions',
                    '3. Use visual analysis when non-visual methods fail',
                    '4. Combine both approaches for maximum reliability'
                ]
            }
        }

    def _extract_page_info(self, result) -> dict:
        """Extract page information from Browser MCP result"""
        # Implementation to parse page info from result
        info = {}
        if isinstance(result, dict) and 'content' in result:
            content = result['content'][0]['text'] if result['content'] else ''
            lines = content.split('\n')
            for line in lines:
                if 'Page URL:' in line:
                    info['url'] = line.split('Page URL:')[1].strip()
                elif 'Page Title:' in line:
                    info['title'] = line.split('Page Title:')[1].strip()
            info['content_preview'] = content[:200] + '...' if len(content) > 200 else content
        return info

    def _extract_interactive_elements(self, content: str) -> list:
        """Extract interactive elements from DOM snapshot"""
        elements = []
        if content:
            lines = content.split('\n')
            for line in lines:
                if '[ref=' in line and any(keyword in line.lower() for keyword in 
                    ['button', 'link', 'input', 'combobox', 'textbox', 'search']):
                    # Extract element info
                    import re
                    ref_match = re.search(r'\[ref=([^\]]+)\]', line)
                    if ref_match:
                        ref = ref_match.group(1)
                        element_type = line.split()[1] if len(line.split()) > 1 else 'element'
                        elements.append({
                            'ref': ref,
                            'type': element_type,
                            'description': line.strip()
                        })
        return elements

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


