class AgentPlanner:
    def __init__(self):
        self.rules = {
            "coding": {
                "keywords": ["código", "python", "bug", "classe", "função", "programar", "implementar"],
                "team": ["coordinator", "programmer", "reviewer"]
            },
            "math": {
                "keywords": ["prova", "teorema", "lema", "demonstração", "equação", "estimativa"],
                "team": ["coordinator", "mathematician", "reviewer"]
            },
            "physics": {
                "keywords": ["física", "navier", "vorticidade", "stretching", "pressão", "energia"],
                "team": ["coordinator", "physicist", "mathematician", "reviewer"]
            },
            "paper": {
                "keywords": ["paper", "artigo", "arxiv", "pdf"],
                "team": ["coordinator", "paper_analyst", "reviewer"]
            },
            "explain": {
                "keywords": ["explique", "explica", "intuitivo", "didático", "entender"],
                "team": ["coordinator", "explainer"]
            }
        }

    def plan(self, question):
        text = question.lower()

        for category, rule in self.rules.items():
            if any(k in text for k in rule["keywords"]):
                return {
                    "category": category,
                    "team": rule["team"],
                    "reason": f"Detectado como tarefa de {category}."
                }

        return {
            "category": "general",
            "team": ["coordinator", "reviewer", "mathematician"],
            "reason": "Nenhuma categoria específica detectada."
        }