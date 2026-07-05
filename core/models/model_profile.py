from dataclasses import dataclass


@dataclass
class ModelProfile:

    name: str

    reasoning: int = 5

    coding: int = 5

    writing: int = 5

    math: int = 5

    speed: int = 5

    context: int = 32000

    cost: str = "free"

    offline: bool = False

    available: bool = True