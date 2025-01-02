import logging
from logging import Logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from reinforcement_learning import IPpoPoliciesPersistence, PpoAgentTrainer
from trading_bot.candlestick.candlestick_data_interval import CandlestickDataInterval
from trading_bot.candlestick.i_candlestick_data_persistence import ICandlestickDataPersistence
from trading_bot.environments.trading_environment import TradingEnvironment


class TradingPpoAgentTrainer:
    _log: Logger = logging.getLogger(__name__)
    _ppo_policies_persistence: IPpoPoliciesPersistence
    _candlestick_data_persistence: ICandlestickDataPersistence

    @inject
    def __init__(
        self,
        ppo_policies_persistence: IPpoPoliciesPersistence = Provide['ppo_policies_persistence'],
        candlestick_data_persistence: ICandlestickDataPersistence = Provide['candlestick_data_persistence']
    ) -> None:
        self._ppo_policies_persistence = ppo_policies_persistence
        self._candlestick_data_persistence = candlestick_data_persistence

    def train_trading_ppo_agent(
        self,
        ppo_policy_id: UUID,
        base_asset: str,
        quote_asset: str,
        lower_interval: CandlestickDataInterval,
        higher_interval: CandlestickDataInterval,
        lower_interval_lookback_candles: int,
        higher_interval_lookback_candles: int,
        episodes: int,
        max_time_steps: int
    ) -> None:
        self._log.info(f'Training trading PPO agent with policy ID \'{ppo_policy_id}\'...')
        PpoAgentTrainer(
            environment=TradingEnvironment(
                lower_interval_candlestick_data=self._candlestick_data_persistence.load_symbol_candlestick_data(
                    base_asset=base_asset,
                    quote_asset=quote_asset,
                    interval=lower_interval
                ),
                higher_interval_candlestick_data=self._candlestick_data_persistence.load_symbol_candlestick_data(
                    base_asset=base_asset,
                    quote_asset=quote_asset,
                    interval=higher_interval
                ),
                lower_interval_lookback_candles=lower_interval_lookback_candles,
                higher_interval_lookback_candles=higher_interval_lookback_candles
            ),
            ppo_policies_persistence=self._ppo_policies_persistence,
            episodes=episodes,
            max_time_steps=max_time_steps
        ).train_ppo_agent(ppo_policy_id)
        self._log.info(f'Trading PPO agent with policy ID \'{ppo_policy_id}\' training completed')
