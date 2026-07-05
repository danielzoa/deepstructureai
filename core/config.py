from pathlib import Path
import os
OBSIDIAN_VAULT_PATH = r"C:\NTG\ObsidianVault"
LLM_PROVIDER = "ollama"  # opções: "openai" ou "ollama"

OPENAI_MODEL = "gpt-5.5"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_URL = os.getenv("OLLAMA_URL", f"{OLLAMA_BASE_URL}/api/chat")

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_NAME = "gpt-5.5"

MEMORY_FILE = ROOT_DIR / "data" / "memory.json"
JOURNAL_FILE = ROOT_DIR / "data" / "journal.json"
TASK_FILE = ROOT_DIR / "data" / "tasks.json"
GOAL_FILE = ROOT_DIR / "data" / "goals.json"
LOG_FILE = ROOT_DIR / "logs" / "agent.log"
PROFILE_DIR = ROOT_DIR / "knowledge" / "profile"
SEMANTIC_MEMORY_FILE = ROOT_DIR / "data" / "semantic_memory.db"
LAB_NOTEBOOK_FILE = ROOT_DIR / "data" / "laboratory.db"
IDEA_VALIDATION_FILE = ROOT_DIR / "data" / "idea_validations.db"
KNOWLEDGE_GRAPH_FILE = ROOT_DIR / "data" / "knowledge_graph.db"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 512

LLM_PROVIDER = "router"

DEFAULT_MODEL_TASK = "chat"

MODEL_ROUTING = {
    "chat": {
        "primary": "ollama",
        "fallback": "openai"
    },
    "research": {
        "primary": "openai",
        "fallback": "ollama"
    },
    "coding": {
        "primary": "openai",
        "fallback": "ollama"
    },
    "fast": {
        "primary": "ollama",
        "fallback": "openai"
    },
    "private": {
        "primary": "ollama",
        "fallback": None
    }
}

OPENAI_MODEL = "gpt-5.5"
HERMES_MODEL = "hermes3"
OLLAMA_MODEL = "qwen2.5:3b"
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
QWEN_MODEL = "qwen3:4b"
CLAUDE_MODEL = "claude-sonnet-4-5"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_URL = os.getenv("OLLAMA_URL", f"{OLLAMA_BASE_URL}/api/chat")
ZAI_BASE_URL = os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4")
ZAI_MODEL = os.getenv("ZAI_MODEL", "GLM-5.2")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "glm")
DEFAULT_FAST_MODEL = os.getenv("DEFAULT_FAST_MODEL", "groq")
DEFAULT_DOCUMENT_MODEL = os.getenv("DEFAULT_DOCUMENT_MODEL", "gemini")
DEFAULT_CRITIC_MODEL = os.getenv("DEFAULT_CRITIC_MODEL", "deepseek")
DEFAULT_OFFLINE_MODEL = os.getenv("DEFAULT_OFFLINE_MODEL", "ollama")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
