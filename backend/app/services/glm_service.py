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
            raise RuntimeError("ZAI_API_KEY nao configurada.")

        from core.models.zai_model import ZAIModel

        system_prompt = (
            "Voce e o DeepStructureAI, assistente de pesquisa cientifica em NTG. "
            "Responda em portugues, com clareza, rigor e foco operacional."
        )
        if mode == "critic":
            system_prompt += " Aponte riscos, falhas e contraexemplos relevantes."
        elif mode == "writer":
            system_prompt += " Estruture a resposta como texto cientifico revisavel."
        elif mode == "lab":
            system_prompt += " Foque em hipoteses, evidencias, testes e proximos passos."
        elif mode == "research":
            system_prompt += " Foque em investigacao, fontes e conexoes conceituais."

        return ZAIModel(self.model_name, self.base_url).generate(system_prompt, message)
