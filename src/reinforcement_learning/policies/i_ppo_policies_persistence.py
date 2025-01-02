from abc import ABC, abstractmethod
from uuid import UUID

from reinforcement_learning.policies.ppo_policy import PpoPolicy


class IPpoPoliciesPersistence(ABC):

    @abstractmethod
    def load_ppo_policy(self, ppo_policy_id: UUID) -> PpoPolicy:
        raise NotImplementedError

    @abstractmethod
    def save_ppo_policy(self, ppo_policy: PpoPolicy) -> None:
        raise NotImplementedError
