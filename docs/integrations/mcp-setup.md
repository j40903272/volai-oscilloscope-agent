# MCP Server Setup Guide

## What is the MCP Server?

The MCP (Model Context Protocol) server exposes your oscilloscope as a set of **tools** and **resources** that AI assistants like Claude can use directly.

## Running the MCP Server

### 1. Start the Server

```bash
cd "/Users/interview/Documents/YUN DA"
make run-server
```

The server will:
- Connect to your oscilloscope (USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR)
- Expose tools for measurements, configuration, etc.
- Expose resources for real-time status
- Wait for MCP client connections via stdio

### 2. Connect from Claude Desktop

To use this with Claude Desktop, add this to your Claude Desktop MCP configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "oscilloscope": {
      "command": "python3",
      "args": [
        "-m",
        "src.mcp_server.server"
      ],
      "cwd": "/Users/interview/Documents/YUN DA",
      "env": {
        "OSCILLOSCOPE_RESOURCE": "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR",
        "OSCILLOSCOPE_TIMEOUT": "10000"
      }
    }
  }
}
```

After adding this configuration:
1. Restart Claude Desktop
2. Claude will automatically connect to your oscilloscope
3. You can ask Claude things like:
   - "Measure the frequency on channel 1"
   - "Set the voltage division to 500mV"
   - "What's the current status of the oscilloscope?"

## Available Tools

When connected via MCP, Claude can use these tools:

### Measurements
- `measure_channel` - Measure frequency, voltage, period on a channel
- `capture_waveform` - Capture raw waveform data

### Configuration
- `configure_channel` - Set voltage division, coupling, probe ratio
- `configure_timebase` - Set time per division
- `configure_trigger` - Set trigger source, mode, level

### Control
- `auto_setup` - Automatically configure scope for best view
- `reset_scope` - Reset to factory defaults
- `run_acquisition` - Start/stop acquisition
- `single_trigger` - Capture single trigger event

### Status
- `get_status` - Get current scope status

## Available Resources

Resources are automatically updated data that Claude can access:

- `oscilloscope://status` - Real-time scope status
- `oscilloscope://channel/1` - Channel 1 configuration
- `oscilloscope://channel/2` - Channel 2 configuration

## Troubleshooting

### Server won't start
```bash
# Check if oscilloscope is connected
make check-device

# Check environment variables
cat .env
```

### Claude Desktop can't connect
1. Make sure the path in `cwd` is correct
2. Check Claude Desktop logs: 
   - macOS: `~/Library/Logs/Claude/mcp*.log`
3. Verify Python can be found: `which python3`

### Permission denied
```bash
# Make sure you're in a virtual environment or have proper permissions
python3 -m pip install -e .
```

## Testing the MCP Server

You can test the MCP server without Claude Desktop using the included test client:

```bash
python3 examples/mcp_client.py
```

This will simulate an MCP client and show you what tools and resources are available.

## Architecture

```
Claude Desktop
    ↓ (JSON-RPC over stdio)
MCP Server
    ↓ (Python imports)
OscilloscopeDriver
    ↓ (PyVISA)
Oscilloscope Hardware
```

The MCP server acts as a bridge between Claude's standardized tool-calling interface and your oscilloscope's SCPI commands.

## When to Use MCP vs Web App

**Use MCP Server (Claude Desktop) when:**
- You want to control oscilloscope through natural conversation with Claude
- You want Claude to have direct access to your hardware
- You prefer desktop app interface
- You want to integrate with other MCP tools

**Use Web App (Streamlit) when:**
- You want a visual dashboard
- You want to see waveform plots
- You want manual controls alongside AI
- You want to download data as CSV
- You prefer browser interface

**You can run both at the same time!** Just:
1. Use the web app for visualization and manual control
2. Use Claude Desktop (MCP) for natural language commands

They both connect to the same oscilloscope via PyVISA.

