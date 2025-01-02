import random

from pandas import DataFrame, Timestamp

from reinforcement_learning import Environment
from trading_bot.agents.trading_agent_action import TradingAgentAction
from trading_bot.environments.trading_environment_state import TradingEnvironmentState


class TradingEnvironment(Environment):
    _columns_to_drop: list[str] = ['open_time', 'close_time', 'volume']
    _initial_balance: float = 1000.0
    _position_size: float = 100.0
    _trading_fee: float = 0.001
    _lower_interval_candlestick_data: DataFrame
    _higher_interval_candlestick_data: DataFrame
    _lower_interval_lookback_candles: int
    _higher_interval_lookback_candles: int
    _current_lower_interval_index: int
    _current_lower_interval_candlestick_data: DataFrame
    _current_higher_interval_candlestick_data: DataFrame
    _open_position_lower_interval_index: int | None
    _current_balance: float
    _holdings: float

    def __init__(
        self,
        lower_interval_candlestick_data: DataFrame,
        higher_interval_candlestick_data: DataFrame,
        lower_interval_lookback_candles: int,
        higher_interval_lookback_candles: int
    ) -> None:
        self._lower_interval_candlestick_data = lower_interval_candlestick_data
        self._higher_interval_candlestick_data = higher_interval_candlestick_data
        self._lower_interval_lookback_candles = lower_interval_lookback_candles
        self._higher_interval_lookback_candles = higher_interval_lookback_candles

    def reset(self, max_time_steps: int) -> TradingEnvironmentState:
        self._current_lower_interval_index = random.randint(
            a=(self._lower_interval_lookback_candles - 1),
            b=(len(self._lower_interval_candlestick_data) - max_time_steps - 1)
        )
        self._update_candlestick_data()
        self._open_position_lower_interval_index = None
        self._current_balance = self._initial_balance
        self._holdings = 0.0
        return self._get_current_state()

    def make_step(self, agent_action_id: int) -> TradingEnvironmentState:
        close_column_loc: int = self._lower_interval_candlestick_data.columns.get_loc('close')
        reward: float = 0.0
        agent_action: TradingAgentAction = TradingAgentAction(agent_action_id)
        if agent_action == TradingAgentAction.open_position:
            if self._open_position_lower_interval_index is None:
                self._open_position_lower_interval_index = self._current_lower_interval_index
        elif agent_action == TradingAgentAction.close_position:
            self._open_position_lower_interval_index = None
        else:
            pass
        self._current_lower_interval_index += 1
        self._update_candlestick_data()
        done: bool = self._open_position_lower_interval_index is None and self._current_balance <= 0.0
        return self._get_current_state(reward, done)

    def _update_candlestick_data(self) -> None:
        self._current_lower_interval_candlestick_data = self._lower_interval_candlestick_data[
            (self._current_lower_interval_index + 1 - self._lower_interval_lookback_candles):
            (self._current_lower_interval_index + 1)
        ]
        current_lower_interval_close_time: Timestamp = (
            self._current_lower_interval_candlestick_data['close_time'].iloc[-1]
        )
        current_higher_interval_index: int = self._higher_interval_candlestick_data[
            (self._higher_interval_candlestick_data['open_time'] < current_lower_interval_close_time) &
            (current_lower_interval_close_time <= self._higher_interval_candlestick_data['close_time'])
            ].index.item()
        self._current_higher_interval_candlestick_data = self._higher_interval_candlestick_data[
            (current_higher_interval_index + 1 - self._higher_interval_lookback_candles):
            (current_higher_interval_index + 1)
        ]

    def _get_current_state(self, reward: float = 0.0, done: bool = False) -> TradingEnvironmentState:
        current_lower_interval_candlestick_data: DataFrame = self._current_lower_interval_candlestick_data.copy()
        current_higher_interval_candlestick_data: DataFrame = self._current_higher_interval_candlestick_data.copy()
        current_higher_interval_open_time: Timestamp = (
            current_higher_interval_candlestick_data['open_time'].iloc[-1]
        )
        current_higher_interval_close_time: Timestamp = (
            current_higher_interval_candlestick_data['close_time'].iloc[-1]
        )
        close_column_loc: int = current_higher_interval_candlestick_data.columns.get_loc('close')
        high_column_loc: int = current_higher_interval_candlestick_data.columns.get_loc('high')
        low_column_loc: int = current_higher_interval_candlestick_data.columns.get_loc('low')
        current_higher_interval_candlestick_data.iloc[-1, close_column_loc] = (
            current_lower_interval_candlestick_data['close'].iloc[-1]
        )
        current_higher_interval_candlestick_data.iloc[-1, high_column_loc] = (
            current_lower_interval_candlestick_data[
                (current_higher_interval_open_time <= current_lower_interval_candlestick_data['open_time']) &
                (current_lower_interval_candlestick_data['close_time'] <= current_higher_interval_close_time)
            ]['high'].max()
        )
        current_higher_interval_candlestick_data.iloc[-1, low_column_loc] = (
            current_lower_interval_candlestick_data[
                (current_higher_interval_open_time <= current_lower_interval_candlestick_data['open_time']) &
                (current_lower_interval_candlestick_data['close_time'] <= current_higher_interval_close_time)
            ]['low'].min()
        )
        current_lower_interval_candlestick_data.drop(columns=self._columns_to_drop, inplace=True)
        current_higher_interval_candlestick_data.drop(columns=self._columns_to_drop, inplace=True)
        is_position_open: bool
        open_position_gain_or_loss: float
        open_position_age: float
        if self._open_position_lower_interval_index is not None:
            is_position_open = True
            current_price: float = current_lower_interval_candlestick_data['close'].iloc[-1]
            open_position_price: float = self._lower_interval_candlestick_data['close'].iloc[
                self._open_position_lower_interval_index
            ]
            open_position_gain_or_loss = (current_price - open_position_price) / open_position_price
            open_position_age = (
                (self._current_lower_interval_index - self._open_position_lower_interval_index) /
                self._lower_interval_lookback_candles
            )
        else:
            is_position_open = False
            open_position_gain_or_loss = 0.0
            open_position_age = 0.0
        max_high_price: float = float(current_higher_interval_candlestick_data['high'].max())
        min_low_price: float = float(current_higher_interval_candlestick_data['low'].min())
        delta_price: float = max_high_price - min_low_price
        current_lower_interval_candlestick_data_normalized: DataFrame = (
            (current_lower_interval_candlestick_data - min_low_price) / delta_price
        )
        current_higher_interval_candlestick_data_normalized: DataFrame = (
            (current_higher_interval_candlestick_data - min_low_price) / delta_price
        )
        return TradingEnvironmentState(
            reward=reward,
            done=done,
            lower_interval_candlestick_data=current_lower_interval_candlestick_data_normalized,
            higher_interval_candlestick_data=current_higher_interval_candlestick_data_normalized,
            is_position_open=is_position_open,
            open_position_gain_or_loss=open_position_gain_or_loss,
            open_position_age=open_position_age
        )
