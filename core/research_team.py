class ResearchTeam:
    def __init__(self):
        self.roles = {
            "coordinator": {
                "model": "ollama",
                "goal": "Organizar a análise, decidir a estratégia e produzir síntese."
            },
            "mathematician": {"model": "deepseek", "goal": "Verificar rigor matemático, hipóteses, lemas e lacunas."},
            "programmer": {"model": "qwen", "goal": "Implementar, revisar e depurar código científico."},
            "reviewer": {"model": "deepseek", "goal": "Encontrar falhas, circularidades e riscos."},
            "explainer": {"model": "hermes", "goal": "Explicar ideias de forma clara, criativa e intuitiva."}
        }

    def role(self, name):
        return self.roles.get(name)

    def model_for(self, name):
        role = self.role(name)
        if not role:
            return None
        return role["model"]

    def goal_for(self, name):
        role = self.role(name)
        if not role:
            return ""
        return role["goal"]

    def summary(self):
        lines = ["Research Team\n"]

        for role, data in self.roles.items():
            lines.append(
                f"{role:15} -> {data['model']} | {data['goal']}"
            )

        return "\n".join(lines)