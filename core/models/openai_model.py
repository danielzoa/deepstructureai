from openai import OpenAI
from core.models.base_model import BaseModel


class OpenAIModel(BaseModel):
    name = "openai"

    def __init__(self, model_name):
        self.model_name = model_name
        self.client = None

    def _client(self):
        if self.client is None:
            self.client = OpenAI()
        return self.client

    def generate(self, system_prompt, user_prompt):
        response = self._client().responses.create(
            model=self.model_name,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response.output_text
