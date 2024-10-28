"""Module for managing Streamlit session state."""
import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime

class SessionState:
    @staticmethod
    def initialize():
        """Initialize session state variables."""
        if 'book_content' not in st.session_state:
            st.session_state.book_content = None
        if 'book_analysis' not in st.session_state:
            st.session_state.book_analysis = None
        if 'podcast_audio' not in st.session_state:
            st.session_state.podcast_audio = None
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    @staticmethod
    def update_book_content(content: Optional[str]):
        """Update book content in session state."""
        st.session_state.book_content = content

    @staticmethod
    def update_book_analysis(analysis: Optional[str]):
        """Update book analysis in session state."""
        st.session_state.book_analysis = analysis

    @staticmethod
    def update_podcast_audio(audio: Optional[bytes]):
        """Update podcast audio in session state."""
        st.session_state.podcast_audio = audio

    @staticmethod
    def add_to_chat_history(message: Dict[str, str]):
        """Add a message to the chat history."""

        st.session_state.chat_history.append(message)

    @staticmethod
    def clear_chat_history():
        """Clear the chat history."""
        st.session_state.chat_history = []

    @staticmethod
    def clear_all():
        """Clear all session state data."""
        st.session_state.book_content = None
        st.session_state.book_analysis = None
        st.session_state.podcast_audio = None
        st.session_state.chat_history = []