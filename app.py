import streamlit as st
import ollama
from typing import Generator
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from gtts import gTTS
import io
import os
import tempfile
import base64

# Page configuration
st.set_page_config(
    page_title="GearHead Assistant",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .main {
        max-width: 1200px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔧 Gearhead Assist")
st.markdown("*Your AI-powered mobile equipment diagnostics and troubleshooting expert*")

# Model configuration
MODEL_NAME = "gearhead3.2"
CONTEXT_WINDOW = 8192  # From Modelfile

# Ollama configuration - can be overridden with environment variable
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Helper functions for audio
def transcribe_audio(audio_bytes):
    """Convert audio bytes to text using speech recognition"""
    try:
        recognizer = sr.Recognizer()

        # Save audio bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name

        # Load audio file
        with sr.AudioFile(tmp_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Clean up temp file
        os.unlink(tmp_file_path)

        return text
    except Exception as e:
        return f"Error: {str(e)}"

def text_to_speech(text):
    """Convert text to speech and return audio bytes"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)

        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return audio_buffer.getvalue()
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

def autoplay_audio(audio_bytes):
    """Auto-play audio in browser"""
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state for token tracking
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "prompt_tokens" not in st.session_state:
    st.session_state.prompt_tokens = 0
if "completion_tokens" not in st.session_state:
    st.session_state.completion_tokens = 0

# Initialize session state for voice
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""
if "enable_tts" not in st.session_state:
    st.session_state.enable_tts = False
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# Initialize session state for model availability
if "model_available" not in st.session_state:
    try:
        # Configure Ollama client with custom host
        client = ollama.Client(host=OLLAMA_HOST)

        # Check if the model is available
        models = client.list()
        # Access 'model' key from the model dictionary (not 'name')
        model_list = models.get('models', []) if isinstance(models, dict) else models['models']
        st.session_state.model_available = any(
            (m.get('model') if isinstance(m, dict) else m.model).startswith(MODEL_NAME)
            for m in model_list
        )
    except Exception as e:
        st.session_state.model_available = False
        st.error(f"Error connecting to Ollama at {OLLAMA_HOST}: {str(e)}")

# Sidebar with information and controls
with st.sidebar:
    st.header("Settings")

    # Model status
    if st.session_state.model_available:
        st.success(f"✅ Model '{MODEL_NAME}' is ready")
    else:
        st.error(f"❌ Model '{MODEL_NAME}' not found")
        st.info("Please ensure Ollama is running and the model is created:\n```bash\nollama create gearhead3.2 -f Modelfile\n```")

    st.divider()

    # Voice settings
    st.subheader("Voice Settings")
    st.session_state.enable_tts = st.toggle("🔊 Auto-play responses", value=st.session_state.enable_tts)

    # Listen to last response button
    if st.session_state.last_response and st.button("🔊 Replay Last Response"):
        audio_bytes = text_to_speech(st.session_state.last_response)
        if audio_bytes:
            autoplay_audio(audio_bytes)

    # Context tracking
    st.subheader("Context Usage")

    # Calculate usage percentage
    usage_percent = (st.session_state.total_tokens / CONTEXT_WINDOW) * 100 if st.session_state.total_tokens > 0 else 0

    # Progress bar with color based on usage
    if usage_percent < 60:
        bar_color = "normal"
    elif usage_percent < 80:
        bar_color = "normal"  # Streamlit doesn't support color change directly
    else:
        bar_color = "normal"

    st.progress(min(usage_percent / 100, 1.0))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tokens Used", f"{st.session_state.total_tokens:,}")
    with col2:
        st.metric("Remaining", f"{max(0, CONTEXT_WINDOW - st.session_state.total_tokens):,}")

    st.caption(f"Context Window: {CONTEXT_WINDOW:,} tokens ({usage_percent:.1f}% used)")

    if usage_percent > 80:
        st.warning("⚠️ Context usage is high. Consider clearing chat history soon.")
    elif usage_percent > 90:
        st.error("🚨 Context nearly full! Clear chat history to continue.")

    # Token breakdown (expandable)
    with st.expander("Token Details"):
        st.write(f"**Prompt tokens:** {st.session_state.prompt_tokens:,}")
        st.write(f"**Response tokens:** {st.session_state.completion_tokens:,}")
        st.write(f"**Messages in history:** {len(st.session_state.messages)}")

    st.divider()

    # Clear chat button
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.session_state.prompt_tokens = 0
        st.session_state.completion_tokens = 0
        st.rerun()

    st.divider()

    # Information section
    st.header("About")
    st.markdown("""
    This assistant specializes in:
    - Mini excavators
    - Skid steer loaders
    - Boom lifts
    - Scissor lifts
    - Forklifts (counterbalance & variable reach)
    - Other mobile equipment

    Ask questions about diagnostics, troubleshooting, maintenance, and repairs.
    """)

    st.divider()

    # Example prompts
    st.header("Example Questions")
    example_prompts = [
        "My mini excavator won't start. What should I check?",
        "How do I diagnose hydraulic issues on a skid steer?",
        "What are common causes of a scissor lift not raising?",
        "My forklift is losing power. What could be wrong?"
    ]

    for prompt in example_prompts:
        if st.button(prompt, key=f"example_{hash(prompt)}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Voice input section above chat input
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("#### 🎤 Voice Input or Type Below")

with col2:
    # Microphone recorder
    audio_data = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹️ Stop Recording",
        just_once=False,
        use_container_width=True,
        key="voice_recorder"
    )

with col3:
    # Process recorded audio
    if audio_data is not None:
        if st.button("📝 Transcribe", use_container_width=True):
            with st.spinner("Transcribing..."):
                transcribed_text = transcribe_audio(audio_data['bytes'])
                if not transcribed_text.startswith("Error"):
                    st.session_state.voice_input = transcribed_text
                    # Automatically submit the transcribed text
                    st.session_state.messages.append({"role": "user", "content": transcribed_text})
                    st.rerun()
                else:
                    st.error(transcribed_text)

# Chat input
if prompt := st.chat_input("Ask about mobile equipment diagnostics and troubleshooting..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    if st.session_state.model_available:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response_metadata = None

            try:
                # Configure Ollama client with custom host
                client = ollama.Client(host=OLLAMA_HOST)

                # Stream the response from Ollama
                stream = client.chat(
                    model=MODEL_NAME,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True
                )

                # Display streaming response
                for chunk in stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        full_response += chunk['message']['content']
                        message_placeholder.markdown(full_response + "▌")

                    # Capture token usage from the final chunk
                    if 'done' in chunk and chunk['done']:
                        response_metadata = chunk

                # Display final response
                message_placeholder.markdown(full_response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

                # Store last response for replay
                st.session_state.last_response = full_response

                # Text-to-speech if enabled
                if st.session_state.enable_tts and full_response:
                    with st.spinner("🔊 Generating audio..."):
                        audio_bytes = text_to_speech(full_response)
                        if audio_bytes:
                            autoplay_audio(audio_bytes)

                # Update token counts from metadata
                if response_metadata:
                    if 'prompt_eval_count' in response_metadata:
                        st.session_state.prompt_tokens = response_metadata.get('prompt_eval_count', 0)
                    if 'eval_count' in response_metadata:
                        st.session_state.completion_tokens += response_metadata.get('eval_count', 0)

                    # Total tokens is the sum of prompt and completion tokens
                    st.session_state.total_tokens = st.session_state.prompt_tokens + st.session_state.completion_tokens

                    # Force a rerun to update the sidebar metrics
                    st.rerun()

            except Exception as e:
                error_message = f"Error generating response: {str(e)}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
    else:
        with st.chat_message("assistant"):
            st.error("Cannot generate response: Model is not available. Please check the sidebar for setup instructions.")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    Powered by Ollama and Streamlit | Model: gearhead3.2 (llama3.2:2b)
    </div>
    """,
    unsafe_allow_html=True
)
