#!/usr/bin/env python3
"""Test screen capture functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.oscilloscope.driver import OscilloscopeDriver

def test_screen_capture():
    """Test fast screen capture."""
    print("=" * 60)
    print("Testing Screen Capture (Fast Method)")
    print("=" * 60)
    
    resource = "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR"
    driver = OscilloscopeDriver(resource_name=resource)
    
    try:
        print("\n1. Connecting...")
        if not driver.connect():
            print("❌ Failed to connect")
            return
        print("✅ Connected")
        
        print("\n2. Capturing screen (should take 2-3 seconds)...")
        import time
        start = time.time()
        
        screen_data = driver.capture_screen()
        
        elapsed = time.time() - start
        print(f"✅ Captured {len(screen_data)} bytes in {elapsed:.1f} seconds")
        
        print("\n3. Saving to file...")
        with open("oscilloscope_screen.bmp", "wb") as f:
            f.write(screen_data)
        print("✅ Saved to oscilloscope_screen.bmp")
        
        print("\n" + "=" * 60)
        print("✅ Screen capture works! Much faster than waveform.")
        print("=" * 60)
        print("\n💡 Use screen capture in web app for quick visualization!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.disconnect()

if __name__ == "__main__":
    test_screen_capture()

