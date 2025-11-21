"""Example: Test natural language agent WITHOUT oscilloscope (demo mode)."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.agent import OscilloscopeAgent


def demo_offline():
    """Test agent in offline mode (without oscilloscope connection)."""
    
    print("=" * 60)
    print("Oscilloscope Agent - OFFLINE DEMO MODE")
    print("(Oscilloscope not required)")
    print("=" * 60)
    
    # Initialize agent WITHOUT connecting to oscilloscope
    print("\nInitializing agent (offline mode)...")
    agent = OscilloscopeAgent(connect_on_init=False)
    
    print("\n✓ Agent initialized successfully!")
    print("\nNote: Commands that require actual oscilloscope will fail,")
    print("but the agent's natural language processing is working.\n")
    
    # Test commands
    commands = [
        "Hello, can you help me with the oscilloscope?",
        "What tools do you have available?",
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"\n{'-'*60}")
        print(f"Test {i}: {command}")
        print(f"{'-'*60}")
        
        try:
            response = agent.execute(command)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"\nError: {e}")
    
    print("\n" + "=" * 60)
    print("Offline demo completed!")
    print("=" * 60)
    
    agent.disconnect()


if __name__ == "__main__":
    demo_offline()

