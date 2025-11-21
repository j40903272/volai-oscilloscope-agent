"""Streamlit Web Interface for Oscilloscope Control."""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Oscilloscope Control",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our modules
from src.oscilloscope.driver import OscilloscopeDriver, OscilloscopeError
from src.agent.agent import OscilloscopeAgent

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'driver' not in st.session_state:
    st.session_state.driver = None
    st.session_state.connected = False
    st.session_state.agent = None
    st.session_state.chat_history = []
    st.session_state.measurements = None
    st.session_state.model_type = "claude"  # Default to Claude
    st.session_state.hf_model_name = "Qwen/Qwen2.5-0.5B-Instruct"  # Default HF model

# Sidebar - Connection & Settings
with st.sidebar:
    st.markdown("### 🔌 Connection")
    
    resource_name = st.text_input(
        "VISA Resource",
        value=os.getenv("OSCILLOSCOPE_RESOURCE", "USB0::0xF4ED::0xEE3A::SDS1EEFX803161::INSTR"),
        help="USB resource name for your oscilloscope"
    )
    
    st.divider()
    
    # Model Selection
    st.markdown("### 🤖 AI Model")
    
    model_type = st.selectbox(
        "Model Type",
        options=["claude", "huggingface"],
        index=0 if st.session_state.model_type == "claude" else 1,
        help="Choose between Claude (cloud) or HuggingFace (local)"
    )
    
    if model_type == "huggingface":
        hf_model_name = st.selectbox(
            "HuggingFace Model",
            options=[
                "Qwen/Qwen2.5-0.5B-Instruct",
                "Qwen/Qwen2.5-1.5B-Instruct",
                "Qwen/Qwen2.5-3B-Instruct",
                "Qwen/Qwen3-0.6B",
                "microsoft/Phi-3-mini-4k-instruct",
                "google/gemma-2-2b-it"
            ],
            index=0,
            help="Select local model from HuggingFace"
        )
        st.session_state.hf_model_name = hf_model_name
        st.info("💡 First time will download model (~1-3GB)")
    else:
        st.caption("Using Claude API (requires ANTHROPIC_API_KEY)")
    
    st.session_state.model_type = model_type
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🟢 Connect", use_container_width=True):
            try:
                with st.spinner("Connecting..."):
                    st.session_state.driver = OscilloscopeDriver(resource_name, timeout=10000)
                    st.session_state.driver.connect()
                    st.session_state.connected = True
                    
                    # Initialize agent with selected model
                    if st.session_state.model_type == "huggingface":
                        with st.spinner(f"Loading {st.session_state.hf_model_name} model..."):
                            st.session_state.agent = OscilloscopeAgent(
                                resource_name=resource_name,
                                model_type="huggingface",
                                hf_model_name=st.session_state.hf_model_name,
                                connect_on_init=False
                            )
                    else:
                        st.session_state.agent = OscilloscopeAgent(
                            resource_name=resource_name,
                            model_type="claude",
                            connect_on_init=False
                        )
                    st.session_state.agent.driver = st.session_state.driver
                    
                st.success("✅ Connected!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
    
    with col2:
        if st.button("🔴 Disconnect", use_container_width=True):
            if st.session_state.driver:
                st.session_state.driver.disconnect()
                st.session_state.driver = None
                st.session_state.connected = False
                st.session_state.agent = None
            st.success("Disconnected")
            st.rerun()
    
    # Connection status
    if st.session_state.connected:
        st.markdown("**Status:** 🟢 Connected")
    else:
        st.markdown("**Status:** 🔴 Disconnected")
    
    st.divider()
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🎯 Auto Setup", use_container_width=True, disabled=not st.session_state.connected):
        try:
            st.session_state.driver.auto_setup()
            st.success("Auto setup complete!")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if st.button("🔄 Reset", use_container_width=True, disabled=not st.session_state.connected):
        try:
            st.session_state.driver.reset()
            st.success("Oscilloscope reset!")
        except Exception as e:
            st.error(f"Error: {e}")

# Main content
st.markdown('<h1 class="main-header">📊 Oscilloscope Control Center</h1>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "💬 AI Assistant", "⚙️ Controls", "📸 Capture"])

# TAB 1: DASHBOARD
with tab1:
    if not st.session_state.connected:
        st.info("👈 Connect to your oscilloscope using the sidebar to get started!")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Real-time Measurements")
            
            # Channel selection
            channel = st.selectbox("Select Channel", [1, 2], key="measure_channel")
            
            if st.button("🔍 Measure Now", use_container_width=True):
                try:
                    with st.spinner("Measuring..."):
                        measurements = st.session_state.driver.measure_channel(channel)
                        st.session_state.measurements = measurements
                except Exception as e:
                    st.error(f"Measurement error: {e}")
            
            # Display measurements
            if st.session_state.measurements:
                m = st.session_state.measurements
                
                # Create metrics display
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if m.frequency:
                        st.metric("Frequency", f"{m.frequency:.2f} Hz", help="Signal frequency")
                    if m.peak_to_peak:
                        st.metric("Peak-to-Peak", f"{m.peak_to_peak:.3f} V", help="Vpp")
                
                with col_b:
                    if m.period:
                        st.metric("Period", f"{m.period*1000:.3f} ms", help="Signal period")
                    if m.rms:
                        st.metric("RMS", f"{m.rms:.3f} V", help="RMS voltage")
                
                with col_c:
                    if m.maximum:
                        st.metric("Max", f"{m.maximum:.3f} V", help="Maximum voltage")
                    if m.minimum:
                        st.metric("Min", f"{m.minimum:.3f} V", help="Minimum voltage")
                
                # Additional measurements
                with st.expander("📋 All Measurements"):
                    st.json({
                        "channel": m.channel,
                        "frequency_hz": m.frequency,
                        "period_s": m.period,
                        "peak_to_peak_v": m.peak_to_peak,
                        "amplitude_v": m.amplitude,
                        "maximum_v": m.maximum,
                        "minimum_v": m.minimum,
                        "mean_v": m.mean,
                        "rms_v": m.rms,
                    })
        
        with col2:
            st.markdown("### 🎛️ Scope Status")
            
            if st.button("🔄 Refresh Status", use_container_width=True):
                try:
                    status = st.session_state.driver.get_status()
                    st.json({
                        "Model": status.model,
                        "Serial": status.serial_number,
                        "Firmware": status.firmware_version,
                        "Connected": status.connected,
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

# TAB 2: AI ASSISTANT
with tab2:
    # Display current model
    model_display = "Claude" if st.session_state.model_type == "claude" else st.session_state.hf_model_name
    st.markdown(f"### 💬 AI Assistant ({model_display})")
    
    # Show if screenshot is available for reference
    if 'screen_for_ai' in st.session_state:
        already_sent = st.session_state.get('screen_sent', False)
        
        col_scr1, col_scr2 = st.columns([3, 1])
        with col_scr1:
            if already_sent:
                st.info("📸 Screenshot was sent. Future messages are text-only (saves API costs).")
            else:
                st.success("🎯 Screenshot ready! It will be sent with your NEXT message (vision API).")
        with col_scr2:
            button_label = "🗑️ Clear" if already_sent else "❌ Cancel"
            if st.button(button_label):
                print(f"🗑️ Clearing screenshot state (was sent: {already_sent})")
                del st.session_state.screen_for_ai
                if 'screen_sent' in st.session_state:
                    del st.session_state.screen_sent
                st.rerun()
        
        # Show thumbnail of screenshot
        with st.expander("🖼️ View Screenshot"):
            if 'screen_image' in st.session_state:
                st.image(st.session_state.screen_image, use_column_width=True)
    
    if not st.session_state.connected:
        st.warning("⚠️ Please connect to the oscilloscope first!")
    else:
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Chat input
        placeholder = "Ask about the oscilloscope or the captured waveform..." if 'screen_for_ai' in st.session_state else "Ask me anything about the oscilloscope..."
        if prompt := st.chat_input(placeholder):
            # Check if agent is initialized
            if not st.session_state.get('agent'):
                st.error("❌ Please connect to the oscilloscope first!")
                st.stop()
            
            # Add user message to chat (with image if available)
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
                # Show thumbnail of image being sent
                if 'screen_for_ai' in st.session_state and 'screen_image' in st.session_state:
                    st.image(st.session_state.screen_image, width=200, caption="Sent screenshot")
            
            # Get AI response
            with st.chat_message("assistant"):
                # Check if we should send the screenshot (only once)
                has_screenshot = 'screen_for_ai' in st.session_state
                already_sent = st.session_state.get('screen_sent', False)
                is_claude = st.session_state.model_type == "claude"
                
                should_send_image = has_screenshot and not already_sent and is_claude
                
                # Debug info (can be removed later)
                logger_info = f"Screenshot state: has={has_screenshot}, sent={already_sent}, claude={is_claude}, will_send={should_send_image}"
                print(logger_info)  # For debugging
                
                with st.spinner("Analyzing screenshot..." if should_send_image else "Thinking..."):
                    try:
                        # If screenshot is available, not yet sent, and using Claude, send image
                        if should_send_image:
                            print("📸 SENDING SCREENSHOT WITH VISION API")
                            response = st.session_state.agent.execute_with_image(
                                prompt, 
                                st.session_state.screen_for_ai
                            )
                            # Mark as sent so it won't be sent again
                            st.session_state.screen_sent = True
                            print(f"✅ Screenshot marked as sent. screen_sent={st.session_state.screen_sent}")
                        else:
                            if has_screenshot and already_sent:
                                print("💬 Text-only (screenshot already sent)")
                            response = st.session_state.agent.execute(prompt)
                        
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    except AttributeError as e:
                        if "execute_with_image" in str(e):
                            # Fallback to text-only if vision not supported
                            context = f"{prompt}\n\n[Note: User has captured an oscilloscope screenshot. Help interpret what might be on it based on measurements.]"
                            response = st.session_state.agent.execute(context)
                            st.markdown(response)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                        else:
                            error_msg = "❌ Agent not initialized. Please reconnect to the oscilloscope."
                            st.error(error_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        # Example prompts
        st.markdown("#### 💡 Try these:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📏 Measure Channel 1"):
                st.session_state.chat_history.append({"role": "user", "content": "Measure frequency on channel 1"})
                st.rerun()
        
        with col2:
            if st.button("⚙️ Auto Setup"):
                st.session_state.chat_history.append({"role": "user", "content": "Auto setup the oscilloscope"})
                st.rerun()
        
        with col3:
            if st.button("ℹ️ Get Status"):
                st.session_state.chat_history.append({"role": "user", "content": "What's the oscilloscope status?"})
                st.rerun()
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

# TAB 3: MANUAL CONTROLS
with tab3:
    if not st.session_state.connected:
        st.info("Connect to oscilloscope to use controls")
    else:
        st.markdown("### ⚙️ Manual Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Channel 1 Settings")
            
            ch1_enabled = st.checkbox("Enable Channel 1", value=True)
            ch1_vdiv = st.selectbox("Voltage/Div", ["500MV", "1V", "2V", "5V", "10V"], index=1, key="ch1_vdiv")
            ch1_coupling = st.selectbox("Coupling", ["DC_1M", "AC_1M", "DC_50"], key="ch1_coupling")
            
            if st.button("Apply Channel 1 Settings"):
                try:
                    from src.oscilloscope.models import ChannelConfig, CouplingMode
                    config = ChannelConfig(
                        channel=1,
                        enabled=ch1_enabled,
                        voltage_div=ch1_vdiv,
                        coupling=CouplingMode[ch1_coupling]
                    )
                    st.session_state.driver.configure_channel(config)
                    st.success("✅ Channel 1 configured!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            st.markdown("#### Timebase Settings")
            
            time_div = st.selectbox(
                "Time/Div",
                ["1US", "10US", "100US", "500US", "1MS", "10MS", "100MS", "1S"],
                index=4
            )
            
            if st.button("Apply Timebase"):
                try:
                    from src.oscilloscope.models import TimebaseConfig
                    config = TimebaseConfig(time_div=time_div)
                    st.session_state.driver.configure_timebase(config)
                    st.success("✅ Timebase configured!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()
        
        st.markdown("#### Trigger Settings")
        col_t1, col_t2, col_t3 = st.columns(3)
        
        with col_t1:
            trig_source = st.selectbox("Source", [1, 2], key="trig_source")
        
        with col_t2:
            trig_mode = st.selectbox("Mode", ["AUTO", "NORMAL", "SINGLE"], key="trig_mode")
        
        with col_t3:
            trig_slope = st.selectbox("Slope", ["RISING", "FALLING"], key="trig_slope")
        
        trig_level = st.text_input("Trigger Level", value="0V", key="trig_level")
        
        if st.button("Apply Trigger Settings"):
            try:
                from src.oscilloscope.models import TriggerConfig, TriggerMode, TriggerSlope
                config = TriggerConfig(
                    source=trig_source,
                    mode=TriggerMode[trig_mode],
                    slope=TriggerSlope[trig_slope],
                    level=trig_level
                )
                st.session_state.driver.configure_trigger(config)
                st.success("✅ Trigger configured!")
            except Exception as e:
                st.error(f"Error: {e}")

# TAB 4: SCREEN CAPTURE
with tab4:
    if not st.session_state.connected:
        st.info("Connect to oscilloscope to capture screen")
    else:
        st.markdown("### 📸 Screen Capture")
        st.caption("Fast screenshot of oscilloscope display (2-3 seconds)")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("#### Capture Controls")
            
            if st.button("📸 Capture Screen", use_container_width=True, type="primary"):
                try:
                    with st.spinner("📡 Capturing screen... (2-3 seconds)"):
                        screen_data = st.session_state.driver.capture_screen()
                        
                        # Save screen capture
                        import io
                        from PIL import Image
                        img = Image.open(io.BytesIO(screen_data))
                        st.session_state.screen_image = img
                        st.session_state.capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Clear previous AI screenshot if exists (new capture = new screenshot)
                        if 'screen_for_ai' in st.session_state:
                            del st.session_state.screen_for_ai
                        if 'screen_sent' in st.session_state:
                            del st.session_state.screen_sent
                        
                        st.success("✅ Screen captured!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Capture failed: {e}")
                    st.info("💡 Make sure oscilloscope is connected")
            
            st.divider()
            
            # Send to AI Assistant button
            if 'screen_image' in st.session_state and st.session_state.screen_image:
                # Check if already marked for AI
                already_ready = 'screen_for_ai' in st.session_state
                
                button_label = "🔄 Re-send to AI" if already_ready else "🤖 Send to AI Assistant"
                button_help = "Mark for re-sending (will send on next message)" if already_ready else "Prepare screenshot for AI analysis"
                
                if st.button(button_label, use_container_width=True, help=button_help):
                    # Save to temporary buffer for AI
                    import io
                    buf = io.BytesIO()
                    st.session_state.screen_image.save(buf, format='PNG')
                    buf.seek(0)
                    st.session_state.screen_for_ai = buf.getvalue()
                    st.session_state.screen_sent = False  # Mark as not sent yet (reset if re-sending)
                    print(f"🔄 Screenshot prepared for AI. screen_sent reset to False")
                    st.success("✅ Screenshot ready for AI!")
                    st.info("💡 Go to 'AI Assistant' tab - screenshot will be sent with your NEXT message only")
        
        with col2:
            # Display screen capture
            if 'screen_image' in st.session_state and st.session_state.screen_image:
                st.markdown(f"### 📸 Captured - {st.session_state.get('capture_time', '')}")
                st.image(st.session_state.screen_image, use_column_width=True)
                
                st.divider()
                
                # Download screen image
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    import io
                    buf = io.BytesIO()
                    st.session_state.screen_image.save(buf, format='PNG')
                    buf.seek(0)
                    st.download_button(
                        label="📥 Download PNG",
                        data=buf,
                        file_name=f"oscilloscope_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                with col_dl2:
                    if st.button("🗑️ Clear", use_container_width=True):
                        if 'screen_image' in st.session_state:
                            del st.session_state.screen_image
                        if 'screen_for_ai' in st.session_state:
                            del st.session_state.screen_for_ai
                        if 'screen_sent' in st.session_state:
                            del st.session_state.screen_sent
                        st.rerun()
                
                st.caption("💡 Tip: Use 'Send to AI Assistant' to analyze this waveform with AI vision")
            else:
                st.info("👆 Click 'Capture Screen' to take a screenshot")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🔬 Oscilloscope Control Interface | Built with Streamlit & Claude</p>
</div>
""", unsafe_allow_html=True)

