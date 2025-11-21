# Using Local HuggingFace Models

This guide explains how to use local HuggingFace models (like Qwen3-0.6B) with the Oscilloscope Agent as an alternative to Claude.

## Features

- **Offline Operation**: Run models locally without API calls
- **Cost-Free**: No API costs after initial download
- **Privacy**: Data stays on your machine
- **Multiple Models**: Support for Qwen, Phi-3, Gemma, and more

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `transformers` - HuggingFace transformers library
- `torch` - PyTorch for model inference
- `accelerate` - Faster model loading
- `langchain-huggingface` - LangChain integration

### 2. First Time Setup

On first run, the model will be downloaded automatically from HuggingFace (~1-3GB depending on model size). Subsequent runs will use the cached model.

## Supported Models

### Recommended Models

1. **Qwen/Qwen2.5-0.5B-Instruct** (Default)
   - Size: ~1GB
   - Speed: Very fast
   - Quality: Good for basic tasks
   - Best for: Quick responses, low memory systems

2. **Qwen/Qwen2.5-1.5B-Instruct**
   - Size: ~3GB
   - Speed: Fast
   - Quality: Better reasoning
   - Best for: Balance of speed and quality

3. **Qwen/Qwen2.5-3B-Instruct**
   - Size: ~6GB
   - Speed: Moderate
   - Quality: Best quality
   - Best for: Complex reasoning tasks

4. **microsoft/Phi-3-mini-4k-instruct**
   - Size: ~8GB
   - Speed: Moderate
   - Quality: Excellent
   - Best for: High-quality responses

5. **google/gemma-2-2b-it**
   - Size: ~5GB
   - Speed: Fast
   - Quality: Very good
   - Best for: General purpose

## Usage

### Option 1: Streamlit Web Interface

1. Start the app:
```bash
streamlit run app.py
```

2. In the sidebar:
   - Select **Model Type**: Choose "huggingface"
   - Select **HuggingFace Model**: Choose your preferred model
   - Click **Connect**

3. Use the AI Assistant tab to chat with the model

### Option 2: Python Script

```python
from src.agent.agent import OscilloscopeAgent

# Create agent with HuggingFace model
agent = OscilloscopeAgent(
    resource_name="USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR",
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct",
    connect_on_init=True
)

# Use the agent
response = agent.execute("Measure frequency on channel 1")
print(response)

# Cleanup
agent.disconnect()
```

### Option 3: Example Script

```bash
python examples/agent_demo_huggingface.py
```

This script:
- Lets you choose a model
- Optionally connects to oscilloscope
- Provides interactive chat interface

### Option 4: Test Model Loading

```bash
python test_huggingface_model.py
```

Quick test to verify HuggingFace integration works.

## Model Selection Guide

### Choose Based on Your Hardware

**Low-end System (8GB RAM, no GPU)**
- Use: `Qwen/Qwen2.5-0.5B-Instruct`
- Fast and lightweight

**Mid-range System (16GB RAM, optional GPU)**
- Use: `Qwen/Qwen2.5-1.5B-Instruct` or `google/gemma-2-2b-it`
- Good balance

**High-end System (32GB+ RAM, GPU)**
- Use: `Qwen/Qwen2.5-3B-Instruct` or `microsoft/Phi-3-mini-4k-instruct`
- Best quality

### GPU Acceleration

If you have a CUDA-compatible GPU:
- Models will automatically use GPU
- Much faster inference (10-100x)

If you have an Apple Silicon Mac:
- Models will use Metal Performance Shaders (MPS)
- Significant speedup on M1/M2/M3

## API Comparison

### Claude (Cloud)
✅ Highest quality responses
✅ No local resources needed
✅ Always up-to-date
❌ Requires API key
❌ Costs per request
❌ Requires internet
❌ Data sent to cloud

### HuggingFace (Local)
✅ Free after download
✅ Works offline
✅ Data stays local
✅ No API limits
❌ Requires local resources
❌ Initial download needed
❌ Quality varies by model
❌ Slower than Claude

## Advanced Configuration

### Using Custom Models

```python
from src.agent.llm_wrapper import create_llm

# Load any HuggingFace model
llm = create_llm(
    model_type="huggingface",
    model_name="your-model-name",
    max_new_tokens=512,      # Maximum response length
    temperature=0.1,          # Lower = more deterministic
    load_in_8bit=False,      # Enable 8-bit quantization
    load_in_4bit=False       # Enable 4-bit quantization
)
```

### Quantization for Lower Memory

Use quantization for very large models:

```python
llm = create_llm(
    model_type="huggingface",
    model_name="Qwen/Qwen2.5-3B-Instruct",
    load_in_8bit=True  # Reduces memory by ~50%
)
```

### Model Caching

Models are cached in:
- Linux/Mac: `~/.cache/huggingface/`
- Windows: `%USERPROFILE%\.cache\huggingface\`

To clear cache and re-download:
```bash
rm -rf ~/.cache/huggingface/
```

## Troubleshooting

### "Out of Memory" Error

1. Use a smaller model (0.5B instead of 1.5B)
2. Enable quantization (`load_in_8bit=True`)
3. Close other applications

### Slow First Run

First run downloads the model. This is normal and only happens once.

### Model Not Loading

Check you have enough disk space:
- 0.5B model: ~1GB
- 1.5B model: ~3GB
- 3B model: ~6GB

### Poor Quality Responses

1. Try a larger model (1.5B or 3B)
2. Adjust temperature (lower = more deterministic)
3. Consider using Claude for complex tasks

## Examples

### Example 1: Basic Usage

```python
from src.agent.agent import OscilloscopeAgent

agent = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct"
)

print(agent.execute("Get oscilloscope status"))
```

### Example 2: Model Comparison

```python
# Test with Claude
agent_claude = OscilloscopeAgent(model_type="claude")
response1 = agent_claude.execute("Measure channel 1")

# Test with HuggingFace
agent_hf = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-1.5B-Instruct"
)
response2 = agent_hf.execute("Measure channel 1")

print("Claude:", response1)
print("HuggingFace:", response2)
```

### Example 3: Context Manager

```python
with OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct"
) as agent:
    response = agent.execute("Auto setup")
    print(response)
# Automatically disconnects
```

## Performance Tips

1. **Use GPU if available** - 10-100x faster
2. **Choose smaller models** for real-time responses
3. **Enable quantization** for memory-constrained systems
4. **Cache models** - download once, use many times
5. **Adjust max_new_tokens** - lower = faster responses

## See Also

- [QUICKSTART.md](QUICKSTART.md) - General setup guide
- [examples/agent_demo_huggingface.py](examples/agent_demo_huggingface.py) - Interactive demo
- [test_huggingface_model.py](test_huggingface_model.py) - Quick test

