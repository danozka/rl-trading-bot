import logging
from logging import Logger
from pathlib import Path

import pandas
from pandas import DataFrame

from rl_trading_bot.domain.candlestick_data_interval import CandlestickDataInterval
from rl_trading_bot.persistence.i_candlestick_data_persistence import ICandlestickDataPersistence


class PickleCandlestickDataPersistence(ICandlestickDataPersistence):
    _log: Logger = logging.getLogger(__name__)
    _filename_template: str = 'candlestick_data_{base_asset}_{quote_asset}_{interval}.pkl'
    _data_directory: Path

    def __init__(self, data_directory: Path = Path('./data')) -> None:
        self._data_directory = data_directory
        self._data_directory.mkdir(parents=True, exist_ok=True)

    def save_symbol_candlestick_data(
        self,
        base_asset: str,
        quote_asset: str,
        interval: CandlestickDataInterval,
        candlestick_data: DataFrame
    ) -> None:
        self._log.debug(
            f'Saving candlestick data for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and '
            f'interval \'{interval}\'...'
        )
        candlestick_data.to_pickle(
            self._data_directory.joinpath(
                self._filename_template.format(base_asset=base_asset, quote_asset=quote_asset, interval=interval)
            )
        )
        self._log.debug(
            f'Candlestick data for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and '
            f'interval \'{interval}\' saved'
        )

    def load_symbol_candlestick_data(
        self,
        base_asset: str,
        quote_asset: str,
        interval: CandlestickDataInterval
    ) -> DataFrame:
        self._log.debug(
            f'Loading candlestick data for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and '
            f'interval \'{interval}\'...'
        )
        result: DataFrame = pandas.read_pickle(
            self._data_directory.joinpath(
                self._filename_template.format(base_asset=base_asset, quote_asset=quote_asset, interval=interval)
            )
        )
        self._log.debug(
            f'Candlestick data for base asset \'{base_asset}\', quote asset \'{quote_asset}\' and '
            f'interval \'{interval}\' loaded'
        )
        return result
