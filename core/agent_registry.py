from datetime import datetime


class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, name, agent, role, description):
        self.agents[name] = {
            "instance": agent,
            "role": role,
            "description": description,
            "calls": 0,
            "last_execution": None,
            "last_project": None,
            "last_question": None,
            "total_time": 0.0,
        }

    def get(self, name):
        data = self.agents.get(name)
        return data["instance"] if data else None

    def record_execution(self, name, context, elapsed):
        data = self.agents.get(name)
        if data is None:
            return

        data["calls"] += 1
        data["last_execution"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["last_project"] = context.project
        data["last_question"] = context.question
        data["total_time"] += elapsed

    def names(self):
        return list(self.agents)

    def info(self, name):
        return self.agents.get(name)

    def show(self):
        if not self.agents:
            return "Nenhum agente registrado."
        return "\n".join(
            f"{name} | {data['role']} | chamadas: {data['calls']}"
            for name, data in self.agents.items()
        )

    def describe(self, name):
        data = self.agents.get(name)
        if not data:
            return f"Agente não encontrado: {name}"

        return (
            f"Nome:\n{name}\n\n"
            f"Função:\n{data['role']}\n\n"
            f"Descrição:\n{data['description']}\n\n"
            f"Chamadas:\n{data['calls']}"
        )
