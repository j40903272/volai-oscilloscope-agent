"""Example: MCP client for oscilloscope control."""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Demonstrate MCP client usage."""
    
    print("=" * 60)
    print("MCP Client Example")
    print("=" * 60)
    
    # Server parameters - adjust path to your server script
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server.server"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # Initialize
            await session.initialize()
            
            print("\n1. Listing available tools...")
            tools = await session.list_tools()
            print(f"   Found {len(tools.tools)} tools:")
            for tool in tools.tools[:5]:  # Show first 5
                print(f"   - {tool.name}: {tool.description}")
            
            print("\n2. Listing available resources...")
            resources = await session.list_resources()
            print(f"   Found {len(resources.resources)} resources:")
            for resource in resources.resources[:5]:  # Show first 5
                print(f"   - {resource.name} ({resource.uri})")
            
            # Example: Get scope status
            print("\n3. Getting oscilloscope status...")
            status_response = await session.call_tool(
                "get_scope_status",
                arguments={}
            )
            print("   Status:")
            if status_response.content:
                status_data = json.loads(status_response.content[0].text)
                print(f"   Model: {status_data['model']}")
                print(f"   Serial: {status_data['serial_number']}")
                print(f"   Firmware: {status_data['firmware_version']}")
            
            # Example: Configure channel
            print("\n4. Configuring Channel 1...")
            ch1_response = await session.call_tool(
                "set_channel_config",
                arguments={
                    "channel": 1,
                    "voltage_div": "2V",
                    "coupling": "DC_1M"
                }
            )
            print(f"   {ch1_response.content[0].text}")
            
            # Example: Set timebase
            print("\n5. Setting timebase...")
            tb_response = await session.call_tool(
                "set_timebase",
                arguments={
                    "time_div": "500US"
                }
            )
            print(f"   {tb_response.content[0].text}")
            
            # Example: Measure channel
            print("\n6. Measuring Channel 1...")
            measure_response = await session.call_tool(
                "measure_channel",
                arguments={"channel": 1}
            )
            print("   Measurements:")
            if measure_response.content:
                measurements = json.loads(measure_response.content[0].text)
                for key, value in measurements.items():
                    if value is not None:
                        print(f"   - {key}: {value}")
            
            # Example: Read resource
            print("\n7. Reading resource: scope://channels/1/measurements")
            measurements_resource = await session.read_resource(
                "scope://channels/1/measurements"
            )
            print("   Resource data:")
            if measurements_resource.contents:
                data = json.loads(measurements_resource.contents[0].text)
                print(json.dumps(data, indent=4))
            
            print("\n" + "=" * 60)
            print("MCP Client example completed!")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

