"""Example: Natural language agent for oscilloscope control."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.agent import OscilloscopeAgent


def demo_commands():
    """Demonstrate agent with predefined commands."""
    
    print("=" * 60)
    print("Oscilloscope Natural Language Agent Demo")
    print("=" * 60)
    
    # Initialize agent
    print("\nInitializing agent...")
    agent = OscilloscopeAgent()
    
    # List of demo commands
    commands = [
        "Get the current oscilloscope status",
        "Set channel 1 to 2 volts per division",
        "Change the timebase to 1 millisecond per division",
        "Configure trigger on rising edge at 1.5 volts on channel 1",
        "Measure the frequency on channel 1",
        "What's the peak-to-peak voltage on channel 1?",
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"\n{'-'*60}")
        print(f"Command {i}: {command}")
        print(f"{'-'*60}")
        
        try:
            response = agent.execute(command)
            print(f"\nAgent Response:\n{response}")
        except Exception as e:
            print(f"\nError: {e}")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
    
    # Cleanup
    agent.disconnect()


def interactive_mode():
    """Run agent in interactive mode."""
    
    print("=" * 60)
    print("Oscilloscope Natural Language Agent - Interactive Mode")
    print("=" * 60)
    print("\nStarting interactive session...")
    print("You can ask questions like:")
    print("  - 'Measure frequency on channel 1'")
    print("  - 'Set channel 2 to 500mV per division'")
    print("  - 'Auto setup the oscilloscope'")
    print("  - 'What's the voltage on channel 1?'")
    print("\nType 'quit' to exit\n")
    
    # Initialize and run chat
    with OscilloscopeAgent() as agent:
        agent.chat()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Run interactive mode
        interactive_mode()
    else:
        # Run demo with predefined commands
        demo_commands()
        
        print("\n\nTip: Run with --interactive flag for interactive mode:")
        print("  python agent_demo.py --interactive")

