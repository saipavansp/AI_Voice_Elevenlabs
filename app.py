"""Main application file for Book Analysis Podcast System."""
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
    """Create custom CSS for better styling."""
    st.markdown("""
        <style>
        /* Main container styles */
        .main > div {
            max-width: 1200px;
            padding: 1rem 2rem;
        }
        
        /* Text area styles */
        .stTextArea textarea {
            min-height: 100px;
            font-size: 16px;
        }
        
        /* Chat message styles */
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            width: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .user-message {
            background-color: #e6f3ff;
            border-left: 4px solid #2196F3;
        }
        
        .assistant-message {
            background-color: #f8f9fa;
            border-left: 4px solid #4CAF50;
        }
        
        /* Content container styles */
        .content-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 100%;
        }
        
        /* Audio player styles */
        .audio-player {
            width: 100%;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            margin: 1rem 0;
            border: 1px solid #e0e0e0;
        }
        
        /* Script display styles */
        .podcast-script {
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            padding: 1.5rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            margin: 1rem 0;
            border-left: 4px solid #9C27B0;
            max-height: 400px;
            overflow-y: auto;
        }
        
        /* File upload container */
        .upload-container {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
            border: 2px dashed #2196F3;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        /* Question input container */
        .question-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Loading spinner */
        .stSpinner {
            text-align: center;
            margin: 1rem 0;
        }
        
        /* Error and success messages */
        .stAlert {
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        /* Improved button styling */
        .stButton button {
            width: 100%;
            padding: 0.75rem 1.5rem;
            font-weight: bold;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Download button styling */
        .download-button {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #4CAF50;
            color: white;
            border-radius: 0.5rem;
            text-decoration: none;
            margin-top: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .download-button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_components():
    """Initialize application components."""
    if 'text_analyzer' not in st.session_state:
        st.session_state.text_analyzer = TextAnalyzer()
    if 'podcast_creator' not in st.session_state:
        st.session_state.podcast_creator = PodcastCreator()

def handle_audio_error(e: Exception):
    """Handle audio generation errors."""
    error_msg = str(e)
    if "voice" in error_msg.lower():
        display_error("Voice initialization error. Please check system voices.")
    elif "memory" in error_msg.lower():
        display_error("Memory error during audio generation. Text might be too long.")
    else:
        display_error(f"Error generating audio: {error_msg}")

def handle_file_upload(uploaded_file):
    """Handle file upload and processing."""
    if uploaded_file != st.session_state.current_file:
        with st.spinner("Processing file..."):
            content = BookProcessor.process_file(uploaded_file)
            if content:
                SessionState.update_book_content(content)
                st.session_state.current_file = uploaded_file

                with st.spinner("Analyzing content..."):
                    analysis = st.session_state.text_analyzer.analyze_text(content)
                    if analysis['success']:
                        SessionState.update_book_analysis(analysis['analysis'])
                        display_success(f"Successfully analyzed: {uploaded_file.name}")

                        st.markdown('<div class="content-container">', unsafe_allow_html=True)
                        st.write("📄 File Information:")
                        file_info = BookProcessor.get_file_info(uploaded_file)
                        for key, value in file_info.items():
                            st.write(f"- {key.capitalize()}: {value}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        display_error(f"Error analyzing book: {analysis.get('error')}")

def handle_user_question(question: str):
    """Handle user question and generate response."""
    try:
        st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong><br>{question}
            </div>
        """, unsafe_allow_html=True)

        with st.spinner("Creating response..."):
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
                    <strong>Assistant:</strong>
                """, unsafe_allow_html=True)

            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            st.write(result.text_answer)
            st.markdown('</div>', unsafe_allow_html=True)

            # Display podcast
            if result.audio:
                st.markdown('<div class="audio-player">', unsafe_allow_html=True)
                st.write("🎧 Listen to Podcast Version:")
                try:
                    st.audio(result.audio, format="audio/wav")

                    # Download button
                    st.download_button(
                        label="⬇️ Download Audio",
                        data=result.audio,
                        file_name=f"podcast_answer_{len(st.session_state.chat_history)}.wav",
                        mime="audio/wav"
                    )
                except Exception as e:
                    handle_audio_error(e)
                st.markdown('</div>', unsafe_allow_html=True)

            # Show conversation script
            if result.podcast_script:
                with st.expander("🎭 Show Conversation Script", expanded=False):
                    st.markdown('<div class="podcast-script">', unsafe_allow_html=True)
                    st.write(result.podcast_script)
                    st.markdown('</div>', unsafe_allow_html=True)

            if result.error:
                display_error(result.error)

            st.markdown('</div>', unsafe_allow_html=True)

            # Update chat history
            SessionState.add_to_chat_history(question, {
                'text_answer': result.text_answer,
                'podcast_script': result.podcast_script,
                'audio': result.audio,
                'error': result.error
            })
    except Exception as e:
        display_error(f"Error processing question: {str(e)}")

def display_chat_history():
    """Display chat history with audio playback."""
    if st.session_state.chat_history:
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)
        st.write("💬 Recent Conversations")

        for chat in SessionState.get_recent_chat_history():
            with st.expander(
                f"Q: {chat['question']} ({format_timestamp(chat['timestamp'])})",
                expanded=False
            ):
                st.markdown('<div class="content-container">', unsafe_allow_html=True)
                st.write("Answer:", chat['answer'])

                if chat.get('audio'):
                    st.markdown('<div class="audio-player">', unsafe_allow_html=True)
                    try:
                        st.audio(chat['audio'], format="audio/wav")
                    except Exception as e:
                        handle_audio_error(e)
                    st.markdown('</div>', unsafe_allow_html=True)

                if chat.get('podcast_script'):
                    st.markdown('<div class="podcast-script">', unsafe_allow_html=True)
                    st.write("Conversation Script:")
                    st.write(chat['podcast_script'])
                    st.markdown('</div>', unsafe_allow_html=True)

                if chat.get('error'):
                    display_error(chat['error'])

                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    create_custom_css()

    # Initialize
    SessionState.initialize()
    initialize_components()

    st.title("📚 Book Analysis with Podcast Answers")

    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    st.write("""
    Welcome to the Book Analysis System! Upload a book and ask questions about it.
    Get answers in both text and podcast format, featuring a natural conversation
    between two hosts discussing your questions.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Create two-column layout
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown('<div class="upload-container">', unsafe_allow_html=True)
        st.write("### Upload Book")
        uploaded_file = st.file_uploader(
            "Choose a PDF or TXT file:",
            type=["pdf", "txt"],
            help="Upload a book in PDF or TXT format"
        )

        if uploaded_file:
            handle_file_upload(uploaded_file)

        if st.session_state.chat_history:
            st.write("---")
            if st.button("🗑️ Clear History", type="secondary"):
                SessionState.clear_chat_history()
                st.success("Chat history cleared!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if st.session_state.book_content:
            if st.session_state.book_analysis:
                with st.expander("📖 Book Analysis", expanded=False):
                    st.markdown('<div class="content-container">', unsafe_allow_html=True)
                    st.write(st.session_state.book_analysis)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="question-container">', unsafe_allow_html=True)
            st.write("### Ask Your Question")
            question = st.text_area(
                "What would you like to know about the book?",
                height=100,
                placeholder="Enter your question here..."
            )

            if st.button("🔍 Ask Question", type="primary"):
                if question:
                    handle_user_question(question)
                else:
                    display_info("Please enter a question!")
            st.markdown('</div>', unsafe_allow_html=True)

            display_chat_history()
        else:
            display_info("👈 Please upload a book to start the conversation!")

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <p>Book Analysis System with AI-Powered Podcast Responses</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()