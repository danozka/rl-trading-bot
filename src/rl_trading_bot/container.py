from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Singleton

from rl_trading_bot import use_cases
from rl_trading_bot.persistence.i_candlestick_data_persistence import ICandlestickDataPersistence
from rl_trading_bot.persistence.pickle_candlestick_data_persistence import PickleCandlestickDataPersistence
from rl_trading_bot.services.binance_candlestick_data_repository import BinanceCandlestickDataRepository
from rl_trading_bot.services.i_candlestick_data_repository import ICandlestickDataRepository


class Container(DeclarativeContainer):
    wiring_config: WiringConfiguration = WiringConfiguration(packages=[use_cases])
    candlestick_data_persistence: Singleton[ICandlestickDataPersistence] = Singleton(PickleCandlestickDataPersistence)
    candlestick_data_repository: Singleton[ICandlestickDataRepository] = Singleton(BinanceCandlestickDataRepository)
