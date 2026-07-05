class SpecialistRegistry:

    def __init__(self):

        self.specialists = {

            "coordinator": [
                "ollama",
                "openai"
            ],

            "mathematician": [
                "ollama"
            ],

            "physicist": [
                "ollama"
            ],

            "programmer": [
                "ollama"
            ],

            "paper_analyst": [
                "ollama"
            ],

            "reviewer": [
                "ollama"
            ],

            "explainer": [
                "hermes",
                "ollama"
            ]
        }

    def models(self, specialist):

        return self.specialists.get(
            specialist,
            []
        )

    def primary(self, specialist):

        models = self.models(
            specialist
        )

        if not models:
            return None

        return models[0]

    def add_model(
        self,
        specialist,
        model
    ):

        self.specialists.setdefault(
            specialist,
            []
        )

        if model not in self.specialists[specialist]:

            self.specialists[specialist].append(
                model
            )

    def summary(self):

        lines = []

        lines.append(
            "Specialist Registry\n"
        )

        for spec, models in self.specialists.items():

            lines.append(
                f"{spec:15} -> {', '.join(models)}"
            )

        return "\n".join(lines)