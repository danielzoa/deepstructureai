import os
from core.config import LOG_FILE

class Logger:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file

        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log(self, event, details=""):
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        line = f"[{timestamp}] {event}"

        if details:
            line += f" | {details}"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")