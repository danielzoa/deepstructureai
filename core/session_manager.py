import json
import os


class SessionManager:

    def __init__(self):
        self.file = "data/last_session.json"

    def save(self, context):

        os.makedirs("data", exist_ok=True)

        data = {
            "project": context.project,
            "goal": context.goal,
            "question": context.question,
            "plan": context.plan,
            "criticisms": context.criticisms,
            "hypotheses": context.hypotheses,
            "obsidian_notes": context.obsidian_notes,
            "answer": context.answer
        }

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

    def load(self):

        if not os.path.exists(self.file):
            return None

        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)