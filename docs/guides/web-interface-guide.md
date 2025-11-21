# 🌐 Web Interface Guide

Beautiful, intuitive web interface for controlling your oscilloscope!

## ✨ Features

### 📈 Dashboard Tab
- **Real-time measurements** with beautiful metric cards
- **One-click measurement** from any channel
- **Scope status display**
- Color-coded, easy-to-read metrics

### 💬 AI Assistant Tab
- **Natural language chat** with Claude
- Ask questions like:
  - "Measure frequency on channel 1"
  - "What's the voltage?"
  - "Auto setup the oscilloscope"
- **Chat history** preserved during session
- **Example prompts** for quick actions

### ⚙️ Manual Controls Tab
- **Channel configuration**
  - Enable/disable channels
  - Set voltage per division
  - Configure coupling (DC/AC)
- **Timebase settings**
  - Time per division
  - Horizontal delay
- **Trigger configuration**
  - Source channel
  - Mode (AUTO/NORMAL/SINGLE)
  - Slope (RISING/FALLING)
  - Trigger level

### 📸 Waveform Capture Tab
- **Capture and display waveforms**
- Interactive Plotly graphs
- Zoom, pan, and analyze
- Configurable number of sample points

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install streamlit plotly
```

Or:

```bash
make install
```

### 2. Launch Web Interface

```bash
make run-web
```

Or:

```bash
streamlit run app.py
```

### 3. Open in Browser

Your browser will automatically open to `http://localhost:8501`

## 🎮 Using the Interface

### Connecting

1. **In the sidebar**, enter your oscilloscope's VISA resource name
2. Click **🟢 Connect**
3. Wait for "✅ Connected!" message

### Measuring

**Dashboard Tab:**
1. Select channel (1 or 2)
2. Click **🔍 Measure Now**
3. View beautiful metric cards with all measurements

**AI Assistant Tab:**
1. Type: "Measure frequency on channel 1"
2. AI will execute the command and show results
3. Natural conversation interface!

### Configuring

**Manual Controls Tab:**
1. Adjust settings using dropdown menus
2. Click **Apply** buttons to send to oscilloscope
3. Instant feedback on success/failure

### Capturing Waveforms

**Waveform Capture Tab:**
1. Select channel
2. Set number of points (100-10000)
3. Click **📊 Capture Waveform**
4. View interactive plot!

## 🎨 Interface Features

### Sidebar
- **Connection controls** (Connect/Disconnect)
- **Connection status indicator** (🟢/🔴)
- **Quick actions** (Auto Setup, Reset)

### Beautiful Design
- **Gradient headers** and cards
- **Color-coded metrics**
- **Smooth transitions**
- **Responsive layout**
- **Dark/Light theme support** (Streamlit settings)

### Real-time Updates
- **Live measurements**
- **Instant status checks**
- **Interactive graphs**

## 💡 Tips

### Best Practices
- **Connect signal first** before measuring (use CAL output)
- **Auto setup** when signal is unclear
- **Check status** if commands fail

### Keyboard Shortcuts
- **Tab**: Switch between tabs
- **Enter**: Submit chat messages
- **Ctrl+C**: Stop server

### Performance
- The web interface runs **locally** on your computer
- **No internet required** except for AI Assistant
- **Fast and responsive** even with large waveforms

## 🐛 Troubleshooting

### Can't Connect
- Check oscilloscope is powered on
- Verify USB cable is connected
- Confirm resource name in sidebar

### Measurements Show `****`
- No signal on selected channel
- Connect probe to CAL output for testing
- Press Auto Setup button

### AI Assistant Not Working
- Check `ANTHROPIC_API_KEY` in `.env` file
- Ensure internet connection is available
- Verify API key is valid

### Waveform Doesn't Display
- Ensure signal is present
- Try Auto Setup first
- Check channel is enabled

## 🎯 Example Workflows

### Quick Check
1. Connect
2. Dashboard → Select Channel 1
3. Click Measure Now
4. View results instantly!

### Using AI
1. Connect  
2. AI Assistant tab
3. Type: "What's the voltage on channel 1?"
4. AI measures and explains results

### Manual Configuration
1. Connect
2. Controls tab
3. Set Channel 1 to 2V/div, DC coupling
4. Set Timebase to 1MS/div
5. Apply settings
6. Measure!

### Waveform Analysis
1. Connect probe to CAL output
2. Capture tab
3. Select Channel 1, 1000 points
4. Capture Waveform
5. Analyze the beautiful graph!

## 🔧 Advanced

### Customization
Edit `app.py` to:
- Change colors/styling (CSS in markdown)
- Add custom buttons
- Create new tabs
- Modify measurement displays

### Integration
The web interface uses the same driver as:
- Command-line agent
- MCP server
- Direct Python API

All work together seamlessly!

## 📸 Screenshots

### Dashboard View
- Large metric cards with gradient backgrounds
- Real-time measurement display
- Status indicators

### AI Chat
- Clean chat interface
- Message history
- Quick action buttons

### Controls
- Organized settings panels
- Clear apply buttons
- Instant feedback

### Waveform Plot
- Interactive Plotly graphs
- Zoom, pan, hover for details
- Professional visualization

---

**Enjoy your beautiful oscilloscope interface! 🎉**

