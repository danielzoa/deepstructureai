import os

from dotenv import load_dotenv

load_dotenv()


class GLMService:
    def __init__(self):
        self.model_name = os.getenv("ZAI_MODEL", "GLM-5.2")
        self.base_url = os.getenv(
            "ZAI_BASE_URL",
            "https://api.z.ai/api/coding/paas/v4",
        )

    @property
    def configured(self):
        return bool(os.getenv("ZAI_API_KEY"))

    def generate(self, message: str, mode: str = "chat") -> str:
        if not self.configured:
            raise RuntimeError("ZAI_API_KEY não configurada.")

        from core.models.zai_model import ZAIModel

        system_prompt = (
            "Você é o DeepStructureAI, assistente de pesquisa científica em NTG. "
            "Responda em português, com clareza, rigor e foco operacional."
        )
        if mode == "critic":
            system_prompt += " Aponte riscos, falhas e contraexemplos relevantes."
        elif mode == "writer":
            system_prompt += " Estruture a resposta como texto científico revisável."
        elif mode == "lab":
            system_prompt += " Foque em hipóteses, evidências, testes e próximos passos."
        elif mode == "research":
            system_prompt += " Foque em investigação, fontes e conexões conceituais."

        return ZAIModel(self.model_name, self.base_url).generate(system_prompt, message)
