"""Module for analyzing text using Google's Gemini API."""
import streamlit as st
import google.generativeai as genai
from typing import Dict, Any, Optional
from .config import MAX_CHUNK_SIZE, MODEL_NAME, ERROR_MESSAGES
from .logger import logger

class TextAnalyzer:
    def __init__(self):
        """Initialize the text analyzer."""
        try:
            if 'GOOGLE_API_KEY' not in st.secrets:
                raise ValueError(ERROR_MESSAGES['no_api_key'])

            genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])
            self.model = genai.GenerativeModel(MODEL_NAME)
            self.chunk_size = MAX_CHUNK_SIZE
        except Exception as e:
            logger.error(f"Error initializing TextAnalyzer: {str(e)}", exc_info=True)
            st.error("Failed to initialize TextAnalyzer. Check the logs for more details.")
            st.stop()

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into manageable chunks."""
        return [text[i:i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size)]

    def generate_summary(self, content: str) -> str:
        """Generate a summary of the content."""
        try:
            chunks = self._chunk_text(content)
            summaries = []

            for chunk in chunks:
                prompt = """
                Provide a concise summary of the following content. Focus on the main ideas and key points:

                Content: {content}

                Summary:
                """

                response = self.model.generate_content(prompt.format(content=chunk))

                summaries.append(response.text)

            combined_summary = "\n\n".join(summaries)

            # Generate a final, condensed summary
            final_summary_prompt = f"""
            Condense the following summaries into a single, coherent summary of no more than 500 words:

            {combined_summary}

            Final Summary:
            """

            final_summary = self.model.generate_content(final_summary_prompt)
            return final_summary.text

        except Exception as e:
            logger.error(f"Error in generate_summary: {str(e)}", exc_info=True)
            return f"Error generating summary: {str(e)}"

    def create_podcast_script(self, summary: str) -> str:
        """Convert summary to a natural conversation format for a podcast."""
        try:
            prompt = """
            Convert this summary into a natural podcast conversation between Sarah and Mike.
            Sarah is an enthusiastic book expert, and Mike is a curious interviewer.

            Make it sound natural with:
            - Casual conversation flow
            - Questions and follow-ups
            - Personal insights
            - Clear explanations
            - Engaging discussion

            The conversation should be around 5-7 minutes long when spoken.

            Format each line as: 
            Sarah: [dialogue]
            Mike: [dialogue]

            Summary to convert:
            {summary}
            """

            response = self.model.generate_content(prompt.format(summary=summary))
            return response.text
        except Exception as e:
            logger.error(f"Error in create_podcast_script: {str(e)}", exc_info=True)
            return f"Error creating podcast script: {str(e)}"

    def answer_question(self, question: str, content: str) -> str:
        """Generate answer using Gemini."""
        try:
            chunks = self._chunk_text(content)
            best_response = ""

            for chunk in chunks:
                prompt = f"""
                Based on this content, answer the following question:
                Question: {question}
                
                Content: {chunk}
                
                Provide a detailed answer using specific information from the content.
                Include examples and explain your reasoning.
                """

                response = self.model.generate_content(prompt)
                if len(response.text) > len(best_response):
                    best_response = response.text

            return best_response

        except Exception as e:
            logger.error(f"Error in answer_question: {str(e)}", exc_info=True)
            return f"Error generating answer: {str(e)}"