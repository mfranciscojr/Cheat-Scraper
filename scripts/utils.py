# scripts/utils.py

import logging
import re
from colorama import init, Fore, Style

def setup_logging():
    init(autoreset=True)
    logging.basicConfig(level=logging.INFO, format='%(message)s')

def sanitize_filename(filename):
    # Remove any invalid characters from the filename
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    return filename.strip()
