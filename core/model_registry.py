class ModelRegistry:

    def __init__(self):
        self.models = {}

    def register(
        self,
        name,
        model,
        profile=None
    ):
        self.models[name] = {
            "model": model,
            "profile": profile
        }

    def show(self):
        if not self.models:
            return "Nenhum modelo registrado."

        lines = ["Modelos registrados:\n"]

        for name, entry in self.models.items():
            profile = entry.get("profile")

            if profile:
                lines.append(
                    f"{name} | {profile.name} | "
                    f"reasoning={profile.reasoning} | "
                    f"coding={profile.coding} | "
                    f"math={profile.math} | "
                    f"offline={profile.offline} | "
                    f"cost={profile.cost}"
                )
            else:
                lines.append(f"{name} | sem profile")

        return "\n".join(lines)

    def get(self, name):
        entry = self.models.get(name)

        if not entry:
            return None

        return entry.get("model")

    def profile(self, name):
        entry = self.models.get(name)

        if not entry:
            return None

        return entry.get("profile")

    def names(self):
        return list(self.models.keys())
