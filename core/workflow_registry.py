class WorkflowRegistry:

    def __init__(self):
        self.workflows = {}

    def register(self, name, workflow):
        self.workflows[name] = workflow

    def get(self, name):
        return self.workflows.get(name)

    def names(self):
        return list(self.workflows.keys())

    def show(self):
        if not self.workflows:
            return "Nenhum workflow registrado."

        lines = ["Workflows disponíveis:"]

        for name in self.workflows:
            lines.append(f"- {name}")

        return "\n".join(lines)