import json
import os
from pathlib import Path

from core.research_session import ResearchSession


class ResearchSessionManager:
    def __init__(self, base_dir="data/sessions"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.active_file = self.base_dir / "active_session.json"
        self.active_session = self.load_active()

    def next_id(self):
        existing = list(self.base_dir.glob("session_*.json"))
        numbers = []

        for file in existing:
            try:
                number = int(file.stem.replace("session_", ""))
                numbers.append(number)
            except ValueError:
                pass

        next_number = max(numbers, default=0) + 1
        return f"session_{next_number:04d}"

    def session_path(self, session_id):
        return self.base_dir / f"{session_id}.json"

    def start(self, title, project, objective, team=None):
        session_id = self.next_id()

        session = ResearchSession(
            session_id=session_id,
            title=title,
            project=project,
            objective=objective,
            team=team or {},
        )

        session.add_event(
            "session_started",
            f"Sessão iniciada: {title}"
        )

        self.active_session = session
        self.save(session)
        self.save_active()

        return session

    def save(self, session):
        path = self.session_path(session.id)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                session.to_dict(),
                f,
                indent=2,
                ensure_ascii=False
            )

    def load(self, session_id):
        path = self.session_path(session_id)

        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ResearchSession.from_dict(data)

    def save_active(self):
        if not self.active_session:
            if self.active_file.exists():
                self.active_file.unlink()
            return

        with open(self.active_file, "w", encoding="utf-8") as f:
            json.dump(
                {"active_session_id": self.active_session.id},
                f,
                indent=2,
                ensure_ascii=False
            )

    def load_active(self):
        if not self.active_file.exists():
            return None

        with open(self.active_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        session_id = data.get("active_session_id")

        if not session_id:
            return None

        return self.load(session_id)

    def add_event(self, event_type, content):
        if not self.active_session:
            return None

        event = self.active_session.add_event(event_type, content)
        self.save(self.active_session)

        return event

    def finish(self):
        if not self.active_session:
            return None

        self.active_session.add_event(
            "session_finished",
            "Sessão encerrada."
        )

        self.active_session.finish()
        finished = self.active_session

        self.save(finished)

        self.active_session = None
        self.save_active()

        return finished

    def status(self):
        if not self.active_session:
            return "Nenhuma sessão ativa."

        s = self.active_session

        return f"""
Research Session

ID: {s.id}
Título: {s.title}
Projeto: {s.project}
Objetivo: {s.objective}
Status: {s.status}
Início: {s.started_at}
Eventos: {len(s.events)}
"""

    def events(self):
        if not self.active_session:
            return "Nenhuma sessão ativa."

        if not self.active_session.events:
            return "Nenhum evento registrado."

        lines = [f"Eventos da sessão {self.active_session.id}:"]

        for event in self.active_session.events:
            lines.append(
                f"- [{event['time']}] {event['type']}: {event['content']}"
            )

        return "\n".join(lines)