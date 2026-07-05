import os
from anthropic import Anthropic

from core.models.base_model import BaseModel


class ClaudeModel(BaseModel):
    name = "claude"

    def __init__(self, model_name):
        self.model_name = model_name
        self.client = None

    def _client(self):
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY nao configurada.")
        if self.client is None:
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        return self.client

    def generate(self, system_prompt, user_prompt):
        response = self._client().messages.create(
            model=self.model_name,
            max_tokens=1200,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )

        return response.content[0].text
