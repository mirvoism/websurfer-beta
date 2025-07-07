"""
MCP Client for Browser MCP

Handles low-level JSON-RPC communication with the MCP server.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Handles JSON-RPC communication with the Browser MCP server.
    
    This class provides low-level methods for sending requests and receiving
    responses from the MCP server process.
    """
    
    def __init__(self, server_process: asyncio.subprocess.Process):
        self.server_process = server_process
        self.timeout = 30  # Default timeout in seconds
        
    async def send_request(self, method: str, params: Optional[Dict] = None) -> Any:
        """
        Send a JSON-RPC request to the MCP server.
        
        Args:
            method (str): The method name to call
            params (dict, optional): Parameters for the method
            
        Returns:
            Any: The result from the server response
            
        Raises:
            Exception: If the server returns an error or communication fails
        """
        if not self.server_process:
            raise Exception("MCP server process not available")
            
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params or {}
        }
        
        logger.debug(f"🔧 Sending MCP request: {method}")
        
        try:
            # Send request
            request_json = json.dumps(request) + '\n'
            self.server_process.stdin.write(request_json.encode())
            await self.server_process.stdin.drain()
            
            # Read response with chunked handling for large responses
            response_data = await self._read_response()
            
            # Parse and validate response
            response = json.loads(response_data)
            
            if 'error' in response:
                raise Exception(f"MCP Error: {response['error']}")
                
            logger.debug(f"✅ MCP request {method} completed successfully")
            return response.get('result')
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse MCP response: {e}")
            raise Exception(f"Invalid JSON response from MCP server: {e}")
        except Exception as e:
            logger.error(f"❌ MCP request {method} failed: {e}")
            raise
    
    async def _read_response(self) -> str:
        """
        Read and assemble the complete JSON response from the server.
        
        This method handles chunked responses and large payloads like screenshots.
        
        Returns:
            str: The complete JSON response as a string
        """
        response_data = b''
        max_attempts = 100  # Prevent infinite loops
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Try to read a chunk of data with timeout
                chunk = await asyncio.wait_for(
                    self.server_process.stdout.read(8192), 
                    timeout=1.0
                )
                
                if not chunk:
                    break
                    
                response_data += chunk
                
                # Try to parse as complete JSON response
                try:
                    response_str = response_data.decode('utf-8').strip()
                    
                    # For very large responses (like screenshots), parse incrementally
                    if len(response_data) > 100000:  # 100KB threshold
                        complete_json = self._extract_complete_json(response_str)
                        if complete_json:
                            return complete_json
                    
                    # Look for complete JSON response (ends with })
                    if response_str.endswith('}') or response_str.endswith('}\n'):
                        # Try to find the start of JSON response
                        lines = response_str.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('{') and line.endswith('}'):
                                try:
                                    # Validate JSON
                                    json.loads(line)
                                    return line
                                except json.JSONDecodeError:
                                    continue
                        
                        # If we can't find a complete JSON line, try parsing the whole thing
                        try:
                            json.loads(response_str)
                            return response_str
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
                        json.loads(line)
                        return line
                    except json.JSONDecodeError:
                        continue
                        
            raise Exception(f"Failed to parse MCP response after {attempt} attempts. Data length: {len(response_data)}")
            
        except UnicodeDecodeError as e:
            raise Exception(f"Failed to decode MCP response: {e}")
    
    def _extract_complete_json(self, response_str: str) -> Optional[str]:
        """
        Extract complete JSON from a large response string.
        
        Args:
            response_str (str): The response string to parse
            
        Returns:
            Optional[str]: The complete JSON string if found, None otherwise
        """
        # Look for JSON response boundaries
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
                    # Validate JSON
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError:
                    pass
        
        return None
    
    async def call_tool(self, tool_name: str, arguments: Optional[Dict] = None) -> Any:
        """
        Call a Browser MCP tool.
        
        Args:
            tool_name (str): Name of the tool to call
            arguments (dict, optional): Arguments for the tool
            
        Returns:
            Any: The result from the tool call
        """
        return await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
    
    def set_timeout(self, timeout: int) -> None:
        """
        Set the timeout for requests.
        
        Args:
            timeout (int): Timeout in seconds
        """
        self.timeout = timeout 