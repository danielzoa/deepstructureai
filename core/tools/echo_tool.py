from .base_tool import BaseTool


class EchoTool(BaseTool):
    name = "Echo"

    def run(self, query):
        return f"[EchoTool] Recebi: {query}"