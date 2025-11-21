"""MCP tools for oscilloscope operations."""

from typing import Any, Dict, List
from mcp.types import Tool, TextContent
import json

from ..oscilloscope.driver import OscilloscopeDriver
from ..oscilloscope.models import (
    ChannelConfig,
    TimebaseConfig,
    TriggerConfig,
    TriggerMode,
    TriggerType,
    TriggerSlope,
    CouplingMode,
)


class OscilloscopeTools:
    """MCP tools for oscilloscope control."""
    
    def __init__(self, driver: OscilloscopeDriver):
        """Initialize with oscilloscope driver."""
        self.driver = driver
    
    def get_tools(self) -> List[Tool]:
        """Return list of available MCP tools."""
        return [
            Tool(
                name="set_channel_config",
                description="Configure oscilloscope channel settings (voltage scale, coupling, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "integer",
                            "description": "Channel number (1-4)",
                            "minimum": 1,
                            "maximum": 4
                        },
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable or disable the channel",
                            "default": True
                        },
                        "voltage_div": {
                            "type": "string",
                            "description": "Volts per division (e.g., '1V', '500MV', '2V')",
                            "default": "1V"
                        },
                        "offset": {
                            "type": "string",
                            "description": "Vertical offset (e.g., '0V', '-2V')",
                            "default": "0V"
                        },
                        "coupling": {
                            "type": "string",
                            "enum": ["DC_1M", "AC_1M", "DC_50", "GND"],
                            "description": "Coupling mode",
                            "default": "DC_1M"
                        }
                    },
                    "required": ["channel"]
                }
            ),
            Tool(
                name="set_timebase",
                description="Configure oscilloscope timebase (time scale and delay)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "time_div": {
                            "type": "string",
                            "description": "Time per division (e.g., '1MS', '500US', '10US')",
                        },
                        "delay": {
                            "type": "string",
                            "description": "Horizontal delay (e.g., '0S', '100MS')",
                            "default": "0S"
                        }
                    },
                    "required": ["time_div"]
                }
            ),
            Tool(
                name="set_trigger",
                description="Configure oscilloscope trigger settings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "integer",
                            "description": "Trigger source channel (1-4)",
                            "minimum": 1,
                            "maximum": 4
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["AUTO", "NORMAL", "SINGLE", "STOP"],
                            "description": "Trigger mode",
                            "default": "AUTO"
                        },
                        "trigger_type": {
                            "type": "string",
                            "enum": ["EDGE", "PULSE", "VIDEO", "PATTERN"],
                            "description": "Trigger type",
                            "default": "EDGE"
                        },
                        "slope": {
                            "type": "string",
                            "enum": ["RISING", "FALLING", "BOTH"],
                            "description": "Trigger slope/edge",
                            "default": "RISING"
                        },
                        "level": {
                            "type": "string",
                            "description": "Trigger level (e.g., '0V', '1.5V')",
                            "default": "0V"
                        }
                    },
                    "required": ["source"]
                }
            ),
            Tool(
                name="measure_channel",
                description="Get all measurements from a specified channel (frequency, voltage, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "integer",
                            "description": "Channel number to measure (1-4)",
                            "minimum": 1,
                            "maximum": 4
                        }
                    },
                    "required": ["channel"]
                }
            ),
            Tool(
                name="capture_waveform",
                description="Capture waveform data from a channel",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "integer",
                            "description": "Channel number (1-4)",
                            "minimum": 1,
                            "maximum": 4
                        },
                        "num_points": {
                            "type": "integer",
                            "description": "Number of data points to capture",
                            "default": 1400
                        }
                    },
                    "required": ["channel"]
                }
            ),
            Tool(
                name="auto_setup",
                description="Automatically configure oscilloscope for optimal viewing of signal",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="reset_scope",
                description="Reset oscilloscope to default factory settings",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="arm_single_trigger",
                description="Arm oscilloscope for single trigger acquisition",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="stop_acquisition",
                description="Stop oscilloscope acquisition",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_scope_status",
                description="Get complete oscilloscope status and configuration",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a tool and return results."""
        try:
            if tool_name == "set_channel_config":
                return await self._set_channel_config(arguments)
            elif tool_name == "set_timebase":
                return await self._set_timebase(arguments)
            elif tool_name == "set_trigger":
                return await self._set_trigger(arguments)
            elif tool_name == "measure_channel":
                return await self._measure_channel(arguments)
            elif tool_name == "capture_waveform":
                return await self._capture_waveform(arguments)
            elif tool_name == "auto_setup":
                return await self._auto_setup()
            elif tool_name == "reset_scope":
                return await self._reset_scope()
            elif tool_name == "arm_single_trigger":
                return await self._arm_single_trigger()
            elif tool_name == "stop_acquisition":
                return await self._stop_acquisition()
            elif tool_name == "get_scope_status":
                return await self._get_scope_status()
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {tool_name}"
                )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing {tool_name}: {str(e)}"
            )]
    
    async def _set_channel_config(self, args: Dict[str, Any]) -> List[TextContent]:
        """Configure channel."""
        coupling_map = {
            "DC_1M": CouplingMode.DC_1M,
            "AC_1M": CouplingMode.AC_1M,
            "DC_50": CouplingMode.DC_50,
            "GND": CouplingMode.GND
        }
        
        config = ChannelConfig(
            channel=args["channel"],
            enabled=args.get("enabled", True),
            voltage_div=args.get("voltage_div", "1V"),
            offset=args.get("offset", "0V"),
            coupling=coupling_map.get(args.get("coupling", "DC_1M"), CouplingMode.DC_1M)
        )
        
        self.driver.configure_channel(config)
        
        return [TextContent(
            type="text",
            text=f"Channel {config.channel} configured: {config.voltage_div}/div, {config.coupling.value} coupling"
        )]
    
    async def _set_timebase(self, args: Dict[str, Any]) -> List[TextContent]:
        """Configure timebase."""
        config = TimebaseConfig(
            time_div=args["time_div"],
            delay=args.get("delay", "0S")
        )
        
        self.driver.configure_timebase(config)
        
        return [TextContent(
            type="text",
            text=f"Timebase configured: {config.time_div}/div"
        )]
    
    async def _set_trigger(self, args: Dict[str, Any]) -> List[TextContent]:
        """Configure trigger."""
        mode_map = {
            "AUTO": TriggerMode.AUTO,
            "NORMAL": TriggerMode.NORMAL,
            "SINGLE": TriggerMode.SINGLE,
            "STOP": TriggerMode.STOP
        }
        
        type_map = {
            "EDGE": TriggerType.EDGE,
            "PULSE": TriggerType.PULSE,
            "VIDEO": TriggerType.VIDEO,
            "PATTERN": TriggerType.PATTERN
        }
        
        slope_map = {
            "RISING": TriggerSlope.RISING,
            "FALLING": TriggerSlope.FALLING,
            "BOTH": TriggerSlope.BOTH
        }
        
        config = TriggerConfig(
            source=args["source"],
            mode=mode_map.get(args.get("mode", "AUTO"), TriggerMode.AUTO),
            trigger_type=type_map.get(args.get("trigger_type", "EDGE"), TriggerType.EDGE),
            slope=slope_map.get(args.get("slope", "RISING"), TriggerSlope.RISING),
            level=args.get("level", "0V")
        )
        
        self.driver.configure_trigger(config)
        
        return [TextContent(
            type="text",
            text=f"Trigger configured: Channel {config.source}, {config.mode.value} mode, {config.slope.value} edge at {config.level}"
        )]
    
    async def _measure_channel(self, args: Dict[str, Any]) -> List[TextContent]:
        """Measure channel."""
        channel = args["channel"]
        measurements = self.driver.measure_channel(channel)
        
        # Format measurements nicely
        result = {
            "channel": measurements.channel,
            "frequency_hz": measurements.frequency,
            "period_s": measurements.period,
            "peak_to_peak_v": measurements.peak_to_peak,
            "amplitude_v": measurements.amplitude,
            "maximum_v": measurements.maximum,
            "minimum_v": measurements.minimum,
            "mean_v": measurements.mean,
            "rms_v": measurements.rms
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def _capture_waveform(self, args: Dict[str, Any]) -> List[TextContent]:
        """Capture waveform."""
        channel = args["channel"]
        num_points = args.get("num_points", 1400)
        
        waveform = self.driver.capture_waveform(channel, num_points)
        
        result = {
            "channel": waveform.channel,
            "num_points": waveform.num_points,
            "sample_rate_hz": waveform.sample_rate,
            "voltage_scale": waveform.voltage_scale,
            "time_range_s": [min(waveform.time_points), max(waveform.time_points)],
            "voltage_range_v": [min(waveform.data_points), max(waveform.data_points)],
            "note": "Full waveform data available in waveform.data_points"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def _auto_setup(self) -> List[TextContent]:
        """Auto setup."""
        self.driver.auto_setup()
        return [TextContent(type="text", text="Auto setup completed")]
    
    async def _reset_scope(self) -> List[TextContent]:
        """Reset scope."""
        self.driver.reset()
        return [TextContent(type="text", text="Oscilloscope reset to factory defaults")]
    
    async def _arm_single_trigger(self) -> List[TextContent]:
        """Arm single trigger."""
        self.driver.arm_trigger()
        return [TextContent(type="text", text="Oscilloscope armed for single trigger")]
    
    async def _stop_acquisition(self) -> List[TextContent]:
        """Stop acquisition."""
        self.driver.stop_acquisition()
        return [TextContent(type="text", text="Acquisition stopped")]
    
    async def _get_scope_status(self) -> List[TextContent]:
        """Get scope status."""
        status = self.driver.get_status()
        
        result = {
            "connected": status.connected,
            "model": status.model,
            "serial_number": status.serial_number,
            "firmware_version": status.firmware_version,
            "acquisition_running": status.acquisition_running,
            "num_channels": len(status.channels),
            "timebase": {
                "time_div": status.timebase.time_div,
                "delay": status.timebase.delay
            },
            "trigger": {
                "source": status.trigger.source,
                "mode": status.trigger.mode.value,
                "level": status.trigger.level
            }
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

