import os
from dataclasses import dataclass

import httpx

from core.model_registry import ModelRegistry
from core.model_router import ModelRouter
from core.models.deepseek_model import DeepSeekModel
from core.models.gemini_model import GeminiModel
from core.models.groq_model import GroqModel
from core.models.model_profile import ModelProfile
from core.models.ollama_model import OllamaModel
from core.models.zai_model import ZAIModel


@dataclass
class ModelResult:
    answer: str
    model: str
    warnings: list[str]


class MultiAIService:
    def __init__(self):
        self.registry = ModelRegistry()
        self._register()
        self.router = ModelRouter(self.registry)

    def _register(self):
        ollama_available = self._ollama_available()
        entries = [
            (
                "glm",
                ZAIModel(),
                ModelProfile(
                    name="GLM / Z.AI",
                    reasoning=9,
                    coding=9,
                    math=8,
                    writing=8,
                    speed=8,
                    context=1000000,
                    cost="api",
                    offline=False,
                    available=bool(os.getenv("ZAI_API_KEY")),
                ),
            ),
            (
                "gemini",
                GeminiModel(),
                ModelProfile(
                    name="Gemini",
                    reasoning=8,
                    coding=7,
                    math=8,
                    writing=9,
                    speed=8,
                    context=1000000,
                    cost="api",
                    offline=False,
                    available=bool(os.getenv("GEMINI_API_KEY")),
                ),
            ),
            (
                "groq",
                GroqModel(),
                ModelProfile(
                    name="Groq",
                    reasoning=7,
                    coding=7,
                    math=6,
                    writing=7,
                    speed=10,
                    context=128000,
                    cost="api",
                    offline=False,
                    available=bool(os.getenv("GROQ_API_KEY")),
                ),
            ),
            (
                "deepseek",
                DeepSeekModel(),
                ModelProfile(
                    name="DeepSeek",
                    reasoning=9,
                    coding=9,
                    math=9,
                    writing=7,
                    speed=7,
                    context=128000,
                    cost="api",
                    offline=False,
                    available=bool(os.getenv("DEEPSEEK_API_KEY")),
                ),
            ),
            (
                "ollama",
                OllamaModel(),
                ModelProfile(
                    name="Ollama",
                    reasoning=6,
                    coding=6,
                    math=5,
                    writing=6,
                    speed=7,
                    context=32000,
                    cost="free",
                    offline=True,
                    available=ollama_available,
                ),
            ),
        ]
        for name, model, profile in entries:
            self.registry.register(name, model, profile)

    def refresh(self):
        self.registry = ModelRegistry()
        self._register()
        self.router = ModelRouter(self.registry)

    def _ollama_available(self):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        try:
            response = httpx.get(f"{base_url}/api/tags", timeout=0.8)
            return response.status_code == 200
        except Exception:
            return False

    def models(self):
        self.refresh()
        models = []
        for name in ["glm", "gemini", "groq", "deepseek", "ollama"]:
            profile = self.registry.profile(name)
            models.append(
                {
                    "id": name,
                    "name": profile.name if profile else name,
                    "available": bool(profile and profile.available),
                    "offline": bool(profile and profile.offline) if profile else False,
                    "role": self.role_for(name),
                }
            )
        return models

    def role_for(self, name):
        return {
            "glm": "principal, planejamento, escrita, pesquisa e coordenação",
            "gemini": "documentos longos, PDFs, contexto grande e multimodal futuro",
            "groq": "respostas rápidas, comandos, status e triagem",
            "deepseek": "crítica, validação lógica, matemática e revisão",
            "ollama": "modo local/offline e fallback privado",
        }.get(name, "")

    def status(self):
        self.refresh()
        return {
            "models": self.models(),
            "routes": {
                key: self.router.chain(key, include_unavailable=True)
                for key in ["chat", "fast", "document", "critic", "code", "lab", "offline"]
            },
            "activeRoutes": {
                key: self.router.chain(key)
                for key in ["chat", "fast", "document", "critic", "code", "lab", "offline"]
            },
        }

    def generate(self, message: str, mode: str = "chat", requested_model: str | None = "auto"):
        self.refresh()
        normalized_mode = self.router.normalize_task(mode)
        warnings = []

        if requested_model and requested_model != "auto":
            chain = [requested_model, "mock"]
        else:
            chain = self.router.chain(normalized_mode)

        system_prompt = self.system_prompt(normalized_mode)

        for model_name in chain:
            if model_name == "mock":
                break
            model = self.registry.get(model_name)
            if not model:
                continue
            try:
                answer = model.generate(system_prompt, message)
                return ModelResult(answer=answer, model=model_name, warnings=warnings)
            except Exception:
                warnings.append(f"{model_name}_failed")

        return ModelResult(
            answer=(
                "Modo demo/fallback ativo: recebi sua mensagem e mantive o fluxo do "
                "DeepStructureAI sem expor ou exigir chaves no cliente."
            ),
            model="mock",
            warnings=warnings or ["mock_fallback"],
        )

    def system_prompt(self, mode):
        base = (
            "Você é o DeepStructureAI, assistente de pesquisa científica em NTG. "
            "Responda em português, com clareza, rigor e foco operacional."
        )
        prompts = {
            "fast": " Seja breve, direto e útil para triagem ou status.",
            "document": " Priorize contexto longo, documentos, PDFs e explicações estruturadas.",
            "critic": " Atue como revisor crítico: encontre falhas, riscos e contraexemplos.",
            "code": " Foque em análise de código, riscos, testes e mudanças pequenas.",
            "lab": " Foque em hipóteses, evidências, testes, progresso e próximos passos.",
            "offline": " Responda em modo local/privado, sem depender de serviços externos.",
        }
        return base + prompts.get(mode, "")


multi_ai = MultiAIService()
