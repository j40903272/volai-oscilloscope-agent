"""Example: Direct oscilloscope control using the driver."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.oscilloscope.driver import OscilloscopeDriver
from src.oscilloscope.models import (
    ChannelConfig,
    TimebaseConfig,
    TriggerConfig,
    TriggerMode,
    TriggerSlope,
    CouplingMode
)


def main():
    """Demonstrate basic oscilloscope control."""
    
    # Initialize driver
    resource_name = "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR"
    
    # Use context manager for automatic cleanup
    with OscilloscopeDriver(resource_name, auto_connect=True) as scope:
        
        print("=" * 60)
        print("Oscilloscope Basic Control Example")
        print("=" * 60)
        
        # Get status
        print("\n1. Getting oscilloscope status...")
        status = scope.get_status()
        print(f"   Model: {status.model}")
        print(f"   Serial: {status.serial_number}")
        print(f"   Firmware: {status.firmware_version}")
        
        # Configure Channel 1
        print("\n2. Configuring Channel 1...")
        ch1_config = ChannelConfig(
            channel=1,
            enabled=True,
            voltage_div="1V",
            offset="0V",
            coupling=CouplingMode.DC_1M,
            probe_ratio=10
        )
        scope.configure_channel(ch1_config)
        print(f"   Channel 1: {ch1_config.voltage_div}/div, {ch1_config.coupling.value}")
        
        # Configure Channel 2
        print("\n3. Configuring Channel 2...")
        ch2_config = ChannelConfig(
            channel=2,
            enabled=True,
            voltage_div="500MV",
            offset="0V",
            coupling=CouplingMode.AC_1M
        )
        scope.configure_channel(ch2_config)
        print(f"   Channel 2: {ch2_config.voltage_div}/div, {ch2_config.coupling.value}")
        
        # Configure Timebase
        print("\n4. Configuring Timebase...")
        timebase = TimebaseConfig(
            time_div="1MS",
            delay="0S"
        )
        scope.configure_timebase(timebase)
        print(f"   Timebase: {timebase.time_div}/div")
        
        # Configure Trigger
        print("\n5. Configuring Trigger...")
        trigger = TriggerConfig(
            source=1,
            mode=TriggerMode.AUTO,
            slope=TriggerSlope.RISING,
            level="0V"
        )
        scope.configure_trigger(trigger)
        print(f"   Trigger: Channel {trigger.source}, {trigger.mode.value}, {trigger.slope.value}")
        
        # Measure Channel 1
        print("\n6. Measuring Channel 1...")
        measurements = scope.measure_channel(1)
        print(f"   Frequency: {measurements.frequency} Hz" if measurements.frequency else "   Frequency: N/A")
        print(f"   Peak-to-Peak: {measurements.peak_to_peak} V" if measurements.peak_to_peak else "   Peak-to-Peak: N/A")
        print(f"   Maximum: {measurements.maximum} V" if measurements.maximum else "   Maximum: N/A")
        print(f"   Minimum: {measurements.minimum} V" if measurements.minimum else "   Minimum: N/A")
        print(f"   Mean: {measurements.mean} V" if measurements.mean else "   Mean: N/A")
        
        # Capture waveform (optional - uncomment if needed)
        # print("\n7. Capturing Waveform from Channel 1...")
        # waveform = scope.capture_waveform(1, num_points=1000)
        # print(f"   Captured {waveform.num_points} points")
        # print(f"   Voltage range: {min(waveform.data_points):.3f}V to {max(waveform.data_points):.3f}V")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()

