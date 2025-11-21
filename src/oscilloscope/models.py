"""Data models for oscilloscope operations."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class CouplingMode(str, Enum):
    """Channel coupling modes."""
    DC_1M = "D1M"  # DC coupling, 1M ohm
    AC_1M = "A1M"  # AC coupling, 1M ohm
    DC_50 = "D50"  # DC coupling, 50 ohm
    GND = "GND"    # Ground


class TriggerMode(str, Enum):
    """Trigger modes."""
    AUTO = "AUTO"
    NORMAL = "NORM"
    SINGLE = "SINGLE"
    STOP = "STOP"


class TriggerType(str, Enum):
    """Trigger types."""
    EDGE = "EDGE"
    PULSE = "PULSE"
    VIDEO = "VIDEO"
    PATTERN = "PATTERN"


class TriggerSlope(str, Enum):
    """Trigger slope."""
    RISING = "POS"
    FALLING = "NEG"
    BOTH = "WINDOW"


class ChannelConfig(BaseModel):
    """Channel configuration."""
    channel: int = Field(ge=1, le=4, description="Channel number (1-4)")
    enabled: bool = Field(default=True, description="Channel enabled")
    voltage_div: str = Field(default="1V", description="Volts per division (e.g., '1V', '500MV')")
    offset: str = Field(default="0V", description="Vertical offset")
    coupling: CouplingMode = Field(default=CouplingMode.DC_1M, description="Coupling mode")
    probe_ratio: int = Field(default=1, description="Probe attenuation ratio (1, 10, 100, 1000)")
    bandwidth_limit: bool = Field(default=False, description="20MHz bandwidth limit")


class TimebaseConfig(BaseModel):
    """Timebase configuration."""
    time_div: str = Field(default="1MS", description="Time per division (e.g., '1MS', '500US')")
    delay: str = Field(default="0S", description="Horizontal delay")
    sample_rate: Optional[str] = Field(default=None, description="Sample rate (read-only)")


class TriggerConfig(BaseModel):
    """Trigger configuration."""
    source: int = Field(ge=1, le=4, default=1, description="Trigger source channel")
    mode: TriggerMode = Field(default=TriggerMode.AUTO, description="Trigger mode")
    trigger_type: TriggerType = Field(default=TriggerType.EDGE, description="Trigger type")
    slope: TriggerSlope = Field(default=TriggerSlope.RISING, description="Trigger slope")
    level: str = Field(default="0V", description="Trigger level")
    holdoff: Optional[str] = Field(default=None, description="Trigger holdoff time")


class Measurements(BaseModel):
    """Channel measurement data."""
    channel: int
    frequency: Optional[float] = Field(default=None, description="Frequency in Hz")
    period: Optional[float] = Field(default=None, description="Period in seconds")
    peak_to_peak: Optional[float] = Field(default=None, description="Peak-to-peak voltage")
    amplitude: Optional[float] = Field(default=None, description="Amplitude")
    maximum: Optional[float] = Field(default=None, description="Maximum voltage")
    minimum: Optional[float] = Field(default=None, description="Minimum voltage")
    mean: Optional[float] = Field(default=None, description="Mean voltage")
    rms: Optional[float] = Field(default=None, description="RMS voltage")
    rise_time: Optional[float] = Field(default=None, description="Rise time")
    fall_time: Optional[float] = Field(default=None, description="Fall time")
    positive_width: Optional[float] = Field(default=None, description="Positive pulse width")
    negative_width: Optional[float] = Field(default=None, description="Negative pulse width")


class WaveformData(BaseModel):
    """Waveform data from channel."""
    channel: int
    num_points: int
    sample_rate: float
    voltage_scale: float
    voltage_offset: float
    time_scale: float
    data_points: List[float] = Field(description="Voltage values")
    time_points: List[float] = Field(description="Time values")


class ScopeStatus(BaseModel):
    """Overall oscilloscope status."""
    connected: bool
    model: str
    serial_number: str
    firmware_version: str
    channels: List[ChannelConfig]
    timebase: TimebaseConfig
    trigger: TriggerConfig
    acquisition_running: bool
    memory_depth: Optional[int] = None

