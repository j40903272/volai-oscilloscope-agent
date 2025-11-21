# MCP Server Quick Start

## 🎯 What You Can Do

Run your oscilloscope MCP server in **3 ways**:

### 1. Test the MCP Server (Recommended First Step)
```bash
make test-mcp
```
This will:
- Start the MCP server
- Connect to your oscilloscope  
- Run example commands (list tools, measure, configure)
- Show you what's available

### 2. Run MCP Server Standalone
```bash
make run-server
```
This starts the server and waits for connections (from Claude Desktop or other MCP clients).

Press `Ctrl+C` to stop.

### 3. Use with Claude Desktop

Add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oscilloscope": {
      "command": "python3",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/Users/interview/Documents/YUN DA",
      "env": {
        "OSCILLOSCOPE_RESOURCE": "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR"
      }
    }
  }
}
```

Restart Claude Desktop, then ask:
- "What tools do you have for the oscilloscope?"
- "Measure frequency on channel 1"
- "Set voltage to 500mV per division on channel 1"

---

## 📋 Available Tools via MCP

Once connected, Claude (or any MCP client) can use:

| Tool | Description |
|------|-------------|
| `measure_channel` | Measure frequency, voltage, period |
| `set_channel_config` | Configure voltage division, coupling |
| `set_timebase` | Set time per division |
| `auto_setup` | Auto-configure scope |
| `get_scope_status` | Get current status |
| `capture_waveform` | Get raw waveform data |

---

## 🔍 Troubleshooting

**Server won't start:**
```bash
# Check oscilloscope connection first
make check-device
```

**Can't find Python module:**
```bash
# Reinstall package
make install
```

**Claude Desktop can't connect:**
- Check the `cwd` path matches your actual directory
- Look at logs: `~/Library/Logs/Claude/mcp*.log`

---

## 💡 Tips

1. **Test first** with `make test-mcp` before trying Claude Desktop
2. **Only one connection** can use the oscilloscope at a time
3. **Close the web app** if you want to use MCP server (or vice versa)
4. **Check status** anytime with the test command

---

## 🆚 MCP Server vs Web App

**MCP Server:**
- Natural language with Claude Desktop
- Standardized AI tool interface
- Great for automated workflows
- Better for voice/chat control

**Web App (`make run-web`):**
- Visual dashboard with charts
- Download waveforms as CSV
- Manual controls
- Real-time visualization

**Pick what works best for your task!** Both use the same driver underneath.

