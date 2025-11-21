"""Tests for oscilloscope driver."""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.oscilloscope.driver import OscilloscopeDriver, OscilloscopeError
from src.oscilloscope.models import (
    ChannelConfig,
    TimebaseConfig,
    TriggerConfig,
    CouplingMode,
    TriggerMode,
    TriggerSlope
)


@pytest.fixture
def mock_resource_manager():
    """Mock PyVISA resource manager."""
    with patch('pyvisa.ResourceManager') as mock_rm:
        # Create mock instrument
        mock_instrument = MagicMock()
        mock_instrument.query.return_value = "Siglent Technologies,SDS1202X-E,SDS1EEFX803161,1.3.27"
        
        # Configure mock resource manager
        mock_rm_instance = Mock()
        mock_rm_instance.open_resource.return_value = mock_instrument
        mock_rm.return_value = mock_rm_instance
        
        yield mock_rm_instance, mock_instrument


def test_driver_initialization():
    """Test driver initialization."""
    driver = OscilloscopeDriver("TEST::RESOURCE")
    assert driver.resource_name == "TEST::RESOURCE"
    assert driver.timeout == 5000
    assert not driver._connected


def test_driver_connect(mock_resource_manager):
    """Test connecting to oscilloscope."""
    mock_rm, mock_instrument = mock_resource_manager
    
    driver = OscilloscopeDriver("TEST::RESOURCE")
    driver.connect()
    
    assert driver._connected
    mock_rm.open_resource.assert_called_once_with("TEST::RESOURCE")


def test_driver_disconnect(mock_resource_manager):
    """Test disconnecting from oscilloscope."""
    mock_rm, mock_instrument = mock_resource_manager
    
    driver = OscilloscopeDriver("TEST::RESOURCE")
    driver.connect()
    driver.disconnect()
    
    assert not driver._connected
    mock_instrument.close.assert_called_once()


def test_configure_channel(mock_resource_manager):
    """Test channel configuration."""
    mock_rm, mock_instrument = mock_resource_manager
    
    driver = OscilloscopeDriver("TEST::RESOURCE", auto_connect=True)
    
    config = ChannelConfig(
        channel=1,
        enabled=True,
        voltage_div="2V",
        offset="0V",
        coupling=CouplingMode.DC_1M
    )
    
    driver.configure_channel(config)
    
    # Verify write calls
    assert mock_instrument.write.called
    write_calls = [call[0][0] for call in mock_instrument.write.call_args_list]
    assert any("C1:TRA ON" in call for call in write_calls)
    assert any("C1:VDIV 2V" in call for call in write_calls)


def test_configure_timebase(mock_resource_manager):
    """Test timebase configuration."""
    mock_rm, mock_instrument = mock_resource_manager
    
    driver = OscilloscopeDriver("TEST::RESOURCE", auto_connect=True)
    
    config = TimebaseConfig(time_div="1MS", delay="0S")
    driver.configure_timebase(config)
    
    write_calls = [call[0][0] for call in mock_instrument.write.call_args_list]
    assert any("TDIV 1MS" in call for call in write_calls)


def test_configure_trigger(mock_resource_manager):
    """Test trigger configuration."""
    mock_rm, mock_instrument = mock_resource_manager
    
    driver = OscilloscopeDriver("TEST::RESOURCE", auto_connect=True)
    
    config = TriggerConfig(
        source=1,
        mode=TriggerMode.AUTO,
        slope=TriggerSlope.RISING,
        level="1.5V"
    )
    
    driver.configure_trigger(config)
    
    write_calls = [call[0][0] for call in mock_instrument.write.call_args_list]
    assert any("TRMD AUTO" in call for call in write_calls)
    assert any("C1:TRLV 1.5V" in call for call in write_calls)


def test_measure_channel(mock_resource_manager):
    """Test channel measurements."""
    mock_rm, mock_instrument = mock_resource_manager
    
    # Setup mock responses
    mock_instrument.query.side_effect = [
        "Siglent Technologies,SDS1202X-E,SDS1EEFX803161,1.3.27",  # IDN
        "C1:PAVA FREQ,1000.0HZ",  # Frequency
        "C1:PAVA PERI,0.001S",     # Period
        "C1:PAVA PKPK,5.0V",       # Peak-to-peak
        "C1:PAVA AMPL,2.5V",       # Amplitude
        "C1:PAVA MAX,2.5V",        # Max
        "C1:PAVA MIN,-2.5V",       # Min
        "C1:PAVA MEAN,0.0V",       # Mean
        "C1:PAVA RMS,1.77V"        # RMS
    ]
    
    driver = OscilloscopeDriver("TEST::RESOURCE", auto_connect=True)
    measurements = driver.measure_channel(1)
    
    assert measurements.channel == 1
    assert measurements.frequency == 1000.0
    assert measurements.peak_to_peak == 5.0


def test_parse_measurement():
    """Test measurement value parsing."""
    driver = OscilloscopeDriver("TEST::RESOURCE")
    
    # Test various formats
    assert driver._parse_measurement("C1:PAVA FREQ,1.5KHZ") == 1500.0
    assert driver._parse_measurement("C1:PAVA PKPK,2.5V") == 2.5
    assert driver._parse_measurement("500MV") == 0.5
    assert driver._parse_measurement("1.5MHZ") == 1500000.0


def test_context_manager(mock_resource_manager):
    """Test using driver as context manager."""
    mock_rm, mock_instrument = mock_resource_manager
    
    with OscilloscopeDriver("TEST::RESOURCE") as driver:
        assert driver._connected
    
    # Should be disconnected after exit
    mock_instrument.close.assert_called()


def test_error_handling():
    """Test error handling when not connected."""
    driver = OscilloscopeDriver("TEST::RESOURCE")
    
    with pytest.raises(OscilloscopeError):
        driver.write("*RST")
    
    with pytest.raises(OscilloscopeError):
        driver.query("*IDN?")

