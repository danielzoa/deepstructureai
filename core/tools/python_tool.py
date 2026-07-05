import sympy as sp
from core.tools.base_tool import BaseTool


class PythonTool(BaseTool):
    name = "Python"

    def run(self, query):
        x = sp.Symbol("x")

        try:
            if "integral" in query.lower():
                expr_text = query.lower().replace("integral", "").strip()
                expr = sp.sympify(expr_text)
                return str(sp.integrate(expr, x))

            if "derivada" in query.lower():
                expr_text = query.lower().replace("derivada", "").strip()
                expr = sp.sympify(expr_text)
                return str(sp.diff(expr, x))

            return "PythonTool básico ativo. Use: 'integral x**2' ou 'derivada sin(x)'."

        except Exception as e:
            return f"Erro no PythonTool: {e}"