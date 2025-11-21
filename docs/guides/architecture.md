# Architecture Documentation

## System Overview

The oscilloscope control system is designed with a layered architecture that separates concerns and provides multiple interfaces for different use cases.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Natural    │  │   MCP        │  │   Direct     │      │
│  │   Language   │  │   Client     │  │   Python     │      │
│  │   (Claude)   │  │   (JSON-RPC) │  │   API        │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  │
┌─────────────────────────────────────────────┐│
│         Application Layer                   ││
│  ┌────────────────┐  ┌──────────────────┐  ││
│  │  Agent Layer   │  │   MCP Server     │  ││
│  │  (LangChain)   │  │   (Tools &       │  ││
│  │                │  │    Resources)    │  ││
│  └────────┬───────┘  └────────┬─────────┘  ││
└───────────┼──────────────────┼─────────────┘│
            │                  │              │
            └──────────┬───────┘              │
                       ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Oscilloscope Driver Layer                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  OscilloscopeDriver (PyVISA Wrapper)               │    │
│  │  - Command Generation (SCPI)                       │    │
│  │  - Response Parsing                                │    │
│  │  - Error Handling                                  │    │
│  │  - Data Models (Pydantic)                          │    │
│  └──────────────────────────┬─────────────────────────┘    │
└─────────────────────────────┼──────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Hardware Interface Layer                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PyVISA / NI-VISA                                  │    │
│  │  - USB Communication                               │    │
│  │  - VISA Protocol                                   │    │
│  └──────────────────────────┬─────────────────────────┘    │
└─────────────────────────────┼──────────────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │   Oscilloscope   │
                    │  (Siglent        │
                    │   SDS1202X-E)    │
                    └──────────────────┘
```

## Layer Descriptions

### 1. Hardware Interface Layer (PyVISA)

**Purpose:** Low-level communication with oscilloscope hardware

**Components:**
- PyVISA library
- NI-VISA backend (or PyVISA-py)
- USB communication protocol

**Responsibilities:**
- Establish USB connection
- Send raw SCPI commands
- Receive raw responses
- Handle timeouts and errors

### 2. Driver Layer (`src/oscilloscope/`)

**Purpose:** Abstraction of hardware-specific SCPI commands into Pythonic API

**Components:**

#### `driver.py` - Core Driver
```python
class OscilloscopeDriver:
    - connect() / disconnect()
    - write() / query() / read_raw()
    - configure_channel()
    - configure_timebase()
    - configure_trigger()
    - measure_channel()
    - capture_waveform()
    - auto_setup()
    - get_status()
```

#### `commands.py` - SCPI Command Definitions
- Command templates for all oscilloscope operations
- Parameter value constants (voltage scales, time scales, etc.)
- Command formatting utilities

#### `models.py` - Data Models
```python
- ChannelConfig: Channel settings
- TimebaseConfig: Time base settings
- TriggerConfig: Trigger settings
- Measurements: Measurement results
- WaveformData: Captured waveform
- ScopeStatus: Overall status
```

**Responsibilities:**
- Generate SCPI commands
- Parse SCPI responses
- Type-safe configuration using Pydantic models
- Error handling and validation
- Context manager support

### 3. Application Layer

#### 3a. MCP Server (`src/mcp_server/`)

**Purpose:** Standardized JSON-RPC interface for AI agents and external systems

**Components:**

##### `server.py` - MCP Server
- Implements Model Context Protocol
- Handles client connections
- Routes requests to tools/resources
- Lifecycle management

##### `tools.py` - MCP Tools
Exposes oscilloscope operations as callable tools:
- `set_channel_config` - Configure channels
- `set_timebase` - Configure time base
- `set_trigger` - Configure trigger
- `measure_channel` - Get measurements
- `capture_waveform` - Capture data
- `auto_setup` - Auto configure
- `get_scope_status` - Get status

##### `resources.py` - MCP Resources
Exposes real-time data as queryable resources:
- `scope://status` - Current status
- `scope://channels/{n}/config` - Channel config
- `scope://channels/{n}/measurements` - Real-time measurements
- `scope://waveform/{n}` - Waveform data
- `scope://trigger/status` - Trigger status

**Responsibilities:**
- Provide standardized API
- Enable AI agent integration
- Support external system integration
- Structured data exchange

#### 3b. Agent Layer (`src/agent/`)

