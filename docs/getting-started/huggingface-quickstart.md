# Quick Start: HuggingFace Local Models

Get started with local AI models in 3 steps!

## Step 1: Install Dependencies (2 minutes)

```bash
cd "/Users/interview/Documents/YUN DA"
pip install -r requirements.txt
```

This installs HuggingFace transformers, PyTorch, and other dependencies.

## Step 2: Test the Setup (2-5 minutes)

```bash
python test_huggingface_model.py
```

**First run**: Downloads Qwen 0.5B model (~1GB) - takes 2-5 minutes
**Subsequent runs**: Uses cached model - instant!

Expected output:
```
Testing HuggingFace Model Integration
=================================================

Loading model: Qwen/Qwen2.5-0.5B-Instruct
This may take a minute on first run...

✅ Model loaded successfully!

Testing model responses:
--------------------------------------------------

Q: What is 2+2?
A: 4

Q: List three colors.
A: Red, Blue, Green

✅ All tests passed!
```

## Step 3: Use It!

### Option A: Web Interface (Recommended)

```bash
streamlit run app.py
```

Then:
1. In sidebar, select **Model Type**: "huggingface"
2. Select **HuggingFace Model**: "Qwen/Qwen2.5-0.5B-Instruct"
3. Click **Connect**
4. Go to **AI Assistant** tab and chat!

### Option B: Interactive Demo

```bash
python examples/agent_demo_huggingface.py
```

Choose a model and start chatting!

### Option C: Python Code

```python
from src.agent.agent import OscilloscopeAgent

# Create agent with local model
agent = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct",
    connect_on_init=False  # Set True to connect to oscilloscope
)

# Use it!
response = agent.execute("What can you help me with?")
print(response)
```

## Available Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **Qwen/Qwen2.5-0.5B-Instruct** | ~1GB | ⚡⚡⚡ | ⭐⭐ | Quick responses, low memory |
| **Qwen/Qwen2.5-1.5B-Instruct** | ~3GB | ⚡⚡ | ⭐⭐⭐ | Balanced performance |
| **Qwen/Qwen2.5-3B-Instruct** | ~6GB | ⚡ | ⭐⭐⭐⭐ | Best quality |
| **microsoft/Phi-3-mini-4k-instruct** | ~8GB | ⚡ | ⭐⭐⭐⭐ | High quality |
| **google/gemma-2-2b-it** | ~5GB | ⚡⚡ | ⭐⭐⭐ | General purpose |

**Recommendation**: Start with **Qwen/Qwen2.5-0.5B-Instruct** - it's fast and works on any system!

## Comparison: Claude vs Local

| Feature | Claude | HuggingFace |
|---------|--------|-------------|
| **Cost** | ❌ Pay per request | ✅ Free after download |
| **Internet** | ❌ Required | ✅ Works offline |
| **Privacy** | ❌ Data sent to cloud | ✅ Data stays local |
| **Quality** | ⭐⭐⭐⭐⭐ Best | ⭐⭐⭐ Good |
| **Speed** | ⚡⚡⚡ Fast | ⚡⚡ Moderate (GPU helps) |
| **Setup** | ✅ Just API key | ❌ Download model |

**Use Claude for**: Best quality, cloud convenience
**Use HuggingFace for**: Privacy, offline, cost savings

## Troubleshooting

### ❌ Out of Memory

**Solution**: Use smaller model
```python
agent = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct"  # Smallest option
)
```

### ❌ Too Slow

**Solutions**:
1. Use GPU (10-100x faster)
2. Use smaller model
3. Reduce max tokens:
```python
from src.agent.llm_wrapper import create_llm

llm = create_llm(
    model_type="huggingface",
    model_name="Qwen/Qwen2.5-0.5B-Instruct",
    max_new_tokens=256  # Shorter responses = faster
)
```

### ❌ Model Download Failed

**Solution**: Check internet connection and disk space
- Need: 1-6GB free space
- Location: `~/.cache/huggingface/`

### ❌ Import Error

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

## Examples

### Example 1: Compare Models

```python
from src.agent.agent import OscilloscopeAgent

# Test Claude
agent1 = OscilloscopeAgent(model_type="claude")
print("Claude:", agent1.execute("Hello!"))

# Test HuggingFace
agent2 = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct"
)
print("HuggingFace:", agent2.execute("Hello!"))
```

### Example 2: Oscilloscope Control

```python
from src.agent.agent import OscilloscopeAgent

# Create agent with local model
agent = OscilloscopeAgent(
    resource_name="USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR",
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-1.5B-Instruct",
    connect_on_init=True
)

# Use natural language!
print(agent.execute("Measure frequency on channel 1"))
print(agent.execute("Set channel 1 voltage to 100MV"))
print(agent.execute("What's the oscilloscope status?"))

agent.disconnect()
```

### Example 3: Offline Mode

```python
# Perfect for demos, development, or privacy
agent = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct",
    connect_on_init=False  # No oscilloscope needed
)

# Still works for questions!
print(agent.execute("What can you help me with?"))
print(agent.execute("How do I measure frequency?"))
```

## Hardware Acceleration

### NVIDIA GPU (CUDA)
✅ Automatically detected
✅ 10-100x faster
✅ No configuration needed

### Apple Silicon (M1/M2/M3)
✅ Automatically uses Metal Performance Shaders
✅ 5-20x faster
✅ No configuration needed

### CPU Only
✅ Still works!
⚠️ Slower (1-5 tokens/sec)
💡 Use smallest model (0.5B)

## Next Steps

1. ✅ **Read full docs**: `HUGGINGFACE_MODELS.md`
2. ✅ **See changes**: `CHANGES_HUGGINGFACE.md`
3. ✅ **Try demo**: `python examples/agent_demo_huggingface.py`
4. ✅ **Build something!**

## Need Help?

- 📖 Full documentation: `HUGGINGFACE_MODELS.md`
- 🔧 Troubleshooting: See "Troubleshooting" section in `HUGGINGFACE_MODELS.md`
- 💡 Examples: `examples/agent_demo_huggingface.py`
- 🧪 Quick test: `python test_huggingface_model.py`

---

**Have fun with local AI! 🚀**

