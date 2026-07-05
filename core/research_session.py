import json
import os
from datetime import datetime


class ResearchSession:
    def __init__(
        self,
        session_id,
        title,
        project,
        objective,
        team=None,
        status="running",
        started_at=None,
        finished_at=None,
        events=None,
    ):
        self.id = session_id
        self.title = title
        self.project = project
        self.objective = objective
        self.team = team or {}
        self.status = status
        self.started_at = started_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.finished_at = finished_at
        self.events = events or []

    def add_event(self, event_type, content):
        event = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": event_type,
            "content": content,
        }

        self.events.append(event)

        return event

    def finish(self):
        self.status = "finished"
        self.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "project": self.project,
            "objective": self.objective,
            "team": self.team,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "events": self.events,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            session_id=data["id"],
            title=data["title"],
            project=data["project"],
            objective=data["objective"],
            team=data.get("team", {}),
            status=data.get("status", "running"),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            events=data.get("events", []),
        )