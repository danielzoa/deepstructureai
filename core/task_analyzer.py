class TaskAnalyzer:
    def __init__(self):
        self.rules = {
            "coding": ["python", "classe", "função", "código", "bug", "programa", "algoritmo"],
            "research": ["navier", "paper", "artigo", "hipótese", "teorema", "prova", "pesquisa", "ntg"],
            "pdf": ["pdf", "livro", "capítulo", "documento"],
            "math": ["equação", "integral", "derivada", "tensor", "matriz"],
            "fast": ["rápido", "resuma", "curto", "direto"],
            "private": ["privado", "offline", "local", "sensível"]
        }

    def analyze(self, text):
        text = text.lower()

        for task, keywords in self.rules.items():
            if any(keyword in text for keyword in keywords):
                return task

        return "chat"