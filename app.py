"""Main application file for Book Analysis Podcast System with enhanced styling and workflow."""
import streamlit as st
from src.book_processor import BookProcessor
from src.text_analyzer import TextAnalyzer
from src.podcast_creator import PodcastCreator
from src.session_state import SessionState
from src.utils import (
    format_timestamp,
    display_error,
    display_success,
    display_info,
    create_download_link
)
from src.config import PAGE_TITLE, PAGE_ICON, LAYOUT

def create_custom_css():
    """Create custom CSS with modern dark theme styling."""
    st.markdown("""
        <style>
        /* Base theme colors */
        :root {
            --primary-bg: #1e1e2e;
            --secondary-bg: #2a2a3c;
            --accent-color: #7c3aed;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --success-color: #10b981;
            --error-color: #ef4444;
            --info-color: #3b82f6;
            --border-color: #374151;
        }

        /* Main container and global styles */
        .main {
            background-color: var(--primary-bg);
            color: var(--text-primary);
        }

        .stApp {
            background-color: var(--primary-bg);
        }

        .main > div {
            max-width: 1200px;
            padding: 1rem 2rem;
        }

        /* Header styles */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
        }

        /* Text area styles */
        .stTextArea textarea {
            min-height: 100px;
            font-size: 16px;
            background-color: var(--secondary-bg);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
        }

        /* Chat message styles */
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            width: 100%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }

        .user-message {
            background-color: var(--secondary-bg);
            border-left: 4px solid var(--accent-color);
        }

        .assistant-message {
            background-color: var(--secondary-bg);
            border-left: 4px solid var(--success-color);
        }

        /* Content container styles */
        .content-container {
            background-color: var(--secondary-bg);
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border-color);
        }

        /* Audio player styles */
        .audio-player {
            width: 100%;
            padding: 1rem;
            background-color: var(--secondary-bg);
            border-radius: 0.5rem;
            margin: 1rem 0;
            border: 1px solid var(--border-color);
        }

        /* Script display styles */
        .podcast-script {
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            padding: 1.5rem;
            background-color: var(--secondary-bg);
            border-radius: 0.5rem;
            margin: 1rem 0;
            border-left: 4px solid var(--accent-color);
            max-height: 400px;
            overflow-y: auto;
        }

        /* File upload container */
        .upload-container {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background-color: var(--secondary-bg);
            border: 2px dashed var(--accent-color);
            margin-bottom: 1rem;
            text-align: center;
        }

        /* Question container */
        .question-container {
            background-color: var(--secondary-bg);
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border-color);
        }

        /* Button styling */
        .stButton button {
            width: 100%;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
            border-radius: 0.5rem;
            background-color: var(--accent-color);
            color: var(--text-primary);
            border: none;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            background-color: #6d28d9;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: var(--secondary-bg) !important;
            color: var(--text-primary) !important;
            border-radius: 0.5rem;
            border: 1px solid var(--border-color);
        }

        .streamlit-expanderContent {
            background-color: var(--secondary-bg) !important;
            color: var(--text-primary) !important;
            border-radius: 0 0 0.5rem 0.5rem;
        }

        /* File uploader styling */
        .stFileUploader {
            background-color: var(--secondary-bg);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border-color);
        }

        /* Download button styling */
        .download-button {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: var(--success-color);
            color: var(--text-primary);
            border-radius: 0.5rem;
            text-decoration: none;
            margin-top: 0.5rem;
            transition: all 0.3s ease;
            border: none;
        }

        .download-button:hover {
            background-color: #059669;
            transform: translateY(-2px);
        }

        /* Alert/message styling */
        .stAlert {
            background-color: var(--secondary-bg);
            color: var(--text-primary);
            border-radius: 0.5rem;
            margin: 1rem 0;
            border: 1px solid var(--border-color);
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--secondary-bg);
        }

        /* Progress bar styling */
        .stProgress > div > div {
            background-color: var(--accent-color);
        }

        /* Spinner styling */
        .stSpinner {
            text-align: center;
            margin: 1rem 0;
            color: var(--accent-color);
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_components():
    """Initialize application components."""
    if 'text_analyzer' not in st.session_state:
        st.session_state.text_analyzer = TextAnalyzer()
    if 'podcast_creator' not in st.session_state:
        st.session_state.podcast_creator = PodcastCreator()
    if 'current_content' not in st.session_state:
        st.session_state.current_content = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def process_content(content):
    """Process the content and generate initial analysis and podcast."""
    with st.spinner("🤔 Analyzing content..."):
        # Generate text summary
        summary = st.session_state.text_analyzer.generate_summary(content)

        # Generate podcast script
        podcast_script = st.session_state.text_analyzer.create_podcast_script(summary)

        # Create podcast
        podcast_audio = st.session_state.podcast_creator.create_podcast(podcast_script)

        if podcast_audio:
            SessionState.update_book_content(content)
            SessionState.update_book_analysis(summary)
            SessionState.update_podcast_audio(podcast_audio)
            display_success("✨ Content processed successfully!")
        else:
            display_error("❌ Failed to generate podcast audio.")

def handle_file_upload(uploaded_file):
    """Handle file upload and processing."""
    if uploaded_file:
        with st.spinner("📖 Processing your file..."):
            content = BookProcessor.process_file(uploaded_file)
            if content:
                process_content(content)

def handle_text_input(text):
    """Handle text input from text area."""
    if text:
        with st.spinner("📖 Processing your text..."):
            content = BookProcessor.process_text(text)
            if content:
                process_content(content)

def display_summary_and_podcast():
    """Display the summary and podcast audio."""
    if st.session_state.book_analysis:
        st.subheader("📝 Content Summary")
        st.write(st.session_state.book_analysis)

    if st.session_state.podcast_audio:
        st.subheader("🎧 Podcast Summary")
        st.audio(st.session_state.podcast_audio, format="audio/mp3")
        st.download_button(
            label="⬇️ Download Podcast",
            data=st.session_state.podcast_audio,
            file_name="book_summary_podcast.mp3",
            mime="audio/mp3"
        )

def handle_user_question(question: str):
    """Process user question and generate response."""
    try:
        with st.spinner("🤖 Generating response..."):
            answer = st.session_state.text_analyzer.answer_question(question, st.session_state.book_content)

            # Add to chat history
            SessionState.add_to_chat_history({"role": "user", "content": question})
            SessionState.add_to_chat_history({"role": "assistant", "content": answer})

    except Exception as e:
        display_error(f"❌ Error: {str(e)}")

def display_chat_interface():
    """Display chat-like interface for user interaction."""
    st.subheader("💬 Ask Questions")

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"<div class='chat-message user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message assistant-message'><strong>Assistant:</strong> {message['content']}</div>", unsafe_allow_html=True)

    # User input
    user_question = st.text_input("Ask a question about the content:")
    if st.button("Send", key="send_question"):
        if user_question:
            handle_user_question(user_question)
        else:
            display_info("Please enter a question.")

def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded"
    )

    # Apply custom styling
    create_custom_css()

    # Initialize components
    SessionState.initialize()
    initialize_components()

    st.title("📚 Interactive Book Analyzer")

    # Content input section
    st.header("📥 Input Your Content")
    input_type = st.radio("Choose input type:", ("Upload File", "Paste Text"))

    if input_type == "Upload File":
        uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
        if uploaded_file:
            handle_file_upload(uploaded_file)
    else:
        text_input = st.text_area("Paste your text here:", height=200)
        if st.button("Process Text"):
            handle_text_input(text_input)

    # Display summary and podcast if available
    if st.session_state.book_content:
        col1, col2 = st.columns([2, 1])

        with col1:
            display_summary_and_podcast()

        with col2:
            display_chat_interface()
    else:
        display_info("👆 Input your content to get started!")

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: var(--text-secondary); padding: 1rem;'>
            <p>AI-Powered Book Analysis & Podcast Generator</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()