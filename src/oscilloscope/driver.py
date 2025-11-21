"""Oscilloscope driver using PyVISA."""

import logging
import time
from typing import Optional, List
import numpy as np
import pyvisa

from .commands import SCPICommands, format_command
from .models import (
    ChannelConfig,
    TimebaseConfig,
    TriggerConfig,
    Measurements,
    WaveformData,
    ScopeStatus,
    TriggerMode,
    TriggerType,
    TriggerSlope,
)


logger = logging.getLogger(__name__)


class OscilloscopeError(Exception):
    """Base exception for oscilloscope errors."""
    pass


class OscilloscopeDriver:
    """Driver for Siglent SDS series oscilloscopes."""
    
    def __init__(
        self,
        resource_name: str,
        timeout: int = 10000,
        auto_connect: bool = False,
        backend: str = None
    ):
        """
        Initialize oscilloscope driver.
        
        Args:
            resource_name: VISA resource name (e.g., 'USB0::0xF4ED::0xEE3A::...')
            timeout: Timeout in milliseconds
            auto_connect: Automatically connect on initialization
            backend: PyVISA backend ('@py' for PyVISA-py, None for default NI-VISA)
        """
        self.resource_name = resource_name
        self.timeout = timeout
        self.backend = backend
        self._instrument: Optional[pyvisa.resources.Resource] = None
        self._rm: Optional[pyvisa.ResourceManager] = None
        self._connected = False
        
        if auto_connect:
            self.connect()
    
    def connect(self) -> None:
        """Connect to the oscilloscope."""
        try:
            # Use specified backend or default (NI-VISA)
            if self.backend:
                logger.debug(f"Using PyVISA backend: {self.backend}")
                self._rm = pyvisa.ResourceManager(self.backend)
            else:
                logger.debug("Using default PyVISA backend (NI-VISA)")
                self._rm = pyvisa.ResourceManager()
            
            self._instrument = self._rm.open_resource(self.resource_name)
            self._instrument.timeout = self.timeout
            
            # Mark as connected BEFORE verifying (needed for query to work)
            self._connected = True
            
            # Verify connection
            idn = self.query(SCPICommands.IDENTIFY)
            logger.info(f"Connected to: {idn}")
            
        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect to oscilloscope: {e}")
            raise OscilloscopeError(f"Connection failed: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from the oscilloscope."""
        if self._instrument:
            self._instrument.close()
        if self._rm:
            self._rm.close()
        self._connected = False
        logger.info("Disconnected from oscilloscope")
    
    def write(self, command: str) -> None:
        """Write a command to the oscilloscope."""
        if not self._connected or not self._instrument:
            raise OscilloscopeError("Not connected to oscilloscope")
        try:
            self._instrument.write(command)
            logger.debug(f"Sent command: {command}")
        except Exception as e:
            logger.error(f"Write error: {e}")
            raise OscilloscopeError(f"Write failed: {e}")
    
    def query(self, command: str) -> str:
        """Query the oscilloscope and return response."""
        if not self._connected or not self._instrument:
            raise OscilloscopeError("Not connected to oscilloscope")
        try:
            response = self._instrument.query(command).strip()
            logger.debug(f"Query: {command} -> {response}")
            return response
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise OscilloscopeError(f"Query failed: {e}")
    
    def read_raw(self) -> bytes:
        """Read raw binary data from the oscilloscope."""
        if not self._connected or not self._instrument:
            raise OscilloscopeError("Not connected to oscilloscope")
        try:
            return self._instrument.read_raw()
        except Exception as e:
            logger.error(f"Read raw error: {e}")
            raise OscilloscopeError(f"Read raw failed: {e}")
    
    def reset(self) -> None:
        """Reset the oscilloscope to default settings."""
        self.write(SCPICommands.RESET)
        time.sleep(2)  # Wait for reset to complete
        logger.info("Oscilloscope reset")
    
    def clear_status(self) -> None:
        """Clear status registers."""
        self.write(SCPICommands.CLEAR_STATUS)
    
    # Channel control methods
    
    def configure_channel(self, config: ChannelConfig) -> None:
        """Configure a channel."""
        ch = config.channel
        
        # Enable/disable channel
        state = "ON" if config.enabled else "OFF"
        self.write(format_command(SCPICommands.CHANNEL_TRACE, ch=ch, state=state))
        
        # Set voltage scale
        self.write(format_command(SCPICommands.CHANNEL_VDIV, ch=ch, value=config.voltage_div))
        
        # Set offset
        self.write(format_command(SCPICommands.CHANNEL_OFFSET, ch=ch, value=config.offset))
        
        # Set coupling
        self.write(format_command(SCPICommands.CHANNEL_COUPLING, ch=ch, mode=config.coupling.value))
        
        # Set probe ratio
        self.write(format_command(SCPICommands.CHANNEL_PROBE, ch=ch, ratio=config.probe_ratio))
        
        # Set bandwidth limit
        bwl_state = "ON" if config.bandwidth_limit else "OFF"
        self.write(format_command(SCPICommands.CHANNEL_BWLIMIT, ch=ch, state=bwl_state))
        
        logger.info(f"Configured channel {ch}")
    
    def enable_channel(self, channel: int, enabled: bool = True) -> None:
        """Enable or disable a channel."""
        state = "ON" if enabled else "OFF"
        self.write(format_command(SCPICommands.CHANNEL_TRACE, ch=channel, state=state))
    
    def get_channel_config(self, channel: int) -> dict:
        """
        Get current channel configuration.
        
        Args:
            channel: Channel number (1 or 2)
            
        Returns:
            dict with 'voltage_div', 'coupling', 'probe_ratio', 'offset'
        """
        vdiv = self.query(f"C{channel}:VDIV?").strip()
        coupling = self.query(f"C{channel}:CPL?").strip()
        probe = self.query(f"C{channel}:ATTN?").strip()
        offset = self.query(f"C{channel}:OFST?").strip()
        
        return {
            'voltage_div': vdiv,
            'coupling': coupling,
            'probe_ratio': probe,
            'offset': offset
        }
    
    def set_voltage_scale(self, channel: int, voltage_div: str) -> None:
        """Set voltage scale for a channel."""
        self.write(format_command(SCPICommands.CHANNEL_VDIV, ch=channel, value=voltage_div))
    
    def set_voltage_offset(self, channel: int, offset: str) -> None:
        """Set voltage offset for a channel."""
        self.write(format_command(SCPICommands.CHANNEL_OFFSET, ch=channel, value=offset))
    
    # Timebase control methods
    
    def configure_timebase(self, config: TimebaseConfig) -> None:
        """Configure timebase."""
        self.write(format_command(SCPICommands.TIME_DIV, value=config.time_div))
        self.write(format_command(SCPICommands.TIME_DELAY, value=config.delay))
        logger.info(f"Configured timebase: {config.time_div}/div")
    
    def get_timebase(self) -> dict:
        """
        Get current timebase settings.
        
        Returns:
            dict: {'time_div': str, 'delay': str} with current settings
        """
        time_div = self.query("TDIV?").strip()
        delay = self.query("TRDL?").strip()
        return {
            'time_div': time_div,
            'delay': delay
        }
    
    def set_time_scale(self, time_div: str) -> None:
        """Set time scale."""
        self.write(format_command(SCPICommands.TIME_DIV, value=time_div))
    
    # Trigger control methods
    
    def configure_trigger(self, config: TriggerConfig) -> None:
        """Configure trigger."""
        ch = config.source
        
        # Set trigger type and source
        trigger_cmd = format_command(
            SCPICommands.TRIGGER_SELECT,
            type=config.trigger_type.value,
            ch=ch,
            slope=config.slope.value
        )
        self.write(trigger_cmd)
        
        # Set trigger mode
        self.write(format_command(SCPICommands.TRIGGER_MODE, mode=config.mode.value))
        
        # Set trigger level
        self.write(format_command(SCPICommands.TRIGGER_LEVEL, ch=ch, level=config.level))
        
        # Set holdoff if specified
        if config.holdoff:
            self.write(format_command(SCPICommands.TRIGGER_HOLDOFF, time=config.holdoff))
        
        logger.info(f"Configured trigger on channel {ch}, mode: {config.mode.value}")
    
    def set_trigger_mode(self, mode: TriggerMode) -> None:
        """Set trigger mode."""
        self.write(format_command(SCPICommands.TRIGGER_MODE, mode=mode.value))
    
    def arm_trigger(self) -> None:
        """Arm the trigger for single acquisition."""
        self.write(SCPICommands.ARM_ACQUISITION)
    
    def stop_acquisition(self) -> None:
        """Stop acquisition."""
        self.write(SCPICommands.STOP_ACQUISITION)
    
    # Measurement methods
    
    def measure_channel(self, channel: int) -> Measurements:
        """Get all measurements from a channel."""
        measurements = Measurements(channel=channel)
        
        # Measure frequency using CYMOMETER (proven to work)
        try:
            result = self.query(SCPICommands.MEASURE_FREQ)
            # Parse CYMOMETER response: "CYMT 1.00E+03Hz"
            if "CYMT" in result:
                freq_str = result.split()[1]  # Get "1.00E+03Hz"
                measurements.frequency = self._parse_measurement(freq_str)
                # Calculate period from frequency
                if measurements.frequency and measurements.frequency > 0:
                    measurements.period = 1.0 / measurements.frequency
        except Exception as e:
            logger.debug(f"Failed to get frequency: {e}")
        
        # Try PAVA measurements first (fast but often returns ****)
        measurement_funcs = [
            ("peak_to_peak", SCPICommands.MEASURE_PKPK),
            ("amplitude", SCPICommands.MEASURE_AMPL),
            ("maximum", SCPICommands.MEASURE_MAX),
            ("minimum", SCPICommands.MEASURE_MIN),
            ("mean", SCPICommands.MEASURE_MEAN),
            ("rms", SCPICommands.MEASURE_RMS),
        ]
        
        pava_worked = False
        for attr_name, command_template in measurement_funcs:
            try:
                result = self.query(format_command(command_template, ch=channel))
                if "****" not in result:
                    value = self._parse_measurement(result)
                    setattr(measurements, attr_name, value)
                    pava_worked = True
            except Exception as e:
                logger.debug(f"Failed to get {attr_name}: {e}")
                continue
        
        # If PAVA didn't work, calculate from waveform data
        if not pava_worked:
            logger.debug("PAVA returned ****, calculating from waveform data")
            try:
                waveform = self.capture_waveform(channel, num_points=1000)
                if waveform and waveform.data_points:
                    import numpy as np
                    data = np.array(waveform.data_points)
                    
                    # Calculate statistics
                    measurements.maximum = float(np.max(data))
                    measurements.minimum = float(np.min(data))
                    measurements.peak_to_peak = measurements.maximum - measurements.minimum
                    measurements.amplitude = measurements.peak_to_peak / 2.0
                    measurements.mean = float(np.mean(data))
                    measurements.rms = float(np.sqrt(np.mean(data**2)))
                    
                    logger.debug(f"Calculated from waveform: Vpp={measurements.peak_to_peak:.3f}V")
            except Exception as e:
                logger.warning(f"Could not calculate from waveform: {e}")
        
        return measurements
    
    def _parse_measurement(self, value_str: str) -> Optional[float]:
        """Parse measurement value from response."""
        try:
            # Remove parameter name if present (e.g., "C1:PAVA PKPK,2.50V")
            if ',' in value_str:
                value_str = value_str.split(',')[1]
            
            # Remove units and convert to float
            value_str = value_str.strip().upper()
            
            # Handle different units
            multiplier = 1.0
            if value_str.endswith('GHZ'):
                multiplier = 1e9
                value_str = value_str[:-3]
            elif value_str.endswith('MHZ'):
                multiplier = 1e6
                value_str = value_str[:-3]
            elif value_str.endswith('KHZ'):
                multiplier = 1e3
                value_str = value_str[:-3]
            elif value_str.endswith('HZ'):
                value_str = value_str[:-2]
            elif value_str.endswith('V'):
                value_str = value_str[:-1]
            elif value_str.endswith('S'):
                value_str = value_str[:-1]
            
            # Handle SI prefixes
            if value_str.endswith('G'):
                multiplier *= 1e9
                value_str = value_str[:-1]
            elif value_str.endswith('M'):
                multiplier *= 1e6
                value_str = value_str[:-1]
            elif value_str.endswith('K'):
                multiplier *= 1e3
                value_str = value_str[:-1]
            elif value_str.endswith('U'):
                multiplier *= 1e-6
                value_str = value_str[:-1]
            elif value_str.endswith('N'):
                multiplier *= 1e-9
                value_str = value_str[:-1]
            
            return float(value_str) * multiplier
            
        except (ValueError, IndexError):
            return None
    
    def capture_screen(self) -> bytes:
        """
        Capture screen image from oscilloscope (MUCH faster than waveform data).
        
        Returns:
            bytes: BMP image data of oscilloscope screen
            
        Note: This is ~100x faster than capturing waveform data.
        Use this for visualization, use capture_waveform for data analysis.
        """
        import time
        
        old_timeout = self._instrument.timeout
        try:
            # Screen capture is fast, but give it 10 seconds just in case
            self._instrument.timeout = 10000
            
            logger.info("Requesting screen capture...")
            self.write("SCDP")
            time.sleep(0.5)  # Brief wait for screen capture
            
            screen_data = self.read_raw()
            logger.info(f"Received screen capture: {len(screen_data)} bytes")
            
            return screen_data
            
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            raise OscilloscopeError(f"Screen capture failed: {e}")
        finally:
            self._instrument.timeout = old_timeout
    
    def capture_waveform(self, channel: int, num_points: int = 1400) -> WaveformData:
        """
        Capture waveform data from a channel.
        
        Note: Siglent oscilloscopes are VERY slow at transferring waveform data.
        This can take 20-60 seconds depending on memory depth.
        
        Args:
            channel: Channel number (1 or 2)
            num_points: Desired number of points (actual may vary)
        """
        import time
        
        # Save original timeout
        old_timeout = self._instrument.timeout
        
        try:
            # Set sparse mode for faster capture
            # Sparse mode: 0=off, 2=every 4th, 4=every 10th, 6=every 20th, 10=every 100th
            # For ~700 points from 14K memory, use sparse mode 4 (every 10th point)
            if num_points <= 200:
                sparse_mode = 10  # Every 100th point
            elif num_points <= 500:
                sparse_mode = 6   # Every 20th point
            elif num_points <= 1000:
                sparse_mode = 4   # Every 10th point
            else:
                sparse_mode = 2   # Every 4th point
            
            logger.info(f"Setting sparse mode to {sparse_mode} for ~{num_points} points")
            self.write(f"WFSU SP,{sparse_mode},NP,0,FP,0")
            time.sleep(0.3)
            
            # Reduce memory depth for faster transfer
            logger.info("Setting memory depth to 7K for faster capture")
            self.write("MSIZ 7K")
            time.sleep(0.3)
            
            # Increase timeout to 60 seconds for waveform capture
            self._instrument.timeout = 60000
            
            # Request waveform data
            waveform_cmd = format_command(SCPICommands.WAVEFORM_DATA, ch=channel)
            logger.info(f"Requesting waveform: {waveform_cmd}")
            
            # Send command and wait longer for data preparation
            self.write(waveform_cmd)
            time.sleep(2)  # Give scope time to prepare data
            
            # Read raw data
            logger.info("Reading waveform data (may take 20-60 seconds)...")
            start_time = time.time()
            raw_data = self.read_raw()
            elapsed = time.time() - start_time
            logger.info(f"Received {len(raw_data)} bytes in {elapsed:.1f}s")
            
        except Exception as e:
            logger.error(f"Waveform capture failed: {e}")
            raise OscilloscopeError(f"Waveform capture timeout or error: {e}")
        finally:
            # Restore original timeout
            self._instrument.timeout = old_timeout
            # Reset to normal mode
            try:
                self.write("WFSU SP,0,NP,0,FP,0")  # Turn off sparse mode
            except:
                pass
        
        # Parse waveform data (Siglent format)
        # Format: descriptor header + data
        # This is simplified - actual parsing depends on format
        data_points = self._parse_waveform_data(raw_data)
        
        # Get time and voltage scales
        time_div = self.query(format_command(SCPICommands.TIME_DIV, value="?"))
        volt_div = self.query(format_command(SCPICommands.CHANNEL_VDIV, ch=channel, value="?"))
        
        # Create time array
        sample_rate = 1e9  # Placeholder - should query actual rate
        time_points = np.arange(len(data_points)) / sample_rate
        
        return WaveformData(
            channel=channel,
            num_points=len(data_points),
            sample_rate=sample_rate,
            voltage_scale=1.0,  # Parse from volt_div
            voltage_offset=0.0,
            time_scale=1.0,  # Parse from time_div
            data_points=data_points.tolist(),
            time_points=time_points.tolist()
        )
    
    def _parse_waveform_data(self, raw_data: bytes) -> np.ndarray:
        """Parse raw waveform data from Siglent format."""
        try:
            # Siglent uses IEEE 488.2 format: #<N><digits><data>
            # where N is number of digits, digits is byte count, data is waveform
            
            # Find the start of the binary block
            if raw_data.startswith(b'C') and b'#9' in raw_data:
                # Format: "C1:WF DAT2,#9000001400<binary data>"
                header_start = raw_data.find(b'#9')
                if header_start < 0:
                    logger.error("Could not find #9 header")
                    return np.array([])
                
                # Skip "#9" and read 9 digits for byte count
                byte_count_str = raw_data[header_start+2:header_start+11]
                byte_count = int(byte_count_str)
                
                # Extract binary data
                data_start = header_start + 11
                data_end = data_start + byte_count
                binary_data = raw_data[data_start:data_end]
                
                # Convert to voltage values (int8 format, scaled)
                values = np.frombuffer(binary_data, dtype=np.int8)
                
                # Get vertical scale to convert to volts
                # Values are typically -127 to 127 representing the screen divisions
                # Need to scale by volts/div and account for probe ratio
                vdiv_response = self.query(f"C1:VDIV?")
                vdiv = self._parse_measurement(vdiv_response.split()[1]) if vdiv_response else 1.0
                
                # Each division is typically 25 samples on Siglent
                # Convert ADC counts to volts
                voltage_values = (values / 25.0) * vdiv
                
                return voltage_values.astype(float)
            else:
                logger.error(f"Unexpected waveform format: {raw_data[:50]}")
                return np.array([])
                
        except Exception as e:
            logger.error(f"Waveform parsing error: {e}")
            return np.array([])
    
    # Auto setup
    
    def auto_setup(self) -> None:
        """Perform auto setup."""
        self.write(SCPICommands.AUTO_SETUP)
        time.sleep(3)  # Wait for auto setup to complete
        logger.info("Auto setup completed")
    
    # Status methods
    
    def get_status(self) -> ScopeStatus:
        """Get complete oscilloscope status."""
        idn = self.query(SCPICommands.IDENTIFY)
        parts = idn.split(',')
        
        manufacturer = parts[0] if len(parts) > 0 else "Unknown"
        model = parts[1] if len(parts) > 1 else "Unknown"
        serial = parts[2] if len(parts) > 2 else "Unknown"
        firmware = parts[3] if len(parts) > 3 else "Unknown"
        
        # Get basic configuration (simplified)
        channels = []
        for ch in range(1, 3):  # Assuming 2 channels
            channels.append(ChannelConfig(
                channel=ch,
                enabled=True,
                voltage_div="1V",
                offset="0V"
            ))
        
        timebase = TimebaseConfig(time_div="1MS", delay="0S")
        trigger = TriggerConfig(source=1, mode=TriggerMode.AUTO)
        
        return ScopeStatus(
            connected=self._connected,
            model=model,
            serial_number=serial,
            firmware_version=firmware,
            channels=channels,
            timebase=timebase,
            trigger=trigger,
            acquisition_running=True
        )
    
    def __enter__(self):
        """Context manager entry."""
        if not self._connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False

