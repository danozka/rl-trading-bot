from dataclasses import dataclass


@dataclass
class EnvironmentState:
    reward: float
    done: bool
