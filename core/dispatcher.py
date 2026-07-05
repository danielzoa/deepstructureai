class Dispatcher:
    def decide_next(self, context):
        text = context.question.lower()

        if any(k in text for k in ["código", "python", "simular", "calcular", "executar"]):
            return "Executor"

        if any(k in text for k in ["hipótese", "ideia", "explorar", "alternativa"]):
            return "Researcher"

        if any(k in text for k in ["falha", "refutar", "contraexemplo", "criticar"]):
            return "Critic"

        if any(k in text for k in ["relatório", "resumo", "escrever", "documentar"]):
            return "Writer"

        if any(k in text for k in ["revisar", "avaliar", "conferir"]):
            return "Reviewer"

        if any(k in text for k in ["plano", "próximo passo", "continuar", "estratégia"]):
            return "Planner"

        return "Planner"