**Purpose:** Natural language interface powered by Claude

**Components:**

##### `agent.py` - Oscilloscope Agent
- LangChain agent implementation
- Tool execution
- Natural language processing
- Interactive chat interface

##### `prompts.py` - System Prompts
- System prompt for Claude
- Example interactions
- Command mapping guidance

**Responsibilities:**
- Parse natural language commands
- Map intentions to tool calls
- Provide conversational interface
- Handle multi-step workflows
- Error explanation and recovery

## Data Flow

### Example: Natural Language Command

```
User: "Measure the frequency on channel 1"
  │
  ▼
┌─────────────────────────────────────┐
│ Agent Layer                         │
│ - Parse intent: "measure frequency" │
│ - Extract params: channel=1         │
│ - Select tool: measure_channel      │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ Driver Layer                        │
│ - Generate SCPI: "C1:PAVA? FREQ"    │
│ - Send via PyVISA                   │
│ - Parse response: "1000.0HZ"        │
│ - Return: Measurements(freq=1000.0) │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ PyVISA                              │
│ - USB write: "C1:PAVA? FREQ"        │
│ - USB read: "C1:PAVA FREQ,1000.0HZ" │
└──────────────┬──────────────────────┘
               ▼
         Oscilloscope
         Returns: 1000.0 Hz
               ▲
               │
               ▼
    Response flows back up through layers
               │
               ▼
User receives: "The frequency on channel 1 is 1000.0 Hz"
```

## Design Principles

### 1. Separation of Concerns
- Each layer has a single, well-defined responsibility
- Layers only communicate with adjacent layers
- Changes in one layer don't cascade to others

### 2. Type Safety
- Pydantic models for all data structures
- Type hints throughout codebase
- Runtime validation

### 3. Error Handling
- Errors caught at appropriate layer
- Wrapped in custom exceptions
- Meaningful error messages propagated up

### 4. Extensibility
- Easy to add new commands (add to commands.py)
- Easy to add new tools (add to tools.py)
- Easy to add new resources (add to resources.py)

### 5. Multiple Interfaces
- Direct API for programmatic control
- MCP for standardized integration
- Agent for natural language

### 6. Testability
- Each layer independently testable
- Mock interfaces between layers
- Unit tests for each component

## Configuration

### Environment Variables
```
OSCILLOSCOPE_RESOURCE - VISA resource name
OSCILLOSCOPE_TIMEOUT - Command timeout (ms)
ANTHROPIC_API_KEY - API key for Claude
MCP_SERVER_HOST - MCP server host
MCP_SERVER_PORT - MCP server port
LOG_LEVEL - Logging level
```

### Configuration Files
- `.env` - Environment variables
- `pyproject.toml` - Project metadata and dependencies
- `requirements.txt` - Python dependencies

## Logging

All layers log to a unified logging system:
- DEBUG: Detailed SCPI commands and responses
- INFO: High-level operations
- WARNING: Recoverable issues
- ERROR: Failures requiring attention

## Performance Considerations

1. **Connection Management**
   - Persistent connection (don't reconnect per command)
   - Context managers for cleanup
   - Connection pooling for multi-client scenarios

2. **Data Transfer**
   - Binary format for waveform data
   - Chunked transfers for large datasets
   - Compression where applicable

3. **Caching**
   - Cache static configuration
   - Invalidate on writes
   - Refresh on demand

4. **Async Operations**
   - MCP server uses async/await
   - Non-blocking I/O where possible
   - Parallel measurements on multiple channels

## Security Considerations

1. **Network Security**
   - MCP server should run on localhost
   - Use SSH tunneling for remote access
   - Validate all inputs

2. **API Keys**
   - Never commit API keys
   - Use environment variables
   - Rotate keys regularly

3. **Command Validation**
   - Validate all parameters
   - Range checks on values
   - Prevent command injection

## Future Enhancements

1. **Multi-instrument Support**
   - Support for multiple oscilloscopes
   - Device discovery
   - Load balancing

2. **Advanced Analysis**
   - FFT analysis
   - Protocol decoding
   - Mathematical operations

3. **Data Storage**
   - Save/load waveforms
   - Measurement history
   - Database integration

4. **Web Interface**
   - Real-time web dashboard
   - Remote control
   - Collaborative features

5. **Integration**
   - LabVIEW integration
   - MATLAB integration
   - Jupyter notebook widgets

