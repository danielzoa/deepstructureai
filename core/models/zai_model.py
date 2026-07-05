import os

from openai import OpenAI

from core.models.base_model import BaseModel


class ZAIModel(BaseModel):
    name = "glm"

    def __init__(self, model_name=None, base_url=None, api_key=None):
        self.model_name = model_name or os.getenv("ZAI_MODEL", "GLM-5.2")
        self.base_url = base_url or os.getenv(
            "ZAI_BASE_URL",
            "https://api.z.ai/api/paas/v4",
        )
        self.api_key = api_key or os.getenv("ZAI_API_KEY")
        self.client = None

    @property
    def available(self):
        return bool(self.api_key)

    def _client(self):
        if not self.api_key:
            raise RuntimeError("ZAI_API_KEY nao configurada.")

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
