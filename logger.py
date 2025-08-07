# logger.py

from rich.console import Console
from datetime import datetime
import os

console = Console()

# Defaults – can be changed in main.py

LOG_TO_FILE = False
LOG_FILE = "logs/session.log"

def _write_to_file(message, level):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level.upper()}] {message}\n")

def log(message, style=None, level="info"):

    if LOG_TO_FILE:
        _write_to_file(message, level)

# Semantic shortcuts
def info(msg): log(msg, "cyan", "info")
def success(msg): log(f"✔ {msg}", "green", "success")
def warn(msg): log(f"! {msg}", "orange3", "warn")
def error(msg): log(f"✘ {msg}", "red", "error")
