from abc import ABC, abstractmethod

from pandas import DataFrame

from trading_bot.candlestick.candlestick_data_interval import CandlestickDataInterval


class ICandlestickDataPersistence(ABC):

    @abstractmethod
    def save_symbol_candlestick_data(
        self,
        base_asset: str,
        quote_asset: str,
        interval: CandlestickDataInterval,
        candlestick_data: DataFrame
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_symbol_candlestick_data(
        self,
        base_asset: str,
        quote_asset: str,
        interval: CandlestickDataInterval
    ) -> DataFrame:
        raise NotImplementedError
