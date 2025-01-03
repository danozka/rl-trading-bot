import logging
from logging import Logger
from uuid import uuid4

from dependency_injector.wiring import inject, Provide

from reinforcement_learning import IPpoPoliciesPersistence, PpoAgentTrainer
from validation.environments.lunar_lander_environment import LunarLanderEnvironment


class LunarLanderPpoAgentTrainer:
    _log: Logger = logging.getLogger(__name__)
    _ppo_policies_persistence: IPpoPoliciesPersistence

    @inject
    def __init__(self, ppo_policies_persistence: IPpoPoliciesPersistence = Provide['ppo_policies_persistence']) -> None:
        self._ppo_policies_persistence = ppo_policies_persistence

    def train_lunar_lander_ppo_agent(self, episodes: int, max_time_steps: int) -> None:
        self._log.info('Training Lunar Lander PPO agent...')
        PpoAgentTrainer(
            environment=LunarLanderEnvironment(),
            ppo_policies_persistence=self._ppo_policies_persistence,
            episodes=episodes,
            max_time_steps=max_time_steps
        ).train_ppo_agent(uuid4())
        self._log.info('Lunar Lander PPO agent training completed')
