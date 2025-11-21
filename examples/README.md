# Examples

This directory contains example scripts demonstrating different ways to interact with the oscilloscope control system.

## Examples Overview

### 1. `basic_control.py` - Direct Driver Usage

Demonstrates low-level control using the PyVISA driver directly.

```bash
python basic_control.py
```

**What it shows:**
- Connecting to oscilloscope
- Configuring channels (voltage scale, coupling)
- Setting timebase
- Configuring trigger
- Taking measurements

**Use this when:** You need direct, programmatic control with no abstraction.

---

### 2. `mcp_client.py` - MCP Client

Demonstrates using the MCP (Model Context Protocol) server to control the oscilloscope.

```bash
# Terminal 1: Start MCP server
python -m src.mcp_server.server

# Terminal 2: Run client
python mcp_client.py
```

**What it shows:**
- Listing available MCP tools and resources
- Calling tools (configure, measure, etc.)
- Reading resources (status, measurements)

**Use this when:** You want a standardized API for programmatic control or integration with other systems.

---

### 3. `agent_demo.py` - Natural Language Agent

Demonstrates natural language control using Claude as an intelligent agent.

```bash
# Demo mode (predefined commands)
python agent_demo.py

# Interactive mode
python agent_demo.py --interactive
```

**What it shows:**
- Natural language commands → oscilloscope actions
- Context-aware responses
- Interactive conversation

**Example commands:**
- "Measure frequency on channel 1"
- "Set channel 2 to 2V per division"
- "What's the peak-to-peak voltage?"
- "Trigger on rising edge at 1.5 volts"
- "Auto setup the oscilloscope"

**Use this when:** You want intuitive, conversational control without needing to remember exact commands or APIs.

---

## Setup

Before running examples, ensure:

1. **Environment variables are set** (copy `.env.example` to `.env`):
   ```bash
   OSCILLOSCOPE_RESOURCE=USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR
   ANTHROPIC_API_KEY=your_api_key_here
   ```

2. **Dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Oscilloscope is connected** and can be detected by PyVISA:
   ```python
   import pyvisa
   rm = pyvisa.ResourceManager()
   print(rm.list_resources())
   ```

## Comparison

| Feature | Direct Driver | MCP Client | Natural Language Agent |
|---------|--------------|------------|----------------------|
| **Ease of use** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Integration** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Learning curve** | High | Medium | Low |

## Common Workflows

### Quick Measurement
```python
# Direct Driver
from src.oscilloscope.driver import OscilloscopeDriver
scope = OscilloscopeDriver("USB0::...")
scope.connect()
measurements = scope.measure_channel(1)
print(measurements.frequency)

# Natural Language Agent
from src.agent.agent import OscilloscopeAgent
agent = OscilloscopeAgent()
response = agent.execute("What's the frequency on channel 1?")
print(response)
```

### Configuration
```python
# Direct Driver
from src.oscilloscope.models import ChannelConfig, CouplingMode
config = ChannelConfig(channel=1, voltage_div="2V", coupling=CouplingMode.DC_1M)
scope.configure_channel(config)

# Natural Language Agent
agent.execute("Set channel 1 to 2V per division with DC coupling")
```

### Automated Testing
```python
# MCP Client (best for automation)
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Configure
        await session.call_tool("set_channel_config", {"channel": 1, "voltage_div": "1V"})
        # Measure
        result = await session.call_tool("measure_channel", {"channel": 1})
        # Assert expected values
        assert result.frequency > 1000  # Expect > 1kHz
```

## Troubleshooting

### "No oscilloscope found"
- Check USB connection
- Verify resource name with `pyvisa.ResourceManager().list_resources()`
- Ensure NI-VISA or PyVISA-py backend is installed

### "ANTHROPIC_API_KEY not set"
- Copy `.env.example` to `.env`
- Add your Anthropic API key
- Or set environment variable: `export ANTHROPIC_API_KEY=your_key`

### "MCP server connection failed"
- Ensure server is running in separate terminal
- Check port availability (default: 8000)
- Review server logs for errors

## Next Steps

After running these examples:

1. **Modify examples** to match your specific use case
2. **Build custom tools** by extending the MCP server
3. **Create automation scripts** using the driver or MCP client
4. **Integrate with other systems** (LabVIEW, MATLAB, etc.)

For more information, see the main [README.md](../README.md).

