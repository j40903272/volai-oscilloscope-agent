# HuggingFace Model Integration - Summary of Changes

## Overview

Added support for local HuggingFace models (including Qwen3-0.5B/1.5B/3B) alongside Claude. Users can now choose between cloud-based Claude API or local open-source models.

## Files Added

### 1. `src/agent/llm_wrapper.py` (NEW)
- **Purpose**: Unified interface for both Claude and HuggingFace models
- **Key Classes**:
  - `HuggingFaceChatWrapper`: Makes HF models compatible with LangChain chat interface
  - `LLMFactory`: Factory pattern for creating model instances
  - `ModelType`: Enum for model types (CLAUDE, HUGGINGFACE)
- **Key Functions**:
  - `create_llm()`: Convenience function to create any model type

### 2. `examples/agent_demo_huggingface.py` (NEW)
- **Purpose**: Interactive demo for HuggingFace models
- **Features**:
  - Model selection menu
  - Optional oscilloscope connection
  - Interactive chat interface
  - Example queries

### 3. `test_huggingface_model.py` (NEW)
- **Purpose**: Quick test to verify HF integration
- **Features**:
  - Loads Qwen 0.5B model
  - Tests basic inference
  - Validates setup

### 4. `HUGGINGFACE_MODELS.md` (NEW)
- **Purpose**: Complete documentation for using HF models
- **Contents**:
  - Installation guide
  - Model recommendations
  - Usage examples
  - Troubleshooting
  - Performance tips

### 5. `CHANGES_HUGGINGFACE.md` (THIS FILE)
- **Purpose**: Summary of all changes

## Files Modified

### 1. `requirements.txt`
**Added dependencies:**
```
transformers==4.44.2        # HuggingFace transformers
torch==2.4.1                # PyTorch for inference
accelerate==0.34.2          # Faster model loading
sentencepiece==0.2.0        # Tokenization
langchain-huggingface==0.1.0  # LangChain integration
```

### 2. `src/agent/agent.py`
**Changes:**
- Added `model_type` parameter to `__init__` (default: "claude")
- Added `hf_model_name` parameter for HuggingFace models
- Import `create_llm` from `llm_wrapper`
- Model selection logic:
  - If `model_type="claude"`: Uses Claude API
  - If `model_type="huggingface"`: Loads local HF model

**New Parameters:**
```python
OscilloscopeAgent(
    resource_name="...",
    model_type="huggingface",           # NEW
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct",  # NEW
    connect_on_init=True
)
```

### 3. `app.py` (Streamlit UI)
**Changes:**
- Added model selection in sidebar:
  - Dropdown: "claude" or "huggingface"
  - HF model selector (when HF is selected)
- Session state variables:
  - `st.session_state.model_type`
  - `st.session_state.hf_model_name`
- Dynamic agent initialization based on selected model
- Updated chat header to show current model

## Usage

### Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Test HuggingFace integration:**
```bash
python test_huggingface_model.py
```

3. **Run interactive demo:**
```bash
python examples/agent_demo_huggingface.py
```

4. **Use in web interface:**
```bash
streamlit run app.py
```
Then select "huggingface" in the Model Type dropdown.

### Code Example

```python
from src.agent.agent import OscilloscopeAgent

# Option 1: Use Claude (existing behavior)
agent_claude = OscilloscopeAgent(
    model_type="claude",
    model="claude-haiku-4-5-20251001"
)

# Option 2: Use HuggingFace (NEW)
agent_hf = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct"
)

# Both work the same way
response = agent_hf.execute("Measure channel 1")
```

## Supported Models

### Recommended Options

1. **Qwen/Qwen2.5-0.5B-Instruct** - Fast, lightweight (~1GB)
2. **Qwen/Qwen2.5-1.5B-Instruct** - Balanced (~3GB)
3. **Qwen/Qwen2.5-3B-Instruct** - Best quality (~6GB)
4. **microsoft/Phi-3-mini-4k-instruct** - High quality (~8GB)
5. **google/gemma-2-2b-it** - Good general purpose (~5GB)

## Benefits

### Claude (Cloud)
- ✅ Highest quality
- ✅ No local resources
- ❌ Requires API key & internet
- ❌ Costs per request

### HuggingFace (Local)
- ✅ Free after download
- ✅ Works offline
- ✅ Privacy (data stays local)
- ❌ Requires local resources
- ❌ Quality varies

## Technical Details

### Architecture

```
User Query
    ↓
OscilloscopeAgent
    ↓
LLMFactory.create_model()
    ↓
    ├─→ Claude (ChatAnthropic)
    │
    └─→ HuggingFace (HuggingFaceChatWrapper)
            ↓
        transformers.pipeline
            ↓
        Local Model Inference
```

### Model Loading

1. First run: Downloads model from HuggingFace (~1-6GB)
2. Cached in `~/.cache/huggingface/`
3. Subsequent runs use cached model
4. Auto-detects hardware (CUDA/MPS/CPU)

### Performance

- **CPU**: 1-5 tokens/sec (slow but works)
- **Apple Silicon (MPS)**: 10-50 tokens/sec
- **NVIDIA GPU (CUDA)**: 50-200+ tokens/sec

## Migration Guide

### Existing Code (Claude only)

```python
agent = OscilloscopeAgent()
```

### New Code (with choice)

```python
# Still works (Claude by default)
agent = OscilloscopeAgent()

# Or explicitly specify
agent = OscilloscopeAgent(model_type="claude")

# Or use HuggingFace
agent = OscilloscopeAgent(
    model_type="huggingface",
    hf_model_name="Qwen/Qwen2.5-0.5B-Instruct"
)
```

**Result**: Backwards compatible! Existing code continues to work.

## Testing

Run tests to verify:

```bash
# Test HF model loading
python test_huggingface_model.py

# Test agent with HF
python examples/agent_demo_huggingface.py

# Test web interface
streamlit run app.py
```

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Read documentation: `HUGGINGFACE_MODELS.md`
3. Test the integration: `python test_huggingface_model.py`
4. Try the demo: `python examples/agent_demo_huggingface.py`
5. Use in your code!

## Troubleshooting

### "No module named 'transformers'"
```bash
pip install -r requirements.txt
```

### Out of memory
- Use smaller model (0.5B instead of 1.5B)
- Enable quantization: `load_in_8bit=True`

### Slow inference
- Use GPU if available
- Use smaller model
- Reduce `max_new_tokens`

## Support

See `HUGGINGFACE_MODELS.md` for detailed documentation, troubleshooting, and examples.

