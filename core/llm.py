import os

from core.config import (
    CLAUDE_MODEL,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    GEMINI_MODEL,
    GROQ_BASE_URL,
    GROQ_MODEL,
    HERMES_MODEL,
    OLLAMA_MODEL,
    OPENAI_MODEL,
    QWEN_MODEL,
    ZAI_MODEL,
)
from core.model_registry import ModelRegistry
from core.model_router import ModelRouter
from core.models.claude_model import ClaudeModel
from core.models.deepseek_model import DeepSeekModel
from core.models.gemini_model import GeminiModel
from core.models.groq_model import GroqModel
from core.models.model_profile import ModelProfile
from core.models.ollama_model import OllamaModel
from core.models.openai_model import OpenAIModel
from core.models.zai_model import ZAIModel
from core.task_analyzer import TaskAnalyzer


class LLM:
    def __init__(self):
        self.registry = ModelRegistry()
        self.task_analyzer = TaskAnalyzer()
        self._register_models()
        self.router = ModelRouter(self.registry)

    def _register_models(self):
        self.registry.register(
            "glm",
            ZAIModel(ZAI_MODEL),
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
        )
        self.registry.register(
            "gemini",
            GeminiModel(GEMINI_MODEL),
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
        )
        self.registry.register(
            "groq",
            GroqModel(GROQ_MODEL, GROQ_BASE_URL),
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
        )
        self.registry.register(
            "deepseek",
            DeepSeekModel(DEEPSEEK_MODEL, DEEPSEEK_BASE_URL),
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
        )
        self.registry.register(
            "ollama",
            OllamaModel(OLLAMA_MODEL),
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
                available=True,
            ),
        )

        self.registry.register(
            "openai",
            OpenAIModel(OPENAI_MODEL),
            ModelProfile(
                name="OpenAI",
                reasoning=10,
                coding=9,
                math=10,
                writing=10,
                speed=8,
                context=200000,
                cost="paid",
                offline=False,
                available=bool(os.getenv("OPENAI_API_KEY")),
            ),
        )
        self.registry.register(
            "claude",
            ClaudeModel(CLAUDE_MODEL),
            ModelProfile(
                name="Claude",
                reasoning=9,
                coding=10,
                math=8,
                writing=9,
                speed=7,
                context=200000,
                cost="paid",
                offline=False,
                available=bool(os.getenv("ANTHROPIC_API_KEY")),
            ),
        )
        self.registry.register(
            "hermes",
            OllamaModel(HERMES_MODEL),
            ModelProfile(
                name="Hermes",
                reasoning=7,
                coding=7,
                math=6,
                writing=9,
                speed=6,
                context=32000,
                cost="free",
                offline=True,
            ),
        )
        self.registry.register(
            "qwen",
            OllamaModel(QWEN_MODEL),
            ModelProfile(
                name="Qwen",
                reasoning=7,
                coding=7,
                math=7,
                writing=7,
                speed=7,
                context=32000,
                cost="free",
                offline=True,
            ),
        )

    def ask_model(self, model_name, system_prompt, user_prompt, fallback="ollama"):
        model = self.registry.get(model_name)

        if not model:
            raise ValueError(f"Modelo nao registrado: {model_name}")

        try:
            return model.generate(system_prompt, user_prompt)
        except Exception:
            if fallback and fallback != model_name:
                fallback_model = self.registry.get(fallback)
                if fallback_model:
                    return fallback_model.generate(system_prompt, user_prompt)
            raise

    def ask(self, system_prompt, user_prompt, task=None):
        if task is None:
            task = self.task_analyzer.analyze(user_prompt)

        route = self.router.decide(task)
        last_error = None
        for model_name in route.get("chain", []):
            if model_name == "mock":
                break
            model = self.registry.get(model_name)
            if not model:
                continue
            try:
                return model.generate(system_prompt, user_prompt)
            except Exception as exc:
                last_error = exc

        if last_error:
            raise last_error
        raise RuntimeError("Nenhum modelo disponivel.")
