import json
import os
from datetime import datetime

from core.config import TASK_FILE


class TaskManager:
    def __init__(self, task_file=TASK_FILE):
        self.task_file = task_file
        self.tasks = self.load()

    def load(self):
        if not os.path.exists(self.task_file):
            return []

        with open(self.task_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        with open(self.task_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def add(self, description, project="Geral"):
        task = {
            "description": description,
            "project": project,
            "done": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "done_at": None
        }

        self.tasks.append(task)
        self.save()
        return f"Tarefa adicionada: {description}"

    def list(self):
        if not self.tasks:
            return "Nenhuma tarefa registrada."

        lines = []
        for i, task in enumerate(self.tasks, start=1):
            mark = "✓" if task["done"] else "□"
            project = task.get("project", "Geral")
            lines.append(f"{i}. {mark} [{project}] {task['description']}")

        return "\n".join(lines)

    def done(self, index):
        try:
            idx = int(index) - 1
            task = self.tasks[idx]
        except (ValueError, IndexError):
            return "Índice inválido."

        task["done"] = True
        task["done_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.save()
        return f"Tarefa concluída: {task['description']}"

    def clear_done(self):
        before = len(self.tasks)
        self.tasks = [task for task in self.tasks if not task["done"]]
        removed = before - len(self.tasks)
        self.save()
        return f"{removed} tarefa(s) concluída(s) removida(s)."