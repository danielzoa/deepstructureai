class WorkflowDispatcher:

    def decide(self, context):

        text = context.question.lower()

        if any(k in text for k in [
            "navier",
            "pesquisa",
            "hipótese",
            "prova",
            "teorema",
            "riemann"
        ]):
            return "research"

        if any(k in text for k in [
            "python",
            "programar",
            "código",
            "script"
        ]):
            return "coding"

        if any(k in text for k in [
            "artigo",
            "latex",
            "paper",
            "escreva"
        ]):
            return "writing"

        return "research"