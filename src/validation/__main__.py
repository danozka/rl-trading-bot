import logging
from logging import Logger

import typer
from typing_extensions import Annotated

from validation.container import Container
from validation.use_cases.lunar_lander_ppo_agent_trainer import LunarLanderPpoAgentTrainer


log: Logger = logging.getLogger(__name__)


def main(
    episodes: Annotated[int, typer.Option(help='Number of episodes to train the trading bot')] = 10000,
    max_time_steps: Annotated[int, typer.Option(help='Maximum number of time steps to update the trading bot')] = 500
) -> None:
    log.info('Starting application...')
    try:
        LunarLanderPpoAgentTrainer().train_lunar_lander_ppo_agent(episodes=episodes, max_time_steps=max_time_steps)
    except Exception as exception:
        log.error(f'Exception found: {exception.__class__.__name__} - {exception}')
        raise typer.Exit(code=1)
    finally:
        log.info('Application stopped')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)
    container: Container = Container()
    typer.run(main)
