class BaseModel:
    name = "base"

    def generate(self, system_prompt, user_prompt):
        raise NotImplementedError("Modelos precisam implementar generate().")