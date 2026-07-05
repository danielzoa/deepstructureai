import requests
from core.models.base_model import BaseModel
import os


class OllamaModel(BaseModel):
    name = "ollama"

    def __init__(self, model_name=None, url=None):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.url = url or os.getenv("OLLAMA_URL", f"{base_url}/api/chat")

    def generate(self, system_prompt, user_prompt):
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()
        return data["message"]["content"]
