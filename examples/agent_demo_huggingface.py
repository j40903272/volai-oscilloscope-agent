"""Demo script showing how to use the agent with HuggingFace local models."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.agent import OscilloscopeAgent
from src.oscilloscope.driver import OscilloscopeError


def main():
    """Run demo with HuggingFace model."""
    
    print("=" * 60)
    print("Oscilloscope Agent Demo - HuggingFace Local Model")
    print("=" * 60)
    print()
    
    # Configuration
    resource_name = os.getenv(
        "OSCILLOSCOPE_RESOURCE",
        "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR"
    )
    
    # Available models (from smallest to largest)
    models = {
        "1": ("Qwen/Qwen2.5-0.5B-Instruct", "~1GB"),
        "2": ("Qwen/Qwen2.5-1.5B-Instruct", "~3GB"),
        "3": ("microsoft/Phi-3-mini-4k-instruct", "~8GB"),
        "4": ("google/gemma-2-2b-it", "~5GB"),
    }
    
    print("Available HuggingFace Models:")
    for key, (name, size) in models.items():
        print(f"  {key}. {name} ({size})")
    print()
    
    choice = input("Select model (1-4) [1]: ").strip() or "1"
    model_name, model_size = models.get(choice, models["1"])
    
    print(f"\nSelected: {model_name} ({model_size})")
    print(f"Note: First run will download the model (~{model_size})")
    print()
    
    # Create agent
    print("Initializing agent with HuggingFace model...")
    print("This may take a minute on first run...")
    print()
    
    try:
        # Option 1: Connect to real oscilloscope
        connect = input("Connect to oscilloscope? (y/n) [n]: ").strip().lower() == 'y'
        
        agent = OscilloscopeAgent(
            resource_name=resource_name,
            model_type="huggingface",
            hf_model_name=model_name,
            connect_on_init=connect
        )
        
        if connect:
            print("✅ Connected to oscilloscope!")
        else:
            print("⚠️  Running in offline mode (oscilloscope commands will fail)")
        
        print(f"✅ Agent initialized with {model_name}")
        print()
        
        # Interactive chat
        print("=" * 60)
        print("Chat with the agent (type 'quit' to exit)")
        print("=" * 60)
        print()
        
        # Example queries
        examples = [
            "What's the oscilloscope status?",
            "Measure frequency on channel 1",
            "Set channel 1 voltage to 100MV",
            "Auto setup the oscilloscope"
        ]
        
        print("💡 Example queries:")
        for i, example in enumerate(examples, 1):
            print(f"  {i}. {example}")
        print()
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\nAgent: ", end="", flush=True)
                response = agent.execute(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
    except OscilloscopeError as e:
        print(f"❌ Oscilloscope error: {e}")
        print("Tip: Check that the oscilloscope is connected and the resource name is correct")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'agent' in locals():
            agent.disconnect()
            print("\nDisconnected from oscilloscope")


if __name__ == "__main__":
    main()

