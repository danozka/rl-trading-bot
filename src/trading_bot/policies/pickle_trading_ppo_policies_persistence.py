import logging
import pickle
from logging import Logger
from pathlib import Path
from uuid import UUID

from reinforcement_learning import IPpoPoliciesPersistence
from trading_bot.policies.trading_ppo_policy import TradingPpoPolicy


class PickleTradingPpoPoliciesPersistence(IPpoPoliciesPersistence):
    _log: Logger = logging.getLogger(__name__)
    _filename_template: str = 'ppo-policy-{ppo_policy_id}.pkl'
    _ppo_policies_directory: Path

    def __init__(self, ppo_policies_directory: Path = Path('./ppo-policies')) -> None:
        self._ppo_policies_directory = ppo_policies_directory
        self._ppo_policies_directory.mkdir(parents=True, exist_ok=True)

    def load_ppo_policy(self, ppo_policy_id: UUID) -> TradingPpoPolicy:
        self._log.debug(f'Loading trading PPO policy with ID \'{ppo_policy_id}\'...')
        ppo_policy_file_path: Path = self._ppo_policies_directory.joinpath(
            self._filename_template.format(ppo_policy_id=ppo_policy_id)
        )
        if ppo_policy_file_path.exists():
            with open(file=ppo_policy_file_path, mode='rb') as file:
                result: TradingPpoPolicy = pickle.load(file)
                self._log.debug(f'Trading PPO policy with ID \'{ppo_policy_id}\' loaded')
                return result
        else:
            self._log.debug(f'Trading PPO policy with ID \'{ppo_policy_id}\' not found. Creating new instance...')
            return TradingPpoPolicy()

    def save_ppo_policy(self, ppo_policy: TradingPpoPolicy) -> None:
        pass
