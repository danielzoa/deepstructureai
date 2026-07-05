import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from core.config import ROOT_DIR


class SecurityViolation(ValueError):
    pass


class PublicContentPolicy:
    """Policy for content crossing the public Moltbook boundary."""

    SECRET_PATTERNS = (
        re.compile(r"(?i)(api[_ -]?key|token|password|senha)\s*[:=]\s*\S+"),
        re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    )
    PRIVATE_PATTERNS = (
        re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
        re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    )
    INJECTION_PATTERNS = (
        re.compile(r"(?i)ignore (?:all |any )?(?:previous|prior) instructions"),
        re.compile(r"(?i)reveal (?:your |the )?(?:system prompt|secrets?|tokens?)"),
        re.compile(r"(?i)(?:execute|run) (?:this )?(?:command|code|script)"),
    )

    def validate_outbound(self, content):
        text = content.strip()
        if not text:
            raise SecurityViolation("Conteúdo público vazio.")
        if len(text) > 4000:
            raise SecurityViolation("Conteúdo público excede 4.000 caracteres.")
        for pattern in (*self.SECRET_PATTERNS, *self.PRIVATE_PATTERNS):
            if pattern.search(text):
                raise SecurityViolation(
                    "Conteúdo bloqueado: possível segredo ou dado pessoal."
                )
        return text

    def inspect_inbound(self, content):
        warnings = [
            pattern.pattern
            for pattern in self.INJECTION_PATTERNS
            if pattern.search(content)
        ]
        return {
            "trusted": False,
            "allow_code_execution": False,
            "allow_private_context": False,
            "prompt_injection_suspected": bool(warnings),
            "matches": warnings,
        }


class MoltbookGateway:
    """Human-approved boundary. Network publishing is disabled by default."""

    def __init__(
        self,
        client=None,
        dry_run=True,
        pending_file=None,
        audit_file=None,
        policy=None,
    ):
        self.client = client
        self.dry_run = dry_run
        self.pending_file = Path(
            pending_file or ROOT_DIR / "data" / "moltbook_pending.json"
        )
        self.audit_file = Path(
            audit_file or ROOT_DIR / "logs" / "moltbook_audit.jsonl"
        )
        self.policy = policy or PublicContentPolicy()

    def _load(self):
        if not self.pending_file.exists():
            return []
        with self.pending_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, actions):
        self.pending_file.parent.mkdir(parents=True, exist_ok=True)
        with self.pending_file.open("w", encoding="utf-8") as file:
            json.dump(actions, file, indent=2, ensure_ascii=False)

    def _audit(self, event, action):
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "action_id": action["id"],
            "status": action["status"],
        }
        with self.audit_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def propose_post(self, content):
        content = self.policy.validate_outbound(content)
        action = {
            "id": uuid4().hex[:10],
            "type": "post",
            "content": content,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "contains_private_context": False,
            "code_execution_allowed": False,
        }
        actions = self._load()
        actions.append(action)
        self._save(actions)
        self._audit("proposed", action)
        return action

    def pending(self):
        return [action for action in self._load() if action["status"] == "pending"]

    def approve(self, action_id):
        actions = self._load()
        action = next((item for item in actions if item["id"] == action_id), None)
        if action is None:
            raise KeyError(f"Ação não encontrada: {action_id}")
        if action["status"] != "pending":
            raise ValueError(f"Ação já processada: {action['status']}")

        if self.dry_run:
            action["status"] = "approved_dry_run"
            result = {
                "published": False,
                "reason": "dry-run: nenhuma chamada de rede realizada",
            }
        else:
            if self.client is None:
                raise RuntimeError("Cliente Moltbook não configurado.")
            result = self.client.publish_post(action["content"])
            action["status"] = "published"

        action["processed_at"] = datetime.now(timezone.utc).isoformat()
        self._save(actions)
        self._audit("approved", action)
        return {"action": action, "result": result}
