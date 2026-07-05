from pathlib import Path

from core.config import ROOT_DIR


class Executor:
    """Stores generated code, but never executes it unless explicitly enabled."""

    def __init__(self, allow_execution=False, sandbox_dir=None):
        self.allow_execution = allow_execution
        self.sandbox_dir = Path(sandbox_dir or ROOT_DIR / "sandbox").resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, filename):
        path = (self.sandbox_dir / Path(filename).name).resolve()
        if path.parent != self.sandbox_dir:
            raise ValueError("Arquivo precisa permanecer no diretório sandbox.")
        if path.suffix.casefold() != ".py":
            raise ValueError("Somente arquivos .py são permitidos.")
        return path

    def run_python_code(self, code):
        return (
            "Execução arbitrária desativada por segurança. "
            "O código pode ser salvo para revisão humana."
        )

    def run_python_file(self, filename):
        path = self._safe_path(filename)
        if not path.exists():
            return f"Arquivo não encontrado no sandbox: {path.name}"
        if not self.allow_execution:
            return (
                "Execução desativada por segurança. Revise o arquivo em "
                f"{path} antes de executá-lo manualmente."
            )
        return (
            "Execução automática não implementada: habilitar a flag não substitui "
            "um sandbox real de sistema operacional."
        )

    def save_generated_code(self, code, filename="generated_code.py"):
        path = self._safe_path(filename)
        path.write_text(code, encoding="utf-8")
        return f"Código salvo em {path}. Revise antes de executar."
