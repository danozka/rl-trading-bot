from abc import ABC, abstractmethod

from pandas import DataFrame

from rl_trading_bot.domain.candlestick_data_interval import CandlestickDataInterval


class ICandlestickDataRepository(ABC):

    @abstractmethod
    def get_symbol_candlestick_data(
        self,
        base_asset: str,
        quote_asset: str,
        interval: CandlestickDataInterval
    ) -> DataFrame:
        raise NotImplementedError
