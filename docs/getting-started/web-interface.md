# Quick Start Guide - Oscilloscope Control

## 🚀 Start the Web App

```bash
cd "/Users/interview/Documents/YUN DA"
make run-web
```

Then open your browser to the URL shown (usually `http://localhost:8501`)

---

## ✨ What You Can Do

### 1. 📊 Dashboard Tab
- **Quick Measurements** - Frequency, voltage, period (< 1 second)
- **Auto Setup** - Automatically configure scope
- **Status Check** - See oscilloscope info

### 2. 💬 AI Assistant Tab
- **Natural Language Control** - Just type what you want
- **Screenshot Analysis** - Reference captured waveforms
- **Examples:**
  - "Measure frequency on channel 1"
  - "Set voltage to 500mV per division"
  - "Change time resolution to 100 microseconds per division"

### 3. ⚙️ Manual Controls Tab
- **Channel Settings** - Voltage division, coupling, probe ratio
- **Timebase Settings** - Time per division
- **Trigger Settings** - Source, mode, slope, level

### 4. 📸 Screen Capture Tab
- **Fast Screenshot** - Capture in 2-3 seconds
- **Download PNG** - Save with timestamp
- **Send to AI** - Analyze with AI Assistant

---

## 🎯 Common Tasks

### Take a Screenshot
1. Go to "📸 Capture" tab
2. Click "📸 Capture Screen"
3. Wait 2-3 seconds
4. Click "📥 Download PNG" to save

### Measure Frequency
**Option 1: Dashboard (Fastest)**
1. Go to "📈 Dashboard" tab
2. Select channel
3. Click "📊 Measure"
4. See frequency instantly

**Option 2: AI Assistant**
1. Go to "💬 AI Assistant" tab
2. Type: "measure frequency on channel 1"
3. Get result in 1-2 seconds

### Change Settings with AI
- "Set voltage division to 500mV on channel 1"
- "Change timebase to 100 microseconds"
- "Set trigger to rising edge on channel 2"

### Analyze Waveform
1. Capture screenshot in "📸 Capture" tab
2. Click "🤖 Send to AI Assistant"
3. Go to "💬 AI Assistant" tab  
4. Ask: "What do you see in this waveform?"

---

## 🤖 AI Models

You can choose between two AI models in the sidebar:

### Claude (Default)
- **Pros:** Most capable, fastest, best understanding
- **Cons:** Requires ANTHROPIC_API_KEY, uses cloud API
- **Best for:** Daily use, complex tasks

### HuggingFace (Local)
- **Pros:** Runs locally, free, private
- **Cons:** First download ~1-3GB, slower responses
- **Best for:** Offline use, no API key available

---

## 🆘 Troubleshooting

### Can't Connect to Oscilloscope
```bash
# Check connection
make check-device

# Make sure nothing else is using it
# Close any other oscilloscope software
# Close extra browser tabs with the web app
```

### Screen Capture Fails
- Make sure you're connected first
- Check oscilloscope USB cable
- Try power cycling oscilloscope
- Restart the web app

### AI Not Responding
- Check if you have ANTHROPIC_API_KEY in `.env` (for Claude)
- Or switch to HuggingFace model in sidebar
- Check that oscilloscope is connected

### Web App Won't Start
```bash
# Install dependencies
make install

# Then try again
make run-web
```

---

## 📚 More Help

- **`SCREEN_CAPTURE_GUIDE.md`** - Detailed screen capture guide
- **`CLEANUP_SUMMARY.md`** - What changed in the latest update
- **`QUICKSTART_MCP.md`** - How to use MCP server with Claude Desktop
- **`README.md`** - Full project documentation

---

## 💡 Pro Tips

1. **Use shortcuts:** Dashboard measurements are fastest for values
2. **Use AI for convenience:** Natural language is easier than remembering commands
3. **Screenshot first:** Capture before asking AI to analyze
4. **Save screenshots:** Download PNGs for documentation
5. **Mix methods:** Use dashboard + AI + manual controls together!

---

## ✨ Quick Reference

| What You Want | Where to Go | Time |
|---------------|-------------|------|
| Measure frequency | Dashboard → Measure | < 1 sec |
| Take screenshot | Capture → Capture Screen | 2-3 sec |
| Change settings | AI Assistant or Manual Controls | 1-2 sec |
| Analyze waveform | Capture → Send to AI → Ask | 3-5 sec |
| Download data | Capture → Download PNG | Instant |

---

Enjoy your oscilloscope control system! 🎉

