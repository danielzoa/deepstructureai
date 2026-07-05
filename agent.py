from dotenv import load_dotenv
from deepstructure import DeepStructureAI
import sys

load_dotenv()

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    agent = DeepStructureAI()
    agent.chat()
