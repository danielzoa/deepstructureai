import json
import os

from core.config import MEMORY_FILE


class MemoryManager:
    def __init__(self, memory_file=MEMORY_FILE):
        self.memory_file = memory_file
        self.memory = self.load()
        self.ensure_structure()

    def load(self):
        if not os.path.exists(self.memory_file):
            return {
                "owner": "Felipe Gaspar",
                "agent_name": "DeepStructureAI",
                "focus": [],
                "working_style": [],
                "current_project": "Geral",
                "projects": {
                    "Geral": {
                        "status": "Ativo",
                        "notes": []
                    }
                },
                "research_projects": []
            }

        with open(self.memory_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def ensure_structure(self):
        self.memory.setdefault("current_project", "Geral")
        self.memory.setdefault("projects", {})
        self.memory["projects"].setdefault("Geral", {
            "status": "Ativo",
            "notes": []
        })
        self.memory.setdefault("research_projects", [])
        self.save()

    def save(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def create_project(self, name):
        if name in self.memory["projects"]:
            return f"O projeto '{name}' já existe."

        self.memory["projects"][name] = {
            "status": "Ativo",
            "notes": []
        }
        self.save()
        return f"Projeto criado: {name}"

    def use_project(self, name):
        if name not in self.memory["projects"]:
            return f"Projeto não encontrado: {name}"

        self.memory["current_project"] = name
        self.save()
        return f"Projeto ativo agora: {name}"

    def list_projects(self):
        projects = self.memory.get("projects", {})
        current = self.memory.get("current_project", "Geral")

        lines = []
        for name in projects:
            marker = "*" if name == current else "-"
            lines.append(f"{marker} {name}")

        return "\n".join(lines)

    def current_project(self):
        return self.memory.get("current_project", "Geral")

    def remember(self, note):
        project = self.current_project()

        item = {
            "title": "Nota de pesquisa",
            "description": note,
            "status": "Em estudo"
        }

        self.memory["projects"][project].setdefault("notes", [])
        self.memory["projects"][project]["notes"].append(item)
        self.save()

        return f"Memória salva no projeto: {project}"

    def show(self):
        return json.dumps(self.memory, indent=2, ensure_ascii=False)