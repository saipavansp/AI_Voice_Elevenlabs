"""Main application file for Book Analysis Podcast System with enhanced styling."""
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
    create_expander_header,
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
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None

def handle_file_upload(uploaded_file):
    """Handle file upload and processing."""
    if uploaded_file != st.session_state.current_file:
        with st.spinner("📖 Processing your book..."):
            content = BookProcessor.process_file(uploaded_file)
            if content:
                SessionState.update_book_content(content)
                st.session_state.current_file = uploaded_file

                with st.spinner("🤔 Analyzing content..."):
                    analysis = st.session_state.text_analyzer.analyze_text(content)
                    if analysis['success']:
                        SessionState.update_book_analysis(analysis['analysis'])
                        display_success("✨ Book processed successfully!")
                    else:
                        display_error(f"❌ Analysis failed: {analysis.get('error')}")

def handle_user_question(question: str):
    """Process user question and generate response."""
    try:
        st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You asked:</strong><br>{question}
            </div>
        """, unsafe_allow_html=True)

        with st.spinner("🎙️ Creating your personalized response..."):
            # Get text answer
            answer = st.session_state.text_analyzer.answer_question(
                question,
                st.session_state.book_content
            )

            # Create podcast script
            script = st.session_state.text_analyzer.create_podcast_script(answer)

            # Generate podcast
            result = st.session_state.podcast_creator.process_answer(answer, script)

            # Display response
            st.markdown("""
                <div class="chat-message assistant-message">
                    <strong>Response:</strong>
                """, unsafe_allow_html=True)

            st.markdown(result.text_answer)

            # Display podcast
            if result.audio:
                st.markdown('<div class="audio-player">', unsafe_allow_html=True)
                st.write("🎧 Listen to the Podcast Version:")
                try:
                    st.audio(result.audio, format="audio/wav")
                    st.download_button(
                        label="⬇️ Download Audio",
                        data=result.audio,
                        file_name=f"podcast_{len(st.session_state.chat_history)}.wav",
                        mime="audio/wav"
                    )
                except Exception as e:
                    display_error(f"🎵 Audio playback error: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Show conversation script
            if result.podcast_script:
                with st.expander("🎭 View Conversation Script", expanded=False):
                    st.markdown('<div class="podcast-script">', unsafe_allow_html=True)
                    st.write(result.podcast_script)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Update chat history
            SessionState.add_to_chat_history(question, {
                'text_answer': result.text_answer,
                'podcast_script': result.podcast_script,
                'audio': result.audio,
                'error': result.error
            })

    except Exception as e:
        display_error(f"❌ Error: {str(e)}")

def display_chat_history():
    """Display chat history with audio playback."""
    if st.session_state.chat_history:
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        st.write("💬 Previous Conversations")

        for chat in SessionState.get_recent_chat_history():
            with st.expander(
                f"🗣️ {chat['question']} ({format_timestamp(chat['timestamp'])})",
                expanded=False
            ):
                st.markdown('<div class="content-container">', unsafe_allow_html=True)
                st.write(chat['answer'])

                if chat.get('audio'):
                    st.markdown('<div class="audio-player">', unsafe_allow_html=True)
                    st.audio(chat['audio'], format="audio/wav")
                    st.markdown('</div>', unsafe_allow_html=True)

                if chat.get('podcast_script'):
                    st.markdown('<div class="podcast-script">', unsafe_allow_html=True)
                    st.write("📝 Conversation Script:")
                    st.write(chat['podcast_script'])
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

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

    st.title("📚 AI Book Analysis & Podcast")

    # Welcome message
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.write("""
    Welcome! Upload your book and ask questions to get insights in both text and podcast format. 
    Experience your book discussions as engaging conversations between our AI hosts.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Create layout
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown('<div class="upload-container">', unsafe_allow_html=True)
        st.write("📤 Upload Your Book")
        uploaded_file = st.file_uploader(
            "Select PDF or TXT file",
            type=["pdf", "txt"],
            help="Supported formats: PDF, TXT"
        )

        if uploaded_file:
            handle_file_upload(uploaded_file)

        if st.session_state.chat_history:
            if st.button("🗑️ Clear History"):
                SessionState.clear_chat_history()
                st.success("History cleared!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if st.session_state.book_content:
            if st.session_state.book_analysis:
                with st.expander("📖 Book Analysis", expanded=False):
                    st.markdown('<div class="content-container">', unsafe_allow_html=True)
                    st.write(st.session_state.book_analysis)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="question-container">', unsafe_allow_html=True)
            st.write("❓ Ask About Your Book")
            question = st.text_area(
                "What would you like to know?",
                height=100,
                placeholder="Type your question here..."
            )

            if st.button("🔍 Get Answer", type="primary"):
                if question:
                    handle_user_question(question)
                else:
                    display_info("Please enter a question first!")
            st.markdown('</div>', unsafe_allow_html=True)

            display_chat_history()
        else:
            display_info("👈 Upload a book to begin!")

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: var(--text-secondary); padding: 1rem;'>
            <p>AI-Powered Book Analysis & Podcast Generator</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()