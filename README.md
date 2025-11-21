# Oscilloscope Agent & MCP Server

A natural language agent system with MCP (Model Context Protocol) server for controlling and operating Siglent oscilloscopes.

## Architecture

```
┌─────────────────────────────────────┐
│   Natural Language Agent Layer      │
│  (LangChain + Claude or HuggingFace)│
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      MCP Server (JSON-RPC)          │
│  - Tools (control operations)       │
│  - Resources (data retrieval)       │
│  - Prompts (common workflows)       │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│   Oscilloscope Driver Layer         │
│      (PyVISA Wrapper)               │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Hardware: Siglent SDS1202X-E       │
│  via USB (PyVISA/NI-VISA)          │
└─────────────────────────────────────┘
```

## Project Structure

```
.
├── src/
│   ├── oscilloscope/
│   │   ├── __init__.py
│   │   ├── driver.py              # PyVISA oscilloscope driver
│   │   ├── commands.py            # SCPI command constants
│   │   └── models.py              # Data models/schemas
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server.py              # MCP server implementation
│   │   ├── tools.py               # MCP tools definitions
│   │   └── resources.py           # MCP resources definitions
│   └── agent/
│       ├── __init__.py
│       ├── agent.py               # Natural language agent
│       └── prompts.py             # System prompts
├── examples/
│   ├── basic_control.py           # Direct driver usage
│   ├── mcp_client.py              # MCP client example
│   └── agent_demo.py              # Agent usage example
├── tests/
│   ├── test_driver.py
│   ├── test_mcp_server.py
│   └── test_agent.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

## Quick Start

### 1. Direct Driver Usage

```python
from src.oscilloscope.driver import OscilloscopeDriver

scope = OscilloscopeDriver("USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR")
scope.connect()
measurements = scope.measure_channel(1)
print(measurements)
```

### 2. MCP Server

```bash
# Start MCP server
python src/mcp_server/server.py

# In another terminal, use MCP client
python examples/mcp_client.py
```

### 3. Natural Language Agent

#### With Claude (Cloud)
```python
from src.agent.agent import OscilloscopeAgent

agent = OscilloscopeAgent(model_type="claude")
response = agent.execute("Measure the frequency on channel 1")
print(response)
```

#### With HuggingFace (Local) - NEW! 🎉
```python
from src.agent.agent import OscilloscopeAgent

agent = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct"
)
response = agent.execute("Measure the frequency on channel 1")
print(response)
```

**See [docs/getting-started/huggingface-quickstart.md](docs/getting-started/huggingface-quickstart.md) for local model setup!**

## Features

### MCP Server Tools
- `set_channel_config` - Configure channel settings
- `set_timebase` - Configure time base
- `set_trigger` - Configure trigger settings
- `measure_channel` - Get channel measurements
- `capture_waveform` - Capture waveform data
- `auto_setup` - Auto-configure scope
- `save_screenshot` - Save screen capture

### MCP Server Resources
- `scope://status` - Current scope status
- `scope://channels/1/config` - Channel configuration
- `scope://channels/1/measurements` - Real-time measurements
- `scope://waveform/1` - Waveform data

### Natural Language Commands
- "Measure frequency on channel 1"
- "Set channel 1 to 2V per division"
- "Trigger on rising edge at 1.5 volts"
- "Capture waveform from channel 2"
- "What's the peak-to-peak voltage?"
- "Auto-setup the oscilloscope"

## Configuration

Set these in `.env`:

```
OSCILLOSCOPE_RESOURCE=USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR
ANTHROPIC_API_KEY=your_api_key_here  # Required for Claude models
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
```

## AI Model Options

### Claude (Cloud) ☁️
- **Pros**: Highest quality responses, no local resources needed
- **Cons**: Requires API key, costs per request, needs internet
- **Setup**: Set `ANTHROPIC_API_KEY` in `.env`

### HuggingFace (Local) 🏠
- **Pros**: Free, works offline, data stays private
- **Cons**: Requires downloading model (~1-6GB), uses local resources
- **Setup**: See [docs/getting-started/huggingface-quickstart.md](docs/getting-started/huggingface-quickstart.md)
- **Supported Models**: Qwen, Phi-3, Gemma, and more

**Quick Start with Local Models:**
```bash
pip install -r requirements.txt
python test_huggingface_model.py
```

## Documentation

📚 **[Complete Documentation](docs/README.md)**

### Quick Links
- 🚀 **[Quick Start Guide](docs/getting-started/quickstart.md)** - Get started in 5 minutes
- 🌐 **[Web Interface Guide](docs/getting-started/web-interface.md)** - Use the Streamlit web UI
- 🤖 **[HuggingFace Quick Start](docs/getting-started/huggingface-quickstart.md)** - Use local AI models
- 🔌 **[MCP Setup](docs/integrations/mcp-setup.md)** - Integrate with Claude Desktop
- 📖 **[Architecture Guide](docs/guides/architecture.md)** - Understand the system design
- 📋 **[Project Summary](docs/reference/project-summary.md)** - Complete overview

## License

MIT

