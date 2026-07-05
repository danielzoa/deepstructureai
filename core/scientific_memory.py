import json
import os
from datetime import datetime


class ScientificMemory:
    def __init__(self, file="data/scientific_memory.json"):
        self.file = file
        self.data = self.load()
        self.normalize()
        self.save()

    def load(self):
        if not os.path.exists(self.file):
            return {
                "hypotheses": {},
                "experiments": {},
                "papers": {},
                "decisions": {},
                "open_questions": {}
            }

        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize(self):
        for key in ["hypotheses", "experiments", "papers", "decisions", "open_questions"]:
            if key not in self.data:
                self.data[key] = {}

            if isinstance(self.data[key], list):
                converted = {}
                for i, item in enumerate(self.data[key], start=1):
                    item_id = item.get("id", f"{key[:1].upper()}{i}")
                    converted[item_id] = item
                self.data[key] = converted

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def next_id(self, category, prefix):
        return f"{prefix}{len(self.data[category]) + 1}"

    def add_hypothesis(self, title, description, project="Geral", status="active"):
        hypothesis_id = self.next_id("hypotheses", "H")

        item = {
            "id": hypothesis_id,
            "title": title,
            "description": description,
            "project": project,
            "status": status,
            "confidence": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "evidence": [],
            "counterpoints": [],
            "related_papers": [],
            "experiments": [],
            "dependencies": [],
            "next_steps": [],
            "history": []
        }

        self.data["hypotheses"][hypothesis_id] = item
        self.save()

        return f"Hipótese registrada: {hypothesis_id} — {title}"

    def add_open_question(self, question, project="Geral"):
        question_id = self.next_id("open_questions", "Q")

        item = {
            "id": question_id,
            "question": question,
            "project": project,
            "status": "open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.data["open_questions"][question_id] = item
        self.save()

        return f"Questão aberta registrada: {question_id} — {question}"

    def add_experiment(self, title, result, project="Geral"):
        experiment_id = self.next_id("experiments", "E")

        item = {
            "id": experiment_id,
            "title": title,
            "project": project,
            "result": result,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.data["experiments"][experiment_id] = item
        self.save()

        return f"Experimento registrado: {experiment_id} — {title}"

    def add_decision(self, decision, reason, project="Geral"):
        decision_id = self.next_id("decisions", "D")

        item = {
            "id": decision_id,
            "decision": decision,
            "reason": reason,
            "project": project,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.data["decisions"][decision_id] = item
        self.save()

        return f"Decisão registrada: {decision_id} — {decision}"

    def recall(self, item_id):
        item_id = item_id.strip()

        for category in ["hypotheses", "experiments", "papers", "decisions", "open_questions"]:
            if item_id in self.data[category]:
                item = self.data[category][item_id]
                return json.dumps(item, indent=2, ensure_ascii=False)

        return f"Item não encontrado: {item_id}"

    def summary(self):
        return f"""
Scientific Memory

Hipóteses: {len(self.data['hypotheses'])}
Experimentos: {len(self.data['experiments'])}
Papers: {len(self.data['papers'])}
Decisões: {len(self.data['decisions'])}
Questões abertas: {len(self.data['open_questions'])}
"""

    def show_hypotheses(self):
        if not self.data["hypotheses"]:
            return "Nenhuma hipótese registrada."

        lines = []

        for h in self.data["hypotheses"].values():
            lines.append(
                f"{h['id']} | {h['status']} | {h['title']} | Projeto: {h['project']}"
            )

        return "\n".join(lines)