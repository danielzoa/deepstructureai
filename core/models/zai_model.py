import os

from openai import OpenAI

from core.models.base_model import BaseModel


class ZAIModel(BaseModel):
    name = "glm"

    def __init__(self, model_name=None, base_url=None, api_key=None):
        self.api_key = api_key or os.getenv("ZAI_API_KEY")
        env_base_url = os.getenv("ZAI_BASE_URL")
        uses_openrouter_key = bool(self.api_key and self.api_key.startswith("sk-or-"))
        env_model = os.getenv("ZAI_MODEL")
        if uses_openrouter_key:
            self.base_url = base_url or "https://openrouter.ai/api/v1"
            self.model_name = model_name or (
                "z-ai/glm-5.2" if not env_model or env_model == "GLM-5.2" else env_model
            )
        else:
            self.base_url = base_url or env_base_url or "https://api.z.ai/api/paas/v4"
            self.model_name = model_name or env_model or "GLM-5.2"
        self.max_tokens = int(os.getenv("ZAI_MAX_TOKENS", "4096"))
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
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content or ""
