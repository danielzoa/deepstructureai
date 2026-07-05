import json
import os
from datetime import datetime
from core.config import JOURNAL_FILE


class ResearchJournal:
    def __init__(self, journal_file=JOURNAL_FILE):
        self.journal_file = journal_file
        self.entries = self.load()

    def load(self):
        if not os.path.exists(self.journal_file):
            return []

        with open(self.journal_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        with open(self.journal_file, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def add_entry(self, summary, project="Geral", next_steps=""):
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "project": project,
            "summary": summary,
            "next_steps": next_steps
        }

        self.entries.append(entry)
        self.save()

        return "Entrada adicionada ao diário de pesquisa."

    def show(self):
        return json.dumps(self.entries, indent=2, ensure_ascii=False)