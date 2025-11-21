"""Quick test script to verify HuggingFace model loading."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.llm_wrapper import create_llm


def test_huggingface_model():
    """Test that HuggingFace model can be loaded and used."""
    
    print("=" * 60)
    print("Testing HuggingFace Model Integration")
    print("=" * 60)
    print()
    
    # Test with smallest Qwen model
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    
    print(f"Loading model: {model_name}")
    print("This may take a minute on first run...")
    print()
    
    try:
        # Create model
        llm = create_llm(
            model_type="huggingface",
            model_name=model_name,
            max_new_tokens=256,
            temperature=0.1
        )
        
        print("✅ Model loaded successfully!")
        print()
        
        # Test with simple prompt
        from langchain_core.messages import HumanMessage
        
        test_prompts = [
            "What is 2+2?",
            "List three colors.",
            "Complete: The capital of France is"
        ]
        
        print("Testing model responses:")
        print("-" * 60)
        
        for prompt in test_prompts:
            print(f"\nQ: {prompt}")
            print("A: ", end="", flush=True)
            
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            
            print(response.content)
        
        print()
        print("-" * 60)
        print("✅ All tests passed!")
        print()
        print("You can now use HuggingFace models in the agent!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = test_huggingface_model()
    sys.exit(0 if success else 1)

