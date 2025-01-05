from dataclasses import dataclass

from reinforcement_learning.environments.environment_episode_summary import EnvironmentEpisodeSummary


@dataclass
class TradingEnvironmentEpisodeSummary(EnvironmentEpisodeSummary):
    profit: float
    mean_position_age: float
    mean_reward_per_win: float
    mean_reward_per_loss: float
    closed_positions: int
    win_ratio: float
