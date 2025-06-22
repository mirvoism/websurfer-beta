#!/usr/bin/env python3
"""
Safe Screenshot Wrapper for WebSurfer-β
Integrates safe-screenshot-server with Browser MCP to resize screenshots for LLM processing
"""

import subprocess
import json
import os
import time
import base64
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SafeScreenshotWrapper:
    """
    Wrapper that uses safe-screenshot-server to resize Browser MCP screenshots
    Keeps Browser MCP functionality intact while making screenshots LLM-friendly
    """
    
    def __init__(self):
        self.server_process = None
        self.server_path = Path(__file__).parent / "simple-screenshot-server.js"
        self.enabled = True
        
        # Check if simple-screenshot-server exists
        if not self.server_path.exists():
            logger.warning("⚠️  Simple-screenshot-server not found, will use fallback")
            self.enabled = False
    
    def start_server(self) -> bool:
        """Start the safe-screenshot-server"""
        if not self.enabled:
            return False
            
        try:
            logger.info("🚀 Starting simple-screenshot-server...")
            
            # Start the server
            self.server_process = subprocess.Popen(
                ['node', str(self.server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for server to initialize
            time.sleep(1)
            
            # Check if server is running
            if self.server_process.poll() is None:
                logger.info("✅ Simple-screenshot-server started successfully")
                return True
            else:
                logger.error("❌ Simple-screenshot-server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start simple-screenshot-server: {e}")
            return False
    
    def stop_server(self):
        """Stop the safe-screenshot-server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                logger.info("🔚 Simple-screenshot-server stopped")
            except:
                self.server_process.kill()
            self.server_process = None
    
    def call_server(self, tool_name: str, params: Dict = None) -> Dict:
        """Call the safe-screenshot-server with MCP protocol"""
        if not self.server_process:
            raise Exception("Safe-screenshot-server not running")
        
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params or {}
            }
        }
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.server_process.stdin.write(request_json)
        self.server_process.stdin.flush()
        
        # Read response
        response_line = self.server_process.stdout.readline()
        response = json.loads(response_line.strip())
        
        if 'error' in response:
            raise Exception(f"Server Error: {response['error']}")
        
        return response.get('result', {})
    
    def safe_screenshot_capture(self) -> str:
        """
        Capture screenshot using safe-screenshot-server
        Returns path to saved LLM-optimized screenshot
        """
        try:
            logger.info("📸 Taking safe screenshot (600px max)...")
            
            # Ensure server is running
            if not self.server_process:
                if not self.start_server():
                    raise Exception("Failed to start simple-screenshot-server")
            
            # Call the server
            result = self.call_server("screen_capture_safe")
            
            if result and 'content' in result:
                content = result['content']
                
                # Find the image data
                image_data = None
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'image':
                        image_data = item.get('data')
                        break
                
                if image_data:
                    # Save the resized screenshot
                    os.makedirs("screenshots", exist_ok=True)
                    timestamp = int(time.time())
                    screenshot_path = f"screenshots/safe_screenshot_{timestamp}.png"
                    
                    # Decode and save
                    with open(screenshot_path, 'wb') as f:
                        f.write(base64.b64decode(image_data))
                    
                    logger.info(f"✅ Safe screenshot saved: {screenshot_path}")
                    return screenshot_path
                else:
                    raise Exception("No image data in server response")
            else:
                raise Exception("Invalid server response")
                
        except Exception as e:
            logger.error(f"❌ Safe screenshot failed: {e}")
            return f"Error: {e}"
    
    def process_browser_mcp_screenshot(self, browser_screenshot_result: str) -> str:
        """
        Process Browser MCP screenshot result through safe-screenshot-server
        
        Args:
            browser_screenshot_result: Result from browser.screenshot()
            
        Returns:
            Path to LLM-optimized screenshot
        """
        try:
            # Check if Browser MCP screenshot failed
            if isinstance(browser_screenshot_result, str) and browser_screenshot_result.startswith("Error:"):
                logger.info("🔄 Browser MCP screenshot failed, using safe capture fallback")
                return self.safe_screenshot_capture()
            
            # Check if Browser MCP screenshot succeeded
            if isinstance(browser_screenshot_result, str) and browser_screenshot_result.endswith(".png"):
                logger.info("📸 Browser MCP screenshot succeeded, processing for LLM optimization...")
                
                # For now, if Browser MCP works, we can use safe capture as backup
                # In future, we could resize the Browser MCP image instead
                return self.safe_screenshot_capture()
            
            # Fallback to safe capture
            logger.info("🔄 Using safe screenshot capture")
            return self.safe_screenshot_capture()
            
        except Exception as e:
            logger.error(f"❌ Screenshot processing failed: {e}")
            return f"Error: {e}"
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_server()

# Global instance for easy access
safe_screenshot = SafeScreenshotWrapper()

def get_safe_screenshot() -> str:
    """
    Convenience function to get a safe screenshot
    Returns path to LLM-optimized screenshot (600px max)
    """
    return safe_screenshot.safe_screenshot_capture()

def process_screenshot(browser_result: str) -> str:
    """
    Convenience function to process Browser MCP screenshot
    
    Args:
        browser_result: Result from browser.screenshot()
        
    Returns:
        Path to LLM-optimized screenshot
    """
    return safe_screenshot.process_browser_mcp_screenshot(browser_result)

# Test function
def test_safe_screenshot():
    """Test the safe screenshot functionality"""
    print("🧪 TESTING SAFE SCREENSHOT WRAPPER")
    print("=" * 40)
    
    try:
        # Test direct safe capture
        print("\n📸 Testing direct safe screenshot capture...")
        result = get_safe_screenshot()
        print(f"Result: {result}")
        
        # Test processing a "failed" Browser MCP result
        print("\n🔄 Testing Browser MCP failure processing...")
        failed_result = "Error: Separator is found, but chunk is longer than limit"
        processed = process_screenshot(failed_result)
        print(f"Processed result: {processed}")
        
        print("\n✅ Safe screenshot wrapper test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        safe_screenshot.stop_server()

if __name__ == "__main__":
    test_safe_screenshot() 