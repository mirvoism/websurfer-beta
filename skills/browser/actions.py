"""
Browser actions for WebSurfer-β v2.0

This module provides high-level browser actions using the Action class
with intelligent fallback mechanisms and vision-based error recovery.
"""

import asyncio
import base64
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from ..action import Action
from ..safe_screenshot_wrapper import process_screenshot
from .mcp_server_manager import MCPServerManager
from .mcp_client import MCPClient

logger = logging.getLogger(__name__)


class Browser:
    """
    High-level browser automation using Action objects with intelligent fallback.
    
    This class provides async browser actions with:
    - Action object support for structured actions
    - Fallback selector handling
    - Vision-based error recovery
    - Memory integration for learning
    """
    
    def __init__(self, llm=None, memory=None):
        self.server_manager = MCPServerManager()
        self.client = None
        self.llm = llm  # LLM for vision-based recovery
        self.memory = memory  # Memory system for learning
        self.enabled = os.getenv('BROWSER_MCP_ENABLED', 'true').lower() == 'true'
        self.timeout = int(os.getenv('BROWSER_MCP_TIMEOUT', '30'))
        self.current_url = None
        
    async def start(self) -> bool:
        """
        Start the browser MCP server and initialize the client.
        
        Returns:
            bool: True if successfully started, False otherwise
        """
        if not self.enabled:
            logger.warning("⚠️  Browser MCP is disabled")
            return False
            
        # Check prerequisites
        if not await self.server_manager.check_prerequisites():
            return False
            
        # Start server
        if not await self.server_manager.start_server():
            return False
            
        # Initialize client
        self.client = MCPClient(self.server_manager.server_process)
        
        logger.info("✅ Browser initialized successfully")
        return True
    
    async def stop(self) -> None:
        """Stop the browser MCP server."""
        await self.server_manager.stop_server()
        self.client = None
        logger.info("🔚 Browser stopped")
    
    async def navigate(self, action: Action) -> Dict[str, Any]:
        """
        Navigate to a URL using an Action object.
        
        Args:
            action (Action): Navigate action with URL
            
        Returns:
            Dict[str, Any]: Navigation result with page info
        """
        if not action.url:
            return {
                'status': 'error',
                'message': 'No URL provided for navigation'
            }
            
        logger.info(f"🌐 Navigating to: {action.url}")
        
        try:
            result = await self.client.call_tool("browser_navigate", {"url": action.url})
            
            # Update current URL
            self.current_url = action.url
            
            # Extract page information
            page_info = self._extract_page_info(result)
            
            logger.info(f"✅ Successfully navigated to: {action.url}")
            return {
                'status': 'success',
                'url': action.url,
                'title': page_info.get('title', ''),
                'content': page_info.get('content_preview', ''),
                'message': f"Successfully navigated to {action.url}"
            }
            
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return {
                'status': 'error',
                'url': action.url,
                'message': str(e)
            }
    
    async def click(self, action: Action) -> Dict[str, Any]:
        """
        Click on an element using an Action object with intelligent fallback.
        
        Args:
            action (Action): Click action with selector and fallbacks
            
        Returns:
            Dict[str, Any]: Click result
        """
        logger.info(f"🖱️  Attempting to click: {action.description}")
        
        # Try coordinate-based clicking if coordinates are provided
        if action.coordinates:
            return await self._click_at_coordinates(action.coordinates[0], action.coordinates[1])
        
        # Get all selectors to try (including memory-enhanced ones)
        selectors = await self._get_enhanced_selectors(action)
        
        # Try each selector
        for i, selector in enumerate(selectors):
            try:
                logger.info(f"🎯 Trying selector {i+1}/{len(selectors)}: {selector}")
                
                # Try to get element reference first
                element_info = await self._get_element_ref(selector)
                
                if element_info:
                    result = await self.client.call_tool("browser_click", {
                        "element": element_info['type'],
                        "ref": element_info['ref']
                    })
                else:
                    # Fallback to direct selector
                    result = await self.client.call_tool("browser_click", {
                        "element": selector
                    })
                
                # Success! Save to memory and return
                await self._save_successful_selector(action, selector)
                logger.info(f"✅ Successfully clicked: {action.description}")
                return {
                    'status': 'success',
                    'selector': selector,
                    'message': f"Successfully clicked {action.description}"
                }
                
            except Exception as e:
                logger.warning(f"⚠️  Selector {selector} failed: {e}")
                continue
        
        # All selectors failed, try vision-based recovery
        logger.info("🔄 All selectors failed, attempting vision-based recovery...")
        return await self._recover_with_vision(action)
    
    async def type(self, action: Action) -> Dict[str, Any]:
        """
        Type text into an element using an Action object with intelligent fallback.
        
        Args:
            action (Action): Type action with text, selector, and fallbacks
            
        Returns:
            Dict[str, Any]: Type result
        """
        if not action.text_to_type:
            return {
                'status': 'error',
                'message': 'No text provided for typing'
            }
            
        logger.info(f"⌨️  Attempting to type '{action.text_to_type}' into: {action.description}")
        
        # Get all selectors to try
        selectors = await self._get_enhanced_selectors(action)
        
        # Try each selector
        for i, selector in enumerate(selectors):
            try:
                logger.info(f"🎯 Trying selector {i+1}/{len(selectors)}: {selector}")
                
                # Get element reference
                element_info = await self._get_element_ref(selector)
                
                if element_info:
                    # Click first to focus
                    await self.client.call_tool("browser_click", {
                        "element": element_info['type'],
                        "ref": element_info['ref']
                    })
                    
                    # Small delay
                    await asyncio.sleep(0.5)
                    
                    # Type text
                    result = await self.client.call_tool("browser_type", {
                        "element": element_info['type'],
                        "text": action.text_to_type,
                        "ref": element_info['ref'],
                        "submit": False
                    })
                else:
                    # Fallback to direct selector
                    result = await self.client.call_tool("browser_type", {
                        "element": selector,
                        "text": action.text_to_type,
                        "submit": False
                    })
                
                # Success! Save to memory and return
                await self._save_successful_selector(action, selector)
                logger.info(f"✅ Successfully typed into: {action.description}")
                return {
                    'status': 'success',
                    'selector': selector,
                    'text': action.text_to_type,
                    'message': f"Successfully typed into {action.description}"
                }
                
            except Exception as e:
                logger.warning(f"⚠️  Selector {selector} failed: {e}")
                continue
        
        # All selectors failed, try vision-based recovery
        logger.info("🔄 All selectors failed, attempting vision-based recovery...")
        return await self._recover_with_vision(action)
    
    async def screenshot(self) -> str:
        """
        Take a screenshot and return the optimized path.
        
        Returns:
            str: Path to the optimized screenshot
        """
        logger.info("📸 Taking screenshot...")
        
        try:
            result = await self.client.call_tool("browser_screenshot")
            
            if result and isinstance(result, dict) and 'content' in result:
                content = result['content']
                if isinstance(content, list) and len(content) > 0:
                    screenshot_data = content[0].get('data', '') if isinstance(content[0], dict) else ''
                    
                    if screenshot_data:
                        # Save screenshot
                        os.makedirs("screenshots", exist_ok=True)
                        screenshot_name = f"screenshot_{int(time.time())}.png"
                        screenshot_path = os.path.join("screenshots", screenshot_name)
                        
                        # Decode and save
                        if screenshot_data.startswith('data:image'):
                            screenshot_data = screenshot_data.split(',')[1]
                        
                        with open(screenshot_path, 'wb') as f:
                            f.write(base64.b64decode(screenshot_data))
                        
                        logger.info(f"✅ Screenshot saved: {screenshot_path}")
                        
                        # Process for LLM optimization
                        optimized_path = process_screenshot(screenshot_path)
                        return optimized_path
            
            logger.warning("⚠️  No screenshot data received")
            return "Error: No screenshot data"
            
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return f"Error: {str(e)}"
    
    async def snapshot(self) -> Dict[str, Any]:
        """
        Get DOM snapshot with text content and interactive elements.
        
        Returns:
            Dict[str, Any]: DOM snapshot data
        """
        logger.info("📄 Taking DOM snapshot...")
        
        try:
            result = await self.client.call_tool("browser_snapshot")
            
            if result and isinstance(result, dict) and 'content' in result:
                content = result['content'][0]['text'] if result['content'] else ''
                
                # Extract interactive elements
                elements = self._extract_interactive_elements(content)
                
                return {
                    'status': 'success',
                    'content': content,
                    'text_length': len(content),
                    'elements': elements,
                    'message': f"DOM snapshot captured ({len(content)} chars, {len(elements)} elements)"
                }
            
            return {
                'status': 'error',
                'message': 'Failed to capture DOM snapshot'
            }
            
        except Exception as e:
            logger.error(f"❌ Snapshot failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def _recover_with_vision(self, action: Action) -> Dict[str, Any]:
        """
        Attempt to recover from selector failure using vision-based analysis.
        
        Args:
            action (Action): The failed action to recover
            
        Returns:
            Dict[str, Any]: Recovery result
        """
        if not self.llm or not self.llm.has_vision():
            return {
                'status': 'error',
                'message': 'Vision-based recovery not available (no LLM with vision)'
            }
        
        logger.info("👁️  Attempting vision-based recovery...")
        
        try:
            # Take screenshot
            screenshot_path = await self.screenshot()
            
            if screenshot_path.startswith("Error"):
                return {
                    'status': 'error',
                    'message': f'Screenshot failed: {screenshot_path}'
                }
            
            # Create vision prompt
            vision_prompt = f"""
System: You are a CSS selector expert. Based on the user's request and the provided screenshot, return a JSON object with the most likely CSS selector for the described element.

User: I need to find the selector for: "{action.description}".

Respond with JSON in the format: {{"selector": "your-best-guess-selector"}}
"""
            
            # Get LLM analysis
            response = await self.llm.chat_with_vision(
                text_prompt=vision_prompt,
                image_paths=[screenshot_path],
                model=self.llm.default_model
            )
            
            # Parse response
            try:
                response_json = json.loads(response)
                new_selector = response_json.get('selector')
                
                if new_selector:
                    logger.info(f"🔍 Vision recovery suggested selector: {new_selector}")
                    
                    # Add to action and try
                    action.add_fallback_selector(new_selector)
                    
                    # Try the new selector
                    if action.action_type == "click":
                        return await self._try_single_click(action, new_selector)
                    elif action.action_type == "type":
                        return await self._try_single_type(action, new_selector)
                    
                else:
                    return {
                        'status': 'error',
                        'message': 'Vision analysis did not provide a selector'
                    }
                    
            except json.JSONDecodeError:
                return {
                    'status': 'error',
                    'message': 'Failed to parse vision analysis response'
                }
            
        except Exception as e:
            logger.error(f"❌ Vision recovery failed: {e}")
            return {
                'status': 'error',
                'message': f'Vision recovery failed: {str(e)}'
            }
    
    async def _try_single_click(self, action: Action, selector: str) -> Dict[str, Any]:
        """Try clicking with a single selector."""
        try:
            element_info = await self._get_element_ref(selector)
            
            if element_info:
                await self.client.call_tool("browser_click", {
                    "element": element_info['type'],
                    "ref": element_info['ref']
                })
            else:
                await self.client.call_tool("browser_click", {
                    "element": selector
                })
            
            await self._save_successful_selector(action, selector)
            return {
                'status': 'success',
                'selector': selector,
                'message': f"Vision recovery successful for {action.description}",
                'recovery_method': 'vision'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Vision selector failed: {str(e)}'
            }
    
    async def _try_single_type(self, action: Action, selector: str) -> Dict[str, Any]:
        """Try typing with a single selector."""
        try:
            element_info = await self._get_element_ref(selector)
            
            if element_info:
                # Click first
                await self.client.call_tool("browser_click", {
                    "element": element_info['type'],
                    "ref": element_info['ref']
                })
                
                await asyncio.sleep(0.5)
                
                # Type
                await self.client.call_tool("browser_type", {
                    "element": element_info['type'],
                    "text": action.text_to_type,
                    "ref": element_info['ref'],
                    "submit": False
                })
            else:
                await self.client.call_tool("browser_type", {
                    "element": selector,
                    "text": action.text_to_type,
                    "submit": False
                })
            
            await self._save_successful_selector(action, selector)
            return {
                'status': 'success',
                'selector': selector,
                'message': f"Vision recovery successful for {action.description}",
                'recovery_method': 'vision'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Vision selector failed: {str(e)}'
            }
    
    async def _click_at_coordinates(self, x: int, y: int) -> Dict[str, Any]:
        """Click at specific coordinates."""
        try:
            result = await self.client.call_tool("browser_click_coordinates", {
                "x": x,
                "y": y
            })
            
            return {
                'status': 'success',
                'coordinates': [x, y],
                'message': f"Clicked at ({x}, {y})"
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'coordinates': [x, y],
                'message': str(e)
            }
    
    async def _get_enhanced_selectors(self, action: Action) -> List[str]:
        """Get enhanced selectors including memory-based ones."""
        selectors = action.get_all_selectors()
        
        # Add memory-based selectors if available
        if self.memory and self.current_url:
            domain = urlparse(self.current_url).netloc
            known_selector = await self.memory.get_known_selector(domain, action.description)
            if known_selector and known_selector not in selectors:
                selectors.insert(0, known_selector)  # Prioritize known selectors
        
        return selectors
    
    async def _save_successful_selector(self, action: Action, selector: str) -> None:
        """Save successful selector to memory."""
        if self.memory and self.current_url:
            domain = urlparse(self.current_url).netloc
            await self.memory.add_successful_selector(domain, action.description, selector)
    
    async def _get_element_ref(self, selector: str) -> Optional[Dict[str, str]]:
        """Get element reference from DOM snapshot."""
        try:
            snapshot = await self.snapshot()
            if snapshot['status'] == 'success':
                for element in snapshot['elements']:
                    if selector in element.get('description', ''):
                        return {
                            'ref': element['ref'],
                            'type': element['type']
                        }
            return None
        except Exception:
            return None
    
    def _extract_page_info(self, result: Dict) -> Dict[str, str]:
        """Extract page information from MCP result."""
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
    
    def _extract_interactive_elements(self, content: str) -> List[Dict[str, str]]:
        """Extract interactive elements from DOM snapshot."""
        elements = []
        if content:
            lines = content.split('\n')
            for line in lines:
                if '[ref=' in line and any(keyword in line.lower() for keyword in 
                    ['button', 'link', 'input', 'combobox', 'textbox', 'search']):
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
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop() 