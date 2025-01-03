import logging
from logging import Logger
from pathlib import Path
from uuid import UUID

from reinforcement_learning import IPpoPoliciesPersistence
from validation.policies.lunar_lander_ppo_policy import LunarLanderPpoPolicy


class LunarLanderPpoPoliciesPersistence(IPpoPoliciesPersistence):
    _log: Logger = logging.getLogger(__name__)

    def __init__(self, ppo_policies_directory: Path = Path('./ppo-policies')) -> None:
        self._ppo_policies_directory = ppo_policies_directory
        self._ppo_policies_directory.mkdir(parents=True, exist_ok=True)

    def load_ppo_policy(self, ppo_policy_id: UUID) -> LunarLanderPpoPolicy:
        self._log.debug('Creating Lunar Lander PPO policy...')
        result: LunarLanderPpoPolicy = LunarLanderPpoPolicy()
        self._log.debug('Lunar Lander PPO policy created')
        return result

    def save_ppo_policy(self, ppo_policy: LunarLanderPpoPolicy) -> None:
        pass
