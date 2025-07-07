"""
MCP Server Manager for Browser MCP

Manages the lifecycle of the Browser MCP npx server process using asyncio.
"""

import asyncio
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class MCPServerManager:
    """
    Manages the Browser MCP server process lifecycle.
    
    This class handles starting, stopping, and monitoring the Browser MCP
    server process asynchronously.
    """
    
    def __init__(self):
        self.server_process: Optional[asyncio.subprocess.Process] = None
        self.server_ready = False
        
    async def start_server(self) -> bool:
        """
        Start the Browser MCP server process.
        
        Returns:
            bool: True if server started successfully, False otherwise
        """
        if self.server_ready and self.server_process:
            return True
            
        try:
            logger.info("🚀 Starting Browser MCP server...")
            
            # Clean up any existing server
            if self.server_process:
                await self.stop_server()
            
            # Start the Browser MCP server as a subprocess
            self.server_process = await asyncio.create_subprocess_exec(
                'npx', '@browsermcp/mcp@latest',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for server to initialize
            await asyncio.sleep(2)
            
            # Check if process is still running
            if self.server_process.returncode is None:
                logger.info("✅ Browser MCP server started successfully")
                self.server_ready = True
                return True
            else:
                logger.error(f"❌ Browser MCP server failed to start (exit code: {self.server_process.returncode})")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start Browser MCP server: {e}")
            return False
    
    async def stop_server(self) -> None:
        """
        Stop the Browser MCP server process.
        """
        if self.server_process:
            try:
                logger.info("🔚 Stopping Browser MCP server...")
                self.server_process.terminate()
                
                # Wait for process to terminate gracefully
                try:
                    await asyncio.wait_for(self.server_process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Force kill if it doesn't terminate gracefully
                    logger.warning("⚠️  Force killing Browser MCP server...")
                    self.server_process.kill()
                    await self.server_process.wait()
                
                logger.info("✅ Browser MCP server stopped")
                
            except Exception as e:
                logger.error(f"❌ Error stopping Browser MCP server: {e}")
            finally:
                self.server_process = None
                self.server_ready = False
    
    async def is_running(self) -> bool:
        """
        Check if the MCP server is running.
        
        Returns:
            bool: True if server is running, False otherwise
        """
        if not self.server_process:
            return False
            
        # Check if process is still alive
        if self.server_process.returncode is not None:
            self.server_ready = False
            return False
            
        return self.server_ready
    
    async def restart_server(self) -> bool:
        """
        Restart the Browser MCP server.
        
        Returns:
            bool: True if server restarted successfully, False otherwise
        """
        await self.stop_server()
        return await self.start_server()
    
    async def check_prerequisites(self) -> bool:
        """
        Check if Node.js and Browser MCP are available.
        
        Returns:
            bool: True if prerequisites are met, False otherwise
        """
        try:
            # Check Node.js
            proc = await asyncio.create_subprocess_exec(
                'node', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error("❌ Node.js not found")
                return False
                
            node_version = stdout.decode().strip()
            logger.info(f"✅ Node.js found: {node_version}")
            
            # Check if Browser MCP is available
            proc = await asyncio.create_subprocess_exec(
                'npx', '@browsermcp/mcp@latest', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.warning("⚠️  Browser MCP not found, will attempt to use if available")
                logger.info("💡 Install Browser MCP: npm install -g @browsermcp/mcp@latest")
            else:
                logger.info("✅ Browser MCP available")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Prerequisites check failed: {e}")
            logger.error("💡 Make sure Node.js is installed: https://nodejs.org")
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_server()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_server() 