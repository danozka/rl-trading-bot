import logging
from logging import Logger

from dependency_injector.wiring import inject, Provide

from rl_trading_bot.domain.candlestick_data_interval import CandlestickDataInterval
from rl_trading_bot.persistence.i_candlestick_data_persistence import ICandlestickDataPersistence
from rl_trading_bot.services.i_candlestick_data_repository import ICandlestickDataRepository


class CandlestickDataDownloader:
    _log: Logger = logging.getLogger(__name__)
    _candlestick_data_persistence: ICandlestickDataPersistence
    _candlestick_data_repository: ICandlestickDataRepository

    @inject
    def __init__(
        self,
        candlestick_data_persistence: ICandlestickDataPersistence = Provide['candlestick_data_persistence'],
        candlestick_data_repository: ICandlestickDataRepository = Provide['candlestick_data_repository']
    ) -> None:
        self._candlestick_data_persistence = candlestick_data_persistence
        self._candlestick_data_repository = candlestick_data_repository

    def download_candlestick_data(self, base_asset: str, quote_asset: str, interval: CandlestickDataInterval) -> None:
        self._log.info(
            f'Downloading candlestick data for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and '
            f'interval \'{interval}\'...'
        )
        self._candlestick_data_persistence.save_symbol_candlestick_data(
            base_asset=base_asset,
            quote_asset=quote_asset,
            interval=interval,
            candlestick_data=self._candlestick_data_repository.get_symbol_candlestick_data(
                base_asset=base_asset,
                quote_asset=quote_asset,
                interval=interval
            )
        )
        self._log.info(
            f'Candlestick data download for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and '
            f'interval \'{interval}\' completed'
        )
