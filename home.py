import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO
import base64
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
import subprocess
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found! Please check your .env file")
    st.stop()
client = OpenAI(api_key=api_key)

def stream_response(messages):
    """Generator for streaming API responses"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True
        )

        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"An error occurred: {str(e)}"

def get_grammar_help(topic, question):
    """Get guided help without direct answers"""
    system_msg = """You are a Socratic grammar tutor. Help students think through problems by:
    - Asking 2-3 guiding questions
    - Providing hints and patterns instead of answers
    - Breaking problems into smaller steps
    - Providing partial examples to require completion
    - Encouraging self-discovery
    - Never providing complete solutions or direct answers"""
    
    user_prompt = f"""Student needs help with {topic}. Their question: {question}
    Guide them to find the answer themselves using these techniques:
    1. Ask questions about what they've tried
    2. Identify patterns in similar problems
    3. Provide incomplete examples to complete
    4. Suggest resources for self-checking
    5. Highlight key concepts to focus on
    Never give the direct answer or full solution!"""

    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ])

def analyze_grammar(text):
    """Analyze text for grammatical errors and provide guided correction help"""
    system_msg = """You are a meticulous grammar coach. Follow these steps:
    1. Identify 3-5 grammatical errors in the text
    2. Categorize each error (e.g., tense, punctuation, voice)
    3. Explain why it's incorrect using simple terms
    4. Ask a guiding question to help correct it
    5. Never show the corrected version
    6. Prioritize serious errors over minor ones
    7. Use examples where helpful"""
    
    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Analyze this text:\n{text}"}
    ])

def get_direct_answer_home(topic, question):
    """Get direct answer for home page questions"""
    system_msg = """You are a helpful grammar tutor that provides direct answers and clear explanations."""
    user_prompt = f"Provide a direct answer and detailed explanation for the student's question about {topic}: {question}"
    
    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ])

def get_direct_answer_analysis(text):
    """Get direct corrections for analysis page text"""
    system_msg = """You are a meticulous writing coach. Provide a corrected version of the user's text with detailed explanations of each change made. Format your response with the corrected text followed by bullet points explaining each correction."""
    user_prompt = f"Text to correct and explain:\n{text}"
    
    return stream_response([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ])

def generate_image(prompt):
    """Generate image using DALL·E"""
    try:
        response = client.images.generate(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="url"
        )
        return response.data[0].url
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Page configuration
st.set_page_config(page_title="Grammar Guide", layout="wide")

# Initialize session state for page navigation and answer tracking
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'home_initial' not in st.session_state:
    st.session_state.home_initial = False
if 'analysis_initial' not in st.session_state:
    st.session_state.analysis_initial = False

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Home", "✍️ Analyze My Writing", "🎨 Generate Image", "🗣️ Socratic Tutor"], key='page')
    
    st.markdown("---")
    st.header("How to Use")
    st.markdown("""
    1. Select your grammar topic
    2. Type your question
    3. Get instant expert guidance
    4. Ask follow-up questions!
    """)
    st.markdown("---")
    st.info("**New Feature:** Use the 'Analyze My Writing' section to get personalized feedback on your texts!")

# Home Page - Grammar Concept Helper
if page == "Home":
    st.title("📚 Grammar Concept Helper")
    st.markdown("""
    Welcome to your personal grammar tutor! Get help with:
    - Story writing ✍️
    - Essay composition 📝
    - Tenses ⏳
    - Active/Passive voice 🔄
    - And more!
    """)

    st.markdown("---")
    topic = st.selectbox(
        "Select Grammar Topic",
        options=["Story Writing", "Essay Writing", "Tenses", "Active/Passive Voice", "Other"]
    )
    user_question = st.text_area("Your Question/Prompt:", height=150, key="question")

    if st.button("Get Help"):
        if user_question.strip() == "":
            st.warning("Please enter your question first!")
        else:
            st.subheader("Here's Your Guidance:")
            response = get_grammar_help(topic, user_question)
            st.write_stream(response)
            # Store session state for direct answer
            st.session_state.home_initial = True
            st.session_state.home_topic = topic
            st.session_state.home_question = user_question
            st.markdown("---")
            st.success("Remember: Great learning happens through exploration! Try applying these suggestions.")

    # Show direct answer button only after initial response
    if st.session_state.home_initial and st.session_state.page == 'Home':
        if st.button("Give Answer"):
            st.subheader("Direct Answer:")
            direct_response = get_direct_answer_home(
                st.session_state.home_topic, 
                st.session_state.home_question
            )
            st.write_stream(direct_response)

