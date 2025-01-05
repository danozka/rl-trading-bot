from dataclasses import dataclass

from pandas import DataFrame

from reinforcement_learning import EnvironmentState


@dataclass
class TradingEnvironmentState(EnvironmentState):
    lower_interval_candlestick_data: DataFrame
    higher_interval_candlestick_data: DataFrame
    is_position_open: float
    open_position_gain_or_loss: float
    open_position_max_gain: float
    open_position_max_loss: float
    open_position_age: float
    market_volatility: float
    trend: float
    recent_win_ratio: float
    hour_of_day: float
