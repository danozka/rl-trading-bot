import logging
import sys
from logging import Logger

from . import chatbot_container, video_service_container
from .http.app import App


if __name__ == '__main__':
    log: Logger = logging.getLogger(__name__)
    log.info('Starting application...')
    try:
        chatbot_container.init_resources()
        video_service_container.init_resources()
        App().start()
    except Exception as exception:
        log.error(f'Stopped application because of exception: {exception.__class__.__name__} - {exception}')
    finally:
        log.info('Application stopped')
        sys.exit(1)
