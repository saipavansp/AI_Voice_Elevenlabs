"""Module for processing book files."""
import streamlit as st
from PyPDF2 import PdfReader
from typing import Optional
import tempfile
from .config import ERROR_MESSAGES


class BookProcessor:
    @staticmethod
    def read_pdf_file(file) -> Optional[str]:
        """Read content from PDF file."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_file.seek(0)

                pdf_reader = PdfReader(tmp_file.name)
                text_content = ""
                total_pages = len(pdf_reader.pages)

                progress_bar = st.progress(0)
                for i, page in enumerate(pdf_reader.pages):
                    text_content += page.extract_text() + "\n"
                    progress = (i + 1) / total_pages
                    progress_bar.progress(progress, f"Reading page {i+1}/{total_pages}")

                progress_bar.empty()
                return text_content.strip()
        except Exception as e:
            st.error(ERROR_MESSAGES['file_read_error'].format(str(e)))
            return None

    @staticmethod
    def read_text_file(file) -> Optional[str]:
        """Read content from text file."""
        try:
            return file.getvalue().decode('utf-8')
        except Exception as e:
            st.error(ERROR_MESSAGES['file_read_error'].format(str(e)))
            return None

    @staticmethod
    def process_file(file) -> Optional[str]:
        """Process uploaded file and extract content."""
        try:
            if file.name.lower().endswith('.pdf'):
                return BookProcessor.read_pdf_file(file)
            else:
                return BookProcessor.read_text_file(file)
        except Exception as e:
            st.error(ERROR_MESSAGES['file_read_error'].format(str(e)))
            return None

    @staticmethod
    def get_file_info(file) -> dict:
        """Get information about the uploaded file."""
        return {
            'name': file.name,
            'type': file.type,
            'size': f"{file.size / 1024:.1f} KB"
        }