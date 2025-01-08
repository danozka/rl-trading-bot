from dataclasses import dataclass

from reinforcement_learning.environments.environment_episode_summary import EnvironmentEpisodeSummary


@dataclass
class TradingEnvironmentEpisodeSummary(EnvironmentEpisodeSummary):
    profit: float
    win_ratio: float
    closed_positions: int
    forbidden_actions: int
    position_age_mean: float
    position_age_std: float
    reward_per_win_mean: float
    reward_per_win_std: float
    reward_per_loss_mean: float
    reward_per_loss_std: float
