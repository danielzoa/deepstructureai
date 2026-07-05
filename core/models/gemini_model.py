import os

import requests

from core.models.base_model import BaseModel


class GeminiModel(BaseModel):
    name = "gemini"

    def __init__(self, model_name=None, api_key=None):
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    @property
    def available(self):
        return bool(self.api_key)

    def generate(self, system_prompt, user_prompt):
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY nao configurada.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent"
        )
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
        }
        response = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "\n".join(part.get("text", "") for part in parts).strip()
