# scripts/constants.py

from threading import local

class ThreadLocalVar(local):
    def __init__(self):
        self.value = None

# Global variable for the API token
CHEATSLIPS_API_TOKEN = ThreadLocalVar()
