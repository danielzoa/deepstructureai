from pathlib import Path
from core.config import OBSIDIAN_VAULT_PATH


class ObsidianSync:
    def __init__(self, vault_path=OBSIDIAN_VAULT_PATH):
        self.vault_path = Path(vault_path)

    def read_note(self, title):
        title_lower = title.lower()

        for path in self.vault_path.rglob("*.md"):
            if path.stem.lower() == title_lower:
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    text = path.read_text(encoding="latin-1")

                return f"""
Nota:
{path.relative_to(self.vault_path)}

Conteúdo:

{text}
"""

        return f"Nota não encontrada: {title}"

    def search(self, query, limit=10):
        query_lower = query.lower()
        results = []

        for path in self.vault_path.rglob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="latin-1")

            if query_lower in text.lower() or query_lower in path.stem.lower():
                snippet_index = text.lower().find(query_lower)

                if snippet_index == -1:
                    snippet = text[:300]
                else:
                    start = max(0, snippet_index - 120)
                    end = min(len(text), snippet_index + 220)
                    snippet = text[start:end]

                results.append({
                    "title": path.stem,
                    "relative_path": str(path.relative_to(self.vault_path)),
                    "snippet": snippet.replace("\n", " ")
                })

        if not results:
            return "Nenhuma nota encontrada."

        lines = [f"Resultados para: {query}"]

        for item in results[:limit]:
            lines.append(
                f"\n- {item['relative_path']}\n  {item['snippet']}"
            )

        return "\n".join(lines)
    
    [
    {
        "title": "Hipótese H1",
        "path": "NTG/Hipótese H1.md",
        "snippet": "A pressão anisotrópica...",
        "score": 98
    },

    {
        "title": "Pressão",
        "path": "Conceitos/Pressão.md",
        "snippet": "Define-se pressão...",
        "score": 91
    }
]

    def list_notes(self):
        if not self.vault_path.exists():
            return []

        notes = []

        for path in self.vault_path.rglob("*.md"):
            notes.append({
                "title": path.stem,
                "path": str(path),
                "relative_path": str(path.relative_to(self.vault_path))
            })

        return notes

    def summary(self):
        notes = self.list_notes()

        if not notes:
            return "Nenhuma nota encontrada ou Vault inexistente."

        lines = [f"Notas encontradas: {len(notes)}"]

        for note in notes[:20]:
            lines.append(f"- {note['relative_path']}")

        if len(notes) > 20:
            lines.append(f"... e mais {len(notes) - 20} nota(s).")

        return "\n".join(lines)