"""MCP resources for oscilloscope data retrieval."""

from typing import Any, Dict
from mcp.types import Resource, TextContent, ResourceContents
import json

from ..oscilloscope.driver import OscilloscopeDriver


class OscilloscopeResources:
    """MCP resources for oscilloscope data."""
    
    def __init__(self, driver: OscilloscopeDriver):
        """Initialize with oscilloscope driver."""
        self.driver = driver
    
    def get_resources(self) -> list[Resource]:
        """Return list of available MCP resources."""
        return [
            Resource(
                uri="scope://status",
                name="Oscilloscope Status",
                description="Current status and configuration of the oscilloscope",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://channels/1/config",
                name="Channel 1 Configuration",
                description="Configuration settings for channel 1",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://channels/2/config",
                name="Channel 2 Configuration",
                description="Configuration settings for channel 2",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://channels/1/measurements",
                name="Channel 1 Measurements",
                description="Real-time measurements from channel 1",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://channels/2/measurements",
                name="Channel 2 Measurements",
                description="Real-time measurements from channel 2",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://waveform/1",
                name="Channel 1 Waveform",
                description="Waveform data from channel 1",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://waveform/2",
                name="Channel 2 Waveform",
                description="Waveform data from channel 2",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://trigger/status",
                name="Trigger Status",
                description="Current trigger configuration and status",
                mimeType="application/json"
            ),
            Resource(
                uri="scope://timebase/config",
                name="Timebase Configuration",
                description="Current timebase settings",
                mimeType="application/json"
            )
        ]
    
    async def read_resource(self, uri: str) -> ResourceContents:
        """Read a resource by URI."""
        try:
            if uri == "scope://status":
                return await self._read_status()
            elif uri.startswith("scope://channels/") and uri.endswith("/config"):
                channel = int(uri.split("/")[2])
                return await self._read_channel_config(channel)
            elif uri.startswith("scope://channels/") and uri.endswith("/measurements"):
                channel = int(uri.split("/")[2])
                return await self._read_channel_measurements(channel)
            elif uri.startswith("scope://waveform/"):
                channel = int(uri.split("/")[2])
                return await self._read_waveform(channel)
            elif uri == "scope://trigger/status":
                return await self._read_trigger_status()
            elif uri == "scope://timebase/config":
                return await self._read_timebase_config()
            else:
                return ResourceContents(
                    uri=uri,
                    mimeType="text/plain",
                    text=f"Unknown resource: {uri}"
                )
        except Exception as e:
            return ResourceContents(
                uri=uri,
                mimeType="text/plain",
                text=f"Error reading resource {uri}: {str(e)}"
            )
    
    async def _read_status(self) -> ResourceContents:
        """Read oscilloscope status."""
        status = self.driver.get_status()
        
        data = {
            "connected": status.connected,
            "model": status.model,
            "serial_number": status.serial_number,
            "firmware_version": status.firmware_version,
            "acquisition_running": status.acquisition_running,
            "memory_depth": status.memory_depth
        }
        
        return ResourceContents(
            uri="scope://status",
            mimeType="application/json",
            text=json.dumps(data, indent=2)
        )
    
    async def _read_channel_config(self, channel: int) -> ResourceContents:
        """Read channel configuration."""
        # In a real implementation, query actual config from scope
        # For now, return placeholder
        data = {
            "channel": channel,
            "enabled": True,
            "voltage_div": "1V",
            "offset": "0V",
            "coupling": "DC_1M",
            "probe_ratio": 1,
            "bandwidth_limit": False
        }
        
        return ResourceContents(
            uri=f"scope://channels/{channel}/config",
            mimeType="application/json",
            text=json.dumps(data, indent=2)
        )
    
    async def _read_channel_measurements(self, channel: int) -> ResourceContents:
        """Read channel measurements."""
        measurements = self.driver.measure_channel(channel)
        
        data = {
            "channel": measurements.channel,
            "frequency_hz": measurements.frequency,
            "period_s": measurements.period,
            "peak_to_peak_v": measurements.peak_to_peak,
            "amplitude_v": measurements.amplitude,
            "maximum_v": measurements.maximum,
            "minimum_v": measurements.minimum,
            "mean_v": measurements.mean,
            "rms_v": measurements.rms,
            "rise_time_s": measurements.rise_time,
            "fall_time_s": measurements.fall_time
        }
        
        return ResourceContents(
            uri=f"scope://channels/{channel}/measurements",
            mimeType="application/json",
            text=json.dumps(data, indent=2)
        )
    
    async def _read_waveform(self, channel: int) -> ResourceContents:
        """Read waveform data."""
        waveform = self.driver.capture_waveform(channel)
        
        # Return summary instead of full data (full data could be huge)
        data = {
            "channel": waveform.channel,
            "num_points": waveform.num_points,
            "sample_rate_hz": waveform.sample_rate,
            "voltage_scale": waveform.voltage_scale,
            "voltage_offset": waveform.voltage_offset,
            "time_scale": waveform.time_scale,
            "time_range_s": [min(waveform.time_points), max(waveform.time_points)],
            "voltage_range_v": [min(waveform.data_points), max(waveform.data_points)],
            "statistics": {
                "mean": sum(waveform.data_points) / len(waveform.data_points),
                "min": min(waveform.data_points),
                "max": max(waveform.data_points)
            },
            "note": "Use capture_waveform tool to get full data points"
        }
        
        return ResourceContents(
            uri=f"scope://waveform/{channel}",
            mimeType="application/json",
            text=json.dumps(data, indent=2)
        )
    
    async def _read_trigger_status(self) -> ResourceContents:
        """Read trigger status."""
        status = self.driver.get_status()
        
        data = {
            "source_channel": status.trigger.source,
            "mode": status.trigger.mode.value,
            "trigger_type": status.trigger.trigger_type.value,
            "slope": status.trigger.slope.value,
            "level": status.trigger.level,
            "holdoff": status.trigger.holdoff
        }
        
        return ResourceContents(
            uri="scope://trigger/status",
            mimeType="application/json",
            text=json.dumps(data, indent=2)
        )
    
    async def _read_timebase_config(self) -> ResourceContents:
        """Read timebase configuration."""
        status = self.driver.get_status()
        
        data = {
            "time_div": status.timebase.time_div,
            "delay": status.timebase.delay,
            "sample_rate": status.timebase.sample_rate
        }
        
        return ResourceContents(
            uri="scope://timebase/config",
            mimeType="application/json",
            text=json.dumps(data, indent=2)
        )

