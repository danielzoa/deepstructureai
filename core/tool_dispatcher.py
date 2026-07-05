class ToolDispatcher:

    def decide(self, query):

        text = query.lower()

        if any(k in text for k in [
            "artigo",
            "paper",
            "arxiv",
            "publicação"
        ]):
            return "Arxiv"

        if any(k in text for k in [
            "calcular",
            "resolver",
            "integral",
            "equação",
            "simular",
            "python",
            "matriz"
        ]):
            return "Python"

        if any(k in text for k in [
            "github",
            "repositório",
            "código"
        ]):
            return "GitHub"

        return "Web"