# Analysis Page
elif page == "✍️ Analyze My Writing":
    st.title("✍️ Analyze My Writing")
    st.markdown("""
    **Get personalized feedback on your writing:**
    1. Paste your text below
    2. Get error analysis
    3. Improve it yourself with guided questions
    """)
    
    user_text = st.text_area("Your Text:", height=300, key="text_analysis")
    
    if st.button("Analyze My Writing"):
        if user_text.strip() == "":
            st.warning("Please enter some text to analyze!")
        else:
            st.subheader("Writing Feedback")
            st.markdown("**Key Areas to Improve** (work through these one at a time):")
            analysis = analyze_grammar(user_text)
            st.write_stream(analysis)
            # Store session state for direct answer
            st.session_state.analysis_initial = True
            st.session_state.analysis_text = user_text
            st.success("Try making corrections based on these insights, then analyze again!")

    # Show direct answer button only after initial response
    if st.session_state.analysis_initial and st.session_state.page == '✍️ Analyze My Writing':
        if st.button("Give Answer"):
            st.subheader("Direct Answer and Corrections:")
            direct_response = get_direct_answer_analysis(st.session_state.analysis_text)
            st.write_stream(direct_response)

# Image Generation Page
elif page == "🎨 Generate Image":
    st.title("🎨 Visual Story Helper")
    st.markdown("""
    **Turn your story ideas into images!**
    1. Describe a scene or character
    2. Get AI-generated artwork
    3. Use it for inspiration in your writing
    """)
    
    image_prompt = st.text_area("Describe what you want to visualize:", 
                              height=150,
                              placeholder="Example: 'A brave knight fighting a dragon at sunset in a medieval castle courtyard'")
    
    if st.button("Generate Image"):
        if not image_prompt.strip():
            st.warning("Please enter a description first!")
        else:
            with st.spinner("Creating your artwork..."):
                image_url = generate_image(image_prompt)
                
                if image_url.startswith('http'):
                    response = requests.get(image_url)
                    image = Image.open(BytesIO(response.content))
                    st.image(image, caption="Your Generated Artwork")
                    st.success("Use this image to inspire your writing!")
                else:
                    st.error(image_url)

# Socratic Tutor Page
elif page == "🗣️ Socratic Tutor":
    st.title("Socratic Tutor 🤔")
    float_init()

    # Initialize session state
    if "socratic_messages" not in st.session_state:
        st.session_state.socratic_messages = [
            {"role": "system", "content": """You are a Socratic tutor. Never give direct answers. 
            Ask thought-provoking questions to guide users to discover answers independently."""},
            {"role": "assistant", "content": "What topic shall we explore today? I'll help you think through it with questions!"}
        ]

    # Footer container for microphone
    footer_container = st.container()
    with footer_container:
        audio_bytes = audio_recorder()

    # Display chat messages (skip system role)
    for message in st.session_state.socratic_messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Handle audio input
    if audio_bytes:
        with st.spinner("Transcribing..."):
            webm_file_path = "temp_audio.webm"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)
            
            try:
                transcript = speech_to_text(webm_file_path)
                if transcript:
                    st.session_state.socratic_messages.append({"role": "user", "content": transcript})
                    with st.chat_message("user"):
                        st.write(transcript)
            except Exception as e:
                st.error(f"Error during transcription: {e}")
            finally:
                if os.path.exists(webm_file_path):
                    os.remove(webm_file_path)

    # Generate response
    if st.session_state.socratic_messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking🤔..."):
                # Exclude system message from API call (already in context)
                final_response = get_answer([msg for msg in st.session_state.socratic_messages if msg["role"] != "system"])
            with st.spinner("Generating audio response..."):
                audio_file = text_to_speech(final_response)
                autoplay_audio(audio_file)
            st.write(final_response)
            st.session_state.socratic_messages.append({"role": "assistant", "content": final_response})
            if os.path.exists(audio_file):
                os.remove(audio_file)

    # Float footer
    footer_container.float("bottom: 0rem;")

# Footer
st.markdown("---")
st.caption("Powered by Brain | Made By Ayan Parmar")
