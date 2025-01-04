import logging
from logging import Logger
from typing import Optional
from uuid import UUID, uuid4

import typer
from typing_extensions import Annotated

from trading_bot.candlestick.candlestick_data_interval import CandlestickDataInterval
from trading_bot.container import Container
from trading_bot.use_cases.candlestick_data_downloader import CandlestickDataDownloader
from trading_bot.use_cases.trading_ppo_agent_trainer import TradingPpoAgentTrainer


log: Logger = logging.getLogger(__name__)


def main(
    base_asset: Annotated[str, typer.Option(help='Base asset to work with', show_default=False)],
    quote_asset: Annotated[str, typer.Option(help='Quote asset to work with', show_default=False)],
    ppo_policy_id: Annotated[
        Optional[UUID],
        typer.Option(help='Trading bot PPO policy ID (used for reproducibility)')
    ] = None,
    interval: Annotated[
        CandlestickDataInterval,
        typer.Option(help='Candlestick data interval to download')
    ] = CandlestickDataInterval.one_day,
    lower_interval: Annotated[
        CandlestickDataInterval,
        typer.Option(help='Candlestick data lower interval used during trading bot training')
    ] = CandlestickDataInterval.five_minutes,
    higher_interval: Annotated[
        CandlestickDataInterval,
        typer.Option(help='Candlestick data higher interval used during trading bot training')
    ] = CandlestickDataInterval.one_hour,
    lower_interval_lookback_candles: Annotated[
        int,
        typer.Option(help='Number of previous candles in the lower interval seen by the trading bot during training')
    ] = 96,
    higher_interval_lookback_candles: Annotated[
        int,
        typer.Option(help='Number of previous candles in the higher interval seen by the trading bot during training')
    ] = 120,
    episodes: Annotated[int, typer.Option(help='Number of episodes to train the trading bot')] = 10000,
    max_time_steps: Annotated[int, typer.Option(help='Maximum number of time steps to update the trading bot')] = 864,
    download: Annotated[bool, typer.Option('--download', help='Download candlestick data')] = False,
    train: Annotated[bool, typer.Option('--train', help='Train trading bot')] = False,
) -> None:
    if not (download or train):
        log.error('You must specify either --download or --train.')
        raise typer.Exit(code=1)
    elif download and train:
        log.error('Specify only one of --download or --train.')
        raise typer.Exit(code=1)
    log.info('Starting application...')
    try:
        if download:
            CandlestickDataDownloader().download_candlestick_data(
                base_asset=base_asset,
                quote_asset=quote_asset,
                interval=CandlestickDataInterval(interval)
            )
        elif train:
            TradingPpoAgentTrainer().train_trading_ppo_agent(
                ppo_policy_id=ppo_policy_id if ppo_policy_id is not None else uuid4(),
                base_asset=base_asset,
                quote_asset=quote_asset,
                lower_interval=CandlestickDataInterval(lower_interval),
                higher_interval=CandlestickDataInterval(higher_interval),
                lower_interval_lookback_candles=lower_interval_lookback_candles,
                higher_interval_lookback_candles=higher_interval_lookback_candles,
                episodes=episodes,
                max_time_steps=max_time_steps
            )
    except Exception as exception:
        log.error(msg=f'Exception found: {exception.__class__.__name__} - {exception}', exc_info=True)
        raise typer.Exit(code=1)
    finally:
        log.info('Application stopped')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d - [%(levelname)s] - [%(name)s] - %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        level=logging.DEBUG
    )
    container: Container = Container()
    typer.run(main)
