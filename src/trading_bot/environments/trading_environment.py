import random

from pandas import DataFrame, Timestamp
from ta.trend import ema_indicator
from ta.volatility import average_true_range

from reinforcement_learning import Environment
from trading_bot.agents.trading_agent_action import TradingAgentAction
from trading_bot.environments.trading_environment_episode_summary import TradingEnvironmentEpisodeSummary
from trading_bot.environments.trading_environment_state import TradingEnvironmentState


class TradingEnvironment(Environment):
    _columns_to_drop: list[str] = ['open_time', 'close_time', 'volume']
    _initial_balance: float = 1000.0
    _position_size: float = 100.0
    _trading_fee: float = 0.001
    _recent_profit_and_loss_memory: int = 5
    _lower_interval_candlestick_data: DataFrame
    _higher_interval_candlestick_data: DataFrame
    _lower_interval_lookback_candles: int
    _higher_interval_lookback_candles: int
    _higher_interval_close_time_column_loc: int
    _higher_interval_close_column_loc: int
    _higher_interval_high_column_loc: int
    _higher_interval_low_column_loc: int
    _min_lower_interval_index: int
    _current_lower_interval_index: int
    _current_lower_interval_candlestick_data: DataFrame
    _current_higher_interval_candlestick_data: DataFrame
    _open_position_lower_interval_index: int | None
    _current_balance: float
    _holdings: float
    _steps_without_action: int
    _profit_and_loss_history: list[bool]
    _profit: float
    _open_position_max_gain: float
    _open_position_max_loss: float
    _current_state: TradingEnvironmentState

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
        self._higher_interval_close_time_column_loc = self._higher_interval_candlestick_data.columns.get_loc(
            'close_time'
        )
        self._higher_interval_close_column_loc = self._higher_interval_candlestick_data.columns.get_loc('close')
        self._higher_interval_high_column_loc = self._higher_interval_candlestick_data.columns.get_loc('high')
        self._higher_interval_low_column_loc = self._higher_interval_candlestick_data.columns.get_loc('low')
        min_lower_interval_index: int = self._lower_interval_lookback_candles - 1
        min_higher_interval_index: int = self._higher_interval_lookback_candles - 1
        min_close_time: Timestamp = self._higher_interval_candlestick_data.iloc[
            min_higher_interval_index,
            self._higher_interval_close_time_column_loc
        ]
        min_lower_interval_index_imposed_by_higher_interval: int = self._lower_interval_candlestick_data[
            self._lower_interval_candlestick_data['close_time'] == min_close_time
        ].index.item()
        self._min_lower_interval_index = max(
            min_lower_interval_index,
            min_lower_interval_index_imposed_by_higher_interval
        )

    def reset(self, max_time_steps: int) -> TradingEnvironmentState:
        self._current_lower_interval_index = random.randint(
            a=self._min_lower_interval_index,
            b=(len(self._lower_interval_candlestick_data) - max_time_steps - 1)
        )
        self._update_candlestick_data()
        self._open_position_lower_interval_index = None
        self._current_balance = self._initial_balance
        self._holdings = 0.0
        self._steps_without_action = 0
        self._profit_and_loss_history = []
        self._profit = 0.0
        self._update_current_state()
        return self._current_state

    def make_step(self, agent_action_id: int) -> TradingEnvironmentState:
        reward: float = 0.0
        current_price: float = float(self._current_lower_interval_candlestick_data['close'].iloc[-1])
        agent_action: TradingAgentAction = TradingAgentAction(agent_action_id)
        if agent_action == TradingAgentAction.open_long_position:
            self._steps_without_action = 0
            if self._open_position_lower_interval_index is None:
                reward += 0.05  # Encourage exploration
                self._open_position_lower_interval_index = self._current_lower_interval_index
                self._current_balance -= self._position_size
                self._holdings = (self._position_size / current_price) * (1.0 - self._trading_fee)
            else:
                reward -= 0.2  # Discourage multiple open positions
        elif agent_action == TradingAgentAction.close_long_position:
            self._steps_without_action = 0
            if self._open_position_lower_interval_index is None:
                reward -= 0.1  # Penalize invalid action
            else:
                reward += 0.1  # Encourage closing positions
                position_profit_and_loss: float = (self._holdings * current_price) * (1.0 - self._trading_fee)
                step_profit_and_loss = position_profit_and_loss - self._position_size
                self._profit += step_profit_and_loss
                self._holdings = 0.0
                self._current_balance += position_profit_and_loss
                self._open_position_lower_interval_index = None
                # Reward/Penalize based on profit and volatility
                if step_profit_and_loss > 0:
                    # Sharpe-like adjustment
                    reward += (step_profit_and_loss / (1 + self._current_state.market_volatility)) * 2.0
                    self._profit_and_loss_history.append(True)
                else:
                    reward += step_profit_and_loss * 0.5
                    self._profit_and_loss_history.append(False)
        else:
            self._steps_without_action += 1
            reward -= 0.01 * self._steps_without_action  # Penalize inaction
        # Penalize holding positions too long
        if self._open_position_lower_interval_index is not None:
            position_age = self._current_lower_interval_index - self._open_position_lower_interval_index
            if position_age > 10:
                reward -= (position_age - 10) * 0.01
        self._current_lower_interval_index += 1
        self._update_candlestick_data()
        done: bool = self._open_position_lower_interval_index is None and self._current_balance <= 0.0
        self._update_current_state(reward, done)
        return self._current_state

    def get_episode_summary(self) -> TradingEnvironmentEpisodeSummary:
        return TradingEnvironmentEpisodeSummary(
            profit=round(number=self._profit, ndigits=2),
            closed_positions=len(self._profit_and_loss_history),
            win_ratio=round(number=(sum(self._profit_and_loss_history) / len(self._profit_and_loss_history)), ndigits=3)
        )

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

    def _update_current_state(self, reward: float = 0.0, done: bool = False) -> None:
        current_lower_interval_candlestick_data: DataFrame = self._current_lower_interval_candlestick_data.copy()
        current_higher_interval_candlestick_data: DataFrame = self._current_higher_interval_candlestick_data.copy()
        current_higher_interval_open_time: Timestamp = (
            current_higher_interval_candlestick_data['open_time'].iloc[-1]
        )
        current_higher_interval_close_time: Timestamp = (
            current_higher_interval_candlestick_data['close_time'].iloc[-1]
        )
        current_higher_interval_candlestick_data.iloc[-1, self._higher_interval_close_column_loc] = (
            current_lower_interval_candlestick_data['close'].iloc[-1]
        )
        current_higher_interval_candlestick_data.iloc[-1, self._higher_interval_high_column_loc] = (
            current_lower_interval_candlestick_data[
                (current_higher_interval_open_time <= current_lower_interval_candlestick_data['open_time']) &
                (current_lower_interval_candlestick_data['close_time'] <= current_higher_interval_close_time)
            ]['high'].max()
        )
        current_higher_interval_candlestick_data.iloc[-1, self._higher_interval_low_column_loc] = (
            current_lower_interval_candlestick_data[
                (current_higher_interval_open_time <= current_lower_interval_candlestick_data['open_time']) &
                (current_lower_interval_candlestick_data['close_time'] <= current_higher_interval_close_time)
            ]['low'].min()
        )
        current_lower_interval_candlestick_data.drop(columns=self._columns_to_drop, inplace=True)
        current_higher_interval_candlestick_data.drop(columns=self._columns_to_drop, inplace=True)
        max_high_price: float = float(current_higher_interval_candlestick_data['high'].max())
        min_low_price: float = float(current_higher_interval_candlestick_data['low'].min())
        delta_price: float = max_high_price - min_low_price
        current_lower_interval_candlestick_data_normalized: DataFrame = (
            (current_lower_interval_candlestick_data - min_low_price) / delta_price
        )
        current_higher_interval_candlestick_data_normalized: DataFrame = (
            (current_higher_interval_candlestick_data - min_low_price) / delta_price
        )
        is_position_open: bool
        open_position_gain_or_loss: float
        open_position_age: float
        if self._open_position_lower_interval_index is not None:
            is_position_open = True
            current_price: float = float(self._current_lower_interval_candlestick_data['close'].iloc[-1])
            open_position_price: float = float(
                self._lower_interval_candlestick_data['close'].iloc[self._open_position_lower_interval_index]
            )
            open_position_gain_or_loss = (current_price - open_position_price) / open_position_price
            if open_position_gain_or_loss >= 0.0:
                self._open_position_max_gain = max(self._open_position_max_gain, open_position_gain_or_loss)
            else:
                self._open_position_max_loss = min(self._open_position_max_loss, open_position_gain_or_loss)
            open_position_age = (
                (self._current_lower_interval_index - self._open_position_lower_interval_index) /
                self._lower_interval_lookback_candles
            )
        else:
            is_position_open = False
            open_position_gain_or_loss = 0.0
            self._open_position_max_gain = 0.0
            self._open_position_max_loss = 0.0
            open_position_age = 0.0
        self._current_state = TradingEnvironmentState(
            reward=reward,
            done=done,
            lower_interval_candlestick_data=current_lower_interval_candlestick_data_normalized,
            higher_interval_candlestick_data=current_higher_interval_candlestick_data_normalized,
            is_position_open=float(is_position_open),
            open_position_gain_or_loss=open_position_gain_or_loss,
            open_position_max_gain=self._open_position_max_gain,
            open_position_max_loss=self._open_position_max_loss,
            open_position_age=open_position_age,
            market_volatility=float(
                average_true_range(
                    high=current_lower_interval_candlestick_data_normalized['high'],
                    low=current_lower_interval_candlestick_data_normalized['low'],
                    close=current_lower_interval_candlestick_data_normalized['close']
                ).iloc[-1]
            ),
            trend=float(
                ema_indicator(
                    close=current_lower_interval_candlestick_data_normalized['close'],
                    window=20
                ).iloc[-1] -
                ema_indicator(
                    close=current_lower_interval_candlestick_data_normalized['close'],
                    window=50
                ).iloc[-1]
            ),
            recent_win_ratio=(
                sum(self._profit_and_loss_history[-self._recent_profit_and_loss_memory:]) /
                self._recent_profit_and_loss_memory
            ),
            hour_of_day=(self._current_higher_interval_candlestick_data['close_time'].iloc[-1].hour / 24.0)
        )
