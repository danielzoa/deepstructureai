import json
from pathlib import Path

from core.config import PROFILE_DIR


class ProfileKnowledge:
    """User-curated context that is kept separate from research memory."""

    ALLOWED_FILES = ("identity.json", "preferences.json", "boundaries.json")

    def __init__(self, base_path=PROFILE_DIR):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load(self):
        profile = {}
        for filename in self.ALLOWED_FILES:
            path = self.base_path / filename
            if path.exists():
                with path.open("r", encoding="utf-8") as file:
                    profile[path.stem] = json.load(file)
        return profile

    def as_text(self):
        return json.dumps(self.load(), indent=2, ensure_ascii=False)

    def prompt_context(self):
        profile = self.load()
        boundaries = profile.get("boundaries", {})
        if not boundaries.get("use_in_prompts", True):
            return "Perfil pessoal desativado para prompts."

        safe_profile = {
            "identity": profile.get("identity", {}),
            "preferences": profile.get("preferences", {}),
        }
        return json.dumps(safe_profile, indent=2, ensure_ascii=False)
