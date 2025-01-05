from dataclasses import dataclass

from reinforcement_learning.environments.environment_episode_summary import EnvironmentEpisodeSummary


@dataclass
class TradingEnvironmentEpisodeSummary(EnvironmentEpisodeSummary):
    final_balance: float
    closed_positions: int
    win_ratio: float
