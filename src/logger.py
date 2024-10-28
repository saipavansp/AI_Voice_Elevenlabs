import logging
import streamlit as st

def setup_logger():
    """Set up and configure the logger."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create a StreamHandler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    # Create a custom Streamlit handler
    class StreamlitHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            if record.levelno >= logging.ERROR:
                st.error(log_entry)
            elif record.levelno >= logging.WARNING:
                st.warning(log_entry)
            elif record.levelno >= logging.INFO:
                st.info(log_entry)

    streamlit_handler = StreamlitHandler()
    streamlit_handler.setFormatter(formatter)
    logger.addHandler(streamlit_handler)

    return logger

# Create and configure the logger
logger = setup_logger()