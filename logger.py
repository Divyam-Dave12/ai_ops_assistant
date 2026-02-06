import logging
import os
import sys
from datetime import datetime

# 1. Create logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 2. Generate a unique filename based on the current time
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"error_log_{timestamp}.log")

# 3. Configure the Logger
logger = logging.getLogger("AI_Movie_Assistant")

# Global Gate: We allow INFO and up to enter the system
logger.setLevel(logging.INFO)

if not logger.handlers:
    # --- HANDLER 1: FILE (Strict - Errors Only) ---
    # This ensures the log file stays empty unless something actually breaks.
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.ERROR)  # <--- HERE IS THE MAGIC
    file_format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # --- HANDLER 2: CONSOLE (Verbose - See everything running) ---
    # This lets you watch the agents work in your terminal window.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # <--- Shows Info + Errors
    console_format = logging.Formatter('👉 %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

def get_logger(module_name):
    """
    Creates a child logger for a specific module (e.g., 'Planner', 'Executor')
    """
    return logger.getChild(module_name)

print(f"📝 Error Logging initialized at: {LOG_FILE}")