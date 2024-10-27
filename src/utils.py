"""Utility functions for the application."""
import streamlit as st
import base64
from typing import Optional
from datetime import datetime

def format_timestamp(dt: datetime) -> str:
    """Format timestamp for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def display_error(message: str):
    """Display error message with consistent styling."""
    st.error(f"🚫 {message}")

def display_success(message: str):
    """Display success message with consistent styling."""
    st.success(f"✅ {message}")

def display_info(message: str):
    """Display info message with consistent styling."""
    st.info(f"ℹ️ {message}")

def create_expander_header(title: str, emoji: str = "") -> str:
    """Create consistently styled expander header."""
    return f"{emoji} {title}" if emoji else title

def create_download_link(data: bytes, filename: str) -> str:
    """Create download link for audio file."""
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download Audio</a>'

def get_file_size_str(size_in_bytes: int) -> str:
    """Convert file size to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f} TB"