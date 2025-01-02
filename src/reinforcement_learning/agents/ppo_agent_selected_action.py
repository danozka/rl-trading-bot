from dataclasses import dataclass


@dataclass
class PpoAgentSelectedAction:
    action_id: int
    log_probability: float
