"""SCPI command constants for Siglent oscilloscopes."""

from typing import Dict


class SCPICommands:
    """SCPI commands for Siglent SDS series oscilloscopes."""
    
    # System commands
    IDENTIFY = "*IDN?"
    RESET = "*RST"
    CLEAR_STATUS = "*CLS"
    
    # Channel commands
    CHANNEL_TRACE = "C{ch}:TRA {state}"  # ON/OFF
    CHANNEL_VDIV = "C{ch}:VDIV {value}"  # Voltage per division
    CHANNEL_OFFSET = "C{ch}:OFST {value}"  # Vertical offset
    CHANNEL_COUPLING = "C{ch}:CPL {mode}"  # Coupling mode
    CHANNEL_PROBE = "C{ch}:ATTN {ratio}"  # Probe ratio
    CHANNEL_BWLIMIT = "C{ch}:BWL {state}"  # Bandwidth limit ON/OFF
    
    # Timebase commands
    TIME_DIV = "TDIV {value}"  # Time per division
    TIME_DELAY = "TRDL {value}"  # Horizontal delay
    SAMPLE_RATE = "SARA?"  # Sample rate query
    
    # Trigger commands
    TRIGGER_SELECT = "TRSE {type},SR,C{ch},{slope},OFF"  # Trigger setup
    TRIGGER_MODE = "TRMD {mode}"  # AUTO, NORM, SINGLE, STOP
    TRIGGER_LEVEL = "C{ch}:TRLV {level}"  # Trigger level
    TRIGGER_HOLDOFF = "TRHLD {time}"  # Trigger holdoff
    TRIGGER_STATUS = "TRMD?"  # Trigger status query
    
    # Measurement commands - Parameter values (PAVA)
    MEASURE_FREQ = "CYMOMETER?"  # Frequency (using frequency counter - more reliable)
    MEASURE_FREQ_PAVA = "C{ch}:PAVA? FREQ"  # Frequency (alternative via PAVA)
    MEASURE_PERIOD = "C{ch}:PAVA? PERI"  # Period
    MEASURE_PKPK = "C{ch}:PAVA? PKPK"  # Peak-to-peak
    MEASURE_AMPL = "C{ch}:PAVA? AMPL"  # Amplitude
    MEASURE_MAX = "C{ch}:PAVA? MAX"  # Maximum
    MEASURE_MIN = "C{ch}:PAVA? MIN"  # Minimum
    MEASURE_MEAN = "C{ch}:PAVA? MEAN"  # Mean
    MEASURE_RMS = "C{ch}:PAVA? RMS"  # RMS
    MEASURE_RISE = "C{ch}:PAVA? RISE"  # Rise time
    MEASURE_FALL = "C{ch}:PAVA? FALL"  # Fall time
    MEASURE_PWID = "C{ch}:PAVA? PWID"  # Positive width
    MEASURE_NWID = "C{ch}:PAVA? NWID"  # Negative width
    
    # Enable parameter measurements
    PARAM_ENABLE = "PAMD ON"  # Parameter measurement display ON
    
    # Waveform commands
    WAVEFORM_SETUP = "WFSU SP,{pts},NP,0,FP,0"  # Waveform setup
    WAVEFORM_DATA = "C{ch}:WF? DAT2"  # Get waveform data
    WAVEFORM_PREAMBLE = "C{ch}:WF? DESC"  # Get waveform preamble
    
    # Acquisition commands
    ARM_ACQUISITION = "ARM"  # Start acquisition
    STOP_ACQUISITION = "STOP"  # Stop acquisition
    AUTO_SETUP = "ASET"  # Auto setup
    
    # Memory and storage
    MEMORY_SIZE = "MSIZ?"  # Memory depth query
    SAVE_WAVEFORM = "STORE C{ch},FILE,'HDD,{filename}'"
    RECALL_WAVEFORM = "RECALL C{ch},FILE,'HDD,{filename}'"
    
    # Screen capture
    SCREEN_DUMP = "SCDP"  # Screen dump
    HARDCOPY_START = "HCSU DEV,{device},FORMAT,{format}"


# Mapping of common parameter values
VOLTAGE_SCALES = [
    "500UV", "1MV", "2MV", "5MV", "10MV", "20MV", "50MV",
    "100MV", "200MV", "500MV", "1V", "2V", "5V", "10V"
]

TIME_SCALES = [
    "1NS", "2NS", "5NS", "10NS", "20NS", "50NS", "100NS", "200NS", "500NS",
    "1US", "2US", "5US", "10US", "20US", "50US", "100US", "200US", "500US",
    "1MS", "2MS", "5MS", "10MS", "20MS", "50MS", "100MS", "200MS", "500MS",
    "1S", "2S", "5S", "10S", "20S", "50S", "100S"
]

PROBE_RATIOS = [1, 10, 100, 1000]


def format_command(template: str, **kwargs: str) -> str:
    """Format a command template with parameters."""
    return template.format(**kwargs)

