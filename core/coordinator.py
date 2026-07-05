class Coordinator:
    def decide(self, message):
        text = message.lower()

        critic_keywords = [
            "hipótese",
            "falha",
            "critique",
            "crítica",
            "refutar",
            "contraexemplo",
            "parece boa",
            "está certa",
        ]

        planner_keywords = [
            "plano",
            "planeje",
            "como continuamos",
            "continuar",
            "próximo passo",
            "o que fazemos agora",
        ]

        researcher_keywords = [
            "pesquise",
            "explore",
            "novas ideias",
            "alternativas",
            "hipóteses novas",
        ]

        if any(keyword in text for keyword in critic_keywords):
            return "critic"

        if any(keyword in text for keyword in planner_keywords):
            return "planner"

        if any(keyword in text for keyword in researcher_keywords):
            return "researcher"

        return "chat"