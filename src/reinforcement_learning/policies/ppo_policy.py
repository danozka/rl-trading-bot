from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from torch import device
from torch.nn import Module

from reinforcement_learning.environments.environment_state import EnvironmentState
from reinforcement_learning.policies.ppo_policy_output import PpoPolicyOutput


class PpoPolicy(Module, ABC):
    id: UUID

    def __init__(self, id_: UUID = uuid4()) -> None:
        super().__init__()
        self.id = id_

    @abstractmethod
    def forward(self, environment_states: list[EnvironmentState]) -> PpoPolicyOutput:
        raise NotImplementedError

    @abstractmethod
    def get_device(self) -> device:
        raise NotImplementedError
