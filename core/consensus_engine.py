class ConsensusEngine:
    def __init__(self, llm, team, agent_planner=None):
        self.llm = llm
        self.team = team
        self.agent_planner = agent_planner

    def ask_role(self, role_name, question, system_prompt):
        model_name = self.team.model_for(role_name)

        if not model_name:
            print("[DEBUG] role_name:", role_name)
            print("[DEBUG] roles disponíveis:", self.team.roles.keys())
            raise ValueError(f"Papel não encontrado: {role_name}")

        response = self.llm.ask_model(
            model_name=model_name,
            system_prompt=system_prompt,
            user_prompt=question,
            fallback="ollama"
        )

        return {
            "role": role_name,
            "model": model_name,
            "response": response
        }

    def system_prompt_for(self, role_name):
        goals = {
            "coordinator": "Você é o coordenador científico. Organize a estratégia geral da análise.",
            "mathematician": "Você é o matemático da equipe. Verifique rigor, hipóteses, lacunas e estrutura lógica.",
            "physicist": "Você é o físico da equipe. Analise plausibilidade física, interpretação e mecanismos.",
            "programmer": "Você é o programador científico. Proponha implementação, testes e riscos técnicos.",
            "paper_analyst": "Você é o analista de artigos. Relacione a questão com literatura, resultados e limitações.",
            "reviewer": "Você é o revisor crítico. Procure falhas, circularidades, riscos e contraexemplos.",
            "explainer": "Você é o explicador. Reescreva a ideia de modo claro, intuitivo e didático."
        }

        return goals.get(role_name, "Você é um especialista científico. Analise a questão.")

    def discuss(self, question):
        if self.agent_planner:
            plan = self.agent_planner.plan(question)
            selected_roles = plan["team"]
        else:
            plan = {
                "category": "default",
                "team": ["coordinator", "reviewer"],
                "reason": "Sem AgentPlanner."
            }
            selected_roles = plan["team"]

        participants = []

        for role in selected_roles:
            participants.append(
                self.ask_role(
                    role,
                    question,
                    self.system_prompt_for(role)
                )
            )

        combined = "\n\n".join(
            f"=== {p['role']} ({p['model']}) ===\n{p['response']}"
            for p in participants
        )

        synthesis = self.ask_role(
            "coordinator",
            f"""
Pergunta original:
{question}

Plano de equipe:
{plan}

Respostas dos especialistas:
{combined}
""",
            """
Você é o sintetizador científico.

Produza:
- síntese final;
- especialistas consultados;
- concordâncias;
- divergências;
- riscos principais;
- próximos passos objetivos.
"""
        )

        return {
            "question": question,
            "plan": plan,
            "participants": participants,
            "synthesis": synthesis
        }