import os

from openai import OpenAI

from core.models.base_model import BaseModel


class GroqModel(BaseModel):
    name = "groq"

    def __init__(self, model_name=None, base_url=None, api_key=None):
        self.model_name = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.base_url = base_url or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None

    @property
    def available(self):
        return bool(self.api_key)

    def _client(self):
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY nao configurada.")
        if self.client is None:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self.client

    def generate(self, system_prompt, user_prompt):
        response = self._client().chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
