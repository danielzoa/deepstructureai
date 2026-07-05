import json
import os
from datetime import datetime
from core.config import GOAL_FILE


class GoalManager:
    def __init__(self, goal_file=GOAL_FILE):
        self.goal_file = goal_file
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.goal_file):
            return {
                "current_goal": None,
                "goals": []
            }

        with open(self.goal_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        with open(self.goal_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def create(self, description, project="Geral"):
        goal = {
            "description": description,
            "project": project,
            "status": "Ativo",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.data["goals"].append(goal)
        self.data["current_goal"] = description
        self.save()

        return f"Objetivo criado e ativado: {description}"

    def list(self):
        goals = self.data.get("goals", [])

        if not goals:
            return "Nenhum objetivo registrado."

        current = self.data.get("current_goal")
        lines = []

        for i, goal in enumerate(goals, start=1):
            marker = "*" if goal["description"] == current else "-"
            lines.append(
                f"{i}. {marker} [{goal.get('project', 'Geral')}] "
                f"{goal['description']} ({goal['status']})"
            )

        return "\n".join(lines)

    def use(self, index):
        try:
            idx = int(index) - 1
            goal = self.data["goals"][idx]
        except (ValueError, IndexError):
            return "Índice inválido."

        self.data["current_goal"] = goal["description"]
        self.save()

        return f"Objetivo ativo agora: {goal['description']}"

    def current(self):
        goal = self.data.get("current_goal")

        if not goal:
            return "Nenhum objetivo ativo."

        return goal

    def complete(self, index):
        try:
            idx = int(index) - 1
            goal = self.data["goals"][idx]
        except (ValueError, IndexError):
            return "Índice inválido."

        goal["status"] = "Concluído"

        if self.data.get("current_goal") == goal["description"]:
            self.data["current_goal"] = None

        self.save()

        return f"Objetivo concluído: {goal['description']}"
