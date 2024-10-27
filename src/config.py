"""Configuration settings for the application."""

# Text Analysis Settings
MAX_CHUNK_SIZE = 8000
MODEL_NAME = 'gemini-pro'

# Audio Settings
SILENCE_DURATION = 500  # milliseconds
VOICES = {
    'voice1': {'lang': 'en', 'tld': 'com'},      # US English
    'voice2': {'lang': 'en', 'tld': 'co.uk'}     # British English
}

# UI Settings
PAGE_TITLE = "Book Analysis Podcast"
PAGE_ICON = "📚"
LAYOUT = "wide"

# Error Messages
ERROR_MESSAGES = {
    'no_api_key': 'API key not found in secrets!',
    'file_read_error': 'Error reading file: {}',
    'analysis_error': 'Error analyzing book: {}',
    'audio_error': 'Error generating audio: {}'
}