"""Natural language agent for oscilloscope control."""

import os
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from anthropic import Anthropic
from langchain.agents import AgentExecutor, create_react_agent, initialize_agent, AgentType
from langchain.tools import StructuredTool, Tool
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import PromptTemplate

from ..oscilloscope.driver import OscilloscopeDriver, OscilloscopeError
from ..oscilloscope.models import ChannelConfig, TimebaseConfig, TriggerConfig
from .prompts import get_system_prompt
from .llm_wrapper import create_llm, ModelType


# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class OscilloscopeAgent:
    """Natural language agent for oscilloscope control."""
    
    def __init__(
        self,
        resource_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "claude-haiku-4-5-20251001",
        model_type: str = "claude",
        hf_model_name: Optional[str] = None,
        connect_on_init: bool = True
    ):
        """
        Initialize oscilloscope agent.
        
        Args:
            resource_name: VISA resource name for oscilloscope
            api_key: Anthropic API key (for Claude models)
            model: Claude model to use (if model_type="claude")
            model_type: Type of model - "claude" or "huggingface"
            hf_model_name: HuggingFace model name (if model_type="huggingface")
            connect_on_init: Whether to connect to oscilloscope on initialization
        """
        # Setup oscilloscope driver
        self.resource_name = resource_name or os.getenv(
            "OSCILLOSCOPE_RESOURCE",
            "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR"
        )
        self.driver = OscilloscopeDriver(self.resource_name)
        self.connect_on_init = connect_on_init
        self.model_type = model_type
        self.model = model  # Store model name for vision API
        
        # Setup LLM based on type
        if model_type.lower() == "claude":
            # Setup Claude
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY must be set for Claude models")
            
            logger.info(f"Initializing agent with Claude model: {model}")
            self.llm = create_llm(
                model_type="claude",
                model_name=model,
                api_key=self.api_key,
                temperature=0
            )
        elif model_type.lower() == "huggingface":
            # Setup HuggingFace
            if not hf_model_name:
                hf_model_name = "Qwen/Qwen3-0.6B"
            
            logger.info(f"Initializing agent with HuggingFace model: {hf_model_name}")
            self.llm = create_llm(
                model_type="huggingface",
                model_name=hf_model_name,
                max_new_tokens=512,
                temperature=0.1  # Lower temperature for more deterministic outputs
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}. Must be 'claude' or 'huggingface'")
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent using initialize_agent 
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate",
            agent_kwargs={
                "prefix": get_system_prompt() + "\n\nYou MUST use the tools to get actual results. Do not make up measurements."
            }
        )
        
        # Connect to oscilloscope (if requested)
        if self.connect_on_init:
            self._connect()
    
    def _connect(self):
        """Connect to oscilloscope."""
        try:
            self.driver.connect()
            logger.info(f"Connected to oscilloscope: {self.resource_name}")
        except OscilloscopeError as e:
            logger.error(f"Failed to connect: {e}")
            logger.warning("Running in offline mode - oscilloscope commands will fail")
            # Don't raise - allow agent to run in offline mode for testing
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools from oscilloscope operations."""
        
        def measure_channel_wrapper(channel: str) -> str:
            """Wrapper to handle channel parameter."""
            try:
                clean_channel = str(channel).strip().strip("'\"")
                ch = int(clean_channel)
                return self._measure_channel(ch)
            except Exception as e:
                return f"Error measuring channel: {e}"
        
        def set_channel_config_wrapper(input_str: str) -> str:
            """Wrapper for channel configuration.
            Expected format: 'channel=1, voltage_div=100MV' or similar.
            """
            try:
                # Parse the input string
                import re
                
                # Extract channel number
                ch_match = re.search(r'channel[=\s]+(\d+)', input_str, re.IGNORECASE)
                channel = int(ch_match.group(1)) if ch_match else 1
                
                # Extract voltage division
                vdiv_match = re.search(r'voltage_div[=\s]+([\w]+)', input_str, re.IGNORECASE) or \
                            re.search(r'(\d+\s*[mM]?[vV])', input_str)
                
                if vdiv_match:
                    voltage_div = vdiv_match.group(1).upper().replace(' ', '')
                    # Normalize format: ensure it's like "100MV" not "100mv"
                    if not voltage_div.endswith('V'):
                        voltage_div += 'V'
                    return self._set_channel_config(channel=channel, voltage_div=voltage_div)
                else:
                    return "Error: Could not parse voltage division value"
                    
            except Exception as e:
                return f"Error configuring channel: {e}"
        
        def set_timebase_wrapper(input_str: str) -> str:
            """Wrapper for timebase configuration."""
            try:
                import re
                
                # Map from various unit formats to standard abbreviations
                time_unit_map = {
                    'nanosecond': 'NS',
                    'nanoseconds': 'NS',
                    'microsecond': 'US',
                    'microseconds': 'US',
                    'millisecond': 'MS',
                    'milliseconds': 'MS',
                    'second': 'S',
                    'seconds': 'S',
                    'ns': 'NS',
                    'us': 'US',
                    'µs': 'US',
                    'ms': 'MS',
                    's': 'S'
                }
                
                # Try to extract number and unit
                # Matches patterns like "100 microsecond", "100microseconds", "100us", "100 us"
                match = re.search(r'(\d+)\s*(nanoseconds?|microseconds?|milliseconds?|seconds?|ns|us|µs|ms|s)\b', 
                                input_str, re.IGNORECASE)
                
                if match:
                    number = match.group(1)
                    unit_text = match.group(2).lower()  # Just lowercase, don't strip 's'
                    
                    # Map to SCPI format (now handles both plural and abbreviations correctly)
                    unit = time_unit_map.get(unit_text, 'S')
                    time_div = f"{number}{unit}"
                    
                    return self._set_timebase(time_div=time_div)
                
                return "Error: Could not parse time division. Try formats like '100 microseconds' or '1 millisecond'"
            except Exception as e:
                return f"Error setting timebase: {e}"
        
        def get_timebase_wrapper(input: str = "") -> str:
            """Wrapper to get current timebase settings."""
            try:
                return self._get_timebase()
            except Exception as e:
                return f"Error getting timebase: {e}"
        
        def get_channel_config_wrapper(input_str: str) -> str:
            """Wrapper to get channel configuration."""
            try:
                # Extract channel number
                channel = int(input_str.strip().strip("'\""))
                return self._get_channel_config(channel)
            except Exception as e:
                return f"Error getting channel config: {e}"
        
        def auto_setup_wrapper(input: str = "") -> str:
            """Wrapper for auto setup."""
            return self._auto_setup()
        
        def reset_scope_wrapper(input: str = "") -> str:
            """Wrapper for reset."""
            return self._reset_scope()
        
        def get_status_wrapper(input: str = "") -> str:
            """Wrapper for status."""
            return self._get_scope_status()
        
        tools = [
            Tool(
                name="measure_channel",
                description="Get all measurements from a channel (frequency, voltage, etc.). Input: channel number like '1' or '2'",
                func=measure_channel_wrapper
            ),
            Tool(
                name="set_channel_voltage",
                description="Set voltage division (volts per division) for a channel. Input: description like 'channel 1 to 100MV' or 'channel=1, voltage_div=2V'. Accepts: 500UV, 1MV, 2MV, 5MV, 10MV, 20MV, 50MV, 100MV, 200MV, 500MV, 1V, 2V, 5V, 10V",
                func=set_channel_config_wrapper
            ),
            Tool(
                name="set_timebase",
                description="Set time division (time per division) for horizontal scale. Input: time value like '1MS' or '500US'. Accepts: 1NS to 100S",
                func=set_timebase_wrapper
            ),
            Tool(
                name="get_timebase",
                description="Get current timebase (time per division) setting. No input needed.",
                func=get_timebase_wrapper
            ),
            Tool(
                name="get_channel_config",
                description="Get channel configuration including voltage division. Input: channel number like '1' or '2'",
                func=get_channel_config_wrapper
            ),
            Tool(
                name="auto_setup",
                description="Automatically configure oscilloscope for optimal viewing. No input needed.",
                func=auto_setup_wrapper
            ),
            Tool(
                name="reset_scope",
                description="Reset oscilloscope to factory defaults. No input needed.",
                func=reset_scope_wrapper
            ),
            Tool(
                name="get_scope_status",
                description="Get current oscilloscope status and configuration. No input needed.",
                func=get_status_wrapper
            )
        ]
        
        return tools
    
    # Tool implementation methods
    
    def _set_channel_config(
        self,
        channel: int,
        enabled: bool = True,
        voltage_div: str = "1V",
        offset: str = "0V",
        coupling: str = "DC_1M"
    ) -> str:
        """Configure a channel."""
        from ..oscilloscope.models import CouplingMode
        
        coupling_map = {
            "DC_1M": CouplingMode.DC_1M,
            "AC_1M": CouplingMode.AC_1M,
            "DC_50": CouplingMode.DC_50,
            "GND": CouplingMode.GND
        }
        
        config = ChannelConfig(
            channel=channel,
            enabled=enabled,
            voltage_div=voltage_div,
            offset=offset,
            coupling=coupling_map.get(coupling, CouplingMode.DC_1M)
        )
        
        self.driver.configure_channel(config)
        return f"✅ Channel {channel} configured: {voltage_div}/div"
    
    def _set_timebase(self, time_div: str, delay: str = "0S") -> str:
        """Configure timebase - converts to scientific notation and validates."""
        import re
        
        # Valid timebase values (Siglent standard)
        VALID_BASE_VALUES = [1, 2, 5]  # Base values that repeat per magnitude
        
        def find_nearest_valid(value: float, unit: str) -> tuple:
            """Find nearest valid timebase value."""
            # All valid values in seconds
            valid_values = []
            magnitudes = [1e-9, 1e-6, 1e-3, 1]  # NS, US, MS, S
            for mag in magnitudes:
                for base in [1, 2, 5]:
                    for mult in [1, 10, 100]:
                        val = base * mult * mag
                        if 1e-9 <= val <= 100:  # 1NS to 100S
                            valid_values.append(val)
            
            valid_values.sort()
            
            # Find nearest
            nearest = min(valid_values, key=lambda x: abs(x - value))
            return nearest
        
        def convert_to_scientific(value_str: str) -> tuple:
            """Convert time string to seconds and find nearest valid value."""
            value_str = value_str.upper().strip()
            
            # Extract number and unit
            match = re.match(r'([\d.]+)\s*([MUNP]?S?)', value_str)
            if not match:
                return value_str, value_str, False  # Return as-is if no match
            
            number = float(match.group(1))
            unit = match.group(2)
            
            # Convert to seconds based on unit
            multipliers = {
                'NS': 1e-9,
                'US': 1e-6,
                'MS': 1e-3,
                'S': 1,
                '': 1
            }
            
            multiplier = multipliers.get(unit, 1)
            seconds = number * multiplier
            
            # Find nearest valid value
            nearest_seconds = find_nearest_valid(seconds, unit)
            was_adjusted = abs(nearest_seconds - seconds) > 1e-12
            
            return f"{nearest_seconds:.6E}", nearest_seconds, was_adjusted
        
        converted_time_div, actual_seconds, was_adjusted = convert_to_scientific(time_div)
        converted_delay, _, _ = convert_to_scientific(delay)
        
        config = TimebaseConfig(time_div=converted_time_div, delay=converted_delay)
        self.driver.configure_timebase(config)
        
        # Query back to verify what was actually set
        actual_tdiv = self.driver.query("TDIV?").strip()
        
        # Format response with warning if adjusted
        if was_adjusted:
            # Convert back to human-readable
            if actual_seconds >= 1:
                readable = f"{actual_seconds:.0f}S"
            elif actual_seconds >= 1e-3:
                readable = f"{actual_seconds*1e3:.0f}MS"
            elif actual_seconds >= 1e-6:
                readable = f"{actual_seconds*1e6:.0f}US"
            else:
                readable = f"{actual_seconds*1e9:.0f}NS"
            
            return f"⚠️  {time_div} is not valid. Set to nearest: {readable} ({actual_tdiv} on scope)"
        else:
            return f"✅ Timebase set to {time_div} ({actual_tdiv} on scope)"
    
    def _get_timebase(self) -> str:
        """Get current timebase settings."""
        try:
            settings = self.driver.get_timebase()
            return f"Current timebase: {settings['time_div']}/div, Delay: {settings['delay']}"
        except Exception as e:
            return f"Error getting timebase: {e}"
    
    def _get_channel_config(self, channel: int) -> str:
        """Get current channel configuration."""
        try:
            config = self.driver.get_channel_config(channel)
            return (
                f"Channel {channel} configuration:\n"
                f"  Voltage division: {config['voltage_div']}/div\n"
                f"  Coupling: {config['coupling']}\n"
                f"  Probe ratio: {config['probe_ratio']}\n"
                f"  Offset: {config['offset']}"
            )
        except Exception as e:
            return f"Error getting channel {channel} config: {e}"
    
    def _set_trigger(
        self,
        source: int,
        mode: str = "AUTO",
        trigger_type: str = "EDGE",
        slope: str = "RISING",
        level: str = "0V"
    ) -> str:
        """Configure trigger."""
        from ..oscilloscope.models import TriggerMode, TriggerType, TriggerSlope
        
        mode_map = {"AUTO": TriggerMode.AUTO, "NORMAL": TriggerMode.NORMAL,
                   "SINGLE": TriggerMode.SINGLE, "STOP": TriggerMode.STOP}
        type_map = {"EDGE": TriggerType.EDGE, "PULSE": TriggerType.PULSE,
                   "VIDEO": TriggerType.VIDEO, "PATTERN": TriggerType.PATTERN}
        slope_map = {"RISING": TriggerSlope.RISING, "FALLING": TriggerSlope.FALLING,
                    "BOTH": TriggerSlope.BOTH}
        
        config = TriggerConfig(
            source=source,
            mode=mode_map.get(mode, TriggerMode.AUTO),
            trigger_type=type_map.get(trigger_type, TriggerType.EDGE),
            slope=slope_map.get(slope, TriggerSlope.RISING),
            level=level
        )
        
        self.driver.configure_trigger(config)
        return f"Trigger configured: Channel {source}, {mode} mode, {slope} edge at {level}"
    
    def _measure_channel(self, channel: int) -> str:
        """Measure a channel."""
        measurements = self.driver.measure_channel(channel)
        
        result = f"Channel {channel} Measurements:\n"
        if measurements.frequency:
            result += f"  Frequency: {measurements.frequency:.2f} Hz\n"
        if measurements.period:
            result += f"  Period: {measurements.period*1000:.3f} ms\n"
        if measurements.peak_to_peak:
            result += f"  Peak-to-Peak: {measurements.peak_to_peak:.3f} V\n"
        if measurements.amplitude:
            result += f"  Amplitude: {measurements.amplitude:.3f} V\n"
        if measurements.maximum:
            result += f"  Maximum: {measurements.maximum:.3f} V\n"
        if measurements.minimum:
            result += f"  Minimum: {measurements.minimum:.3f} V\n"
        if measurements.mean:
            result += f"  Mean: {measurements.mean:.3f} V\n"
        if measurements.rms:
            result += f"  RMS: {measurements.rms:.3f} V\n"
        
        return result
    
    def _capture_waveform(self, channel: int, num_points: int = 1400) -> str:
        """Capture waveform."""
        waveform = self.driver.capture_waveform(channel, num_points)
        return (
            f"Captured waveform from channel {channel}:\n"
            f"  Points: {waveform.num_points}\n"
            f"  Sample rate: {waveform.sample_rate} Hz\n"
            f"  Voltage range: {min(waveform.data_points):.3f}V to {max(waveform.data_points):.3f}V"
        )
    
    def _auto_setup(self) -> str:
        """Auto setup."""
        self.driver.auto_setup()
        return "Auto setup completed. Oscilloscope has been automatically configured."
    
    def _reset_scope(self) -> str:
        """Reset scope."""
        self.driver.reset()
        return "Oscilloscope reset to factory defaults."
    
    def _get_scope_status(self) -> str:
        """Get scope status."""
        status = self.driver.get_status()
        return (
            f"Oscilloscope Status:\n"
            f"  Model: {status.model}\n"
            f"  Serial: {status.serial_number}\n"
            f"  Firmware: {status.firmware_version}\n"
            f"  Connected: {status.connected}\n"
            f"  Acquisition: {'Running' if status.acquisition_running else 'Stopped'}"
        )
    
    def execute(self, command: str) -> str:
        """
        Execute a natural language command.
        
        Args:
            command: Natural language command
            
        Returns:
            Response from the agent
        """
        try:
            result = self.agent_executor.invoke({"input": command})
            return result["output"]
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return f"Error: {str(e)}"
    
    def execute_with_image(self, command: str, image_data: bytes) -> str:
        """
        Execute a natural language command with an image (Claude Vision).
        
        Args:
            command: Natural language command
            image_data: Image data as bytes (PNG or BMP)
            
        Returns:
            Result of the command execution with image analysis
        """
        try:
            # Only works with Claude models that support vision
            if self.model_type != "claude":
                return self.execute(
                    f"{command}\n[Note: Image analysis not available with this model. "
                    "Please use measurements or describe what you see.]"
                )
            
            # Use Anthropic API directly for vision
            import base64
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            # Convert image to base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine media type
            if image_data.startswith(b'\x89PNG'):
                media_type = "image/png"
            elif image_data.startswith(b'BM'):
                media_type = "image/bmp"
            else:
                media_type = "image/png"  # Assume PNG
            
            # Use Claude 3.5 Sonnet for vision (Haiku doesn't support vision well)
            vision_model = "claude-haiku-4-5-20251001"
            
            # Create message with image
            system_prompt = (
                "You are an expert oscilloscope operator and electronics engineer. "
                "You can see an oscilloscope screenshot. Analyze it carefully and help the user. "
                "Describe what you see: waveform shape, signal type (sine/square/etc), "
                "frequency estimate based on screen divisions, amplitude, any anomalies or noise."
            )
            
            logger.info(f"Calling Claude Vision API with model: {vision_model}")
            
            # Call Claude with vision
            message = client.messages.create(
                model=vision_model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": command
                        }
                    ],
                }]
            )
            
            # Extract response
            response_text = message.content[0].text
            
            logger.info(f"Vision analysis completed")
            return response_text
            
        except Exception as e:
            logger.error(f"Vision execution failed: {e}")
            # Fallback to regular execution
            return self.execute(
                f"{command}\n[Note: Vision analysis failed: {e}. Using text-only mode.]"
            )
    
    def chat(self):
        """Start interactive chat session."""
        print("Oscilloscope Agent - Type 'quit' to exit")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                response = self.execute(user_input)
                print(f"\nAgent: {response}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
    
    def disconnect(self):
        """Disconnect from oscilloscope."""
        self.driver.disconnect()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False

