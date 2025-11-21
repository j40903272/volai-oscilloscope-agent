# Quick Start Guide

Get up and running with oscilloscope control in 5 minutes!

## Prerequisites

1. **Hardware:**
   - Siglent SDS1202X-E oscilloscope (or compatible)
   - USB cable connected to your computer

2. **Software:**
   - Python 3.9 or higher
   - NI-VISA or PyVISA-py backend
   - Anthropic API key (for natural language agent)

## Installation

### Step 1: Clone/Download Project

```bash
cd "YUN DA"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your favorite editor
```

Set these values:
```bash
OSCILLOSCOPE_RESOURCE=USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR
ANTHROPIC_API_KEY=your_api_key_here
```

### Step 4: Find Your Oscilloscope

```bash
python -c "import pyvisa; rm = pyvisa.ResourceManager(); print(rm.list_resources())"
```

You should see something like:
```
('ASRL1::INSTR', 'ASRL2::INSTR', 'USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR')
```

The USB device is your oscilloscope! Copy that exact string to your `.env` file.

## 🎯 Usage Options

### Option 1: Natural Language Agent (Easiest!)

**Best for:** Quick measurements, exploratory work, learning

```bash
python examples/agent_demo.py --interactive
```

Then just talk to it:
```
You: Measure frequency on channel 1
Agent: I'll measure the frequency on channel 1 for you.

Channel 1 Measurements:
  Frequency: 1000.00 Hz
  Period: 1.000 ms
  Peak-to-Peak: 5.000 V
  ...
```

### Option 2: Python API (Most Control)

**Best for:** Scripts, automation, custom workflows

```python
from src.oscilloscope.driver import OscilloscopeDriver
from src.oscilloscope.models import ChannelConfig, CouplingMode

# Connect
with OscilloscopeDriver("USB0::...") as scope:
    # Configure
    scope.configure_channel(ChannelConfig(
        channel=1,
        voltage_div="2V",
        coupling=CouplingMode.DC_1M
    ))
    
    # Measure
    measurements = scope.measure_channel(1)
    print(f"Frequency: {measurements.frequency} Hz")
```

See `examples/basic_control.py` for complete example.

### Option 3: MCP Server (Best Integration)

**Best for:** AI agents, external systems, standardized API

**Terminal 1 - Start server:**
```bash
python -m src.mcp_server.server
```

**Terminal 2 - Use client:**
```bash
python examples/mcp_client.py
```

## Common Tasks

### 📊 Take a Measurement

**Natural Language:**
```
You: What's the frequency on channel 1?
```

**Python API:**
```python
measurements = scope.measure_channel(1)
print(measurements.frequency)
```

**MCP:**
```python
result = await session.call_tool("measure_channel", {"channel": 1})
```

### ⚙️ Configure Channel

**Natural Language:**
```
You: Set channel 1 to 2V per division
```

**Python API:**
```python
scope.set_voltage_scale(channel=1, voltage_div="2V")
```

**MCP:**
```python
await session.call_tool("set_channel_config", {
    "channel": 1,
    "voltage_div": "2V"
})
```

### 🔍 Auto Setup

**Natural Language:**
```
You: Auto setup the oscilloscope
```

**Python API:**
```python
scope.auto_setup()
```

**MCP:**
```python
await session.call_tool("auto_setup", {})
```

### 📈 Capture Waveform

**Natural Language:**
```
You: Capture waveform from channel 1
```

**Python API:**
```python
waveform = scope.capture_waveform(channel=1, num_points=1000)
print(waveform.data_points)  # List of voltage values
print(waveform.time_points)  # List of time values
```

**MCP:**
```python
result = await session.call_tool("capture_waveform", {
    "channel": 1,
    "num_points": 1000
})
```

## Troubleshooting

### ❌ "No module named 'pyvisa'"

```bash
pip install pyvisa pyvisa-py
```

### ❌ "Could not open resource"

1. Check USB connection
2. Verify resource name:
   ```bash
   python -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"
   ```
3. Try with PyVISA-py backend:
   ```python
   import pyvisa
   rm = pyvisa.ResourceManager('@py')
   print(rm.list_resources())
   ```

### ❌ "ANTHROPIC_API_KEY not set"

1. Get API key from https://console.anthropic.com/
2. Add to `.env` file:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### ❌ "VI_ERROR_TMO: Timeout expired"

1. Increase timeout in driver initialization:
   ```python
   scope = OscilloscopeDriver("USB0::...", timeout=10000)  # 10 seconds
   ```
2. Check oscilloscope is on and responsive
3. Try manual command:
   ```python
   scope.query("*IDN?")
   ```

### ❌ Measurements return None

1. Check if signal is present
2. Run auto setup first:
   ```python
   scope.auto_setup()
   ```
3. Check trigger is working
4. Verify channel is enabled

## Next Steps

1. **Explore Examples**
   ```bash
   cd examples
   python basic_control.py
   python agent_demo.py
   ```

2. **Read Documentation**
   - `README.md` - Full project overview
   - `ARCHITECTURE.md` - System design
   - `examples/README.md` - Detailed examples

3. **Customize**
   - Modify examples for your use case
   - Add custom tools to MCP server
   - Create automation scripts

4. **Integrate**
   - Connect to your data pipeline
   - Add to test automation
   - Build custom dashboards

## Tips & Tricks

### 💡 Quick Script Template

```python
from src.oscilloscope.driver import OscilloscopeDriver

with OscilloscopeDriver("USB0::...") as scope:
    # Your code here
    scope.auto_setup()
    measurements = scope.measure_channel(1)
    print(measurements)
```

### 💡 Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see all SCPI commands
scope = OscilloscopeDriver("USB0::...")
```

### 💡 Save Measurements

```python
import json

measurements = scope.measure_channel(1)
with open('measurements.json', 'w') as f:
    json.dump(measurements.dict(), f, indent=2)
```

### 💡 Multiple Channels

```python
for ch in [1, 2]:
    m = scope.measure_channel(ch)
    print(f"Channel {ch}: {m.frequency} Hz")
```

## Support

- **Issues:** Check ARCHITECTURE.md for system details
- **Examples:** See examples/ directory
- **Tests:** See tests/ for usage patterns

## Quick Reference Card

| Task | Natural Language | Python API |
|------|-----------------|------------|
| Measure | "Measure frequency on CH1" | `scope.measure_channel(1)` |
| Configure | "Set CH1 to 2V/div" | `scope.set_voltage_scale(1, "2V")` |
| Trigger | "Trigger on rising edge" | `scope.configure_trigger(config)` |
| Timebase | "Set to 1ms per division" | `scope.set_time_scale("1MS")` |
| Auto | "Auto setup" | `scope.auto_setup()` |
| Reset | "Reset scope" | `scope.reset()` |

---

**Ready to go!** Start with the natural language agent for the easiest experience:

```bash
python examples/agent_demo.py --interactive
```

