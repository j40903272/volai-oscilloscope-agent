"""MCP server implementation for oscilloscope control."""

import asyncio
import logging
import os
from typing import Any
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    Resource,
    TextContent,
    ResourceContents,
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
)

from ..oscilloscope.driver import OscilloscopeDriver, OscilloscopeError
from .tools import OscilloscopeTools
from .resources import OscilloscopeResources


# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OscilloscopeMCPServer:
    """MCP server for oscilloscope control."""
    
    def __init__(self, resource_name: str = None):
        """
        Initialize MCP server.
        
        Args:
            resource_name: VISA resource name for oscilloscope
        """
        self.resource_name = resource_name or os.getenv(
            "OSCILLOSCOPE_RESOURCE",
            "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR"
        )
        self.timeout = int(os.getenv("OSCILLOSCOPE_TIMEOUT", "5000"))
        
        # Initialize driver
        self.driver = OscilloscopeDriver(self.resource_name, self.timeout)
        
        # Initialize tools and resources
        self.tools_handler = OscilloscopeTools(self.driver)
        self.resources_handler = OscilloscopeResources(self.driver)
        
        # Create MCP server
        self.server = Server("oscilloscope-server")
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP server handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            logger.info("Listing tools")
            return self.tools_handler.get_tools()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute a tool."""
            logger.info(f"Calling tool: {name} with args: {arguments}")
            return await self.tools_handler.execute_tool(name, arguments)
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources."""
            logger.info("Listing resources")
            return self.resources_handler.get_resources()
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> ResourceContents:
            """Read a resource."""
            logger.info(f"Reading resource: {uri}")
            return await self.resources_handler.read_resource(uri)
    
    async def run(self):
        """Run the MCP server."""
        try:
            # Connect to oscilloscope
            logger.info(f"Connecting to oscilloscope: {self.resource_name}")
            self.driver.connect()
            logger.info("Oscilloscope connected successfully")
            
            # Run server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server started")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except OscilloscopeError as e:
            logger.error(f"Oscilloscope error: {e}")
            raise
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            # Cleanup
            logger.info("Shutting down server")
            self.driver.disconnect()


def main():
    """Main entry point for MCP server."""
    server = OscilloscopeMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise


if __name__ == "__main__":
    main()

