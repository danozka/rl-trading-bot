from abc import ABC, abstractmethod

from reinforcement_learning.environments.environment_episode_summary import EnvironmentEpisodeSummary
from reinforcement_learning.environments.environment_state import EnvironmentState


class Environment(ABC):

    @abstractmethod
    def reset(self, max_time_steps: int) -> EnvironmentState:
        raise NotImplementedError

    @abstractmethod
    def make_step(self, agent_action_id: int) -> EnvironmentState:
        raise NotImplementedError

    @abstractmethod
    def get_episode_summary(self) -> EnvironmentEpisodeSummary:
        raise NotImplementedError
