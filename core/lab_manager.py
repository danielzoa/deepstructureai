import json
import os
from datetime import datetime


class LabManager:

    def __init__(self, file="data/lab_session.json"):
        self.file = file
        self.active = False
        self.session = None

    def start(self, project):

        self.active = True

        self.session = {
            "project": project,
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ended_at": "",
            "notes": []
        }

        self.save()

        return f"Sessão de laboratório iniciada: {project}"

    def note(self, text):

        if not self.active or self.session is None:
            return "Nenhuma sessão de laboratório ativa."

        self.session["notes"].append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "text": text
            }
        )

        self.save()

        return "Nota registrada."

    def end(self):

        if not self.active or self.session is None:
            return "Nenhuma sessão de laboratório ativa.", None

        self.session["ended_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        notes = self.session.get("notes", [])

        summary = "\n".join(
            f"- [{note['time']}] {note['text']}"
            for note in notes
        )

        result = f"""
==========================
Sessão encerrada
==========================

Projeto:
{self.session['project']}

Início:
{self.session['started_at']}

Fim:
{self.session['ended_at']}

Quantidade de notas:
{len(notes)}

Notas:

{summary}
"""

        finished_session = dict(self.session)

        self.active = False

        self.save()

        return result, finished_session

    def save(self):

        os.makedirs("data", exist_ok=True)

        with open(self.file, "w", encoding="utf-8") as f:

            json.dump(
                {
                    "active": self.active,
                    "session": self.session
                },
                f,
                indent=2,
                ensure_ascii=False
            )

    def load(self):

        if not os.path.exists(self.file):
            return

        with open(self.file, "r", encoding="utf-8") as f:

            data = json.load(f)

        self.active = data.get("active", False)
        self.session = data.get("session")

    def is_active(self):

        return self.active

    def get_session(self):

        return self.session