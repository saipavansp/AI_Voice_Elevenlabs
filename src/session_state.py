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
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'current_file' not in st.session_state:
            st.session_state.current_file = None

    @staticmethod
    def add_to_chat_history(question: str, response: Dict[str, Any]):
        """Add Q&A interaction to chat history."""
        st.session_state.chat_history.append({
            'timestamp': datetime.now(),
            'question': question,
            'answer': response.get('text_answer'),
            'podcast_script': response.get('podcast_script'),
            'audio': response.get('audio'),
            'error': response.get('error')
        })

    @staticmethod
    def get_recent_chat_history(limit: int = 5) -> list:
        """Get recent chat history."""
        return list(reversed(st.session_state.chat_history[-limit:]))

    @staticmethod
    def clear_chat_history():
        """Clear chat history."""
        st.session_state.chat_history = []

    @staticmethod
    def update_book_content(content: Optional[str]):
        """Update book content in session state."""
        st.session_state.book_content = content

    @staticmethod
    def update_book_analysis(analysis: Optional[Dict[str, Any]]):
        """Update book analysis in session state."""
        st.session_state.book_analysis = analysis