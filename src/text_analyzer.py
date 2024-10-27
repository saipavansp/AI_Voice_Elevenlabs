"""Module for analyzing text using Google's Gemini API."""
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Optional
from .config import MAX_CHUNK_SIZE, MODEL_NAME, ERROR_MESSAGES

class TextAnalyzer:
    def __init__(self):
        """Initialize the text analyzer."""
        if 'GOOGLE_API_KEY' not in st.secrets:
            st.error(ERROR_MESSAGES['no_api_key'])
            st.stop()

        genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.chunk_size = MAX_CHUNK_SIZE

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into manageable chunks."""
        return [text[i:i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size)]

    def analyze_text(self, content: str) -> Dict[str, Any]:
        """Analyze book content using Gemini."""
        try:
            chunks = self._chunk_text(content)
            analyses = []

            for chunk in chunks:
                prompt = """
                Analyze this book content and provide:
                1. Brief summary
                2. Main themes and key concepts
                3. Important points and insights
                4. Key takeaways
                
                Content: {content}
                """

                response = self.model.generate_content(prompt.format(content=chunk))
                analyses.append(response.text)

            combined_analysis = "\n\n".join(analyses)

            return {
                'success': True,
                'analysis': combined_analysis
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def answer_question(self, question: str, content: str) -> str:
        """Generate answer using Gemini."""
        try:
            chunks = self._chunk_text(content)
            best_response = ""

            for chunk in chunks:
                prompt = f"""
                Based on this book content, answer the following question:
                Question: {question}
                
                Content: {chunk}
                
                Provide a detailed answer using specific information from the book.
                Include examples and explain your reasoning.
                """

                response = self.model.generate_content(prompt)
                if len(response.text) > len(best_response):
                    best_response = response.text

            return best_response

        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def create_podcast_script(self, text: str) -> Optional[str]:
        """Convert text to natural conversation format."""
        try:
            prompt = """
            Convert this text into a natural podcast conversation between Sarah and Mike.
            Sarah is an enthusiastic book expert, and Mike is a curious interviewer.
            
            Make it sound natural with:
            - Casual conversation flow
            - Questions and follow-ups
            - Personal insights
            - Clear explanations
            - Engaging discussion
            
            Format each line as: 
            Sarah: [dialogue]
            Mike: [dialogue]
            
            Text to convert:
            {text}
            """

            response = self.model.generate_content(prompt.format(text=text))
            return response.text
        except Exception as e:
            st.error(f"Error creating conversation: {str(e)}")
            return None