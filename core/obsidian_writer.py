from pathlib import Path
from datetime import datetime
from core.config import OBSIDIAN_VAULT_PATH


class ObsidianWriter:
    def __init__(self, vault_path=OBSIDIAN_VAULT_PATH):
        self.vault = Path(vault_path)

    def save_lab_session(self, session):
        diary = self.vault / "01 Diário"
        diary.mkdir(parents=True, exist_ok=True)

        filename = datetime.now().strftime("%Y-%m-%d") + ".md"
        file = diary / filename

        text = f"""

# Sessão de Pesquisa

## Projeto

{session["project"]}

## Início

{session["started_at"]}

## Fim

{session["ended_at"]}

## Notas
"""

        for note in session["notes"]:
            text += f"""

### {note["time"]}

{note["text"]}
"""

        text += """

## Próximos passos

- [ ] Continuar investigação.
"""

        with open(file, "a", encoding="utf-8") as f:
            f.write(text)

        return str(file)