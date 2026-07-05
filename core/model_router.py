class ModelRouter:
    ROUTES = {
        "chat": ["glm", "gemini", "groq", "ollama", "mock"],
        "research": ["glm", "gemini", "groq", "ollama", "mock"],
        "writing": ["glm", "gemini", "groq", "ollama", "mock"],
        "planning": ["glm", "gemini", "groq", "ollama", "mock"],
        "fast": ["groq", "glm", "ollama", "mock"],
        "document": ["gemini", "glm", "ollama", "mock"],
        "critic": ["deepseek", "glm", "gemini", "ollama", "mock"],
        "code": ["deepseek", "glm", "groq", "ollama", "mock"],
        "coding": ["deepseek", "glm", "groq", "ollama", "mock"],
        "lab": ["deepseek", "glm", "gemini", "ollama", "mock"],
        "offline": ["ollama", "mock"],
        "private": ["ollama", "mock"],
    }

    def __init__(self, registry=None):
        self.registry = registry

    def normalize_task(self, task):
        task = (task or "chat").lower()
        aliases = {
            "auto": "chat",
            "rapido": "fast",
            "documento": "document",
            "critico": "critic",
            "codigo": "code",
            "laboratorio": "lab",
            "writer": "writing",
        }
        return aliases.get(task, task if task in self.ROUTES else "chat")

    def chain(self, task="chat", include_unavailable=False):
        task = self.normalize_task(task)
        route = self.ROUTES.get(task, self.ROUTES["chat"])

        if not self.registry:
            return route

        available = []
        for name in route:
            if name == "mock":
                available.append(name)
                continue

            profile = self.registry.profile(name)
            if include_unavailable or (profile and profile.available):
                available.append(name)

        return available or ["mock"]

    def decide(self, task="chat"):
        task = self.normalize_task(task)
        chain = self.chain(task)
        primary = chain[0] if chain else "mock"
        fallback = chain[1] if len(chain) > 1 else None
        return {
            "task": task,
            "primary": primary,
            "fallback": fallback,
            "chain": chain,
            "reason": "Escolhido pela ordem de prioridade multi-IA.",
        }
