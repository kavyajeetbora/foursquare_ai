"""
General utility functions.
"""
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logging.info("Logging is set up.")
