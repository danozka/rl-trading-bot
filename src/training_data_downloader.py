import logging

from rl_trading_bot.domain.candlestick_data_interval import CandlestickDataInterval
from rl_trading_bot.use_cases.candlestick_data_downloader import CandlestickDataDownloader


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d - [%(levelname)s] - [%(name)s] - %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        level=logging.INFO
    )
    candlestick_data_downloader: CandlestickDataDownloader = CandlestickDataDownloader()
    base_asset: str = 'BTC'
    quote_asset: str = 'USDT'
    candlestick_data_downloader.download_candlestick_data(
        base_asset=base_asset,
        quote_asset=quote_asset,
        interval=CandlestickDataInterval.five_minutes
    )
    candlestick_data_downloader.download_candlestick_data(
        base_asset=base_asset,
        quote_asset=quote_asset,
        interval=CandlestickDataInterval.one_hour
    )
